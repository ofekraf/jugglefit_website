# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

JuggleFit website: a Flask platform for juggling competitions that measure
skill through control over specific tricks. Scope on `main`: event pages,
generating/building/running practice routes, the Siteswap-X reference and
formatter, and a URL shortener used to share routes.

There is no login/accounts system, crowd-sourced trick submission, or
crowd-rating games on `main`. That system was removed while the site had
too few users to need it. It is fully preserved on the
`feature/crowd-contribution` git branch (with its own
`docs/crowd_backend.md`). Look there, not here, if it is ever needed again.
Some code comments still mention it (e.g. `suggest_trick` in the
`MAX_CONTENT_LENGTH` comment in `app.py`); those are leftovers.

## Hard rules - read before touching routes, URLs, or templates

1. **Never change these URL paths**: `/created_route`, `/run_route`,
   `/live_event` (defined in `app.py` via `_render_route_page`). They are
   embedded in QR codes and short links printed on physical event
   materials and shared externally. The `?route=<serialized>` query
   parameter format (JSON → zlib → base64, see `pylib/classes/route.py`
   `Route.serialize`/`deserialize`) must also stay backward compatible.
   `/build_route?route=...` is used for "Edit" links and should be
   treated with the same care. `/shortener/<code>` links are also shared
   externally.
2. Do not rename existing Flask endpoint names that templates reference
   via `url_for(...)` without also updating every template.
3. `hardcoded_database/events/upcoming_events.py` and
   `hardcoded_database/events/past_events/__init__.py` must stay
   **ordered by date** (explicit `# Keep ordered by date` comments) -
   insert new entries in chronological position rather than appending.
   `hardcoded_database/organization/team.py` has a `# Order for team page`
   comment - that order is intentional display order, not alphabetical.
4. Run `pytest` before committing changes to routes or templates
   (`tests/unit/` covers the route pages and live finals). For pages it
   does not cover, also run the app in-process and hit them:
   ```python
   import app as appmod
   client = appmod.app.test_client()
   print(client.get("/some/path").status_code)
   ```
   For anything touching `/created_route`, `/run_route`, `/live_event`,
   or `/build_route`, test with a real serialized `Route` rather than a
   made-up string - these pages redirect to `/build_route` on a missing
   or invalid `?route=` payload. Get one from `Route(...).serialize()`, or
   from a past event in `hardcoded_database/events/past_events/`.
   POSTs through the test client need a CSRF token (see Security below).
5. Do not invent Siteswap-X notation. Before generating or editing any
   `siteswap_x` value (trick CSVs, past events), read
   `docs/siteswap_x_agents.md`. If unsure, leave `siteswap_x` empty.

## Development Commands

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # check PORT in .env - it overrides the default 5001

python app.py                 # dev server, 0.0.0.0:$PORT, debug unless FLASK_ENV=production
flask run                     # alternative
gunicorn --bind 0.0.0.0:5001 --workers 2 --threads 4 --preload wsgi:app   # prod-style

docker-compose up --build                          # dev container
docker-compose -f docker-compose.prod.yml up -d    # prod container (named volume for SQLite)
```

Docker port mapping: the container listens on `$PORT` from `.env`. If
`.env` has `PORT=3333`, map `-p 5001:3333`, not `-p 5001:5001`.

### Tests

- `tests/unit/` - in-process app tests (route pages, live finals API/DB,
  CSV log). `tests/unit/conftest.py` points `SQLITE_DB_DIR` at a temp dir
  *before* importing `app` (the DB and trick registry initialize at
  import). Do not add a `tests/app/` package: it would shadow `app.py`.
- `tests/integration/` - `@pytest.mark.integration`, deselected by default
  (`pytest.ini`). Runs `scripts/simulate_final.py` against a local
  gunicorn (2 workers, like prod): one functional run plus load levels of
  50/150/300 polling viewers (~2 min total, no nginx cache). Also runs
  against a deployed server when `JUGGLEFIT_BASE_URL` and
  `JUGGLEFIT_ADMIN_PASSWORD` are set. The local fixture bypasses
  `HTTP(S)_PROXY` for loopback, and on macOS starts gunicorn without
  `--preload` (the system `libsqlite3.dylib` segfaults in forked workers
  after the parent used SQLite; Linux/prod is not affected). On a worker
  crash, the gunicorn log (with faulthandler tracebacks) is printed.
- `tests/docker/` - infrastructure tests (Dockerfile, compose files,
  production config, OCI deploy scripts). Tests that need a Docker daemon
  skip themselves when Docker is unavailable.

```bash
pytest                                   # unit + docker (fast)
pytest -m integration                    # simulated live final on local gunicorn
pytest tests/unit/test_finals_api.py::test_rename
```

No linter or formatter is configured for this repo.

### Scripts

- `scripts/convert_route.py` - take a serialized route (or a full URL
  containing one) and override fields such as prop or duration; prints
  the new serialized value / URL.
- `scripts/gen_past_event_diff.py` - list tricks used in past events that
  are missing from the master trick CSVs.
- `scripts/simulate_final.py` - run a fictional live final (test final
  on a `SIMULATION <id>` route, admin moves + N polling viewers) against
  any base URL; checks final state, CSV log and viewer delay. `--cleanup`
  deletes the test final.
- `python -m database.seed` - force re-seed of tricks from CSV (see the
  seeding caveat below).
- `python -m database.backup` / `python -m database.prune` - DB snapshot
  and URL-mapping retention sweep.

## Architecture

### Request flow

- `app.py` holds Flask config, the CSRF guard, the context processor
  (`cache_version` for static cache-busting, `current_year`), and all page
  routes. `wsgi.py` is the gunicorn entry point; it runs `init_db()` and
  prunes stale short URLs at startup.
- `blueprints/api.py` defines two blueprints: `api_bp` (`/api` prefix:
  `POST /api/fetch_tricks`, `POST /api/shorten_url`) and `shortener_bp`
  (top-level `GET /shortener/<code>`).
- `/generate_route` (POST) calls `RouteGenerator.generate(...)`, then
  redirects to `/created_route?route=<serialized>`. All route state lives
  in the URL - routes are never stored server-side, except as the long
  URL behind a short code.
- `/build_route` is client-side: the page fetches tricks from
  `/api/fetch_tricks` and assembles the route in JS
  (`static/js/route_helpers.js`).
- `blueprints/finals.py` - live finals, see below.

### Live finals (`/live_event`)

Server-side progress of a final, shown on the existing `/live_event` page.

- A final is tied to a route by `Route.key()` (sha256 of the canonical
  `to_dict()` JSON, not the base64 payload). QR codes printed before the
  event keep working: while a final is active for a route,
  `/created_route` shows a "The final is live" banner, and `/live_event`
  switches from the local in-memory tracker to the live grid
  (`static/js/live_final.js`, `static/css/pages/live-final.css`).
  `?final=<id>` shows a specific final, also after it ended.
- Organizers use the "Organizer: Run this live event" button (on
  `/created_route`, and on `/live_event` when no final is live; shared
  dialog `templates/macros/organizer_dialog.html` +
  `static/js/organizer_dialog.js`). The password (`ADMIN_PASSWORD`, env,
  read per request; unset = feature off, 404) goes to `POST /api/finals`:
  it creates a final, or **resumes** the one already live for the route
  (so a second device just enters the password again), and marks the
  session as admin. "Start over" (`POST /api/finals/<id>/restart`) ends
  the final and creates a new one with the same names. Creating also
  returns a secret `/final/admin/<id>/<token>` link (only the token hash
  is stored), used by `scripts/simulate_final.py`.
- Tables: `finals` (with `version`, bumped on every change, so
  `GET /api/finals/<id>/state?since=<v>` returns 204 when unchanged),
  `final_competitors` (`stage` 0..N-1 = trick, N = Finished),
  `final_events` (append-only log -> `log.csv`; take-backs stay visible;
  `client_at` = admin device time, used in the CSV because the admin
  phone queues moves while offline). `is_test` finals (simulation) are
  the only ones that can be deleted.
- Viewers poll every 3-4 s. In production, nginx caches the state
  endpoint for 1 s. `deploy/oci-ubuntu/nginx.conf` sizes per-IP limits
  for ~150 phones behind one venue Wi-Fi IP, serves `/static/` from
  `/opt/jugglefit/static/` on disk (not gunicorn), and returns 429 on a
  limit (`live_final.js` retries queued admin moves on 429). `update.sh`
  does not install nginx config - see the README there.

### Trick data: CSV → SQLite → in-process cache

1. Source of truth: `hardcoded_database/tricks/<prop.value>.csv`, one per
   `Prop` enum value (`balls`, `clubs`, `rings`, `club passing`,
   `balance`). Only `MAIN_PROPS` (balls, clubs, rings) show in the route
   generator/builder prop selectors.
2. `database/seed.py` imports each CSV into the SQLite `tricks` table.
3. `pylib/utils/trick_registry.py` runs the seed step at import time, then
   loads the table into `ALL_PROPS_TRICKS` / `ALL_PROPS_SETTINGS` /
   `ALL_PROPS_SETTINGS_JSON` (re-exported by `hardcoded_database.tricks`
   for backward compatibility). `PropSettings` (min/max props, etc.) is
   derived from the tricks, not configured.
4. `pylib/utils/filter_tricks.py` filters the cache for both the generator
   and `/api/fetch_tricks`.

**Seeding caveat**: the automatic seed only runs for a prop whose table
has zero rows. Edits to a CSV do **not** reach an existing database
(including the persistent `sqlite_data` volume in production) on restart.
`python -m database.seed` (force) only inserts rows that are new under
`UNIQUE(prop_type, props_count, name, siteswap_x)`: changed difficulty or
tags on an existing trick are not updated, and a renamed trick leaves its
old row behind. SQLite treats NULLs as distinct in UNIQUE constraints, so
a force re-seed can also duplicate tricks with an empty `name` or
`siteswap_x`. A clean rebuild of the `tricks` table is the reliable way
to apply CSV edits.

### Database (`database/db_manager.py`)

SQLite in WAL mode with `busy_timeout` (multi-worker gunicorn). Tables:
`tricks`, `url_mappings` (shortener, expires after
`URL_RETENTION_MONTHS` of inactivity), `meta` (bookkeeping), and the live
final tables `finals`, `final_competitors`, `final_events` (kept, never
pruned). The
`db_manager` singleton calls `init_db()` in `DBManager.__init__`, so the
schema exists on import - this matters because the trick registry reads
the DB at import time, before any `__main__` block.

### Static data (`hardcoded_database/`)

Events and team are Python modules, not DB rows. Each past event is its
own module under `past_events/Y<year>/`, built from `PastEvent`,
`RouteResult`, `Route`, and `Trick` objects, and must be imported and
listed in `past_events/__init__.py` (`FRONT_PAGE_PAST_EVENTS` or
`NON_FRONT_PAGE_PAST_EVENTS`).

### Security

- CSRF: session-token guard in `app._csrf_protect` for all
  POST/PUT/PATCH/DELETE. Forms use `{{ csrf_token() }}`; JS `fetch()`
  gets `X-CSRF-Token` auto-attached by a shim in `base.html`. Use the
  `csrf_exempt` decorator to opt a view out.
- `SECRET_KEY` is required when `FLASK_ENV=production` (the app raises on
  boot). In dev, an ephemeral key is generated, so sessions reset on
  restart.
- The URL shortener only accepts same-origin targets (`_is_same_origin`),
  checked on both create and redirect; 8 KB cap on long URLs.

## Frontend Architecture (templates + CSS)

### Template structure

- Every page template extends `templates/macros/base.html`, the single
  site-wide layout (`<head>`, navbar, `<main>`, footer, orientation-alert
  overlay, CSRF-fetch shim).
- The navbar is a separate partial, `templates/macros/navbar.html`,
  included by `base.html`. Edit the navbar there, not in `base.html`.
- Reusable form controls / widgets live under `templates/macros/` as
  Jinja `{% macro %}` definitions (imported via `{% from ... import ... %}`)
  or plain `{% include %}` partials (e.g. `route_display.html`,
  `trick_container.html`, `siteswap_x_toggle.html` are includes, not
  macros, despite living in the same folder - check which pattern a given
  file uses before copying it as a template).
- Standard child-template blocks: `{% block title %}`, `{% block head %}`
  (page-specific `<link>`/`<script>`/`<style>`; call `{{ super() }}` first
  if you need anything `base.html`'s own `head` block adds),
  `{% block content %}`, `{% block scripts %}`.
- `templates/siteswap_modifiers_printed_page.html` (served at
  `/siteswap_x/print`) is the one exception - a standalone full HTML
  document (no `{% extends %}`) used for a print popup. Leave it
  self-contained.

### CSS structure - do not recreate a monolithic stylesheet

CSS was split from one 3600+ line `static/css/styles.css` into small,
focused files under `static/css/{base,components,pages}/`. New styles go
into an existing file if they fit its scope, or a new small file if they
do not - never back into one giant file.

**Global** (linked unconditionally in `macros/base.html`):
- `base/variables.css` (CSS custom properties), `base/base.css` (resets +
  utilities `.hidden`, `.text-center`, `.float-right`,
  `.mt-1`/`.mt-1-5`/`.mt-2`), `base/layout.css`, `base/animations.css`
- `components/navbar.css`, `footer.css`, `buttons.css`, `forms.css`,
  `orientation-alert.css`, `toast.css`, `print.css`
- `components/trick-display.css`, `prop-selection.css`, `siteswap-x.css` -
  global even though their static markup appears on few templates,
  because `static/js/route_helpers.js` and `static/js/siteswap_x.js` can
  inject `.trick-*`/`.prop-*`/`.siteswap-x-*` elements into almost any
  route-related page.

**Page-scoped** (linked via `{% block head %}` only where needed):
- `pages/home.css` + `components/carousel.css` → `index.html`,
  `host_event.html`
- `pages/route-pages.css` → pages using `.route-page`/`.route-header`/
  `.route-form` (generate_route, build_route, created_route)
- `components/custom-trick-form.css` → `build_route.html` only
- `components/tag-categories.css` → build_route, generate_route
- `components/countdown-timer.css` → created_route, live_event
- `pages/live-final.css` → live_event; `components/live-final-banner.css`
  → created_route (only while a final is live)
- `components/organizer-dialog.css` → created_route, live_event
- `pages/donate.css`, `pages/past-events.css`, `pages/live-event.css`,
  `pages/siteswap-x.css`, `pages/siteswap-x-formatter.css` → one page each
- `static/css/run_route.css` → `run_route.html` only

When adding a page: extend `base.html` and link only the page-scoped CSS
it needs. Do not add rules to the global files unless the class is used
across most of the site.

### Inline styles

Avoid static inline `style="..."` attributes in templates. Use the
utility classes in `base/base.css` for one-offs, or a named class in the
relevant page/component CSS file. Inline styles computed or toggled by
JavaScript at runtime (progress-bar widths, display toggles) are fine.

## Deployment

- Production runs on an OCI Ubuntu host with Docker Compose
  (`docker-compose.prod.yml`) behind nginx. Setup and details are in
  `deploy/oci-ubuntu/README.md`.
- There is no CI/CD. GitHub Actions was removed (commit `6e51ffe`).
  Deploy is manual: `sudo bash /opt/jugglefit/deploy/oci-ubuntu/update.sh`
  on the host (DB snapshot → `git pull --ff-only origin main` → rebuild
  → wait for `/health`). It prints a rollback command on failure.
- Backups: `deploy/oci-ubuntu/backup.sh` runs nightly via cron
  (`database.backup` then `database.prune`, rclone for off-box copies).

## Local clutter

The untracked directories `classes/`, `py_lib/`, `route_generator/` (only
`__pycache__` leftovers from an older layout) and the git-ignored `data/`
are not part of the app. The real code is under `pylib/`.
