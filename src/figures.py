from typing import List, Optional

from src.helpers import sign, Coords
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


# global state for figure textures
figures = dict()


def rescale_images(canvas: 'pygame.Surface') -> None:
    """
    Helper method to rescale all figure-textures based on a given canvas.
    Each figure will be scaled 1/8th of the canvas input

    :param canvas: canvas to scale based on
    """
    import pygame
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

    ratio = (int(canvas.get_width() / 8), int(canvas.get_height() / 8))

    def scale_figure(figure):
        return pygame.transform.scale(figure, ratio)

    figures = {key: scale_figure(figure) for key, figure in figures.items()}


class Figure(Movable):
    def __init__(self, pos: Coords, is_white: bool, _board: 'CheckerBoard'):
        self.type: int = FieldType.WHITE if is_white else FieldType.BLACK
        self.is_white: bool = is_white
        self.is_selected = False
        self.en_passant = False
        self.checked_en_passant = False
        self.castles_with: Optional[Figure] = None
        super().__init__(pos, _board)

    def checkmate(self) -> bool:
        """
        Method to signalize checkmate, this is actually only implemented in King
        """
        return False

    def draw(self, canvas: 'pygame.Surface') -> None:
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

        canvas.blit(figure, (scale[0] * self.position.x, scale[1] * self.position.y))

    def draw_allowed_moves(self, canvas: 'pygame.Surface') -> None:
        """
        Helper method to render allowed moves of a figure onto a canvas

        :param canvas: canvas to draw to
        """
        import pygame
        square_size = self.board.cell_size
        mask = pygame.Surface(canvas.get_size(), pygame.SRCALPHA)
        for move in self.remove_set(self.allowed_moves):
            pos = (move.x * square_size[0], move.y * square_size[1], square_size[0], square_size[1])
            pygame.draw.rect(mask, (0, 0, 0, 100), pos)

        canvas.blit(mask, mask.get_rect())


class Pawn(Figure):
    def __init__(self, pos: Coords, **kwargs):
        super().__init__(pos, **kwargs)
        self.type |= FieldType.PAWN
        self.direction = -1 if self.is_white else 1

    @property
    def allowed_moves(self) -> List[Coords]:
        moves = list()

        # right
        if -1 < self.position.x - self.direction < 8 and -1 < self.position.y + self.direction < 8:
            pos = Coords(self.position.x - self.direction, self.position.y + self.direction)
            fig = self.board.fields[pos.y][pos.x]
            if fig:
                if fig.is_white != self.is_white:
                    moves.append(pos)

        # left
        if -1 < self.position.x + self.direction < 8 and -1 < self.position.y - self.direction < 8:
            pos = Coords(self.position.x + self.direction, self.position.y + self.direction)
            fig = self.board.fields[pos.row][pos.col]
            if fig:
                if fig.is_white != self.is_white:
                    moves.append(pos)

        # check for en-passant rule neighbor pawns
        en_passant_moves = self.clean_target_fields([Coords(self.position.x - self.direction, self.position.y),
                                                     Coords(self.position.x + self.direction, self.position.y)])
        for pos in en_passant_moves:
            fig = self.board.fields[pos.y][pos.x]
            if fig:
                if fig.is_white != self.is_white and fig.en_passant:
                    moves.append(Coords(pos.x, pos.y + self.direction))

        moves += list(
            [Coords(self.position.x, self.position.y + self.direction)]
            + ([Coords(self.position.x, self.position.y + (2 * self.direction))] if not self.has_moved else [])
        )
        return moves

    def remove_set(self, coords):
        new_coords = super().remove_set(coords)
        out = list()
        for coord in new_coords:
            if coord in [Coords(self.position.y + self.direction, self.position.x),
                         Coords(self.position.y + 2 * self.direction, self.position.x)] \
                    and self.check_field(coord) is not None:
                continue
            out.append(coord)

        return out

    def is_move_allowed(self, move: Coords) -> bool:
        return (
            (sign(move.y - self.position.y) == (-1 if self.is_white else 1))
            and (self.is_valid_move(move) or self.is_valid_check(move))
        )

    def is_valid_check(self, move):
        """
        Test for diagonal, or en-passant check
        """
        # is unblocked move in column
        if ((en_passant_fig := self.check_field(Coords(move.x, move.y - self.direction)))
                and en_passant_fig.is_white != self.is_white and en_passant_fig.en_passant):
            self.checked_en_passant = True
            return True

        return (
            self.is_diagonal(move - self.position)
            and ((fig := self.can_move(move)) is not None and not isinstance(fig, bool) and fig.is_white != self.is_white)
        )

    def is_valid_move(self, move: Coords) -> bool:
        """
        Test for regular directed movement, either 2 tiles for unmoved pawns, or 1 tile for moved pawns
        """
        # is unblocked move in column
        return ((self.position.x - move.x) == 0
                and (abs(move.y - self.position.y) <= (1 if self.has_moved else 2))
                # no figure in target field
                and self.can_move(move) is None)

    def __str__(self) -> str:
        return f'{"white " if self.is_white else "black "}Pawn: {self.position}'

    def move(self, new_pos: Coords) -> bool:
        """
        Overridden method to test for en-passant and figure promotions
        """
        pos = self.position
        allowed = super().move(new_pos)

        if allowed:
            self.en_passant = abs(new_pos.y - pos.y) == 2

        if (self.is_white and new_pos.y == 0) or (not self.is_white and new_pos.y == 7):
            # we're on the other side
            self.board.needs_render_selector = True
        return allowed


class Queen(Figure):
    def __init__(self, pos: Coords, **kwargs):
        super().__init__(pos, **kwargs)
        self.type |= FieldType.QUEEN

    @property
    def allowed_moves(self) -> List[Coords]:
        return self.get_diagonals(self.position, 8) + self.get_lines(self.position, 8)

    def __str__(self) -> str:
        return f'{"white " if self.is_white else "black "}Queen: {self.position}'


class King(Figure):
    def __init__(self, pos: Coords, **kwargs):
        super().__init__(pos, **kwargs)
        self.type |= FieldType.KING
        self.can_castle = True

    @property
    def allowed_moves(self) -> List[Coords]:
        castle_positions = self.get_castles() if self.can_castle else []
        return castle_positions + self.get_diagonals(self.position, 1) + self.get_lines(self.position, 1)

    def get_castles(self) -> List[Coords]:
        rooks = self.board.get_figures(FieldType.ROOK | (FieldType.WHITE if self.is_white else FieldType.BLACK))
        rooks = list(filter(lambda r: not r.has_moved and self.position.y == r.position.y, rooks))
        out = list()
        for rook in rooks:
            not_rook = False
            # TODO: allow vertical, if explicitly configured
            sign_x = sign(rook.position.x - self.position.x)
            for x in range(self.position.x + sign_x, rook.position.x, sign_x):
                fig = self.check_field(Coords(x, self.position.y))
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

    def move(self, new_pos: Coords) -> bool:
        castles = [c for c in self.get_castles() if new_pos.x == c.x and new_pos.y == c.y]
        if len(castles) > 0:
            self.castles_with = self.check_field(new_pos)
            self.position = new_pos
            return True
        moved = super().move(new_pos)
        self.can_castle = not moved
        return moved


class Rook(Figure):
    def __init__(self, pos: Coords, **kwargs) -> None:
        super().__init__(pos, **kwargs)
        self.type |= FieldType.ROOK

    @property
    def allowed_moves(self) -> List[Coords]:
        return self.get_lines(self.position, 8)

    def __str__(self) -> str:
        return f'{"white " if self.is_white else "black "}Rook: {self.position}'


class Bishop(Figure):
    def __init__(self, pos, **kwargs):
        super().__init__(pos, **kwargs)
        self.type |= FieldType.BISHOP

    @property
    def allowed_moves(self) -> List[Coords]:
        return self.get_diagonals(self.position, 8)

    def __str__(self):
        return f'{"white " if self.is_white else "black "}Bishop: {self.position}'


class Knight(Figure):
    def __init__(self, pos: Coords, **kwargs):
        super().__init__(pos, **kwargs)
        self.type |= FieldType.KNIGHT
        self.can_jump = True

    @property
    def allowed_moves(self) -> List[Coords]:
        x = self.position.x
        y = self.position.y
        return self.clean_target_fields([
            Coords(x - 1, y - 2), Coords(x - 2, y - 1),
            Coords(x + 1, y - 2), Coords(x + 2, y - 1),
            Coords(x - 1, y + 2), Coords(x - 2, y + 1),
            Coords(x + 1, y + 2), Coords(x + 2, y + 1)
        ])

    def __str__(self) -> str:
        return f'{"white " if self.is_white else "black "}Knight: {self.position}'
