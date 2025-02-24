

from ..utils.reverse_lookup_enum import ReverseLookupEnum

class Tag(ReverseLookupEnum):
    s360 = "360"
    s720 = "720"
    Spins = "spins"
    MultiStage = "multistage"
    Siteswap = "siteswap"
    BasePattern = "base pattern"
    BodyThrows = "body throws"
    SpinControl = "spin control"
    
TAG_OPTIONS = [t.value for t in Tag]
    