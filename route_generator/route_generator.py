import random
from typing import Set

from .tricks.tags import Tag
from .utils.general import has_intersection

from .exceptions import NotEnoughTricksFoundException
from .prop import Prop

from .tricks.balls import BALLS_TRICKS
from .tricks.clubs import CLUBS_TRICKS
from .tricks.rings import RINGS_TRICKS

# @todo: Do I wastefully copy here huge lists?
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
    exclude_tags: Set[Tag]
):
    relevant_tricks = [trick for trick in PROP_TO_TRICKS[prop] if 
                       max_difficulty >= trick.difficulty >= min_difficulty and
                       max_props >= trick.props_count >= min_props and
                       not has_intersection(trick.tags, exclude_tags)]
    
    if len(relevant_tricks) < route_length:
        raise NotEnoughTricksFoundException()
    tricks = random.sample(relevant_tricks, route_length)
    tricks.sort(key=lambda trick: (trick.props_count, trick.difficulty))
    
    route = dict()
    for trick in tricks:
        if trick.props_count not in route.keys():
            route[trick.props_count] = []
        route[trick.props_count].append(trick)
    
    return route
    
