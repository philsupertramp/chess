from unittest import TestCase, main

from src.figures import DirectionMixin


class DirectionCheckMixinTestCase(TestCase):
    def test_is_diagonal(self):
        self.assertTrue(DirectionMixin.is_diagonal((1, 1), 1))
        self.assertTrue(DirectionMixin.is_diagonal((1, -1), 1))
        self.assertTrue(DirectionMixin.is_diagonal((-1, 1), 1))
        self.assertTrue(DirectionMixin.is_diagonal((-1, -1), 1))

        self.assertTrue(DirectionMixin.is_diagonal((-2, -2), 2))
        self.assertFalse(DirectionMixin.is_diagonal((-2, -3), 2))
        self.assertFalse(DirectionMixin.is_diagonal((0, -3), 2))

        self.assertFalse(DirectionMixin.is_diagonal((1, 0), 1))
        self.assertFalse(DirectionMixin.is_diagonal((0, -1), 1))
        self.assertFalse(DirectionMixin.is_diagonal((0, 1), 1))
        self.assertFalse(DirectionMixin.is_diagonal((-1, 0), 1))

    def test_is_line(self):
        self.assertTrue(DirectionMixin.is_line((1, 0), 1))
        self.assertTrue(DirectionMixin.is_line((0, -1), 1))
        self.assertTrue(DirectionMixin.is_line((0, 1), 1))
        self.assertTrue(DirectionMixin.is_line((-1, 0), 1))

        self.assertFalse(DirectionMixin.is_line((-2, -2), 2))
        self.assertFalse(DirectionMixin.is_line((-2, -3), 2))
        self.assertTrue(DirectionMixin.is_line((0, -3), 3))

        self.assertFalse(DirectionMixin.is_line((1, 1), 1))
        self.assertFalse(DirectionMixin.is_line((1, -1), 1))
        self.assertFalse(DirectionMixin.is_line((-1, 1), 1))
        self.assertFalse(DirectionMixin.is_line((-1, -1), 1))

    def test_get_diagonals(self):
        diagonals = DirectionMixin.get_diagonals((3, 3), 1)
        expected = {(4, 4), (-4, 4), (4, -4), (-4, -4)}

        self.assertSetEqual(set(diagonals), expected, diagonals)

        diagonals = DirectionMixin.get_diagonals((3, 3), 2)
        expected = {(4, 4), (-4, 4), (4, -4), (-4, -4), (5, 5), (-5, 5), (5, -5), (-5, -5)}

        self.assertSetEqual(set(diagonals), expected, diagonals)


if __name__ == '__main__':
    main()
