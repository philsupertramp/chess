#! /usr/bin/env python


import argparse
import time
from typing import Optional

from src.board import CheckerBoard

from src.history import TurnHistory

from src.figures import Figure


class Game:
    history = TurnHistory()
    selected_figure: Optional[Figure] = None

    is_mouse_clicked = False
    running = True
    is_white_turn = True

    def __init__(self, use_pygame: bool = True, underpromoted_castling: bool = False, frame_rate: float = 0.05) -> None:
        """
        Main Game class maintains and holds state of chess game.

        :param use_pygame: indicates to use pygame backend, if false headless console backend is used
        :param underpromoted_castling:
        :param frame_rate: 0.05 for 120FPS, 0.1 for 60 FPS, 0.2 for 30 FPS
        """
        self.use_pygame = use_pygame
        self.frame_rate = frame_rate
        if self.use_pygame:
            from src.backends.pygame_backend import PygameBackend
            self.backend = PygameBackend(self)
        else:
            from src.backends.base import HeadlessBackend
            self.backend = HeadlessBackend(self)

        self.board = CheckerBoard(self.backend.canvas, self)
        self.needs_render_selector = False
        self.underpromoted_castling = underpromoted_castling

    @property
    def figure_selector(self) -> Optional['FigureSelector']:
        return self.backend.figure_selector

    def run(self) -> None:
        """
        game loop
        """
        start = time.time()
        counter = 0
        while self.running:
            if (time.time() - start) < self.frame_rate:
                continue
            self.backend.render()
            self.backend.handle_game_events([])

            counter += 1
            if (time.time() - start) > 1:
                print(f'FPS: {int(counter/(time.time() - start))}')
                counter = 0
                start = time.time()

        self.history.is_final = True

    def handle_mouse_click(self, cols: int, rows: int) -> None:
        """
        Handles mouse click onto given position.

        Processes figure picking and placement.
        :param cols: selected columns
        :param rows: selected rows
        """
        if rows < 0 or rows > 7 or cols < 0 or cols > 7:
            return

        if self.board.handle_mouse_click(cols, rows, self.is_white_turn) and not self.backend.needs_render_selector:
            # switch turn
            self.is_white_turn = not self.is_white_turn

    def reset(self) -> None:
        """
        reset game state, except history
        """
        self.backend.rescale()
        self.board = CheckerBoard(self.backend.canvas, self)

        self.running = True
        self.is_white_turn = True

    def replay(self, step_length: float = 1.5) -> None:
        """
        Replays
        :param step_length: time between steps to display
        """
        moves = self.history.turns

        for turn in moves:
            self.handle_mouse_click(turn.start.x, turn.start.y)
            self.handle_mouse_click(turn.end.x, turn.end.y)
            self.backend.render()

            self.backend.handle_game_events([], [])

            # TODO: add some interruptable timeout
            time.sleep(1)

    def close(self):
        self.backend.shutdown()


def init_argparse() -> argparse.ArgumentParser:
    _parser = argparse.ArgumentParser(description='Process some integers.')
    _parser.add_argument('--headless', dest='headless', action='store_true',
                         help='Use headless console version.')
    return _parser


if __name__ == '__main__':
    parser = init_argparse()
    args = parser.parse_args()
    game = Game(not args.headless)
    game.run()

    game.reset()
    game.replay()

    game.close()
