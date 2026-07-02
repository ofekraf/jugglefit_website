"""
JuggleFit Flask application factory + public page routes.

Feature areas live in :mod:`blueprints`:
  - :mod:`blueprints.auth`  – user login/registration
  - :mod:`blueprints.games` – crowd-rating games + game API
  - :mod:`blueprints.api`   – public JSON API + URL shortener
  - :mod:`blueprints.admin` – admin & super-admin console
"""
from __future__ import annotations

import csv
import io
import logging
import os
import secrets
import time
from datetime import timedelta
from urllib.parse import unquote

from dotenv import load_dotenv
from flask import (
    Flask, Response, flash, jsonify, redirect, render_template, request,
    session, url_for,
)

from database.db_manager import db_manager
from hardcoded_database.consts import URL_RETENTION_MONTHS
from hardcoded_database.events.past_events import ALL_PAST_EVENTS, FRONT_PAGE_PAST_EVENTS
from hardcoded_database.events.upcoming_events import UPCOMING_EVENTS
from hardcoded_database.organization.team import TEAM
from hardcoded_database.tricks import ALL_PROPS_SETTINGS_JSON
from pylib.auth import current_user as _current_user
from pylib.classes.prop import MAIN_PROPS, Prop
from pylib.classes.route import Route
from pylib.classes.siteswap_x_modifiers import CatchModifier, ThrowModifier
from pylib.classes.tag import TAG_CATEGORY_MAP_JSON, Tag, TagCategory
from pylib.configuration.consts import LEADERBOARD_PERIODS, USER_SESSION_DAYS
from pylib.rating.leaderboard import KIND_META as LB_META, KINDS as LB_KINDS
from pylib.route_generator.exceptions import NotEnoughTricksFoundException
from pylib.route_generator.route_generator import RouteGenerator

from blueprints.admin import admin_bp, super_admin_session_valid
from blueprints.api import api_bp, shortener_bp
from blueprints.auth import auth_bp
from blueprints.games import games_api, games_bp


# ---------------------------------------------------------------------------
# app + config
# ---------------------------------------------------------------------------
load_dotenv()

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

IS_PRODUCTION = os.environ.get("FLASK_ENV") == "production"

app = Flask(__name__)

# --- SECRET_KEY -----------------------------------------------------------
# In production, refuse to boot without a real secret. In development, generate
# a random per-process key so cookies/tokens are still unforgeable but don't
# survive restarts (acceptable for dev).
_secret = os.environ.get("SECRET_KEY")
if not _secret:
    if IS_PRODUCTION:
        raise RuntimeError(
            "SECRET_KEY is not set. Refusing to start in production. "
            "Set SECRET_KEY in the environment / .env file."
        )
    _secret = secrets.token_hex(32)
    logging.getLogger(__name__).warning(
        "SECRET_KEY not set; using an ephemeral dev key (sessions reset on restart)."
    )
app.secret_key = _secret

# --- Session cookie hardening + request limits ---------------------------
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=IS_PRODUCTION,
    PERMANENT_SESSION_LIFETIME=timedelta(days=USER_SESSION_DAYS),
    # Cap request bodies. Largest legitimate POST is a serialized route in
    # /api/shorten_url or a suggest_trick payload — both well under 64 KB.
    # Prevents a single oversized body OOM-ing a mem_limit=700m worker.
    MAX_CONTENT_LENGTH=64 * 1024,
)
app.permanent_session_lifetime = timedelta(days=USER_SESSION_DAYS)

# Cache-busting version: changes on each app restart so browsers fetch fresh
# static files.
APP_START_TIME = str(int(time.time()))


# --- CSRF (session token, no external deps) -------------------------------
_CSRF_SESSION_KEY = "_csrf_token"
_CSRF_EXEMPT: set = set()


def generate_csrf_token() -> str:
    tok = session.get(_CSRF_SESSION_KEY)
    if not tok:
        tok = secrets.token_urlsafe(32)
        session[_CSRF_SESSION_KEY] = tok
    return tok


def csrf_exempt(view):
    """Decorator: skip CSRF validation for this view."""
    _CSRF_EXEMPT.add(view)
    return view


@app.before_request
def _csrf_protect():
    if request.method not in ("POST", "PUT", "PATCH", "DELETE"):
        return None
    view = app.view_functions.get(request.endpoint)
    if view in _CSRF_EXEMPT:
        return None
    sent = (request.headers.get("X-CSRF-Token")
            or request.form.get("_csrf_token")
            or (request.get_json(silent=True) or {}).get("_csrf_token"))
    expected = session.get(_CSRF_SESSION_KEY)
    if not expected or not sent or not secrets.compare_digest(sent, expected):
        if request.is_json or request.accept_mimetypes.best == "application/json":
            return jsonify({"error": "CSRF token missing or invalid"}), 403
        flash("Your session expired. Please try again.", "error")
        return redirect(request.referrer or url_for("home"))
    return None


app.jinja_env.globals["csrf_token"] = generate_csrf_token


@app.context_processor
def inject_globals():
    return {
        "cache_version": APP_START_TIME,
        "current_user": _current_user(),
        "is_super_admin": super_admin_session_valid(),
    }


# --- blueprints -----------------------------------------------------------
app.register_blueprint(auth_bp)
app.register_blueprint(games_bp)
app.register_blueprint(games_api)
app.register_blueprint(api_bp)
app.register_blueprint(shortener_bp)
app.register_blueprint(admin_bp)

# Legacy endpoint aliases so existing url_for('admin_*') / templates keep
# working after the admin blueprint extraction. Each alias is a real URL
# rule that shares the blueprint's view function.
_ADMIN_ALIASES = {
    "admin_login": ("/admin/login", "admin.login", ("GET", "POST")),
    "admin_logout": ("/admin/logout", "admin.logout", ("GET",)),
    "admin_crowd": ("/admin/crowd", "admin.crowd", ("GET",)),
    "admin_users": ("/admin/users", "admin.users", ("GET",)),
}
for _old, (_rule, _new, _methods) in _ADMIN_ALIASES.items():
    app.add_url_rule(_rule, endpoint=_old,
                     view_func=app.view_functions[_new], methods=_methods)


# ---------------------------------------------------------------------------
# health / readiness
# ---------------------------------------------------------------------------
@app.route("/health")
def health_check():
    """Health check endpoint for container health checks."""
    return {"status": "healthy", "message": "Application is running"}, 200


@app.route("/ready")
def readiness_check():
    """Readiness check endpoint for load balancers."""
    return {"status": "ready", "message": "Application is ready to serve requests"}, 200


# ---------------------------------------------------------------------------
# public pages
# ---------------------------------------------------------------------------
@app.route("/")
def home():
    return render_template("index.html",
                           upcoming_events=UPCOMING_EVENTS,
                           last_events=FRONT_PAGE_PAST_EVENTS)


@app.route("/past_events")
def past_events():
    return render_template("past_events.html", past_events=ALL_PAST_EVENTS)


@app.route("/host_event")
def host_event():
    return render_template("host_event.html", team=TEAM)


@app.route("/event_checklist")
def equipment_list():
    return render_template("event_checklist.html")


@app.route("/donate")
def donate():
    return render_template("donate.html")


@app.route("/contribute/software")
def software_contribution():
    return render_template("software_contribution.html")


@app.route("/leaderboards")
def leaderboard():
    return render_template("leaderboard.html",
                           kinds=LB_KINDS,
                           kind_meta=LB_META,
                           periods=list(LEADERBOARD_PERIODS.keys()))


@app.route("/siteswap_x")
def siteswap_x():
    return render_template("siteswap_x.html",
                           ThrowModifier=ThrowModifier, CatchModifier=CatchModifier)


@app.route("/siteswap_x/print")
def siteswap_x_print():
    return render_template("siteswap_modifiers_printed_page.html",
                           ThrowModifier=ThrowModifier, CatchModifier=CatchModifier)


@app.route("/siteswap_x/formatter")
def siteswap_x_formatter():
    return render_template("siteswap_x_formatter.html")


@app.route("/verify")
def verify_game():
    """Legacy two-round verify game — superseded by /contribute/games/harder."""
    return redirect(url_for("games.hub"), code=301)


# ---------------------------------------------------------------------------
# route builder / generator
# ---------------------------------------------------------------------------
@app.route("/generate_route", methods=["GET", "POST"])
def generate_route():
    if request.method == "GET":
        return render_template("generate_route.html",
                               current_page="generate_route",
                               tag_category_map=TAG_CATEGORY_MAP_JSON,
                               tag_categories=list(TagCategory),
                               props_settings=ALL_PROPS_SETTINGS_JSON,
                               main_props=MAIN_PROPS)

    route_name = request.form["route_name"]
    prop = request.form["prop"]
    min_props = int(request.form["min_props"])
    max_props = int(request.form["max_props"])
    min_difficulty = int(request.form["min_difficulty"])
    max_difficulty = int(request.form["max_difficulty"])
    route_length = int(request.form["route_length"])
    route_duration_seconds = int(request.form["route_duration"]) * 60
    max_throw_str = request.form.get("max_throw", "").strip()
    max_throw = int(max_throw_str) if max_throw_str else None
    exclude_tags = {Tag.get_key_by_value(t) for t in request.form.getlist("exclude_tags")
                    if Tag.get_key_by_value(t) is not None}

    try:
        route = RouteGenerator.generate(
            prop=Prop.get_key_by_value(prop),
            min_props=min_props,
            max_props=max_props,
            min_difficulty=min_difficulty,
            max_difficulty=max_difficulty,
            route_length=route_length,
            exclude_tags=exclude_tags,
            name=route_name,
            duration_seconds=route_duration_seconds,
            max_throw=max_throw,
        )
        return redirect(url_for("created_route", route=route.serialize()))
    except NotEnoughTricksFoundException:
        return '<p class="no-tricks">Not enough tricks in database. Try adjusting your criteria.</p>'


@app.route("/build_route")
def build_route():
    route_param = request.args.get("route", type=str)
    initial_route = None
    if route_param:
        try:
            initial_route = Route.deserialize(unquote(route_param)).to_dict()
        except Exception as e:
            flash(f"Error loading route: {e}", "error")
            return redirect(url_for("build_route"))

    return render_template("build_route.html",
                           tag_category_map=TAG_CATEGORY_MAP_JSON,
                           tag_categories=list(TagCategory),
                           props_settings=ALL_PROPS_SETTINGS_JSON,
                           initial_route=initial_route,
                           main_props=MAIN_PROPS)


def _render_route_page(template: str):
    """Shared loader for created_route / live_event / run_route."""
    route_param = request.args.get("route", type=str)
    if not route_param:
        return redirect(url_for("build_route"))
    try:
        route = Route.deserialize(route_param)
        return render_template(template, route=route)
    except Exception as e:
        flash(f"Error loading route: {e}")
        return redirect(url_for("build_route"))


@app.route("/created_route")
def created_route():
    return _render_route_page("created_route.html")


@app.route("/live_event")
def live_event():
    return _render_route_page("live_event.html")


@app.route("/run_route")
def run_route():
    return _render_route_page("run_route.html")


# ---------------------------------------------------------------------------
# contribute
# ---------------------------------------------------------------------------
@app.route("/contribute/add_tricks")
def add_tricks():
    db_connected = False
    try:
        conn = db_manager.connection
        if conn:
            db_connected = True
            conn.close()
    except Exception:
        pass

    return render_template("add_tricks.html",
                           props_settings=ALL_PROPS_SETTINGS_JSON,
                           main_props=MAIN_PROPS,
                           MAX_TRICK_PROPS_COUNT=13,
                           db_connected=db_connected)


@app.route("/contribute/download_tricks_csv/<prop_type>")
def download_tricks_csv(prop_type):
    """Stream the *stable* (master) tricks for a prop as CSV, generated
    live from SQLite — includes crowd-promoted tricks, not just the seed."""
    try:
        Prop.get_key_by_value(prop_type)
    except Exception:
        return "Invalid prop", 404
    cols = ["name", "props_count", "difficulty", "tags", "comment", "max_throw", "siteswap_x"]
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=cols)
    w.writeheader()
    for r in db_manager.get_tricks(prop_type):
        w.writerow({k: ("" if r.get(k) is None else r.get(k)) for k in cols})
    safe_name = prop_type.replace(" ", "_").replace("+", "_")
    return Response(buf.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": f"attachment; filename={safe_name}_tricks.csv"})


# ---------------------------------------------------------------------------
# entrypoint (dev only — production uses gunicorn via wsgi.py)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        db_manager.init_db()
        db_manager.delete_inactive_urls(URL_RETENTION_MONTHS)
    except Exception as e:
        app.logger.warning("Database initialization/migration failed: %s", e)

    port = int(os.environ.get("PORT", 5001))
    # Never enable the interactive debugger in production.
    app.run(host="0.0.0.0", port=port, debug=not IS_PRODUCTION)
