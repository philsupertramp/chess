from typing import Optional, List

import pygame

from src.backends.colors import BLACK, WHITE
from src.backends.screen import Screen, screen
from src.history import TurnHistory, Turn


class DisplaySection:
    def render(self, canvas, **kwargs):
        raise NotImplementedError()


class TurnHistorySection(DisplaySection):
    # TODO: make scrollable
    class TurnRecord:
        def __init__(self, turn: Turn, index: int):
            self.turn = turn
            self.position = index

        def render(self, surface: pygame.Surface):
            pos = (85 * (self.position % 10), 25 * max(self.position//10, 0))
            screen.draw_text_to_surface(self.text, pos, surface, WHITE if self.turn.figure.is_white else BLACK)

        @property
        def text(self):
            return f'{f"{self.position // 2 + 1}." if self.turn.figure.is_white else ""}{str(self.turn)}'

    def __init__(self):
        self.records: List['TurnRecord'] = list()
        self.surface = None

    def resize(self, canvas):
        rec = canvas.get_size()
        self.surface = pygame.Surface((rec[0], rec[1] - canvas.get_field_height() + 10))
        self.surface.fill((50, 50, 50))

    def render(self, canvas: Screen, history: Optional[TurnHistory] = None, **kwargs):
        if history and history.turns:
            has_changed = False
            if len(history.turns) > len(self.records):
                record_len = len(self.records)
                self.records.extend([self.TurnRecord(turn, record_len + index) for index, turn in enumerate(history.turns[record_len:])])
                has_changed = True
            elif not self.records:
                self.records.extend([self.TurnRecord(turn, index) for index, turn in enumerate(history.turns)])
                has_changed = True

            if has_changed:
                self.surface.fill((50, 50, 50))

                for record in self.records:
                    record.render(self.surface)

        canvas.blit(self.surface, (0, canvas.get_field_height() - 5))


class StatisticsSection(DisplaySection):
    def __init__(self):
        self.surface = None
        self.data = dict()

    def resize(self, canvas):
        rec = canvas.get_size()
        self.surface = pygame.Surface((rec[0] - canvas.get_field_width() + 10, canvas.get_field_height() + 10))
        self.surface.fill((50, 50, 50))
        screen.draw_text_to_surface("Statistics", (150, 0), self.surface)
        for index, (key, value) in enumerate(self.data.items()):
            screen.draw_text_to_surface(f'{key}: {value}', (10, 35 * (1 + index)), self.surface)

    def render(self, canvas, game=None, **kwargs):
        if game and game.game_history.data:
            if game.game_history.data != self.data:
                self.data = game.game_history.data.copy()
                self.resize(canvas)

        canvas.blit(self.surface, (screen.get_field_width()-5, 0))
