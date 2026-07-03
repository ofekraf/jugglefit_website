#!/bin/bash
#
# One-time host setup for the JuggleFit OCI VM.
# Idempotent: safe to re-run.
#
#   sudo bash /opt/jugglefit/deploy/oci-ubuntu/setup.sh
#
# What it does:
#   1. Ensures required .env keys exist (prompts for SUPER_ADMIN_* if missing)
#   2. Installs rclone (for off-box backup) if not present
#   3. Walks you through `rclone config` if no remote is set up yet
#   4. Installs cron jobs:
#        03:00 daily  → backup.sh  (snapshot → rclone → DB prune)
#        04:00 1st/mo → docker system prune -af  (reclaim image layers)
#   5. Locks down .env permissions

set -euo pipefail

APP_DIR="${APP_DIR:-/opt/jugglefit}"
ENV_FILE="$APP_DIR/.env"
BACKUP_SH="$APP_DIR/deploy/oci-ubuntu/backup.sh"
CRON_TAG="# jugglefit"
# Log under /var/log/jugglefit/ so the logrotate rule installed by
# deploy.sh (glob: /var/log/jugglefit/*.log) rotates these files.
LOG_DIR="/var/log/jugglefit"

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
say()  { echo -e "${GREEN}==>${NC} $*"; }
warn() { echo -e "${YELLOW}!${NC} $*"; }
die()  { echo -e "${RED}ERROR:${NC} $*" >&2; exit 1; }

[ "$(id -u)" -eq 0 ] || die "run as root (sudo)"
[ -d "$APP_DIR" ]    || die "APP_DIR $APP_DIR not found"
[ -f "$BACKUP_SH" ]  || die "backup.sh not found at $BACKUP_SH"

# ---------------------------------------------------------------------------
# 1. .env
# ---------------------------------------------------------------------------
say "Checking $ENV_FILE"
touch "$ENV_FILE"

ensure_env() {
    local key="$1" prompt="$2" default="${3:-}" silent="${4:-}"
    if grep -q "^${key}=" "$ENV_FILE"; then
        echo "  $key already set"
        return
    fi
    local val
    if [ -n "$silent" ]; then
        read -r -s -p "  $prompt: " val; echo
    else
        read -r -p "  $prompt${default:+ [$default]}: " val
    fi
    val="${val:-$default}"
    [ -n "$val" ] || die "$key is required"
    echo "${key}=${val}" >> "$ENV_FILE"
    echo "  $key written"
}

ensure_env SECRET_KEY            "Flask SECRET_KEY (random string)" "$(head -c32 /dev/urandom | base64 | tr -d '=+/')"
ensure_env SUPER_ADMIN_USER      "Super-admin username" "Admin"
ensure_env SUPER_ADMIN_PASSWORD  "Super-admin password" "" silent

chmod 600 "$ENV_FILE"
say ".env locked to 600"

# ---------------------------------------------------------------------------
# 2. rclone
# ---------------------------------------------------------------------------
if ! command -v rclone >/dev/null 2>&1; then
    say "Installing rclone"
    if command -v apt-get >/dev/null 2>&1; then
        apt-get update -qq && apt-get install -y rclone
    else
        curl -fsSL https://rclone.org/install.sh | bash
    fi
else
    say "rclone already installed ($(rclone version | head -1))"
fi

# ---------------------------------------------------------------------------
# 3. rclone remote + RCLONE_REMOTE in .env
# ---------------------------------------------------------------------------
if ! grep -q "^RCLONE_REMOTE=" "$ENV_FILE"; then
    warn "RCLONE_REMOTE not set — off-box backup will be skipped until configured."
    if rclone listremotes 2>/dev/null | grep -q .; then
        echo "  Existing rclone remotes:"
        rclone listremotes | sed 's/^/    /'
    else
        echo "  No rclone remotes configured yet."
        read -r -p "  Run 'rclone config' now to create one? [y/N] " ans
        if [[ "$ans" =~ ^[Yy]$ ]]; then
            rclone config
        fi
    fi
    if rclone listremotes 2>/dev/null | grep -q .; then
        first_remote="$(rclone listremotes | head -1 | tr -d ':')"
        read -r -p "  RCLONE_REMOTE (e.g. ${first_remote}:jugglefit-backups): " rr
        if [ -n "$rr" ]; then
            echo "RCLONE_REMOTE=${rr}" >> "$ENV_FILE"
            say "RCLONE_REMOTE written"
        else
            warn "Skipped — set RCLONE_REMOTE in $ENV_FILE later."
        fi
    fi
else
    say "RCLONE_REMOTE already set: $(grep '^RCLONE_REMOTE=' "$ENV_FILE" | cut -d= -f2-)"
fi

# ---------------------------------------------------------------------------
# 4. cron (idempotent — strip our tagged lines, re-add)
# ---------------------------------------------------------------------------
say "Installing cron jobs"
mkdir -p "$LOG_DIR"
CRON_LINES=$(cat <<EOF
0 3 * * * $BACKUP_SH >> $LOG_DIR/backup.log 2>&1 $CRON_TAG
0 4 1 * * docker system prune -af >> $LOG_DIR/docker-prune.log 2>&1 $CRON_TAG
EOF
)
# `|| true`: with set -euo pipefail, an empty/no crontab makes both
# `crontab -l` and `grep -v` exit 1, which would abort the subshell
# before echo runs and leave root with an empty crontab.
( crontab -l 2>/dev/null | grep -v "$CRON_TAG" || true ; echo "$CRON_LINES" ) | crontab -
say "Cron installed:"
crontab -l | grep "$CRON_TAG" | sed 's/^/  /'

# ---------------------------------------------------------------------------
# 5. summary
# ---------------------------------------------------------------------------
echo
say "Setup complete."
echo "  .env:        $ENV_FILE (chmod 600)"
echo "  Daily 03:00: $BACKUP_SH  → snapshot, rclone upload, DB prune"
echo "  Monthly:     docker system prune -af"
echo
echo "  Next: docker compose -f $APP_DIR/docker-compose.prod.yml up -d --build"
if ! grep -q "^RCLONE_REMOTE=" "$ENV_FILE"; then
    warn "Reminder: off-box backup is OFF until RCLONE_REMOTE is set."
fi
