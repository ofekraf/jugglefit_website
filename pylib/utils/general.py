from typing import Set
from contextlib import contextmanager
import threading


def has_intersection(set1: Set, set2: Set):
    return bool(set1 & set2)


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
