"""
Achievements: evaluate + persist badges on ``users.badges`` (JSON list).

``check_and_award(user_id)`` is idempotent — call after any counter change;
it recomputes the earned set from the user row and writes only if new
badges appeared. Returns the list of *newly* earned badge ids so callers
can toast.

Event-driven badges that can't be derived from counters (``founder``,
``curator_*``, ``tastemaker``) are awarded via ``award(user_id, badge_id)``
from the relevant code path.
"""
from __future__ import annotations

import json
from typing import Iterable

from database.db_manager import db_manager
from pylib.configuration.consts import BADGES


def _current(row: dict) -> set[str]:
    try:
        return set(json.loads(row.get("badges") or "[]"))
    except Exception:
        return set()


def _derive(row: dict) -> set[str]:
    """Badges that are a pure function of the user row's counters."""
    out: set[str] = set()
    n_total = row.get("n_harder", 0) + row.get("n_tagging", 0) + row.get("n_throw", 0)
    if n_total >= 1:
        out.add("first_answer")
    for n, b in ((10, "answers_10"), (50, "answers_50"),
                 (200, "answers_200"), (1000, "answers_1000")):
        if n_total >= n:
            out.add(b)
    if row.get("n_harder", 0) and row.get("n_tagging", 0) and row.get("n_throw", 0):
        out.add("polyglot")
    if row.get("reliability", 0) >= 0.9 and n_total >= 50:
        out.add("sharp_eye")
    for col, b in (("n_balls", "balls_50"), ("n_clubs", "clubs_50"),
                   ("n_rings", "rings_50")):
        if row.get(col, 0) >= 50:
            out.add(b)
    nc = row.get("n_curated", 0)
    for n, b in ((1, "curator_1"), (5, "curator_5"), (25, "curator_25")):
        if nc >= n:
            out.add(b)
    if row.get("n_tricks_promoted", 0) >= 1:
        out.add("founder")
    return out & set(BADGES)


def check_and_award(user_id: int) -> list[str]:
    row = db_manager.get_user_row(user_id)
    if not row:
        return []
    have = _current(row)
    earned = have | _derive(row)
    new = sorted(earned - have)
    if new:
        db_manager.set_user_badges(user_id, sorted(earned))
    return new


def award(user_ids: int | Iterable[int], badge_id: str) -> None:
    """Directly grant an event badge (idempotent)."""
    if badge_id not in BADGES:
        return
    ids = [user_ids] if isinstance(user_ids, int) else list(user_ids)
    for uid in ids:
        row = db_manager.get_user_row(uid)
        if not row:
            continue
        have = _current(row)
        if badge_id not in have:
            db_manager.set_user_badges(uid, sorted(have | {badge_id}))


def on_candidate_promoted(candidate_id: int, *, submitter_id: int | None) -> None:
    """Hook from promote_candidate: bump n_curated for every voter, award
    founder to the submitter, then re-derive counter badges for all."""
    voters = db_manager.voters_for_candidate(candidate_id)
    db_manager.bump_user_curated(voters)
    for uid in voters:
        check_and_award(uid)
    if submitter_id:
        # n_tricks_promoted is bumped by the caller; founder derives from it.
        check_and_award(submitter_id)


def on_candidate_removed(candidate_id: int) -> None:
    """Hook from queue_for_deletion: award tastemaker to flaggers. Must run
    BEFORE purge_candidate_votes (which deletes trick_flags)."""
    for uid in db_manager.flaggers_for_candidate(candidate_id):
        award(uid, "tastemaker")
