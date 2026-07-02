"""
Storage retention for the raw vote/log tables.

Primary deletion happens **synchronously at settle time** via
``db_manager.purge_candidate_votes(cid)`` (called from
``promote_candidate`` / flag-removal / admin reject). This module is the
**periodic safety-net sweep** for rows that don't belong to a single
candidate or that escaped the synchronous purge:

  * anchor-vs-anchor ``comparisons`` (control questions) — no candidate
    to settle, pruned by age only;
  * any vote row whose candidate is settled (should be empty in normal
    operation, but covers crashes mid-promote / manual DB edits);
  * ``pending_tricks`` older than ``PENDING_RETENTION_DAYS``.

Run **after** ``backup_db()`` so the snapshot still contains anything
about to be reclaimed.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict

from database.db_manager import db_manager
from hardcoded_database.consts import URL_RETENTION_MONTHS
from pylib.configuration.consts import (
    RAW_VOTE_RETENTION_DAYS, PENDING_RETENTION_DAYS, PRUNE_BATCH_SIZE,
)

_AGE = f"datetime('now', '-{int(RAW_VOTE_RETENTION_DAYS)} days')"
_PENDING_AGE = f"datetime('now', '-{int(PENDING_RETENTION_DAYS)} days')"

# A candidate is "settled" once it has left the active pool.
_SETTLED = (
    "SELECT id FROM candidate_tricks "
    "WHERE promoted_at IS NOT NULL OR removed_at IS NOT NULL"
)

# rowid-batched DELETEs keep write locks short.
_JOBS: dict[str, str] = {
    # Anchor-only comparison rows (control questions). Candidate-touching
    # rows are purged synchronously at settle time, so this is age-only.
    "comparisons_anchor": f"""
        DELETE FROM comparisons WHERE rowid IN (
          SELECT rowid FROM comparisons
          WHERE left_kind != 'candidate' AND right_kind != 'candidate'
            AND created_at < {_AGE}
          LIMIT {int(PRUNE_BATCH_SIZE)}
        )
    """,
    # Safety-net: any row whose candidate is settled but escaped the
    # synchronous purge (crash, manual edit). No age gate — should be 0.
    "comparisons_settled": f"""
        DELETE FROM comparisons WHERE rowid IN (
          SELECT rowid FROM comparisons
          WHERE (left_kind  = 'candidate' AND CAST(left_id  AS INTEGER) IN ({_SETTLED}))
             OR (right_kind = 'candidate' AND CAST(right_id AS INTEGER) IN ({_SETTLED}))
          LIMIT {int(PRUNE_BATCH_SIZE)}
        )
    """,
    "tag_votes": f"""
        DELETE FROM tag_votes WHERE rowid IN (
          SELECT rowid FROM tag_votes WHERE candidate_id IN ({_SETTLED})
          LIMIT {int(PRUNE_BATCH_SIZE)}
        )
    """,
    "throw_votes": f"""
        DELETE FROM throw_votes WHERE rowid IN (
          SELECT rowid FROM throw_votes WHERE candidate_id IN ({_SETTLED})
          LIMIT {int(PRUNE_BATCH_SIZE)}
        )
    """,
    "trick_flags": f"""
        DELETE FROM trick_flags WHERE rowid IN (
          SELECT rowid FROM trick_flags WHERE candidate_id IN ({_SETTLED})
          LIMIT {int(PRUNE_BATCH_SIZE)}
        )
    """,
    "pending_tricks": f"""
        DELETE FROM pending_tricks WHERE rowid IN (
          SELECT rowid FROM pending_tricks WHERE created_at < {_PENDING_AGE}
          LIMIT {int(PRUNE_BATCH_SIZE)}
        )
    """,
}


def prune(*, vacuum: bool = True) -> Dict[str, int]:
    """Delete prunable rows in batches; optionally VACUUM to reclaim disk.

    Returns ``{table: rows_deleted}``.
    """
    deleted: Dict[str, int] = {k: 0 for k in _JOBS}
    for table, sql in _JOBS.items():
        while True:
            with db_manager.cursor(commit=True) as cur:
                cur.execute(sql)
                n = cur.rowcount
            deleted[table] += max(0, n)
            if n < PRUNE_BATCH_SIZE:
                break
    # Short-URL retention (also runs on app boot; here so a long-lived
    # container still gets nightly cleanup via cron).
    deleted["url_mappings"] = db_manager.delete_inactive_urls(URL_RETENTION_MONTHS) or 0
    if vacuum and any(deleted.values()):
        # VACUUM must run outside a transaction on its own connection.
        conn = db_manager.get_connection()
        if conn is not None:
            try:
                conn.isolation_level = None
                conn.execute("VACUUM")
            finally:
                conn.close()
    db_manager.set_meta("last_prune_at",
                        datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S"))
    db_manager.set_meta("last_prune_deleted",
                        ",".join(f"{k}={v}" for k, v in deleted.items()))
    return deleted


if __name__ == "__main__":
    for k, v in prune().items():
        print(f"{k}: deleted {v}")
