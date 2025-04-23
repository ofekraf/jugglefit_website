from enum import Enum

from .utils.reverse_lookup_enum import ReverseLookupEnum

class Prop(ReverseLookupEnum):
    Balls = "balls"
    Clubs = "clubs"
    Rings = "rings"
    # ClubPassing = "club_passing" # Hopefully one day :)

    def __lt__(self, other):
        """Make Prop sortable by comparing their values."""
        return self.value < other.value

    def __str__(self) -> str:
        """Make the prop JSON serializable by returning its value."""
        return self.value

PROP_OPTIONS = [p.value for p in Prop]