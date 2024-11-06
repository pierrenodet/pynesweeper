# SPDX-FileCopyrightText: 2024-present Pierre Nodet <nodet.pierre@gmail.com>
#
# SPDX-License-Identifier: MIT
import argparse
from functools import partial
import math
import sys
import curses
import numpy as np

from pynesweeper import Board, Difficulty

arrow_keys = {curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT}


# def color(s):
#     if s in [str(i) for i in range (1, 7)]:
#         colors[]


# colors = {
#     "default": (curses.COLOR_WHITE, curses.COLOR_BLACK),
#     "cursor": (curses.COLOR_BLACK, curses.COLOR_WHITE),
# }
# colors = {k: (i, *v) for i, (k, v) in enumerate(colors.items(), start=1)}

color_pairs = {str(i): (i, curses.COLOR_BLACK) for i in range(1, 7)}
color_pairs.update({str(i): (i + 2, curses.COLOR_BLACK) for i in range(7, 9)})
color_pairs.update(
    {f"highlight_{k}": (v[0], curses.COLOR_WHITE) for k, v in color_pairs.items()}
)
color_pairs.update({"default": (curses.COLOR_WHITE, curses.COLOR_BLACK)})
color_pairs.update({"highlight_default": (curses.COLOR_BLACK, curses.COLOR_WHITE)})


def display(win, board: Board, colors=dict()):
    s = board.asstr()
    for i in range(board.shape[0]):
        win.addstr(i, 0, " " + " ".join(s[i, :]) + " ")
        for j in range(board.shape[1]):
            if (
                board.discovered[i, j]
                and (n := board.neighbours[i, j]) > 0
                and not board.mined[i, j]
                and not board.marked[i, j]
            ):
                win.chgat(i, 2 * j + 1, 1, curses.color_pair(colors[str(n)]))
    win.addstr(board.shape[0], 0, f"{board.remaining_mines}")


def rmcursor(win, board, cursor, colors):
    x, y = cursor
    win.chgat(x, 2 * y, 1, curses.color_pair(colors["default"]))
    c = "default" if (cue := board.cues[x, y]) == 0 else str(cue)
    win.chgat(x, 2 * y + 1, 1, curses.color_pair(colors[f"{c}"]))
    win.chgat(x, 2 * y + 2, 1, curses.color_pair(colors["default"]))


def addcursor(win, board, cursor, colors):
    x, y = cursor
    win.chgat(x, 2 * y, 1, curses.color_pair(colors["highlight_default"]))
    c = "default" if (cue := board.cues[x, y]) == 0 else str(cue)
    win.chgat(x, 2 * y + 1, 1, curses.color_pair(colors[f"highlight_{c}"]))
    win.chgat(x, 2 * y + 2, 1, curses.color_pair(colors["highlight_default"]))


def main():
    parser = argparse.ArgumentParser(
        prog="pynesweeper",
        description="a minesweeper game that runs in the terminal",
    )
    parser.add_argument(
        "-d",
        "--difficulty",
        type=Difficulty,
        choices=[difficulty.value for difficulty in Difficulty],
        help="difficulty increases board size",
        default=Difficulty.MEDIUM,
    )
    parser.add_argument("--seed", type=int, help="for replayable games")
    args = parser.parse_args()

    try:
        board = Board.make_board(np.random.default_rng(args.seed), args.difficulty)
        x, y = (0, 0)

        stdscr = curses.initscr()
        curses.cbreak()
        curses.noecho()
        curses.curs_set(0)
        stdscr.keypad(True)

        stdscr.clear()

        colors = {}
        curses.start_color()
        for i, (key, (fg, bg)) in enumerate(color_pairs.items(), start=1):
            curses.init_pair(i, fg, bg)
            colors[key] = i
        stdscr.attron(curses.color_pair(colors["default"]))

        display(stdscr, board, colors=colors)
        addcursor(stdscr, board, (x, y), colors=colors)

        while not board.won() and not board.gameover():
            key = stdscr.getch()

            if key in arrow_keys:
                rmcursor(stdscr, board, (x, y), colors=colors)
                if key == curses.KEY_UP and x > 0:
                    x -= 1
                if key == curses.KEY_DOWN and x < board.shape[0] - 1:
                    x += 1
                if key == curses.KEY_RIGHT and y < board.shape[1] - 1:
                    y += 1
                if key == curses.KEY_LEFT and y > 0:
                    y -= 1
            else:
                if key == 10 and not board.marked[x, y]:  # ENTER KEY = 10
                    board.detonate(x, y)

                if key == ord("x"):
                    if not board.marked[x, y]:
                        board.mark(x, y)
                    else:
                        board.unmark(x, y)

                display(stdscr, board, colors=colors)

            addcursor(stdscr, board, (x, y), colors=colors)

        if go := board.gameover():
            board.discovered[:] = True
        display(stdscr, board, colors=colors)
        stdscr.addstr(board.shape[0], 0, "BOOM" if go else "WON")
        stdscr.getch()

    finally:
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.flushinp()
        curses.endwin()


if __name__ == "__main__":
    sys.exit(main())
