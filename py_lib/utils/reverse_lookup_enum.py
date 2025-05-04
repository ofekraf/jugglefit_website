from enum import Enum

class ReverseLookupEnum(Enum):
    # This class will automatically create the reverse lookup dictionary for subclasses.
    
    @classmethod
    def _reverse_lookup(cls):
        # Creates a dictionary for reverse lookup (value -> name)
        return {item.value: item for item in cls}

    @classmethod
    def get_key_by_value(cls, value):
        # Uses the reverse lookup dictionary for fast access
        reverse_dict = cls._reverse_lookup()
        return reverse_dict.get(value, None)