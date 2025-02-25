from dataclasses import dataclass
from typing import Dict, List

from route_generator.prop import Prop
from route_generator.tricks.base_trick import Trick


@dataclass(kw_only=True)
class Route:
    name: str
    prop: Prop
    
    # Dict[props_count: tricks]
    tricks: List[Trick]
    
    @property
    def tricks_map(self) -> Dict[int, List[Trick]]:
        """get map from props count to relevant tricks

        Returns:
            Dict[int, List[Trick]]: key is props_count
        """
        props_count_map = {}
        for trick in self.tricks:
            if trick.props_count not in props_count_map.keys():
                props_count_map[trick.props_count] = []
            props_count_map[trick.props_count].append(trick)
    
        return props_count_map