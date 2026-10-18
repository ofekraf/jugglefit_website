#!/bin/bash
#
# Install host-level config (nginx + systemd) from the repo onto the VM.
# Idempotent; called by update.sh, deploy.sh and setup-ssl.sh.
#
#   sudo bash /opt/jugglefit/deploy/oci-ubuntu/install-host-config.sh
#
# The repo is the source of truth. Do not edit these on the host:
#   /etc/nginx/conf.d/jugglefit.conf          <- nginx/http.conf
#   /etc/nginx/snippets/jugglefit-app.conf    <- nginx/app.conf
#   /etc/nginx/sites-available/jugglefit      <- nginx/site-http.conf or site-https.conf
#   /etc/systemd/system/jugglefit.service     <- jugglefit.service
#
# Settings come from $APP_DIR/.env:
#   DOMAINS=jugglefit.org,www.jugglefit.org   (first one = certificate name)
#   CERT_NAME=...                             (optional, if certbot's cert dir differs)
#
# If `nginx -t` fails, the previous nginx files are restored.

set -euo pipefail

APP_DIR="${APP_DIR:-/opt/jugglefit}"
SRC="$APP_DIR/deploy/oci-ubuntu"
ENV_FILE="$APP_DIR/.env"

NGINX_HTTP_CONF=/etc/nginx/conf.d/jugglefit.conf
NGINX_SNIPPET=/etc/nginx/snippets/jugglefit-app.conf
NGINX_SITE=/etc/nginx/sites-available/jugglefit
NGINX_SITE_LINK=/etc/nginx/sites-enabled/jugglefit
SERVICE_FILE=/etc/systemd/system/jugglefit.service

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
say()  { echo -e "${GREEN}==>${NC} $*"; }
warn() { echo -e "${YELLOW}!${NC} $*"; }
die()  { echo -e "${RED}ERROR:${NC} $*" >&2; exit 1; }

[ "$(id -u)" -eq 0 ] || die "run as root (sudo)"
[ -d "$SRC/nginx" ]  || die "nginx templates not found in $SRC/nginx"

env_get() {
    [ -f "$ENV_FILE" ] || return 0
    grep -E "^$1=" "$ENV_FILE" | tail -1 | cut -d= -f2- | tr -d '"'"'"'\r' || true
}

DOMAINS="$(env_get DOMAINS)"
CERT_NAME="$(env_get CERT_NAME)"
if [ -n "$DOMAINS" ]; then
    SERVER_NAME="$(echo "$DOMAINS" | tr ',' ' ' | xargs)"
    CERT_NAME="${CERT_NAME:-${SERVER_NAME%% *}}"
else
    # Safety: a host with certificates but no DOMAINS would silently drop
    # to HTTP-only. Refuse instead.
    if ls /etc/letsencrypt/live/*/fullchain.pem >/dev/null 2>&1; then
        die "TLS certificates exist but DOMAINS is not set in $ENV_FILE.
  Add e.g.:  DOMAINS=jugglefit.org,www.jugglefit.org
  (certs found: $(ls /etc/letsencrypt/live | grep -v README | xargs))"
    fi
    SERVER_NAME="_"
fi

if [ -n "$CERT_NAME" ] && [ -f "/etc/letsencrypt/live/$CERT_NAME/fullchain.pem" ]; then
    SITE_TEMPLATE="$SRC/nginx/site-https.conf"
    MODE="HTTPS (cert: $CERT_NAME)"
else
    SITE_TEMPLATE="$SRC/nginx/site-http.conf"
    MODE="HTTP only"
    [ -n "$DOMAINS" ] && warn "No certificate for '$CERT_NAME' yet; run setup-ssl.sh to enable HTTPS."
fi

# ---------------------------------------------------------------------------
# nginx
# ---------------------------------------------------------------------------
if command -v nginx >/dev/null 2>&1; then
    say "Installing nginx config: $MODE, server_name $SERVER_NAME"
    BACKUP_DIR="$(mktemp -d)"
    trap 'rm -rf "$BACKUP_DIR"' EXIT
    for f in "$NGINX_HTTP_CONF" "$NGINX_SNIPPET" "$NGINX_SITE"; do
        [ -f "$f" ] && cp -a "$f" "$BACKUP_DIR/$(basename "$f").bak"
    done

    # nginx (www-data) serves /static straight from the checkout.
    chmod o+x "$APP_DIR"
    chmod -R a+rX "$APP_DIR/static"

    mkdir -p /etc/nginx/conf.d /etc/nginx/snippets /var/cache/nginx
    install -m 644 "$SRC/nginx/http.conf" "$NGINX_HTTP_CONF"
    install -m 644 "$SRC/nginx/app.conf"  "$NGINX_SNIPPET"
    sed -e "s|__SERVER_NAME__|$SERVER_NAME|g" -e "s|__CERT_NAME__|$CERT_NAME|g" \
        "$SITE_TEMPLATE" > "$NGINX_SITE"
    chmod 644 "$NGINX_SITE"
    ln -sf "$NGINX_SITE" "$NGINX_SITE_LINK"
    rm -f /etc/nginx/sites-enabled/default

    if nginx -t 2>/tmp/jugglefit-nginx-test.log; then
        systemctl reload nginx 2>/dev/null || systemctl restart nginx
        say "nginx reloaded"
    else
        cat /tmp/jugglefit-nginx-test.log >&2
        warn "nginx -t failed; restoring previous config"
        for f in "$NGINX_HTTP_CONF" "$NGINX_SNIPPET" "$NGINX_SITE"; do
            b="$BACKUP_DIR/$(basename "$f").bak"
            if [ -f "$b" ]; then cp -a "$b" "$f"; else rm -f "$f"; fi
        done
        nginx -t && systemctl reload nginx
        die "new nginx config rejected (previous config restored)"
    fi
else
    warn "nginx not installed; skipping nginx config"
fi

# ---------------------------------------------------------------------------
# systemd
# ---------------------------------------------------------------------------
if ! cmp -s "$SRC/jugglefit.service" "$SERVICE_FILE" 2>/dev/null; then
    say "Installing systemd unit"
    install -m 644 "$SRC/jugglefit.service" "$SERVICE_FILE"
    systemctl daemon-reload
    systemctl enable jugglefit >/dev/null 2>&1 || true
    systemctl reset-failed jugglefit 2>/dev/null || true
    # One-time restart so systemd tracks the new unit (and any restart loop
    # from an older unit stops). `up -d` brings the containers straight back.
    say "Restarting jugglefit service (unit changed; a few seconds of downtime)"
    systemctl restart jugglefit
else
    say "systemd unit unchanged"
fi

# ---------------------------------------------------------------------------
# certbot: reload nginx after renewals, drop the redundant cron entry
# (Ubuntu's certbot package already ships a systemd timer)
# ---------------------------------------------------------------------------
if [ -d /etc/letsencrypt ]; then
    mkdir -p /etc/letsencrypt/renewal-hooks/deploy
    cat > /etc/letsencrypt/renewal-hooks/deploy/jugglefit-reload-nginx.sh <<'EOF'
#!/bin/sh
systemctl reload nginx
EOF
    chmod 755 /etc/letsencrypt/renewal-hooks/deploy/jugglefit-reload-nginx.sh
fi
if crontab -l 2>/dev/null | grep -q "certbot renew"; then
    ( crontab -l 2>/dev/null | grep -v "certbot renew" || true ) | crontab -
    say "Removed duplicate certbot cron entry (systemd timer handles renewal)"
fi

say "Host config installed"
