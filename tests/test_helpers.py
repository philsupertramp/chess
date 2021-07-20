from unittest import TestCase

from parameterized import parameterized

from src.helpers import Coords


class CoordsTestCase(TestCase):
    def test_col(self):
        val = Coords(0, 1)
        self.assertEqual(val.col, 0)

    def test_row(self):
        val = Coords(0, 1)
        self.assertEqual(val.row, 1)

    def test_len(self):
        val = Coords(0, 2)
        self.assertEqual(val.len, 2)

    @parameterized.expand([
        ('a1', Coords(0, 7)),
        ('h1', Coords(7, 7)),
        ('a8', Coords(0, 0)),
        ('h8', Coords(7, 0)),
    ])
    def test_from_string(self, val, expected):
        out = Coords.from_string(val)
        self.assertEqual(out, expected)

    @parameterized.expand([
        (Coords(0, 7), 'a1'),
        (Coords(7, 7), 'h1'),
        (Coords(0, 0), 'a8'),
        (Coords(7, 0), 'h8'),
    ])
    def test_from_string(self, val, expected):
        out = val.to_string()
        self.assertEqual(out, expected)

    def test__sub__(self):
        a = Coords(1, 1)
        self.assertEqual(a - a, Coords(0, 0))

    def test__eq__(self):
        a = Coords(1, 1)
        self.assertTrue(a == a)

    def test__lt__(self):
        a = Coords(1, 1)
        b = Coords(2, 2)
        self.assertTrue(a < b)
