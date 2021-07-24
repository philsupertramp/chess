import pygame

from src.backends.colors import BLACK, WHITE
from src.figures import FieldType, Queen, Rook, Knight, Bishop
from src.backends.screen import screen


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

    def select(self, value):
        assert value <= 3
        if value == self.queen:
            return Queen
        elif value == self.rook:
            return Rook
        elif value == self.knight:
            return Knight
        elif value == self.bishop:
            return Bishop

    def populate_surfaces(self):
        ratio = (int(screen.get_width() / 8), int(screen.get_height() / 8))

        self.white_surf.fill(BLACK)
        self.black_surf.fill(WHITE)

        figs = [FieldType.ROOK, FieldType.BISHOP, FieldType.QUEEN, FieldType.KNIGHT]
        for index, fig in enumerate(figs):
            screen.draw_figure(FieldType.WHITE | fig, ((index < 2) * ratio[0], (index % 2) * ratio[1]), self.white_surf)
            screen.draw_figure(FieldType.BLACK | fig, ((index < 2) * ratio[0], (index % 2) * ratio[1]), self.black_surf)

    def rescale(self):
        cells = screen.get_width() / 4, screen.get_height() / 4
        # 2x2 canvas
        self.white_surf = pygame.Surface(cells)
        self.black_surf = pygame.Surface(cells)
        self.populate_surfaces()

    def render(self, iswhite: bool):
        if iswhite:
            screen.blit(self.white_surf, self.white_surf.get_rect())
        else:
            screen.blit(self.black_surf, self.black_surf.get_rect())
