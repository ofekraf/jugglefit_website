from dataclasses import dataclass
from typing import Set, Optional
from route_generator.tricks.tags import Tag

@dataclass(kw_only=True)
class Trick:
    # def __init__(self, *, name: str, difficulty: int, props_count: int, tags: List[str], comment: Optional[str]=None):
    name: str
    props_count: int
    difficulty: Optional[int] = None
    tags: Optional[Set[Tag]] = None
    comment: Optional[str] = None
