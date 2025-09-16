from dataclasses import dataclass
from typing import Set, Optional

from pylib.classes.tag import Tag
from pylib.configuration.consts import (
    MAX_TRICK_NAME_LENGTH,
    MIN_TRICK_PROPS_COUNT, MAX_TRICK_PROPS_COUNT,
    MIN_TRICK_DIFFICULTY, MAX_TRICK_DIFFICULTY
)

@dataclass(kw_only=True)
class Trick:
    name: Optional[str]
    props_count: int
    difficulty: int = -1
    tags: Optional[Set[Tag]] = None
    comment: Optional[str] = None
    max_throw: Optional[int] = None
    siteswap_x: Optional[str] = None

    def __post_init__(self):
        if len(self.name) > MAX_TRICK_NAME_LENGTH:
            raise ValueError(f"Trick name {self.name} is too long. Please keep it under {MAX_TRICK_NAME_LENGTH} characters.")

        if (self.difficulty != -1 and 
        not MIN_TRICK_DIFFICULTY <= self.difficulty <= MAX_TRICK_DIFFICULTY):
            raise ValueError(f"Trick {self.name} difficulty must be between {MIN_TRICK_DIFFICULTY} and {MAX_TRICK_DIFFICULTY}.")

        if not MIN_TRICK_PROPS_COUNT <= self.props_count <= MAX_TRICK_PROPS_COUNT:
            raise ValueError(f"Trick {self.name} props count must be between {MIN_TRICK_PROPS_COUNT} and {MAX_TRICK_PROPS_COUNT}.")
        
        if self.siteswap_x is None and self.name is None:
            raise ValueError("Either siteswap_x or name must be provided for a trick.")
        
    def __eq__(self, other):
        return ((self.props_count == other.props_count) and 
            (self.name == other.name or self.siteswap_x == other.siteswap_x))
        
    def to_dict(self) -> dict:
        """Convert the trick to a dictionary for JSON serialization."""
        return {
            'name': self.name,
            'props_count': self.props_count,
            'difficulty': self.difficulty,
            'tags': [str(tag) for tag in self.tags] if self.tags else [],
            'comment': self.comment,
            'max_throw': self.max_throw,
            'siteswap_x': self.siteswap_x
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Trick':
        """Create a Trick instance from a dictionary."""
        tags = {Tag.get_key_by_value(tag) for tag in data.get('tags', [])} if data.get('tags') else None
        return cls(
            name=data['name'],
            props_count=data['props_count'],
            difficulty=data.get('difficulty', -1),
            tags=tags,
            comment=data.get('comment'),
            max_throw=data.get('max_throw'),
            siteswap_x=data.get('siteswap_x')
        )
