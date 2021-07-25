from unittest import TestCase, mock, main

from parameterized import parameterized

from src.figures import Pawn, King, Rook, FieldType
from src.helpers import Coords


class FieldTypeTestCase(TestCase):
    def test_conversation(self):
        black_king = FieldType.KING | FieldType.BLACK

        self.assertEqual(FieldType.clear(black_king), FieldType.KING)

        self.assertEqual(black_king & FieldType.KING, FieldType.KING)
        self.assertEqual(black_king & FieldType.BLACK, FieldType.BLACK)

        self.assertEqual(black_king - FieldType.KING, FieldType.BLACK)
        self.assertEqual(black_king - FieldType.BLACK, FieldType.KING)


class FigureTestCase(TestCase):
    def setUp(self) -> None:
        self.board = mock.Mock(fields=[[None for _ in range(8)] for _ in range(8)])

    def _add_figure(self, fig):
        self.board.fields[fig.position.row][fig.position.col] = fig

    def _test_moves(self, white, black, expected_white, expected_black):
        self._add_figure(white)
        self._add_figure(black)

        for move in expected_white:
            self.assertIn(Coords.from_string(move), white.allowed_moves)
        for move in expected_black:
            self.assertIn(Coords.from_string(move), black.allowed_moves)


class PawnTestCase(FigureTestCase):
    def test_available_moves(self):
        pawn = Pawn(Coords.from_string('e2'), is_white=True, _board=self.board)
        self._add_figure(pawn)

        self.assertEqual(pawn.allowed_moves, [Coords.from_string('e3'), Coords.from_string('e4')])

    @parameterized.expand([
        ('e5', False, 'f5', True, ['f6', 'e6'], ['f4']),
        ('e5', False, 'd5', True, ['d6', 'e6'], ['d4']),
        ('e4', True, 'f4', False, ['e5'], ['e3', 'f3']),
    ])
    def test_available_moves_en_passant(self, white_start, white_en_pas, black_start, black_en_pas, expected_white,
                                        expected_black):
        white_pawn = Pawn(Coords.from_string(white_start), is_white=True, _board=self.board)
        white_pawn.has_moved = True
        white_pawn.en_passant = white_en_pas
        black_pawn = Pawn(Coords.from_string(black_start), is_white=False, _board=self.board)
        black_pawn.has_moved = True
        black_pawn.en_passant = black_en_pas

        self._test_moves(white_pawn, black_pawn, expected_white, expected_black)


class KingTestCase(FigureTestCase):
    def test_available_moves_castling(self):
        white_king = King(Coords.from_string('e1'), is_white=True, _board=self.board)
        white_king.has_moved = False
        black_king = King(Coords.from_string('e8'), is_white=False, _board=self.board)
        black_king.has_moved = False

        white_rooks = [Rook(Coords.from_string('a1'), is_white=True, _board=self.board),
                       Rook(Coords.from_string('h1'), is_white=True, _board=self.board)]

        black_rooks = [Rook(Coords.from_string('a8'), is_white=False, _board=self.board),
                       Rook(Coords.from_string('h8'), is_white=False, _board=self.board)]

        self._add_figure(white_rooks[0])
        self._add_figure(white_rooks[1])
        self._add_figure(black_rooks[0])
        self._add_figure(black_rooks[1])

        def get_figs(fig_type):
            if fig_type - FieldType.BLACK > 0:
                return black_rooks
            return white_rooks

        self.board.get_figures = get_figs
        self._test_moves(white_king, black_king,
                         ['a1', 'd1', 'f1', 'e2', 'f2', 'd2', 'h1'],
                         ['a8', 'd8', 'f8', 'e7', 'f7', 'd7', 'h8'])

    def test_checkmate(self):
        self.assertTrue(King(Coords.from_string('e1'), is_white=True, _board=self.board).checkmate())


if __name__ == '__main__':
    main()
