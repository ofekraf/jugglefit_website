from dataclasses import dataclass
from typing import Set, Optional
from route_generator.tricks.tags import Tag


# Because it breaks the UI
MAX_TRICK_NAME_LENGTH = 75
@dataclass(kw_only=True)
class Trick:
    name: str
    props_count: int
    difficulty: int = -1
    tags: Optional[Set[Tag]] = None
    comment: Optional[str] = None

    def __post_init__(self):
        if len(self.name) > MAX_TRICK_NAME_LENGTH:
            raise ValueError(f"Trick name {self.name} is too long. Please keep it under {MAX_TRICK_NAME_LENGTH} characters.")
