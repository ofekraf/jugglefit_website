from hardcoded_database.consts import get_trick_csv_path
from pylib.classes.prop import Prop
from pylib.utils.trick_loader import load_tricks_from_csv


PROP_TO_TRICKS = {prop: load_tricks_from_csv(get_trick_csv_path(prop)) for prop in Prop}
