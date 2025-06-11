import threading
from git import Repo
from pathlib import Path
import os


# Global mutex for git operations
git_mutex = threading.Lock()

# Global git repository instance
jugglefit_bot_repo = Repo(Path(os.getenv('GIT_REPO_PATH', str(Path(__file__).parent.parent))))

# Configure git user
with jugglefit_bot_repo.config_writer() as config:
    config.set_value("user", "name", os.getenv('GIT_USER_NAME', 'JuggleFit Bot'))
    config.set_value("user", "email", os.getenv('GIT_USER_EMAIL', 'bot@jugglefit.com'))

# Git configuration constants
GIT_REMOTE_NAME = os.getenv('GIT_REMOTE_NAME', 'origin')
GIT_MAIN_BRANCH = os.getenv('GIT_MAIN_BRANCH', 'main')
