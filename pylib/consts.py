from pathlib import Path
from google.oauth2 import service_account

PYLIB_ROOT = Path(__file__).parent

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


TRICK_SUGGESTIONS_SPREADSHEET_ID = '1cQtg5wUoy_BaAEC2Nn2i1qbAChZ_kXbCpEUi2vLMo1c'

# Don't yet worry about permissions and secrets stuff, currently it has only access to the trick_suggestions sheet
JUGGLEFIT_BOT_SERVICE_ACCOUNT_FILE = PYLIB_ROOT / "utils" / "JuggleFitBot_credentials.json"

# If modifying these scopes, consider the principle of least privilege.
# 'https://www.googleapis.com/auth/spreadsheets' gives full read/write access to spreadsheets.
# You could use 'https://www.googleapis.com/auth/spreadsheets.readonly' for read-only.
JUGGLEFIT_BOT_SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
JUGGLEFIT_BOT_CREDS = service_account.Credentials.from_service_account_file(
        JUGGLEFIT_BOT_SERVICE_ACCOUNT_FILE, scopes=JUGGLEFIT_BOT_SCOPES)
