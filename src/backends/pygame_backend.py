from typing import Optional, List, Callable

from pygame.event import Event

from src.backends.screen import screen
import pygame

from src.backends.base import BaseBackend
from src.backends.sections import StatisticsSection, TurnHistorySection
from src.backends.selector import FigureSelector


EventCallback = Callable[[Event], None]


class PygameBackend(BaseBackend):
    def __init__(self, game):
        super().__init__(game)
        self.canvas = pygame.Surface((screen.get_field_width(), screen.get_field_height()))
        self.figure_selector = FigureSelector()
        self.stats_section = StatisticsSection()
        self.turn_history_section = TurnHistorySection()

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
        text = f'{"Whites" if self.game.is_white_turn else "Blacks"} turn {self.game.history}'

        screen.draw_text(text, (50, screen.get_height() - 15))
        if self.needs_render_selector:
            self.figure_selector.render(self.game.is_white_turn)
        self.stats_section.render(screen, game=self.game)
        self.turn_history_section.render(screen, history=self.game.history)
        pygame.display.flip()

    def rescale(self):
        self.canvas = pygame.Surface((screen.get_field_width(), screen.get_field_height()))
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
        screen.resize_figure_font(0.5 * screen.get_field_width() / 8)

    def handle_click(self) -> None:
        """
        Handles mouse click.

        Call to get mouse position from pygame state
        """
        self.is_mouse_clicked = True

        mouse_pos = pygame.mouse.get_pos()

        scale = screen.get_field_width() / 8, (screen.get_field_height()) / 8
        cols = int(mouse_pos[0] / scale[0])
        rows = int(mouse_pos[1] / scale[1])

        if self.needs_render_selector:
            self.game.board.handle_figure_promotion(cols, rows)
        else:
            self.game.handle_mouse_click(cols, rows)

    def shutdown(self):
        pygame.quit()
