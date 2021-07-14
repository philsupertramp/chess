from typing import Optional

from src.figures import FieldType


class TurnHistory:
    data: str = ''
    last_move: Optional[str] = ''
    turn: int = 0

    def record(self, figure, move, prev_fig):
        """
        Records Figure moved from [figure.position] [x] [move]
        might check prev_fig while doing so
        could also end up in checkmate, appends # at end

        :param figure:
        :param move:
        :param prev_fig:
        :return:
        """
        self.last_move = ''
        if figure.is_white:
            figure_manipulator = 'lower'
        else:
            figure_manipulator = 'upper'

        figure_type = figure.type - (FieldType.WHITE if figure.is_white else FieldType.BLACK)
        if figure_type == FieldType.KING:
            self.last_move += getattr('k', figure_manipulator)()
        elif figure_type == FieldType.QUEEN:
            self.last_move += getattr('q', figure_manipulator)()
        elif figure_type == FieldType.ROOK:
            self.last_move += getattr('r', figure_manipulator)()
        elif figure_type == FieldType.KNIGHT:
            self.last_move += getattr('k', figure_manipulator)()
        elif figure_type == FieldType.PAWN:
            self.last_move += getattr('p', figure_manipulator)()
        elif figure_type == FieldType.BISHOP:
            self.last_move += getattr('b', figure_manipulator)()

        self.last_move += chr(figure.position[0] + 1 + 97)
        self.last_move += str(figure.position[1] + 1)

        if prev_fig:
            self.last_move += 'x'
        else:
            self.last_move += '—'

        self.last_move += chr(move[0] + 1 + 97)
        self.last_move += str(move[1] + 1)

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

    def save(self, filename):
        with open(filename, 'w') as file:
            file.write(self.data)
