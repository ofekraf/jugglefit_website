from pylib.utils.reverse_lookup_enum import ReverseLookupEnum


class ThrowModifier(ReverseLookupEnum):
    BACKCROSS = "B"
    SHOULDER = "S"
    OUTSIDE = "Ou"
    INSIDE = "In"
    UNDER_THE_LEG = "Ul"
    NECK = "N"
    INVERTED = "I"
    OVERHEAD = "Oh"
    FLATFRONT = "F"
    PANCAKE = "Pc"


class CatchModifier(ReverseLookupEnum):
    PENGUIN = "Pe"
    REVERSE_BACKCROSS = "Rb"
    REVERSE_SHOULDER = "Rs"
    LAZY = "L"
    UNDER_THE_LEG = "Ul"