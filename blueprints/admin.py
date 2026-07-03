"""
Admin & super-admin routes.

* **Admin**  = a logged-in user row with ``is_admin = 1``.
* **Super-admin** = env-credential gate (``SUPER_ADMIN_USER`` /
  ``SUPER_ADMIN_PASSWORD``). Works at both ``/auth/login`` and
  ``/admin/login``. Only super-admin can grant/revoke admin on users.
"""
from __future__ import annotations

import time
from functools import wraps

from flask import (
    Blueprint, render_template, request, jsonify, redirect, url_for, flash,
    session,
)

from database.db_manager import db_manager
from database.backup import backup_db
from database.prune import prune
from hardcoded_database.tricks import ALL_PROPS_SETTINGS_JSON
from pylib.auth import (
    current_user, login_user, SUPER_ADMIN_USER,
    is_super_admin_credentials, ensure_super_admin_user,
)
from pylib.classes.prop import Prop, MAIN_PROPS
from pylib.configuration.consts import ADMIN_SESSION_SECONDS
from pylib.rating.flags import queue_for_deletion
from pylib.rating.promote import (
    ready_candidates, annotated_active_candidates,
    annotate_candidate, promote_candidate,
)


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# ---------------------------------------------------------------------------
# auth helpers (also used by app.py context processor)
# ---------------------------------------------------------------------------
def super_admin_session_valid() -> bool:
    ts = session.get("super_admin_at")
    if not ts:
        return False
    if time.time() - ts > ADMIN_SESSION_SECONDS:
        session.pop("super_admin_at", None)
        return False
    return True


def is_admin() -> bool:
    user = current_user()
    return bool((user and user.is_admin) or super_admin_session_valid())


def _wants_json() -> bool:
    return request.is_json or request.accept_mimetypes.best == "application/json"


def admin_required(f):
    """Gate: logged-in user with ``is_admin`` OR valid super-admin session."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if is_admin():
            return f(*args, **kwargs)
        if _wants_json():
            return jsonify({"error": "admin login required"}), 401
        return redirect(url_for("admin.login", next=request.path))
    return wrapper


def super_admin_required(f):
    """Only the env-credential super-admin may pass."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if super_admin_session_valid():
            return f(*args, **kwargs)
        if _wants_json():
            return jsonify({"error": "super-admin login required"}), 403
        return redirect(url_for("admin.login", next=request.path))
    return wrapper


def _safe_next(target: str | None) -> str | None:
    if target and target.startswith("/") and not target.startswith("//"):
        return target
    return None


# ---------------------------------------------------------------------------
# pages
# ---------------------------------------------------------------------------
@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        if is_super_admin_credentials(username, password):
            login_user(ensure_super_admin_user())
            session["super_admin_at"] = time.time()
            return redirect(_safe_next(request.args.get("next")) or url_for("admin.crowd"))
        flash("Invalid credentials", "error")
    return render_template("admin/login.html", need_username=bool(SUPER_ADMIN_USER))


@admin_bp.route("/logout")
def logout():
    session.pop("super_admin_at", None)
    session.pop("admin_logged_in_at", None)
    session.pop("logged_in", None)
    return redirect(url_for("home"))


@admin_bp.route("/suggestions")
def suggestions():
    # Legacy URL — pipeline replaced by /admin/crowd.
    return redirect(url_for("admin.crowd"))


@admin_bp.route("/crowd")
@admin_required
def crowd():
    return render_template(
        "admin/crowd.html",
        props_settings=ALL_PROPS_SETTINGS_JSON,
        main_props=MAIN_PROPS,
        is_super_admin=super_admin_session_valid(),
    )


@admin_bp.route("/users")
@super_admin_required
def users():
    return render_template("admin/users.html", users=db_manager.list_users())


# ---------------------------------------------------------------------------
# JSON API
# ---------------------------------------------------------------------------
@admin_bp.route("/api/candidates/<prop_type>")
@admin_required
def api_candidates(prop_type):
    state = request.args.get("state", "pool")
    try:
        Prop.get_key_by_value(prop_type)
    except Exception:
        return jsonify({"error": "invalid prop"}), 400
    if state == "ready":
        return jsonify(ready_candidates(prop_type))
    if state == "pool":
        # Server-side annotation so the client doesn't fan out N per-row
        # fetches (which also caused a stale-render race when switching tabs).
        return jsonify(annotated_active_candidates(prop_type))
    try:
        return jsonify(db_manager.get_candidates_by_state(prop_type, state))
    except ValueError:
        return jsonify({"error": "invalid state"}), 400


@admin_bp.route("/api/candidate/<int:candidate_id>")
@admin_required
def api_candidate(candidate_id):
    a = annotate_candidate(candidate_id)
    if a is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(a)


@admin_bp.route("/api/users")
@super_admin_required
def api_users():
    return jsonify(db_manager.list_users())


@admin_bp.route("/api/users/<int:user_id>/admin", methods=["POST"])
@super_admin_required
def api_set_user_admin(user_id):
    body = request.get_json(silent=True) or {}
    is_admin_val = bool(body.get("is_admin"))
    if not db_manager.set_user_admin(user_id, is_admin=is_admin_val):
        return jsonify({"error": "not found"}), 404
    return jsonify({"ok": True, "user_id": user_id, "is_admin": is_admin_val})


@admin_bp.route("/api/promote/<int:candidate_id>", methods=["POST"])
@admin_required
def api_promote(candidate_id):
    body = request.get_json(silent=True) or {}
    overrides = {k: body[k] for k in ("difficulty", "tags", "max_throw") if k in body}
    try:
        result = promote_candidate(candidate_id, overrides=overrides)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify({"ok": True, **result})


@admin_bp.route("/api/backup", methods=["POST"])
@admin_required
def api_backup():
    try:
        path = backup_db()
        return jsonify({"ok": True, "path": str(path)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/api/prune", methods=["POST"])
@admin_required
def api_prune():
    try:
        vacuum = bool((request.get_json(silent=True) or {}).get("vacuum", True))
        deleted = prune(vacuum=vacuum)
        return jsonify({"ok": True, "deleted": deleted})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/api/restore/<int:candidate_id>", methods=["POST"])
@admin_required
def api_restore(candidate_id):
    cand = db_manager.get_candidate(candidate_id)
    if cand is None:
        return jsonify({"error": "not found"}), 404
    if not db_manager.restore_candidate(candidate_id):
        return jsonify({"error": "only pending_deletion candidates can be restored"}), 400
    return jsonify({"ok": True})


@admin_bp.route("/api/reject/<int:candidate_id>", methods=["POST"])
@admin_required
def api_reject(candidate_id):
    """Queue an active candidate for deletion (admin review stage)."""
    cand = db_manager.get_candidate(candidate_id)
    if cand is None:
        return jsonify({"error": "not found"}), 404
    queue_for_deletion(candidate_id, reason="admin_reject")
    return jsonify({"ok": True})


@admin_bp.route("/api/delete/<int:candidate_id>", methods=["POST"])
@admin_required
def api_delete(candidate_id):
    """Permanently delete a candidate that is in pending_deletion."""
    cand = db_manager.get_candidate(candidate_id)
    if cand is None:
        return jsonify({"error": "not found"}), 404
    if cand.get("status") != "pending_deletion":
        return jsonify({"error": "only pending_deletion candidates can be permanently deleted"}), 400
    db_manager.delete_candidate_permanently(candidate_id)
    return jsonify({"ok": True})
