"""
SQLite online backup.

Writes a single ``jugglefit_<ts>.db`` snapshot (full database — every
table, every row) and prunes old snapshots. Nothing else: the snapshot
is sufficient to restore everything; CSVs/tarballs are not produced.

Triggers:
  * before every candidate→master promotion
  * daily via deploy/oci-ubuntu/backup.sh
  * POST /admin/api/backup
  * python -m database.backup
"""
from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from database.db_manager import db_manager

# How many snapshots to keep ON THE LOCAL DISK. Default 1: the local copy
# exists only as the upload source / instant rollback point. Long-term
# retention lives off-box (rclone remote) and is governed by
# BACKUP_REMOTE_KEEP_DAILY/WEEKLY in deploy/oci-ubuntu/backup.sh.
DEFAULT_KEEP_LOCAL = int(os.environ.get("BACKUP_KEEP_LOCAL", 1))


def _backup_dir() -> Path:
    d = Path(os.environ.get(
        "SQLITE_BACKUP_DIR",
        os.path.join(db_manager.db_dir, "backups"),
    ))
    d.mkdir(parents=True, exist_ok=True)
    return d


def _prune_local(directory: Path, *, keep: int) -> None:
    """Keep only the newest ``keep`` local snapshots."""
    snaps: List[Path] = sorted(directory.glob("jugglefit_*.db"), reverse=True)
    for p in snaps[keep:]:
        p.unlink(missing_ok=True)


def backup_db(*, keep_local: int = DEFAULT_KEEP_LOCAL) -> Path:
    """Create an online-safe snapshot of the SQLite file.

    Only ``keep_local`` (default 1) snapshots are retained on disk; the
    caller (backup.sh) is responsible for pushing to off-box storage
    *before* the next run replaces it.
    """
    dst_dir = _backup_dir()
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    db_dest = dst_dir / f"jugglefit_{ts}.db"

    # NB: ``with sqlite3.connect`` commits but does NOT close — explicitly
    # close so the file handle is released (matters on Windows and for
    # immediate prune below).
    src = sqlite3.connect(db_manager.db_path)
    dst = sqlite3.connect(db_dest)
    try:
        src.backup(dst)
    finally:
        dst.close()
        src.close()

    _prune_local(dst_dir, keep=max(1, keep_local))
    db_manager.set_meta("last_backup_at", ts)
    return db_dest


if __name__ == "__main__":
    path = backup_db()
    print(f"Backup written to {path}")
