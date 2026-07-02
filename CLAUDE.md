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

Create a `.env` file from `.env.example`:
```bash
# Port Configuration (CRITICAL - Flask reads this!)
PORT=5001

# Flask Configuration
FLASK_ENV=development         # Set to 'production' for production
SECRET_KEY=<random-hex>       # REQUIRED when FLASK_ENV=production (app aborts otherwise)

# SQLite storage
SQLITE_DB_DIR=./database_data
SQLITE_DB_NAME=jugglefit.db

# Super-admin (env-credential login at /auth/login and /admin/login)
SUPER_ADMIN_USER=Admin
SUPER_ADMIN_PASSWORD=<change-me>
```

### Running the Application
```bash
# Development server
flask run

# Alternative using Python directly (debug on unless FLASK_ENV=production)
python app.py  # Runs on host='0.0.0.0', port=$PORT (default 5001)

# Production using WSGI
gunicorn --bind 0.0.0.0:5001 --workers 2 --threads 4 --preload wsgi:app
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
- **Main App** (`app.py`): Flask app config, CSRF, and public page routes
- **Blueprints** (`blueprints/`): `auth.py`, `games.py`, `api.py`, `admin.py`
- **Database Layer** (`database/db_manager.py`): SQLite (WAL mode) — tricks, candidates, votes, users, short URLs. Schema is auto-created on `init_db()`; lightweight migrations run at startup.
- **Hardcoded Data**: Static data for events, team members, and seed tricks in `/hardcoded_database/`
- **Classes**: `Trick`, `Route`, `Prop`, `Tag` core entities in `pylib/classes/`
- **Crowd Rating** (`pylib/rating/`): Elo-based difficulty rating, task tokens, promotion pipeline — see `docs/crowd_backend.md`
- **Route Generation**: Algorithm-based practice-route builder

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
- SQLite `url_mappings` table with automatic expiry
- Cleanup runs on app startup and nightly via `database/prune.py`
- Same-origin guard prevents open-redirect abuse; 8 KB length cap

### API Endpoints

**Core API** (`/api/` blueprint — `blueprints/api.py`):
- `POST /api/fetch_tricks`: Filter tricks by criteria, return JSON
- `POST /api/trick_exists`: Dedup check for name/siteswap
- `POST /api/suggest_trick`: Submit a trick to the crowd pipeline
- `POST /api/shorten_url`: Generate short URLs (same-origin only)
- `GET  /api/leaderboard`: Contribution leaderboards
- `GET  /shortener/<code>`: Redirect to original URL

**Games API** (`/api/games/` — `blueprints/games.py`):
- `GET  /api/games/needs`, `GET /api/games/<game>/next_set`
- `POST /api/games/answer`, `POST /api/games/flag`

**Admin API** (`/admin/api/` — `blueprints/admin.py`):
- Candidates list/detail, promote/reject/restore/delete, backup, prune, user-admin toggle

**Health and Monitoring**:
- `GET /health`: Container health check endpoint (returns JSON status)
- `GET /ready`: Readiness probe for load balancers

### Configuration System

**Constants Management** (`pylib/configuration/consts.py`):
- Trick validation limits (props count, difficulty ranges)
- Rating pipeline knobs (set size, control fraction, promotion thresholds)
- Session lifetimes, leaderboard periods

**Database Configuration** (`database/db_manager.py`):
- SQLite path from `SQLITE_DB_DIR` / `SQLITE_DB_NAME`
- WAL mode + `busy_timeout` for multi-worker gunicorn

## Key Development Patterns

### Error Handling
- Custom exceptions in `pylib/route_generator/exceptions.py`
- Validation in class `__post_init__` methods
- Try-catch blocks with user-friendly error messages

### Data Loading and Caching
- Seed CSV tricks loaded into SQLite on first `init_db()`
- `ALL_PROPS_TRICKS` cached in-process (loaded at import, refreshed after promotion)
- Static data in Python modules for events and team information
- User-submitted tricks flow through the crowd pipeline (`pylib/rating/intake.py`)

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
- `SECRET_KEY` is **required** when `FLASK_ENV=production` (app raises on boot otherwise)
- `SUPER_ADMIN_USER` / `SUPER_ADMIN_PASSWORD` gate `/admin/*`
- Debug mode is only enabled when `FLASK_ENV != production`

**Database Setup:**
- SQLite schema is created automatically via `init_db()` on startup
- Lightweight column-add migrations in `db_manager._MIGRATIONS`
- Backups: `database/backup.py` snapshots the DB file; `deploy/oci-ubuntu/setup.sh`
  wires cron + rclone for off-box copies

**Security:**
- CSRF: session-token guard in `app._csrf_protect`; forms use `{{ csrf_token() }}`,
  JS `fetch()` gets `X-CSRF-Token` auto-attached via `<head>` shim in `base.html`
- Session cookies: `HttpOnly`, `SameSite=Lax`, `Secure` in prod
- URL shortener rejects off-site targets (`_is_same_origin`)

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