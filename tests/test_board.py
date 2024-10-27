import numpy as np

from pynesweeper import Board, Difficulty


def test_board():
    board = Board.make_board(np.random.default_rng(1), difficulty=Difficulty.DEBUG)
    board.detonate(0, 0)
    board.detonate(1, 0)
    board.detonate(2, 0)
    board.mark(0, 1)
    board.detonate(0, 2)
    board.mark(0, 3)
    board.detonate(0, 4)
    assert board.won()
