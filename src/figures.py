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
    def __init__(self, pos: Tuple[int, int], is_white: bool, _board: 'CheckerBoard'):  # careful! this one is inverted position in board (x == rows, y == cols)
        self.type: int = FieldType.WHITE if is_white else FieldType.BLACK
        self.is_white: bool = is_white
        self.is_selected = False
        self.en_passant = False
        self.checked_en_passant = False
        self.castles_with: Optional[Figure] = None
        super().__init__(pos, _board)
        # self.allowed_moves: List[Tuple[int, int]] = list()

    def checkmate(self) -> bool:
        """
        Method to signalize checkmate, this is actually only implemented in King
        """
        return False

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
            and ((fig := self.can_move(move)) is not None and fig.is_white != self.is_white)
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
