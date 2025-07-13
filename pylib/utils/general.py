from typing import Set, Optional
from contextlib import contextmanager
import threading


def has_intersection(set1: Set, set2: Set) -> bool:
    return bool(set1 & set2)


def quote_string(val: Optional[str]) -> str:
    """
    Returns the string value always wrapped in double quotes, escaping any embedded double quotes.
    """
    s = '' if val is None else str(val)
    s = s.replace('"', '""')  # Escape embedded double quotes for CSV
    return f'"{s}"'


@contextmanager
def acquired(mutex: threading.Lock, timeout: float = 5.0):
    """Context manager for acquiring a mutex with timeout.
    
    Raises:
        RuntimeError: If mutex cannot be acquired within timeout period
    """
    if not mutex.acquire(timeout=timeout):
        raise RuntimeError(f"Could not acquire mutex within {timeout} seconds")
    try:
        yield
    finally:
        mutex.release()
