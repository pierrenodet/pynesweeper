# SPDX-FileCopyrightText: 2024-present Pierre Nodet <nodet.pierre@gmail.com>
#
# SPDX-License-Identifier: MIT

from dataclasses import dataclass, field
from enum import StrEnum
from itertools import product

import numpy as np
from scipy import signal


class Difficulty(StrEnum):
    EASY = "e"
    MEDIUM = "m"
    HARD = "h"
    VERY_HARD = "hh"

    @property
    def size(self):
        match self:
            case Difficulty.EASY:
                return (4, 5)
            case Difficulty.MEDIUM:
                return (8, 12)
            case Difficulty.HARD:
                return (12, 24)
            case Difficulty.VERY_HARD:
                return (16, 28)

    @property
    def pbomb(self):
        match self:
            case Difficulty.EASY:
                return 0.1
            case Difficulty.MEDIUM:
                return 0.15
            case Difficulty.HARD:
                return 0.2
            case Difficulty.VERY_HARD:
                return 0.25


KERNEL = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]])


@dataclass
class Board:
    mined: np.ndarray
    neighbours: np.ndarray

    discovered: np.ndarray = field(init=False)
    flagged: np.ndarray = field(init=False)

    def __post_init__(self):
        self.discovered = np.zeros_like(self.mined, dtype=bool)
        self.flagged = np.zeros_like(self.mined, dtype=bool)

    def __contains__(self, xy):
        x, y = xy
        xmax, ymax = self.mined.shape
        return x >= 0 and x < xmax and y >= 0 and y < ymax

    @classmethod
    def make_board(cls, seed=None, difficulty=Difficulty.MEDIUM):
        rng = np.random.default_rng(seed)
        mined = rng.binomial(1, difficulty.pbomb, size=difficulty.size).astype(bool)
        neighbours = signal.convolve(mined, KERNEL, mode="same")
        return cls(mined, neighbours)

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

    def detonate(self, x, y):
        if not self.discovered[x, y]:
            self.discovered[x, y] = True
            if self.neighbours[x, y] == 0:
                for xx, yy in product([x - 1, x, x + 1], [y - 1, y, y + 1]):
                    if (xx, yy) in self:
                        self.detonate(xx, yy)
