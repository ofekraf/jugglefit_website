import random
from typing import List, Set

from route_generator.tricks.tags import Tag
from route_generator.utils.general import has_intersection

from .exceptions import NotEnoughTricksFoundException
from .prop import Prop

from .tricks.balls import BALLS_TRICKS
from .tricks.clubs import CLUBS_TRICKS
from .tricks.rings import RINGS_TRICKS

PROP_TO_TRICKS = {
    Prop.Balls: BALLS_TRICKS, 
    Prop.Clubs: CLUBS_TRICKS,
    Prop.Rings: RINGS_TRICKS,
}

def generate_route(*, 
    prop: Prop,
    min_props: int,
    max_props: int, 
    min_difficulty: int,
    max_difficulty: int,
    route_length: int,
    excluded_tags: Set[Tag]
):
    relevant_tricks = [trick for trick in PROP_TO_TRICKS[prop] if 
                       max_difficulty >= trick.difficulty >= min_difficulty and
                       max_props >= trick.props_count >= min_props and
                       not has_intersection(trick.tags, excluded_tags)]
    
    if len(relevant_tricks) < route_length:
        raise NotEnoughTricksFoundException()
    route = random.sample(relevant_tricks, route_length)
    route.sort(key=lambda trick: (trick.props_count, trick.difficulty))
    return route
    
