from enum import Enum

from .utils.reverse_lookup_enum import ReverseLookupEnum

class Prop(ReverseLookupEnum):
    Balls = "balls"
    Clubs = "clubs"
    Rings = "rings"
    # ClubPassing = "club_passing" # Hopefully one day :)

PROP_OPTIONS = [p.value for p in Prop]