
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


class Movable(DirectionMixin):
    pass
