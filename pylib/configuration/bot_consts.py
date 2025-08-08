import os
import json5
from pathlib import Path
from google.oauth2 import service_account


JUGGLEFIT_BOT_PRIVATE_KEY_ENV_NAME = 'JUGGLEFIT_BOT_PRIVATE_KEY'
TRICK_SUGGESTIONS_SPREADSHEET_ID_ENV_NAME = 'TRICK_SUGGESTIONS_SPREADSHEET_ID'

# Verify required environment variables
_private_key = os.getenv(JUGGLEFIT_BOT_PRIVATE_KEY_ENV_NAME)
if _private_key is None:
    raise ValueError(f"{JUGGLEFIT_BOT_PRIVATE_KEY_ENV_NAME} environment variable is not set")

_spreadsheet_id = os.getenv(TRICK_SUGGESTIONS_SPREADSHEET_ID_ENV_NAME)
if _spreadsheet_id is None:
    raise ValueError(f"{TRICK_SUGGESTIONS_SPREADSHEET_ID_ENV_NAME} environment variable is not set")

# Bot configuration
PYLIB_ROOT = Path(__file__).parent.parent
JUGGLEFIT_BOT_SERVICE_ACCOUNT_FILE = PYLIB_ROOT / "configuration" / "JuggleFitBot_credentials.json5"
JUGGLEFIT_BOT_SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
TRICK_SUGGESTIONS_SPREADSHEET_ID = _spreadsheet_id

# Load and process credentials file
_creds_content = JUGGLEFIT_BOT_SERVICE_ACCOUNT_FILE.read_text()
_creds_content = os.path.expandvars(_creds_content)
JUGGLEFIT_BOT_CREDS_INFO = json5.loads(_creds_content)

# # Create credentials object
# JUGGLEFIT_BOT_CREDS = service_account.Credentials.from_service_account_info(
#     JUGGLEFIT_BOT_CREDS_INFO,
#     scopes=JUGGLEFIT_BOT_SCOPES
# )