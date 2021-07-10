import sys
from typing import List, Optional, Tuple

import numpy as np

import pygame
from pygame.locals import *

pygame.init()

size = width, height = 320, 240

screen = pygame.display.set_mode(size, pygame.RESIZABLE)


class FieldType:
    EMPTY = 0
    KING = 1
    PAWN = 2
    KNIGHT = 3
    BISHOP = 4
    ROOK = 5
    QUEEN = 6

    WHITE = 8
    BLACK = 16


BLACK = pygame.color.Color(103,	114, 136, 50)
WHITE = pygame.color.Color(255, 255, 255, 255)


def scale_figure(figure: pygame.Surface):
    ratio = (int(screen.get_width() / 8), int(screen.get_height() / 8))
    return pygame.transform.scale(figure, ratio)


figures = {
    FieldType.QUEEN | FieldType.BLACK: pygame.image.load('resources/king.png').convert_alpha(),
    FieldType.KING | FieldType.BLACK: pygame.image.load('resources/queen.png').convert_alpha(),
    FieldType.ROOK | FieldType.BLACK: pygame.image.load('resources/rook.png').convert_alpha(),
    FieldType.KNIGHT | FieldType.BLACK: pygame.image.load('resources/knight.png').convert_alpha(),
    FieldType.BISHOP | FieldType.BLACK: pygame.image.load('resources/bishop.png').convert_alpha(),
    FieldType.PAWN | FieldType.BLACK: pygame.image.load('resources/pawn.png').convert_alpha(),

    FieldType.QUEEN | FieldType.WHITE: pygame.image.load('resources/king_w.png').convert_alpha(),
    FieldType.KING | FieldType.WHITE: pygame.image.load('resources/queen_w.png').convert_alpha(),
    FieldType.ROOK | FieldType.WHITE: pygame.image.load('resources/rook_w.png').convert_alpha(),
    FieldType.KNIGHT | FieldType.WHITE: pygame.image.load('resources/knight_w.png').convert_alpha(),
    FieldType.BISHOP | FieldType.WHITE: pygame.image.load('resources/bishop_w.png').convert_alpha(),
    FieldType.PAWN | FieldType.WHITE: pygame.image.load('resources/pawn_w.png').convert_alpha(),
}


def rescale_images():
    global figures
    figures = {key: scale_figure(figure) for key, figure in figures.items()}


rescale_images()


class Figure:
    def __init__(self, pos, is_white, _board):
        self.position = pos
        self.type: int = FieldType.WHITE if is_white else FieldType.BLACK
        self.is_white: bool = is_white
        self.board = _board
        self.is_selected = False

    def check_field(self, move):
        fig = self.get_figure_at_target(move)
        if fig is not None:
            return fig.is_white != self.is_white
        return True

    def can_move(self, move) -> bool:
        figure_at_target = self.get_figure_at_target(move)
        if figure_at_target is not None:
            return figure_at_target.is_white != self.is_white

        if abs(move[0]) > 0 and abs(move[0]) == abs(move[1]):
            # diagonal move
            factors = ((-1) if move[0] > 0 else 1, (-1) if move[1] > 0 else 1, )
            for i in range(1, abs(move[0])+1):
                if not self.check_field((self.position[0] + factors[0] * i, self.position[1] + factors[1] * i)):
                    return False
        elif abs(move[0]) > 0:
            # x direction
            factor = (-1) if move[0] < 0 else 1
            for i in range(1, abs(move[0])+1):
                if not self.check_field((self.position[0] + factor * i, self.position[1])):
                    return False
        elif abs(move[1]) > 0:
            # y direction
            factor = (-1) if move[1] < 0 else 1
            for i in range(1, abs(move[1])+1):
                if not self.check_field((self.position[0], self.position[1] + factor * i)):
                    return False
        return True

    def get_figure_at_target(self, move):
        return self.board.fields[move[0]][move[1]]

    def move(self, new_pos) -> bool:
        if self.is_move_allowed(new_pos):
            self.position = new_pos
            return True
        return False

    def is_move_allowed(self, move):
        raise NotImplementedError

    def draw(self, canvas):
        if self.type == FieldType.EMPTY:
            return

        scale = canvas.get_width()/8, canvas.get_height()/8
        figure = figures.get(self.type)
        if self.is_selected:
            figure = figure.copy()
            figure.convert_alpha()
            figure.set_colorkey((255, 0, 255))

        canvas.blit(figure, (scale[0] * self.position[0], scale[1] * self.position[1]))


class Pawn(Figure):
    def __init__(self, pos, **kwargs):
        super().__init__(pos, **kwargs)
        self.type |= FieldType.PAWN

    def is_move_allowed(self, move):
        if abs(move[0]) == 1 and abs(move[1]) == 1 and not self.can_move((move[0] - self.position[0], move[1] - self.position[1])):
            print(f"Pawn defeats {self.get_figure_at_target(move)}")
            return True
        return (self.position[0] - move[0]) == 0 and (self.position[1] - move[1] <= 1 if self.is_white else -1) and self.can_move((move[0] - self.position[0], move[1] - self.position[1]))

    def __str__(self):
        return f'{"white " if self.is_white else "black "}Pawn: {self.position}'


class Queen(Figure):
    def __init__(self, pos, **kwargs):
        super().__init__(pos, **kwargs)
        self.type |= FieldType.QUEEN

    def is_move_allowed(self, move):
        return self.can_move(move)  # and abs(self.position[0] - move[0]) <= 1 and abs(self.position[1] - move[1]) <= 1

    def __str__(self):
        return f'{"white " if self.is_white else "black "}Queen: {self.position}'


class King(Figure):
    def __init__(self, pos, **kwargs):
        super().__init__(pos, **kwargs)
        self.type |= FieldType.KING

    def is_move_allowed(self, move):
        # (abs(move[0]) <= 1 and abs(move[1]) <= 1) and (not (abs(move[0]) == 1 and abs(move[1]) == 1))

        return abs(self.position[0] - move[0]) <= 1 and abs(self.position[1] - move[1]) <= 1 and self.can_move((move[0] - self.position[0], move[1] - self.position[1]))

    def __str__(self):
        return f'{"white " if self.is_white else "black "}King: {self.position}'


class Rook(Figure):
    def __init__(self, pos, **kwargs):
        super().__init__(pos, **kwargs)
        self.type |= FieldType.ROOK

    def is_move_allowed(self, move):
        return (abs(self.position[0] - move[0]) <= 1) != (abs(self.position[1] - move[1]) <= 1)\
               and self.can_move((move[0] - self.position[0], move[1] - self.position[1]))

    def __str__(self):
        return f'{"white " if self.is_white else "black "}Rook: {self.position}'


class Bishop(Figure):
    def __init__(self, pos, **kwargs):
        super().__init__(pos, **kwargs)
        self.type |= FieldType.BISHOP

    def is_move_allowed(self, move):
        return abs(self.position[0] - move[0]) == abs(self.position[1] - move[1]) and self.can_move((move[0] - self.position[0], move[1] - self.position[1]))

    def __str__(self):
        return f'{"white " if self.is_white else "black "}Bishop: {self.position}'


class Knight(Figure):
    def __init__(self, pos, **kwargs):
        super().__init__(pos, **kwargs)
        self.type |= FieldType.KNIGHT

    def is_move_allowed(self, move):
        abs_x = abs(self.position[0] - move[0])
        abs_y = abs(self.position[1] - move[1])
        return ((abs_x == 1 and abs_y == 2) or (abs_x == 2 and abs_y == 1)) and self.can_move((move[0] - self.position[0], move[1] - self.position[1]))

    def __str__(self):
        return f'{"white " if self.is_white else "black "}Knight: {self.position}'


class CheckerBoard:
    fields = list(list())
    field_objects: List = list()
    elem_width: int = 0
    elem_height: int = 0

    def __init__(self):
        self.empty_board: Optional[pygame.Surface] = None
        self.cell_size: Optional[Tuple[int]] = None
        self.init_empty_field()

        self.fields: List[List[Optional[Figure]]] = [[None for _ in range(8)] for _ in range(8)]

        self.load_game_from_string('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR')

    def init_empty_field(self):
        self.cell_size = screen.get_width() / 8, screen.get_height() / 8
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

    def load_game_from_string(self, input_string):
        """do some magic, for now just something on the screen"""
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
        screen.blit(self.empty_board, self.empty_board.get_rect())

        for x in range(len(self.fields)):
            for y in range(len(self.fields[x])):
                if not self.fields[x][y]:
                    continue

                self.fields[x][y].draw(screen)


if __name__ == '__main__':
    board = CheckerBoard()
    selected_figure = None
    is_mouse_clicked = False
    running = True
    while running:
        board.draw()
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.K_ESCAPE:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

            if event.type == pygame.WINDOWSIZECHANGED:
                board.init_empty_field()
                rescale_images()

            if not is_mouse_clicked:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    is_mouse_clicked = True
                    mouse_pos = pygame.mouse.get_pos()
                    scale = screen.get_width() / 8, screen.get_height() / 8

                    cols = int(mouse_pos[0] / scale[0])
                    rows = int(mouse_pos[1] / scale[1])

                    if not selected_figure:
                        selected_figure = board.fields[rows][cols]
                        if selected_figure:
                            board.fields[rows][cols].is_selected = True
                    else:
                        old_pos = selected_figure.position
                        if selected_figure.move((cols, rows)):
                            board.fields[old_pos[0]][old_pos[1]] = None
                            board.fields[rows][cols] = selected_figure
                            selected_figure = None
                        else:
                            print(f'Tried moving {selected_figure} -> {(cols, rows)}, not allowed.')
                            selected_figure = None

            if event.type == pygame.MOUSEBUTTONUP:
                is_mouse_clicked = False

    pygame.quit()
