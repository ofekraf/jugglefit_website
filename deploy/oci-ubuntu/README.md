# JuggleFit OCI Ubuntu Deployment Guide

This guide provides comprehensive instructions for deploying the JuggleFit application on Oracle Cloud Infrastructure (OCI) using Ubuntu.

## Prerequisites

Before starting the deployment, ensure you have:

- Ubuntu 20.04 or 22.04 LTS server
- Root or sudo access
- At least 2GB memory (RAM) and 10GB disk space
- CPU: 1 vCPU minimum, 2 vCPU recommended
- Public IP address for external access
- Domain name (optional, for SSL configuration)

### System Requirements

- **OS**: Ubuntu 20.04/22.04 LTS
- **Memory**: Minimum 2GB, recommended 4GB
- **CPU**: 1 vCPU minimum, 2 vCPU recommended  
- **Disk**: Minimum 10GB available disk space
- **Network**: Open ports 80, 443, and 5001

## Installation

### 1. Initial Server Setup

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y curl wget git nginx ufw
```

### 2. Docker Installation

Run the deployment script to install Docker and configure the system:

```bash
# Make the deployment script executable
chmod +x deploy.sh

# Run the deployment script
sudo ./deploy.sh
```

The deployment script will:
- Install Docker and Docker Compose
- Configure system users and permissions
- Set up firewall rules
- Install the JuggleFit application

### 3. Manual Docker Installation (Alternative)

If you prefer manual installation:

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

## Configuration

### 1. Environment Configuration

Create a `.env` file with your configuration:

```bash
# Copy example environment file
cp .env.example .env

# Edit environment variables
nano .env
```

Required environment variables:
- `PORT`: Application port (default: 5001)
- `FLASK_ENV`: Set to 'production'
- `FLASK_DEBUG`: Set to 0 for production

### 2. Application Deployment

```bash
# Build and start the application
docker-compose -f docker-compose.prod.yml up -d --build

# Check application status
docker-compose -f docker-compose.prod.yml ps
```

### 3. Nginx Configuration

The provided `nginx.conf` file configures Nginx as a reverse proxy:

```bash
# Copy Nginx configuration
sudo cp nginx.conf /etc/nginx/sites-available/jugglefit
sudo ln -s /etc/nginx/sites-available/jugglefit /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test and reload Nginx
sudo nginx -t
sudo systemctl reload nginx
```

## SSL Configuration

### 1. Domain Setup

Point your domain to your server's public IP address before configuring SSL.

### 2. SSL Certificate Installation

```bash
# Make SSL setup script executable
chmod +x setup-ssl.sh

# Run SSL setup (replace with your domain)
sudo ./setup-ssl.sh yourdomain.com
```

The SSL setup script will:
- Install Certbot
- Obtain Let's Encrypt certificate
- Configure automatic renewal
- Update Nginx configuration

### 3. Manual SSL Setup (Alternative)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com

# Test automatic renewal
sudo certbot renew --dry-run
```

## Firewall Configuration

### 1. UFW Setup

```bash
# Enable firewall
sudo ufw enable

# Allow SSH (important!)
sudo ufw allow ssh

# Allow HTTP and HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Allow application port (if direct access needed)
sudo ufw allow 5001

# Check firewall status
sudo ufw status
```

### 2. OCI Security Rules

In your OCI console, ensure these ports are open in your security group:
- Port 22 (SSH)
- Port 80 (HTTP)
- Port 443 (HTTPS)
- Port 5001 (Application, if needed)

## Systemd Service

The included `jugglefit.service` file provides systemd integration:

```bash
# Copy service file
sudo cp jugglefit.service /etc/systemd/system/

# Enable and start service
sudo systemctl enable jugglefit
sudo systemctl start jugglefit

# Check service status
sudo systemctl status jugglefit
```

## Monitoring and Maintenance

### 1. Health Checks

Use the provided health check script:

```bash
# Make health check script executable
chmod +x health-check.sh

# Run health check
./health-check.sh
```

### 2. Backup

Use the backup script for regular backups:

```bash
# Make backup script executable
chmod +x backup.sh

# Run backup
./backup.sh
```

### 3. Log Monitoring

```bash
# View application logs
docker-compose -f docker-compose.prod.yml logs -f

# View Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## Troubleshooting

### Common Issues

#### Application Not Starting
```bash
# Check Docker status
sudo systemctl status docker

# Check container logs
docker-compose -f docker-compose.prod.yml logs

# Restart application
docker-compose -f docker-compose.prod.yml restart
```

#### SSL Certificate Issues
```bash
# Check certificate status
sudo certbot certificates

# Renew certificate manually
sudo certbot renew

# Check Nginx configuration
sudo nginx -t
```

#### Port Conflicts
```bash
# Check what's using port 80/443
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443

# Stop conflicting services
sudo systemctl stop apache2  # if Apache is installed
```

### Support

- Check application logs for specific error messages
- Ensure all required ports are open in both UFW and OCI security groups
- Verify domain DNS settings if using SSL
- Test health endpoints: `curl http://localhost:5001/health`

## Security Checklist

- [ ] Firewall configured (UFW enabled)
- [ ] OCI security groups properly configured
- [ ] SSL certificate installed and auto-renewal configured
- [ ] Application running as non-root user
- [ ] Regular backup schedule established
- [ ] Monitoring and health checks in place
- [ ] Default SSH port changed (recommended)
- [ ] SSH key authentication enabled
- [ ] Fail2ban installed (recommended)

## Updates and Maintenance

### Updating the Application

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart containers
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build
```

### System Updates

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Clean up old Docker images
docker system prune -a
```

For additional support, refer to the main project documentation or open an issue on the project repository.