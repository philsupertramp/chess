import time
from copy import deepcopy
from typing import Optional

from src.board import CheckerBoard

from src.history import TurnHistory, GameHistory


class Game:
    # TODO:
    #      - Integrate `ml/main`
    #      - implement interface as painted...
    history = TurnHistory()
    game_history = GameHistory()

    is_mouse_clicked = False
    running = True
    is_white_turn = True

    def __init__(self, use_pygame: bool = True, underpromoted_castling: bool = False, frame_rate: float = 0.05, skip_init: bool = False) -> None:
        """
        Main Game class maintains and holds state of chess game.

        :param use_pygame: indicates to use pygame backend, if false headless console backend is used
        :param underpromoted_castling:
        :param frame_rate: 0.05 for 120FPS, 0.1 for 60 FPS, 0.2 for 30 FPS
        """
        if skip_init:
            return
        self.use_pygame = use_pygame
        self.frame_rate = frame_rate
        if self.use_pygame:
            from src.backends.pygame_backend import PygameBackend
            self.backend = PygameBackend(self)
        else:
            from src.backends.base import HeadlessBackend
            self.backend = HeadlessBackend(self)

        self.board = CheckerBoard(self.backend.canvas, self)
        self.underpromoted_castling = underpromoted_castling

    def copy(self):
        game = Game(skip_init=True)
        game.use_pygame = self.use_pygame
        game.is_white_turn = self.is_white_turn
        game.is_mouse_clicked = self.is_mouse_clicked
        game.game_history = self.game_history
        game.history = self.history
        game.frame_rate = self.frame_rate
        game.board = self.board.copy()
        game.backend = self.backend
        game.underpromoted_castling = self.underpromoted_castling
        return game

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
        self.game_history.save()

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

    def reset(self, with_history: bool = False) -> None:
        """
        reset game state, except history
        """
        self.backend.rescale()
        self.board = CheckerBoard(self.backend.canvas, self)
        if with_history:
            self.history = TurnHistory()
            if hasattr(self.backend, 'turn_history_section'):
                self.backend.turn_history_section.reset()

        self.running = True
        self.is_white_turn = True

    def replay(self, step_length: float = 1.) -> None:
        """
        Replays
        :param step_length: time between steps to display
        """
        moves = self.history.turns

        for turn in moves:
            if turn.is_promotion:
                self.handle_mouse_click(turn.start.x, turn.start.y)
                self.handle_mouse_click(turn.end.x, turn.end.y)
                self.backend.needs_render_selector = False
                self.board.fields[turn.start.y][turn.start.y] = None
                self.board.fields[turn.end.y][turn.end.y] = turn.figure
                self.board.fields[turn.end.y][turn.end.y].has_moved = True
                self.board.fields[turn.end.y][turn.end.y].prev_position = turn.start
                self.board.selected_figure = None
            else:
                self.handle_mouse_click(turn.start.x, turn.start.y)
                self.handle_mouse_click(turn.end.x, turn.end.y)
            self.backend.render()

            self.backend.handle_game_events([], [])

            # TODO: add some interruptable timeout
            time.sleep(step_length)

    def close(self):
        self.backend.shutdown()
