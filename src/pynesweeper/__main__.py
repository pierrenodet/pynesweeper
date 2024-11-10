# SPDX-FileCopyrightText: 2024-present Pierre Nodet <nodet.pierre@gmail.com>
#
# SPDX-License-Identifier: MIT
import argparse
import sys
import curses

from pynesweeper import Board, Difficulty

ARROW_KEYS = {curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT}


# def color(s):
#     if s in [str(i) for i in range (1, 7)]:
#         colors[]


# colors = {
#     "default": (curses.COLOR_WHITE, curses.COLOR_BLACK),
#     "cursor": (curses.COLOR_BLACK, curses.COLOR_WHITE),
# }
# colors = {k: (i, *v) for i, (k, v) in enumerate(colors.items(), start=1)}

color_pairs = {i: (i, -1) for i in range(1, 7)}
color_pairs.update({i: (i + 2, -1) for i in range(7, 9)})
color_pairs.update(
    {f"highlight_{k}": (v[0], curses.COLOR_WHITE) for k, v in color_pairs.items()}
)
color_pairs.update({"default": (curses.COLOR_WHITE, curses.COLOR_BLACK)})
color_pairs.update({"highlight_default": (curses.COLOR_BLACK, curses.COLOR_WHITE)})


def display(win, board: Board, colors=dict()):
    s = board.asstr()
    c = board.cues()
    for i in range(board.shape[0]):
        win.addstr(i, 0, " " + " ".join(s[i, :]) + " ")
        for j in range(board.shape[1]):
            if (n := c[i, j]) > 0:
                win.chgat(i, 2 * j + 1, 1, colors[n])
    win.addstr(board.shape[0], 0, f"{board.remaining_mines}")


def rmcursor(win, board, cursor, colors):
    x, y = cursor
    win.chgat(x, 2 * y, 1, colors["default"])
    c = "default" if (cue := board.cues()[x, y]) == 0 else cue
    win.chgat(x, 2 * y + 1, 1, colors[c])
    win.chgat(x, 2 * y + 2, 1, colors["default"])


def addcursor(win, board, cursor, colors):
    x, y = cursor
    win.chgat(x, 2 * y, 1, colors["highlight_default"])
    c = "default" if (cue := board.cues()[x, y]) == 0 else cue
    win.chgat(x, 2 * y + 1, 1, colors[c] | curses.A_REVERSE)
    win.chgat(x, 2 * y + 2, 1, colors["highlight_default"])


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
        board = Board.make_board(args.seed, args.difficulty)
        x, y = (0, 0)

        stdscr = curses.initscr()
        curses.cbreak()
        curses.noecho()
        curses.curs_set(0)
        stdscr.keypad(True)
        # curses.mousemask(curses.ALL_MOUSE_EVENTS)
        # print("\033[?1003h")

        stdscr.clear()

        colors = {}
        curses.start_color()
        curses.use_default_colors()
        for i, (key, (fg, bg)) in enumerate(color_pairs.items(), start=1):
            curses.init_pair(i, fg, bg)
            colors[key] = curses.color_pair(i)
        stdscr.attron(colors["default"])

        display(stdscr, board, colors=colors)
        addcursor(stdscr, board, (x, y), colors=colors)

        while not board.won() and not board.gameover():
            key = stdscr.getch()

            if key in ARROW_KEYS:
                rmcursor(stdscr, board, (x, y), colors=colors)
                if key == curses.KEY_UP and x > 0:
                    x -= 1
                if key == curses.KEY_DOWN and x < board.shape[0] - 1:
                    x += 1
                if key == curses.KEY_RIGHT and y < board.shape[1] - 1:
                    y += 1
                if key == curses.KEY_LEFT and y > 0:
                    y -= 1
            # if key == curses.KEY_MOUSE:
            #     _, yy, x, _, bstate = curses.getmouse()
            #     y = yy // 2
            #     if bstate & curses.BUTTON1_CLICKED:
            #         board.detonate(x, y)
            #         display(stdscr, board, colors=colors)
            else:
                if key == 10 and not board.flagged[x, y]:  # ENTER KEY = 10
                    board.detonate(x, y)

                if key == ord("x") or key == ord("f"):
                    if not board.flagged[x, y]:
                        board.flag(x, y)
                    else:
                        board.unflag(x, y)

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
        print("\033[?1003l")
        curses.echo()
        curses.flushinp()
        curses.endwin()


if __name__ == "__main__":
    sys.exit(main())
