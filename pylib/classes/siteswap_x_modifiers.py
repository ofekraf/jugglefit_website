from pylib.utils.reverse_lookup_enum import ReverseLookupEnum


class ThrowModifier(ReverseLookupEnum):
    BACKCROSS = "B"
    UNDER_THE_LEG = "Ul"
    SHOULDER = "S"
    NECK = "N"
    OVERHEAD = "Oh"
    FLATFRONT = "F"
    PANCAKE = "Pc"


class CatchModifier(ReverseLookupEnum):
    PENGUIN = "Pe"
    LAZY = "L"
    REVERSE_BACKCROSS = "Rb"
    REVERSE_SHOULDER = "Rs"
    UNDER_THE_LEG = "Ul"