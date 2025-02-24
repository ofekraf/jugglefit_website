from typing import List

class Trick:
    def __init__(self, *, name: str, difficulty: int, props_count: int, tags: List[str]):
        self.name = name
        self.difficulty = difficulty
        self.props_count = props_count
        self.tags = tags
