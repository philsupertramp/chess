import pprint
from typing import Set, Optional

from src.game import Game
from src.history import Turn


class Collector:
    def __init__(self, max_depth: int = 10):
        self.game = Game(use_pygame=False)
        self.max_depth = max_depth

    def init(self, fen_string, white_moves: bool = True):
        self.game.reset(True)
        self.game.board.reset(fen_string)
        self.game.is_white_turn = white_moves

    def collect(self):
        current_state = self.game.copy()
        return self.collect_depth(0, current_state)

    def collect_depth(self, current_depth, current_state, moves: Optional[Set[Turn]] = None):
        if moves is None:
            moves = {}

        if current_depth == self.max_depth:
            return moves

        moves[current_depth] = dict()

        for row in current_state.board.fields:
            for field in filter(lambda x: x is not None, row):
                for move in field.remove_set(field.allowed_moves):
                    new_state = current_state.copy()
                    new_state.handle_mouse_click(field.position.col, field.position.row)
                    new_state.handle_mouse_click(move.col, move.row)

                    if field.position in moves and move in moves[field.position]:
                        moves[current_depth][field.position].append(move)
                    else:
                        moves[current_depth][field.position] = [move]

                    self.collect_depth(current_depth + 1, new_state, moves)

        return moves


if __name__ == '__main__':
    collector = Collector(3)
    collector.init('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR')
    collection = collector.collect()
    pprint.pprint(collection, indent=2)
