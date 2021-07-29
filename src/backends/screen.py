import pygame

from src.figures import FieldType


class Screen:
    def __init__(self, surf: pygame.Surface):
        self.window = surf
        self.font = pygame.font.SysFont('DejaVu Sans Mono', size=16, bold=True)
        self.figure_size = 0
        self.figure_font = None
        self.resize_figure_font(0.35 * surf.get_width() / 8)

    @classmethod
    def build(cls, width, height):
        size = width, height
        return cls(pygame.display.set_mode(size, pygame.RESIZABLE | pygame.NOFRAME))

    def draw_text(self, text, position):
        self.draw_text_to_surface(text, position, self.window)

    def resize_figure_font(self, size):
        if self.figure_size != int(size):
            self.figure_size = int(size)
            self.figure_font = pygame.font.Font('/home/phil/work/private/chess/resources/merida.ttf', self.figure_size)

    def draw_figure(self, fig_type, position, surface=None):
        if surface is None:
            surface = self.window

        text = {
            FieldType.WHITE | FieldType.PAWN: 'p',
            FieldType.BLACK | FieldType.PAWN: 'o',
            FieldType.WHITE | FieldType.KNIGHT: 'n',
            FieldType.BLACK | FieldType.KNIGHT: 'm',
            FieldType.WHITE | FieldType.BISHOP: 'b',
            FieldType.BLACK | FieldType.BISHOP: 'v',
            FieldType.WHITE | FieldType.ROOK: 'r',
            FieldType.BLACK | FieldType.ROOK: 't',
            FieldType.WHITE | FieldType.QUEEN: 'q',
            FieldType.BLACK | FieldType.QUEEN: 'w',
            FieldType.WHITE | FieldType.KING: 'k',
            FieldType.BLACK | FieldType.KING: 'l',
        }[fig_type]

        text_surface = self.figure_font.render(text, False, (0, 0, 0))
        surface.blit(text_surface, position)

    def draw_text_to_surface(self, text, position, surface, color=(0, 0, 0)):
        text_surface = self.font.render(text, True, color)
        surface.blit(text_surface, position)

    def fill(self, color):
        self.window.fill(color)

    def blit(self, canvas, rect):
        self.window.blit(canvas, rect)

    def get_size(self):
        return self.window.get_size()

    def get_height(self):
        return self.window.get_height()

    def get_width(self):
        return self.window.get_width()

    def get_field_height(self):
        return self.window.get_height() * 0.8

    def get_field_width(self):
        return self.window.get_width() * 0.7


pygame.init()
pygame.font.init()
screen = Screen.build(320, 240)
