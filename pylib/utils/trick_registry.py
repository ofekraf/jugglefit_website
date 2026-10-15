"""
In-memory cache of master tricks + derived per-prop settings.

Tricks are hardcoded in ``hardcoded_database/tricks/<prop>.csv`` and loaded
once at import time. The dictionaries here are the *same objects*
re-exported by ``hardcoded_database.tricks`` for backward compatibility.
"""
from __future__ import annotations

from typing import Dict, List

from hardcoded_database.consts import get_trick_csv_path
from pylib.classes.prop import Prop
from pylib.classes.prop_settings import PropSettings
from pylib.classes.trick import Trick
from pylib.utils.trick_loader import load_tricks_from_csv


def _load_prop_tricks(prop: Prop) -> List[Trick]:
    csv_path = get_trick_csv_path(prop)
    if not csv_path.exists():
        return []
    tricks = load_tricks_from_csv(csv_path)
    return sorted(tricks, key=lambda t: (t.props_count, t.difficulty))


ALL_PROPS_TRICKS: Dict[Prop, List[Trick]] = {
    prop: _load_prop_tricks(prop) for prop in Prop
}
ALL_PROPS_SETTINGS: Dict[Prop, PropSettings] = {
    prop: PropSettings.from_tricks(tricks) for prop, tricks in ALL_PROPS_TRICKS.items()
}
ALL_PROPS_SETTINGS_JSON: Dict[str, dict] = {
    prop.value: settings.to_dict() for prop, settings in ALL_PROPS_SETTINGS.items()
}
