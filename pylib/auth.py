"""
Lightweight username+password accounts backed by the SQLite ``users`` table.

No external dependencies: password hashing uses
``werkzeug.security`` (already a Flask dependency).
"""
from __future__ import annotations

import os
import re
import sqlite3
import uuid
from dataclasses import dataclass
from functools import wraps
from typing import Optional

from flask import session, redirect, url_for, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

from database.db_manager import db_manager
from pylib.configuration.consts import (
    USERNAME_RE, PASSWORD_MIN_LENGTH, PASSWORD_MAX_LENGTH,
)

SUPER_ADMIN_USER = os.environ.get("SUPER_ADMIN_USER")
SUPER_ADMIN_PASSWORD = os.environ.get("SUPER_ADMIN_PASSWORD")


@dataclass(frozen=True)
class User:
    id: int
    display_name: str
    is_admin: bool
    n_tricks_promoted: int
    n_harder: int
    n_tagging: int
    n_throw: int
    reliability: float

    @classmethod
    def from_row(cls, row) -> "User":
        return cls(
            id=row["id"],
            display_name=row["display_name"],
            is_admin=bool(row["is_admin"]),
            n_tricks_promoted=row["n_tricks_promoted"],
            n_harder=row["n_harder"],
            n_tagging=row["n_tagging"],
            n_throw=row["n_throw"],
            reliability=row["reliability"],
        )


# ---------------------------------------------------------------------------
# core operations
# ---------------------------------------------------------------------------
def register(display_name: str, password: str) -> User:
    display_name = (display_name or "").strip()
    if not re.fullmatch(USERNAME_RE, display_name):
        raise ValueError(
            "Display name must be 3–24 characters: letters, numbers, spaces or underscores."
        )
    if SUPER_ADMIN_USER and display_name.lower() == SUPER_ADMIN_USER.lower():
        raise ValueError("That display name is reserved.")
    if not (PASSWORD_MIN_LENGTH <= len(password or "") <= PASSWORD_MAX_LENGTH):
        raise ValueError(
            f"Password must be {PASSWORD_MIN_LENGTH}-{PASSWORD_MAX_LENGTH} characters."
        )

    pw_hash = generate_password_hash(password)
    try:
        with db_manager.cursor(commit=True) as cur:
            cur.execute(
                "SELECT 1 FROM users WHERE display_name = ? COLLATE NOCASE",
                (display_name,),
            )
            if cur.fetchone():
                raise ValueError("That display name is already taken.")
            cur.execute(
                "INSERT INTO users (display_name, password_hash) VALUES (?, ?)",
                (display_name, pw_hash),
            )
            user_id = cur.lastrowid
    except sqlite3.IntegrityError:
        # Lost a race against a concurrent registration with the same name.
        raise ValueError("That display name is already taken.")
    return get_user_by_id(user_id)  # type: ignore[return-value]


class AuthError(ValueError):
    """Raised by authenticate() with a user-facing message."""


def authenticate(display_name: str, password: str) -> User:
    with db_manager.cursor(commit=True) as cur:
        cur.execute(
            "SELECT * FROM users WHERE display_name = ? COLLATE NOCASE",
            ((display_name or "").strip(),),
        )
        row = cur.fetchone()
        if not row:
            raise AuthError("User doesn't exist.")
        if not check_password_hash(row["password_hash"], password or ""):
            raise AuthError("Wrong password.")
        cur.execute(
            "UPDATE users SET last_login_at = CURRENT_TIMESTAMP WHERE id = ?",
            (row["id"],),
        )
    return User.from_row(row)


def get_user_by_id(user_id: int) -> Optional[User]:
    with db_manager.cursor() as cur:
        cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cur.fetchone()
        return User.from_row(row) if row else None


# ---------------------------------------------------------------------------
# super-admin (env credentials)
# ---------------------------------------------------------------------------
def is_super_admin_credentials(display_name: str, password: str) -> bool:
    if not (SUPER_ADMIN_USER and SUPER_ADMIN_PASSWORD):
        return False
    return ((display_name or "").strip() == SUPER_ADMIN_USER
            and password == SUPER_ADMIN_PASSWORD)


def ensure_super_admin_user() -> User:
    """Get-or-create the ``users`` row backing the env super-admin so the
    nav/profile/leaderboard work like a normal account. The row's
    ``password_hash`` mirrors the env password and ``is_admin`` is forced
    on; the *authority* still comes from the env, not the row."""
    if not (SUPER_ADMIN_USER and SUPER_ADMIN_PASSWORD):
        raise AuthError("Super-admin not configured.")
    with db_manager.cursor(commit=True) as cur:
        cur.execute(
            "SELECT * FROM users WHERE display_name = ? COLLATE NOCASE",
            (SUPER_ADMIN_USER,),
        )
        row = cur.fetchone()
        if row:
            cur.execute(
                "UPDATE users SET is_admin = 1, last_login_at = CURRENT_TIMESTAMP "
                "WHERE id = ?",
                (row["id"],),
            )
            return User.from_row({**dict(row), "is_admin": 1})
        cur.execute(
            "INSERT INTO users (display_name, password_hash, is_admin) "
            "VALUES (?, ?, 1)",
            (SUPER_ADMIN_USER, generate_password_hash(SUPER_ADMIN_PASSWORD)),
        )
        uid = cur.lastrowid
    return get_user_by_id(uid)  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# session helpers
# ---------------------------------------------------------------------------
def login_user(user: User) -> None:
    session.permanent = True
    session["user_id"] = user.id


def logout_user() -> None:
    session.pop("user_id", None)


def current_user() -> Optional[User]:
    uid = session.get("user_id")
    return get_user_by_id(uid) if uid else None


def get_or_create_anon_id() -> str:
    """Stable per-browser id for anonymous game answers."""
    anon = session.get("anon_id")
    if not anon:
        anon = uuid.uuid4().hex
        session["anon_id"] = anon
        session.permanent = True
    return anon


# ---------------------------------------------------------------------------
# decorators
# ---------------------------------------------------------------------------
def login_required_user(view):
    """Require a logged-in *user* (distinct from the legacy admin gate)."""

    @wraps(view)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            if request.accept_mimetypes.best == "application/json" or request.is_json:
                return jsonify({"error": "login_required"}), 401
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)

    return wrapper
