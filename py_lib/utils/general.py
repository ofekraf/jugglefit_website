from typing import Set, List, Optional
from py_lib.prop import Prop
from py_lib.tag import Tag
from py_lib.trick import Trick
from py_lib.consts import (
    DEFAULT_MIN_TRICK_PROPS_COUNT, DEFAULT_MAX_TRICK_PROPS_COUNT,
    DEFAULT_MIN_TRICK_DIFFICULTY, DEFAULT_MAX_TRICK_DIFFICULTY
)
from database.tricks import PROP_TO_TRICKS


def has_intersection(set1: Set, set2: Set) -> bool:
    """Check if two sets have any common elements."""
    return bool(set1 & set2)
