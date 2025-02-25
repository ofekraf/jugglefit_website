from dataclasses import dataclass
from typing import Dict, List

from route_generator.prop import Prop
from route_generator.tricks.base_trick import Trick


@dataclass(kw_only=True)
class Route:
    name: str
    prop: Prop
    
    # Dict[props_count: tricks]
    tricks: Dict[int, List[Trick]]
    
    @classmethod
    def from_list(cls, *, name: str, prop: Prop, tricks: List[Trick]):
        tricks.sort(key=lambda trick: (trick.props_count, trick.difficulty))
        formatted_tricks = {}
        for trick in tricks:
            if trick.props_count not in formatted_tricks.keys():
                formatted_tricks[trick.props_count] = []
            formatted_tricks[trick.props_count].append(trick)
    
        return cls(name=name, prop=prop, tricks=formatted_tricks)