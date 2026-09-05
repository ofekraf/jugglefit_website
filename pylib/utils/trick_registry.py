"""
In-memory cache of master tricks + derived per-prop settings.

The dictionaries here are the *same objects* re-exported by
``hardcoded_database.tricks`` for backward compatibility, so existing
imports keep working.
"""
from __future__ import annotations

from typing import Dict, List

from pylib.classes.prop import Prop
from pylib.classes.prop_settings import PropSettings
from pylib.classes.trick import Trick
from pylib.utils.trick_loader import load_tricks_from_db
from database.seed import seed_tricks_from_csv

# Ensure the SQLite ``tricks`` table is populated before first read.
# No-op after the first successful run.
seed_tricks_from_csv()

ALL_PROPS_TRICKS: Dict[Prop, List[Trick]] = {
    prop: load_tricks_from_db(prop.value) for prop in Prop
}
ALL_PROPS_SETTINGS: Dict[Prop, PropSettings] = {
    prop: PropSettings.from_tricks(tricks) for prop, tricks in ALL_PROPS_TRICKS.items()
}
ALL_PROPS_SETTINGS_JSON: Dict[str, dict] = {
    prop.value: settings.to_dict() for prop, settings in ALL_PROPS_SETTINGS.items()
}
