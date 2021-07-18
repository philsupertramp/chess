from typing import Tuple, Optional, List

from src.helpers import sign


class DirectionMixin:
    @classmethod
    def is_diagonal(cls, new_pos: Tuple[int, int]) -> bool:
        """
        Helper to detect if move is diagonal

        :param new_pos:
        :return: move is diagonal
        """
        return (abs(new_pos[0]) + abs(new_pos[1])) / 2 == abs(new_pos[0])

    @classmethod
    def is_line(cls, new_pos: Tuple[int, int]) -> bool:
        """
        Helper to detect if move is straight line
        :param new_pos:
        :return: move is line
        """
        return new_pos[0] == 0 or new_pos[1] == 0

    @classmethod
    def get_diagonals(cls, pos: Tuple[int, int], length: int) -> List[Tuple[int, int]]:
        """
        Helper to create diagonal moves
        :param pos: starting pos
        :param length: length of diagonals starting at `pos`
        :return: list of diagonal tiles starting from `pos`
        """
        x = pos[0]
        y = pos[1]

        res = list()
        for _x in range(1, length + 1):
            res.extend([(x + _x, y + _x), (x - _x, y - _x), (x - _x, y + _x), (x + _x, y - _x)])
        return list(set(filter(lambda val: val[0] >= 0 and val[1] >= 0 and abs(val[0]) < 8 and abs(val[1]) < 8, res)))

    @classmethod
    def get_lines(cls, pos: Tuple[int, int], length: int) -> List[Tuple[int, int]]:
        """
        Helper to create straight line moves
        :param pos: starting pos
        :param length: length of lines starting at `pos`
        :return: list of tiles in straight lines starting from `pos`
        """
        x = pos[0]
        y = pos[1]

        res = list()
        for _x in range(1, length + 1):
            res.extend([(x + _x, y), (x - _x, y), (x, y + _x), (x, y - _x)])
        return list(set(filter(lambda val: val[0] >= 0 and val[1] >= 0 and abs(val[0]) < 8 and abs(val[1]) < 8, res)))


class BoardState:
    def __init__(self, board: 'CheckerBoard'):
        self.board = board

    def check_field(self, move: Tuple[int, int]) -> Optional['Figure']:
        """
        Helper to detect figure on given tile
        """
        return self.board.fields[move[1]][move[0]]

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

    def move_in_state(self, new_pos):
        pass


class Movable(DirectionMixin, BoardState):
    def __init__(self, pos: Tuple[int, int], board: 'CheckerBoard'):
        self.position = pos
        self.has_moved = False
        self.can_jump = False
        super().__init__(board)

    def move(self, new_pos: Tuple[int, int]) -> bool:
        """
        Moves a figure to a new given position, checks and return success

        :param new_pos: position to move the figure to, potentially
        :return: successfully moved figure
        """
        if self.is_move_allowed(new_pos):  # not self.locked() and self.is_move_allowed(new_pos):
            self.move_in_state(new_pos)
            self.position = new_pos
            self.has_moved = True
            return True
        return False

    def is_move_allowed(self, move: Tuple[int, int]) -> bool:
        """
        Tests if a move is allowed to be performed

        :param move: potential tile to move to
        """
        fig = self.can_move(move)
        return fig is None or (fig and (fig.position[0] == move[0] and fig.position[1] == move[1] and fig.is_white != self.is_white))

    def can_move(self, move: Tuple[int, int]) -> Optional['Figure']:
        """
        Determines whether a move can be performed or not

        :param move: the actual tile location to move to
        :return: Figure or None, None is considered good and successful
        """
        if move not in self.allowed_moves:
            return False

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

    @property
    def allowed_moves(self) -> List[Tuple[int, int]]:
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

    def __get_checkmate_positions(self, is_white: bool) -> List[Tuple[int, ...]]:
        """
        TODO: fix me
        """
        from src.figures import FieldType
        own_king_pos: Tuple[int, int] = (-1, -1)
        for row in self.board.fields:
            for cell in row:
                if not cell:
                    continue
                if cell.type - FieldType.KING == (FieldType.WHITE if is_white else FieldType.BLACK):
                    own_king_pos = cell.position

        assert own_king_pos != (-1, -1), 'Did not find King... Something is wrong!'

        checkmate_positions: List[Tuple[int, ...]] = list()
        for row in self.board.fields:
            for cell in row:
                if not cell or cell.is_white == is_white:
                    continue
                target_fields = cell.allowed_moves
                if own_king_pos in target_fields:
                    for x in range(abs(own_king_pos[0] - cell.position[0]) + 1):
                        for y in range(abs(own_king_pos[1] - cell.position[1]) + 1):
                            checkmate_positions.append((own_king_pos[0] + x, own_king_pos[1] + y))
        return checkmate_positions
