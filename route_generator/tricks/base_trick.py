from dataclasses import dataclass
from typing import Set, Optional
from route_generator.tricks.tags import Tag

@dataclass(kw_only=True)
class Trick:
    name: str
    props_count: int
    difficulty: int = -1
    tags: Optional[Set[Tag]] = None
    comment: Optional[str] = None
