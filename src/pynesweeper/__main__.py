# SPDX-FileCopyrightText: 2024-present Pierre Nodet <nodet.pierre@gmail.com>
#
# SPDX-License-Identifier: MIT
import argparse
import curses
import sys

from pynesweeper import Board, CustomDifficulty, Difficulty


def display(win, board: Board, colors: dict):
    s = board.asstr()
    c = board.cues()
    for i in range(board.shape[0]):
        win.addstr(i, 0, " " + " ".join(s[i, :]) + " ")
        for j in range(board.shape[1]):
            if (n := c[i, j]) > 0:
                win.chgat(i, 2 * j + 1, 1, colors[n])
    win.addstr(board.shape[0], 0, " " * board.shape[1])
    win.addstr(board.shape[0], 0, f"{board.remaining_mines}/{board.mined.sum()}")


MAC_BUTTON3_PRESSED = 8192


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
            "You should either set the difficulty from predifined \
values with -d or use a custom difficulty with -s and -p",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        board = Board.make_board(args.seed, difficulty)
        x, y = (0, 0)

        stdscr = curses.initscr()
        curses.cbreak()
        curses.noecho()
        curses.curs_set(0)
        stdscr.keypad(True)
        curses.mousemask(-1)
        curses.mouseinterval(0)

        stdscr.clear()

        colors = {}
        curses.start_color()
        curses.use_default_colors()
        for i in range(1, 9):
            curses.init_pair(i, i, -1)
            colors[i] = curses.color_pair(i)

        while not board.won() and not board.gameover():
            display(stdscr, board, colors)
            key = stdscr.getch()

            if key == curses.KEY_MOUSE:
                _, yy, x, _, bstate = curses.getmouse()
                y = (yy - 1) // 2

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

        if go := board.gameover():
            board.discovered[:] = True
        display(stdscr, board, colors)
        stdscr.addstr(board.shape[0], 0, " " * board.shape[1])
        stdscr.addstr(board.shape[0], 0, "BOOM" if go else "WON")
        stdscr.getch()

    finally:
        curses.nocbreak()
        curses.curs_set(1)
        stdscr.keypad(False)
        curses.echo()
        curses.flushinp()
        curses.endwin()


if __name__ == "__main__":
    sys.exit(main())
