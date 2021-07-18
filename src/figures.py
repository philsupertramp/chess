from typing import Tuple, List, Optional, Union

import pygame

from src.helpers import sign
from src.movable import Movable


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

    @classmethod
    def clear(cls, val: int) -> int:
        if val - cls.BLACK > 0:
            return val - cls.BLACK
        return val - cls.WHITE


def scale_figure(figure: pygame.Surface, canvas: pygame.Surface) -> pygame.Surface:
    """
    Helper method to rescale figure texture. A figure will be 1/8th of canvas' dimensions

    :param figure: figure texture/surface
    :param canvas: the canvas to scale the figure with
    :return:
    """
    ratio = (int(canvas.get_width() / 8), int(canvas.get_height() / 8))
    return pygame.transform.scale(figure, ratio)


# global state for figure textures
figures = dict()


def reload_images() -> None:
    """
    Loads unscaled figure textures into memory
    :return:
    """
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


def rescale_images(canvas: pygame.Surface) -> None:
    """
    Helper method to rescale all figure-textures based on a given canvas.
    Each figure will be scaled 1/8th of the canvas input

    :param canvas: canvas to scale based on
    """
    reload_images()
    global figures
    figures = {key: scale_figure(figure, canvas) for key, figure in figures.items()}


class Figure(Movable):
    def __init__(self, pos: Tuple[int, int], is_white: bool, _board: 'CheckerBoard'):
        self.position = pos  # careful! this one is inverted position in board (x == rows, y == cols)
        self.type: int = FieldType.WHITE if is_white else FieldType.BLACK
        self.is_white: bool = is_white
        self.board: 'CheckerBoard' = _board
        self.is_selected = False
        self.has_moved = False
        self.can_jump = False
        self.en_passant = False
        self.checked_en_passant = False
        self.castles_with: Optional[Figure] = None
        # self.allowed_moves: List[Tuple[int, int]] = list()

    @property
    def allowed_moves(self) -> List[Tuple[int, int]]:
        """
        Helper method to get all available moves of a figure

        :return: list of possible moves
        """
        raise NotImplementedError

    def check_field(self, move: Tuple[int, int]) -> Optional['Figure']:
        """
        Helper to detect figure on given tile
        """
        return self.board.fields[move[1]][move[0]]

    def can_move(self, move: Tuple[int, int]) -> Optional['Figure']:
        """
        Determines whether a move can be performed or not

        :param move: the actual tile location to move to
        :return: Figure or None, None is considered good and successful
        """
        if move not in self.allowed_moves:
            # idk, there's no other way then providing an arbitrary object here
            return Figure((-1, -1), self.is_white, self.board)

        figure_at_pos = self.check_field(move)

        if self.can_jump:
            return figure_at_pos

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

        return figure_at_pos

    def move(self, new_pos: Tuple[int, int]) -> bool:
        """
        Moves a figure to a new given position, checks and return success

        :param new_pos: position to move the figure to, potentially
        :return: successfully moved figure
        """
        if self.is_move_allowed(new_pos):  # not self.locked() and self.is_move_allowed(new_pos):
            self.position = new_pos
            self.has_moved = True
            return True
        return False

    def checkmate(self) -> bool:
        """
        Method to signalize checkmate, this is actually only implemented in King
        """
        return False

    def is_move_allowed(self, move: Tuple[int, int]) -> bool:
        """
        Tests if a move is allowed to be performed

        :param move: potential tile to move to
        """
        fig = self.can_move(move)
        return not fig or (fig.position[0] == move[0] and fig.position[1] == move[1] and fig.is_white != self.is_white)

    def draw(self, canvas: pygame.Surface) -> None:
        """
        Renders figure (incl. allowed moves) onto given canvas

        :param canvas: canvas to draw to
        """
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
        """
        Helper method to render allowed moves of a figure onto a canvas

        :param canvas: canvas to draw to
        """
        square_size = int(canvas.get_width() / 8), int(canvas.get_height() / 8)
        mask = pygame.Surface(canvas.get_size(), pygame.SRCALPHA)
        for move in self.allowed_moves:
            pos = (move[0] * square_size[0], move[1] * square_size[1], square_size[0], square_size[1])
            pygame.draw.rect(mask, (0, 0, 0, 100), pos)

        canvas.blit(mask, mask.get_rect())

    def locked(self) -> bool:
        """
        :return: False if figure would allow checkmate
        """
        positions = self.__get_checkmate_positions()
        return self.position in positions

    def __get_checkmate_positions(self) -> List[Tuple[int, ...]]:
        """
        TODO: fix me
        """
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
        Drops fields not present on the 8x8 board
        :param fields: list of fields to clean
        :return: cleaned list of provided fields
        """
        cleaned_fields = []
        for field in fields:
            if field[0] < 0 or field[1] < 0 or field[0] > 7 or field[1] > 7:
                continue
            cleaned_fields.append(field)
        return cleaned_fields


class Pawn(Figure):
    def __init__(self, pos: Tuple[int, int], **kwargs):
        super().__init__(pos, **kwargs)
        self.type |= FieldType.PAWN

    @property
    def allowed_moves(self) -> List[Tuple[int, int]]:
        direction = -1 if self.is_white else 1
        moves = list()

        # right
        if 0 < self.position[0] - direction < 8 and 0 < self.position[1] + direction < 8:
            pos = (self.position[0] - direction, self.position[1] + direction)
            fig = self.board.fields[pos[1]][pos[0]]
            if fig:
                if fig.is_white != self.is_white:
                    moves.append(pos)

        # left
        if 0 < self.position[0] + direction < 8 and 0 < self.position[1] - direction < 8:
            pos = (self.position[0] + direction, self.position[1] + direction)
            fig = self.board.fields[pos[1]][pos[0]]
            if fig:
                if fig.is_white != self.is_white:
                    moves.append(pos)

        # check for en-passant rule neighbor pawns
        en_passant_moves = self.clean_target_fields([(self.position[0] - direction, self.position[1]),
                                                     (self.position[0] + direction, self.position[1])])
        for pos in en_passant_moves:
            fig = self.board.fields[pos[1]][pos[0]]
            if fig:
                if fig.is_white != self.is_white and fig.en_passant:
                    moves.append((pos[0], pos[1] + direction))

        moves += list(
            [(self.position[0], self.position[1] + direction)]
            + ([(self.position[0], self.position[1] + (2 * direction))] if not self.has_moved else [])
        )
        return moves

    def is_move_allowed(self, move: Tuple[int, int]) -> bool:
        return (
            (sign(move[1] - self.position[1]) == (-1 if self.is_white else 1))
            and (self.is_valid_move(move) or self.is_valid_check(move))
        )

    def is_valid_check(self, move):
        """
        Test for diagonal, or en-passant check
        """
        direction = -1 if self.is_white else 1
        # is unblocked move in column
        if ((en_passant_fig := self.check_field(
            (move[0],
             move[1] - direction))) and en_passant_fig.is_white != self.is_white and en_passant_fig.en_passant):
            self.checked_en_passant = True
            return True

        return (
            abs(self.position[0] - move[0]) == 1
            and abs(move[1] - self.position[1]) == 1
            and ((fig := self.can_move(move)) and fig.is_white != self.is_white)
        )

    def is_valid_move(self, move: Tuple[int, int]) -> bool:
        """
        Test for regular directed movement, either 2 tiles for unmoved pawns, or 1 tile for moved pawns
        """
        # is unblocked move in column
        return ((self.position[0] - move[0]) == 0
                and (abs(move[1] - self.position[1]) <= (1 if self.has_moved else 2))
                and not self.can_move(move))

    def __str__(self) -> str:
        return f'{"white " if self.is_white else "black "}Pawn: {self.position}'

    def move(self, new_pos: Tuple[int, int]) -> bool:
        """
        Overridden method to test for en-passant and figure promotions
        """
        pos = self.position
        allowed = super().move(new_pos)

        if allowed:
            self.en_passant = abs(new_pos[1] - pos[1]) == 2

        if (self.is_white and new_pos[1] == 0) or (not self.is_white and new_pos[1] == 7):
            # we're on the other side
            self.board.needs_render_selector = True
        return allowed


class Queen(Figure):
    def __init__(self, pos: Tuple[int, int], **kwargs):
        super().__init__(pos, **kwargs)
        self.type |= FieldType.QUEEN

    @property
    def allowed_moves(self) -> List[Tuple[int, int]]:
        return self.get_diagonals(self.position, 8) + self.get_lines(self.position, 8)

    def __str__(self) -> str:
        return f'{"white " if self.is_white else "black "}Queen: {self.position}'


class King(Figure):
    def __init__(self, pos: Tuple[int, int], **kwargs):
        super().__init__(pos, **kwargs)
        self.type |= FieldType.KING
        self.can_castle = True

    @property
    def allowed_moves(self) -> List[Tuple[int, int]]:
        castle_positions = self.get_castles() if self.can_castle else []
        return castle_positions + self.get_diagonals(self.position, 1) + self.get_lines(self.position, 1)

    def get_castles(self) -> List[Tuple[int, int]]:
        rooks = self.board.get_figures(FieldType.ROOK | (FieldType.WHITE if self.is_white else FieldType.BLACK))
        rooks = list(filter(lambda r: not r.has_moved and self.position[1] == r.position[1], rooks))
        out = list()
        for rook in rooks:
            not_rook = False
            # TODO: allow vertical, if explicitly configured
            sign_x = sign(rook.position[0] - self.position[0])
            for x in range(self.position[0] + sign_x, rook.position[0], sign_x):
                fig = self.check_field((x, self.position[1]))
                if fig is not None:
                    not_rook = True
                    break
            if not not_rook:
                out.append(rook.position)
        return out

    def __str__(self) -> str:
        return f'{"white " if self.is_white else "black "}King: {self.position}'

    def checkmate(self) -> bool:
        return True

    def move(self, new_pos: Tuple[int, int]) -> bool:
        castles = [c for c in self.get_castles() if new_pos[0] == c[0] and new_pos[1] == c[1]]
        if len(castles) > 0:
            self.castles_with = self.check_field(new_pos)
            self.position = new_pos
            return True
        moved = super().move(new_pos)
        self.can_castle = not moved
        return moved

    def is_move_allowed(self, move: Tuple[int, int]) -> bool:
        return super().is_move_allowed(move)


class Rook(Figure):
    def __init__(self, pos: Tuple[int, int], **kwargs) -> None:
        super().__init__(pos, **kwargs)
        self.type |= FieldType.ROOK

    @property
    def allowed_moves(self) -> List[Tuple[int, int]]:
        return self.get_lines(self.position, 8)

    def __str__(self) -> str:
        return f'{"white " if self.is_white else "black "}Rook: {self.position}'


class Bishop(Figure):
    def __init__(self, pos, **kwargs):
        super().__init__(pos, **kwargs)
        self.type |= FieldType.BISHOP

    @property
    def allowed_moves(self) -> List[Tuple[int, int]]:
        return self.get_diagonals(self.position, 8)

    def __str__(self):
        return f'{"white " if self.is_white else "black "}Bishop: {self.position}'


class Knight(Figure):
    def __init__(self, pos: Tuple[int, int], **kwargs):
        super().__init__(pos, **kwargs)
        self.type |= FieldType.KNIGHT
        self.can_jump = True

    @property
    def allowed_moves(self) -> List[Tuple[int, int]]:
        x = self.position[0]
        y = self.position[1]
        return self.clean_target_fields([
            (x - 1, y - 2), (x - 2, y - 1),
            (x + 1, y - 2), (x + 2, y - 1),
            (x - 1, y + 2), (x - 2, y + 1),
            (x + 1, y + 2), (x + 2, y + 1)
        ])

    def __str__(self) -> str:
        return f'{"white " if self.is_white else "black "}Knight: {self.position}'


class FigureChange:
    def __init__(self, figure: 'Figure', new_figure_type: Union[FieldType, int]) -> None:
        self.prev_figure = figure
        self.new_figure: Optional[Figure] = None
        self.set_new_figure(new_figure_type)

    def set_new_figure(self, figure_type: int) -> None:
        is_white = self.prev_figure.is_white
        if figure_type == FieldType.QUEEN:
            self.new_figure = Queen(self.prev_figure.position, is_white=is_white, _board=self.prev_figure.board)
        elif figure_type == FieldType.KNIGHT:
            self.new_figure = Knight(self.prev_figure.position, is_white=is_white, _board=self.prev_figure.board)
        elif figure_type == FieldType.ROOK:
            self.new_figure = Rook(self.prev_figure.position, is_white=is_white, _board=self.prev_figure.board)
        elif figure_type == FieldType.BISHOP:
            self.new_figure = Bishop(self.prev_figure.position, is_white=is_white, _board=self.prev_figure.board)
