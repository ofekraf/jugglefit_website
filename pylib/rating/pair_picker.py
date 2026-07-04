"""
Build homogeneous task sets for each game.

Only the *compare* builder is implemented here; tag/throw builders land in
Steps 7/8 but the public ``build_set(game, ...)`` dispatcher already exists
so the blueprint stays stable.
"""
from __future__ import annotations

import random
from typing import Optional

from database.db_manager import db_manager
from pylib.classes.tag import TAG_CATEGORY_MAP, TagCategory
from pylib.configuration.consts import (
    RATING_SET_SIZE, RATING_CONTROL_FRACTION, CONTROL_MIN_GAP,
    TAG_UNLOCK_SIGMA, THROW_STEPPER_MIN, THROW_STEPPER_MAX,
)
from pylib.rating.aggregate import relevant_categories
from pylib.rating.tasks import sign
from pylib.rating.totd import pick as totd_pick


def _pins(prop_type: str, focus: int | None) -> list[dict]:
    """Candidate rows to force to the front of every set (TOTD + ?focus=)."""
    out: list[dict] = []
    seen: set[int] = set()
    for row in (
        db_manager.get_candidate(focus) if focus else None,
        totd_pick(prop_type),
    ):
        if (row and row.get("status") == "active"
                and row.get("prop_type") == prop_type
                and row["id"] not in seen):
            out.append(row)
            seen.add(row["id"])
    return out


# ---------------------------------------------------------------------------
# rendering helpers
# ---------------------------------------------------------------------------
def _public_side(row: dict) -> dict:
    name = row.get("name") or None
    ss = row.get("siteswap_x") or None
    return {
        "name": name,
        "siteswap_x": ss,
        "label": name or ss or "?",   # fallback for renderers that don't split
        "props_count": row["props_count"],
    }


# ---------------------------------------------------------------------------
# compare set
# ---------------------------------------------------------------------------
def _control_compare(prop_type: str) -> Optional[dict]:
    pair = db_manager.random_anchor_pair(prop_type, min_gap=CONTROL_MIN_GAP)
    if not pair:
        return None
    a, b = pair
    left, right = (a, b) if random.random() < 0.5 else (b, a)
    expected = "left" if left["difficulty"] > right["difficulty"] else "right"
    return _make_compare_task(prop_type, ("anchor", left), ("anchor", right),
                              is_control=True, expected=expected)


def build_compare_set(prop_type: str, *, user_id: int,
                      size: int = RATING_SET_SIZE,
                      focus: int | None = None) -> list[dict]:
    n_control = max(1, round(size * RATING_CONTROL_FRACTION))
    pins = _pins(prop_type, focus)
    cands = pins + [
        c for c in db_manager.pick_candidates_for_compare(
            prop_type, exclude_user=user_id, limit=size,
        ) if c["id"] not in {p["id"] for p in pins}
    ]
    tasks: list[dict] = []

    for _ in range(n_control):
        t = _control_compare(prop_type)
        if t:
            tasks.append(t)
    if not tasks and not cands:
        return []  # no anchors and no candidates → nothing to play

    ci = 0
    while len(tasks) < size and cands:
        c = cands[ci % len(cands)]
        ci += 1
        a = db_manager.anchor_near(prop_type, mu=c["mu"],
                                   props_count=c["props_count"], window=10)
        if a is None:
            break
        left, right = (("candidate", c), ("anchor", a))
        if random.random() < 0.5:
            left, right = right, left
        tasks.append(_make_compare_task(prop_type, left, right,
                                        is_control=False, expected=None))
        if len(cands) >= 2 and len(tasks) < size and ci % 2 == 0:
            c2 = cands[ci % len(cands)]
            if c2["id"] != c["id"]:
                l, r = (("candidate", c), ("candidate", c2))
                if random.random() < 0.5:
                    l, r = r, l
                tasks.append(_make_compare_task(prop_type, l, r,
                                                is_control=False, expected=None))

    while len(tasks) < size:
        t = _control_compare(prop_type)
        if not t:
            break
        tasks.append(t)

    random.shuffle(tasks)
    tasks = tasks[:size]
    # Re-pin: move any task involving a pinned candidate to the front,
    # preserving pin order (focus first, then TOTD).
    pin_ids = [p["id"] for p in pins]
    def _has_pin(t):
        for i, pid in enumerate(pin_ids):
            if pid in (t.get("_cand_ids") or []):
                return i
        return len(pin_ids)
    tasks.sort(key=_has_pin)
    for t in tasks:
        t.pop("_cand_ids", None)
    return tasks


def _make_compare_task(prop_type: str,
                       left: tuple[str, dict], right: tuple[str, dict],
                       *, is_control: bool, expected: Optional[str]) -> dict:
    l_kind, l_row = left
    r_kind, r_row = right
    candidate_ids = [
        row["id"] for kind, row in (left, right) if kind == "candidate"
    ]
    token = sign({
        "k": "compare",
        "p": prop_type,
        "l": {"t": l_kind, "i": l_row["id"]},
        "r": {"t": r_kind, "i": r_row["id"]},
        "c": is_control,
        "e": expected,
        "cand": candidate_ids,  # convenience for flag endpoint
    })
    return {
        "kind": "compare",
        "task_id": token,
        "left": _public_side(l_row),
        "right": _public_side(r_row),
        "flaggable": bool(candidate_ids),
        "_cand_ids": candidate_ids,   # stripped before returning to client
    }


# ---------------------------------------------------------------------------
# tag set
# ---------------------------------------------------------------------------
def _category_tags(category: str) -> list[str]:
    cat = TagCategory.get_key_by_value(category)
    return sorted(str(t) for t in TAG_CATEGORY_MAP.get(cat, set()))


def _eligible_for_metadata(prop_type: str, *, user_id: int, order: str,
                           limit: int) -> list[dict]:
    return db_manager.pick_candidates_for_metadata(
        prop_type, exclude_user=user_id, max_sigma=TAG_UNLOCK_SIGMA,
        order=order, limit=limit,
    )


def _make_tag_task(prop_type: str, *, kind: str, row: dict,
                   cats: list[str], expected: Optional[list[str]]) -> dict:
    """One task = one trick × ALL prop-relevant categories."""
    tags_by_cat = {cat: _category_tags(cat) for cat in cats}
    all_tags = [t for ts in tags_by_cat.values() for t in ts]
    cid = row["id"] if kind == "candidate" else None
    token = sign({
        "k": "tag", "p": prop_type,
        "cid": cid,
        "aid": row["id"] if kind == "anchor" else None,
        "cats": cats, "tags": all_tags,
        "c": kind == "anchor", "e": expected,
        "cand": [cid] if cid is not None else [],
    })
    return {
        "kind": "tag", "task_id": token,
        "trick": _public_side(row),
        # Legacy renderers may still read `category`/`tags`; keep both flat
        # and grouped forms so old clients don't crash mid-deploy.
        "category": None, "tags": all_tags,
        "tags_by_cat": tags_by_cat,
        "flaggable": cid is not None,
        "_cid": cid,
    }


def _tag_control(prop_type: str, cats: list[str]) -> Optional[dict]:
    """Random tagged anchor; expected = its master tags restricted to the
    prop's tag universe."""
    a = db_manager.random_anchor_with_tags(prop_type)
    if not a:
        return None
    a_tags = set((a.get("tags") or "").split("|")) - {""}
    universe = {t for cat in cats for t in _category_tags(cat)}
    expected = sorted(a_tags & universe)
    if not expected:
        return None
    return _make_tag_task(prop_type, kind="anchor", row=a,
                          cats=cats, expected=expected)


def build_tag_set(prop_type: str, *, user_id: int,
                  size: int = RATING_SET_SIZE,
                  focus: int | None = None) -> list[dict]:
    cats = relevant_categories(prop_type)
    if not cats:
        return []
    pins = _pins(prop_type, focus)
    cands = pins + [
        c for c in _eligible_for_metadata(prop_type, user_id=user_id,
                                          order="tag", limit=size)
        if c["id"] not in {p["id"] for p in pins}
    ]
    n_control = max(1, round(size * RATING_CONTROL_FRACTION))
    tasks: list[dict] = []

    for _ in range(n_control):
        t = _tag_control(prop_type, cats)
        if t:
            tasks.append(t)

    # One card now covers ALL categories, so each candidate appears at most
    # once per set. If the pool is smaller than `size`, controls fill the gap.
    for c in cands:
        if len(tasks) >= size:
            break
        tasks.append(_make_tag_task(prop_type, kind="candidate", row=c,
                                    cats=cats, expected=None))

    attempts = 0
    while len(tasks) < size and attempts < size * 4:
        attempts += 1
        t = _tag_control(prop_type, cats)
        if t:
            tasks.append(t)

    random.shuffle(tasks)
    tasks = tasks[:size]
    _pin_to_front(tasks, [p["id"] for p in pins])
    return tasks


def _pin_to_front(tasks: list[dict], pin_ids: list[int]) -> None:
    """Stable-move tasks whose `_cid` matches a pin id to the front."""
    if not pin_ids:
        for t in tasks:
            t.pop("_cid", None)
        return
    order = {pid: i for i, pid in enumerate(pin_ids)}
    tasks.sort(key=lambda t: order.get(t.get("_cid"), len(pin_ids)))
    for t in tasks:
        t.pop("_cid", None)


# ---------------------------------------------------------------------------
# throw set
# ---------------------------------------------------------------------------
def _make_throw_task(prop_type: str, *, kind: str, row: dict,
                     expected: Optional[int]) -> dict:
    cid = row["id"] if kind == "candidate" else None
    token = sign({
        "k": "throw", "p": prop_type,
        "cid": cid,
        "aid": row["id"] if kind == "anchor" else None,
        "c": kind == "anchor", "e": expected,
        "cand": [cid] if cid is not None else [],
    })
    return {
        "kind": "throw", "task_id": token,
        "trick": _public_side(row),
        "min": THROW_STEPPER_MIN, "max": THROW_STEPPER_MAX,
        "default": row["props_count"],
        "flaggable": cid is not None,
        "_cid": cid,
    }


def _throw_control(prop_type: str) -> Optional[dict]:
    a = db_manager.random_anchor_with_throw(prop_type)
    if not a:
        return None
    return _make_throw_task(prop_type, kind="anchor", row=a,
                            expected=a["max_throw"])


def build_throw_set(prop_type: str, *, user_id: int,
                    size: int = RATING_SET_SIZE,
                    focus: int | None = None) -> list[dict]:
    pins = _pins(prop_type, focus)
    cands = pins + [
        c for c in _eligible_for_metadata(prop_type, user_id=user_id,
                                          order="throw", limit=size)
        if c["id"] not in {p["id"] for p in pins}
    ]
    n_control = max(1, round(size * RATING_CONTROL_FRACTION))
    tasks: list[dict] = []

    for _ in range(n_control):
        t = _throw_control(prop_type)
        if t:
            tasks.append(t)

    for c in cands:
        if len(tasks) >= size:
            break
        tasks.append(_make_throw_task(prop_type, kind="candidate", row=c,
                                      expected=None))

    while len(tasks) < size:
        t = _throw_control(prop_type)
        if not t:
            break
        tasks.append(t)

    random.shuffle(tasks)
    tasks = tasks[:size]
    _pin_to_front(tasks, [p["id"] for p in pins])
    return tasks


# ---------------------------------------------------------------------------
# dispatcher
# ---------------------------------------------------------------------------
_BUILDERS = {
    "harder": build_compare_set,
    "tagging": build_tag_set,
    "throw": build_throw_set,
}

AVAILABLE_GAMES: set[str] = set(_BUILDERS.keys())


def build_set(game: str, prop_type: str, *, user_id: int,
              focus: int | None = None) -> list[dict]:
    builder = _BUILDERS.get(game)
    if builder is None:
        raise ValueError(f"unknown or not-yet-available game: {game}")
    return builder(prop_type, user_id=user_id, focus=focus)
