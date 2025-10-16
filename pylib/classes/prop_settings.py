from collections.abc import Set
from dataclasses import dataclass, field
from typing import List, Optional

from pylib.classes.tag import Tag
from pylib.classes.trick import Trick

@dataclass
class PropSettings:
    relevant_tags: Set[Tag] = field(default_factory=set)
    min_props: Optional[int] = None
    max_props: Optional[int] = None
    max_throw: Optional[int] = None

    @classmethod
    def from_tricks(cls, tricks: List[Trick]) -> 'PropSettings':
        relevant_tags = set()
        min_props = None
        max_props = None
        max_throw = None
        
        for trick in tricks:
            relevant_tags.update(trick.tags or [])
            props_count = trick.props_count
            if min_props is None or props_count < min_props:
                min_props = props_count
            if max_props is None or props_count > max_props:
                max_props = props_count
            if trick.max_throw is not None:
                if max_throw is None or trick.max_throw > max_throw:
                    max_throw = trick.max_throw

        return cls(
            relevant_tags=list(relevant_tags),
            min_props=min_props,
            max_props=max_props,
            max_throw=max_throw,
        )

    def to_dict(self):
        return {
            'relevant_tags': [str(tag) for tag in self.relevant_tags],
            'min_props': self.min_props,
            'max_props': self.max_props,
            'max_throw': self.max_throw
        }