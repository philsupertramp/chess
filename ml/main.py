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


MODEL_NAME = "256x2"
MIN_REWARD = -200

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
    epsilon = .75  # not a constant, going to be decayed

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
                action = np.unravel_index(np.argmax(qs, axis=None), qs.shape)
            else:
                # Get random action
                action = np.random.randint(0, 7, size=4)

            new_state, reward, done = env.step(action)

            # Transform new continuous state to new discrete state and count reward
            episode_reward += reward

            # if SHOW_PREVIEW:# and not episode % AGGREGATE_STATS_EVERY:
            env.render()

            # Every step we update replay memory and train main network
            agent.update_replay_memory((current_state, action, reward, new_state, done))
            agent.train(done, step)

            current_state = new_state
            step += 1
            while not env.game.is_white_turn and env.game.running:
                env.render()
                done = not env.game.running

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
