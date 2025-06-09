from typing import Set


def has_intersection(set1: Set, set2: Set) -> bool:
    """Check if two sets have any common elements."""
    return bool(set1 & set2)
