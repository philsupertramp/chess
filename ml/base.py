from typing import Tuple, Union

import tensorflow as tf
from keras.callbacks import TensorBoard


# Own Tensorboard class
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


class BaseDQNAgent:
    REPLAY_MEMORY_SIZE = 50_000
    MIN_REPLAY_MEMORY_SIZE = 1_000
    MODEL_NAME = "256x2"
    MINI_BATCH_SIZE = 64
    DISCOUNT = 0.99
    MIN_REWARD = -200
    UPDATE_TARGET_EVERY = 5

    def __init__(self, env):
        self.env = env

    def create_model(self):
        raise NotImplementedError()

    def get_qs(self, state):
        raise NotImplementedError()

    def train(self, terminal_state, step):
        raise NotImplementedError()


class QEnv:
    SIZE = 10
    OBSERVATION_SPACE_VALUES: Tuple[int, int, int] = (SIZE, SIZE, 3)  # 4
    ACTION_SPACE_SIZE: int = 9
    episode_step: int = 0
    # define rewards/penalties as constants

    def reset(self) -> Tuple[Union[float, int], Union[float, int]]:
        """
        Resets the env state to initial (random) values.
        :return:
        """
        raise NotImplementedError()

    def step(self, action: int) -> Tuple[Tuple[Union[float, int], Union[float, int]], Union[float, int], bool]:
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
    def get_image(self):
        pass
