from typing import Optional, List

from src.figures import FieldType
from src.helpers import sign


class Turn:
    def __init__(self, start, end, is_castling, fig):
        self.start = start
        self.end = end
        self.is_castling = is_castling
        self.figure = fig

    def __str__(self):
        return (TurnHistory.figure_move_to_string(self.figure, self.start)
                + f'–{TurnHistory.pos_to_string(self.end)}')


class TurnHistory:
    data: str = ''
    last_move: Optional[str] = ''
    turn: int = 0
    turns: List[Turn] = list()
    is_final: bool = False

    def __init__(self):
        self.prev_was_pawn = False

    @staticmethod
    def figure_move_to_string(figure, move):
        last_move = ''
        if figure.is_white:
            figure_manipulator = 'lower'
        else:
            figure_manipulator = 'upper'

        figure_type = FieldType.clear(figure.type)
        if figure_type == FieldType.KING:
            last_move += getattr('k', figure_manipulator)()
        elif figure_type == FieldType.QUEEN:
            last_move += getattr('q', figure_manipulator)()
        elif figure_type == FieldType.ROOK:
            last_move += getattr('r', figure_manipulator)()
        elif figure_type == FieldType.KNIGHT:
            last_move += getattr('k', figure_manipulator)()
        elif figure_type == FieldType.PAWN:
            last_move += getattr('p', figure_manipulator)()
        elif figure_type == FieldType.BISHOP:
            last_move += getattr('b', figure_manipulator)()

        return last_move + TurnHistory.pos_to_string(move)

    @staticmethod
    def string_to_pos(move: str):
        return ord(move[0]) - 97, 8 - int(move[1])

    @staticmethod
    def pos_to_string(move):
        return chr((move[0]) + 97) + str((8 - move[1]))

    def record(self, figure, old_pos, move, prev_fig):
        """
        Records Figure moved from [figure.position] [x] [move]
        might check prev_fig while doing so
        could also end up in checkmate, appends # at end

        :param figure:
        :param old_pos:
        :param move:
        :param prev_fig:
        :param is_castling:
        :return:
        """
        if self.is_final:
            return

        is_castling: bool = figure.castles_with is not None
        self.turns.append(Turn(old_pos, move, is_castling, figure))

        if is_castling:
            if sign(move[0] - old_pos[0]) == 1:
                # kingside
                self.last_move = '0-0 '
            else:
                # queenside
                self.last_move = '0-0-0 '
            self.data += self.last_move
            return

        self.prev_was_pawn = figure.type == (FieldType.PAWN + FieldType.WHITE if figure.is_white else FieldType.BLACK)

        self.last_move = self.figure_move_to_string(figure, old_pos)

        if prev_fig:
            self.last_move += 'x'
        else:
            self.last_move += '—'

        self.last_move += self.pos_to_string(move)

        if prev_fig and prev_fig.checkmate():
            self.last_move += '#'
        else:
            self.last_move += ' '

        self.data += self.last_move
        if not figure.is_white:
            self.turn += 1
            self.data += '\n'

        if '#' in self.data:
            print(self.data)
            self.is_final = True

    def save(self, filename):
        with open(filename, 'w') as file:
            file.write(self.data)
