from pylib.classes.trick import Trick
from pylib.classes.tag import Tag
from pylib.utils.trick_loader import load_tricks_from_csv

CLUBS_TRICKS = load_tricks_from_csv(__file__.replace('.py', '.csv'))
