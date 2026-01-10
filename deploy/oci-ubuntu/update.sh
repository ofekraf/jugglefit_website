#!/bin/bash

# JuggleFit Update Script
# Updates the application code, rebuilds images, and restarts the service

set -e

APP_DIR="/opt/jugglefit"
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting JuggleFit update...${NC}"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${YELLOW}This script must be run as root (use sudo)${NC}"
   exit 1
fi

cd $APP_DIR

# Pull latest changes
echo -e "${YELLOW}Pulling latest changes from git...${NC}"
git pull origin main

# Rebuild docker images
echo -e "${YELLOW}Rebuilding Docker images...${NC}"
docker-compose -f docker-compose.prod.yml build

# Restart service
echo -e "${YELLOW}Restarting jugglefit service...${NC}"
systemctl restart jugglefit

echo -e "${GREEN}Update completed successfully!${NC}"