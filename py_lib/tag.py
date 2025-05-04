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
    Spin180 = "180 spin"
    Spin360 = "360 spin"
    Spin720 = "720 spin"
    Spin1080 = "1080 spin"
    Spin1440 = "1440 spin"
    MultiStage = "multi stage"
    
    # Base Pattern
    BasePattern = "base pattern"
    SyncBasePattern = "sync base pattern"
    AsyncBasePattern = "async base pattern"
    
    # Body Throws
    Backcrosses = "backcrosses"
    Shoulders = "shoulders"
    Overheads = "overheads"
    Necks = "necks"
    UnderLegs = "under legs"
    SpecialBodyThrows = "special body throws"
    Lazies = "lazies"
    ReverseShoulders = "reverse shoulders"

    # Spin Control
    Flats = "flats"
    SpinControl = "spin control"
    FlatFront = "flat front"

    # Siteswap
    SyncSiteswap = "sync siteswap"
    AsyncSiteswap = "async siteswap"
    
    # Isolation
    Isolated = "isolated"
    OnTheKnees = "on the knees"
    Sitting = "sitting"
    OnTheBack = "on the back"

    def __lt__(self, other):
        """Make Tag sortable by comparing their values."""
        return self.value < other.value

    def __str__(self) -> str:
        """Make the tag JSON serializable by returning its value."""
        return self.value
    

TAG_CATEGORY_MAP = {
    # Spin
    Tag.Spin180: TagCategory.Spin,
    Tag.Spin360: TagCategory.Spin,
    Tag.Spin720: TagCategory.Spin,
    Tag.Spin1080: TagCategory.Spin,
    Tag.Spin1440: TagCategory.Spin,
    Tag.MultiStage: TagCategory.Spin,
    
    # Base Pattern
    Tag.BasePattern: TagCategory.BasePattern,
    Tag.SyncBasePattern: TagCategory.BasePattern,
    Tag.AsyncBasePattern: TagCategory.BasePattern,
    
    # Body Throws
    Tag.Backcrosses: TagCategory.BodyThrows,
    Tag.Shoulders: TagCategory.BodyThrows,
    Tag.Overheads: TagCategory.BodyThrows,
    Tag.Necks: TagCategory.BodyThrows,
    Tag.UnderLegs: TagCategory.BodyThrows,
    Tag.SpecialBodyThrows: TagCategory.BodyThrows,
    Tag.Lazies: TagCategory.BodyThrows,
    Tag.ReverseShoulders: TagCategory.BodyThrows,

    # Spin Control
    Tag.Flats: TagCategory.SpinControl,
    Tag.SpinControl: TagCategory.SpinControl,
    Tag.FlatFront: TagCategory.SpinControl,

    # Siteswap
    Tag.SyncSiteswap: TagCategory.Siteswap,
    Tag.AsyncSiteswap: TagCategory.Siteswap,
    
    # Isolation
    Tag.Isolated: TagCategory.Isolation,
    Tag.OnTheKnees: TagCategory.Isolation,
    Tag.Sitting: TagCategory.Isolation,
    Tag.OnTheBack: TagCategory.Isolation,
    
}