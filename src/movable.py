from typing import Optional, List, Union

from src.helpers import sign, Coords


class DirectionMixin:
    @classmethod
    def is_diagonal(cls, new_pos: Coords) -> bool:
        """
        Helper to detect if move is diagonal

        :param new_pos:
        :return: move is diagonal
        """
        return (abs(new_pos.x) + abs(new_pos.y)) / 2 == abs(new_pos.x)

    @classmethod
    def is_line(cls, new_pos: Coords) -> bool:
        """
        Helper to detect if move is straight line
        :param new_pos:
        :return: move is line
        """
        return new_pos.x == 0 or new_pos.y == 0

    @classmethod
    def get_diagonals(cls, pos: Coords, length: int) -> List[Coords]:
        """
        Helper to create diagonal moves
        :param pos: starting pos
        :param length: length of diagonals starting at `pos`
        :return: list of diagonal tiles starting from `pos`
        """
        x = pos.x
        y = pos.y

        res = list()
        for _x in range(1, length + 1):
            res.extend([Coords(x + _x, y + _x), Coords(x - _x, y - _x), Coords(x - _x, y + _x), Coords(x + _x, y - _x)])
        return list(set(filter(lambda val: val.x >= 0 and val.y >= 0 and abs(val.x) < 8 and abs(val.y) < 8, res)))

    @classmethod
    def get_night_moves(cls, pos: Coords) -> List[Coords]:
        x = pos.x
        y = pos.y
        return [
            Coords(x - 1, y - 2), Coords(x - 2, y - 1),
            Coords(x + 1, y - 2), Coords(x + 2, y - 1),
            Coords(x - 1, y + 2), Coords(x - 2, y + 1),
            Coords(x + 1, y + 2), Coords(x + 2, y + 1),
        ]

    @classmethod
    def get_lines(cls, pos: Coords, length: int) -> List[Coords]:
        """
        Helper to create straight line moves
        :param pos: starting pos
        :param length: length of lines starting at `pos`
        :return: list of tiles in straight lines starting from `pos`
        """
        x = pos.x
        y = pos.y

        res = list()
        for _x in range(1, length + 1):
            res.extend([Coords(x + _x, y), Coords(x - _x, y), Coords(x, y + _x), Coords(x, y - _x)])
        return list(set(filter(lambda val: val.x >= 0 and val.y >= 0 and abs(val.x) < 8 and abs(val.y) < 8, res)))


class BoardState:
    def __init__(self, board: 'CheckerBoard'):
        self.board = board

    def check_field(self, move: Coords) -> Optional['Figure']:
        """
        Helper to detect figure on given tile
        """
        return self.board.check_field(move)

    @staticmethod
    def clean_target_fields(fields: List[Coords]) -> List[Coords]:
        """
        Drops fields not present on the 8x8 board
        :param fields: list of fields to clean
        :return: cleaned list of provided fields
        """
        cleaned_fields = []
        for field in fields:
            if field.x < 0 or field.y < 0 or field.x > 7 or field.y > 7:
                continue
            cleaned_fields.append(field)
        return cleaned_fields

    def move_in_state(self, new_pos: Coords):
        pass


class Movable(DirectionMixin, BoardState):
    def __init__(self, pos: Coords, board: 'CheckerBoard'):
        self.position = pos
        self.prev_position = None
        self.has_moved = False
        self.can_jump = False
        super().__init__(board)

    def move(self, new_pos: Coords) -> bool:
        """
        Moves a figure to a new given position, checks and return success

        Also sets positions and markers if movable has moved.

        :param new_pos: position to move the figure to, potentially
        :return: successfully moved figure
        """
        if self.is_move_allowed(new_pos):  # not self.locked() and self.is_move_allowed(new_pos):
            self.move_in_state(new_pos)
            self.prev_position = self.position
            self.position = new_pos
            self.has_moved = True
            return True
        return False

    def is_move_allowed(self, move: Coords) -> bool:
        """
        Tests if a move is allowed to be performed

        :param move: potential tile to move to
        """
        fig = self.can_move(move)
        return fig is None or (
                fig and (fig.position.x == move.x and fig.position.y == move.y and fig.is_white != self.is_white))

    def remove_set(self, coords):
        new_coords = list()
        found_x = list()
        found_y = list()
        for field in coords:
            if not self.can_jump and ((fig := self.get_figures_between(field)) is not None and fig.is_white == self.is_white):
                found_x.append(field.x)
                found_y.append(field.y)
                continue
            cell = self.check_field(field)
            if cell and cell.is_white == self.is_white:
                found_x.append(field.x)
                found_y.append(field.y)
                continue
            new_coords.append(field)
        return new_coords

    def can_move(self, move: Coords) -> Optional[Union['Figure', bool]]:
        """
        Determines whether a move can be performed or not

        :param move: the actual tile location to move to
        :return: Figure or None, None is considered good and successful
        """
        if move not in self.remove_set(self.allowed_moves):
            return False

        figure_at_pos = self.check_field(move)

        if self.can_jump:
            return figure_at_pos

        figure_between = self.get_figures_between(move)
        if figure_between:
            return figure_between
        return figure_at_pos

    def get_figures_between(self, move):
        diff_x = move.x - self.position.x
        diff_y = move.y - self.position.y

        if abs(diff_x) > 0 and abs(diff_x) == abs(diff_y):
            # diagonal move
            factors = (sign(diff_x), sign(diff_y))
            for i in range(1, min(abs(diff_x) + 1, 8)):
                if fig := self.check_field(Coords(self.position.x + factors[0] * i, self.position.y + factors[1] * i)):
                    return fig
        elif abs(diff_x) > 0:
            # x direction
            factor = (-1) if diff_x < 0 else 1
            for i in range(1, min(abs(diff_x) + 1, 8)):
                if fig := self.check_field(Coords(self.position.x + factor * i, self.position.y)):
                    return fig
        elif abs(diff_y) > 0:
            # y direction
            factor = (-1) if diff_y < 0 else 1
            for i in range(1, min(abs(diff_y) + 1, 8)):
                if fig := self.check_field(Coords(self.position.x, self.position.y + factor * i)):
                    return fig

    @property
    def allowed_moves(self) -> List[Coords]:
        """
        Helper method to get all available moves of a figure

        :return: list of possible moves
        """
        raise NotImplementedError

    def locked(self, is_white: bool) -> bool:
        """
        :param is_white:
        :return: False if figure would allow checkmate
        """
        positions = self.__get_checkmate_positions(is_white)
        return self.position in positions

    def __get_checkmate_positions(self, is_white: bool) -> List[Coords]:
        """
        TODO: fix me
        """
        from src.figures import FieldType
        own_king_pos: Coords = Coords(-1, -1)
        for row in self.board.fields:
            for cell in row:
                if not cell:
                    continue
                if cell.type - FieldType.KING == (FieldType.WHITE if is_white else FieldType.BLACK):
                    own_king_pos = cell.position

        assert own_king_pos != (-1, -1), 'Did not find King... Something is wrong!'

        checkmate_positions: List[Coords] = list()
        for row in self.board.fields:
            for cell in row:
                if not cell or cell.is_white == is_white:
                    continue
                target_fields = cell.allowed_moves
                if own_king_pos in target_fields:
                    for x in range(abs(own_king_pos.x - cell.position.x) + 1):
                        for y in range(abs(own_king_pos.y - cell.position.y) + 1):
                            checkmate_positions.append(Coords(own_king_pos.x + x, own_king_pos.y + y))
        return checkmate_positions
