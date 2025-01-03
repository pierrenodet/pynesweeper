# SPDX-FileCopyrightText: 2024-present Pierre Nodet <nodet.pierre@gmail.com>
#
# SPDX-License-Identifier: MIT

from enum import Enum
from itertools import product

import numpy as np
from scipy import signal


class Difficulty(Enum):
    EASY = (4, 5), 0.1
    MEDIUM = (8, 12), 0.15
    HARD = (12, 24), 0.2
    VERY_HARD = (16, 28), 0.25

    def __init__(self, size, pbomb):
        self.size = size
        self.pbomb = pbomb

    def __str__(self):
        return self.name

    @staticmethod
    def from_string(s):
        try:
            return Difficulty[s]
        except KeyError as exc:
            raise ValueError from exc


KERNEL = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]])


class Board:
    def __init__(self, mined):
        self.mined = mined

        self.neighbours = signal.convolve(self.mined, KERNEL, mode="same")
        self.discovered = np.zeros_like(self.mined, dtype=bool)
        self.flagged = np.zeros_like(self.mined, dtype=bool)

    @classmethod
    def make_board(cls, difficulty, *, seed=None):
        rng = np.random.default_rng(seed)
        mined = rng.binomial(1, difficulty.pbomb, size=difficulty.size).astype(bool)
        return cls(mined)

    def __contains__(self, xy):
        x, y = xy
        xmax, ymax = self.mined.shape
        return x >= 0 and x < xmax and y >= 0 and y < ymax

    @property
    def shape(self):
        return self.mined.shape

    def asstr(self):
        s = np.full(self.shape, " ", dtype="U1")
        s[self.neighbours > 0] = self.neighbours[self.neighbours > 0].astype("U1")
        s[self.mined] = "@"
        s[~self.discovered] = "■"
        s[self.flagged] = "F"
        return s

    def cues(self):
        c = np.zeros(self.shape, dtype=int)
        mask = (self.neighbours > 0) & self.discovered & ~self.flagged & ~self.mined
        c[mask] = self.neighbours[mask]
        return c

    def flag(self, x, y):
        if not self.discovered[x, y]:
            self.flagged[x, y] = True

    def unflag(self, x, y):
        if self.flagged[x, y]:
            self.flagged[x, y] = False

    def won(self):
        return np.all(self.mined[~self.discovered])

    def gameover(self):
        return np.any(self.mined[self.discovered])

    @property
    def remaining_mines(self) -> int:
        return (np.sum(self.mined) - np.sum(self.flagged)).item()

    def chord(self, x, y):
        flag_neighbours = signal.convolve(self.flagged, KERNEL, mode="same")
        if self.discovered[x, y] and self.neighbours[x, y] == flag_neighbours[x, y]:
            for xx, yy in product([x - 1, x, x + 1], [y - 1, y, y + 1]):
                if (xx, yy) in self:
                    self.detonate(xx, yy)

    def detonate(self, x, y):
        if not self.discovered[x, y] and not self.flagged[x, y]:
            self.discovered[x, y] = True
            if self.neighbours[x, y] == 0:
                for xx, yy in product([x - 1, x, x + 1], [y - 1, y, y + 1]):
                    if (xx, yy) in self:
                        self.detonate(xx, yy)
