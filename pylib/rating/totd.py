"""
Trick of the Day: one deterministic candidate per prop per UTC day.

Everyone rates the same trick first, so data converges fast and the hub
can show "yesterday's" resolved μ / tag consensus.
"""
from __future__ import annotations

import datetime as dt
import zlib
from typing import Optional

from database.db_manager import db_manager


def _seed(prop_type: str, day: dt.date) -> int:
    return zlib.crc32(f"{day.isoformat()}|{prop_type}".encode()) & 0xFFFFFFFF


def pick(prop_type: str, *, day: Optional[dt.date] = None) -> Optional[dict]:
    d = day or dt.datetime.now(dt.timezone.utc).date()
    return db_manager.daily_candidate(prop_type, seed=_seed(prop_type, d))


def yesterday_summary(prop_type: str) -> Optional[dict]:
    y = dt.datetime.now(dt.timezone.utc).date() - dt.timedelta(days=1)
    row = pick(prop_type, day=y)
    if not row:
        return None
    # Local import: promote → aggregate → db_manager; avoid a cycle at
    # module load if pair_picker imports this module.
    from pylib.rating.promote import annotate_candidate
    a = annotate_candidate(row["id"]) or {}
    return {
        "id": row["id"],
        "name": row.get("name"),
        "siteswap_x": row.get("siteswap_x"),
        "props_count": row["props_count"],
        "mu": round(row["mu"], 1),
        "sigma": round(row["sigma"], 1),
        "n_comparisons": row["n_comparisons"],
        "resolved_tags": a.get("resolved_tags", []),
        "readiness": a.get("readiness"),
    }
