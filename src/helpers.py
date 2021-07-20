import math


def sign(val):
    """
    stupid implementation of sign function missing in python

    :param val: a value to get sign of
    :return: 0, 1 or -1
    """
    return 0 if val == 0.0 else 1 if val > 0 else -1


class Coords:
    x: int
    y: int

    def __init__(self, x, y):
        self.x = x
        self.y = y

    @property
    def col(self) -> int:
        return self.x

    @property
    def row(self) -> int:
        return self.y

    @property
    def len(self) -> float:
        return math.sqrt(self.x*self.x+self.y*self.y)

    @classmethod
    def from_string(cls, move: str) -> 'Coords':
        return Coords(ord(move[0]) - 97, 8 - int(move[1]))

    def to_string(self) -> str:
        return chr(self.x + 97) + str((8 - self.y))

    def __sub__(self, other):
        return Coords(self.x - other.x, self.y - other.y)

    def __eq__(self, other) -> bool:
        return self.len == other.len

    def __lt__(self, other) -> bool:
        return self.len < other.len

    def __hash__(self) -> int:
        return hash(repr(self))

    def __str__(self) -> str:
        return f'({self.x}, {self.y})'

    def __repr__(self) -> str:
        return str(self)
