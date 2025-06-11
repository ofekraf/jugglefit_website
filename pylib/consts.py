# UI Constraints
from pathlib import Path
import os

from pylib.classes.prop import Prop


MAX_TRICK_NAME_LENGTH = 100

# Props Count Constraints
MIN_TRICK_PROPS_COUNT = 1
MAX_TRICK_PROPS_COUNT = 9
DEFAULT_MIN_TRICK_PROPS_COUNT = 3
DEFAULT_MAX_TRICK_PROPS_COUNT = 9

# Difficulty Constraints
MIN_TRICK_DIFFICULTY = 0
MAX_TRICK_DIFFICULTY = 100
DEFAULT_MIN_TRICK_DIFFICULTY = 20
DEFAULT_MAX_TRICK_DIFFICULTY = 30 


PYLIB_ROOT = Path(__file__).parent
DATABASE_ROOT = PYLIB_ROOT.parent / 'database'
TRICK_SUGGESTIONS_FOLDER = DATABASE_ROOT / "tricks" / "suggestions"
TRICK_SUGGESTIONS_PROP_FILE_MAP = {
    Prop.Balls: 'balls.txt',
    Prop.Clubs: 'clubs.txt',
    Prop.Rings: 'rings.txt'
}

TRICK_SUGGESTIONS_BRANCH_NAME = f"bot/trick_suggestions"

# Git Configuration
GIT_REPO_PATH = os.getenv('GIT_REPO_PATH', str(PYLIB_ROOT.parent))
GIT_USER_NAME = os.getenv('GIT_USER_NAME', 'JuggleFit Bot')
GIT_USER_EMAIL = os.getenv('GIT_USER_EMAIL', 'bot@jugglefit.com')
GIT_REMOTE_NAME = os.getenv('GIT_REMOTE_NAME', 'origin')
GIT_MAIN_BRANCH = os.getenv('GIT_MAIN_BRANCH', 'main')
