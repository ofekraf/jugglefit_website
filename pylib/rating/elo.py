"""
Online Elo-style update for the 0-100 difficulty scale.

Anchors (master tricks) contribute to the expectation but are never mutated.
"""
from __future__ import annotations

from dataclasses import dataclass

from pylib.configuration.consts import (
    ELO_SCALE, SIGMA_DECAY, MIN_TRICK_DIFFICULTY, MAX_TRICK_DIFFICULTY,
)


@dataclass
class Side:
    mu: float
    sigma: float          # 0.0 for anchors
    is_anchor: bool


def expected_left(mu_left: float, mu_right: float) -> float:
    return 1.0 / (1.0 + 10.0 ** ((mu_right - mu_left) / ELO_SCALE))


def vote_weight(reliability: float) -> float:
    """Map reliability ∈ [0,1] to weight ∈ [0,1]; 0.5 → 0."""
    return max(0.0, 2.0 * reliability - 1.0)


_WINNER_SCORE = {"left": 1.0, "right": 0.0}


def apply_comparison(left: Side, right: Side, *, winner: str,
                     reliability: float) -> tuple[Side, Side]:
    """Return updated (left, right). 'skip' is handled by the caller."""
    if winner not in _WINNER_SCORE:
        return left, right
    s_left = _WINNER_SCORE[winner]
    e_left = expected_left(left.mu, right.mu)
    w = vote_weight(reliability)

    def step(side: Side, s: float, e: float) -> Side:
        if side.is_anchor:
            return side
        k = max(1.0, side.sigma) * 0.8
        mu = side.mu + w * k * (s - e)
        mu = max(MIN_TRICK_DIFFICULTY, min(MAX_TRICK_DIFFICULTY, mu))
        sigma = max(1.0, side.sigma * SIGMA_DECAY)
        return Side(mu=mu, sigma=sigma, is_anchor=False)

    return step(left, s_left, e_left), step(right, 1.0 - s_left, 1.0 - e_left)
