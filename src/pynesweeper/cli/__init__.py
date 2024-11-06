# SPDX-FileCopyrightText: 2024-present Pierre Nodet <nodet.pierre@gmail.com>
#
# SPDX-License-Identifier: MIT
from importlib.metadata import version

import click
import numpy as np

from pynesweeper import Board, Difficulty

arrow_keys = {"\x1b[A", "\x1b[B", "\x1b[C", "\x1b[D"}


@click.group(invoke_without_command=True)
@click.option(
    "-d",
    "--difficulty",
    type=click.Choice(Difficulty, case_sensitive=False),
    help="Difficulty increases board size.",
)
@click.option("--seed", type=int, default=None, help="For replayable games.")
@click.version_option(version=version("pynesweeper"), prog_name="pynesweeper")
def pynesweeper(difficulty, seed):
    board = Board.make_board(np.random.default_rng(seed), difficulty)
    x, y = (0, 0)
    click.clear()
    click.echo(board.show((x, y)))
    while not board.won() and not board.gameover():
        c = click.getchar()
        if c in arrow_keys:
            if c == "\x1b[A" and x > 0:
                x -= 1
            if c == "\x1b[B" and x < board.shape[0]:
                x += 1
            if c == "\x1b[C" and y < board.shape[1]:
                y += 1
            if c == "\x1b[D" and y > 0:
                y -= 1
        if c == "\x0d" and not board.marked[x, y]:
            board.detonate(x, y)
        if c == "x":
            if not board.marked[x, y]:
                board.mark(x, y)
            else:
                board.unmark(x, y)
        click.clear()
        click.echo(board.show((x, y)))
    if board.gameover():
        click.clear()
        board.discovered[:] = True
        click.echo(board.show((x, y)))
    return board
