# JuggleFit Website

Welcome to the JuggleFit website, a platform for a revolutionary sport-juggling competition. JuggleFit aims to create a motivating, fair, and exciting competition that measures juggling skill through control over specific tricks, with minimal preparation required. This website serves as the hub for event information, route creation, and community engagement.

This repository contains the source code for the JuggleFit website, built using Flask, Python, Docker, and modern web technologies. Whether you're a juggler, event host, or developer, you're welcome to explore, use, or contribute!

🌐 **Live Demo**: [jugglefit.org](https://www.jugglefit.org)

## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Development Setup](#development-setup)
- [Production Deployment](#production-deployment)
- [Docker Usage](#docker-usage)
- [Testing](#testing)
- [Environment Variables](#environment-variables)
- [API Endpoints](#api-endpoints)
- [Contributing](#contributing)
- [License](#license)

## Features

### Core Functionality
- **Route Generation**: Create custom juggling practice routes with various filters
- **Trick Database**: Comprehensive database of juggling tricks for balls, clubs, and rings
- **Event Management**: Information about past and upcoming juggling events
- **Team Profiles**: Meet the JuggleFit team members
- **Equipment Guide**: Recommendations for juggling equipment

### Technical Features
- **Dockerized Deployment**: Complete Docker setup for development and production
- **CI/CD Pipeline**: Automated testing and deployment with GitHub Actions
- **Health Monitoring**: Built-in health checks and monitoring endpoints
- **Security**: Rate limiting, security headers, and SSL/TLS support
- **Scalable Architecture**: Designed for cloud deployment and horizontal scaling

## Quick Start

### Using Docker (Recommended)

#### Development Environment
```bash
# Clone the repository
git clone https://github.com/ofekraf/jugglefit_website.git
cd jugglefit_website

# Copy environment template
cp .env.example .env

# Start development environment
docker-compose up --build
```

The application will be available at `http://localhost:5001`

#### Production Environment
```bash
# Start production environment
docker-compose -f docker-compose.prod.yml up --build -d
```

### Traditional Setup

1. **Install Python Dependencies**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Run Development Server**
   ```bash
   flask run
   # or
   python app.py
   ```

## Development Setup

### Prerequisites
- Python 3.11+
- Docker and Docker Compose (recommended)
- Git

### Local Development

1. **Clone and Setup**
   ```bash
   git clone https://github.com/ofekraf/jugglefit_website.git
   cd jugglefit_website
   
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Environment Configuration**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your specific settings:
   - Google Sheets API credentials (optional)
   - Flask configuration
   - Any custom settings

3. **Run Development Server**
   ```bash
   # With Flask CLI
   flask run
   
   # Or directly with Python
   python app.py
   
   # With Docker (recommended)
   docker-compose up --build
   ```

### Development Tools

- **Linting and Formatting**: Configure your editor with Python linting
- **Testing**: Run tests with `pytest tests/`
- **Docker Testing**: Run Docker-specific tests with `pytest tests/docker/`

## Production Deployment

### Cloud Platforms

#### Oracle Cloud Infrastructure (OCI) Ubuntu
See detailed instructions in [`deploy/oci-ubuntu/README.md`](deploy/oci-ubuntu/README.md)

```bash
# Quick OCI deployment
sudo ./deploy/oci-ubuntu/deploy.sh
sudo ./deploy/oci-ubuntu/setup-ssl.sh yourdomain.com
```

#### Other Platforms
- **Render**: Connect your GitHub repository for automatic deployments
- **Railway**: Use the provided `docker-compose.prod.yml`
- **Heroku**: Includes `Procfile` for Heroku deployment
- **DigitalOcean App Platform**: Docker-based deployment supported

### Manual Production Setup

1. **Build Production Image**
   ```bash
   docker build -t jugglefit-website .
   ```

2. **Run Production Container**
   ```bash
   docker run -d \
     --name jugglefit \
     -p 5001:5001 \
     --env-file .env \
     --restart unless-stopped \
     jugglefit-website
   ```

3. **Set Up Reverse Proxy** (Nginx recommended)
   ```bash
   # Copy configuration
   sudo cp deploy/oci-ubuntu/nginx.conf /etc/nginx/sites-available/jugglefit
   sudo ln -s /etc/nginx/sites-available/jugglefit /etc/nginx/sites-enabled/
   sudo systemctl reload nginx
   ```

## Docker Usage

### Available Images
- **Development**: Full development environment with hot reload
- **Production**: Optimized production image with Gunicorn

### Docker Commands

```bash
# Development
docker-compose up --build                    # Start development environment
docker-compose down                          # Stop and remove containers

# Production
docker-compose -f docker-compose.prod.yml up -d    # Start production environment
docker-compose -f docker-compose.prod.yml down     # Stop production environment

# Maintenance
docker-compose logs -f                       # View logs
docker-compose exec web bash                # Access container shell
```

### Image Optimization
- Multi-stage builds for smaller production images
- Non-root user for security
- Health checks for monitoring
- Optimized layer caching

## Testing

### Running Tests

```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run specific test categories
pytest tests/docker/                        # Docker-related tests
pytest tests/docker/test_dockerfile.py      # Dockerfile tests only
pytest tests/docker/test_production.py      # Production tests only

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=.
```

### Test Categories
- **Docker Tests**: Container functionality, builds, and deployments
- **Application Tests**: Flask application functionality
- **Integration Tests**: End-to-end workflow testing
- **Security Tests**: Security configuration validation

### Continuous Integration
Tests run automatically on:
- Pull requests
- Pushes to main/develop branches
- GitHub Actions workflow handles testing, building, and deployment

## Environment Variables

### Required Variables
```bash
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development  # or production
DEBUG=False            # Set to False in production
```

### Optional Variables
```bash
# Google Sheets API (for trick suggestions)
JUGGLEFIT_BOT_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"
TRICK_SUGGESTIONS_SPREADSHEET_ID=your_spreadsheet_id

# PostgreSQL (future feature)
POSTGRESQL_DBNAME=database_name
POSTGRESQL_USERNAME=username
POSTGRESQL_PASSWORD=password
POSTGRESQL_HOST=localhost
POSTGRESQL_PORT=5432

# Production Settings
PORT=5001
WORKERS=4
TIMEOUT=30
```

### Environment Files
- `.env.example`: Template with all available variables
- `.env`: Your local configuration (not tracked in git)
- `deploy/oci-ubuntu/.env.production`: Production template

## API Endpoints

### Health and Monitoring
- `GET /health`: Application health check
- `GET /ready`: Readiness probe for load balancers

### Core API (`/api/` prefix)
- `POST /api/serialize_route`: Convert route data to compressed string
- `POST /api/fetch_tricks`: Filter tricks by criteria
- `POST /api/shorten_url`: Generate short URLs (currently disabled)

### Web Pages
- `/`: Homepage with events and information
- `/generate_route`: Create custom juggling routes
- `/build_route`: Interactive route builder
- `/past_events`: Archive of past events
- `/host_event`: Information for event hosts
- `/equipment_list`: Equipment recommendations

## Contributing

We welcome contributions! Here's how to get started:

### Development Process
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes following our coding standards
4. Write tests for new functionality
5. Run tests: `pytest`
6. Submit a pull request

### Coding Standards
- Follow PEP 8 for Python code
- Write comprehensive tests for new features
- Use Docker for development and testing
- Document your changes in commit messages

### Test-Driven Development
We use TDD for infrastructure changes:
1. Write failing tests first
2. Implement code to pass tests
3. Refactor and optimize
4. All tests must pass before merging

### Contact
- **Email**: jugglefit.competition@gmail.com
- **Project Management**: We use ClickUp for development coordination

## Architecture

### Technology Stack
- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **Containerization**: Docker, Docker Compose
- **CI/CD**: GitHub Actions
- **Deployment**: Multiple cloud platforms supported
- **Monitoring**: Built-in health checks

### Project Structure
```
jugglefit_website/
├── app.py                      # Main Flask application
├── wsgi.py                     # WSGI entry point
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker container configuration
├── docker-compose.yml          # Development environment
├── docker-compose.prod.yml     # Production environment
├── .env.example               # Environment template
├── pylib/                     # Core application modules
├── hardcoded_database/        # Static data (tricks, events, team)
├── static/                    # CSS, JavaScript, images
├── templates/                 # HTML templates
├── tests/                     # Test suite
├── deploy/                    # Deployment configurations
│   └── oci-ubuntu/           # OCI Ubuntu deployment
└── .github/workflows/        # CI/CD pipeline
```

## Troubleshooting

### Common Issues

#### Docker Issues
```bash
# Container won't start
docker-compose logs web

# Port already in use
docker-compose down
# Change port in docker-compose.yml if needed

# Permission denied
sudo chown -R $USER:$USER .
```

#### Application Issues
```bash
# Check application logs
docker-compose logs -f web

# Check health endpoint
curl http://localhost:5001/health

# Debug mode
export FLASK_ENV=development
flask run --debug
```

#### Production Issues
```bash
# Check service status
systemctl status jugglefit

# Check application logs
journalctl -u jugglefit -f

# Check Nginx logs
tail -f /var/log/nginx/jugglefit_error.log
```

### Getting Help
1. Check this README and documentation
2. Review the troubleshooting guides in `deploy/oci-ubuntu/README.md`
3. Check existing GitHub issues
4. Create a new issue with detailed error information

## License

This project is open source. Please respect the community guidelines and contribute positively to the juggling community.

---

**Happy Juggling! 🤹‍♂️🤹‍♀️**
