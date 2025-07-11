from typing import List, Set, Optional
from pylib.classes.prop import Prop
from pylib.classes.tag import Tag
from pylib.classes.trick import Trick
from pylib.classes.route import Route
from pylib.configuration.consts import (
    MIN_TRICK_PROPS_COUNT, MAX_TRICK_PROPS_COUNT,
    MIN_TRICK_DIFFICULTY, MAX_TRICK_DIFFICULTY
)
from pylib.utils.filter_tricks import filter_tricks
from .exceptions import NotEnoughTricksFoundException

class RouteGenerator:
    @staticmethod
    def generate(
        prop: Prop,
        min_props: int = MIN_TRICK_PROPS_COUNT,
        max_props: int = MAX_TRICK_PROPS_COUNT,
        min_difficulty: int = MIN_TRICK_DIFFICULTY,
        max_difficulty: int = MAX_TRICK_DIFFICULTY,
        route_length: int = 5,
        exclude_tags: Optional[Set[Tag]] = None,
        name: str = '',
        duration_seconds: int = 600
    ) -> Route:
        if exclude_tags is None:
            exclude_tags = set()

        # Get filtered tricks
        relevant_tricks = filter_tricks(
            prop=prop,
            min_props=min_props,
            max_props=max_props,
            min_difficulty=min_difficulty,
            max_difficulty=max_difficulty,
            exclude_tags=exclude_tags,
            limit=route_length
        )

        if len(relevant_tricks) < route_length:
            raise NotEnoughTricksFoundException(
                f"Not enough tricks found matching the criteria. Found {len(relevant_tricks)} tricks, but need {route_length}."
            )

        # Select random sample and sort by difficulty
        selected_tricks = sorted(
            relevant_tricks[:route_length],
            key=lambda t: (t.props_count, t.difficulty)
        )

        return Route(
            name=name,
            prop=prop,
            tricks=selected_tricks,
            duration_seconds=duration_seconds
        )
    
