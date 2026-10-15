"""
Trick feedback from generated routes (Dislike / Too hard / Too easy).

Shown only on ``/created_route`` for routes this browser created with the
route generator (``/generate_route``). The generator marks the route in the
session, so the URL (shared links, printed QR codes) stays unchanged and
routes opened from a link never show the buttons.

Votes are stored raw in the ``trick_feedback`` table for later **manual**
review (``python scripts/trick_feedback_report.py``). Nothing reads them
automatically: trick difficulties live in hardcoded_database/tricks/*.csv
and are only changed by hand.
"""
from __future__ import annotations

import hashlib
import json
import secrets
import time
from typing import Optional

from flask import Blueprint, current_app, jsonify, request, session

from database.db_manager import db_manager
from pylib.classes.route import Route

trick_feedback_bp = Blueprint("trick_feedback", __name__, url_prefix="/api")

VOTES = ("dislike", "too_hard", "too_easy")
_GENERATED_KEY = "generated_routes"
_VOTER_KEY = "feedback_voter_id"
_MAX_GENERATED_IN_SESSION = 20


def get_voter_id() -> str:
    """Anonymous per-browser id (session cookie), so a re-vote replaces the
    previous vote instead of counting twice."""
    voter = session.get(_VOTER_KEY)
    if not voter:
        voter = secrets.token_urlsafe(12)
        session[_VOTER_KEY] = voter
        session.permanent = True
    return voter


def feedback_route_key(route: Route) -> str:
    """Stable id of the route content. Unlike ``Route.key()`` it sorts each
    trick's tags: tags are a set, so their order can change after a
    serialize/deserialize round trip (and between processes)."""
    data = route.to_dict()
    for trick in data["tricks"]:
        trick["tags"] = sorted(trick["tags"])
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def remember_generated_route(route: Route) -> None:
    key = feedback_route_key(route)
    keys = [k for k in session.get(_GENERATED_KEY, []) if k != key]
    keys.append(key)
    session[_GENERATED_KEY] = keys[-_MAX_GENERATED_IN_SESSION:]


def is_generated_route(route: Route) -> bool:
    return feedback_route_key(route) in session.get(_GENERATED_KEY, [])


@trick_feedback_bp.route("/trick_feedback", methods=["POST"])
def trick_feedback():
    data = request.get_json(silent=True) or {}
    try:
        route = Route.deserialize(str(data.get("route") or ""))
    except ValueError:
        return jsonify({"error": "invalid route"}), 400
    if not is_generated_route(route):
        return jsonify({"error": "feedback is only collected for generated routes"}), 403

    try:
        index = int(data.get("trick_index"))
    except (TypeError, ValueError):
        return jsonify({"error": "trick_index is required"}), 400
    if not 0 <= index < len(route.tricks):
        return jsonify({"error": "trick_index out of range"}), 400

    vote: Optional[str] = data.get("vote")
    if vote is not None and vote not in VOTES:
        return jsonify({"error": f"vote must be one of {list(VOTES)} or null"}), 400

    trick = route.tricks[index]
    try:
        db_manager.set_trick_feedback(
            voter_id=get_voter_id(),
            route_key=feedback_route_key(route),
            trick_index=index,
            prop=route.prop.value,
            props_count=trick.props_count,
            trick_name=trick.name,
            siteswap_x=trick.siteswap_x,
            difficulty=trick.difficulty if trick.difficulty != -1 else None,
            vote=vote,
            now_ms=int(time.time() * 1000),
        )
    except Exception as e:
        current_app.logger.exception("trick_feedback: %s", e)
        return jsonify({"error": "could not save feedback"}), 500
    return jsonify({"ok": True, "trick_index": index, "vote": vote})
