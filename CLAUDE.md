# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is the JuggleFit website, a Flask-based platform for juggling competitions that measures skill through control over specific tricks. The site includes route generation, trick databases, event management, and URL shortening capabilities.

## Development Commands

### Setup and Dependencies
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Configuration
**IMPORTANT**: Always check the `.env` file for the `PORT` setting, as it overrides the default Flask port.

Create a `.env` file with:
```bash
# Port Configuration (CRITICAL - Flask reads this!)
PORT=5001  # Default Flask port - change carefully if needed

# Flask Configuration
FLASK_ENV=development  # Set to 'production' for production
FLASK_DEBUG=1         # Set to 0 for production

# Google Sheets API Configuration
JUGGLEFIT_BOT_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYour private key here\n-----END PRIVATE KEY-----"
TRICK_SUGGESTIONS_SPREADSHEET_ID=your_spreadsheet_id

# PostgreSQL Configuration (optional - falls back to hardcoded values)
POSTGRESQL_DBNAME=database_name
POSTGRESQL_USERNAME=username
POSTGRESQL_PASSWORD=password
POSTGRESQL_HOST=localhost
POSTGRESQL_PORT=5432
```

### Running the Application
```bash
# Development server
flask run

# Alternative using Python directly
python app.py  # Runs on host='0.0.0.0', port=5001, debug=True

# Production using WSGI
gunicorn -w 4 -b 0.0.0.0:5001 wsgi:app
```

### Docker Deployment
**IMPORTANT Docker Port Mapping**: The Flask app reads the `PORT` environment variable from `.env`. 
- If `.env` has `PORT=5001`, use: `docker run -p 5001:5001`
- If `.env` has `PORT=3333`, use: `docker run -p 5001:3333` (maps host 5001 to container 3333)
- Always check `.env` file first to avoid port mapping confusion!

```bash
# Check what port Flask will use
grep PORT .env

# Development with Docker Compose
docker-compose up --build

# Production with Docker Compose  
docker-compose -f docker-compose.prod.yml up -d

# Manual Docker build and run
docker build -t jugglefit-website .
docker run -p 5001:5001 --env-file .env jugglefit-website

# Common Docker troubleshooting
docker ps                           # List running containers
docker logs <container-name>        # Check container logs
docker rm -f <container-name>       # Force remove container
```

## Architecture Overview

### Core Components

**Flask Application Structure:**
- **Main App** (`app.py`): Central Flask application with route definitions and API endpoints
- **Database Layer**: PostgreSQL integration for URL shortening with automatic cleanup
- **Hardcoded Data**: Static data for events, team members, and tricks stored in `/hardcoded_database/`
- **Classes**: Object-oriented design with `Trick`, `Route`, `Prop`, `Tag`, and other core entities
- **Route Generation**: Algorithm-based system for creating juggling practice routes

**Key Classes and Their Relationships:**
- **`Trick`** (`pylib/classes/trick.py`): Core entity with name, props_count, difficulty, tags, and validation
- **`Route`** (`pylib/classes/route.py`): Collection of tricks with serialization/compression for URL sharing
- **`RouteGenerator`** (`pylib/route_generator/route_generator.py`): Filters and selects tricks based on criteria
- **`Prop`** (`pylib/classes/prop.py`): Enum for juggling prop types (balls, clubs, rings)
- **`Tag`** (`pylib/classes/tag.py`): Categorized tags for trick classification

### Data Architecture

**Trick Database:**
- CSV-based storage in `/hardcoded_database/tricks/` (balls.csv, clubs.csv, rings.csv)
- Loaded via `trick_loader.py` with validation and tag parsing
- Filterable by props count, difficulty, tags, and prop type

**Route Serialization:**
- JSON → zlib compression → base64 encoding for URL-friendly route sharing
- Enables deep-linking to specific routes via query parameters

**URL Shortening System:**
- PostgreSQL table with automatic expiry and cleanup
- Background thread for removing expired URLs
- Configurable expiry and extension periods

### API Endpoints

**Core API** (`/api/` blueprint):
- `POST /api/serialize_route`: Convert route data to compressed string
- `POST /api/fetch_tricks`: Filter tricks by criteria, return JSON
- `POST /api/shorten_url`: Generate short URLs (currently disabled)
- `GET /shortener/<code>`: Redirect to original URL (currently disabled)

**Health and Monitoring**:
- `GET /health`: Container health check endpoint (returns JSON status)
- `GET /ready`: Readiness probe for load balancers

### Configuration System

**Constants Management** (`pylib/configuration/consts.py`):
- Trick validation limits (props count, difficulty ranges)
- Default values for route generation
- Maximum name lengths and other constraints

**Database Configuration** (`database/hardcoded_config.py`):
- PostgreSQL connection parameters with environment variable fallbacks
- URL shortening behavior (expiry intervals, cleanup frequency)

## Key Development Patterns

### Error Handling
- Custom exceptions in `pylib/route_generator/exceptions.py`
- Validation in class `__post_init__` methods
- Try-catch blocks with user-friendly error messages

### Data Loading and Caching
- CSV-based trick databases loaded at application startup
- Static data in Python modules for events and team information
- Google Sheets integration for user-submitted trick suggestions

### Template Architecture
- Jinja2 templates in `/templates/` with base template inheritance
- JavaScript utilities in `/static/js/` for dynamic interactions
- CSS styling in `/static/css/styles.css`

## Testing and Validation

### Test Suite
The project includes a comprehensive test suite using pytest:

```bash
# Install test dependencies (included in requirements.txt)
pip install pytest pytest-docker docker pyyaml

# Run all tests
pytest

# Run specific test categories
pytest tests/docker/                        # Docker-related tests
pytest tests/docker/test_dockerfile.py      # Dockerfile tests only  
pytest tests/docker/test_production.py      # Production deployment tests

# Run with verbose output
pytest -v

# Run with coverage (if coverage tools installed)
pytest --cov=.
```

### Test Categories
- **Docker Tests** (`tests/docker/`): Container functionality, builds, health checks
- **Application Tests**: Flask application functionality (TODO)
- **Integration Tests**: End-to-end workflow testing (TODO)

### Manual Testing
For manual verification:
- Route generation with various filter criteria
- Health endpoints: `curl http://localhost:5001/health`
- Trick filtering and serialization
- Template rendering with different data sets
- Docker container startup and port mapping

## Deployment Considerations

**Environment Variables:**
- Google Sheets API credentials are required for trick suggestions
- PostgreSQL configuration defaults to hardcoded values if not provided
- Flask runs in debug mode by default in `app.py`

**Database Setup:**
- PostgreSQL table creation is handled automatically via `init_db()`
- Background cleanup thread starts automatically on app initialization
- No migration system - schema changes require manual intervention

## GitHub Actions and CI/CD

### Authentication Setup
To work with GitHub Actions, ensure proper authentication:

```bash
# Check current authentication
gh auth status

# If not authenticated to github.com, login:
gh auth login --hostname github.com

# Select HTTPS protocol and authenticate via web browser
```

### Checking CI/CD Status
```bash
# List recent workflow runs
gh run list --limit 5

# View details of a specific run
gh run view <run-id>

# View logs of a failed run
gh run view <run-id> --log-failed

# Check workflow status
gh workflow list
gh workflow view deploy.yml
```

### Common CI/CD Issues
- **Authentication failures**: Re-run `gh auth login --hostname github.com`
- **Test failures**: Run tests locally first with `pytest`
- **Docker build failures**: Ensure Dockerfile and requirements.txt are correct
- **Environment variables**: GitHub secrets must match `.env.example` structure

### Troubleshooting GitHub Actions
If you encounter issues:
1. Check the Actions tab on github.com
2. Review workflow logs for specific error messages
3. Test Docker builds locally before pushing
4. Ensure all required secrets are configured in repository settings