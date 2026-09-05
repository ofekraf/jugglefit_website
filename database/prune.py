"""
Storage retention sweep.

Run **after** ``backup_db()`` so the snapshot still contains anything
about to be reclaimed. Invoked nightly via cron on the deploy host
(see ``deploy/oci-ubuntu/backup.sh``).

This app has no crowd-sourced vote/candidate tables to prune (see
CLAUDE.md / the ``feature/crowd-contribution`` git branch for that
system). The only prunable data is stale URL-shortener mappings —
``delete_inactive_urls`` also runs at app boot, so this script mainly
matters for long-lived containers that aren't restarted often.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict

from database.db_manager import db_manager
from hardcoded_database.consts import URL_RETENTION_MONTHS


def prune(*, vacuum: bool = True) -> Dict[str, int]:
    """Delete prunable rows; optionally VACUUM to reclaim disk.

    Returns ``{table: rows_deleted}``.
    """
    deleted: Dict[str, int] = {
        "url_mappings": db_manager.delete_inactive_urls(URL_RETENTION_MONTHS) or 0,
    }
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
