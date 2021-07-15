from typing import Tuple, List, Optional, Union

import pygame


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
        vals = [(x+i+1, y+i+1) for i in range(length)]

        res = list()
        for _x, _y in vals:
            for i in [-1, 1]:
                res.extend([(_x*i, _y*i), (_x*i, _y), (_x, _y*i)])
        return list(set(filter(lambda val: val[0] >= 0 and val[1] >= 0 and abs(val[0]) < 8 and abs(val[1]) < 8, res)))

    @classmethod
    def get_lines(cls, pos, length):
        x = pos[0]
        y = pos[1]
        vals = [(x+i+1, y) for i in range(length)] + [(x, y+i+1) for i in range(length)]
        vals = list(filter(lambda val: val[0] >= 0 and val[1] >= 0 and abs(val[0]) < 8 and abs(val[1]) < 8, vals))


class Figure(DirectionMixin):
    def __init__(self, pos, is_white, _board):
        self.position = pos  # careful! this one is inverted position (x == rows, y == cols)
        self.type: int = FieldType.WHITE if is_white else FieldType.BLACK
        self.is_white: bool = is_white
        self.board: 'CheckerBoard' = _board
        self.is_selected = False
        self.has_moved = False

    @property
    def allowed_moves(self) -> List[Tuple[int, int]]:
        raise NotImplementedError

    def check_field(self, move) -> Optional['Figure']:
        return self.get_figure_at_target(move)

    def can_move(self, move) -> Optional['Figure']:
        figure_at_target = self.get_figure_at_target(move)
        if figure_at_target is not None:
            return figure_at_target

        diff_x = move[0] - self.position[0]
        diff_y = move[1] - self.position[1]

        if abs(diff_x) > 0 and abs(diff_x) == abs(diff_y):
            # diagonal move
            factors = (1 if diff_x > 0 else -1, 1 if diff_y > 0 else -1,)
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
        return None

    def get_figure_at_target(self, move) -> Optional['Figure']:
        return self.board.fields[move[1]][move[0]]

    def move(self, new_pos) -> bool:
        if self.is_move_allowed(new_pos):  # not self.locked() and self.is_move_allowed(new_pos):
            self.position = new_pos
            self.has_moved = True
            return True
        return False

    def checkmate(self) -> bool:
        return False

    def is_move_allowed(self, move) -> bool:
        raise NotImplementedError

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
                target_fields = cell.get_target_fields()
                if own_king_pos in target_fields:
                    for x in range(abs(own_king_pos[0] - cell.position[0]) + 1):
                        for y in range(abs(own_king_pos[1] - cell.position[1]) + 1):
                            checkmate_positions.append((own_king_pos[0] + x, own_king_pos[1] + y))
        return checkmate_positions

    def clean_target_fields(self, fields) -> List[Tuple[int, int]]:
        """
        Drops fields not present on the board
        :param fields:
        :return:
        """
        cleaned_fields = []
        for field in fields:
            if field[0] < 0 or field[1] < 0:
                continue
            cleaned_fields.append(field)
        return fields

    def get_target_fields(self) -> List[Tuple[int, int]]:
        raise NotImplementedError


class Pawn(Figure):
    """
    TODO:
    - allow initial 2-field step
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

    @property
    def allowed_moves(self) -> List[Tuple[int, int]]:
        direction = -1 if self.is_white else 1
        return list(
            [(self.position[0], self.position[1] + direction)]
            + ([(self.position[0], self.position[1] + (2 * direction))] if not self.has_moved else [])
        )

    def is_move_allowed(self, move) -> bool:
        if abs(move[0] - self.position[0]) == 1 and abs(move[1] - self.position[1]) == 1 \
                and (target_figure := self.get_figure_at_target(move)) is not None:
            return target_figure.is_white != self.is_white

        return ((self.position[0] - move[0]) == 0
                and (abs(move[1] - self.position[1]) <= (1 if self.has_moved else 2))
                # TODO: add sign here => and (move[1]-move[1]) == (-0.0 if self.is_white else 0.0)
                and not self.can_move(move)) or (
                abs(self.position[0] - move[0]) == 1
                and abs(move[1] - self.position[1]) == 1
                and ((fig := self.can_move(move)) and fig.is_white != self.is_white)
        )

    def __str__(self):
        return f'{"white " if self.is_white else "black "}Pawn: {self.position}'

    def get_target_fields(self) -> List[Tuple[int, int]]:
        return self.clean_target_fields(self.allowed_moves)

    def move(self, new_pos) -> bool:
        # todo: this is the place were we need to check if pawn is on last tile on opponents side
        #       then convert pawn into new figure
        allowed = super().move(new_pos)

        if (self.is_white and new_pos[1] == 0) or (not self.is_white and new_pos[1] == 7):
            # we're on the other side
            self.board.needs_render_selector = True
        return allowed


class Queen(Figure):
    def __init__(self, pos, **kwargs):
        super().__init__(pos, **kwargs)
        self.type |= FieldType.QUEEN

    @property
    def allowed_moves(self) -> List[Tuple[int, int]]:
        x = self.position[0]
        y = self.position[1]
        return [
            (x-1, y+1),
            (x+1, y+1),
            (x+1, y-1),
            (x-1, y-1),
            (x-1, y),
            (x, y+1),
            (x+1, y),
            (x, y-1),
        ]

    def is_move_allowed(self, move) -> bool:
        return not (fig := self.can_move(move)) or fig.is_white != self.is_white  # and abs(self.position[0] - move[0]) <= 1 and abs(self.position[1] - move[1]) <= 1

    def __str__(self):
        return f'{"white " if self.is_white else "black "}Queen: {self.position}'

    def get_target_fields(self) -> List[Tuple[int, int]]:
        targets = []
        for x in range(8):
            for y in range(8):
                abs_x = abs(self.position[0] - x)
                abs_y = abs(self.position[1] - y)
                if abs_y == 0 and abs_x == 0:
                    continue
                # potential bug
                if (0 < abs_x == abs_y) \
                        or (abs_x > 0 and abs_y == 0) \
                        or (abs_y > 0 and abs_x == 0):
                    targets.append((x, y))
        return self.clean_target_fields(targets)


class King(Figure):
    def __init__(self, pos, **kwargs):
        super().__init__(pos, **kwargs)
        self.type |= FieldType.KING

    @property
    def allowed_moves(self) -> List[Tuple[int, int]]:
        x = self.position[0]
        y = self.position[1]
        return [
            (x-1, y+1),
            (x+1, y+1),
            (x+1, y-1),
            (x-1, y-1),
            (x-1, y),
            (x, y+1),
            (x+1, y),
            (x, y-1),
        ]

    def is_move_allowed(self, move) -> bool:
        # (abs(move[0]) <= 1 and abs(move[1]) <= 1) and (not (abs(move[0]) == 1 and abs(move[1]) == 1))

        return abs(self.position[0] - move[0]) <= 1 and abs(self.position[1] - move[1]) <= 1 and (not (fig := self.can_move(move)) or fig.is_white != self.is_white)

    def __str__(self):
        return f'{"white " if self.is_white else "black "}King: {self.position}'

    def checkmate(self) -> bool:
        return True

    def get_target_fields(self) -> List[Tuple[int, int]]:
        return self.clean_target_fields(
            [(self.position[0] + i, self.position[1] + j) for i in range(-1, 1, 2) for j in range(-1, 1, 2)])


class Rook(Figure):
    def __init__(self, pos, **kwargs):
        super().__init__(pos, **kwargs)
        self.type |= FieldType.ROOK

    @property
    def allowed_moves(self) -> List[Tuple[int, int]]:
        x = self.position[0]
        y = self.position[1]
        return [
            (x-1, y),
            (x, y-1),
            (x+1, y),
            (x, y+1),
        ]

    def is_move_allowed(self, move) -> bool:
        return (abs(self.position[0] - move[0]) <= 1) != (abs(self.position[1] - move[1]) <= 1) \
               and (not (fig := self.can_move(move)) or fig.is_white != self.is_white)

    def __str__(self):
        return f'{"white " if self.is_white else "black "}Rook: {self.position}'

    def get_target_fields(self) -> List[Tuple[int, int]]:
        return self.clean_target_fields(
            [(i, self.position[1]) for i in range(8, 1) if i != self.position[0]]
            + [(self.position[0], i) for i in range(8, 1) if i != self.position[1]]
        )


class Bishop(Figure):
    def __init__(self, pos, **kwargs):
        super().__init__(pos, **kwargs)
        self.type |= FieldType.BISHOP

    @property
    def allowed_moves(self) -> List[Tuple[int, int]]:
        return self.get_diagonals(self.position, 8)

    def is_move_allowed(self, move) -> bool:
        return abs(self.position[0] - move[0]) == abs(self.position[1] - move[1]) and (not (fig := self.can_move(move)) or fig.is_white != self.is_white)

    def __str__(self):
        return f'{"white " if self.is_white else "black "}Bishop: {self.position}'

    def get_target_fields(self) -> List[Tuple[int, int]]:
        targets = []
        for i in range(self.position[0]):
            if self.position[1] - i >= 0:
                targets.append((self.position[0] - i, self.position[1] - i))
        for i in range(self.position[1]):
            if self.position[0] - i >= 0:
                targets.append((self.position[0] - i, self.position[1] - i))
        for i in range(self.position[0], 8):
            if self.position[1] + i >= 0:
                targets.append((self.position[0] + i, self.position[1] + i))
        for i in range(self.position[1], 8):
            if self.position[0] - i >= 0:
                targets.append((self.position[0] + i, self.position[1] + i))

        return self.clean_target_fields(targets)


class Knight(Figure):
    def __init__(self, pos, **kwargs):
        super().__init__(pos, **kwargs)
        self.type |= FieldType.KNIGHT

    @property
    def allowed_moves(self) -> List[Tuple[int, int]]:
        x = self.position[0]
        y = self.position[1]
        return [
            (x - 1, y - 2), (x - 2, y - 1),
            (x + 1, y - 2), (x + 2, y - 1),
            (x - 1, y + 2), (x - 2, y + 1),
            (x + 1, y + 2), (x + 2, y + 1)
        ]

    def is_move_allowed(self, move) -> bool:
        abs_x = abs(self.position[0] - move[0])
        abs_y = abs(self.position[1] - move[1])
        return (((abs_x == 1 and abs_y == 2) or (abs_x == 2 and abs_y == 1))
                and (not (fig := self.can_move(move)) or fig.is_white != self.is_white))

    def __str__(self):
        return f'{"white " if self.is_white else "black "}Knight: {self.position}'

    def get_target_fields(self) -> List[Tuple[int, int]]:
        return self.clean_target_fields(self.allowed_moves)

    def clean_target_fields(self, fields) -> List[Tuple[int, int]]:
        # overrides parent method
        return fields


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
