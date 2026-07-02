"""
Score a single game answer identified by its signed task token.
"""
from __future__ import annotations

from typing import Optional

from database.db_manager import db_manager
from pylib.configuration.consts import ANON_VOTE_WEIGHT
from pylib.rating.elo import Side, apply_comparison
from pylib.rating.flags import check_unstable
from pylib.rating.tasks import unsign


_VALID_WINNERS = {"left", "right", "skip"}


def _load_side(kind: str, ident: int) -> Optional[Side]:
    if kind == "anchor":
        row = db_manager.get_master_trick(ident)
        if not row:
            return None
        return Side(mu=float(row["difficulty"]), sigma=0.0, is_anchor=True)
    if kind == "candidate":
        row = db_manager.get_candidate(ident)
        if not row:
            return None
        return Side(mu=row["mu"], sigma=row["sigma"], is_anchor=False)
    return None


def _handle_compare(task: dict, payload: dict, *, user_id: Optional[int],
                    anon_id: Optional[str], reliability: float) -> dict:
    winner = payload.get("winner")
    if winner not in _VALID_WINNERS:
        raise ValueError("invalid winner")

    prop_type = task["p"]
    l_kind, l_id = task["l"]["t"], task["l"]["i"]
    r_kind, r_id = task["r"]["t"], task["r"]["i"]
    is_control = bool(task.get("c"))
    expected = task.get("e")

    db_manager.record_comparison(
        user_id=user_id, anon_id=anon_id, prop_type=prop_type,
        left_kind=l_kind, left_id=str(l_id),
        right_kind=r_kind, right_id=str(r_id),
        winner=winner, is_control=is_control, expected_winner=expected,
    )

    result: dict = {"ok": True, "is_control": is_control}

    if is_control:
        if user_id is not None and winner != "skip":
            correct = (winner == expected)
            new_rel = db_manager.update_user_reliability(user_id, correct=correct)
            result["correct"] = correct
            result["reliability"] = round(new_rel, 3)
        return result

    # data pair
    if user_id is not None:
        db_manager.bump_user_game_counter(user_id, game="harder")

    if winner == "skip":
        for kind, ident in ((l_kind, l_id), (r_kind, r_id)):
            if kind == "candidate":
                c = db_manager.get_candidate(ident)
                if c and c["status"] == "active":
                    db_manager.update_candidate_rating(
                        ident, mu=c["mu"], sigma=c["sigma"], inc_cant_judge=1,
                    )
                    check_unstable(db_manager.get_candidate(ident))
        return result

    # Data pair (≥1 candidate / destabilised side): there is no ground
    # truth — the player is *providing* it. Always reward as a hit so the
    # game stays encouraging while we collect the signal.
    result["correct"] = True

    left = _load_side(l_kind, l_id)
    right = _load_side(r_kind, r_id)
    if left is None or right is None:
        return result  # side vanished (e.g. removed) – logged, nothing to update

    eff_reliability = reliability if user_id is not None else ANON_VOTE_WEIGHT
    new_left, new_right = apply_comparison(left, right, winner=winner,
                                           reliability=eff_reliability)
    for kind, ident, before, after in (
        (l_kind, l_id, left, new_left),
        (r_kind, r_id, right, new_right),
    ):
        if kind == "candidate":
            db_manager.update_candidate_rating(
                ident, mu=after.mu, sigma=after.sigma, inc_comparisons=1,
            )
    return result


def _handle_tag(task: dict, payload: dict, *, user_id: Optional[int],
                anon_id: Optional[str], reliability: float) -> dict:
    shown: list[str] = task.get("tags") or []
    selected = set(payload.get("selected_tags") or [])
    dont_know = bool(payload.get("dont_know"))
    is_control = bool(task.get("c"))
    result: dict = {"ok": True, "is_control": is_control}

    if is_control:
        if user_id is not None and not dont_know:
            expected = set(task.get("e") or [])
            correct = expected.issubset(selected & set(shown))
            new_rel = db_manager.update_user_reliability(user_id, correct=correct)
            result["correct"] = correct
            result["reliability"] = round(new_rel, 3)
        return result

    cid = task.get("cid")
    cand = db_manager.get_candidate(cid) if cid else None
    if not cand or cand.get("status") != "active":
        return result
    if user_id is not None:
        db_manager.bump_user_game_counter(user_id, game="tagging")
    if dont_know:
        votes = {t: 0 for t in shown}
    else:
        votes = {t: (1 if t in selected else -1) for t in shown}
    db_manager.record_tag_votes(candidate_id=cid, user_id=user_id, anon_id=anon_id,
                                category=task["cat"], votes=votes)
    return result


def _handle_throw(task: dict, payload: dict, *, user_id: Optional[int],
                  anon_id: Optional[str], reliability: float) -> dict:
    is_control = bool(task.get("c"))
    raw = payload.get("max_throw", "skip")
    result: dict = {"ok": True, "is_control": is_control}

    if is_control:
        if user_id is not None and raw != "skip":
            expected = task.get("e")
            if raw is None:
                correct = expected is None
            else:
                try:
                    correct = expected is not None and abs(int(raw) - int(expected)) <= 1
                except (TypeError, ValueError):
                    correct = False
            new_rel = db_manager.update_user_reliability(user_id, correct=correct)
            result["correct"] = correct
            result["reliability"] = round(new_rel, 3)
        return result

    cid = task.get("cid")
    cand = db_manager.get_candidate(cid) if cid else None
    if not cand or cand.get("status") != "active":
        return result
    if user_id is not None:
        db_manager.bump_user_game_counter(user_id, game="throw")
    if raw == "skip":
        return result
    val = None if raw is None else int(raw)
    db_manager.record_throw_vote(candidate_id=cid, user_id=user_id,
                                 anon_id=anon_id, max_throw=val)
    return result


_HANDLERS = {
    "compare": _handle_compare,
    "tag": _handle_tag,
    "throw": _handle_throw,
}


def handle_answer(task_id: str, payload: dict, *, user_id: Optional[int],
                  anon_id: Optional[str], reliability: float) -> dict:
    task = unsign(task_id)
    handler = _HANDLERS.get(task.get("k"))
    if handler is None:
        raise ValueError("unsupported task kind")
    return handler(task, payload, user_id=user_id, anon_id=anon_id,
                   reliability=reliability)
