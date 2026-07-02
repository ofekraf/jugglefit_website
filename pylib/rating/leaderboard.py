"""
Leaderboards.

Four boards × two periods. Reads are served live from SQL (cheap at this
scale); ``leaderboard_cache`` exists for future nightly snapshots but is
not required for correctness.
"""
from __future__ import annotations

from typing import Optional

from database.db_manager import db_manager
from pylib.configuration.consts import LEADERBOARD_TOP_N, LEADERBOARD_PERIODS

KINDS = ("tricks", "harder", "tagging", "throw")

KIND_META = {
    "tricks":  {"title": "Trick Hunters",   "metric": "tricks promoted"},
    "harder":  {"title": "Which trick is considered harder", "metric": "weighted answers"},
    "tagging": {"title": "Tagging",         "metric": "weighted answers"},
    "throw":   {"title": "Highest Throw",   "metric": "weighted answers"},
}


def _period_clause(period: str, col: str = "created_at") -> str:
    days = LEADERBOARD_PERIODS.get(period)
    if days is None:
        return "1=1"
    return f"{col} >= datetime('now', '-{int(days)} days')"


_W = "MAX(0.0, 2*u.reliability - 1)"

# All-time game boards read the denormalized counters on ``users`` so they
# survive raw-vote pruning. Periodic boards (e.g. 30d) still aggregate raw
# rows — RAW_VOTE_RETENTION_DAYS must be >= the largest such period.
_ALL_TIME_USER_COL = {
    "harder":  "n_harder",
    "tagging": "n_tagging",
    "throw":   "n_throw",
}


def _sql(kind: str, period: str) -> str:
    pc = _period_clause(period, "t.created_at")
    if kind == "tricks":
        # All attributed master tricks (seed + crowd + admin). ``tricks``
        # rows are never pruned, so both periods aggregate directly.
        return (
            "SELECT u.id AS user_id, u.display_name, COUNT(*) AS score "
            "FROM tricks t JOIN users u ON u.id = t.user_id "
            f"WHERE {pc} "
            "GROUP BY u.id"
        )
    if period == "all" and kind in _ALL_TIME_USER_COL:
        col = _ALL_TIME_USER_COL[kind]
        return (
            "SELECT u.id AS user_id, u.display_name, "
            f"       u.{col} * {_W} AS score "
            f"FROM users u WHERE u.{col} > 0"
        )
    if kind == "harder":
        return (
            f"SELECT u.id AS user_id, u.display_name, SUM({_W}) AS score "
            "FROM comparisons t JOIN users u ON u.id = t.user_id "
            f"WHERE t.is_control = 0 AND {pc} "
            "GROUP BY u.id"
        )
    if kind == "tagging":
        return (
            f"SELECT u.id AS user_id, u.display_name, SUM({_W}) AS score FROM ("
            "  SELECT DISTINCT user_id, candidate_id, category, created_at "
            "  FROM tag_votes WHERE user_id IS NOT NULL"
            ") t JOIN users u ON u.id = t.user_id "
            f"WHERE {pc} GROUP BY u.id"
        )
    if kind == "throw":
        return (
            f"SELECT u.id AS user_id, u.display_name, SUM({_W}) AS score "
            "FROM throw_votes t JOIN users u ON u.id = t.user_id "
            f"WHERE {pc} GROUP BY u.id"
        )
    raise ValueError(kind)


def get_board(kind: str, period: str, *, viewer_id: Optional[int] = None) -> dict:
    if kind not in KINDS or period not in LEADERBOARD_PERIODS:
        raise ValueError("invalid kind/period")
    base = _sql(kind, period)
    # users-table queries have no GROUP BY → WHERE-level filter already applied.
    having = "" if "GROUP BY" not in base else " HAVING score > 0"
    # Wrap as a subquery so we can COUNT / rank / LIMIT without materializing
    # every row in Python — keeps this O(TOP_N) in-process regardless of user
    # count. SQLite runs the aggregate once per subquery use; still cheap at
    # this scale and far better than fetchall().
    sub = f"({base}{having}) b"

    with db_manager.cursor() as cur:
        cur.execute(f"SELECT COUNT(*) AS total FROM {sub}")
        total = cur.fetchone()["total"]

        cur.execute(
            f"SELECT user_id, display_name, score FROM {sub} "
            f"ORDER BY score DESC LIMIT {int(LEADERBOARD_TOP_N)}"
        )
        top = [dict(r) for r in cur.fetchall()]
        for i, r in enumerate(top, 1):
            r["rank"] = i
            r["score"] = round(r["score"], 1)

        you = None
        if viewer_id:
            cur.execute(
                f"SELECT b.user_id, b.display_name, b.score, "
                f"  (SELECT COUNT(*) + 1 FROM {sub}2 WHERE b2.score > b.score) AS rank "
                f"FROM {sub} WHERE b.user_id = ?",
                (viewer_id,),
            )
            row = cur.fetchone()
            if row:
                you = dict(row)
                you["score"] = round(you["score"], 1)

    return {
        "kind": kind, "period": period,
        "title": KIND_META[kind]["title"],
        "metric": KIND_META[kind]["metric"],
        "top": top, "you": you, "total": total,
    }
