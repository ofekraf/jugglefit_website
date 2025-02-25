

from ..utils.reverse_lookup_enum import ReverseLookupEnum

class Tag(ReverseLookupEnum):
    Spin = "spin"
    MultiSpin = "multi spin"
    Siteswap = "siteswap"
    BasePattern = "base pattern"
    BodyThrows = "body throws"
    SpinControl = "spin control"
    
TAG_OPTIONS = [t.value for t in Tag]
    