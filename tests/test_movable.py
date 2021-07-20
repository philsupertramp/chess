from unittest import TestCase, main, mock

from src.helpers import Coords
from src.movable import DirectionMixin, BoardState


class DirectionCheckMixinTestCase(TestCase):
    def test_is_diagonal(self):
        self.assertTrue(DirectionMixin.is_diagonal(Coords(1, 1)))
        self.assertTrue(DirectionMixin.is_diagonal(Coords(1, -1)))
        self.assertTrue(DirectionMixin.is_diagonal(Coords(-1, 1)))
        self.assertTrue(DirectionMixin.is_diagonal(Coords(-1, -1)))

        self.assertTrue(DirectionMixin.is_diagonal(Coords(-2, -2)))
        self.assertFalse(DirectionMixin.is_diagonal(Coords(-2, -3)))
        self.assertFalse(DirectionMixin.is_diagonal(Coords(0, -3)))

        self.assertFalse(DirectionMixin.is_diagonal(Coords(1, 0)))
        self.assertFalse(DirectionMixin.is_diagonal(Coords(0, -1)))
        self.assertFalse(DirectionMixin.is_diagonal(Coords(0, 1)))
        self.assertFalse(DirectionMixin.is_diagonal(Coords(-1, 0)))

    def test_is_line(self):
        self.assertTrue(DirectionMixin.is_line(Coords(1, 0)))
        self.assertTrue(DirectionMixin.is_line(Coords(0, -1)))
        self.assertTrue(DirectionMixin.is_line(Coords(0, 1)))
        self.assertTrue(DirectionMixin.is_line(Coords(-1, 0)))

        self.assertFalse(DirectionMixin.is_line(Coords(-2, -2)))
        self.assertFalse(DirectionMixin.is_line(Coords(-2, -3)))
        self.assertTrue(DirectionMixin.is_line(Coords(0, -3)))

        self.assertFalse(DirectionMixin.is_line(Coords(1, 1)))
        self.assertFalse(DirectionMixin.is_line(Coords(1, -1)))
        self.assertFalse(DirectionMixin.is_line(Coords(-1, 1)))
        self.assertFalse(DirectionMixin.is_line(Coords(-1, -1)))

    def test_get_diagonals(self):
        diagonals = DirectionMixin.get_diagonals(Coords(3, 3), 1)
        expected = {Coords(2, 2), Coords(4, 4), Coords(2, 4), Coords(4, 2)}

        self.assertSetEqual(set(diagonals), expected, diagonals)

        diagonals = DirectionMixin.get_diagonals(Coords(3, 3), 2)
        expected = {Coords(2, 2), Coords(4, 4), Coords(2, 4), Coords(4, 2),
                    Coords(1, 1), Coords(5, 5), Coords(1, 5), Coords(5, 1)}

        self.assertSetEqual(set(diagonals), expected, diagonals)

    def test_get_lines(self):
        lines = DirectionMixin.get_lines(Coords(3, 3), 1)
        expected = {Coords(2, 3), Coords(3, 2), Coords(3, 4), Coords(4, 3)}

        self.assertSetEqual(set(lines), expected, lines)

        lines = DirectionMixin.get_lines(Coords(3, 3), 2)
        expected = {Coords(4, 3), Coords(2, 3), Coords(3, 4), Coords(3, 2),
                    Coords(5, 3), Coords(1, 3), Coords(3, 5), Coords(3, 1)}

        self.assertSetEqual(set(lines), expected, lines)


class BoardStateTestCase(TestCase):
    def setUp(self) -> None:
        self.state = BoardState(mock.Mock(fields=[[]]))

    def test_clean_fields(self):
        no_1, yes_1, yes_2, no_2 = Coords(-1, 2), Coords(0, 0), Coords(2, 3), Coords(0, 8)
        out = self.state.clean_target_fields([no_1, yes_1, yes_2, no_2])

        self.assertListEqual(out, [yes_1, yes_2])

    def test_check_field(self):
        some_value = 1.0
        self.state.board = mock.Mock(fields=[[some_value]])

        result = self.state.check_field(Coords(0, 0))

        self.assertEqual(result, some_value)


if __name__ == '__main__':
    main()
