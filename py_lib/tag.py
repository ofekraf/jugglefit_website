from .utils.reverse_lookup_enum import ReverseLookupEnum

class TagCategory(ReverseLookupEnum):
    Spin = "spin"
    BasePattern = "base pattern"
    BodyThrows = "body throws"
    SpinControl = "spin control"
    Siteswap = "siteswap"
    Isolation = "isolation"

    def __lt__(self, other):
        """Make TagCategory sortable by comparing their values."""
        return self.value < other.value

    def __str__(self) -> str:
        """Make the TagCategory JSON serializable by returning its value."""
        return self.value
    

class Tag(ReverseLookupEnum):
    # Spin
    Spin180 = "180 spin", TagCategory.Spin
    Spin360 = "360 spin", TagCategory.Spin
    Spin720 = "720 spin", TagCategory.Spin
    Spin1080 = "1080 spin", TagCategory.Spin
    Spin1440 = "1440 spin", TagCategory.Spin
    MultiStage = "multi stage", TagCategory.Spin
    
    # Base Pattern
    BasePattern = "base pattern", TagCategory.BasePattern
    SyncBasePattern = "sync base pattern", TagCategory.BasePattern
    AsyncBasePattern = "async base pattern", TagCategory.BasePattern
    
    # Body Throws
    Backcrosses = "backcrosses", TagCategory.BodyThrows
    Shoulders = "shoulders", TagCategory.BodyThrows
    Overheads = "overheads", TagCategory.BodyThrows
    Necks = "necks", TagCategory.BodyThrows
    UnderLegs = "under legs", TagCategory.BodyThrows
    SpecialBodyThrows = "special body throws", TagCategory.BodyThrows
    Lazies = "lazies", TagCategory.BodyThrows
    ReverseShoulders = "reverse shoulders", TagCategory.BodyThrows

    # Spin Control
    Flats = "flats", TagCategory.SpinControl
    SpinControl = "spin control", TagCategory.SpinControl
    FlatFront = "flat front", TagCategory.SpinControl

    # Siteswap
    SyncSiteswap = "sync siteswap", TagCategory.Siteswap
    AsyncSiteswap = "async siteswap", TagCategory.Siteswap
    
    # Isolation
    Isolated = "isolated", TagCategory.Isolation
    OnTheKnees = "on the knees", TagCategory.Isolation
    Sitting = "sitting", TagCategory.Isolation
    OnTheBack = "on the back", TagCategory.Isolation
    
    @classmethod
    def _reverse_lookup(cls):
        # Creates a dictionary for reverse lookup (value -> name)
        return {item.value[0]: item for item in cls}

    def __lt__(self, other):
        """Make Tag sortable by comparing their values."""
        return self.value[0] < other.value[0]

    def __str__(self) -> str:
        """Make the tag JSON serializable by returning its value."""
        return self.value[0]
