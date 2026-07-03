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
SCHEMA_STATEMENTS: List[str] = [
    # --- existing --------------------------------------------------------
    """
    CREATE TABLE IF NOT EXISTS url_mappings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        short_code TEXT NOT NULL UNIQUE,
        long_url TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    # --- users -----------------------------------------------------------
    """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        display_name TEXT NOT NULL UNIQUE COLLATE NOCASE,
        password_hash TEXT NOT NULL,
        is_admin INTEGER NOT NULL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login_at TIMESTAMP,
        n_tricks_promoted INTEGER NOT NULL DEFAULT 0,
        n_harder INTEGER NOT NULL DEFAULT 0,
        n_tagging INTEGER NOT NULL DEFAULT 0,
        n_throw INTEGER NOT NULL DEFAULT 0,
        n_control INTEGER NOT NULL DEFAULT 0,
        n_control_correct INTEGER NOT NULL DEFAULT 0,
        reliability REAL NOT NULL DEFAULT 0.5
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
        source TEXT NOT NULL DEFAULT 'crowd',
        user_id INTEGER REFERENCES users(id),
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
    # --- crowd pipeline --------------------------------------------------
    """
    CREATE TABLE IF NOT EXISTS pending_tricks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prop_type TEXT NOT NULL,
        props_count INTEGER NOT NULL,
        name TEXT,
        siteswap_x TEXT,
        comment TEXT,
        user_id INTEGER REFERENCES users(id),
        anon_id TEXT,
        status TEXT NOT NULL DEFAULT 'new',
        dup_of INTEGER REFERENCES candidate_tricks(id),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS candidate_tricks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prop_type TEXT NOT NULL,
        props_count INTEGER NOT NULL,
        name TEXT,
        siteswap_x TEXT,
        comment TEXT,
        user_id INTEGER REFERENCES users(id),
        mu REAL NOT NULL,
        sigma REAL NOT NULL,
        n_comparisons INTEGER NOT NULL DEFAULT 0,
        n_cant_judge INTEGER NOT NULL DEFAULT 0,
        n_tag_votes INTEGER NOT NULL DEFAULT 0,
        n_throw_votes INTEGER NOT NULL DEFAULT 0,
        n_flags INTEGER NOT NULL DEFAULT 0,
        submission_count INTEGER NOT NULL DEFAULT 1,
        status TEXT NOT NULL DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        promoted_at TIMESTAMP,
        removed_at TIMESTAMP,
        removed_reason TEXT
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_cand_prop_active "
    "ON candidate_tricks(prop_type) WHERE promoted_at IS NULL AND removed_at IS NULL",
    "CREATE INDEX IF NOT EXISTS idx_cand_active_sigma "
    "ON candidate_tricks(prop_type, sigma, n_comparisons) "
    "WHERE promoted_at IS NULL AND removed_at IS NULL",
    "CREATE INDEX IF NOT EXISTS idx_cand_active_throw "
    "ON candidate_tricks(prop_type, n_throw_votes) "
    "WHERE promoted_at IS NULL AND removed_at IS NULL",
    "CREATE INDEX IF NOT EXISTS idx_cand_name_lc "
    "ON candidate_tricks(prop_type, props_count, name COLLATE NOCASE) "
    "WHERE promoted_at IS NULL AND removed_at IS NULL",
    "CREATE INDEX IF NOT EXISTS idx_cand_ss_lc "
    "ON candidate_tricks(prop_type, props_count, siteswap_x COLLATE NOCASE) "
    "WHERE promoted_at IS NULL AND removed_at IS NULL",
    # --- votes -----------------------------------------------------------
    """
    CREATE TABLE IF NOT EXISTS comparisons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER REFERENCES users(id),
        anon_id TEXT,
        prop_type TEXT NOT NULL,
        left_kind TEXT NOT NULL,
        left_id TEXT NOT NULL,
        right_kind TEXT NOT NULL,
        right_id TEXT NOT NULL,
        winner TEXT NOT NULL,
        is_control INTEGER NOT NULL DEFAULT 0,
        expected_winner TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_cmp_user ON comparisons(user_id, is_control, created_at)",
    "CREATE INDEX IF NOT EXISTS idx_cmp_left ON comparisons(left_kind, left_id)",
    "CREATE INDEX IF NOT EXISTS idx_cmp_right ON comparisons(right_kind, right_id)",
    """
    CREATE TABLE IF NOT EXISTS tag_votes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_id INTEGER NOT NULL REFERENCES candidate_tricks(id),
        user_id INTEGER REFERENCES users(id),
        anon_id TEXT,
        category TEXT NOT NULL,
        tag TEXT NOT NULL,
        vote INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(candidate_id, user_id, anon_id, tag)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_tagv_cand ON tag_votes(candidate_id, category)",
    "CREATE INDEX IF NOT EXISTS idx_tagv_user ON tag_votes(user_id, created_at)",
    """
    CREATE TABLE IF NOT EXISTS throw_votes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_id INTEGER NOT NULL REFERENCES candidate_tricks(id),
        user_id INTEGER REFERENCES users(id),
        anon_id TEXT,
        max_throw INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(candidate_id, user_id, anon_id)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_throwv_cand ON throw_votes(candidate_id)",
    "CREATE INDEX IF NOT EXISTS idx_throwv_user ON throw_votes(user_id, created_at)",
    """
    CREATE TABLE IF NOT EXISTS trick_flags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_id INTEGER NOT NULL REFERENCES candidate_tricks(id),
        user_id INTEGER NOT NULL REFERENCES users(id),
        reason TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(candidate_id, user_id)
    )
    """,
    # --- leaderboard cache & meta ---------------------------------------
    """
    CREATE TABLE IF NOT EXISTS leaderboard_cache (
        kind TEXT NOT NULL,
        period TEXT NOT NULL,
        rank INTEGER NOT NULL,
        user_id INTEGER NOT NULL REFERENCES users(id),
        score REAL NOT NULL,
        computed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (kind, period, rank)
    )
    """,
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
    # Lightweight forward-only migrations for columns added after first
    # deploy. SQLite ``ALTER TABLE ADD COLUMN`` is cheap and idempotent
    # when guarded by a pragma check.
    _MIGRATIONS = [
        ("candidate_tricks", "status",
         "ALTER TABLE candidate_tricks ADD COLUMN status TEXT NOT NULL DEFAULT 'active'"),
    ]

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
            for table, col, ddl in self._MIGRATIONS:
                cur.execute(f"PRAGMA table_info({table})")
                if not any(r["name"] == col for r in cur.fetchall()):
                    cur.execute(ddl)
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
        source: str = "crowd",
        user_id: Optional[int] = None,
    ) -> Optional[int]:
        """Insert a master trick. Returns row id, or None on UNIQUE conflict."""
        with self.cursor(commit=True) as cur:
            try:
                cur.execute(
                    """
                    INSERT INTO tricks
                        (prop_type, props_count, name, siteswap_x, difficulty,
                         tags, max_throw, comment, source, user_id, promoted_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """,
                    (prop_type, props_count, name, siteswap_x, difficulty,
                     tags, max_throw, comment, source, user_id),
                )
                return cur.lastrowid
            except sqlite3.IntegrityError:
                return None

    # ------------------------------------------------------------------
    # pending / candidate pipeline
    # ------------------------------------------------------------------
    def add_pending_trick(self, *, prop_type: str, props_count: int,
                          name: Optional[str], siteswap_x: Optional[str],
                          comment: Optional[str], user_id: Optional[int],
                          anon_id: Optional[str]) -> int:
        with self.cursor(commit=True) as cur:
            cur.execute(
                """
                INSERT INTO pending_tricks
                    (prop_type, props_count, name, siteswap_x, comment, user_id, anon_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (prop_type, props_count, name, siteswap_x, comment, user_id, anon_id),
            )
            return cur.lastrowid

    def mark_pending(self, pending_id: int, *, status: str,
                     dup_of: Optional[int] = None) -> None:
        with self.cursor(commit=True) as cur:
            cur.execute(
                "UPDATE pending_tricks SET status = ?, dup_of = ? WHERE id = ?",
                (status, dup_of, pending_id),
            )

    def find_candidate_match(self, *, prop_type: str, props_count: int,
                             name: Optional[str], siteswap_x: Optional[str]
                             ) -> Optional[Dict[str, Any]]:
        """Match an active candidate by Trick.__eq__ semantics:
        same props_count AND (same name OR same siteswap_x)."""
        with self.cursor() as cur:
            cur.execute(
                """
                SELECT * FROM candidate_tricks
                WHERE prop_type = ?
                  AND props_count = ?
                  AND promoted_at IS NULL
                  AND removed_at IS NULL
                  AND (
                        (? IS NOT NULL AND LOWER(name) = LOWER(?))
                     OR (? IS NOT NULL AND LOWER(siteswap_x) = LOWER(?))
                  )
                LIMIT 1
                """,
                (prop_type, props_count, name, name, siteswap_x, siteswap_x),
            )
            row = cur.fetchone()
            return dict(row) if row else None

    def bump_candidate_submission(self, candidate_id: int) -> None:
        with self.cursor(commit=True) as cur:
            cur.execute(
                "UPDATE candidate_tricks SET submission_count = submission_count + 1 "
                "WHERE id = ?",
                (candidate_id,),
            )

    def add_candidate_trick(self, *, prop_type: str, props_count: int,
                            name: Optional[str], siteswap_x: Optional[str],
                            comment: Optional[str], user_id: Optional[int],
                            mu: float, sigma: float) -> int:
        with self.cursor(commit=True) as cur:
            cur.execute(
                """
                INSERT INTO candidate_tricks
                    (prop_type, props_count, name, siteswap_x, comment, user_id, mu, sigma)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (prop_type, props_count, name, siteswap_x, comment, user_id, mu, sigma),
            )
            return cur.lastrowid

    def mean_difficulty(self, prop_type: str, props_count: int) -> Optional[float]:
        """Mean master difficulty for (prop, props_count); falls back to prop mean."""
        with self.cursor() as cur:
            cur.execute(
                "SELECT AVG(difficulty) AS m FROM tricks "
                "WHERE prop_type = ? AND props_count = ?",
                (prop_type, props_count),
            )
            row = cur.fetchone()
            if row and row["m"] is not None:
                return float(row["m"])
            cur.execute(
                "SELECT AVG(difficulty) AS m FROM tricks WHERE prop_type = ?",
                (prop_type,),
            )
            row = cur.fetchone()
            return float(row["m"]) if row and row["m"] is not None else None

    def get_active_candidates(self, prop_type: str) -> List[Dict[str, Any]]:
        with self.cursor() as cur:
            cur.execute(
                "SELECT * FROM candidate_tricks "
                "WHERE prop_type = ? AND promoted_at IS NULL AND removed_at IS NULL "
                "ORDER BY sigma DESC, n_comparisons ASC",
                (prop_type,),
            )
            return [dict(r) for r in cur.fetchall()]

    def get_candidate(self, candidate_id: int) -> Optional[Dict[str, Any]]:
        with self.cursor() as cur:
            cur.execute("SELECT * FROM candidate_tricks WHERE id = ?", (candidate_id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def update_candidate_rating(self, candidate_id: int, *, mu: float,
                                sigma: float, inc_comparisons: int = 0,
                                inc_cant_judge: int = 0) -> None:
        with self.cursor(commit=True) as cur:
            cur.execute(
                "UPDATE candidate_tricks "
                "SET mu = ?, sigma = ?, "
                "    n_comparisons = n_comparisons + ?, "
                "    n_cant_judge = n_cant_judge + ? "
                "WHERE id = ?",
                (mu, sigma, inc_comparisons, inc_cant_judge, candidate_id),
            )

    def get_master_trick(self, trick_id: int) -> Optional[Dict[str, Any]]:
        with self.cursor() as cur:
            cur.execute(
                "SELECT id, prop_type, props_count, name, siteswap_x, difficulty, "
                "       tags, max_throw "
                "FROM tricks WHERE id = ?",
                (trick_id,),
            )
            row = cur.fetchone()
            return dict(row) if row else None

    def find_master_match(self, *, prop_type: str, props_count: int,
                          name: Optional[str], siteswap_x: Optional[str]
                          ) -> Optional[Dict[str, Any]]:
        """Indexed dedup lookup against master tricks. Returns the full row."""
        with self.cursor() as cur:
            cur.execute(
                """
                SELECT t.id, t.prop_type, t.props_count, t.name, t.siteswap_x,
                       t.difficulty, t.tags, t.max_throw, t.comment, t.source,
                       u.display_name AS suggested_by
                FROM tricks t LEFT JOIN users u ON u.id = t.user_id
                WHERE t.prop_type = ? AND t.props_count = ?
                  AND ((? IS NOT NULL AND t.name = ? COLLATE NOCASE)
                    OR (? IS NOT NULL AND t.siteswap_x = ? COLLATE NOCASE))
                LIMIT 1
                """,
                (prop_type, props_count, name, name, siteswap_x, siteswap_x),
            )
            row = cur.fetchone()
            return dict(row) if row else None

    # ---- bounded selection for pair_picker (scale-safe) --------------
    def pick_candidates_for_compare(self, prop_type: str, *, exclude_user: int,
                                    limit: int, pool_factor: int = 8
                                    ) -> List[Dict[str, Any]]:
        """Pull a wider top-σ pool, then weighted-random sample so players
        see variety while high-uncertainty candidates still dominate."""
        import random as _r
        with self.cursor() as cur:
            cur.execute(
                "SELECT id, props_count, name, siteswap_x, mu, sigma, user_id "
                "FROM candidate_tricks "
                "WHERE prop_type = ? AND promoted_at IS NULL AND removed_at IS NULL "
                "  AND (user_id IS NULL OR user_id != ?) "
                "ORDER BY sigma DESC, n_comparisons ASC LIMIT ?",
                (prop_type, exclude_user, limit * pool_factor),
            )
            pool = [dict(r) for r in cur.fetchall()]
        if len(pool) <= limit:
            _r.shuffle(pool)
            return pool
        weights = [max(1.0, r["sigma"]) ** 1.5 for r in pool]
        picked: list[dict] = []
        idxs = list(range(len(pool)))
        for _ in range(limit):
            i = _r.choices(idxs, weights=[weights[j] for j in idxs], k=1)[0]
            picked.append(pool[i])
            idxs.remove(i)
        return picked

    def pick_candidates_for_metadata(self, prop_type: str, *, exclude_user: int,
                                     max_sigma: float, order: str,
                                     limit: int, pool_factor: int = 8
                                     ) -> List[Dict[str, Any]]:
        import random as _r
        order_sql = {
            "tag":   "n_tag_votes ASC, sigma ASC",
            "throw": "n_throw_votes ASC, sigma ASC",
        }[order]
        with self.cursor() as cur:
            cur.execute(
                "SELECT id, props_count, name, siteswap_x, mu, sigma, user_id, "
                "       n_tag_votes, n_throw_votes "
                "FROM candidate_tricks "
                "WHERE prop_type = ? AND promoted_at IS NULL AND removed_at IS NULL "
                "  AND sigma <= ? AND (user_id IS NULL OR user_id != ?) "
                f"ORDER BY {order_sql} LIMIT ?",
                (prop_type, max_sigma, exclude_user, limit * pool_factor),
            )
            pool = [dict(r) for r in cur.fetchall()]
        if len(pool) <= limit:
            _r.shuffle(pool)
            return pool
        return _r.sample(pool, limit)

    def random_anchor_pair(self, prop_type: str, *, min_gap: int
                           ) -> Optional[tuple[Dict[str, Any], Dict[str, Any]]]:
        """One random anchor pair with |Δdifficulty| ≥ min_gap, preferring
        same props_count. Bounded: two indexed point queries."""
        with self.cursor() as cur:
            cur.execute(
                "SELECT id, props_count, name, siteswap_x, difficulty FROM tricks "
                "WHERE prop_type = ? ORDER BY RANDOM() LIMIT 1",
                (prop_type,),
            )
            a = cur.fetchone()
            if not a:
                return None
            a = dict(a)
            cur.execute(
                "SELECT id, props_count, name, siteswap_x, difficulty FROM tricks "
                "WHERE prop_type = ? AND props_count = ? "
                "  AND (difficulty <= ? OR difficulty >= ?) AND id != ? "
                "ORDER BY RANDOM() LIMIT 1",
                (prop_type, a["props_count"],
                 a["difficulty"] - min_gap, a["difficulty"] + min_gap, a["id"]),
            )
            b = cur.fetchone()
            if not b:
                cur.execute(
                    "SELECT id, props_count, name, siteswap_x, difficulty FROM tricks "
                    "WHERE prop_type = ? "
                    "  AND (difficulty <= ? OR difficulty >= ?) AND id != ? "
                    "ORDER BY RANDOM() LIMIT 1",
                    (prop_type, a["difficulty"] - min_gap,
                     a["difficulty"] + min_gap, a["id"]),
                )
                b = cur.fetchone()
            return (a, dict(b)) if b else None

    def anchor_near(self, prop_type: str, *, mu: float, props_count: int,
                    window: int) -> Optional[Dict[str, Any]]:
        with self.cursor() as cur:
            cur.execute(
                "SELECT id, props_count, name, siteswap_x, difficulty FROM tricks "
                "WHERE prop_type = ? AND props_count = ? "
                "  AND difficulty BETWEEN ? AND ? "
                "ORDER BY RANDOM() LIMIT 1",
                (prop_type, props_count, mu - window, mu + window),
            )
            row = cur.fetchone()
            if row:
                return dict(row)
            cur.execute(
                "SELECT id, props_count, name, siteswap_x, difficulty FROM tricks "
                "WHERE prop_type = ? ORDER BY ABS(difficulty - ?) LIMIT 1",
                (prop_type, mu),
            )
            row = cur.fetchone()
            return dict(row) if row else None

    def random_anchor_with_tags(self, prop_type: str) -> Optional[Dict[str, Any]]:
        with self.cursor() as cur:
            cur.execute(
                "SELECT id, props_count, name, siteswap_x, difficulty, tags, max_throw "
                "FROM tricks WHERE prop_type = ? AND tags != '' "
                "ORDER BY RANDOM() LIMIT 1",
                (prop_type,),
            )
            row = cur.fetchone()
            return dict(row) if row else None

    def random_anchor_with_throw(self, prop_type: str) -> Optional[Dict[str, Any]]:
        with self.cursor() as cur:
            cur.execute(
                "SELECT id, props_count, name, siteswap_x, difficulty, tags, max_throw "
                "FROM tricks WHERE prop_type = ? AND max_throw IS NOT NULL "
                "ORDER BY RANDOM() LIMIT 1",
                (prop_type,),
            )
            row = cur.fetchone()
            return dict(row) if row else None

    # ---- need-score aggregates (scale-safe) --------------------------
    def need_stats(self, prop_type: str, *, promote_max_sigma: float,
                   tag_unlock_sigma: float, promote_min_cmp: int,
                   min_tag_votes: int, n_cats: int,
                   min_throw_votes: int) -> Dict[str, int]:
        """Single-pass aggregates for compute_needs(). All bounds come from
        constants (never user input)."""
        with self.cursor() as cur:
            cur.execute(
                """
                SELECT
                  SUM(CASE WHEN sigma > :pmax THEN 1 ELSE 0 END) AS h_backlog,
                  SUM(CASE WHEN sigma > :pmax
                           THEN MAX(0, :mincmp - n_comparisons) ELSE 0 END) AS h_def,
                  SUM(CASE WHEN sigma <= :tlock THEN 1 ELSE 0 END) AS t_backlog,
                  SUM(CASE WHEN sigma <= :tlock
                           THEN MAX(0, :mintag - n_tag_votes) ELSE 0 END) AS t_def,
                  SUM(CASE WHEN sigma <= :tlock
                           THEN MAX(0, :minthrow - n_throw_votes) ELSE 0 END) AS w_def
                FROM candidate_tricks
                WHERE prop_type = :prop AND promoted_at IS NULL AND removed_at IS NULL
                """,
                {
                    "prop": prop_type, "pmax": promote_max_sigma,
                    "tlock": tag_unlock_sigma, "mincmp": promote_min_cmp,
                    "mintag": min_tag_votes * n_cats, "minthrow": min_throw_votes,
                },
            )
            row = dict(cur.fetchone())
        return {k: int(v or 0) for k, v in row.items()}

    # ---- tag / throw votes ------------------------------------------
    def record_tag_votes(self, *, candidate_id: int, user_id: Optional[int],
                         anon_id: Optional[str], category: str,
                         votes: Dict[str, int]) -> None:
        """votes: {tag_value: +1/-1/0}. Replaces any prior vote by this rater
        for these tags via INSERT OR REPLACE."""
        with self.cursor(commit=True) as cur:
            for tag, vote in votes.items():
                cur.execute(
                    "INSERT OR REPLACE INTO tag_votes "
                    "(candidate_id, user_id, anon_id, category, tag, vote) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (candidate_id, user_id, anon_id, category, tag, int(vote)),
                )
            cur.execute(
                "UPDATE candidate_tricks SET n_tag_votes = "
                "  (SELECT COUNT(DISTINCT COALESCE('u:'||user_id,'a:'||anon_id)||':'||category) "
                "   FROM tag_votes WHERE candidate_id = ?) "
                "WHERE id = ?",
                (candidate_id, candidate_id),
            )

    def tag_category_coverage(self, candidate_id: int) -> Dict[str, int]:
        """{category: distinct-rater count} for this candidate."""
        with self.cursor() as cur:
            cur.execute(
                "SELECT category, "
                "       COUNT(DISTINCT COALESCE('u:'||user_id,'a:'||anon_id)) AS n "
                "FROM tag_votes WHERE candidate_id = ? GROUP BY category",
                (candidate_id,),
            )
            return {r["category"]: r["n"] for r in cur.fetchall()}

    def tag_vote_summary(self, candidate_id: int) -> List[Dict[str, Any]]:
        """Reliability-weighted +/- per tag for resolve_tags()."""
        with self.cursor() as cur:
            cur.execute(
                """
                SELECT tv.tag,
                       SUM(CASE WHEN tv.vote > 0
                                THEN COALESCE(MAX(0.0, 2*u.reliability-1), ?) ELSE 0 END) AS w_pos,
                       SUM(CASE WHEN tv.vote < 0
                                THEN COALESCE(MAX(0.0, 2*u.reliability-1), ?) ELSE 0 END) AS w_neg,
                       SUM(CASE WHEN tv.vote != 0 THEN 1 ELSE 0 END) AS n_nonzero
                FROM tag_votes tv
                LEFT JOIN users u ON u.id = tv.user_id
                WHERE tv.candidate_id = ?
                GROUP BY tv.tag
                """,
                # anon weight applied when user row is NULL
                (0.0, 0.0, candidate_id),
            )
            return [dict(r) for r in cur.fetchall()]

    def record_throw_vote(self, *, candidate_id: int, user_id: Optional[int],
                          anon_id: Optional[str], max_throw: Optional[int]) -> None:
        with self.cursor(commit=True) as cur:
            cur.execute(
                "INSERT OR REPLACE INTO throw_votes "
                "(candidate_id, user_id, anon_id, max_throw) VALUES (?, ?, ?, ?)",
                (candidate_id, user_id, anon_id, max_throw),
            )
            cur.execute(
                "UPDATE candidate_tricks SET n_throw_votes = "
                "  (SELECT COUNT(*) FROM throw_votes WHERE candidate_id = ?) "
                "WHERE id = ?",
                (candidate_id, candidate_id),
            )

    def throw_vote_summary(self, candidate_id: int) -> List[Dict[str, Any]]:
        with self.cursor() as cur:
            cur.execute(
                """
                SELECT tv.max_throw,
                       COALESCE(MAX(0.0, 2*u.reliability-1), 0.3) AS w
                FROM throw_votes tv
                LEFT JOIN users u ON u.id = tv.user_id
                WHERE tv.candidate_id = ?
                """,
                (candidate_id,),
            )
            return [dict(r) for r in cur.fetchall()]

    # ---- flags -------------------------------------------------------
    def add_flag(self, *, candidate_id: int, user_id: int, reason: str) -> bool:
        """Record a flag. Returns True if a new row was inserted (False if
        this user already flagged this candidate)."""
        with self.cursor(commit=True) as cur:
            cur.execute(
                "INSERT OR IGNORE INTO trick_flags (candidate_id, user_id, reason) "
                "VALUES (?, ?, ?)",
                (candidate_id, user_id, reason),
            )
            if cur.rowcount == 0:
                return False
            cur.execute(
                "UPDATE candidate_tricks SET n_flags = n_flags + 1 WHERE id = ?",
                (candidate_id,),
            )
            return True

    def distinct_raters_seen(self, candidate_id: int) -> int:
        """How many distinct people have been served this candidate in any
        game so far. Union of comparisons + tag_votes + throw_votes +
        trick_flags (a flag counts as an exposure)."""
        cid = str(candidate_id)
        with self.cursor() as cur:
            cur.execute(
                """
                SELECT COUNT(*) AS c FROM (
                    SELECT COALESCE('u:'||user_id, 'a:'||anon_id) AS who
                    FROM comparisons
                    WHERE (left_kind='candidate'  AND left_id  = ?)
                       OR (right_kind='candidate' AND right_id = ?)
                    UNION
                    SELECT COALESCE('u:'||user_id, 'a:'||anon_id)
                    FROM tag_votes WHERE candidate_id = ?
                    UNION
                    SELECT COALESCE('u:'||user_id, 'a:'||anon_id)
                    FROM throw_votes WHERE candidate_id = ?
                    UNION
                    SELECT 'u:'||user_id
                    FROM trick_flags WHERE candidate_id = ?
                )
                """,
                (cid, cid, candidate_id, candidate_id, candidate_id),
            )
            return cur.fetchone()["c"]

    def top_flag_reason(self, candidate_id: int) -> Optional[str]:
        with self.cursor() as cur:
            cur.execute(
                "SELECT reason, COUNT(*) AS c FROM trick_flags "
                "WHERE candidate_id = ? GROUP BY reason ORDER BY c DESC LIMIT 1",
                (candidate_id,),
            )
            row = cur.fetchone()
            return row["reason"] if row else None

    def queue_for_deletion(self, candidate_id: int, *, reason: str) -> None:
        """Move an active candidate to ``pending_deletion``. Votes are
        purged by the caller; the candidate row is kept for admin review."""
        with self.cursor(commit=True) as cur:
            cur.execute(
                "UPDATE candidate_tricks "
                "SET status = 'pending_deletion', "
                "    removed_at = CURRENT_TIMESTAMP, removed_reason = ? "
                "WHERE id = ? AND status = 'active'",
                (reason, candidate_id),
            )

    # Back-compat alias (older call sites).
    def set_candidate_removed(self, candidate_id: int, *, reason: str) -> None:
        self.queue_for_deletion(candidate_id, reason=reason)

    def delete_candidate_permanently(self, candidate_id: int) -> None:
        """Terminal state. Row is kept (audit) but can never return."""
        with self.cursor(commit=True) as cur:
            cur.execute(
                "UPDATE candidate_tricks SET status = 'deleted' "
                "WHERE id = ? AND status = 'pending_deletion'",
                (candidate_id,),
            )

    def mark_candidate_promoted(self, candidate_id: int) -> None:
        with self.cursor(commit=True) as cur:
            cur.execute(
                "UPDATE candidate_tricks "
                "SET status = 'promoted', promoted_at = CURRENT_TIMESTAMP "
                "WHERE id = ?",
                (candidate_id,),
            )

    def purge_candidate_votes(self, candidate_id: int) -> Dict[str, int]:
        """Delete every raw vote/flag/comparison row that references this
        candidate. Called immediately when a candidate becomes *settled*
        (promoted or removed) — at that point its mu/sigma/tags/max_throw
        are frozen and the raw rows serve no further purpose.

        Safe by construction: only ever called with a settled candidate id.
        Note: a comparison row touching *two* candidates is deleted as soon
        as either side settles; the surviving side's mu/sigma was already
        applied online so nothing is lost.
        """
        cid_s = str(candidate_id)
        deleted: Dict[str, int] = {}
        with self.cursor(commit=True) as cur:
            cur.execute(
                "DELETE FROM comparisons "
                "WHERE (left_kind='candidate'  AND left_id  = ?) "
                "   OR (right_kind='candidate' AND right_id = ?)",
                (cid_s, cid_s),
            )
            deleted["comparisons"] = cur.rowcount
            cur.execute("DELETE FROM tag_votes   WHERE candidate_id = ?", (candidate_id,))
            deleted["tag_votes"] = cur.rowcount
            cur.execute("DELETE FROM throw_votes WHERE candidate_id = ?", (candidate_id,))
            deleted["throw_votes"] = cur.rowcount
            cur.execute("DELETE FROM trick_flags WHERE candidate_id = ?", (candidate_id,))
            deleted["trick_flags"] = cur.rowcount
        return deleted

    def restore_candidate(self, candidate_id: int) -> bool:
        """pending_deletion → active. Votes were purged when queued, so
        reset the derived counters. Returns False if not restorable
        (already promoted/deleted/active)."""
        with self.cursor(commit=True) as cur:
            cur.execute(
                "UPDATE candidate_tricks "
                "SET status = 'active', removed_at = NULL, removed_reason = NULL, "
                "    n_flags = 0, n_comparisons = 0, n_cant_judge = 0, "
                "    n_tag_votes = 0, n_throw_votes = 0 "
                "WHERE id = ? AND status = 'pending_deletion'",
                (candidate_id,),
            )
            return cur.rowcount > 0

    _STATE_QUERY = {
        "pool":             ("status = 'active'",           "sigma DESC, n_comparisons ASC"),
        "pending_deletion": ("status = 'pending_deletion'", "removed_at DESC"),
        "deleted":          ("status = 'deleted'",          "removed_at DESC"),
        "promoted":         ("status = 'promoted'",         "promoted_at DESC"),
    }

    def get_candidates_by_state(self, prop_type: str, state: str,
                                *, limit: int = 500) -> List[Dict[str, Any]]:
        if state not in self._STATE_QUERY:
            raise ValueError(state)
        where, order = self._STATE_QUERY[state]
        with self.cursor() as cur:
            cur.execute(
                f"SELECT * FROM candidate_tricks WHERE prop_type = ? AND {where} "
                f"ORDER BY {order} LIMIT ?",
                (prop_type, limit),
            )
            return [dict(r) for r in cur.fetchall()]

    # ---- comparisons / reliability -----------------------------------
    def record_comparison(self, *, user_id: Optional[int], anon_id: Optional[str],
                          prop_type: str, left_kind: str, left_id: str,
                          right_kind: str, right_id: str, winner: str,
                          is_control: bool, expected_winner: Optional[str]) -> int:
        with self.cursor(commit=True) as cur:
            cur.execute(
                """
                INSERT INTO comparisons
                    (user_id, anon_id, prop_type, left_kind, left_id,
                     right_kind, right_id, winner, is_control, expected_winner)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (user_id, anon_id, prop_type, left_kind, left_id,
                 right_kind, right_id, winner, 1 if is_control else 0,
                 expected_winner),
            )
            return cur.lastrowid

    def bump_user_game_counter(self, user_id: int, *, game: str) -> None:
        col = {"harder": "n_harder", "tagging": "n_tagging", "throw": "n_throw"}.get(game)
        if not col:
            return
        with self.cursor(commit=True) as cur:
            cur.execute(f"UPDATE users SET {col} = {col} + 1 WHERE id = ?", (user_id,))

    # ---- user admin management --------------------------------------
    def list_users(self, *, limit: int = 500) -> List[Dict[str, Any]]:
        with self.cursor() as cur:
            cur.execute(
                "SELECT id, display_name, is_admin, created_at, last_login_at, "
                "       n_tricks_promoted, n_harder, n_tagging, n_throw, reliability "
                "FROM users ORDER BY is_admin DESC, display_name COLLATE NOCASE LIMIT ?",
                (limit,),
            )
            return [dict(r) for r in cur.fetchall()]

    def set_user_admin(self, user_id: int, *, is_admin: bool) -> bool:
        with self.cursor(commit=True) as cur:
            cur.execute("UPDATE users SET is_admin = ? WHERE id = ?",
                        (1 if is_admin else 0, user_id))
            return cur.rowcount > 0

    def update_user_reliability(self, user_id: int, *, correct: bool) -> float:
        """Record a control-question outcome and return the new reliability."""
        with self.cursor(commit=True) as cur:
            cur.execute(
                "UPDATE users SET n_control = n_control + 1, "
                "n_control_correct = n_control_correct + ? WHERE id = ?",
                (1 if correct else 0, user_id),
            )
            cur.execute(
                "SELECT n_control, n_control_correct FROM users WHERE id = ?",
                (user_id,),
            )
            row = cur.fetchone()
            # Laplace-smoothed accuracy.
            rel = (row["n_control_correct"] + 1) / (row["n_control"] + 2)
            cur.execute("UPDATE users SET reliability = ? WHERE id = ?", (rel, user_id))
            return rel

    # ------------------------------------------------------------------
    # url shortener (unchanged behaviour)
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
