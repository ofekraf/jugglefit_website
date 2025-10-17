import random
from typing import Set, List, Optional
from hardcoded_database.tricks import ALL_PROPS_SETTINGS, ALL_PROPS_TRICKS
from pylib.classes.prop import Prop
from pylib.classes.tag import Tag
from pylib.classes.trick import Trick
from pylib.configuration.consts import MIN_TRICK_DIFFICULTY, MAX_TRICK_DIFFICULTY


from pylib.utils.general import has_intersection


def filter_tricks(
    prop: Prop,
    min_props: Optional[int] = None,
    max_props: Optional[int] = None,
    min_difficulty: Optional[int] = None,
    max_difficulty: Optional[int] = None,
    limit: Optional[int] = None,
    exclude_tags: Optional[Set[Tag]] = None,
    tricks: Optional[List[Trick]] = None,
    max_throw: Optional[int] = None,
) -> List[Trick]:
    prop_settings = ALL_PROPS_SETTINGS[prop]
    
    exclude_tags = exclude_tags if exclude_tags is not None else set()
    tricks = tricks if tricks is not None else ALL_PROPS_TRICKS[prop]
    min_props = min_props if min_props is not None else prop_settings.min_props
    max_props = max_props if max_props is not None else prop_settings.max_props
    min_difficulty = min_difficulty if min_difficulty is not None else MIN_TRICK_DIFFICULTY
    max_difficulty = max_difficulty if max_difficulty is not None else MAX_TRICK_DIFFICULTY
    
    filtered_tricks = [
        trick for trick in tricks
        if (min_props <= trick.props_count <= max_props and
            min_difficulty <= trick.difficulty <= max_difficulty and
            not has_intersection(trick.tags, exclude_tags) and
            (max_throw is None or (
                trick.max_throw is not None and trick.max_throw <= max_throw
                )
            ))
    ]
    
    if limit is not None and limit > 0:
        filtered_tricks = random.sample(filtered_tricks, min(limit, len(filtered_tricks)))
    
    return filtered_tricks 