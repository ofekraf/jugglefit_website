import logging
import os
import sqlite3
from sqlite3 import Error
from contextlib import contextmanager
from typing import Optional, List, Dict, Any

from hardcoded_database.consts import URL_RETENTION_MONTHS

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------
# Every table is created with IF NOT EXISTS so init_db() is idempotent and
# safe to call on every process start (including under gunicorn where
# app.py's __main__ block does not run).
#
# This app has no login/accounts, crowd-sourced trick submission, or
# crowd-rating games system — see CLAUDE.md / the ``feature/crowd-contribution``
# git branch for that (larger) schema, preserved for future reactivation.
# The running app only needs: the URL shortener, and the master `tricks`
# table used by route generation/building.
SCHEMA_STATEMENTS: List[str] = [
    """
    CREATE TABLE IF NOT EXISTS url_mappings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        short_code TEXT NOT NULL UNIQUE,
        long_url TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    # --- master tricks (replaces CSV as source of truth) ----------------
    """
    CREATE TABLE IF NOT EXISTS tricks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prop_type TEXT NOT NULL,
        props_count INTEGER NOT NULL,
        name TEXT,
        siteswap_x TEXT,
        difficulty INTEGER NOT NULL,
        tags TEXT NOT NULL DEFAULT '',
        max_throw INTEGER,
        comment TEXT,
        source TEXT NOT NULL DEFAULT 'seed',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        promoted_at TIMESTAMP,
        UNIQUE(prop_type, props_count, name, siteswap_x)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_tricks_prop ON tricks(prop_type)",
    "CREATE INDEX IF NOT EXISTS idx_tricks_prop_pc_diff "
    "ON tricks(prop_type, props_count, difficulty)",
    "CREATE INDEX IF NOT EXISTS idx_tricks_name_lc "
    "ON tricks(prop_type, props_count, name COLLATE NOCASE)",
    "CREATE INDEX IF NOT EXISTS idx_tricks_ss_lc "
    "ON tricks(prop_type, props_count, siteswap_x COLLATE NOCASE)",
    # --- generic key/value bookkeeping (seed/backup/prune timestamps) ---
    """
    CREATE TABLE IF NOT EXISTS meta (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """,
]


class DBManager:
    def __init__(self):
        default_dir = os.path.join(os.getcwd(), 'database_data')
        self.db_dir = os.getenv('SQLITE_DB_DIR', default_dir)
        self.db_name = os.getenv('SQLITE_DB_NAME', 'jugglefit.db')
        self.db_path = os.path.join(self.db_dir, self.db_name)

        if not os.path.exists(self.db_dir):
            try:
                os.makedirs(self.db_dir, exist_ok=True)
            except OSError as e:
                log.error("Error creating database directory: %s", e)

        # Ensure schema exists as soon as the module is imported so that
        # downstream imports (trick registry) can read from the DB even
        # under gunicorn where app.py's __main__ block never runs.
        self.init_db()

    # ------------------------------------------------------------------
    # connection helpers
    # ------------------------------------------------------------------
    def get_connection(self):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            # Retry for up to 5s on writer contention instead of raising
            # 'database is locked'.
            conn.execute("PRAGMA busy_timeout = 5000")
            return conn
        except Error as e:
            log.error("Error connecting to database at %s: %s", self.db_path, e)
            return None

    @property
    def connection(self):
        # Backward-compat shim; callers must close the returned connection.
        return self.get_connection()

    @contextmanager
    def cursor(self, commit: bool = False):
        """Context manager yielding a cursor on a fresh connection."""
        conn = self.get_connection()
        if conn is None:
            raise RuntimeError(f"Could not open SQLite database at {self.db_path}")
        try:
            cur = conn.cursor()
            yield cur
            if commit:
                conn.commit()
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # schema
    # ------------------------------------------------------------------
    def init_db(self):
        conn = self.get_connection()
        if not conn:
            log.error("Failed to connect to database for initialization.")
            return
        try:
            # WAL: readers don't block writers and vice-versa. Persistent
            # (stored in the DB file), so setting once at init is enough.
            conn.execute("PRAGMA journal_mode = WAL")
            conn.execute("PRAGMA synchronous = NORMAL")
            cur = conn.cursor()
            for stmt in SCHEMA_STATEMENTS:
                cur.execute(stmt)
            conn.commit()
        except Error as e:
            log.error("Error initializing database: %s", e)
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # meta
    # ------------------------------------------------------------------
    def get_meta(self, key: str) -> Optional[str]:
        with self.cursor() as cur:
            cur.execute("SELECT value FROM meta WHERE key = ?", (key,))
            row = cur.fetchone()
            return row["value"] if row else None

    def set_meta(self, key: str, value: str) -> None:
        with self.cursor(commit=True) as cur:
            cur.execute(
                "INSERT INTO meta(key, value) VALUES (?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (key, value),
            )

    # ------------------------------------------------------------------
    # tricks (master)
    # ------------------------------------------------------------------
    def count_tricks(self, prop_type: Optional[str] = None) -> int:
        with self.cursor() as cur:
            if prop_type is None:
                cur.execute("SELECT COUNT(*) AS c FROM tricks")
            else:
                cur.execute("SELECT COUNT(*) AS c FROM tricks WHERE prop_type = ?", (prop_type,))
            return cur.fetchone()["c"]

    def get_tricks(self, prop_type: str) -> List[Dict[str, Any]]:
        with self.cursor() as cur:
            cur.execute(
                "SELECT id, name, props_count, difficulty, tags, comment, max_throw, siteswap_x "
                "FROM tricks WHERE prop_type = ? ORDER BY props_count, difficulty",
                (prop_type,),
            )
            return [dict(r) for r in cur.fetchall()]

    def insert_trick(
        self,
        *,
        prop_type: str,
        props_count: int,
        name: Optional[str],
        siteswap_x: Optional[str],
        difficulty: int,
        tags: str,
        max_throw: Optional[int],
        comment: Optional[str],
        source: str = "seed",
    ) -> Optional[int]:
        """Insert a master trick. Returns row id, or None on UNIQUE conflict."""
        with self.cursor(commit=True) as cur:
            try:
                cur.execute(
                    """
                    INSERT INTO tricks
                        (prop_type, props_count, name, siteswap_x, difficulty,
                         tags, max_throw, comment, source, promoted_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """,
                    (prop_type, props_count, name, siteswap_x, difficulty,
                     tags, max_throw, comment, source),
                )
                return cur.lastrowid
            except sqlite3.IntegrityError:
                return None

    # ------------------------------------------------------------------
    # url shortener
    # ------------------------------------------------------------------
    def get_short_code_by_long_url(self, long_url):
        with self.cursor() as cur:
            cur.execute(
                "SELECT short_code FROM url_mappings WHERE long_url = ? LIMIT 1",
                (long_url,),
            )
            row = cur.fetchone()
            return row["short_code"] if row else None

    def create_short_url(self, short_code, long_url):
        try:
            with self.cursor(commit=True) as cur:
                cur.execute(
                    "INSERT INTO url_mappings (short_code, long_url) VALUES (?, ?)",
                    (short_code, long_url),
                )
            return True
        except (Error, sqlite3.IntegrityError) as e:
            log.error("Error creating short URL: %s", e)
            return False

    def get_long_url(self, short_code):
        with self.cursor() as cur:
            cur.execute(
                "SELECT long_url FROM url_mappings WHERE short_code = ?",
                (short_code,),
            )
            row = cur.fetchone()
        if row:
            self.update_last_accessed(short_code)
            return row["long_url"]
        return None

    def update_last_accessed(self, short_code):
        try:
            with self.cursor(commit=True) as cur:
                cur.execute(
                    "UPDATE url_mappings SET last_accessed_at = CURRENT_TIMESTAMP "
                    "WHERE short_code = ?",
                    (short_code,),
                )
        except Error as e:
            log.error("Error updating last accessed time: %s", e)

    def delete_inactive_urls(self, months=URL_RETENTION_MONTHS):
        deleted = 0
        try:
            with self.cursor(commit=True) as cur:
                cur.execute(
                    "DELETE FROM url_mappings "
                    f"WHERE last_accessed_at < datetime('now', '-{int(months)} months')"
                )
                deleted = cur.rowcount
            log.info("Deleted %d inactive URLs.", deleted)
        except Error as e:
            log.error("Error deleting inactive URLs: %s", e)
        return deleted


# Global instance
db_manager = DBManager()
