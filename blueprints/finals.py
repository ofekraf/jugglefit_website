"""
Live finals: server-side competitor progress for ``/live_event``.

A final belongs to a route by ``Route.key()`` (a hash of the route content),
so QR codes printed before the final still lead to it: ``/created_route``
shows a banner while a final is active for that route.

Auth: ``ADMIN_PASSWORD`` (env). Entering it on a route (the "Organizer:
Run this live event" dialog) creates a final, or resumes the one already
live for that route, and marks the browser session as admin for it.
Creating also returns a secret admin link for that final only (used by
scripts/simulate_final.py). Everyone else gets read-only state.
"""
from __future__ import annotations

import hashlib
import os
import secrets
import time
from typing import Any, Dict, List, Optional

from flask import (
    Blueprint, Response, abort, jsonify, redirect, request, session, url_for,
)

from database.db_manager import db_manager
from pylib.classes.route import Route
from pylib.utils.final_log import build_log_rows, finish_times, to_csv


finals_api_bp = Blueprint("finals_api", __name__, url_prefix="/api/finals")
# The admin link is opened directly (e.g. by scanning a QR code on a phone),
# so it lives outside /api.
finals_bp = Blueprint("finals", __name__)

MAX_COMPETITORS = 30
MAX_NAME_LENGTH = 50
MAX_ROUTE_PAYLOAD = 8 * 1024
# Admin sessions remembered per browser (most recent kept).
MAX_ADMIN_FINALS_IN_SESSION = 10
# Accept the admin device clock only if it is this close to server time.
MAX_CLIENT_CLOCK_SKEW_MS = 24 * 60 * 60 * 1000
_SESSION_KEY = "final_admin"


def _now_ms() -> int:
    return int(time.time() * 1000)


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _client_at(data: Dict[str, Any]) -> Optional[int]:
    value = data.get("client_at")
    if not isinstance(value, int) or isinstance(value, bool):
        return None
    if abs(value - _now_ms()) > MAX_CLIENT_CLOCK_SKEW_MS:
        return None
    return value


def is_final_admin(final_id: str) -> bool:
    return final_id in session.get(_SESSION_KEY, [])


def _load_final(final_id: str) -> Dict[str, Any]:
    final = db_manager.get_final(final_id)
    if final is None:
        abort(404)
    return final


def _load_admin_final(final_id: str, require_active: bool = True):
    """Return (final, error_response). error_response is None on success."""
    final = _load_final(final_id)
    if not is_final_admin(final_id):
        return final, (jsonify({"error": "Admin access required"}), 403)
    if require_active and final["status"] != "active":
        return final, (jsonify({"error": "This final has ended"}), 409)
    return final, None


def _route_length(final: Dict[str, Any]) -> int:
    return len(Route.deserialize(final["route_payload"]).tricks)


def _grant_admin(final_id: str) -> None:
    admin_finals = [f for f in session.get(_SESSION_KEY, []) if f != final_id]
    admin_finals.append(final_id)
    session[_SESSION_KEY] = admin_finals[-MAX_ADMIN_FINALS_IN_SESSION:]


def _live_url(final_id: str, route_payload: str) -> str:
    return url_for("live_event", route=route_payload, final=final_id)


def _new_final(route_key: str, route_payload: str, names: List[str], is_test: bool):
    """Create a final (ending any active one for the route), make this
    session its admin, and return the JSON response."""
    final_id = secrets.token_urlsafe(9)
    token = secrets.token_urlsafe(24)
    db_manager.create_final(
        final_id=final_id,
        route_key=route_key,
        route_payload=route_payload,
        admin_token_hash=_hash_token(token),
        names=names,
        now_ms=_now_ms(),
        is_test=is_test,
    )
    _grant_admin(final_id)
    return jsonify({
        "final_id": final_id,
        "resumed": False,
        "live_url": _live_url(final_id, route_payload),
        "admin_url": url_for("finals.admin_login", final_id=final_id, token=token, _external=True),
    }), 201


# ---------------------------------------------------------------------------
# create + admin login
# ---------------------------------------------------------------------------
@finals_api_bp.route("", methods=["POST"])
def create_final():
    admin_password = os.environ.get("ADMIN_PASSWORD")
    if not admin_password:
        abort(404)
    data = request.get_json(silent=True) or {}

    password = data.get("password")
    if not isinstance(password, str) or not secrets.compare_digest(
            password.encode("utf-8"), admin_password.encode("utf-8")):
        return jsonify({"error": "Wrong password"}), 403

    payload = data.get("route")
    if not isinstance(payload, str) or not payload or len(payload) > MAX_ROUTE_PAYLOAD:
        return jsonify({"error": "route is required"}), 400
    try:
        route = Route.deserialize(payload)
    except ValueError:
        return jsonify({"error": "Invalid route"}), 400

    # A final is already live for this route: the password resumes it.
    active = db_manager.get_active_final_by_route_key(route.key())
    if active:
        _grant_admin(active["id"])
        final = db_manager.get_final(active["id"])
        return jsonify({"final_id": active["id"], "resumed": True,
                        "live_url": _live_url(active["id"], final["route_payload"])})

    count = data.get("competitor_count")
    if not isinstance(count, int) or isinstance(count, bool) or not 1 <= count <= MAX_COMPETITORS:
        return jsonify({"error": f"competitor_count must be 1-{MAX_COMPETITORS}"}), 400
    given = data.get("names") or []
    if not isinstance(given, list):
        return jsonify({"error": "names must be a list"}), 400
    names = []
    for i in range(count):
        name = given[i].strip()[:MAX_NAME_LENGTH] if i < len(given) and isinstance(given[i], str) else ""
        names.append(name or f"Competitor {i + 1}")

    return _new_final(route.key(), payload, names, bool(data.get("test")))


@finals_bp.route("/final/admin/<final_id>/<token>")
def admin_login(final_id: str, token: str):
    final = db_manager.get_final(final_id)
    if final is None or not secrets.compare_digest(_hash_token(token), final["admin_token_hash"]):
        abort(404)
    _grant_admin(final_id)
    # Redirect so the token does not stay in the address bar.
    return redirect(_live_url(final_id, final["route_payload"]))


# ---------------------------------------------------------------------------
# public state (polled by every viewer; cached ~1s by nginx)
# ---------------------------------------------------------------------------
@finals_api_bp.route("/<final_id>/state")
def final_state(final_id: str):
    final = _load_final(final_id)
    since = request.args.get("since", type=int)
    if since is not None and since == final["version"]:
        return Response(status=204)

    route_length = _route_length(final)
    finished = finish_times(db_manager.get_final_events(final_id), route_length)
    competitors = [
        {**c, "finished_at": finished.get(c["id"]) if c["stage"] >= route_length else None}
        for c in db_manager.get_final_competitors(final_id)
    ]
    return jsonify({
        "id": final["id"],
        "status": final["status"],
        "version": final["version"],
        "started_at": final["started_at"],
        "ended_at": final["ended_at"],
        "route_length": route_length,
        "server_now": _now_ms(),
        "competitors": competitors,
    })


# ---------------------------------------------------------------------------
# admin actions
# ---------------------------------------------------------------------------
def _find_competitor(final_id: str, competitor_id: Any) -> Optional[Dict[str, Any]]:
    if not isinstance(competitor_id, int) or isinstance(competitor_id, bool):
        return None
    for competitor in db_manager.get_final_competitors(final_id):
        if competitor["id"] == competitor_id:
            return competitor
    return None


@finals_api_bp.route("/<final_id>/start", methods=["POST"])
def start_final(final_id: str):
    final, error = _load_admin_final(final_id)
    if error:
        return error
    data = request.get_json(silent=True) or {}
    competitor_id = data.get("competitor_id")
    if competitor_id is not None and _find_competitor(final_id, competitor_id) is None:
        return jsonify({"error": "Unknown competitor"}), 400
    version = db_manager.start_final(final_id, _now_ms(), _client_at(data), competitor_id)
    return jsonify({"version": version})


@finals_api_bp.route("/<final_id>/move", methods=["POST"])
def move_competitor(final_id: str):
    final, error = _load_admin_final(final_id)
    if error:
        return error
    data = request.get_json(silent=True) or {}
    competitor = _find_competitor(final_id, data.get("competitor_id"))
    if competitor is None:
        return jsonify({"error": "Unknown competitor"}), 400
    to_stage = data.get("to_stage")
    route_length = _route_length(final)
    if not isinstance(to_stage, int) or isinstance(to_stage, bool) or not 0 <= to_stage <= route_length:
        return jsonify({"error": f"to_stage must be 0-{route_length}"}), 400
    if competitor["started_at"] is None:
        return jsonify({"error": "Start this competitor first"}), 409
    version = db_manager.move_competitor(final_id, competitor["id"], to_stage,
                                         _now_ms(), _client_at(data))
    return jsonify({"version": version})


@finals_api_bp.route("/<final_id>/rename", methods=["POST"])
def rename_competitor(final_id: str):
    final, error = _load_admin_final(final_id)
    if error:
        return error
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    if not isinstance(name, str) or not name.strip():
        return jsonify({"error": "name is required"}), 400
    competitor = _find_competitor(final_id, data.get("competitor_id"))
    if competitor is None:
        return jsonify({"error": "Unknown competitor"}), 400
    db_manager.rename_competitor(final_id, competitor["id"], name.strip()[:MAX_NAME_LENGTH])
    return jsonify({"ok": True})


@finals_api_bp.route("/<final_id>/end", methods=["POST"])
def end_final(final_id: str):
    final, error = _load_admin_final(final_id)
    if error:
        return error
    db_manager.end_final(final_id, _now_ms())
    return jsonify({"ok": True})


@finals_api_bp.route("/<final_id>/restart", methods=["POST"])
def restart_final(final_id: str):
    """Start over: end this final (its log is kept) and create a new one for
    the same route, with the same competitor names, all back at trick 1."""
    final, error = _load_admin_final(final_id, require_active=False)
    if error:
        return error
    names = [c["name"] for c in db_manager.get_final_competitors(final_id)]
    return _new_final(final["route_key"], final["route_payload"], names, bool(final["is_test"]))


@finals_api_bp.route("/<final_id>/delete", methods=["POST"])
def delete_final(final_id: str):
    final, error = _load_admin_final(final_id, require_active=False)
    if error:
        return error
    if not final["is_test"]:
        return jsonify({"error": "Only test finals can be deleted"}), 403
    db_manager.delete_test_final(final_id)
    return jsonify({"ok": True})


@finals_api_bp.route("/<final_id>/log.csv")
def final_log(final_id: str):
    final, error = _load_admin_final(final_id, require_active=False)
    if error:
        return error
    route = Route.deserialize(final["route_payload"])
    rows = build_log_rows(
        db_manager.get_final_events(final_id),
        db_manager.get_final_competitors(final_id),
        [trick.name or trick.siteswap_x or "" for trick in route.tricks],
    )
    filename = f"final-{final_id}.csv"
    return Response(to_csv(rows), mimetype="text/csv",
                    headers={"Content-Disposition": f'attachment; filename="{filename}"'})
