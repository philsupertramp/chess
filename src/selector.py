import pygame

from src.colors import BLACK, WHITE
from src.figures import scale_figure, FieldType, Queen, Rook, Knight, Bishop
from src.screen import screen


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
        blacks = [
            scale_figure(pygame.image.load('resources/rook.png').convert_alpha(), screen),
            scale_figure(pygame.image.load('resources/bishop.png').convert_alpha(), screen),
            scale_figure(pygame.image.load('resources/king.png').convert_alpha(), screen),
            scale_figure(pygame.image.load('resources/knight.png').convert_alpha(), screen),
        ]
        whites = [
            scale_figure(pygame.image.load('resources/rook_w.png').convert_alpha(), screen),
            scale_figure(pygame.image.load('resources/bishop_w.png').convert_alpha(), screen),
            scale_figure(pygame.image.load('resources/king_w.png').convert_alpha(), screen),
            scale_figure(pygame.image.load('resources/knight_w.png').convert_alpha(), screen),
        ]

        scale = screen.get_width()/8, screen.get_height()/8

        self.white_surf.fill(BLACK)
        self.black_surf.fill(WHITE)

        for index, fig in enumerate(whites):
            self.white_surf.blit(fig, ((index < 2) * scale[0], (index % 2) * scale[1]))

        for index, fig in enumerate(blacks):
            self.black_surf.blit(fig, ((index < 2) * scale[0], (index % 2) * scale[1]))

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
