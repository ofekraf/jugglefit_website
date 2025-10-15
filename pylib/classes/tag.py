from pylib.utils.reverse_lookup_enum import ReverseLookupEnum


class TagCategory(ReverseLookupEnum):
    Spin = "spin"
    BasePattern = "base pattern"
    BodyThrows = "body throws"
    SpinControl = "spin control"
    Siteswap = "siteswap"
    Isolation = "isolation"
    OneSidedPassing = "one-sided-passing"
    TwoSidedPassing = "two-sided-passing"

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
    AnyBasePattern = "any base pattern"
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
    
    # Passing
    TwoCount = "2-count"
    FourCount = "4-count"
    OneCount = "1-count"
    ThreeCount = "3-count"
    FourHandedSiteswaps = "4-handed siteswaps"

    def __lt__(self, other):
        """Make Tag sortable by comparing their values."""
        return self.value < other.value

    def __str__(self) -> str:
        """Make the tag JSON serializable by returning its value."""
        return self.value

TAG_CATEGORY_MAP = {
    TagCategory.Spin: {
        Tag.Spin180,
        Tag.Spin360,
        Tag.Spin720,
        Tag.Spin1080,
        Tag.Spin1440,
        Tag.MultiStage,
    },
    
    TagCategory.BasePattern: {
        Tag.AnyBasePattern,
        Tag.SyncBasePattern,
        Tag.AsyncBasePattern,
    },
    
    TagCategory.BodyThrows: {
        Tag.Backcrosses,
        Tag.Shoulders,
        Tag.Overheads,
        Tag.Necks,
        Tag.UnderLegs,
        Tag.SpecialBodyThrows,
        Tag.Lazies,
        Tag.ReverseShoulders,
    },

    TagCategory.SpinControl: {
        Tag.Flats,
        Tag.SpinControl,
        Tag.FlatFront,
    },
    
    TagCategory.Siteswap: {
        Tag.SyncSiteswap,
        Tag.AsyncSiteswap,
    },
    
    TagCategory.Isolation: {
        Tag.Isolated,
        Tag.OnTheKnees,
        Tag.Sitting,
        Tag.OnTheBack,
    },
    
    TagCategory.OneSidedPassing: {
        Tag.TwoCount,
        Tag.FourCount
    },
    
    TagCategory.TwoSidedPassing: {
        Tag.OneCount,
        Tag.ThreeCount,
        Tag.FourHandedSiteswaps
    }
}

TAG_CATEGORY_MAP_JSON = {tag_category.value: tags for tag_category, tags in TAG_CATEGORY_MAP.items()}