"""
Resolve crowd votes into final ``tags`` / ``max_throw`` for a candidate.
Used by the Promote step and by the admin Ready view.
"""
from __future__ import annotations

from typing import Optional, Set

from database.db_manager import db_manager
from pylib.configuration.consts import (
    TAG_VOTE_THRESHOLD, MIN_TAG_VOTES, MIN_THROW_VOTES,
    PROP_RELEVANT_CATEGORIES,
)
from pylib.classes.prop import Prop


def relevant_categories(prop_type: str) -> list[str]:
    prop = Prop.get_key_by_value(prop_type)
    return [c.value for c in PROP_RELEVANT_CATEGORIES.get(prop, [])]


def missing_tag_categories(candidate_id: int, prop_type: str) -> list[str]:
    cov = db_manager.tag_category_coverage(candidate_id)
    return [cat for cat in relevant_categories(prop_type)
            if cov.get(cat, 0) < MIN_TAG_VOTES]


def tag_probabilities(candidate_id: int) -> list[dict]:
    """Per-tag confidence, sorted by probability desc.

    ``p`` = reliability-weighted positive share ∈ [0, 1] (0.0 when the tag
    has been shown but nobody with weight has voted). ``n`` = distinct
    non-abstain votes. ``resolved`` mirrors the promotion threshold so
    callers that only need the final set can filter on it.
    """
    out: list[dict] = []
    for row in db_manager.tag_vote_summary(candidate_id):
        w_pos = row["w_pos"] or 0.0
        w_neg = row["w_neg"] or 0.0
        n = row["n_nonzero"] or 0
        denom = w_pos + w_neg
        p = (w_pos / denom) if denom > 0 else 0.0
        out.append({
            "tag": row["tag"],
            "p": round(p, 3),
            "n": n,
            "resolved": n >= MIN_TAG_VOTES and p >= TAG_VOTE_THRESHOLD,
        })
    out.sort(key=lambda r: (-r["p"], -r["n"], r["tag"]))
    return out


def resolve_tags(candidate_id: int) -> Set[str]:
    """Final tag set for promotion — thin threshold over
    :func:`tag_probabilities`."""
    return {r["tag"] for r in tag_probabilities(candidate_id) if r["resolved"]}


def resolve_max_throw(candidate_id: int) -> Optional[int]:
    """Reliability-weighted median of non-NULL votes; NULL if ≥60% voted N/A
    or fewer than MIN_THROW_VOTES votes exist."""
    rows = db_manager.throw_vote_summary(candidate_id)
    if len(rows) < MIN_THROW_VOTES:
        return None
    total_w = sum(r["w"] for r in rows) or 1.0
    na_w = sum(r["w"] for r in rows if r["max_throw"] is None)
    if na_w / total_w >= 0.6:
        return None
    valued = sorted((r for r in rows if r["max_throw"] is not None),
                    key=lambda r: r["max_throw"])
    if not valued:
        return None
    acc, half = 0.0, sum(r["w"] for r in valued) / 2.0
    for r in valued:
        acc += r["w"]
        if acc >= half:
            return int(r["max_throw"])
    return int(valued[-1]["max_throw"])
