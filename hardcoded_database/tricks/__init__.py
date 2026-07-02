# Backward-compat re-export. The registry now lives in
# ``pylib.utils.trick_registry`` and is backed by SQLite (seeded from the
# CSV files in this directory on first run). Existing imports of
# ``hardcoded_database.tricks.ALL_PROPS_TRICKS`` etc. keep working.
from pylib.utils.trick_registry import (  # noqa: F401
    ALL_PROPS_TRICKS,
    ALL_PROPS_SETTINGS,
    ALL_PROPS_SETTINGS_JSON,
    reload_prop,
)
