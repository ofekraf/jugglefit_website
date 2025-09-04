#!/bin/bash

# JuggleFit Website - OCI Ubuntu Deployment Script
# This script sets up the JuggleFit website on an OCI Ubuntu instance

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="jugglefit"
APP_USER="jugglefit"
APP_DIR="/opt/jugglefit"
NGINX_AVAILABLE="/etc/nginx/sites-available"
NGINX_ENABLED="/etc/nginx/sites-enabled"
SERVICE_FILE="/etc/systemd/system/jugglefit.service"

echo -e "${GREEN}Starting JuggleFit deployment on OCI Ubuntu...${NC}"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}This script must be run as root (use sudo)${NC}"
   exit 1
fi

# Update system packages
echo -e "${YELLOW}Updating system packages...${NC}"
apt update && apt upgrade -y

# Install required packages
echo -e "${YELLOW}Installing required packages...${NC}"
apt install -y \
    docker.io \
    docker-compose \
    nginx \
    ufw \
    curl \
    wget \
    git \
    certbot \
    python3-certbot-nginx

# Start and enable Docker
echo -e "${YELLOW}Starting Docker service...${NC}"
systemctl start docker
systemctl enable docker

# Create application user
if ! id "$APP_USER" &>/dev/null; then
    echo -e "${YELLOW}Creating application user: $APP_USER${NC}"
    useradd -r -s /bin/false -d $APP_DIR $APP_USER
fi

# Add application user to docker group
usermod -aG docker $APP_USER

# Create application directory
echo -e "${YELLOW}Creating application directory...${NC}"
mkdir -p $APP_DIR
cd $APP_DIR

# Clone or update application code
if [ -d ".git" ]; then
    echo -e "${YELLOW}Updating application code...${NC}"
    git pull origin main
else
    echo -e "${YELLOW}Cloning application code...${NC}"
    git clone https://github.com/ofekraf/jugglefit_website.git .
fi

# Copy environment file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating environment file...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}Please edit .env file with your configuration${NC}"
fi

# Set ownership
chown -R $APP_USER:$APP_USER $APP_DIR

# Configure firewall
echo -e "${YELLOW}Configuring firewall...${NC}"
ufw --force enable
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp

# Copy and enable systemd service
echo -e "${YELLOW}Setting up systemd service...${NC}"
cp $APP_DIR/deploy/oci-ubuntu/jugglefit.service $SERVICE_FILE
systemctl daemon-reload
systemctl enable jugglefit

# Copy Nginx configuration
echo -e "${YELLOW}Setting up Nginx...${NC}"
cp $APP_DIR/deploy/oci-ubuntu/nginx.conf $NGINX_AVAILABLE/jugglefit
ln -sf $NGINX_AVAILABLE/jugglefit $NGINX_ENABLED/jugglefit

# Remove default Nginx site
rm -f $NGINX_ENABLED/default

# Test Nginx configuration
nginx -t

# Start services
echo -e "${YELLOW}Starting services...${NC}"
systemctl start jugglefit
systemctl restart nginx

# Enable log rotation
echo -e "${YELLOW}Setting up log rotation...${NC}"
cat > /etc/logrotate.d/jugglefit << EOF
/var/log/jugglefit/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
}
EOF

# Create log directory
mkdir -p /var/log/jugglefit
chown $APP_USER:$APP_USER /var/log/jugglefit

echo -e "${GREEN}Deployment completed successfully!${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Edit $APP_DIR/.env with your configuration"
echo "2. Run SSL setup: $APP_DIR/deploy/oci-ubuntu/setup-ssl.sh yourdomain.com"
echo "3. Check service status: systemctl status jugglefit"
echo "4. Check logs: journalctl -u jugglefit -f"
echo "5. Check application: curl http://localhost/health"