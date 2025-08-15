from pathlib import Path

from pylib.classes.prop import Prop

HARDCODED_DATABASE_ROOT = Path(__file__).parent
HARDCODED_TRICKS_ROOT = HARDCODED_DATABASE_ROOT / 'tricks'

def get_trick_csv_path(prop: Prop) -> Path:
    return HARDCODED_TRICKS_ROOT / f'{prop.value}.csv'