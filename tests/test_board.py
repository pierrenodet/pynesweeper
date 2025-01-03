from pynesweeper import Board, Difficulty


def test_board():
    board = Board.make_board(Difficulty.EASY, seed=1)
    board.detonate(0, 0)
    board.detonate(1, 0)
    board.detonate(2, 0)
    board.flag(0, 1)
    board.detonate(0, 2)
    board.flag(0, 3)
    board.detonate(0, 4)
    assert board.won()
