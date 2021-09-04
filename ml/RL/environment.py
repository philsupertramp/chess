from typing import Tuple, Union, List
import numpy as np
from base import QEnv
from src.game import Game

from src.figures import FieldType, Figure
from src.helpers import Coords
from src.history import TurnHistory


class TurnAction:
    def __init__(self, figure: Figure = None, allowed_moves: Union[List[Coords]] = None, move_index: int = -1):
        self.figure = figure
        self.allowed_moves = allowed_moves
        self.move_index = move_index

    def __str__(self):
        return f'{self.figure} –> {self.allowed_moves}'


class ChessEnvironment(QEnv):
    # TODO:
    #   - allow early exit and discarding of steps

    SIZE = 8
    RETURN_IMAGES = False
    LOSS_PENALTY = 100
    PLAYING_REWARD = 1
    MISSING_PENALTY = 1
    ENEMY_SELECTION_PENALTY = 6
    CHECK_PENALTIES = {
        FieldType.PAWN: 10,
        FieldType.KNIGHT: 20,
        FieldType.BISHOP: 30,
        FieldType.ROOK: 40,
        FieldType.QUEEN: 50,
        FieldType.KING: 25,
    }
    MAX_NUM_ACTIONS = 64
    OBSERVATION_SPACE_VALUES = (SIZE, SIZE)
    MAX_STATE_VAL = 100
    ACTION_SPACE_SIZE = (SIZE + SIZE) * MAX_NUM_ACTIONS
    episode_step: int = 0

    def __init__(self):
        self.game = Game(frame_rate=0)
        self.state_storage = None
        self.is_white = True
        self.current_start_reward = 0
        self.figure_map = dict()
        self.set_figure_map()
        super().__init__()

    def set_figure_map(self):
        self.figure_map = dict()
        i = 0
        for row in self.game.board.fields:
            for cell in filter(lambda x: x is not None and x.is_white == self.is_white, row):
                self.figure_map[i] = cell
                i = i + 1

    def reset(self) -> Tuple[Union[float, int], Union[float, int]]:
        """
        Resets the env state to initial (random) values.
        :return:
        """
        heatmap = self.game.backend.stats_section.heatmap.copy()
        self.game = Game()
        self.game.history = TurnHistory()
        self.game.backend.stats_section.heatmap = heatmap
        self.episode_step = 0
        self.set_figure_map()

        return np.array(self.get_current_state())

    def get_figure_by_index(self, index):
        return self.figure_map.get(int((index - (index % 64)) / 64))

    def get_figure_index(self, figure: Figure):
        for key, value in self.figure_map.items():
            if value == figure:
                return key

    def step(self, action: int):
        # -> Tuple[Union[np.ndarray, Tuple[Union[float, int], Union[float, int]]], Union[float, int], bool]:
        """
        Computes a step in the environment  using given action

        :param action:
        :return:
        """
        #
        reward = 0
        self.set_figure_map()

        first_click = self.get_figure_by_index(action)
        if first_click:
            first_click = first_click.position
            offset = action % 64
            second_click = Coords(offset % 8, int(offset/8))
            self.game.handle_mouse_click(first_click.col, first_click.row)
            if self.game.board.selected_figure:
                self.game.handle_mouse_click(second_click.col, second_click.row)
            else:
                reward -= 100
        else:
            reward -= 200
        # else:
        #     target = self.game.board.check_field(first_click)
        #     if target and not target.is_white:
        #         reward -= self.ENEMY_SELECTION_PENALTY
        #     else:
        #         reward -= 10 * self.PLAYING_REWARD
        #         # print('Doesn\'t wanna play')
        #
        # if self.game.board.checked_figure:
        #     enemy_type = FieldType.clear(self.game.board.checked_figure.type)
        #     reward += self.CHECK_PENALTIES[enemy_type]

        # reward = 0.0
        # for row in self.game.board.fields:
        #     reward = reward + sum([field.value for field in filter(lambda x: x is not None, row)])

        return self.get_current_state(), reward, not self.game.is_white_turn

    def render(self):
        """
        Optional method to render the current state
        :return:
        """
        self.game.backend.render()
        self.game.backend.handle_game_events([])

    # FOR CNN #
    def get_current_state(self):
        self.state_storage = np.zeros(shape=self.OBSERVATION_SPACE_VALUES, dtype=float)
        y = 0
        for row in self.game.board.fields:
            x = 0
            for cell in filter(lambda i: i is not None, row):
                self.state_storage[y][x] = cell.value
                x += 1
            y += 1

        return self.state_storage
