#!/bin/bash

# JuggleFit Website Backup Script
# Creates backups of application data and configuration

set -e

# Configuration
BACKUP_DIR="/opt/jugglefit/backups"
APP_DIR="/opt/jugglefit"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="jugglefit_backup_$TIMESTAMP"
RETENTION_DAYS=30

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting JuggleFit backup...${NC}"

# Create backup directory
mkdir -p $BACKUP_DIR

# Create backup archive
echo -e "${YELLOW}Creating backup archive...${NC}"
tar -czf "$BACKUP_DIR/$BACKUP_NAME.tar.gz" \
    -C $APP_DIR \
    --exclude='*.log' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='venv' \
    --exclude='backups' \
    .env \
    docker-compose.prod.yml \
    deploy/

# Create backup info file
cat > "$BACKUP_DIR/$BACKUP_NAME.info" << EOF
Backup created: $(date)
Application directory: $APP_DIR
Backup size: $(du -h "$BACKUP_DIR/$BACKUP_NAME.tar.gz" | cut -f1)
Git commit: $(cd $APP_DIR && git rev-parse HEAD 2>/dev/null || echo "Unknown")
Docker images: $(docker images --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}" | grep jugglefit || echo "None")
EOF

# Clean up old backups
echo -e "${YELLOW}Cleaning up old backups (keeping $RETENTION_DAYS days)...${NC}"
find $BACKUP_DIR -name "jugglefit_backup_*.tar.gz" -mtime +$RETENTION_DAYS -delete
find $BACKUP_DIR -name "jugglefit_backup_*.info" -mtime +$RETENTION_DAYS -delete

echo -e "${GREEN}Backup completed: $BACKUP_DIR/$BACKUP_NAME.tar.gz${NC}"
echo "Backup info: $BACKUP_DIR/$BACKUP_NAME.info"