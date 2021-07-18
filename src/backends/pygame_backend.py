from typing import Optional, List, Callable

from pygame.event import Event

from src.backends.screen import screen
import pygame

from src.backends.base import BaseBackend
from src.backends.selector import FigureSelector
from src.figures import rescale_images


EventCallback = Callable[[Event], None]


class PygameBackend(BaseBackend):
    def __init__(self, game):
        super().__init__(game)
        self.canvas = pygame.Surface((screen.get_size()[0], screen.get_size()[1] - 20))
        rescale_images(screen)
        self.figure_selector = FigureSelector()
        self.needs_render_selector = False
        self.is_mouse_clicked = False

    def handle_game_events(self, procedures: Optional[List[EventCallback]] = None, events=None) -> None:
        def quit_event(event):
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                self.game.running = False

        def resize(event):
            if event.type == pygame.WINDOWSIZECHANGED:
                self.handle_window_resize()

        def mouse_click(event):
            if not self.is_mouse_clicked:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click()

        def mouse_undo_click(event):
            if event.type == pygame.MOUSEBUTTONUP:
                self.is_mouse_clicked = False

        extended_procedures = procedures + [
            quit_event, resize, mouse_click, mouse_undo_click
        ]

        super().handle_game_events(extended_procedures, pygame.event.get())

    def render(self) -> None:
        """
        Renders all required things for the game
        """
        screen.fill((255, 255, 255))
        self.game.board.draw()
        text = f'{"Whites" if self.game.is_white_turn else "Blacks"} turn'
        screen.draw_text(text, (screen.get_width() / 2, screen.get_height() - 15))
        if self.needs_render_selector:
            self.figure_selector.render(self.game.is_white_turn)
        pygame.display.flip()

    def rescale(self):
        self.canvas = pygame.Surface((screen.get_width(), screen.get_height() - 20))
        rescale_images(self.canvas)
        self.figure_selector = FigureSelector()

    def reset(self):
        self.rescale()
        self.needs_render_selector = False

    def handle_window_resize(self) -> None:
        """
        Handles window resizing.

        Call to recreate canvas
        """
        self.rescale()
        self.game.board.rescale(self.canvas)

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
            self.game.handle_figure_promotion(cols, rows)
        else:
            self.game.handle_mouse_click(cols, rows)

    def shutdown(self):
        pygame.quit()
