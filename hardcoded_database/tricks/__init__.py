from hardcoded_database.tricks.balls import BALLS_TRICKS
from hardcoded_database.tricks.clubs import CLUBS_TRICKS
from hardcoded_database.tricks.rings import RINGS_TRICKS
from py_lib.prop import Prop


PROP_TO_TRICKS = {
    Prop.Balls: BALLS_TRICKS, 
    Prop.Clubs: CLUBS_TRICKS,
    Prop.Rings: RINGS_TRICKS,
}
