import time
from typing import Optional, List, Callable
import pygame
from pygame.event import Event

from src.board import CheckerBoard
from src.screen import screen

from src.history import TurnHistory

from src.figures import Figure, rescale_images
from src.selector import FigureSelector


EventCallback = Callable[[Event], None]


class Game:
    history = TurnHistory()
    selected_figure: Optional[Figure] = None

    is_mouse_clicked = False
    running = True
    is_white_turn = True

    def __init__(self) -> None:
        rescale_images(screen)
        self.canvas = pygame.Surface((screen.get_size()[0], screen.get_size()[1] - 20))
        self.board = CheckerBoard(self.canvas)
        self.figure_selector = FigureSelector()
        self.needs_render_selector = False

    def run(self) -> None:
        """
        game loop
        """
        while self.running:
            if self.board.figure_changes:
                self.needs_render_selector = True
            self.render()
            self.board.process_promotions()

            self.handle_game_events()

    def handle_game_events(self, procedures: Optional[List[EventCallback]] = None) -> None:

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.running = False

            if event.type == pygame.WINDOWSIZECHANGED:
                self.handle_window_resize()

            if not self.is_mouse_clicked:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click()

            if event.type == pygame.MOUSEBUTTONUP:
                self.is_mouse_clicked = False

            if procedures:
                for procedure in procedures:
                    procedure(event)

    def render(self) -> None:
        """
        Renders all required things for the game
        """
        screen.fill((255, 255, 255))
        self.board.draw()
        text = f'{"Whites" if self.is_white_turn else "Blacks"} turn'
        screen.draw_text(text, (screen.get_width() / 2, screen.get_height() - 15))
        if self.needs_render_selector:
            self.figure_selector.render(self.is_white_turn)
        pygame.display.flip()

    def handle_window_resize(self) -> None:
        """
        Handles window resizing.

        Call to recreate canvas
        """
        self.canvas = pygame.Surface((screen.get_width(), screen.get_height() - 20))
        rescale_images(self.canvas)
        self.board.rescale(self.canvas)
        self.figure_selector.rescale()

    def handle_click(self) -> None:
        """
        Handles mouse click.

        Call to get mouse position from pygame state
        """
        self.is_mouse_clicked = True

        mouse_pos = pygame.mouse.get_pos()

        scale = screen.get_width() / 8, (screen.get_height() - 20) / 8
        cols = int(mouse_pos[0] / scale[0])
        rows = int(mouse_pos[1] / scale[1])

        if self.needs_render_selector:
            self.handle_figure_promotion(cols, rows)
        else:
            self.handle_mouse_click(cols, rows)

    def handle_figure_promotion(self, cols: int, rows: int) -> None:
        """
        Handles Pawn-promotion

        :param cols: selected column
        :param rows: selected row
        """
        if rows > 1 or cols > 1:
            print('Error selecting...\nRetry!')
        fig_class = self.figure_selector.select(rows * 2 + cols)
        figure = fig_class(self.selected_figure.position, is_white=self.selected_figure.is_white, _board=self.board)
        self.board.fields[self.selected_figure.position[1]][self.selected_figure.position[0]] = figure
        self.selected_figure = None
        self.needs_render_selector = False
        self.is_white_turn = not self.is_white_turn

    def handle_figure_selection(self, cols: int, rows: int) -> None:
        """
        Handles selection of a figure

        Call to select a figure to given position.

        :param cols: selected column
        :param rows: selected row
        """
        self.selected_figure = self.board.fields[rows][cols]
        # only allow selection if its the players turn
        if self.selected_figure:
            if self.selected_figure.is_white == self.is_white_turn:
                # successfully selected figure
                self.board.fields[rows][cols].is_selected = True
            else:
                # unselect figure and print a picking error
                color = "White" if self.is_white_turn else "Black"
                print(f'{color} tried selecting {self.selected_figure}, not allowed.')
                # reset picked figure
                self.selected_figure = None

    def handle_figure_placement(self, cols: int, rows: int) -> None:
        """
        Handles figure placement in board

        Call to place a figure to the given position.
        :param cols: selected column
        :param rows:  selected row
        """
        old_pos = self.selected_figure.position

        if old_pos != (cols, rows) and self.selected_figure.move((cols, rows)):
            prev_fig_pos = (old_pos[1] if self.selected_figure.checked_en_passant else rows, cols)
            prev_fig = self.board.fields[prev_fig_pos[0]][prev_fig_pos[1]]
            self.selected_figure.checked_en_passant = False
            self.history.record(self.selected_figure, old_pos, (rows, cols), prev_fig)
            if prev_fig and prev_fig.checkmate():
                self.running = False
                print(f'Game over {"white" if self.is_white_turn else "black"} wins.')

            self.board.fields[old_pos[1]][old_pos[0]] = None
            # to ensure en-passant pawns are deleted
            self.board.fields[prev_fig_pos[0]][prev_fig_pos[1]] = None
            self.board.fields[rows][cols] = self.selected_figure
            if hasattr(self.selected_figure, 'needs_render_selector'):
                self.needs_render_selector = self.selected_figure.board.needs_render_selector
                # always delete the temporary value. aint no snitch, but try keepin it immutable, fam
                del self.selected_figure.board.needs_render_selector

            if not self.needs_render_selector:
                # switch turn
                self.is_white_turn = not self.is_white_turn
        else:
            print(f'Tried moving {self.selected_figure} -> {(cols, rows)}, not allowed.')

        self.board.fields[self.selected_figure.position[1]][self.selected_figure.position[0]].is_selected = False
        if not self.needs_render_selector:
            self.selected_figure = None
        self.board.process_promotions()
        self.board.reset_en_passant(self.is_white_turn)

    def handle_mouse_click(self, cols: int, rows: int) -> None:
        """
        Handles mouse click onto given position.

        Processes figure picking and placement.
        :param cols: selected columns
        :param rows: selected rows
        """
        if not self.selected_figure:
            self.handle_figure_selection(cols, rows)
        else:
            self.handle_figure_placement(cols, rows)

    def reset(self) -> None:
        """
        reset game state, except history
        """
        self.canvas = pygame.Surface((screen.get_size()[0], screen.get_size()[1] - 20))
        self.board = CheckerBoard(self.canvas)
        self.figure_selector = FigureSelector()
        self.needs_render_selector = False

        self.is_mouse_clicked = False
        self.running = True
        self.is_white_turn = True

    def replay(self, step_length: float = 1.5) -> None:
        """
        Replays
        :param step_length: time between steps to display
        """
        moves = self.history.turns

        def handle_next_step(event):
            if event.type == pygame.K_KP_ENTER:
                nonlocal skip
                skip = True

        for turn in moves:
            skip = False
            self.handle_mouse_click(*turn.start)
            self.handle_mouse_click(*turn.end)
            self.render()
            self.board.process_promotions()

            self.handle_game_events([handle_next_step])

            # TODO: add some interruptable timeout
            time.sleep(1)


if __name__ == '__main__':
    game = Game()
    game.run()

    game.reset()
    game.replay()

    pygame.quit()
