#!/usr/bin/env python


import numpy as np

# import plaidml.keras
# plaidml.keras.install_backend()

import tensorflow as tf
from tqdm import tqdm
import time
import os
import random

from agent import ChessAgent
from environment import ChessEnvironment
from ml.environment import TurnAction
from src.figures import FieldType

MODEL_NAME = "256x2"
MIN_REWARD = -50_000

MEMORY_FRACTION = 0.20

# Environment settings
EPISODES = 20_000
# EPISODES = 5
# Exploration settings
EPSILON_DECAY = 0.99975
MIN_EPSILON = 0.001

#  Stats settings
AGGREGATE_STATS_EVERY = 50  # episodes
SHOW_PREVIEW = True


"""
Penalty system:
- starting penalty: -200
- MOVE_PENALTY = 1
- ENEMY_PENALTY = -300
- LOSS_PENALTY = -1000
- NOT_PLAYING_PENALTY = -60
- CHECK_PENALTIES = {
        FieldType.PAWN: -100,
        FieldType.KNIGHT: -200,
        FieldType.BISHOP: -300,
        FieldType.ROOK: -400,
        FieldType.QUEEN: -500,
        FieldType.KING: LOSS_PENALTY,
    }
Rewards:
- winning: +1000
- checking:
    - FieldType.PAWN: 100,
    - FieldType.KNIGHT: 200,
    - FieldType.BISHOP: 300,
    - FieldType.ROOK: 400,
    - FieldType.QUEEN: 500,
    - FieldType.KING: 1000


To simulate training of allowed moves introduce penalties for arguments:
- first: empty > other color > own color (ranking per type) 
- second: not allowed move > walking > check figure (ranking per type) 

maybe introduce pending penalty, for advanced game to give penalties
whenever only pawns are played

"""


def main():
    env = ChessEnvironment()

    # For stats
    ep_rewards = [-200]

    # For more repetitive results
    random.seed(1)
    np.random.seed(1)
    tf.random.set_seed(1)

    # Memory fraction, used mostly when training multiple agents
    gpu_options = tf.compat.v1.GPUOptions(per_process_gpu_memory_fraction=MEMORY_FRACTION)
    tf.compat.v1.keras.backend.set_session(tf.compat.v1.Session(config=tf.compat.v1.ConfigProto(gpu_options=gpu_options)))

    # Create models folder
    if not os.path.isdir('models'):
        os.makedirs('models')

    agent = ChessAgent(env)
    epsilon = 1  # not a constant, going to be decayed

    # Iterate over episodes
    for episode in tqdm(range(1, EPISODES + 1), ascii=True, unit='episodes'):

        # Update tensorboard step every episode
        agent.tensorboard._train_step = episode

        # Restarting episode - reset episode reward and step number
        episode_reward = 0
        step = 1

        # Reset environment and get initial state
        current_state = env.reset()

        # Reset flag and start iterating until episode ends
        done = False
        while not done:
            agent.tensorboard._test_step = step

            # This part stays mostly the same, the change is to query a model for Q values
            if np.random.random() > epsilon:
                # Get action from Q table
                qs = agent.get_qs(np.array(current_state))
                action = np.argmax(qs, axis=0)
            else:
                # Get random action
                action = np.random.randint(0, 7, size=4)

            new_state, reward, done = env.step(action)

            if env.game.backend.needs_render_selector:
                env.game.board.handle_figure_promotion(0, 0)

            # Transform new continuous state to new discrete state and count reward
            episode_reward += reward

            if episode_reward < 10_000 * -env.LOSS_PENALTY:
                episode_reward -= reward
                break

            # if SHOW_PREVIEW:# and not episode % AGGREGATE_STATS_EVERY:
            env.render()

            while not env.game.is_white_turn and env.game.running:
                moves = []
                for row in env.game.board.fields:
                    for cell in row:
                        if cell and not cell.is_white:
                            allowed_moves = cell.remove_set(cell.allowed_moves)
                            if allowed_moves:
                                moves.append(TurnAction(figure=cell, allowed_moves=allowed_moves))
                fig = moves[random.randint(0, len(moves)-1)]
                move = fig.allowed_moves[random.randint(0, len(fig.allowed_moves)-1)]
                env.game.handle_mouse_click(fig.figure.position.x, fig.figure.position.y)
                env.game.handle_mouse_click(move.x, move.y)
                if env.game.backend.needs_render_selector:
                    env.game.board.handle_figure_promotion(0, 0)
                env.render()

                if env.game.board.checked_figure:
                    enemy_type = FieldType.clear(env.game.board.checked_figure.type)
                    reward -= env.CHECK_PENALTIES[enemy_type]
                done = not env.game.running

            # Every step we update replay memory and train main network
            agent.update_replay_memory((current_state, action, reward, new_state, done))
            agent.train(done, step)

            current_state = new_state
            step += 1

        # Append episode reward to a list and log stats (every given number of episodes)
        ep_rewards.append(episode_reward)
        if not episode % AGGREGATE_STATS_EVERY or episode == 1:
            average_reward = sum(ep_rewards[-AGGREGATE_STATS_EVERY:]) / len(ep_rewards[-AGGREGATE_STATS_EVERY:])
            min_reward = ep_rewards[np.argmin(ep_rewards[-AGGREGATE_STATS_EVERY:])]
            max_reward = ep_rewards[np.argmax(ep_rewards[-AGGREGATE_STATS_EVERY:])]
            agent.tensorboard.update_stats(reward_avg=average_reward, reward_min=min_reward, reward_max=max_reward, epsilon=epsilon)

            # Save model, but only when min reward is greater or equal a set value
            if min_reward >= MIN_REWARD:
                agent.model.save(
                    f'models/{MODEL_NAME}__{max_reward:_>7.2f}max_{average_reward:_>7.2f}avg_{min_reward:_>7.2f}min__{int(time.time())}.model')

        # Decay epsilon
        if epsilon > MIN_EPSILON:
            epsilon *= EPSILON_DECAY
            epsilon = max(MIN_EPSILON, epsilon)


if __name__ == '__main__':
    main()
