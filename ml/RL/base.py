from typing import Tuple, Union, Optional

import tensorflow as tf
from keras.callbacks import TensorBoard
from collections import deque
import numpy as np
import time
import random


# Own Tensorboard class
from src.helpers import Coords


class ModifiedTensorBoard(TensorBoard):

    # Overloaded init to set initial step and writer (we want one log file for all .fit() calls)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._train_step = 1
        self._writers['train'] = tf.summary.create_file_writer(self.log_dir)
        self._should_write_train_graph = False

    # Overload this method to stop creating default log writer
    def set_model(self, model):
        pass

    # Overloaded, saves logs with our step number
    # (otherwise every .fit() will start writing from 0th step)
    def on_epoch_end(self, epoch, logs=None):
        self.update_stats(**logs)

    # Overloaded
    # We train for one batch only, no need to save anything at epoch end
    def on_batch_end(self, batch, logs=None):
        pass

    # Overloaded, so won't close writer
    def on_train_end(self, _):
        pass

    # Custom method for saving own metrics
    # Creates writer, writes custom metrics and closes writer
    def update_stats(self, **stats):
        with self._writers['train'].as_default():
            for key, value in stats.items():
                tf.summary.scalar(key, data=value, step=self._train_step)


class QEnv:
    SIZE = 10
    OBSERVATION_SPACE_VALUES: Tuple[int, int, int] = (SIZE, SIZE, 3)  # 4
    ACTION_SPACE_SIZE: int = 9
    MAX_STATE_VAL: Union[int, float] = 0
    episode_step: int = 0

    def reset(self) -> Tuple[Union[float, int], Union[float, int]]:
        """
        Resets the env state to initial (random) values.
        :return:
        """
        raise NotImplementedError()

    def step(self, action: int) -> Tuple[Tuple[Union[float, int], Union[float, int]], Union[float, int], bool, Optional[Tuple]]:
        """
        Computes a step in the environment  using given action

        :param action:
        :return:
        """
        raise NotImplementedError()

    def render(self):
        """
        Optional method to render the current state
        :return:
        """
        pass

    # FOR CNN #
    def get_current_state(self):
        raise NotImplementedError()


class BaseDQNAgent:
    REPLAY_MEMORY_SIZE = 5_000_000
    MIN_REPLAY_MEMORY_FILLED = 0.01
    MODEL_NAME = ""
    MINI_BATCH_SIZE = 32
    DISCOUNT = 0.99
    MIN_REWARD = 0
    UPDATE_TARGET_EVERY = 100

    def __init__(self, env: QEnv):
        self.env = env

        self.replay_memory = deque(maxlen=self.REPLAY_MEMORY_SIZE)

        self.tensorboard = ModifiedTensorBoard(log_dir=f"logs/{self.MODEL_NAME}-{int(time.time())}")

        self.target_update_counter = 0

        # main model, gets trained every step
        self.model = self.create_model()

        # target model used for predictions in every step to keep predictions consistent
        self.target_model = self.create_model()
        self.target_model.set_weights(self.model.get_weights())

    def update_replay_memory(self, transition):
        self.replay_memory.append(transition)

    def get_qs(self, state):
        # TODO: [0] should be wrong, but could be right we only have a single output parameter :shrug:
        return self.model.predict(self.normalize(state))[0]

    def get_target_qs(self, state):
        # TODO: [0] should be wrong, but could be right we only have a single output parameter :shrug:
        return self.target_model.predict(self.normalize(state))[0]

    def normalize(self, val):
        return val / self.env.MAX_STATE_VAL

    def create_model(self):
        raise NotImplementedError()

    def has_enough_memory(self):
        result = len(self.replay_memory) >= (self.MIN_REPLAY_MEMORY_FILLED * self.REPLAY_MEMORY_SIZE)

        self.env.game.game_history.data['training'] = result
        return result

    def train(self, terminal_state, step):
        if not self.has_enough_memory():
            return

        mini_batch = random.sample(self.replay_memory, self.MINI_BATCH_SIZE)

        # scale to \in [0, 1]
        current_qs_list = np.array([self.get_qs(transition[0]) for transition in mini_batch])

        # again scaled
        future_qs_list = np.array([self.get_target_qs(transition[3]) for transition in mini_batch])

        # features
        x = list()
        # labels
        y = list()

        for index, (current_state, action, reward, new_current_state, done) in enumerate(mini_batch):
            # If not a terminal state, get new q from future states, otherwise set it to 0
            # almost like with Q Learning, but we use just part of the equation here
            if not done:
                max_future_q = np.max(future_qs_list[index])
                new_q = reward + self.DISCOUNT * max_future_q
            else:
                new_q = reward

            # Update Q value for given state
            current_qs = current_qs_list[index]
            current_qs[action] = new_q

            x.append(current_state)
            y.append(current_qs)

        self.model.fit(
            self.normalize(np.array(x)),
            np.array(y).reshape(self.MINI_BATCH_SIZE, 1, 16 * 64),
            batch_size=self.MINI_BATCH_SIZE,
            verbose=0,
            shuffle=False,
            callbacks=[self.tensorboard] if terminal_state else None
        )

        # updating to determine if we want to update target_model yet
        if terminal_state:
            self.target_update_counter += 1

        if self.target_update_counter > self.UPDATE_TARGET_EVERY:
            self.target_model.set_weights(self.model.get_weights())
            self.target_update_counter = 0

        self.replay_memory.clear()
