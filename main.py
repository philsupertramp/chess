#! /usr/bin/env python


import argparse
from src.game import Game


def init_argparse() -> argparse.ArgumentParser:
    _parser = argparse.ArgumentParser(description='Process some integers.')
    _parser.add_argument('--headless', dest='headless', action='store_true',
                         help='Use headless console version.')
    return _parser


if __name__ == '__main__':
    parser = init_argparse()
    args = parser.parse_args()
    game = Game(not args.headless)
    game.run()

    game.reset()
    game.replay()

    game.close()
