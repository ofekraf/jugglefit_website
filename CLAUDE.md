# CLAUDE.md

This file provides guidance to AI coding agents (Claude Code, and others)
when working with code in this repository.

## Repository Overview

This is the JuggleFit website, a Flask-based platform for juggling competitions that measures skill through control over specific tricks. The site includes route generation, trick databases, event management, and URL shortening capabilities.

## Hard rules — read before touching routes, URLs, or templates

1. **Never change these URL paths**: `/created_route`, `/run_route`,
   `/live_event` (defined in `app.py` via `_render_route_page`). They are
   embedded in QR codes and short links printed on physical event
   materials and shared externally. The `?route=<serialized>` query
   parameter format (JSON → zlib → base64, see `pylib/classes/route.py`
   `Route.serialize`/`deserialize`) must also stay backward compatible.
   `/build_route?route=...` is used for "Edit" links and should be
   treated with the same care.
2. Do not rename existing Flask endpoint names that templates reference
   via `url_for(...)` without also updating every template. The legacy
   aliases `admin_login`/`admin_logout`/`admin_crowd`/`admin_users`
   (registered in `app.py` after blueprint registration) exist so old
   `url_for('admin_crowd')`-style calls keep working — don't remove them
   without grepping `templates/` first.
3. `hardcoded_database/events/upcoming_events.py` and
   `hardcoded_database/events/past_events/__init__.py` must stay
   **ordered by date** (explicit `# Keep ordered by date` comments) —
   insert new entries in chronological position rather than appending.
   `hardcoded_database/organization/team.py` similarly has a
   `# Order for team page` comment — that order is intentional display
   order, not alphabetical.
4. There's no application-level test suite yet (only `tests/docker/`
   exists — see Testing section below). Before committing changes to
   routes or templates, sanity-check by running the app in-process and
   hitting the affected pages, e.g.:
   ```python
   import app as appmod
   client = appmod.app.test_client()
   print(client.get("/some/path").status_code)
   ```
   For anything touching `/created_route`, `/run_route`, `/live_event`,
   or `/build_route`, test with a real serialized `Route` (see
   `pylib/classes/route.py`) rather than a made-up string, since these
   pages require a valid `?route=` payload or they redirect.

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
- Jinja2 templates in `/templates/` with base template inheritance (see "Frontend Architecture" below)
- JavaScript utilities in `/static/js/` for dynamic interactions
- CSS split into small, focused files under `/static/css/{base,components,pages}/`
  instead of one monolithic stylesheet (see "Frontend Architecture" below)

## Frontend Architecture (templates + CSS)

### Template structure

- Every page template extends `templates/macros/base.html`, the single
  site-wide layout (`<head>`, navbar, `<main>`, footer, orientation-alert
  overlay, CSRF-fetch shim). The three mini-games (`games/harder.html`,
  `games/tagging.html`, `games/throw.html`) extend
  `templates/games/_game_base.html`, which itself extends `base.html`.
- The navbar is a separate partial, `templates/macros/navbar.html`,
  included by `base.html` via `{% include %}`. Edit the navbar there, not
  in `base.html`.
- Reusable form controls / widgets live under `templates/macros/` as
  Jinja `{% macro %}` definitions (imported via `{% from ... import ... %}`)
  or plain `{% include %}` partials (e.g. `route_display.html`,
  `trick_container.html`, `juggler_captcha.html`, `siteswap_x_toggle.html`
  are includes, not macros, despite living in the same folder — check
  which pattern a given file uses before copying it as a template).
- Standard child-template blocks: `{% block title %}`, `{% block head %}`
  (page-specific `<link>`/`<script>`/`<style>`, call `{{ super() }}` first
  if you need anything `base.html`'s own `head` block would add),
  `{% block content %}`, `{% block scripts %}`.
- `templates/siteswap_modifiers_printed_page.html` is the one exception —
  a standalone full HTML document (no `{% extends %}`) used for a print
  popup. Leave it self-contained.

### CSS structure — do not recreate a monolithic stylesheet

CSS was refactored from one 3600+ line `static/css/styles.css` into small,
focused files under `static/css/{base,components,pages}/`. Keep it that
way — new styles should go into an existing file if they fit its scope,
or a new small file if they don't, never back into one giant file.

**Global** (linked unconditionally in `macros/base.html`, loaded on every
page — because either the classes are used site-wide, or JS present on
most pages can inject that markup at runtime):
- `base/variables.css` — CSS custom properties (`--primary-color` etc.)
- `base/base.css` — resets + small utility classes (`.hidden`,
  `.text-center`, `.float-right`, `.mt-1`/`.mt-1-5`/`.mt-2`)
- `base/layout.css` — `.main-content`, `.section*`, spacing/card helpers
- `base/animations.css` — shared `@keyframes`
- `components/navbar.css`, `components/footer.css`
- `components/buttons.css`, `components/forms.css`
- `components/orientation-alert.css`, `components/toast.css`,
  `components/print.css`
- `components/trick-display.css`, `components/prop-selection.css`,
  `components/siteswap-x.css` — these three are global even though their
  *static* markup only appears on a few templates, because
  `static/js/route_helpers.js`, `static/js/siteswap_x.js`, and
  `static/js/game_engine.js` can dynamically inject `.trick-*`/`.prop-*`/
  `.siteswap-x-*` elements into almost any route-related or game page.

**Page-scoped** (only linked via `{% block head %}` on the templates that
actually need them — check `static/css/pages/*.css` and
`static/css/components/{carousel,tag-categories,countdown-timer,captcha}.css`
before assuming something is global):
- `pages/home.css` + `components/carousel.css` → `index.html`,
  `host_event.html`
- `pages/route-pages.css` → any page using the `.route-page`/
  `.route-header`/`.route-form` wrapper classes (add_tricks, generate_route,
  build_route, created_route, leaderboard, software_contribution,
  admin/crowd, admin/users, admin/login, auth/login, auth/register,
  auth/profile, games/hub, games/_game_base)
- `pages/add-tricks.css` → pages using `.custom-trick-form` (add_tricks,
  build_route, admin/login, auth/login, auth/register)
- `components/tag-categories.css` → build_route, generate_route
- `components/countdown-timer.css` → created_route, live_event
- `components/captcha.css` → add_tricks
- `pages/donate.css`, `pages/past-events.css`, `pages/live-event.css`,
  `pages/siteswap-x.css`, `pages/siteswap-x-formatter.css` → one page each
  (name matches the page)
- `static/css/run_route.css` → `run_route.html` only (was already
  separate before this refactor, untouched)

When adding a new page: extend `base.html`, and only link the
page-scoped CSS files your new template actually needs — don't add new
rules to the global files unless the class is genuinely going to be used
across most of the site.

### Inline styles

Avoid inline `style="..."` attributes in template markup for anything
static. Use a CSS class instead — reach for the existing utility classes
(`.mt-1`, `.mt-1-5`, `.mt-2`, `.hidden`, `.text-center`, `.float-right` in
`base/base.css`) for simple one-offs, or a named class in the relevant
page/component CSS file for anything more specific. Inline styles that
are computed/toggled by JavaScript at runtime (e.g. a progress-bar width,
a `classList`-driven display toggle) are fine and expected — those are
not the target of this rule.

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