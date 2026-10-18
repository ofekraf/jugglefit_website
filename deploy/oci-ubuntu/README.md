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
- **Network**: Open ports 80 and 443. Port 5001 (gunicorn) is bound to
  127.0.0.1 only and must NOT be opened; nginx is the public entry point.

## Routine deploys (TL;DR)

Everything host-level lives in the repo, so a deploy is one command:

```bash
sudo bash /opt/jugglefit/deploy/oci-ubuntu/update.sh
```

It snapshots the DB, pulls, rebuilds the container, waits for `/health`, then
runs `install-host-config.sh`, which installs from the repo:

| Repo file | Installed to |
|---|---|
| `nginx/http.conf` | `/etc/nginx/conf.d/jugglefit.conf` (rate-limit zones, cache, maps) |
| `nginx/app.conf` | `/etc/nginx/snippets/jugglefit-app.conf` (locations, gzip, headers) |
| `nginx/site-http.conf` / `nginx/site-https.conf` | `/etc/nginx/sites-available/jugglefit` |
| `jugglefit.service` | `/etc/systemd/system/jugglefit.service` |

The HTTPS template is used automatically once
`/etc/letsencrypt/live/<first domain>/` exists. Domains come from `DOMAINS=`
in `/opt/jugglefit/.env` (set by `setup-ssl.sh`). If `nginx -t` rejects the
new config, the previous one is restored. **Don't edit these files on the
host**; the next deploy overwrites them.

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
- `ADMIN_PASSWORD`: Password to create live finals on `/live_event`. Empty turns the feature off.

### 2. Application Deployment

```bash
# Build and start the application
docker-compose -f docker-compose.prod.yml up -d --build

# Check application status
docker-compose -f docker-compose.prod.yml ps
```

### 3. Nginx Configuration

Installed automatically by `install-host-config.sh` (see the table above).
To apply nginx/systemd changes without a full deploy:

```bash
sudo bash /opt/jugglefit/deploy/oci-ubuntu/install-host-config.sh
```

### 4. Live finals and venue load

`nginx/http.conf` + `nginx/app.conf` are sized for ~150 phones on one venue
Wi-Fi (they all share one public IP): per-IP limits for pages, static files,
the cached live state and the organizer password; `/static/` served from
`/opt/jugglefit/static/` by nginx; 429 instead of 503 when a limit is hit.
HTTP/2 is on in the HTTPS template.

One host-level setting outside the repo: **`worker_connections`** in
`/etc/nginx/nginx.conf` (`events {}`). Raise the Ubuntu default of 768 to
`4096` if you expect large venue crowds.

To verify after a deploy:

- `curl -sI https://<domain>/static/css/base/base.css` returns 200 (nginx can
  read `/opt/jugglefit/static/`)
- `curl -sI https://<domain>/api/finals/<id>/state` twice: `X-Cache-Status: MISS`, then `HIT`

## SSL Configuration

### 1. Domain Setup

Point your domain to your server's public IP address before configuring SSL.

### 2. SSL Certificate Installation

```bash
# Make SSL setup script executable
chmod +x setup-ssl.sh

# Run SSL setup (replace with your domain(s); first one names the cert)
sudo ./setup-ssl.sh yourdomain.com www.yourdomain.com
```

The SSL setup script will:
- Write `DOMAINS=` to `/opt/jugglefit/.env`
- Obtain a Let's Encrypt certificate (`certbot certonly --nginx`; certbot does
  not edit nginx config)
- Switch nginx to the repo's HTTPS template
- Install a renewal hook that reloads nginx (renewal itself runs from
  certbot's systemd timer)

Test renewal with `sudo certbot renew --dry-run`.

**Existing host whose cert was created by `certbot --nginx`:** just add
`DOMAINS=yourdomain.com,www.yourdomain.com` to `.env` and run `update.sh`. The
existing certificate under `/etc/letsencrypt/live/` is reused. If its directory
name differs from the first domain, also set `CERT_NAME=` (see
`sudo certbot certificates`).

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

# Do NOT open 5001: gunicorn listens on 127.0.0.1:5001 only, behind nginx.

# Check firewall status
sudo ufw status
```

### 2. OCI Security Rules

In your OCI console, ensure these ports are open in your security group:
- Port 22 (SSH)
- Port 80 (HTTP)
- Port 443 (HTTPS)
- Close port 5001 if it was opened earlier (no longer needed)

## Systemd Service

`jugglefit.service` is installed by `install-host-config.sh`. It is a
oneshot unit that runs `docker compose up -d` at boot; Docker's
`restart: unless-stopped` keeps the container running.

```bash
sudo systemctl status jugglefit   # should be "active (exited)"
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
sudo bash /opt/jugglefit/deploy/oci-ubuntu/update.sh
```

### System Updates

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Clean up old Docker images
docker system prune -a
```

For additional support, refer to the main project documentation or open an issue on the project repository.