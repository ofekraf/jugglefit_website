#!/bin/bash
#
# JuggleFit backup: snapshot SQLite (1 local copy) → push to rclone remote
# (long-term retention lives there) → prune live DB.
#
# Retention model:
#   LOCAL : keep BACKUP_KEEP_LOCAL (default 1) — just the upload source.
#   REMOTE: keep BACKUP_REMOTE_KEEP_DAILY newest + one-per-week for
#           BACKUP_REMOTE_KEEP_WEEKLY weeks (defaults 14 / 8).

set -e

APP_DIR="/opt/jugglefit"
COMPOSE="$APP_DIR/docker-compose.prod.yml"
# Resolve the web container id from compose so we don't depend on the
# project-name prefix (varies with APP_DIR / -p).
CONTAINER="$(docker compose -f "$COMPOSE" ps -q web)"
[ -n "$CONTAINER" ] || { echo "ERROR: web container not running"; exit 1; }

[ -f "$APP_DIR/.env" ] && set -a && . "$APP_DIR/.env" && set +a

: "${BACKUP_REMOTE_KEEP_DAILY:=14}"
: "${BACKUP_REMOTE_KEEP_WEEKLY:=8}"

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
echo -e "${GREEN}Starting JuggleFit backup...${NC}"

# 1. Online-safe SQLite snapshot inside the container. Prints the path of
#    the new .db on stdout (last line).
echo -e "${YELLOW}Snapshotting SQLite database...${NC}"
SNAP_PATH=$(docker compose -f "$COMPOSE" exec -T web python -m database.backup \
    | tail -n1 | sed 's/^Backup written to //') \
    || { echo -e "${RED}ERROR: SQLite snapshot failed${NC}"; exit 1; }
[ -n "$SNAP_PATH" ] || { echo -e "${RED}ERROR: snapshot path empty${NC}"; exit 1; }
SNAP_NAME=$(basename "$SNAP_PATH")

# 2. Copy that one file to the host.
HOST_SNAP="/tmp/$SNAP_NAME"
docker cp "$CONTAINER:$SNAP_PATH" "$HOST_SNAP" \
    || { echo -e "${RED}ERROR: docker cp failed${NC}"; exit 1; }
echo "Local snapshot: $HOST_SNAP ($(du -h "$HOST_SNAP" | cut -f1))"

# 3. Off-box: push to remote (copy, NOT sync — remote accumulates) then
#    prune the remote according to daily/weekly retention.
if [ -n "${RCLONE_REMOTE:-}" ] && command -v rclone >/dev/null 2>&1; then
    echo -e "${YELLOW}Uploading to ${RCLONE_REMOTE}...${NC}"
    if rclone copy "$HOST_SNAP" "${RCLONE_REMOTE}/"; then
        echo -e "${GREEN}Upload complete.${NC}"
        # Remote retention: keep newest N + one-per-week for M weeks.
        echo -e "${YELLOW}Pruning remote (keep ${BACKUP_REMOTE_KEEP_DAILY} daily + ${BACKUP_REMOTE_KEEP_WEEKLY} weekly)...${NC}"
        prune_remote() {
            local listing keep_set weeks_seen=""
            listing=$(rclone lsf "${RCLONE_REMOTE}/" --include "jugglefit_*.db" | sort -r)
            local i=0
            while IFS= read -r f; do
                [ -z "$f" ] && continue
                i=$((i+1))
                if [ "$i" -le "$BACKUP_REMOTE_KEEP_DAILY" ]; then
                    keep_set="$keep_set $f"; continue
                fi
                # parse YYYYMMDD from jugglefit_YYYYMMDD_HHMMSS.db → ISO week
                local d="${f#jugglefit_}"; d="${d:0:8}"
                local wk
                wk=$(date -d "${d:0:4}-${d:4:2}-${d:6:2}" +%G-W%V 2>/dev/null) || { keep_set="$keep_set $f"; continue; }
                case " $weeks_seen " in *" $wk "*) ;; *)
                    if [ "$(echo "$weeks_seen" | wc -w)" -lt "$BACKUP_REMOTE_KEEP_WEEKLY" ]; then
                        weeks_seen="$weeks_seen $wk"; keep_set="$keep_set $f"; continue
                    fi;;
                esac
                rclone deletefile "${RCLONE_REMOTE}/$f" && echo "  removed remote $f"
            done <<< "$listing"
        }
        prune_remote
    else
        echo -e "${RED}WARN: rclone upload failed — local snapshot kept at $HOST_SNAP${NC}"
    fi
elif [ -n "${RCLONE_REMOTE:-}" ]; then
    echo -e "${RED}WARN: RCLONE_REMOTE set but rclone not installed${NC}"
else
    echo "RCLONE_REMOTE not set — skipping off-box upload."
fi

# 4. Host cleanup: remove the temp copy (container keeps its 1 local).
rm -f "$HOST_SNAP"

# 5. Reclaim disk in the live DB. Runs *after* upload so today's snapshot
#    still contains anything about to be pruned.
echo -e "${YELLOW}Pruning raw vote rows + VACUUM...${NC}"
docker compose -f "$COMPOSE" exec -T web python -m database.prune \
    || echo "WARN: prune failed"

echo -e "${GREEN}Backup complete.${NC}"
