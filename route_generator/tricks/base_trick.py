from typing import List, Optional

class Trick:
    def __init__(self, *, name: str, difficulty: int, props_count: int, tags: List[str], comment: Optional[str]=None):
        self.name = name
        self.difficulty = difficulty
        self.props_count = props_count
        self.tags = tags
        self.comment = comment
