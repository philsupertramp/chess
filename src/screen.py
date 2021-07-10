import pygame


class Screen:
    def __init__(self, surf: pygame.Surface):
        self.window = surf
        self.font = pygame.font.SysFont('DejaVu Sans Mono', size=16, bold=True)

    @classmethod
    def build(cls, width, height):
        size = width, height
        return cls(pygame.display.set_mode(size, pygame.RESIZABLE | pygame.NOFRAME))

    def draw_text(self, text, position):
        text_surface = self.font.render(text, False, (0, 0, 0))
        self.blit(text_surface, position)

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


pygame.init()
pygame.font.init()
screen = Screen.build(320, 240)