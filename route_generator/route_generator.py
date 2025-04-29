import random
from typing import Set

from py_lib.prop import Prop
from py_lib.route import DEFAULT_ROUTE_DURATION_SECONDS, Route
from database.tricks import PROP_TO_TRICKS
from py_lib.tag import Tag
from py_lib.utils.general import has_intersection

from .exceptions import NotEnoughTricksFoundException


class RouteGenerator:
    @staticmethod
    def generate(*, 
        prop: Prop,
        min_props: int,
        max_props: int, 
        min_difficulty: int,
        max_difficulty: int,
        route_length: int,
        exclude_tags: Set[Tag],
        name: str,
        duration_seconds: int = DEFAULT_ROUTE_DURATION_SECONDS
    ) -> Route:
        relevant_tricks = [trick for trick in PROP_TO_TRICKS[prop] if 
                        max_difficulty >= trick.difficulty >= min_difficulty and
                        max_props >= trick.props_count >= min_props and
                        not has_intersection(trick.tags, exclude_tags)]
        
        if len(relevant_tricks) < route_length:
            raise NotEnoughTricksFoundException()
        tricks = random.sample(relevant_tricks, route_length)
        tricks.sort(key=lambda trick: (trick.props_count, trick.difficulty))
        
        return Route(name=name, prop=prop, tricks=tricks, duration_seconds=duration_seconds)
    
