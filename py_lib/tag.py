from .utils.reverse_lookup_enum import ReverseLookupEnum

class Tag(ReverseLookupEnum):
    Spin = "spin"
    MultiSpin = "multi spin"
    Siteswap = "siteswap"
    BasePattern = "base pattern"
    BodyThrows = "body throws"
    SpinControl = "spin control"
    
    def __lt__(self, other):
        """Make Tag sortable by comparing their values."""
        return self.value < other.value

    def __str__(self) -> str:
        """Make the tag JSON serializable by returning its value."""
        return self.value
    
TAG_OPTIONS = [t.value for t in Tag]
    