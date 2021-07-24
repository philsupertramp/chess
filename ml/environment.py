from typing import Tuple, Union, List
import numpy as np
from base import QEnv
from src.game import Game

from src.figures import FieldType, Figure
from src.helpers import Coords


class TurnAction:
    def __init__(self, figure: Figure, allowed_moves: List[Coords]):
        self.figure = figure
        self.allowed_moves = allowed_moves

    def __str__(self):
        return f'{self.figure} –> {self.move}'


class ChessEnvironment(QEnv):
    SIZE = 8
    RETURN_IMAGES = False
    MOVE_PENALTY = 1
    ENEMY_PENALTY = 300
    LOSS_PENALTY = 500
    NOT_PLAYING_PENALTY = 100
    CHECK_PENALTIES = {
        FieldType.PAWN: 10,
        FieldType.KNIGHT: 20,
        FieldType.BISHOP: 30,
        FieldType.ROOK: 40,
        FieldType.QUEEN: 50,
        FieldType.KING: LOSS_PENALTY,
    }
    ACTION_SPACE_SIZE = 8*2
    OBSERVATION_SPACE_VALUES = (SIZE*SIZE, ACTION_SPACE_SIZE, 1)
    MAX_STATE_VAL = FieldType.KING | FieldType.BLACK
    episode_step: int = 0

    def __init__(self):
        self.game = Game()
        self.action_storage: List[TurnAction] = list()
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

        self.action_storage = list()
        return np.array(self.get_current_state())

    def step(self, action: int) -> Tuple[Union[np.ndarray, Tuple[Union[float, int], Union[float, int]]], Union[float, int], bool]:
        """
        Computes a step in the environment  using given action

        :param action:
        :return:
        """

        reward = self.current_start_reward
        turn = None
        try:
            turn = self.action_storage[action][0][0]
        except IndexError:
            reward -= self.NOT_PLAYING_PENALTY

        if turn and turn.allowed_moves:
            self.game.handle_mouse_click(turn.figure.position.y, turn.figure.position.x)
            self.game.handle_mouse_click(turn.allowed_moves[0].y, turn.allowed_moves[0].x)
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

    # FOR CNN #
    def get_current_state(self):
        self.action_storage = np.empty(shape=self.OBSERVATION_SPACE_VALUES, dtype=TurnAction)
        cell_index = 0
        for y in self.game.board.fields:
            for cell in y:
                if cell is not None and cell.is_white == self.is_white:
                    self.action_storage[cell_index] = TurnAction(cell, cell.allowed_moves)
                    cell_index += 1

        return np.array(np.arange(0, self.ACTION_SPACE_SIZE))
