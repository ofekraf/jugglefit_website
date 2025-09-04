#!/bin/bash

# JuggleFit Website Health Check Script
# Monitors application health and sends alerts if needed

set -e

# Configuration
HEALTH_URL="http://localhost:5001/health"
LOG_FILE="/var/log/jugglefit/health-check.log"
MAX_RESPONSE_TIME=10  # seconds
ALERT_EMAIL=""  # Set to receive email alerts

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create log directory if it doesn't exist
mkdir -p "$(dirname "$LOG_FILE")"

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Function to send alert (if email is configured)
send_alert() {
    if [ -n "$ALERT_EMAIL" ]; then
        echo "Subject: JuggleFit Health Check Alert" | sendmail "$ALERT_EMAIL" << EOF
JuggleFit website health check failed at $(date).

Error: $1

Please check the application status:
- systemctl status jugglefit
- journalctl -u jugglefit -n 20
- curl $HEALTH_URL

Server: $(hostname)
EOF
    fi
}

# Perform health check
echo -e "${YELLOW}Performing health check...${NC}"

# Check if application responds
if response=$(curl -s -w "%{http_code}:%{time_total}" --max-time $MAX_RESPONSE_TIME "$HEALTH_URL" 2>/dev/null); then
    http_code=$(echo "$response" | cut -d: -f1)
    response_time=$(echo "$response" | cut -d: -f2)
    
    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✓ Application is healthy${NC}"
        echo -e "  Response time: ${response_time}s"
        log_message "SUCCESS: Health check passed (${response_time}s)"
        exit 0
    else
        error_msg="HTTP $http_code response from health endpoint"
        echo -e "${RED}✗ $error_msg${NC}"
        log_message "ERROR: $error_msg"
        send_alert "$error_msg"
        exit 1
    fi
else
    error_msg="Failed to connect to health endpoint"
    echo -e "${RED}✗ $error_msg${NC}"
    log_message "ERROR: $error_msg"
    send_alert "$error_msg"
    exit 1
fi