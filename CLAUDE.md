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
Create a `.env` file with:
```bash
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
```bash
# Build and run with Docker Compose
docker-compose up --build

# Build individual container
docker build -t jugglefit-website .
docker run -p 5001:5001 --env-file .env jugglefit-website
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
- `POST /api/shorten_url`: Generate short URLs with automatic expiry
- `GET /shortener/<code>`: Redirect to original URL and refresh expiry

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

Currently no formal test suite exists. Manual testing involves:
- Route generation with various filter criteria
- URL shortening and redirection functionality
- Trick filtering and serialization
- Template rendering with different data sets

## Deployment Considerations

**Environment Variables:**
- Google Sheets API credentials are required for trick suggestions
- PostgreSQL configuration defaults to hardcoded values if not provided
- Flask runs in debug mode by default in `app.py`

**Database Setup:**
- PostgreSQL table creation is handled automatically via `init_db()`
- Background cleanup thread starts automatically on app initialization
- No migration system - schema changes require manual intervention