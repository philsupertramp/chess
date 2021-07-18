from typing import Optional, List

from src.figures import FieldType


class Turn:
    def __init__(self, start, end):
        self.start = start
        self.end = end


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
    def pos_to_string(move):
        return chr((move[0]) + 97) + str((8 - move[1]))

    def record(self, figure, old_pos, move, prev_fig):
        """
        #TODO: Add castling parameter.
               Notation is: 0-0 kingside rook 0-0-0 queenside rook color doesn't matter. it's obvious due to turn

        Records Figure moved from [figure.position] [x] [move]
        might check prev_fig while doing so
        could also end up in checkmate, appends # at end

        :param figure:
        :param old_pos:
        :param move:
        :param prev_fig:
        :return:
        """
        if self.is_final:
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

        self.turns.append(Turn(old_pos, move))

    def save(self, filename):
        with open(filename, 'w') as file:
            file.write(self.data)
