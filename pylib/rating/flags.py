"""
Flag-to-remove: logged-in users can flag a candidate trick from any game
card. When enough distinct users flag it (relative to how many have seen
it), the candidate is soft-removed from the rating pool. Admins remove
instantly; admins can also restore.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from database.db_manager import db_manager
from pylib.configuration.consts import (
    FLAG_REASONS, FLAG_REASON_ALIASES, FLAG_REMOVE_MIN, FLAG_REMOVE_RATIO,
    UNSTABLE_MIN_EXPOSURES, UNSTABLE_UNKNOWN_RATIO,
)
from pylib.rating.tasks import unsign


def queue_for_deletion(candidate_id: int, *, reason: str) -> None:
    """Single entry point: move to pending_deletion and purge raw votes.
    Idempotent — no-op if the candidate is not currently active."""
    # Award tastemaker BEFORE purge deletes trick_flags rows.
    from pylib.rating.achievements import on_candidate_removed
    on_candidate_removed(candidate_id)
    db_manager.queue_for_deletion(candidate_id, reason=reason)
    db_manager.purge_candidate_votes(candidate_id)


def check_unstable(candidate: dict) -> bool:
    """Auto-queue a candidate that the crowd consistently cannot judge.
    Called from the compare-answer path after counters update."""
    exposures = candidate["n_comparisons"] + candidate["n_cant_judge"]
    if exposures < UNSTABLE_MIN_EXPOSURES:
        return False
    bad = candidate["n_cant_judge"] + candidate["n_flags"]
    if bad / exposures < UNSTABLE_UNKNOWN_RATIO:
        return False
    queue_for_deletion(candidate["id"], reason="unstable")
    return True


@dataclass(frozen=True)
class FlagResult:
    candidate_id: int
    new_flag: bool        # False if this user already flagged it
    n_flags: int
    removed: bool


def _candidate_ids_from_task(task: dict) -> List[int]:
    # Compare tasks carry an explicit list; tag/throw tasks (Steps 7/8) will
    # carry a single ``cid`` field.
    ids = list(task.get("cand") or [])
    if "cid" in task and task["cid"] is not None:
        ids.append(task["cid"])
    # dedup, preserve order
    seen: set[int] = set()
    out: List[int] = []
    for i in ids:
        if i not in seen:
            seen.add(i)
            out.append(i)
    return out


def _should_remove(*, n_flags: int, seen: int) -> bool:
    """Queue for deletion only when BOTH: at least FLAG_REMOVE_MIN distinct
    flaggers AND they represent > FLAG_REMOVE_RATIO of everyone who has been
    served this candidate. Flaggers are themselves raters, so ``seen`` is
    always ≥ n_flags in practice; guard the degenerate case anyway."""
    if n_flags < FLAG_REMOVE_MIN:
        return False
    exposures = max(seen, n_flags)
    return (n_flags / exposures) > FLAG_REMOVE_RATIO


def record_flag(*, task_id: str, reason: str, user_id: int,
                is_admin: bool) -> List[FlagResult]:
    reason = FLAG_REASON_ALIASES.get(reason, reason)
    if reason not in FLAG_REASONS:
        raise ValueError("invalid reason")
    task = unsign(task_id)
    cids = _candidate_ids_from_task(task)
    if not cids:
        raise ValueError("nothing to flag on this task")

    results: List[FlagResult] = []
    for cid in cids:
        cand = db_manager.get_candidate(cid)
        if cand is None or cand.get("status") != "active":
            results.append(FlagResult(cid, False, cand["n_flags"] if cand else 0,
                                      removed=bool(cand and cand.get("status") != "active")))
            continue
        is_new = db_manager.add_flag(candidate_id=cid, user_id=user_id, reason=reason)
        cand = db_manager.get_candidate(cid)  # refresh n_flags
        removed = False
        if is_admin:
            removed = True
        else:
            seen = db_manager.distinct_raters_seen(cid)
            removed = _should_remove(n_flags=cand["n_flags"], seen=seen)
        if removed:
            top = db_manager.top_flag_reason(cid) or reason
            queue_for_deletion(cid, reason=top)
        results.append(FlagResult(cid, is_new, cand["n_flags"], removed=removed))
    return results
