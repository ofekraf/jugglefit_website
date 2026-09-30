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
    # --- live finals (see blueprints/finals.py) --------------------------
    # Times are UTC epoch milliseconds. final_events is append-only: it is
    # the timing log exported as CSV, so take-backs stay visible.
    """
    CREATE TABLE IF NOT EXISTS finals (
        id TEXT PRIMARY KEY,
        route_key TEXT NOT NULL,
        route_payload TEXT NOT NULL,
        admin_token_hash TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'active',
        version INTEGER NOT NULL DEFAULT 1,
        is_test INTEGER NOT NULL DEFAULT 0,
        created_at INTEGER NOT NULL,
        started_at INTEGER,
        ended_at INTEGER
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_finals_route_status ON finals(route_key, status)",
    """
    CREATE TABLE IF NOT EXISTS final_competitors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        final_id TEXT NOT NULL REFERENCES finals(id) ON DELETE CASCADE,
        position INTEGER NOT NULL,
        name TEXT NOT NULL,
        stage INTEGER NOT NULL DEFAULT 0,
        started_at INTEGER
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_final_competitors_final ON final_competitors(final_id)",
    """
    CREATE TABLE IF NOT EXISTS final_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        final_id TEXT NOT NULL REFERENCES finals(id) ON DELETE CASCADE,
        competitor_id INTEGER NOT NULL REFERENCES final_competitors(id) ON DELETE CASCADE,
        from_stage INTEGER,
        to_stage INTEGER NOT NULL,
        at INTEGER NOT NULL,
        client_at INTEGER
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_final_events_final ON final_events(final_id)",
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


    # ------------------------------------------------------------------
    # live finals
    # ------------------------------------------------------------------
    def create_final(self, *, final_id: str, route_key: str, route_payload: str,
                     admin_token_hash: str, names: List[str], now_ms: int,
                     is_test: bool = False) -> None:
        """Create a final. Any active final for the same route is ended
        (not deleted - its log is kept)."""
        with self.cursor(commit=True) as cur:
            cur.execute("BEGIN IMMEDIATE")
            cur.execute(
                "UPDATE finals SET status = 'ended', ended_at = ?, version = version + 1 "
                "WHERE route_key = ? AND status = 'active'",
                (now_ms, route_key),
            )
            cur.execute(
                "INSERT INTO finals (id, route_key, route_payload, admin_token_hash, "
                "is_test, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (final_id, route_key, route_payload, admin_token_hash, int(is_test), now_ms),
            )
            cur.executemany(
                "INSERT INTO final_competitors (final_id, position, name) VALUES (?, ?, ?)",
                [(final_id, i, name) for i, name in enumerate(names)],
            )

    def get_final(self, final_id: str) -> Optional[Dict[str, Any]]:
        with self.cursor() as cur:
            cur.execute("SELECT * FROM finals WHERE id = ?", (final_id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def get_active_final_by_route_key(self, route_key: str) -> Optional[Dict[str, Any]]:
        with self.cursor() as cur:
            cur.execute(
                "SELECT id, status, version, started_at FROM finals "
                "WHERE route_key = ? AND status = 'active' ORDER BY created_at DESC LIMIT 1",
                (route_key,),
            )
            row = cur.fetchone()
            return dict(row) if row else None

    def get_final_competitors(self, final_id: str) -> List[Dict[str, Any]]:
        with self.cursor() as cur:
            cur.execute(
                "SELECT id, position, name, stage, started_at FROM final_competitors "
                "WHERE final_id = ? ORDER BY position",
                (final_id,),
            )
            return [dict(r) for r in cur.fetchall()]

    def get_final_events(self, final_id: str) -> List[Dict[str, Any]]:
        with self.cursor() as cur:
            cur.execute(
                "SELECT id, competitor_id, from_stage, to_stage, at, client_at "
                "FROM final_events WHERE final_id = ? ORDER BY id",
                (final_id,),
            )
            return [dict(r) for r in cur.fetchall()]

    def start_final(self, final_id: str, now_ms: int, client_at: Optional[int] = None,
                    competitor_id: Optional[int] = None) -> int:
        """Start one competitor, or every competitor not started yet.
        Logs the entry into their current stage. Returns the new version."""
        with self.cursor(commit=True) as cur:
            cur.execute("BEGIN IMMEDIATE")
            query = ("SELECT id, stage FROM final_competitors "
                     "WHERE final_id = ? AND started_at IS NULL")
            params: tuple = (final_id,)
            if competitor_id is not None:
                query += " AND id = ?"
                params = (final_id, competitor_id)
            cur.execute(query, params)
            to_start = cur.fetchall()
            started = client_at or now_ms
            for row in to_start:
                cur.execute("UPDATE final_competitors SET started_at = ? WHERE id = ?",
                            (started, row["id"]))
                cur.execute(
                    "INSERT INTO final_events (final_id, competitor_id, from_stage, to_stage, "
                    "at, client_at) VALUES (?, ?, NULL, ?, ?, ?)",
                    (final_id, row["id"], row["stage"], now_ms, client_at),
                )
            cur.execute(
                "UPDATE finals SET version = version + 1, "
                "started_at = COALESCE(started_at, ?) WHERE id = ?",
                (started, final_id),
            )
            cur.execute("SELECT version FROM finals WHERE id = ?", (final_id,))
            return cur.fetchone()["version"]

    def move_competitor(self, final_id: str, competitor_id: int, to_stage: int,
                        now_ms: int, client_at: Optional[int] = None) -> Optional[int]:
        """Move a competitor and log it in one transaction. Returns the new
        version, or None if the competitor is not in this final."""
        with self.cursor(commit=True) as cur:
            cur.execute("BEGIN IMMEDIATE")
            cur.execute(
                "SELECT stage FROM final_competitors WHERE id = ? AND final_id = ?",
                (competitor_id, final_id),
            )
            row = cur.fetchone()
            if row is None:
                return None
            if row["stage"] != to_stage:
                cur.execute("UPDATE final_competitors SET stage = ? WHERE id = ?",
                            (to_stage, competitor_id))
                cur.execute(
                    "INSERT INTO final_events (final_id, competitor_id, from_stage, to_stage, "
                    "at, client_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (final_id, competitor_id, row["stage"], to_stage, now_ms, client_at),
                )
                cur.execute("UPDATE finals SET version = version + 1 WHERE id = ?", (final_id,))
            cur.execute("SELECT version FROM finals WHERE id = ?", (final_id,))
            return cur.fetchone()["version"]

    def rename_competitor(self, final_id: str, competitor_id: int, name: str) -> bool:
        with self.cursor(commit=True) as cur:
            cur.execute(
                "UPDATE final_competitors SET name = ? WHERE id = ? AND final_id = ?",
                (name, competitor_id, final_id),
            )
            if cur.rowcount == 0:
                return False
            cur.execute("UPDATE finals SET version = version + 1 WHERE id = ?", (final_id,))
            return True

    def end_final(self, final_id: str, now_ms: int) -> None:
        with self.cursor(commit=True) as cur:
            cur.execute(
                "UPDATE finals SET status = 'ended', ended_at = ?, version = version + 1 "
                "WHERE id = ? AND status = 'active'",
                (now_ms, final_id),
            )

    def delete_test_final(self, final_id: str) -> bool:
        """Delete a final created by the simulation. Real finals are never deleted."""
        with self.cursor(commit=True) as cur:
            cur.execute("DELETE FROM finals WHERE id = ? AND is_test = 1", (final_id,))
            return cur.rowcount > 0


# Global instance
db_manager = DBManager()
