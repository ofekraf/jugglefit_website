#!/bin/bash
#
# Update the running JuggleFit deployment to the latest code.
#
#   sudo bash /opt/jugglefit/deploy/oci-ubuntu/update.sh
#
# Flow: snapshot DB → git pull → build+recreate → wait for /health.

set -euo pipefail

APP_DIR="${APP_DIR:-/opt/jugglefit}"
COMPOSE_FILE="$APP_DIR/docker-compose.prod.yml"
HEALTH_URL="http://localhost:5001/health"

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
say()  { echo -e "${GREEN}==>${NC} $*"; }
warn() { echo -e "${YELLOW}!${NC} $*"; }
die()  { echo -e "${RED}ERROR:${NC} $*" >&2; exit 1; }

[ "$(id -u)" -eq 0 ] || die "run as root (sudo)"
cd "$APP_DIR" || die "APP_DIR $APP_DIR not found"
[ -f "$COMPOSE_FILE" ] || die "compose file not found: $COMPOSE_FILE"

dc() { docker compose -f "$COMPOSE_FILE" "$@"; }

# 1. Pre-update DB snapshot (rollback point). Non-fatal if container is down.
say "Snapshotting database before update"
dc exec -T web python -m database.backup \
    || warn "snapshot skipped (container not running?)"

# 2. Pull
PREV=$(git rev-parse --short HEAD 2>/dev/null || echo "?")
say "git pull (was $PREV)"
git pull --ff-only origin main
NOW=$(git rev-parse --short HEAD)
[ "$PREV" = "$NOW" ] && warn "no new commits — rebuilding anyway"

# 3. Build + recreate (picks up code AND any .env changes)
say "Building and recreating containers"
dc up -d --build

# 4. Health
say "Waiting for /health"
for i in $(seq 1 30); do
    if curl -fsS "$HEALTH_URL" >/dev/null 2>&1; then
        say "Healthy. Updated $PREV → $NOW"
        # Reclaim old image layers from this build.
        docker image prune -f >/dev/null
        exit 0
    fi
    sleep 2
done

echo
die "Health check failed after 60s. Recent logs:
$(dc logs --tail 60 web 2>&1)

Rollback: git reset --hard $PREV && sudo bash $0"
