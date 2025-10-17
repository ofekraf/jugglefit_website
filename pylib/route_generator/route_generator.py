from typing import List, Set, Optional
from pylib.classes.prop import Prop
from pylib.classes.tag import Tag
from pylib.classes.route import Route
from pylib.configuration.consts import MIN_TRICK_DIFFICULTY, MAX_TRICK_DIFFICULTY
from pylib.utils.filter_tricks import filter_tricks
from .exceptions import NotEnoughTricksFoundException

class RouteGenerator:
    @staticmethod
    def generate(
        *,
        prop: Prop,
        min_props: Optional[int] = None,
        max_props: Optional[int] = None,
        min_difficulty: Optional[int] = None,
        max_difficulty: Optional[int] = None,
        route_length: int = 5,
        exclude_tags: Optional[Set[Tag]] = None,
        name: str = '',
        duration_seconds: int = 600,
        max_throw: Optional[int] = None,
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
            limit=route_length,
            max_throw=max_throw,
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
    
