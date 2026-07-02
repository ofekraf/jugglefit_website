from pathlib import Path

PYLIB_ROOT = Path(__file__).parent.parent

MAX_TRICK_NAME_LENGTH = 100
MAX_SITESWAP_X_LENGTH = 200
MAX_COMMENT_LENGTH = 500

# Difficulty Constraints
MIN_TRICK_DIFFICULTY = 0
MAX_TRICK_DIFFICULTY = 100
DEFAULT_MIN_TRICK_DIFFICULTY = 20
DEFAULT_MAX_TRICK_DIFFICULTY = 30

# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
USERNAME_RE = r"[A-Za-z0-9_ ]{3,24}"
PASSWORD_MIN_LENGTH = 6
PASSWORD_MAX_LENGTH = 128
ADMIN_SESSION_SECONDS = 60 * 60  # legacy env-password admin gate lifetime
USER_SESSION_DAYS = 30
ANON_VOTE_WEIGHT = 0.3

# ---------------------------------------------------------------------------
# Crowd rating
# ---------------------------------------------------------------------------
RATING_SET_SIZE = 8
RATING_CONTROL_FRACTION = 0.375
CONTROL_MIN_GAP = 15
CANDIDATE_INIT_SIGMA = 25.0
SIGMA_DECAY = 0.97
ELO_SCALE = 30.0
TAG_UNLOCK_SIGMA = 8.0
TAG_VOTE_THRESHOLD = 0.30
MIN_TAG_VOTES = 5
MIN_THROW_VOTES = 5

# Promotion gates
PROMOTE_MIN_COMPARISONS = 20
PROMOTE_MAX_SIGMA = 6.0
PROMOTE_MAX_UNKNOWN_RATIO = 0.4
PROMOTE_MIN_AGE_HOURS = 48

# Flags (logged-in only)
FLAG_REASONS = ["not_a_trick", "duplicate", "offensive", "wrong_prop"]
FLAG_REMOVE_MIN = 3
FLAG_REMOVE_RATIO = 0.25

# Auto-unstable: a candidate that accumulates this many compare exposures
# while remaining mostly unrecognised is queued for deletion automatically.
UNSTABLE_MIN_EXPOSURES = 30
UNSTABLE_UNKNOWN_RATIO = 0.6  # (n_cant_judge + n_flags) / exposures

# Need-score weights for the games hub
W_HARDER = 1.0
W_TAG = 1.5
W_THROW = 1.2

# Leaderboard
LEADERBOARD_TOP_N = 20
LEADERBOARD_PERIODS = {"all": None, "30d": 30}

# ---------------------------------------------------------------------------
# Storage retention (single-VM disk budget)
# ---------------------------------------------------------------------------
# Raw vote rows for *settled* candidates (promoted or removed) are pruned
# after this many days. Must stay >= the largest non-"all" leaderboard
# period so periodic boards remain exact. The "all" board reads the
# denormalized users.n_* counters and is unaffected by pruning.
RAW_VOTE_RETENTION_DAYS = 45
PENDING_RETENTION_DAYS = 14
PRUNE_BATCH_SIZE = 5000  # rows per DELETE to avoid long write locks

# Highest-throw stepper bounds
THROW_STEPPER_MIN = 3
THROW_STEPPER_MAX = 15

# Which TagCategories make sense per prop. Passing categories only for
# club passing; spin/spin-control only for clubs/rings (not balls).
# Import is local to avoid a cycle through pylib.classes at consts-import time.
def _build_prop_relevant_categories():
    from pylib.classes.prop import Prop
    from pylib.classes.tag import TagCategory as TC
    solo_common = [TC.BasePattern, TC.BodyThrows, TC.Siteswap, TC.Isolation, TC.Spin]
    return {
        Prop.Balls:       [TC.BasePattern, TC.BodyThrows, TC.Siteswap, TC.Isolation, TC.Spin],
        Prop.Clubs:       solo_common + [TC.SpinControl],
        Prop.Rings:       solo_common + [TC.SpinControl],
        Prop.ClubPassing: [TC.OneSidedPassing, TC.TwoSidedPassing, TC.BodyThrows,
                           TC.SpinControl, TC.Siteswap],
        Prop.Balance: [TC.Isolation, TC.BodyThrows],
    }

PROP_RELEVANT_CATEGORIES = _build_prop_relevant_categories()
