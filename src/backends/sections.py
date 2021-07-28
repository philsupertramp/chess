from typing import Optional, List

import pygame

from src.backends.screen import Screen, screen
from src.history import TurnHistory, Turn


class DisplaySection:
    def render(self, canvas, **kwargs):
        raise NotImplementedError()


class TurnHistorySection(DisplaySection):

    class TurnRecord:
        def __init__(self, turn: Turn, index: int):
            self.turn = turn
            self.position = index

        def render(self, surface: pygame.Surface):
            screen.draw_text_to_surface(str(self.turn), (self.position % 5, min(self.position//5, 0)), surface)

    def __init__(self):
        self.records: List['TurnRecord'] = list()

    def render(self, canvas: Screen, history: Optional[TurnHistory] = None, **kwargs):
        if not history:
            return
        rec = canvas.get_size()
        if self.records:
            record_len = len(self.records)
            self.records.extend([self.TurnRecord(turn, record_len + index) for index, turn in enumerate(history.turns[record_len - 1:])])
        else:
            self.records.extend([self.TurnRecord(turn, index) for index, turn in enumerate(history.turns)])
        surface = pygame.Surface((rec[0] - canvas.get_field_width(), rec[1] - canvas.get_field_height()))

        for record in self.records:
            record.render(surface)

        rect = (0, canvas.get_height(), canvas.get_width(), canvas.get_field_height())
        canvas.blit(surface, surface.get_rect(center=(canvas.get_height()-(surface.get_height()/2), canvas.get_width()-(surface.get_width()/2))))


class StatisticsSection(DisplaySection):
    def render(self, canvas, game=None, **kwargs):
        if not game:
            return
