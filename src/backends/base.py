from unittest import mock

import pygame

from src.history import Turn


class BaseBackend:
    canvas = None
    figure_selector = None
    needs_render_selector = False
    is_mouse_clicked = False

    def __init__(self, game):
        self.game = game

    def handle_game_events(self, procedures, events):
        for event in events:
            for procedure in procedures:
                procedure(event)

    def render(self):
        pass

    def rescale(self):
        pass

    def reset(self):
        pass

    def handle_window_resize(self):
        pass

    def handle_mouse_click(self):
        pass

    def shutdown(self):
        pass


class HeadlessBackend(BaseBackend):
    def __init__(self, game):
        super().__init__(game)

        self.canvas = mock.Mock(get_width=mock.Mock(return_value=20*8),
                                get_height=mock.Mock(return_value=20*8))

    def handle_game_events(self, procedures, events=None):
        next_move = ''
        while len(next_move) != 4:
            next_move = input(f'Next move ({"White" if self.game.is_white_turn else "Black"}): ')
        next_move = list(next_move)
        start = self.game.history.string_to_pos(next_move[:2])
        end = self.game.history.string_to_pos(next_move[2:])
        self.game.handle_mouse_click(*start)
        self.game.handle_mouse_click(*end)

    def render(self):
        print(self.game.history.last_move)
