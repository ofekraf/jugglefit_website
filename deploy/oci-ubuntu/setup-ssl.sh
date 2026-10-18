#!/bin/bash
#
# Obtain a Let's Encrypt certificate and switch nginx to HTTPS.
#
#   sudo bash setup-ssl.sh jugglefit.org [www.jugglefit.org ...]
#
# certbot only issues the certificate (`certonly --nginx`). It does not edit
# nginx config: the HTTPS server block comes from nginx/site-https.conf in
# the repo, installed by install-host-config.sh. Renewal is handled by the
# certbot systemd timer, with a hook that reloads nginx.

set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

APP_DIR="${APP_DIR:-/opt/jugglefit}"
ENV_FILE="$APP_DIR/.env"

if [ $# -lt 1 ]; then
    echo -e "${RED}Usage: $0 <domain> [more domains...]${NC}"
    echo "Example: $0 jugglefit.org www.jugglefit.org"
    exit 1
fi
[[ $EUID -eq 0 ]] || { echo -e "${RED}Run as root (sudo)${NC}"; exit 1; }

DOMAINS_CSV="$(IFS=,; echo "$*")"
CERT_NAME="$1"
EMAIL="${CERTBOT_EMAIL:-admin@$1}"

echo -e "${GREEN}Setting up SSL for: $*${NC}"

# 1. Record domains in .env so install-host-config.sh renders them.
touch "$ENV_FILE"
sed -i '/^DOMAINS=/d' "$ENV_FILE"
echo "DOMAINS=$DOMAINS_CSV" >> "$ENV_FILE"

# 2. HTTP site with the right server_name, so the ACME challenge can be served.
bash "$APP_DIR/deploy/oci-ubuntu/install-host-config.sh"

# 3. Certificate only.
D_ARGS=(); for d in "$@"; do D_ARGS+=(-d "$d"); done
certbot certonly --nginx --cert-name "$CERT_NAME" "${D_ARGS[@]}" \
    --non-interactive --agree-tos --email "$EMAIL" --keep-until-expiring

# 4. Now the cert exists -> HTTPS site.
bash "$APP_DIR/deploy/oci-ubuntu/install-host-config.sh"

echo -e "${YELLOW}Certificate:${NC}"
openssl x509 -noout -dates -in "/etc/letsencrypt/live/$CERT_NAME/fullchain.pem"
echo -e "${GREEN}Done. https://$1${NC}"
