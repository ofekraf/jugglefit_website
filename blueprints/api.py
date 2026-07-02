"""
Public JSON API (``/api/*``) — trick lookup, suggestion intake, captcha,
URL shortener. Game and admin APIs live in their own blueprints.
"""
from __future__ import annotations

import random
import string
from urllib.parse import urlsplit

from flask import (
    Blueprint, current_app, jsonify, redirect, request, session, url_for, flash,
)

from database.db_manager import db_manager
from hardcoded_database.captcha import CAPTCHA_QUESTIONS, is_correct_answer
from hardcoded_database.tricks import ALL_PROPS_SETTINGS
from pylib.auth import current_user, get_or_create_anon_id
from pylib.classes.prop import Prop
from pylib.classes.tag import Tag
from pylib.configuration.consts import (
    MIN_TRICK_DIFFICULTY, MAX_TRICK_DIFFICULTY,
    MAX_TRICK_NAME_LENGTH, MAX_SITESWAP_X_LENGTH, MAX_COMMENT_LENGTH,
)
from pylib.rating.intake import submit_and_intake
from pylib.rating.leaderboard import get_board
from pylib.utils.filter_tricks import filter_tricks


api_bp = Blueprint("api", __name__, url_prefix="/api")
# Shortener redirect must be top-level (/shortener/<code>), so it goes on a
# second blueprint without a prefix.
shortener_bp = Blueprint("shortener", __name__)

# Serialized routes (the only legitimate long_url payload) compress to
# well under this. Caps storage bloat in the url_mappings table.
_MAX_LONG_URL = 8 * 1024


# ---------------------------------------------------------------------------
# tricks
# ---------------------------------------------------------------------------
@api_bp.route("/fetch_tricks", methods=["POST"])
def fetch_tricks():
    try:
        data = request.get_json() or {}
        prop_type_value = data.get("prop_type")
        try:
            prop_type = Prop.get_key_by_value(prop_type_value)
        except Exception:
            allowed = [v.value for v in Prop]
            msg = f"Invalid prop_type '{prop_type_value}'. Allowed values: {allowed}"
            current_app.logger.error(msg)
            return jsonify({"error": msg}), 400
        min_props = int(data.get("min_props", ALL_PROPS_SETTINGS[prop_type].min_props))
        max_props = int(data.get("max_props", ALL_PROPS_SETTINGS[prop_type].max_props))
        min_difficulty = int(data.get("min_difficulty", MIN_TRICK_DIFFICULTY))
        max_difficulty = int(data.get("max_difficulty", MAX_TRICK_DIFFICULTY))
        exclude_tags = data.get("exclude_tags", [])
        limit = int(data.get("limit", 0))
        max_throw = int(data.get("max_throw")) if data.get("max_throw") is not None else None

        exclude_tags_set = {Tag.get_key_by_value(tag) for tag in exclude_tags}

        filtered = filter_tricks(
            prop=prop_type,
            min_props=min_props,
            max_props=max_props,
            min_difficulty=min_difficulty,
            max_difficulty=max_difficulty,
            limit=limit if limit > 0 else None,
            exclude_tags=exclude_tags_set,
            max_throw=max_throw,
        )
        return jsonify([t.to_dict() for t in filtered])
    except Exception as e:
        current_app.logger.exception("Error in /api/fetch_tricks: %s", e)
        return jsonify({"error": str(e)}), 400


@api_bp.route("/trick_exists", methods=["POST"])
def trick_exists():
    """Lightweight dedup check used by build_route before adding a custom
    trick. Checks master tricks AND active candidates."""
    data = request.get_json(silent=True) or {}
    prop_type = data.get("prop_type")
    name = (data.get("name") or "").strip() or None
    siteswap_x = (data.get("siteswap_x") or "").strip() or None
    try:
        Prop.get_key_by_value(prop_type)
        props_count = int(data.get("props_count"))
    except Exception:
        return jsonify({"error": "invalid prop/props_count"}), 400
    if not name and not siteswap_x:
        return jsonify({"exists": False})
    m = db_manager.find_master_match(prop_type=prop_type, props_count=props_count,
                                     name=name, siteswap_x=siteswap_x)
    if m:
        return jsonify({"exists": True, "where": "master", "match": m})
    c = db_manager.find_candidate_match(prop_type=prop_type, props_count=props_count,
                                        name=name, siteswap_x=siteswap_x)
    if c:
        return jsonify({"exists": True, "where": "candidate",
                        "match": {k: c.get(k) for k in
                                  ("id", "props_count", "name", "siteswap_x", "comment")}})
    return jsonify({"exists": False})


# ---------------------------------------------------------------------------
# captcha + suggestion intake
# ---------------------------------------------------------------------------
@api_bp.route("/get_captcha", methods=["GET"])
def get_captcha():
    try:
        session.permanent = True
        idx = random.randint(0, len(CAPTCHA_QUESTIONS) - 1)
        session["captcha_index"] = idx
        return jsonify({"question": CAPTCHA_QUESTIONS[idx]["question"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/suggest_trick", methods=["POST"])
def suggest_trick():
    try:
        data = request.get_json() or {}
        prop_type = data.get("prop_type")
        name = (data.get("name") or "").strip() or None
        siteswap_x = (data.get("siteswap_x") or "").strip() or None
        comment = (data.get("comment") or "").strip() or None
        captcha_answer = data.get("captcha_answer")

        try:
            Prop.get_key_by_value(prop_type)
        except Exception:
            return jsonify({"error": "Prop type is required"}), 400
        try:
            props_count = int(data.get("props_count"))
        except (TypeError, ValueError):
            return jsonify({"error": "props_count is required"}), 400
        if not name and not siteswap_x:
            return jsonify({"error": "Either name or siteswap_x is required"}), 400
        if name and len(name) > MAX_TRICK_NAME_LENGTH:
            return jsonify({"error": f"Name too long (max {MAX_TRICK_NAME_LENGTH})."}), 400
        if siteswap_x and len(siteswap_x) > MAX_SITESWAP_X_LENGTH:
            return jsonify({"error": f"Siteswap-X too long (max {MAX_SITESWAP_X_LENGTH})."}), 400
        if comment and len(comment) > MAX_COMMENT_LENGTH:
            return jsonify({"error": f"Comment too long (max {MAX_COMMENT_LENGTH})."}), 400
        if not (1 <= props_count <= 13):
            return jsonify({"error": "props_count out of range."}), 400

        user = current_user()
        # Captcha required only for anonymous submissions that haven't solved one yet.
        if user is None and not session.get("captcha_solved"):
            idx = session.get("captcha_index")
            if idx is None or idx < 0 or idx >= len(CAPTCHA_QUESTIONS):
                return jsonify({"error": "Captcha session expired. Please refresh."}), 400
            if not is_correct_answer(idx, captcha_answer):
                return jsonify({"error": "Incorrect security answer"}), 400
            session["captcha_solved"] = True
            session.pop("captcha_index", None)

        result = submit_and_intake(
            prop_type=prop_type,
            props_count=props_count,
            name=name,
            siteswap_x=siteswap_x,
            comment=comment,
            user_id=user.id if user else None,
            anon_id=None if user else get_or_create_anon_id(),
        )

        return jsonify({
            "status": result.status,
            "pending_id": result.pending_id,
            "candidate_id": result.candidate_id,
            "match": result.match,
            "games_url": url_for("games.hub", prop=prop_type),
        }), 200

    except Exception as e:
        current_app.logger.exception("Error in /api/suggest_trick: %s", e)
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------------------------------------
# leaderboard
# ---------------------------------------------------------------------------
@api_bp.route("/leaderboard")
def api_leaderboard():
    kind = request.args.get("kind", "tricks")
    period = request.args.get("period", "all")
    user = current_user()
    try:
        board = get_board(kind, period, viewer_id=user.id if user else None)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify(board)


# ---------------------------------------------------------------------------
# URL shortener (same-origin only — no open-redirect)
# ---------------------------------------------------------------------------
def _is_same_origin(long_url: str) -> bool:
    """Only shorten URLs that point back to this site — prevents the
    shortener being abused as an open redirect to phishing pages."""
    try:
        target = urlsplit(long_url)
    except ValueError:
        return False
    # Relative URL with a path only → always same-origin.
    if not target.scheme and not target.netloc:
        return long_url.startswith("/") and not long_url.startswith("//")
    if target.scheme not in ("http", "https"):
        return False
    here = urlsplit(request.host_url)
    return target.netloc == here.netloc


@api_bp.route("/shorten_url", methods=["POST"])
def shorten_url():
    try:
        long_url = (request.get_json(silent=True) or {}).get("long_url")
        if not long_url:
            current_app.logger.error("shorten_url: long_url is required")
            return jsonify({"error": "long_url is required"}), 400
        if len(long_url) > _MAX_LONG_URL:
            return jsonify({"error": f"URL too long (max {_MAX_LONG_URL} bytes)"}), 400
        if not _is_same_origin(long_url):
            current_app.logger.warning("shorten_url: rejected off-site URL %r", long_url)
            return jsonify({"error": "Only same-site URLs may be shortened"}), 400

        # Check if URL already exists
        existing_code = db_manager.get_short_code_by_long_url(long_url)
        if existing_code:
            short_url = url_for("shortener.redirect_to_long_url", code=existing_code, _external=True)
            return jsonify({"short_url": short_url, "code": existing_code}), 200

        # Generate a random short code
        chars = string.ascii_letters + string.digits
        for _ in range(5):
            code = "".join(random.choice(chars) for _ in range(8))
            if db_manager.create_short_url(code, long_url):
                short_url = url_for("shortener.redirect_to_long_url", code=code, _external=True)
                return jsonify({"short_url": short_url, "code": code}), 200

        current_app.logger.error("shorten_url: Failed to create unique short URL")
        return jsonify({"error": "Failed to create unique short URL"}), 500

    except Exception as e:
        current_app.logger.exception("shorten_url: Error: %s", e)
        return jsonify({"error": f"Server error: {e}"}), 500


@shortener_bp.route("/shortener/<code>")
def redirect_to_long_url(code):
    try:
        long_url = db_manager.get_long_url(code)
        if long_url and _is_same_origin(long_url):
            return redirect(long_url)
        if long_url:
            current_app.logger.warning("shortener: refusing off-site redirect to %r", long_url)
        flash("Short URL not found.", "error")
        return redirect(url_for("home"))
    except Exception:
        flash("Service temporarily unavailable. Please try again later.", "error")
        return redirect(url_for("home"))
