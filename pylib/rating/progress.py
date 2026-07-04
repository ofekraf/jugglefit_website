"""
User-facing gamification state.

Everything the hub / game header / set-done screen / profile needs, in one
payload so the client makes a single ``/api/games/me`` call.
"""
from __future__ import annotations

import json
from typing import Optional

from database.db_manager import db_manager
from pylib.configuration.consts import LEVELS, BADGES


def level_for(n_total: int) -> dict:
    """Map lifetime answers → {level, title, at, next_at, to_next, pct}."""
    idx = 0
    for i, (thresh, _title) in enumerate(LEVELS):
        if n_total >= thresh:
            idx = i
        else:
            break
    at, title = LEVELS[idx]
    if idx + 1 < len(LEVELS):
        next_at, next_title = LEVELS[idx + 1]
        span = max(1, next_at - at)
        pct = min(1.0, (n_total - at) / span)
        to_next = max(0, next_at - n_total)
    else:
        next_at, next_title, pct, to_next = None, None, 1.0, 0
    return {
        "level": idx + 1,
        "title": title,
        "at": at,
        "next_at": next_at,
        "next_title": next_title,
        "to_next": to_next,
        "pct": round(pct, 3),
    }


def _badges_from_row(row: dict) -> list[str]:
    try:
        b = json.loads(row.get("badges") or "[]")
        return [x for x in b if x in BADGES]
    except Exception:
        return []


def me_payload(user, *, prop: str) -> dict:
    """Full ``/api/games/me`` response for a logged-in user."""
    row = db_manager.get_user_row(user.id) or {}
    n_total = (row.get("n_harder", 0) + row.get("n_tagging", 0)
               + row.get("n_throw", 0))
    pool_size = db_manager.count_active_candidates(prop)
    pool_rated = db_manager.count_candidates_rated_by(user.id, prop)
    lvl = level_for(n_total)
    badges = _badges_from_row(row)
    return {
        "logged_in": True,
        "display_name": row.get("display_name", user.display_name),
        "reliability": round(row.get("reliability", user.reliability), 3),
        "n_harder": row.get("n_harder", 0),
        "n_tagging": row.get("n_tagging", 0),
        "n_throw": row.get("n_throw", 0),
        "n_total": n_total,
        "n_tricks_promoted": row.get("n_tricks_promoted", 0),
        "n_curated": row.get("n_curated", 0),
        "n_balls": row.get("n_balls", 0),
        "n_clubs": row.get("n_clubs", 0),
        "n_rings": row.get("n_rings", 0),
        "level": lvl,
        "prop": prop,
        "pool_size": pool_size,
        "pool_rated": pool_rated,
        "badges": badges,
        "badge_meta": {k: {"label": l, "emoji": e, "desc": d}
                       for k, (l, e, d) in BADGES.items()},
    }
