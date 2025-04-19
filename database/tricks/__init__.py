from database.tricks.balls import BALLS_TRICKS
from database.tricks.clubs import CLUBS_TRICKS
from database.tricks.rings import RINGS_TRICKS
from route_generator.prop import Prop


PROP_TO_TRICKS = {
    Prop.Balls: BALLS_TRICKS, 
    Prop.Clubs: CLUBS_TRICKS,
    Prop.Rings: RINGS_TRICKS,
}
