
from base import BaseDQNAgent
import tensorflow as tf


class ChessAgent(BaseDQNAgent):
    MODEL_NAME = "Chess-"

    def __init__(self, env):
        super().__init__(env)

    def create_model(self):
        model = tf.keras.models.Sequential()
        model.add(tf.keras.layers.Flatten(input_shape=self.env.OBSERVATION_SPACE_VALUES))
        model.add(tf.keras.layers.Dense(64, activation='relu'))
        model.add(tf.keras.layers.Dense(64, activation='relu'))
        model.add(tf.keras.layers.Dense(self.env.ACTION_SPACE_SIZE, activation='linear'))

        model.compile(loss="mse", optimizer=tf.keras.optimizers.Adam(learning_rate=0.001), metrics=['accuracy'])
        return model

