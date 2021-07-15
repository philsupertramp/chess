from typing import Tuple, List, Optional, Union

import pygame

from src.helpers import sign


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


def scale_figure(figure: pygame.Surface, canvas: pygame.Surface):
    ratio = (int(canvas.get_width() / 8), int(canvas.get_height() / 8))
    return pygame.transform.scale(figure, ratio)


figures = dict()


def reload_images():
    global figures

    figures = {
        FieldType.QUEEN | FieldType.BLACK: pygame.image.load('resources/queen.png').convert_alpha(),
        FieldType.KING | FieldType.BLACK: pygame.image.load('resources/king.png').convert_alpha(),
        FieldType.ROOK | FieldType.BLACK: pygame.image.load('resources/rook.png').convert_alpha(),
        FieldType.KNIGHT | FieldType.BLACK: pygame.image.load('resources/knight.png').convert_alpha(),
        FieldType.BISHOP | FieldType.BLACK: pygame.image.load('resources/bishop.png').convert_alpha(),
        FieldType.PAWN | FieldType.BLACK: pygame.image.load('resources/pawn.png').convert_alpha(),

        FieldType.QUEEN | FieldType.WHITE: pygame.image.load('resources/queen_w.png').convert_alpha(),
        FieldType.KING | FieldType.WHITE: pygame.image.load('resources/king_w.png').convert_alpha(),
        FieldType.ROOK | FieldType.WHITE: pygame.image.load('resources/rook_w.png').convert_alpha(),
        FieldType.KNIGHT | FieldType.WHITE: pygame.image.load('resources/knight_w.png').convert_alpha(),
        FieldType.BISHOP | FieldType.WHITE: pygame.image.load('resources/bishop_w.png').convert_alpha(),
        FieldType.PAWN | FieldType.WHITE: pygame.image.load('resources/pawn_w.png').convert_alpha(),
    }


def rescale_images(canvas):
    reload_images()
    global figures
    figures = {key: scale_figure(figure, canvas) for key, figure in figures.items()}


class DirectionMixin:
    @classmethod
    def is_diagonal(cls, new_pos: Tuple[int, int], max_length: int = 1) -> bool:
        return (abs(new_pos[0]) + abs(new_pos[1])) / 2 == abs(new_pos[0]) and abs(new_pos[0]) <= max_length

    @classmethod
    def is_line(cls, new_pos, max_length) -> bool:
        return (new_pos[0] == 0 or new_pos[1] == 0) and abs(new_pos[0]) <= max_length

    @classmethod
    def get_diagonals(cls, pos, length) -> List[Tuple[int, int]]:
        x = pos[0]
        y = pos[1]

        res = list()
        for _x in range(1, length + 1):
            res.extend([(x+_x, y+_x), (x-_x, y-_x), (x-_x, y+_x), (x+_x, y-_x)])
        return list(set(filter(lambda val: val[0] >= 0 and val[1] >= 0 and abs(val[0]) < 8 and abs(val[1]) < 8, res)))

    @classmethod
    def get_lines(cls, pos, length):
        x = pos[0]
        y = pos[1]

        res = list()
        for _x in range(1, length + 1):
            res.extend([(x + _x, y), (x - _x, y), (x, y + _x), (x, y - _x)])
        return list(set(filter(lambda val: val[0] >= 0 and val[1] >= 0 and abs(val[0]) < 8 and abs(val[1]) < 8, res)))


class Figure(DirectionMixin):
    def __init__(self, pos, is_white, _board):
        self.position = pos  # careful! this one is inverted position (x == rows, y == cols)
        self.type: int = FieldType.WHITE if is_white else FieldType.BLACK
        self.is_white: bool = is_white
        self.board: 'CheckerBoard' = _board
        self.is_selected = False
        self.has_moved = False
        self.can_jump = False
        self.allowed_moves: List[Tuple[int, int]] = list()

    def update_allowed_moves(self) -> None:
        raise NotImplementedError

    def check_field(self, move) -> Optional['Figure']:
        return self.board.fields[move[1]][move[0]]

    def can_move(self, move) -> Optional['Figure']:
        """
        Determines whether a move can be performed or not

        :param move: the actual tile location to move to
        :return: Figure or None, None is considered good and successful
        """
        if move not in self.allowed_moves:
            # idk, there's no other way then providing an arbitrary object here
            return Figure((-1, -1), self.is_white, self.board)

        if self.can_jump:
            return None

        diff_x = move[0] - self.position[0]
        diff_y = move[1] - self.position[1]

        if abs(diff_x) > 0 and abs(diff_x) == abs(diff_y):
            # diagonal move
            factors = (sign(diff_x), sign(diff_y))
            for i in range(1, min(abs(diff_x) + 1, 8)):
                if fig := self.check_field((self.position[0] + factors[0] * i, self.position[1] + factors[1] * i)):
                    return fig
        elif abs(diff_x) > 0:
            # x direction
            factor = (-1) if diff_x < 0 else 1
            for i in range(1, min(abs(diff_x) + 1, 8)):
                if fig := self.check_field((self.position[0] + factor * i, self.position[1])):
                    return fig
        elif abs(diff_y) > 0:
            # y direction
            factor = (-1) if diff_y < 0 else 1
            for i in range(1, min(abs(diff_y) + 1, 8)):
                if fig := self.check_field((self.position[0], self.position[1] + factor * i)):
                    return fig

        return self.check_field(move)

    def move(self, new_pos) -> bool:
        if self.is_move_allowed(new_pos):  # not self.locked() and self.is_move_allowed(new_pos):
            self.position = new_pos
            self.has_moved = True
            self.update_allowed_moves()
            return True
        return False

    def checkmate(self) -> bool:
        return False

    def is_move_allowed(self, move) -> bool:
        fig = self.can_move(move)
        return not fig or (fig.position[0] == move[0] and fig.position[1] == move[1] and fig.is_white != self.is_white)

    def draw(self, canvas: pygame.Surface) -> None:
        if self.type == FieldType.EMPTY:
            return

        if self.is_selected:
            self.draw_allowed_moves(canvas)

        scale = canvas.get_width() / 8, canvas.get_height() / 8
        figure = figures.get(self.type).copy()
        if self.is_selected:
            figure.convert_alpha()
            figure.set_colorkey((255, 0, 255))

        canvas.blit(figure, (scale[0] * self.position[0], scale[1] * self.position[1]))

    def draw_allowed_moves(self, canvas: pygame.Surface) -> None:
        square_size = int(canvas.get_width() / 8), int(canvas.get_height() / 8)
        mask = pygame.Surface(canvas.get_size(), pygame.SRCALPHA)
        for move in self.allowed_moves:
            pygame.draw.rect(mask, (0, 0, 0, 100), (move[0] * square_size[0], move[1] * square_size[1], square_size[0], square_size[1]))

        canvas.blit(mask, mask.get_rect())

    def locked(self) -> bool:
        """
        :return: False if figure would allow checkmate
        """
        positions = self.__get_checkmate_positions()
        return self.position in positions

    def __get_checkmate_positions(self) -> List[Tuple[int, ...]]:
        own_king_pos: Tuple[int, int] = (-1, -1)
        for row in self.board.fields:
            for cell in row:
                if not cell:
                    continue
                if cell.type - FieldType.KING == (FieldType.WHITE if self.is_white else FieldType.BLACK):
                    own_king_pos = cell.position

        assert own_king_pos != (-1, -1), 'Did not find King... Something is wrong!'

        checkmate_positions: List[Tuple[int, ...]] = list()
        for row in self.board.fields:
            for cell in row:
                if not cell or cell.is_white == self.is_white:
                    continue
                target_fields = cell.allowed_moves
                if own_king_pos in target_fields:
                    for x in range(abs(own_king_pos[0] - cell.position[0]) + 1):
                        for y in range(abs(own_king_pos[1] - cell.position[1]) + 1):
                            checkmate_positions.append((own_king_pos[0] + x, own_king_pos[1] + y))
        return checkmate_positions

    @staticmethod
    def clean_target_fields(fields: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """
        Drops fields not present on the board
        :param fields:
        :return:
        """
        cleaned_fields = []
        for field in fields:
            if field[0] < 0 or field[1] < 0 or field[0] > 7 or field[1] > 7:
                continue
            cleaned_fields.append(field)
        return cleaned_fields


class Pawn(Figure):
    """
    TODO:
    - fix allowed_move for diagonal checks
    - disallow non-diagonal checks
    - en passant-Rule is pretty fucked up, but here's how it works
        - previous move was opponent pawn
        - previous pawn moved 2 steps
        - self is allowed to move to field in between opponents last move and checks opponents pawn
        i.e. moves: Pc7–c5 pd5-c6 -> Pc5 checked
    """

    def __init__(self, pos, **kwargs):
        super().__init__(pos, **kwargs)
        self.type |= FieldType.PAWN
        self.update_allowed_moves()

    def update_allowed_moves(self) -> None:
        direction = -1 if self.is_white else 1

        # TODO: fixit
        # right
        if 0 < self.position[0] - direction < 8 and 0 < self.position[1] + direction < 8:
            pos = (self.position[0] - direction, self.position[1] + direction)
            fig = self.board.fields[pos[1]][pos[0]]
            if fig:
                if fig.is_white != self.is_white:
                    if self.position not in fig.allowed_moves:
                        fig.update_allowed_moves()
                    self.allowed_moves.append(pos)

        # left
        if 0 < self.position[0] + direction < 8 and 0 < self.position[1] - direction < 8:
            pos = (self.position[0] + direction, self.position[1] - direction)
            fig = self.board.fields[pos[1]][pos[0]]
            if fig:
                if fig.is_white != self.is_white:
                    if self.position not in fig.allowed_moves:
                        fig.update_allowed_moves()
                    self.allowed_moves.append(pos)

        self.allowed_moves += list(
            [(self.position[0], self.position[1] + direction)]
            + ([(self.position[0], self.position[1] + (2 * direction))] if not self.has_moved else [])
        )

    def is_move_allowed(self, move) -> bool:
        return (
                (sign(move[1] - self.position[1]) == (-1 if self.is_white else 1))
                and (self.is_valid_move(move) or self.is_valid_check(move))
        )

    def is_valid_check(self, move):
        # is unblocked move in column
        return (
                abs(self.position[0] - move[0]) == 1
                and abs(move[1] - self.position[1]) == 1
                and ((fig := self.can_move(move)) and fig.is_white != self.is_white)
        )

    def is_valid_move(self, move):
        # is unblocked move in column
        return ((self.position[0] - move[0]) == 0
                and (abs(move[1] - self.position[1]) <= (1 if self.has_moved else 2))
                and not self.can_move(move))

    def __str__(self):
        return f'{"white " if self.is_white else "black "}Pawn: {self.position}'

    def move(self, new_pos) -> bool:
        allowed = super().move(new_pos)

        if (self.is_white and new_pos[1] == 0) or (not self.is_white and new_pos[1] == 7):
            # we're on the other side
            self.board.needs_render_selector = True
        return allowed


class Queen(Figure):
    def __init__(self, pos, **kwargs):
        super().__init__(pos, **kwargs)
        self.type |= FieldType.QUEEN
        self.update_allowed_moves()

    def update_allowed_moves(self) -> None:
        self.allowed_moves = self.get_diagonals(self.position, 8) + self.get_lines(self.position, 8)

    def __str__(self):
        return f'{"white " if self.is_white else "black "}Queen: {self.position}'


class King(Figure):
    def __init__(self, pos, **kwargs):
        super().__init__(pos, **kwargs)
        self.type |= FieldType.KING
        self.update_allowed_moves()

    def update_allowed_moves(self) -> None:
        self.allowed_moves = self.get_diagonals(self.position, 1) + self.get_lines(self.position, 1)

    def __str__(self):
        return f'{"white " if self.is_white else "black "}King: {self.position}'

    def checkmate(self) -> bool:
        return True


class Rook(Figure):
    def __init__(self, pos, **kwargs):
        super().__init__(pos, **kwargs)
        self.type |= FieldType.ROOK
        self.update_allowed_moves()

    def update_allowed_moves(self) -> None:
        self.allowed_moves = self.get_lines(self.position, 8)

    def __str__(self):
        return f'{"white " if self.is_white else "black "}Rook: {self.position}'


class Bishop(Figure):
    def __init__(self, pos, **kwargs):
        super().__init__(pos, **kwargs)
        self.type |= FieldType.BISHOP
        self.update_allowed_moves()

    def update_allowed_moves(self) -> None:
        self.allowed_moves = self.get_diagonals(self.position, 8)

    def __str__(self):
        return f'{"white " if self.is_white else "black "}Bishop: {self.position}'


class Knight(Figure):
    def __init__(self, pos, **kwargs):
        super().__init__(pos, **kwargs)
        self.type |= FieldType.KNIGHT
        self.can_jump = True
        self.update_allowed_moves()

    def update_allowed_moves(self) -> None:
        x = self.position[0]
        y = self.position[1]
        self.allowed_moves = self.clean_target_fields([
            (x - 1, y - 2), (x - 2, y - 1),
            (x + 1, y - 2), (x + 2, y - 1),
            (x - 1, y + 2), (x - 2, y + 1),
            (x + 1, y + 2), (x + 2, y + 1)
        ])

    def __str__(self):
        return f'{"white " if self.is_white else "black "}Knight: {self.position}'


class FigureChange:
    def __init__(self, figure: 'Figure', new_figure_type: Union[FieldType, int]):
        self.prev_figure = figure
        self.new_figure: Optional[Figure] = None
        self.set_new_figure(new_figure_type)

    def set_new_figure(self, figure_type) -> None:
        is_white = self.prev_figure.is_white
        if figure_type == FieldType.QUEEN:
            self.new_figure = Queen(self.prev_figure.position, is_white=is_white, _board=self.prev_figure.board)
        elif figure_type == FieldType.KNIGHT:
            self.new_figure = Knight(self.prev_figure.position, is_white=is_white, _board=self.prev_figure.board)
        elif figure_type == FieldType.ROOK:
            self.new_figure = Rook(self.prev_figure.position, is_white=is_white, _board=self.prev_figure.board)
        elif figure_type == FieldType.BISHOP:
            self.new_figure = Bishop(self.prev_figure.position, is_white=is_white, _board=self.prev_figure.board)
