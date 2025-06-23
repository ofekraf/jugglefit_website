from contextlib import contextmanager
import threading


@contextmanager
def acquired(lock: threading.Lock, timeout: float = 5.0):
    """Context manager for acquiring a lock with timeout.
    
    Raises:
        RuntimeError: If lock cannot be acquired within timeout period
    """
    if not lock.acquire(timeout=timeout):
        raise RuntimeError(f"Could not acquire lock within {timeout} seconds")
    try:
        yield
    finally:
        lock.release()
