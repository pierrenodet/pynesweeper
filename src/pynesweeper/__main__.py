# SPDX-FileCopyrightText: 2024-present Pierre Nodet <nodet.pierre@gmail.com>
#
# SPDX-License-Identifier: MIT
import argparse
import curses
import sys
from contextlib import contextmanager

from pynesweeper import Board, CustomDifficulty, Difficulty


def display(screen: curses.window, board: Board, colors: dict):
    s = board.asstr()
    c = board.cues()
    for i in range(board.shape[0]):
        screen.addstr(i, 0, " ".join(s[i, :]))
        for j in range(board.shape[1]):
            if (n := c[i, j]) > 0:
                screen.chgat(i, 2 * j, 1, colors[n])
    screen.addstr(board.shape[0], 0, " " * board.shape[1])
    screen.addstr(board.shape[0], 0, f"{board.remaining_mines}/{board.mined.sum()}")


MAC_BUTTON3_PRESSED = 8192


@contextmanager
def stdscr(shape: tuple[int, int] | None = None):
    try:
        s = curses.initscr()
        x, y = s.getmaxyx()
        if shape is not None:
            h, w = shape
            err = []
            for dim, size, bound in [("rows", h, x - 1), ("cols", w, (y + 1) // 2)]:
                if size > bound:
                    err += [f"{dim} ({size}>{bound})"]
            if err:
                print(
                    f"You asked for too many {" and ".join(err)}, increase the terminal size or ask for less.",
                    file=sys.stderr,
                )
                sys.exit(1)
        curses.cbreak()
        curses.noecho()
        curses.curs_set(0)
        s.keypad(True)
        curses.mousemask(-1)
        curses.mouseinterval(0)
        s.clear()
        yield s
    finally:
        curses.nocbreak()
        curses.curs_set(1)
        s.keypad(False)
        curses.echo()
        curses.flushinp()
        curses.endwin()


def main():
    parser = argparse.ArgumentParser(
        prog="pynesweeper",
        description="a minesweeper game in Python that runs in your terminal",
    )
    parser.add_argument(
        "-d",
        "--difficulty",
        type=Difficulty,
        choices=[difficulty.value for difficulty in Difficulty],
        help="difficulty increases board size and pbomb",
    )
    parser.add_argument("-s", "--size", type=int, nargs=2, help="board size")
    parser.add_argument("-p", "--pbomb", type=float, help="bomb probability")
    parser.add_argument("--seed", type=int, help="for replayable games")
    args = parser.parse_args()

    if args.size is not None and args.pbomb is not None:
        difficulty = CustomDifficulty(args.size, args.pbomb)
    elif args.difficulty is not None:
        difficulty = args.difficulty
    else:
        print(
            "You should either set the difficulty from predifined values with -d or use a custom difficulty with -s and -p",
            file=sys.stderr,
        )
        sys.exit(1)

    board = Board.make_board(args.seed, difficulty)

    with stdscr(board.shape) as s:
        colors = {}
        curses.start_color()
        curses.use_default_colors()
        for i in range(1, 9):
            curses.init_pair(i, i, -1)
            colors[i] = curses.color_pair(i)

        while not board.won() and not (go := board.gameover()):
            display(s, board, colors)
            key = s.getch()

            if key == curses.KEY_MOUSE:
                _, yy, x, _, bstate = curses.getmouse()
                y = yy // 2

                if (x, y) in board:
                    if bstate & (curses.BUTTON1_CLICKED | curses.BUTTON1_RELEASED):
                        if not board.discovered[x, y]:
                            board.detonate(x, y)
                        else:
                            board.chord(x, y)

                    if bstate & (curses.BUTTON3_PRESSED | MAC_BUTTON3_PRESSED):
                        if not board.flagged[x, y]:
                            board.flag(x, y)
                        else:
                            board.unflag(x, y)

        if go:
            board.discovered[:] = True
        display(s, board, colors)
        s.addstr(board.shape[0], 0, " " * board.shape[1])
        s.addstr(board.shape[0], 0, "BOOM" if go else "WON")
        s.getch()


if __name__ == "__main__":
    sys.exit(main())
