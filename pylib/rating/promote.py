"""
Candidate → master promotion.

``ready_candidates(prop)`` evaluates the gates from the design and attaches
the crowd-resolved difficulty/tags/max_throw so the admin sees exactly what
will be written.

``promote_candidate(id, overrides)`` snapshots the DB, writes the master
``tricks`` row, marks the candidate promoted, bumps the submitter's
``n_tricks_promoted`` counter, and hot-reloads the in-memory registry.
"""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Optional

from database.db_manager import db_manager
from database.backup import backup_db
from pylib.classes.prop import Prop
from pylib.utils.trick_registry import reload_prop
from pylib.rating.aggregate import (
    resolve_max_throw, missing_tag_categories, tag_probabilities,
)
from pylib.configuration.consts import (
    PROMOTE_MIN_COMPARISONS, PROMOTE_MAX_SIGMA, PROMOTE_MAX_UNKNOWN_RATIO,
    PROMOTE_MIN_AGE_HOURS, MIN_THROW_VOTES, MIN_TAG_VOTES,
)
from pylib.rating.aggregate import relevant_categories


def _age_hours(ts: str | None) -> float:
    if not ts:
        return 0.0
    try:
        dt = datetime.fromisoformat(ts)
    except ValueError:
        dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - dt) / timedelta(hours=1)


def _annotate(c: dict) -> dict:
    cid = c["id"]
    seen = c["n_comparisons"] + c["n_cant_judge"] + c["n_flags"]
    unknown_ratio = ((c["n_cant_judge"] + c["n_flags"]) / seen) if seen else 0.0
    out = dict(c)
    out["resolved_difficulty"] = round(c["mu"])
    probs = tag_probabilities(cid)
    out["tag_probs"] = probs
    out["resolved_tags"] = sorted(r["tag"] for r in probs if r["resolved"])
    out["resolved_max_throw"] = resolve_max_throw(cid)
    out["unknown_ratio"] = round(unknown_ratio, 3)
    out["age_hours"] = round(_age_hours(c.get("created_at")), 1)
    n_cats = max(1, len(relevant_categories(c["prop_type"])))
    missing = missing_tag_categories(cid, c["prop_type"])
    out["gates"] = {
        "comparisons": c["n_comparisons"] >= PROMOTE_MIN_COMPARISONS,
        "sigma": c["sigma"] <= PROMOTE_MAX_SIGMA,
        "recognition": unknown_ratio < PROMOTE_MAX_UNKNOWN_RATIO,
        "tags": len(missing) == 0,
        "throw": c["n_throw_votes"] >= MIN_THROW_VOTES,
        "age": out["age_hours"] >= PROMOTE_MIN_AGE_HOURS,
    }
    out["ready"] = all(out["gates"].values())
    # Continuous readiness ∈ [0,1]: mean of per-gate progress. Lets the admin
    # sort the pool by "closest to promotion" without a boolean cliff.
    progress = [
        min(1.0, c["n_comparisons"] / PROMOTE_MIN_COMPARISONS),
        min(1.0, PROMOTE_MAX_SIGMA / max(c["sigma"], 1e-6)),
        1.0 if unknown_ratio < PROMOTE_MAX_UNKNOWN_RATIO
            else max(0.0, 1.0 - (unknown_ratio - PROMOTE_MAX_UNKNOWN_RATIO)
                                 / max(1e-6, 1.0 - PROMOTE_MAX_UNKNOWN_RATIO)),
        (n_cats - len(missing)) / n_cats,
        min(1.0, c["n_throw_votes"] / MIN_THROW_VOTES),
        min(1.0, out["age_hours"] / PROMOTE_MIN_AGE_HOURS),
    ]
    out["readiness"] = round(sum(progress) / len(progress), 3)
    out["gates_passed"] = sum(1 for v in out["gates"].values() if v)
    return out


def annotated_active_candidates(prop_type: str) -> list[dict]:
    """All active candidates for a prop, fully annotated and ordered by
    readiness (closest-to-promotion first)."""
    rows = [_annotate(c) for c in db_manager.get_active_candidates(prop_type)]
    rows.sort(key=lambda a: (-a["gates_passed"], -a["readiness"], a["sigma"]))
    return rows


def ready_candidates(prop_type: str) -> list[dict]:
    return [a for a in annotated_active_candidates(prop_type) if a["ready"]]


def annotate_candidate(candidate_id: int) -> Optional[dict]:
    c = db_manager.get_candidate(candidate_id)
    return _annotate(c) if c else None


def promote_candidate(candidate_id: int, *, overrides: dict | None = None,
                      do_backup: bool = True) -> dict:
    overrides = overrides or {}
    c = db_manager.get_candidate(candidate_id)
    if c is None:
        raise ValueError("candidate not found")
    if c["promoted_at"] is not None:
        raise ValueError("already promoted")
    if c["removed_at"] is not None:
        raise ValueError("candidate is removed")

    a = _annotate(c)

    def _ov(key, default):
        v = overrides.get(key, default)
        if isinstance(v, str):
            v = v.strip() or None
        return v

    name = _ov("name", c["name"])
    siteswap_x = _ov("siteswap_x", c["siteswap_x"])
    comment = _ov("comment", c["comment"])
    if not name and not siteswap_x:
        raise ValueError("name or siteswap_x is required")
    difficulty = int(overrides.get("difficulty", a["resolved_difficulty"]))
    tags_list = overrides.get("tags")
    if tags_list is None:
        tags_list = a["resolved_tags"]
    tags_str = "|".join(sorted(tags_list))
    max_throw = overrides.get("max_throw", a["resolved_max_throw"])
    if isinstance(max_throw, str):
        max_throw = int(max_throw) if max_throw.strip() else None

    if do_backup:
        try:
            backup_db()
        except Exception as e:  # backup must not block promotion in dev
            print(f"WARN: pre-promote backup failed: {e}")

    trick_id = db_manager.insert_trick(
        prop_type=c["prop_type"], props_count=c["props_count"],
        name=name, siteswap_x=siteswap_x,
        difficulty=difficulty, tags=tags_str, max_throw=max_throw,
        comment=comment, source="crowd", user_id=c["user_id"],
    )
    if trick_id is None:
        raise ValueError("master already contains this trick")

    db_manager.mark_candidate_promoted(candidate_id)
    if c["user_id"] is not None:
        with db_manager.cursor(commit=True) as cur:
            cur.execute(
                "UPDATE users SET n_tricks_promoted = n_tricks_promoted + 1 WHERE id = ?",
                (c["user_id"],),
            )

    # Trick is now stable in ``tricks`` — raw votes for it have served
    # their purpose. The pre-promote backup_db() above already snapshotted
    # them, so we can reclaim immediately.
    db_manager.purge_candidate_votes(candidate_id)

    reload_prop(Prop.get_key_by_value(c["prop_type"]))
    return {
        "trick_id": trick_id,
        "difficulty": difficulty,
        "tags": tags_list,
        "max_throw": max_throw,
    }
