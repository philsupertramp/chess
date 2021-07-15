from typing import List, Optional, Tuple

import pygame

from src.colors import BLACK
from src.figures import Figure, King, Queen, Knight, Pawn, Bishop, Rook, FieldType, FigureChange
from src.screen import screen


class CheckerBoard:
    fields: List[List[Optional[Figure]]] = list(list())
    field_objects: List = list()
    elem_width: int = 0
    elem_height: int = 0
    figure_changes: List[FigureChange] = list()

    def __init__(self, display):
        self.empty_board: Optional[pygame.Surface] = None
        self.cell_size: Optional[Tuple[int]] = None
        self.canvas = display
        self.init_empty_field()

        self.fields: List[List[Optional[Figure]]] = list()
        self.reset()

    def reset(self):
        self.fields = [[None for _ in range(8)] for _ in range(8)]
        # only pawns and kings: '4k/PPPPPPPP/8/8/8/8/pppppppp/4K'
        self.load_game_from_string('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR')

    def process_figure_changes(self):
        for figure_change in self.figure_changes:
            pos = figure_change.prev_figure.position
            self.fields[pos[1]][pos[0]] = figure_change.new_figure

    def init_empty_field(self):
        self.cell_size = self.canvas.get_width() / 8, self.canvas.get_height() / 8
        self.empty_board = pygame.Surface((self.cell_size[0] * 8, self.cell_size[1] * 8))
        self.empty_board.fill((255, 255, 255))

        def get_elem_rect(_x, _y):
            return _x * self.cell_size[0], _y * self.cell_size[1], self.cell_size[0], self.cell_size[1]

        for x in range(1, 8, 2):
            for y in range(1, 8, 2):
                pygame.draw.rect(self.empty_board, BLACK, get_elem_rect(x, y))
        for x in range(0, 8, 2):
            for y in range(0, 8, 2):
                pygame.draw.rect(self.empty_board, BLACK, get_elem_rect(x, y))

    def load_game_from_string(self, input_string: str) -> None:
        """do some magic input string parsing

        available types
        k: king
        q: queen
        n: knight
        p: pawn
        b: bishop
        r: rook

        Example:
            initial setup:
            rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR

        :param input_string: input string "/"-separated
        :returns: None
        """
        for row, element in enumerate(input_string.split('/')):
            index = 0
            col = 0
            while index < len(element):
                try:
                    col = int(element[index]) - 1
                    index += 1
                except ValueError:
                    if col == 8:
                        col = 0
                    else:
                        col += 1

                try:
                    figure_type = element[index]
                except IndexError:
                    # found empty line
                    continue

                is_white = figure_type.isupper()
                figure_class = None
                if figure_type.lower() == 'k':
                    figure_class = King
                elif figure_type.lower() == 'q':
                    figure_class = Queen
                elif figure_type.lower() == 'n':
                    figure_class = Knight
                elif figure_type.lower() == 'p':
                    figure_class = Pawn
                elif figure_type.lower() == 'b':
                    figure_class = Bishop
                elif figure_type.lower() == 'r':
                    figure_class = Rook

                self.fields[row][col-1] = figure_class((col-1, row), is_white=is_white, _board=self)
                index += 1

    def draw(self):
        self.canvas.blit(self.empty_board, self.empty_board.get_rect())

        for x in range(len(self.fields)):
            for y in range(len(self.fields[x])):
                if not self.fields[x][y]:
                    continue

                self.fields[x][y].draw(self.canvas)

        screen.blit(self.canvas, self.canvas.get_rect())
