from dataclasses import dataclass
from typing import List, Optional

@dataclass(kw_only=True)
class Trick:
    # def __init__(self, *, name: str, difficulty: int, props_count: int, tags: List[str], comment: Optional[str]=None):
    name: str
    props_count: int
    difficulty: Optional[int] = None
    tags: Optional[List[str]] = None
    comment: Optional[str] = None
