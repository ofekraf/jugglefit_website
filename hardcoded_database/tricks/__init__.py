from hardcoded_database.consts import get_trick_csv_path
from pylib.classes.prop import Prop
from pylib.classes.prop_settings import PropSettings
from pylib.utils.trick_loader import load_tricks_from_csv


ALL_PROPS_TRICKS = {prop: load_tricks_from_csv(get_trick_csv_path(prop)) for prop in Prop}
ALL_PROPS_SETTINGS = {prop: PropSettings.from_tricks(tricks) for prop, tricks in ALL_PROPS_TRICKS.items()}
ALL_PROPS_SETTINGS_JSON = {prop.value: prop_settings.to_dict() for prop, prop_settings in ALL_PROPS_SETTINGS.items()}
