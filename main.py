
from typing import Optional
import pygame

from src.board import CheckerBoard
from src.screen import screen

from src.history import TurnHistory

from src.figures import Figure, rescale_images, FieldType, scale_figure


class FigureSelector:
    white_surf: pygame.Surface
    black_surf: pygame.Surface

    def __init__(self):
        self.rescale()
        self.queen = 0
        self.rook = 1
        self.knight = 2
        self.bishop = 3
        self.figure_map = {
            self.queen: FieldType.QUEEN,
            self.rook: FieldType.ROOK,
            self.knight: FieldType.KNIGHT,
            self.bishop: FieldType.BISHOP,
        }

    def populate_surfaces(self):
        whites = [
            scale_figure(pygame.image.load('resources/king.png').convert_alpha(), screen),
            scale_figure(pygame.image.load('resources/rook.png').convert_alpha(), screen),
            scale_figure(pygame.image.load('resources/knight.png').convert_alpha(), screen),
            scale_figure(pygame.image.load('resources/bishop.png').convert_alpha(), screen)
        ]
        blacks = [
            scale_figure(pygame.image.load('resources/king_w.png').convert_alpha(), screen),
            scale_figure(pygame.image.load('resources/rook_w.png').convert_alpha(), screen),
            scale_figure(pygame.image.load('resources/knight_w.png').convert_alpha(), screen),
            scale_figure(pygame.image.load('resources/bishop_w.png').convert_alpha(), screen)
        ]

        for index, fig in enumerate(whites):
            self.white_surf.blit(fig, ((index % 2) * fig.get_width(), (max(0, index - 2)) * fig.get_height(), fig.get_width(), fig.get_height()))

        for index, fig in enumerate(blacks):
            self.black_surf.blit(fig, ((index % 2) * fig.get_width(), (max(0, index - 2)) * fig.get_height(), fig.get_width(), fig.get_height()))

    def rescale(self):
        cells = screen.get_width() / 4, screen.get_width() / 4
        # 2x2 canvas
        self.white_surf = pygame.Surface((cells[0], cells[1]))
        self.black_surf = pygame.Surface((cells[0], cells[1]))
        self.populate_surfaces()

    def render(self, iswhite: bool):
        if iswhite:
            screen.blit(self.white_surf, self.white_surf.get_rect())
        else:
            screen.blit(self.black_surf, self.black_surf.get_rect())


class Game:
    history = TurnHistory()
    selected_figure: Optional[Figure] = None

    is_mouse_clicked = False
    running = True
    is_white_turn = True
    needs_render_selector = False

    def __init__(self):
        rescale_images(screen)
        self.canvas = pygame.Surface((screen.get_size()[0], screen.get_size()[1] - 20))
        self.board = CheckerBoard(self.canvas)
        self.figure_selector = FigureSelector()

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
        pygame.display.flip()
        if self.needs_render_selector:
            self.render_selector()

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

                # switch turn
                self.is_white_turn = not self.is_white_turn
            else:
                print(f'Tried moving {self.selected_figure} -> {(cols, rows)}, not allowed.')
            self.board.fields[self.selected_figure.position[1]][self.selected_figure.position[0]].is_selected = False
            self.selected_figure = None
            self.board.process_figure_changes()

    def render_selector(self):
        self.figure_selector.render(self.is_white_turn)


if __name__ == '__main__':
    game = Game()
    game.run()
