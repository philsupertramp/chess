
from typing import Optional
import pygame

from src.board import CheckerBoard
from src.screen import screen

from src.history import TurnHistory

from src.figures import Figure, rescale_images
from src.selector import FigureSelector


class Game:
    history = TurnHistory()
    selected_figure: Optional[Figure] = None

    is_mouse_clicked = False
    running = True
    is_white_turn = True

    def __init__(self):
        rescale_images(screen)
        self.canvas = pygame.Surface((screen.get_size()[0], screen.get_size()[1] - 20))
        self.board = CheckerBoard(self.canvas)
        self.figure_selector = FigureSelector()
        self.needs_render_selector = False

    def run(self):
        while self.running:
            if self.board.figure_changes:
                self.needs_render_selector = True
            self.render()
            self.board.process_figure_changes()

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
        pygame.quit()

    def render(self):
        screen.fill((255, 255, 255))
        self.board.draw()
        text = f'{"Whites" if self.is_white_turn else "Blacks"} turn'
        screen.draw_text(text, (screen.get_width() / 2, screen.get_height() - 15))
        if self.needs_render_selector:
            self.figure_selector.render(self.is_white_turn)
        pygame.display.flip()

    def handle_window_resize(self):
        self.canvas = pygame.Surface((screen.get_width(), screen.get_height() - 20))
        rescale_images(self.canvas)
        self.board.canvas = self.canvas
        self.board.init_empty_field()
        self.figure_selector.rescale()

    def handle_click(self):
        self.is_mouse_clicked = True

        mouse_pos = pygame.mouse.get_pos()

        scale = screen.get_width() / 8, (screen.get_height() - 20) / 8
        cols = int(mouse_pos[0] / scale[0])
        rows = int(mouse_pos[1] / scale[1])

        if self.needs_render_selector:
            self.handle_figure_replacement((rows, cols))
        else:
            self.handle_figure_selection((rows, cols))

    def handle_figure_replacement(self, mouse_pos):
        rows, cols = mouse_pos
        if rows > 1 or cols > 1:
            print('Error selecting...\nRetry!')
        fig_class = self.figure_selector.select(rows * 2 + cols)
        figure = fig_class(self.selected_figure.position, is_white=self.selected_figure.is_white, _board=self.board)
        self.board.fields[self.selected_figure.position[1]][self.selected_figure.position[0]] = figure
        self.selected_figure = None
        self.needs_render_selector = False
        self.is_white_turn = not self.is_white_turn

    def handle_figure_selection(self, mouse_pos):
        rows, cols = mouse_pos
        if not self.selected_figure:
            self.selected_figure = self.board.fields[rows][cols]
            # only allow selection if its the players turn
            if self.selected_figure:
                if self.selected_figure.is_white == self.is_white_turn:
                    self.board.fields[rows][cols].is_selected = True
                else:
                    color = "White" if self.is_white_turn else "Black"
                    print(f'{color} tried selecting {self.selected_figure}, not allowed.')
                    self.selected_figure = None
        else:
            old_pos = self.selected_figure.position

            if old_pos != (cols, rows) and self.selected_figure.move((cols, rows)):
                prev_fig = self.board.fields[rows][cols]
                self.history.record(self.selected_figure, (rows, cols), prev_fig)
                if prev_fig and prev_fig.checkmate():
                    self.running = False
                    print(f'Game over {"white" if self.is_white_turn else "black"} wins.')

                self.board.fields[old_pos[1]][old_pos[0]] = None
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
            self.board.process_figure_changes()


if __name__ == '__main__':
    game = Game()
    game.run()
