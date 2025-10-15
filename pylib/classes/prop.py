from pylib.utils.reverse_lookup_enum import ReverseLookupEnum

class Prop(ReverseLookupEnum):
    Balls = "balls"
    Clubs = "clubs"
    Rings = "rings"
    ClubPassing = "club passing"

    def __lt__(self, other):
        """Make Prop sortable by comparing their values."""
        return self.value < other.value

    def __str__(self) -> str:
        """Make the prop JSON serializable by returning its value."""
        return self.value

MAIN_PROPS = {Prop.Balls, Prop.Clubs, Prop.Rings}