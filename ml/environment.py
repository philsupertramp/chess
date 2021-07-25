from typing import Tuple, Union, List
import numpy as np
from base import QEnv
from src.game import Game

from src.figures import FieldType, Figure
from src.helpers import Coords


class TurnAction:
    def __init__(self, x, y, figure: Figure = None, allowed_moves: Union[List[Coords]] = None, move_index: int = -1):
        self.x = x
        self.y = y
        self.figure = figure
        self.allowed_moves = allowed_moves
        self.move_index = move_index

    def __str__(self):
        return f'{self.figure} –> {self.allowed_moves}'


class ChessEnvironment(QEnv):
    SIZE = 8
    RETURN_IMAGES = False
    MOVE_PENALTY = 1
    ENEMY_PENALTY = 300
    LOSS_PENALTY = 500
    NOT_PLAYING_PENALTY = 5
    CHECK_PENALTIES = {
        FieldType.PAWN: 10,
        FieldType.KNIGHT: 20,
        FieldType.BISHOP: 30,
        FieldType.ROOK: 40,
        FieldType.QUEEN: 50,
        FieldType.KING: LOSS_PENALTY,
    }
    ACTION_SPACE_SIZE = 4
    OBSERVATION_SPACE_VALUES = (SIZE, SIZE)
    MAX_STATE_VAL = FieldType.KING | FieldType.BLACK
    episode_step: int = 0

    def __init__(self):
        self.game = Game()
        self.state_storage = None
        self.is_white = True
        self.current_start_reward = 0
        super().__init__()

    def reset(self) -> Tuple[Union[float, int], Union[float, int]]:
        """
        Resets the env state to initial (random) values.
        :return:
        """
        self.game.reset()
        self.episode_step = 0

        return np.array(self.get_current_state())

    def step(self, action: Tuple[int, int]):# -> Tuple[Union[np.ndarray, Tuple[Union[float, int], Union[float, int]]], Union[float, int], bool]:
        """
        Computes a step in the environment  using given action

        :param action:
        :return:
        """

        reward = self.current_start_reward
        turn = None
        self.game.handle_mouse_click(action[0], action[1])
        if self.game.board.selected_figure:
            try:
                turn = action[2], action[3]
            except IndexError:
                reward -= self.NOT_PLAYING_PENALTY

            if turn is not None:
                self.game.handle_mouse_click(*turn)
            else:
                reward -= self.NOT_PLAYING_PENALTY
        else:
            reward -= self.NOT_PLAYING_PENALTY

        done = not self.game.running

        if self.game.board.checked_figure:
            enemy_type = FieldType.clear(self.game.board.checked_figure.type)
            reward += self.CHECK_PENALTIES[enemy_type]

        return self.get_current_state(), reward, done

    def check_enemy_piece(self, enemy_type):
        self.current_start_reward = -self.CHECK_PENALTIES[enemy_type]

    def render(self):
        """
        Optional method to render the current state
        :return:
        """
        self.game.backend.render()
        self.game.backend.handle_game_events([])

    # FOR CNN #
    def get_current_state(self):
        self.state_storage = np.empty(shape=self.OBSERVATION_SPACE_VALUES, dtype=float)
        y = 0
        for row in self.game.board.fields:
            x = 0
            for cell in row:
                if cell is not None and cell.is_white == self.is_white:
                    self.state_storage[y][x] = cell.type
                else:
                    self.state_storage[y][x] = 0
                x += 1
            y += 1

        return self.state_storage
