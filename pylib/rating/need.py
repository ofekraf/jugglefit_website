"""
Need score: orders the three games on the hub by where the candidate pool
needs help most for a given prop.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import List

from database.db_manager import db_manager
from pylib.configuration.consts import (
    PROMOTE_MAX_SIGMA, PROMOTE_MIN_COMPARISONS,
    TAG_UNLOCK_SIGMA, MIN_TAG_VOTES, MIN_THROW_VOTES,
    W_HARDER, W_TAG, W_THROW,
)
from pylib.rating.aggregate import relevant_categories

GAME_META = {
    "harder":  {"title": "Which trick is considered harder",
                "blurb": "Compare two tricks and pick the harder one."},
    "tagging": {"title": "Tagging",       "blurb": "Pick the tags that describe a trick."},
    "throw":   {"title": "Highest Throw", "blurb": "Tell us the highest throw in a trick."},
}


@dataclass
class GameNeed:
    game: str
    title: str
    blurb: str
    backlog: int
    deficit: int
    score: float
    available: bool

    def to_dict(self) -> dict:
        return asdict(self)


def compute_needs(prop_type: str, *, available_games: set[str]) -> List[GameNeed]:
    n_cats = max(1, len(relevant_categories(prop_type)))
    s = db_manager.need_stats(
        prop_type,
        promote_max_sigma=PROMOTE_MAX_SIGMA,
        tag_unlock_sigma=TAG_UNLOCK_SIGMA,
        promote_min_cmp=PROMOTE_MIN_COMPARISONS,
        min_tag_votes=MIN_TAG_VOTES,
        n_cats=n_cats,
        min_throw_votes=MIN_THROW_VOTES,
    )
    raw = [
        ("harder",  s["h_backlog"], s["h_def"], W_HARDER),
        ("tagging", s["t_backlog"], s["t_def"], W_TAG),
        ("throw",   s["t_backlog"], s["w_def"], W_THROW),
    ]
    needs = [
        GameNeed(
            game=g,
            title=GAME_META[g]["title"],
            blurb=GAME_META[g]["blurb"],
            backlog=backlog,
            deficit=deficit,
            score=deficit * weight,
            available=(g in available_games),
        )
        for g, backlog, deficit, weight in raw
    ]
    # Order: available first, then by score desc, then backlog desc.
    needs.sort(key=lambda n: (not n.available, -n.score, -n.backlog))
    return needs
