"""
Feature requests and bug reports (``/feature_requests``).

Anyone can submit (anonymous, CSRF + honeypot + per-browser daily limit).
New submissions have status ``new`` and are **not public** until an admin
approves them on ``/feature_requests/admin`` (``ADMIN_PASSWORD``, unset =
admin off, 404). Approved requests are listed publicly by category; feature
and live-event ideas can be upvoted (one vote per browser), bugs show only
their status.

Private data - ``contact_email``, ``user_agent`` (bugs only) and
``submitter_id`` - is stored for the admin and never sent to the public
page (``db_manager.get_public_feature_requests`` selects public columns only).
"""
from __future__ import annotations

import os
import re
import secrets
import time
from urllib.parse import urlparse

from flask import (
    Blueprint, abort, current_app, flash, jsonify, redirect, render_template,
    request, session, url_for,
)

from blueprints.trick_feedback import get_voter_id
from database.db_manager import db_manager

feature_requests_bp = Blueprint("feature_requests", __name__)

CATEGORIES = {
    "website_feature": "Website feature",
    "website_bug": "Website bug",
    "live_event_idea": "Live event idea",
}
VOTABLE_CATEGORIES = ("website_feature", "live_event_idea")
STATUS_LABELS = {
    "new": "Waiting for review",
    "open": "Open",
    "planned": "Planned",
    "in_progress": "In progress",
    "done": "Done",
    "hidden": "Hidden",
}
# Bugs read better as "Reported" / "Fixed".
BUG_STATUS_LABELS = dict(STATUS_LABELS, open="Reported", done="Fixed")
ADMIN_STATUSES = tuple(STATUS_LABELS)

MAX_TITLE = 120
MAX_BODY = 2000
MAX_PAGE = 200
MAX_EMAIL = 254
MAX_USER_AGENT = 300
MAX_PER_DAY = 5
_DAY_MS = 24 * 60 * 60 * 1000
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_ADMIN_KEY = "feature_admin"


def _now_ms() -> int:
    return int(time.time() * 1000)


def _admin_password() -> str | None:
    return os.environ.get("ADMIN_PASSWORD") or None


def _is_admin() -> bool:
    return bool(_admin_password()) and session.get(_ADMIN_KEY) is True


def status_label(category: str, status: str) -> str:
    labels = BUG_STATUS_LABELS if category == "website_bug" else STATUS_LABELS
    return labels.get(status, status)


def _same_origin_path(url: str | None) -> str:
    """Path of a same-site referrer, to prefill 'which page' for bugs."""
    if not url:
        return ""
    parsed = urlparse(url)
    if parsed.netloc and parsed.netloc != request.host:
        return ""
    if parsed.path.startswith("/feature_requests"):
        return ""
    return parsed.path[:MAX_PAGE]


def _clean(value, limit: int) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip()[:limit]


# ---------------------------------------------------------------------------
# public page + API
# ---------------------------------------------------------------------------
@feature_requests_bp.route("/feature_requests")
def feature_requests_page():
    try:
        requests_ = db_manager.get_public_feature_requests()
        my_votes = db_manager.get_feature_votes_by_voter(get_voter_id())
    except Exception as e:  # never break the page on a DB problem
        current_app.logger.warning("feature requests lookup failed: %s", e)
        requests_, my_votes = [], []
    by_category = {key: [r for r in requests_ if r["category"] == key] for key in CATEGORIES}
    return render_template(
        "feature_requests.html",
        categories=CATEGORIES,
        by_category=by_category,
        votable=VOTABLE_CATEGORIES,
        my_votes=set(my_votes),
        status_label=status_label,
        prefill_page=_same_origin_path(request.referrer),
        max_title=MAX_TITLE, max_body=MAX_BODY,
    )


@feature_requests_bp.route("/api/feature_requests", methods=["POST"])
def submit_feature_request():
    data = request.get_json(silent=True) or {}
    if data.get("website"):  # honeypot: hidden field only bots fill in
        return jsonify({"ok": True}), 201

    category = data.get("category")
    if category not in CATEGORIES:
        return jsonify({"error": "Please choose a category"}), 400
    title = _clean(data.get("title"), MAX_TITLE + 1)
    body = _clean(data.get("body"), MAX_BODY + 1)
    if len(title) < 3:
        return jsonify({"error": "Please add a short title"}), 400
    if len(title) > MAX_TITLE or len(body) > MAX_BODY:
        return jsonify({"error": "Text is too long"}), 400
    email = _clean(data.get("email"), MAX_EMAIL + 1)
    if email and (len(email) > MAX_EMAIL or not _EMAIL_RE.match(email)):
        return jsonify({"error": "That email address doesn't look right"}), 400

    is_bug = category == "website_bug"
    page = _clean(data.get("page"), MAX_PAGE) if is_bug else ""
    user_agent = (request.headers.get("User-Agent") or "")[:MAX_USER_AGENT] if is_bug else ""

    submitter = get_voter_id()
    now = _now_ms()
    try:
        if db_manager.count_feature_requests_since(submitter, now - _DAY_MS) >= MAX_PER_DAY:
            return jsonify({"error": "Thanks! You've sent a lot today - please try again tomorrow."}), 429
        request_id = db_manager.create_feature_request(
            category=category, title=title, body=body, page=page or None,
            contact_email=email or None, user_agent=user_agent or None,
            submitter_id=submitter, now_ms=now,
        )
    except Exception as e:
        current_app.logger.exception("feature request: %s", e)
        return jsonify({"error": "Could not save. Please try again."}), 500
    return jsonify({"ok": True, "id": request_id}), 201


@feature_requests_bp.route("/api/feature_requests/<int:request_id>/vote", methods=["POST"])
def vote_feature_request(request_id: int):
    item = db_manager.get_feature_request(request_id)
    if (item is None or item["status"] not in db_manager.PUBLIC_FEATURE_STATUSES
            or item["category"] not in VOTABLE_CATEGORIES):
        return jsonify({"error": "Not found"}), 404
    data = request.get_json(silent=True) or {}
    voted = data.get("voted") is True
    votes = db_manager.set_feature_vote(request_id, get_voter_id(), voted, _now_ms())
    return jsonify({"ok": True, "voted": voted, "votes": votes})


# ---------------------------------------------------------------------------
# admin (review, approve, change status)
# ---------------------------------------------------------------------------
@feature_requests_bp.route("/feature_requests/admin", methods=["GET", "POST"])
def admin():
    password = _admin_password()
    if not password:
        abort(404)
    if request.method == "POST":
        sent = request.form.get("password", "")
        if secrets.compare_digest(sent.encode("utf-8"), password.encode("utf-8")):
            session[_ADMIN_KEY] = True
            return redirect(url_for("feature_requests.admin"))
        flash("Wrong password", "error")
        return redirect(url_for("feature_requests.admin"))
    if not _is_admin():
        return render_template("feature_requests_admin.html", logged_in=False)

    category = request.args.get("category") if request.args.get("category") in CATEGORIES else None
    status = request.args.get("status") if request.args.get("status") in ADMIN_STATUSES else None
    return render_template(
        "feature_requests_admin.html", logged_in=True,
        items=db_manager.get_all_feature_requests(category, status),
        categories=CATEGORIES, statuses=ADMIN_STATUSES, status_label=status_label,
        filter_category=category, filter_status=status,
    )


@feature_requests_bp.route("/feature_requests/admin/<int:request_id>", methods=["POST"])
def admin_update(request_id: int):
    if not _admin_password():
        abort(404)
    if not _is_admin():
        abort(403)
    back = url_for("feature_requests.admin", **{k: v for k, v in request.args.items()
                                               if k in ("category", "status")})
    if request.form.get("action") == "delete":
        db_manager.delete_feature_request(request_id)
        flash("Deleted", "success")
        return redirect(back)

    item = db_manager.get_feature_request(request_id)
    if item is None:
        abort(404)
    status = request.form.get("status", item["status"])
    if status not in ADMIN_STATUSES:
        abort(400)
    title = _clean(request.form.get("title"), MAX_TITLE) or item["title"]
    body = _clean(request.form.get("body"), MAX_BODY)
    db_manager.update_feature_request(request_id, status=status, title=title, body=body,
                                      now_ms=_now_ms())
    flash(f"Saved #{request_id}", "success")
    return redirect(back)


@feature_requests_bp.route("/feature_requests/admin/logout", methods=["POST"])
def admin_logout():
    session.pop(_ADMIN_KEY, None)
    return redirect(url_for("feature_requests.feature_requests_page"))
