import random
from typing import Set, List, Optional
from py_lib.prop import Prop
from py_lib.tag import Tag
from py_lib.trick import Trick
from py_lib.consts import (
    MIN_TRICK_PROPS_COUNT, MAX_TRICK_PROPS_COUNT,
    MIN_TRICK_DIFFICULTY, MAX_TRICK_DIFFICULTY
)
from database.tricks import PROP_TO_TRICKS

def filter_tricks(
    prop: Prop,
    min_props: int = MIN_TRICK_PROPS_COUNT,
    max_props: int = MAX_TRICK_PROPS_COUNT,
    min_difficulty: int = MIN_TRICK_DIFFICULTY,
    max_difficulty: int = MAX_TRICK_DIFFICULTY,
    limit: Optional[int] = None,
    exclude_tags: Optional[Set[Tag]] = None,
    tricks: Optional[List[Trick]] = None
) -> List[Trick]:
    if exclude_tags is None:
        exclude_tags = set()
    
    if tricks is None:
        tricks = PROP_TO_TRICKS[prop]
    
    filtered_tricks = [
        trick for trick in tricks
        if (min_props <= trick.props_count <= max_props and
            min_difficulty <= trick.difficulty <= max_difficulty and
            not any(tag in exclude_tags for tag in trick.tags))
    ]
    
    if limit is not None and limit > 0:
        filtered_tricks = random.sample(filtered_tricks, min(limit, len(filtered_tricks)))
    
    return filtered_tricks 