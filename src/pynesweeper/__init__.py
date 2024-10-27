# SPDX-FileCopyrightText: 2024-present Pierre Nodet <nodet.pierre@gmail.com>
#
# SPDX-License-Identifier: MIT

import sys
from dataclasses import dataclass, field
from enum import StrEnum
from itertools import product

import numpy as np
from scipy import signal


class Difficulty(StrEnum):
    DEBUG = "d"
    EASY = "e"
    MEDIUM = "m"
    HARD = "h"


kernel = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]])

colors = list(reversed(range(31, 38)))


def colored(color, s):
    return f"\033[{color}m{s}\033[0m"


def bold(s):
    return f"\033[1m{s}\033[0m"


@dataclass
class Board:
    mined: np.ndarray
    neighbours: np.ndarray

    discovered: np.ndarray = field(init=False)
    marked: np.ndarray = field(init=False)
    mines: set[int] = field(init=False)

    def __post_init__(self):
        self.discovered = np.zeros_like(self.mined, dtype=bool)
        self.marked = np.zeros_like(self.mined, dtype=bool)
        self.mines = set(np.flatnonzero(self.mined))

    def __contains__(self, xy):
        x, y = xy
        xmax, ymax = self.mined.shape
        return x >= 0 and x < xmax and y >= 0 and y < ymax

    @classmethod
    def make_board(cls, rng, difficulty=Difficulty.MEDIUM):
        match difficulty:
            case Difficulty.DEBUG:
                size, p = (4, 5), 0.1
            case Difficulty.EASY:
                size, p = (4, 6), 0.1
            case Difficulty.MEDIUM:
                size, p = (8, 12), 0.15
            case Difficulty.HARD:
                size, p = (12, 24), 0.2

        mined = rng.binomial(1, p, size=size).astype(bool)
        neighbours = signal.convolve(mined, kernel, mode="same")
        return cls(mined, neighbours)

    @property
    def shape(self):
        return self.mined.shape

    def char(self, x, y):
        if self.marked[x, y]:
            return bold("x")
        if self.discovered[x, y]:
            neigbours = self.neighbours[x, y]
            return colored(colors[neigbours], neigbours)
        return " "

    def show(self, selector=None):
        x, y = selector if selector is not None else (-1, -1)
        m, n = self.neighbours.shape
        o = "+" + "+".join(["---" for _ in range(n)]) + "+"
        for i in range(m):
            if x == i:

                def s(j):
                    return "-" if y == j else " "
            else:

                def s(_):
                    return " "

            o += "\n|"
            o += "|".join([f"{s(j)}{self.char(i, j)}{s(j)}" for j in range(n)])
            o += "|\n"
            o += "+" + "+".join(["---" for _ in range(n)]) + "+"
        return o

    def mark(self, x, y):
        if not self.discovered[x, y]:
            self.marked[x, y] = True

    def unmark(self, x, y):
        if self.marked[x, y]:
            self.marked[x, y] = False

    def won(self):
        return set(np.flatnonzero(~self.discovered)) == self.mines

    def detonate(self, x, y, *, cascade=False):
        if self.mined[x, y] == 1 and not cascade:
            print("Game Over")
            sys.exit()
        elif not self.discovered[x, y]:
            empty = self.neighbours[x, y] == 0
            self.discovered[x, y] = True
            if empty:
                for xx, yy in product([x - 1, x, x + 1], [y - 1, y, y + 1]):
                    if (xx, yy) in self:
                        self.detonate(xx, yy, cascade=True)
