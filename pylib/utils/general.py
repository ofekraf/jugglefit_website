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


def add_line_breaks_to_trick_name(name: str, max_length: int = 25) -> str:
    """
    Intelligently adds <br> tags to long trick names for better display.

    Breaks at natural points like arrows (→) and after certain character counts
    to prevent text overflow in fixed-width containers.

    Args:
        name: The trick name to process
        max_length: Maximum characters per line before forcing a break

    Returns:
        Trick name with <br> tags inserted at strategic positions
    """
    if len(name) <= max_length:
        return name

    # Strategy 1: Break after arrows if present
    if '→' in name:
        parts = name.split('→')
        result = []
        current_line = ""

        for i, part in enumerate(parts):
            # Add arrow back except for the last part
            segment = part + ('→' if i < len(parts) - 1 else '')

            # If adding this segment would make the line too long, break
            if current_line and len(current_line) + len(segment) > max_length:
                result.append(current_line.strip())
                current_line = segment
            else:
                current_line += segment

        if current_line:
            result.append(current_line.strip())

        return '<br>'.join(result)

    # Strategy 2: Break at spaces near the max_length threshold
    words = name.split()
    result = []
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()

        if len(test_line) > max_length:
            if current_line:
                result.append(current_line)
            current_line = word
        else:
            current_line = test_line

    if current_line:
        result.append(current_line)

    return '<br>'.join(result)
