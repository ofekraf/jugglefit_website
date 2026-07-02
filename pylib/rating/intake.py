"""
``pending_tricks`` → ``candidate_tricks`` intake.

Runs synchronously on every submission (cheap: a couple of indexed lookups
and at most one insert). Dedup rules mirror ``Trick.__eq__``:
same ``props_count`` AND (same ``name`` OR same ``siteswap_x``).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from database.db_manager import db_manager
from pylib.classes.prop import Prop
from pylib.configuration.consts import (
    CANDIDATE_INIT_SIGMA,
    MIN_TRICK_DIFFICULTY,
    MAX_TRICK_DIFFICULTY,
)


@dataclass(frozen=True)
class IntakeResult:
    pending_id: int
    status: str                       # 'accepted' | 'dup_master' | 'dup_candidate'
    candidate_id: Optional[int]       # set for accepted / dup_candidate
    match: Optional[dict] = None      # the existing trick/candidate row on dup


def _normalize(s: Optional[str]) -> Optional[str]:
    if s is None:
        return None
    s = s.strip()
    return s or None


def _initial_mu(prop_type: str, props_count: int) -> float:
    m = db_manager.mean_difficulty(prop_type, props_count)
    if m is None:
        m = (MIN_TRICK_DIFFICULTY + MAX_TRICK_DIFFICULTY) / 2
    return max(MIN_TRICK_DIFFICULTY, min(MAX_TRICK_DIFFICULTY, m))


def submit_and_intake(
    *,
    prop_type: str,
    props_count: int,
    name: Optional[str],
    siteswap_x: Optional[str],
    comment: Optional[str],
    user_id: Optional[int],
    anon_id: Optional[str],
) -> IntakeResult:
    """Record a pending row, then immediately classify/intake it."""
    name = _normalize(name)
    siteswap_x = _normalize(siteswap_x)
    comment = _normalize(comment)

    pending_id = db_manager.add_pending_trick(
        prop_type=prop_type, props_count=props_count,
        name=name, siteswap_x=siteswap_x, comment=comment,
        user_id=user_id, anon_id=anon_id,
    )

    Prop.get_key_by_value(prop_type)  # validate

    # 1. Already in master? (indexed point lookup)
    m = db_manager.find_master_match(prop_type=prop_type, props_count=props_count,
                                     name=name, siteswap_x=siteswap_x)
    if m is not None:
        db_manager.mark_pending(pending_id, status="dup_master")
        return IntakeResult(pending_id=pending_id, status="dup_master",
                            candidate_id=None, match=m)

    # 2. Already an active candidate?
    cm = db_manager.find_candidate_match(
        prop_type=prop_type, props_count=props_count,
        name=name, siteswap_x=siteswap_x,
    )
    if cm:
        db_manager.bump_candidate_submission(cm["id"])
        db_manager.mark_pending(pending_id, status="dup_candidate", dup_of=cm["id"])
        return IntakeResult(pending_id=pending_id, status="dup_candidate",
                            candidate_id=cm["id"],
                            match={k: cm.get(k) for k in
                                   ("id", "props_count", "name", "siteswap_x",
                                    "comment", "submission_count")})

    # 3. New candidate.
    mu = _initial_mu(prop_type, props_count)
    candidate_id = db_manager.add_candidate_trick(
        prop_type=prop_type, props_count=props_count,
        name=name, siteswap_x=siteswap_x, comment=comment,
        user_id=user_id, mu=mu, sigma=CANDIDATE_INIT_SIGMA,
    )
    db_manager.mark_pending(pending_id, status="accepted", dup_of=candidate_id)
    return IntakeResult(pending_id=pending_id, status="accepted",
                        candidate_id=candidate_id)
