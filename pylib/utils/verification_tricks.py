"""
Trick selection utilities for the verification game.

This module provides functions to select trick pairs for the two-round
verification game:
- Round 1: Obvious difficulty pair (easy vs hard)
- Round 2: Random pair from similar difficulty range
"""

import random
from typing import Tuple

from pylib.classes.prop import Prop
from pylib.classes.trick import Trick
from pylib.utils.filter_tricks import filter_tricks


def select_obvious_pair(prop: Prop = Prop.Balls) -> Tuple[Trick, Trick]:
    """
    Select an obvious difficulty pair for Round 1 verification.

    Easy trick: difficulty <= 15
    Hard trick: difficulty >= 70

    This creates a clear ~55+ point difficulty spread to verify
    that the user can identify basic difficulty differences.

    Args:
        prop: Prop type to select tricks from (default: Balls)

    Returns:
        Tuple of (easy_trick, hard_trick)

    Raises:
        ValueError: If not enough tricks available in the difficulty ranges
    """
    # Get pool of easy tricks
    easy_tricks = filter_tricks(
        prop=prop,
        max_difficulty=15,
        limit=10
    )

    # Get pool of hard tricks
    hard_tricks = filter_tricks(
        prop=prop,
        min_difficulty=70,
        limit=10
    )

    if len(easy_tricks) < 1 or len(hard_tricks) < 1:
        raise ValueError(
            f"Not enough tricks for obvious pair. "
            f"Found {len(easy_tricks)} easy tricks and {len(hard_tricks)} hard tricks"
        )

    easy = random.choice(easy_tricks)
    hard = random.choice(hard_tricks)

    return (easy, hard)


def select_random_pair(prop: Prop = Prop.Balls) -> Tuple[Trick, Trick]:
    """
    Select two random tricks from a moderate difficulty range for Round 2.

    Difficulty range: 20-80 (avoids extremes)
    Ensures tricks are different from each other.

    Args:
        prop: Prop type to select tricks from (default: Balls)

    Returns:
        Tuple of (trick1, trick2) - two different tricks

    Raises:
        ValueError: If not enough tricks available (need at least 2)
    """
    # Get pool of moderate difficulty tricks
    tricks = filter_tricks(
        prop=prop,
        min_difficulty=20,
        max_difficulty=80,
        limit=2
    )

    if len(tricks) < 2:
        raise ValueError(
            f"Not enough tricks for random pair. "
            f"Found {len(tricks)} tricks, need at least 2"
        )

    return (tricks[0], tricks[1])


def randomize_order(trick1: Trick, trick2: Trick) -> Tuple[Trick, Trick, str]:
    """
    Randomly order two tricks for display.

    This prevents the harder trick from always appearing in the same position,
    which could allow users to game the system.

    Args:
        trick1: First trick
        trick2: Second trick

    Returns:
        Tuple of (trick_left, trick_right, correct_position)
        where correct_position is 'left' or 'right' indicating which
        position contains the harder trick.
    """
    # Determine which trick is harder
    if trick1.difficulty > trick2.difficulty:
        harder = trick1
        easier = trick2
    else:
        harder = trick2
        easier = trick1

    # Randomly place harder trick on left or right
    if random.choice([True, False]):
        return (harder, easier, 'left')
    else:
        return (easier, harder, 'right')
