#!/bin/bash

# SSL Setup Script for JuggleFit Website
# Usage: ./setup-ssl.sh yourdomain.com

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if domain is provided
if [ -z "$1" ]; then
    echo -e "${RED}Usage: $0 <domain>${NC}"
    echo "Example: $0 jugglefit.com"
    exit 1
fi

DOMAIN="$1"
NGINX_CONFIG="/etc/nginx/sites-available/jugglefit"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}This script must be run as root (use sudo)${NC}"
   exit 1
fi

echo -e "${GREEN}Setting up SSL for domain: $DOMAIN${NC}"

# Update Nginx configuration with actual domain
echo -e "${YELLOW}Updating Nginx configuration...${NC}"
sed -i "s/server_name _;/server_name $DOMAIN;/g" $NGINX_CONFIG
sed -i "s/DOMAIN/$DOMAIN/g" $NGINX_CONFIG

# Test Nginx configuration
nginx -t

# Reload Nginx
systemctl reload nginx

# Obtain SSL certificate
echo -e "${YELLOW}Obtaining SSL certificate...${NC}"
certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN

# Set up automatic renewal
echo -e "${YELLOW}Setting up automatic certificate renewal...${NC}"
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -

# Test SSL configuration
echo -e "${YELLOW}Testing SSL configuration...${NC}"
nginx -t
systemctl reload nginx

# Verify SSL certificate
echo -e "${YELLOW}Verifying SSL certificate...${NC}"
openssl s_client -connect $DOMAIN:443 -servername $DOMAIN < /dev/null 2>/dev/null | openssl x509 -noout -dates

echo -e "${GREEN}SSL setup completed successfully!${NC}"
echo -e "${YELLOW}Your site is now available at:${NC}"
echo "HTTP:  http://$DOMAIN"
echo "HTTPS: https://$DOMAIN"
echo ""
echo -e "${YELLOW}SSL certificate will auto-renew via cron job.${NC}"