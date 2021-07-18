def sign(val):
    """
    stupid implementation of sign function missing in python

    :param val: a value to get sign of
    :return: 0, 1 or -1
    """
    return 0 if val == 0.0 else 1 if val > 0 else -1


class Coords:
    x: float
    y: float

    def __init__(self, x, y):
        self.x = x
        self.y = y

    @property
    def col(self):
        return self.x

    @property
    def row(self):
        return self.y
