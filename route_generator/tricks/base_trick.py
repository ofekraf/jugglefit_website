from dataclasses import dataclass
from typing import Set, Optional
from route_generator.tricks.tags import Tag


# Because it breaks the UI
MAX_TRICK_NAME_LENGTH = 75

MIN_TRICK_DIFFICULTY = 0
MAX_TRICK_DIFFICULTY = 100

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

        if (self.difficulty != -1 and 
        not MIN_TRICK_DIFFICULTY <= self.difficulty <= MAX_TRICK_DIFFICULTY):
            raise ValueError(f"Trick {self.name} difficulty must be between {MIN_TRICK_DIFFICULTY} and {MAX_TRICK_DIFFICULTY}.")

    def to_dict(self) -> dict:
        """Convert the trick to a dictionary for JSON serialization."""
        return {
            'name': self.name,
            'props_count': self.props_count,
            'difficulty': self.difficulty,
            'tags': [str(tag) for tag in self.tags] if self.tags else [],
            'comment': self.comment
        }
