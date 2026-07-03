# JuggleFit Crowd Pipeline — Backend Reference

Complete reference for the crowdsourced trick collection / calibration
system: data model, query patterns, request lifecycle, scaling
characteristics, and operational hooks.

---

## 1. Architecture at a glance

```
                       ┌──────────────────────────────────────────────────────────┐
                       │                    SQLite  (jugglefit.db)                │
  CSV seed files ────▶ │  tricks ◀──promote── candidate_tricks ◀──intake── pending│
  (first-boot only)    │    ▲                       ▲                             │
                       │    │                       │ votes/flags                 │
                       │  users   comparisons  tag_votes  throw_votes  trick_flags│
                       │  url_mappings   leaderboard_cache   meta                 │
                       └──────────────────────────────────────────────────────────┘
                              │ load_tricks_from_db()         │ backup_db()
                              ▼                               ▼
                  ALL_PROPS_TRICKS (in-mem, route generator)  backups/*.db + *.csv
                                                              └─▶ rclone → off-box
```

* **Source of truth:** SQLite (`database_data/jugglefit.db`). CSV files
  under `hardcoded_database/tricks/` are **seed-in / export-out** only.
* **Process model:** single Flask app (gunicorn in prod). Every DB call
  opens a fresh `sqlite3` connection (`db_manager.cursor()` context
  manager) — no connection pooling, no ORM.
* **Hot in-memory cache:** `pylib/utils/trick_registry.ALL_PROPS_TRICKS`
  holds the full master trick list per prop for the route generator.
  Mutated in place by `reload_prop()` after a promotion.

---

## 2. Module map

| Module | Responsibility |
|---|---|
| `database/db_manager.py` | Schema DDL, all SQL, `DBManager` singleton |
| `database/seed.py` | Per-prop idempotent CSV → `tricks` import |
| `database/backup.py` | Online snapshot + CSV export + retention pruning of snapshots |
| `database/prune.py` | Raw-vote retention (settled + aged) + `VACUUM` |
| `pylib/auth.py` | `User` dataclass, `register/authenticate`, session helpers, `@login_required_user` |
| `pylib/rating/intake.py` | `submit_and_intake()` — pending → candidate dedup/creation |
| `pylib/rating/tasks.py` | `sign/unsign` itsdangerous task tokens (1 h TTL) |
| `pylib/rating/elo.py` | `apply_comparison()` — online μ/σ update |
| `pylib/rating/pair_picker.py` | `build_{compare,tag,throw}_set()` — bounded SQL selection |
| `pylib/rating/answer.py` | `handle_answer()` — dispatch by token kind, write raw + apply delta |
| `pylib/rating/aggregate.py` | `resolve_tags/resolve_max_throw/missing_tag_categories` |
| `pylib/rating/flags.py` | `record_flag()` + removal rule |
| `pylib/rating/need.py` | `compute_needs()` — single-aggregate hub ordering |
| `pylib/rating/promote.py` | Gate evaluation + `promote_candidate()` |
| `pylib/rating/leaderboard.py` | `get_board(kind, period)` |
| `pylib/utils/trick_registry.py` | In-mem master cache + `reload_prop()` |
| `blueprints/auth.py` | `/auth/*` pages |
| `blueprints/games.py` | `/contribute/games/*` pages + `/api/games/*` |
| `app.py` | Everything else (admin, leaderboard route, suggest API, legacy routes) |

---

## 3. Database schema

All DDL lives in `database/db_manager.py:SCHEMA_STATEMENTS` and is
applied with `CREATE … IF NOT EXISTS` on every process start
(`DBManager.__init__ → init_db`).

### 3.1 `users`
| col | type | notes |
|---|---|---|
| `id` | INTEGER PK | |
| `display_name` | TEXT NOT NULL **UNIQUE COLLATE NOCASE** | 3–24 chars `[A-Za-z0-9_ ]` |
| `password_hash` | TEXT NOT NULL | `werkzeug.security` pbkdf2:sha256 |
| `is_admin` | INT 0/1 | grants admin routes without env password |
| `created_at`, `last_login_at` | TIMESTAMP | |
| `n_tricks_promoted` | INT | bumped on promote |
| `n_harder` / `n_tagging` / `n_throw` | INT | bumped per **data** answer (not control) |
| `n_control` / `n_control_correct` | INT | control-question tally |
| `reliability` | REAL | Laplace `(correct+1)/(total+2)`; recomputed on every control |

### 3.2 `tricks` (master)
| col | type | notes |
|---|---|---|
| `id` | INTEGER PK | |
| `prop_type` | TEXT | `Prop.value` |
| `props_count` | INT | |
| `name`, `siteswap_x` | TEXT NULL | ≥1 required (app-enforced) |
| `difficulty` | INT 0–100 | frozen at promote / seed |
| `tags` | TEXT | `\|`-joined `Tag.value` |
| `max_throw` | INT NULL | |
| `comment` | TEXT NULL | |
| `source` | TEXT | `'seed' \| 'crowd' \| 'admin'` |
| `user_id` | FK users | submitter (crowd only) |
| `created_at`, `promoted_at` | TIMESTAMP | |
| **UNIQUE** | `(prop_type, props_count, name, siteswap_x)` | |

Indexes: `idx_tricks_prop`, `idx_tricks_prop_pc_diff(prop,pc,difficulty)`,
`idx_tricks_name_lc` / `idx_tricks_ss_lc` (NOCASE dedup).

### 3.3 `pending_tricks`
Raw inbox; one row per submission. `status ∈ {new, accepted,
dup_master, dup_candidate}`, `dup_of → candidate_tricks.id`. Pruned
after `PENDING_RETENTION_DAYS=14`.

### 3.4 `candidate_tricks`
| col | type | notes |
|---|---|---|
| `id` PK, `prop_type`, `props_count`, `name`, `siteswap_x`, `comment`, `user_id` | | copied from pending |
| `mu` REAL | current difficulty estimate | init = mean master diff for `(prop,pc)` |
| `sigma` REAL | uncertainty | init `25.0`, ×`0.97` per comparison, floor `1.0` |
| `n_comparisons`, `n_cant_judge`, `n_tag_votes`, `n_throw_votes`, `n_flags`, `submission_count` | INT | denorm counters |
| `created_at`, `promoted_at`, `removed_at`, `removed_reason` | | lifecycle |

A candidate is **active** ⇔ `promoted_at IS NULL AND removed_at IS NULL`;
**settled** otherwise. **Never pruned.**

Partial indexes (all `WHERE promoted_at IS NULL AND removed_at IS NULL`):
`idx_cand_active_sigma(prop,sigma,n_comparisons)`,
`idx_cand_active_throw(prop,n_throw_votes)`,
`idx_cand_name_lc` / `idx_cand_ss_lc`, plus `idx_cand_prop_active`.

### 3.5 `comparisons`
Append-only log of compare answers. `left/right_kind ∈ {anchor,candidate}`,
`*_id` = `tricks.id` or `candidate_tricks.id` (stored as TEXT),
`winner ∈ {left,right,equal,skip}`, `is_control` 0/1, `expected_winner`.
Indexes: `idx_cmp_user(user_id,is_control,created_at)`,
`idx_cmp_left/right(kind,id)`.

### 3.6 `tag_votes`
`(candidate_id, user_id, anon_id, category, tag, vote ∈ {-1,0,+1})`.
`UNIQUE(candidate_id,user_id,anon_id,tag)` → re-vote overwrites via
`INSERT OR REPLACE`. Indexes: `idx_tagv_cand(cand,category)`,
`idx_tagv_user(user,created_at)`.

### 3.7 `throw_votes`
`(candidate_id, user_id, anon_id, max_throw NULL=N/A)`.
`UNIQUE(candidate_id,user_id,anon_id)`. Indexes mirror tag_votes.

### 3.8 `trick_flags`
`(candidate_id, user_id NOT NULL, reason)`.
`UNIQUE(candidate_id,user_id)` — one flag per user per candidate.

### 3.9 `leaderboard_cache`
`(kind, period, rank) PK → (user_id, score, computed_at)`. **Created but
not yet populated** — boards are computed live; reserved for a future
nightly job.

### 3.10 `meta`
`(key PK, value)` — `seeded_from_csv`, `last_backup_at`,
`last_prune_at`, `last_prune_deleted`.

### 3.11 `url_mappings`
Unrelated short-URL feature; unchanged.

---

## 4. Request lifecycles & queries

### 4.1 Submit a trick — `POST /api/suggest_trick`

`app.py` validates: prop ∈ enum, `1 ≤ props_count ≤ 13`, name ≤ 100,
siteswap ≤ 200, comment ≤ 500, name∨siteswap present, captcha if anon.
Then `submit_and_intake()`:

| Step | Query | Index hit |
|---|---|---|
| insert pending | `INSERT INTO pending_tricks …` | — |
| master dedup | `find_master_match`: `SELECT id FROM tricks WHERE prop=? AND pc=? AND (name=? NOCASE OR siteswap=? NOCASE) LIMIT 1` | `idx_tricks_name_lc` / `_ss_lc` |
| candidate dedup | `find_candidate_match`: same predicate on active candidates | `idx_cand_name_lc` / `_ss_lc` |
| init μ | `mean_difficulty`: `AVG(difficulty) WHERE prop=? AND pc=?` (fallback prop-only) | `idx_tricks_prop_pc_diff` |
| insert candidate | `INSERT INTO candidate_tricks … (mu, sigma=25.0)` | — |
| mark pending | `UPDATE pending_tricks SET status=?, dup_of=?` | PK |

Result: `{status: accepted|dup_master|dup_candidate, candidate_id, games_url}`.

### 4.2 Games hub — `GET /api/games/needs?prop=`

`compute_needs()` → **one** aggregate query (`need_stats`):

```sql
SELECT
  SUM(CASE WHEN sigma >  :pmax  THEN 1 ELSE 0 END)                           AS h_backlog,
  SUM(CASE WHEN sigma >  :pmax  THEN MAX(0,:mincmp - n_comparisons) END)     AS h_def,
  SUM(CASE WHEN sigma <= :tlock THEN 1 ELSE 0 END)                           AS t_backlog,
  SUM(CASE WHEN sigma <= :tlock THEN MAX(0,:mintag   - n_tag_votes)   END)   AS t_def,
  SUM(CASE WHEN sigma <= :tlock THEN MAX(0,:minthrow - n_throw_votes) END)   AS w_def
FROM candidate_tricks
WHERE prop_type=:prop AND promoted_at IS NULL AND removed_at IS NULL
```
→ `idx_cand_prop_active`. Weighted by `W_HARDER=1.0 / W_TAG=1.5 /
W_THROW=1.2`, sorted, returned with `{game,title,blurb,backlog,deficit,score,available}`.

### 4.3 Build a task set — `GET /api/games/<game>/next_set?prop=` *(login)*

All three builders are **bounded** — never load full tables.

**compare** (`build_compare_set`):
1. `pick_candidates_for_compare`: `SELECT … FROM candidate_tricks WHERE
   prop=? AND active AND user_id!=? ORDER BY sigma DESC, n_comparisons
   ASC LIMIT 8` → `idx_cand_active_sigma`.
2. Per control slot (×3): `random_anchor_pair` — two `ORDER BY RANDOM()
   LIMIT 1` queries on `tricks` constrained to `|Δdiff| ≥ 15`, prefer
   same `props_count` → `idx_tricks_prop_pc_diff`.
3. Per data slot: `anchor_near` — `SELECT … WHERE prop=? AND pc=? AND
   difficulty BETWEEN μ-10 AND μ+10 ORDER BY RANDOM() LIMIT 1`; fallback
   `ORDER BY ABS(difficulty-μ) LIMIT 1`.
4. Occasional cand-vs-cand from the same shortlist.

**tag** (`build_tag_set`):
1. `pick_candidates_for_metadata(order='tag')`: active, `sigma ≤ 8.0`,
   `ORDER BY n_tag_votes ASC, sigma ASC LIMIT 8`.
2. Control: `random_anchor_with_tags` (`WHERE tags!='' ORDER BY RANDOM()
   LIMIT 1`) → pick a category the anchor actually has, expected =
   anchor.tags ∩ category.
3. Data: per candidate, `missing_tag_categories(cid)` (one
   `tag_category_coverage` query per shortlisted candidate, ≤8) →
   choose least-covered category.

**throw** (`build_throw_set`): same shape; control =
`random_anchor_with_throw` (`WHERE max_throw IS NOT NULL`); candidates
ordered by `n_throw_votes ASC`.

Each task is wrapped in a **signed token** (`tasks.sign`):

```json
{"k":"compare|tag|throw","p":prop,
 "l":{"t":"anchor|candidate","i":id},"r":{…},   // compare only
 "cid":candidate_id, "aid":anchor_id,            // tag/throw
 "cat":category, "tags":[…],                     // tag
 "c":is_control, "e":expected, "cand":[ids]}
```
Client receives only `{kind, task_id, left/right|trick, …, flaggable}` —
control flag and expected answer are hidden inside the token.

### 4.4 Answer — `POST /api/games/answer` *(login)*

`handle_answer(task_id, payload)` → `unsign` → dispatch by `k`:

**compare** (`_handle_compare`):
| step | query |
|---|---|
| log | `record_comparison` INSERT |
| control? | `update_user_reliability`: `UPDATE users SET n_control+=1, n_control_correct+=?`, then `reliability = (c+1)/(n+2)` |
| data, skip | for each candidate side: `update_candidate_rating(mu,sigma,inc_cant_judge=1)` |
| data, vote | `_load_side` (2× point SELECT) → `apply_comparison`:<br>`E_l = 1/(1+10^((μ_r-μ_l)/30))`, `w = max(0, 2·rel-1)`, `K = max(1,σ)·0.8`, `μ += w·K·(S-E)`, `σ *= 0.97`, clamp `[0,100]` → `update_candidate_rating(mu,sigma,inc_comparisons=1)` per candidate side; anchors immutable |
| counter | `bump_user_game_counter('harder')` |

**tag** (`_handle_tag`): control → reliability if `expected ⊆ selected∩shown`.
Data → `record_tag_votes`: one `INSERT OR REPLACE` per shown tag
(`+1`/`-1`/`0`), then recompute `n_tag_votes` from a
`COUNT(DISTINCT rater×category)` subquery; bump `n_tagging`.

**throw** (`_handle_throw`): control → reliability if `|ans-expected|≤1`.
Data (non-skip) → `record_throw_vote` `INSERT OR REPLACE` + recompute
`n_throw_votes`; bump `n_throw`.

### 4.5 Flag — `POST /api/games/flag` *(login)*

`record_flag()` → `unsign` → for each `cand` in token:
`add_flag` (`INSERT OR IGNORE` + `n_flags++` if new) →
removal check: `is_admin` ⇒ instant; else `n_flags ≥ 3 AND
n_flags / distinct_raters_seen(cid) ≥ 0.25`.
`distinct_raters_seen` = `COUNT` over a `UNION` of
`comparisons|tag_votes|throw_votes` filtered to that candidate (uses
`idx_cmp_left/right`, `idx_tagv_cand`, `idx_throwv_cand`).
Removal = `set_candidate_removed` (sets `removed_at`,
`removed_reason = top_flag_reason()`).

### 4.6 Promote — `POST /admin/api/promote/<id>` *(admin)*

`annotate_candidate` evaluates gates (no SQL beyond `get_candidate` +
`tag_category_coverage` + `tag_vote_summary` + `throw_vote_summary`, all
keyed on `candidate_id`):

| gate | rule |
|---|---|
| comparisons | `n_comparisons ≥ 20` |
| sigma | `σ ≤ 6.0` |
| recognition | `(n_cant_judge+n_flags)/(n_comparisons+n_cant_judge+n_flags) < 0.4` |
| tags | every `PROP_RELEVANT_CATEGORIES[prop]` has ≥ 5 distinct raters |
| throw | `n_throw_votes ≥ 5` |
| age | `≥ 48 h` |

`promote_candidate`:
1. `backup_db()` (snapshot + CSV + users CSV + retention prune of snapshots).
2. `insert_trick(source='crowd', user_id=submitter)` — UNIQUE-guarded.
3. `UPDATE candidate_tricks SET promoted_at=now`.
4. `UPDATE users SET n_tricks_promoted+=1`.
5. `reload_prop()` — re-reads `tricks` for that prop into
   `ALL_PROPS_TRICKS` so the route generator sees it immediately.

`resolve_tags(cid)`: per tag, `w_pos/(w_pos+w_neg) ≥ 0.30 AND
n_nonzero ≥ 5` where `w = max(0, 2·reliability-1)` (anon weight 0).
`resolve_max_throw(cid)`: weighted median of non-NULL votes; NULL if
≥60% voted N/A or `<5` votes.

### 4.7 Leaderboard — `GET /api/leaderboard?kind=&period=`

| kind / period | query |
|---|---|
| `tricks` / any | `COUNT(*) FROM tricks JOIN users WHERE source='crowd' [AND created_at≥now-N] GROUP BY user` |
| `harder|tagging|throw` / `all` | **`users.n_* × max(0,2·reliability-1)`** (no raw-table scan; prune-safe) |
| `harder` / `30d` | `SUM(w) FROM comparisons JOIN users WHERE is_control=0 AND created_at≥… GROUP BY user` → `idx_cmp_user` |
| `tagging` / `30d` | `SUM(w)` over `DISTINCT (user,cand,category)` from `tag_votes` → `idx_tagv_user` |
| `throw` / `30d` | `SUM(w) FROM throw_votes …` → `idx_throwv_user` |

Top-20 + caller's rank returned.

---

## 5. HTTP surface

| Method | Route | Auth | Handler |
|---|---|---|---|
| GET/POST | `/auth/register` `/auth/login` | – | `blueprints/auth.py` |
| GET | `/auth/logout` `/auth/profile` | user | |
| GET | `/contribute/add_tricks` | – | `app.py:add_tricks` |
| POST | `/api/suggest_trick` | – (captcha if anon) | `app.py:suggest_trick` |
| GET | `/contribute/games/` | – | `blueprints/games.py:hub` |
| GET | `/contribute/games/{harder,tagging,throw}` | **user** | |
| GET | `/api/games/needs?prop=` | – | `compute_needs` |
| GET | `/api/games/<game>/next_set?prop=` | **user** | `build_set` |
| POST | `/api/games/answer` | **user** | `handle_answer` |
| POST | `/api/games/flag` | **user** | `record_flag` |
| GET | `/api/games/me` | – | user stats or `{logged_in:false}` |
| GET | `/leaderboards` · `/api/leaderboard?kind=&period=` | – | `get_board` |
| GET | `/admin/crowd` | admin | tabbed UI |
| GET | `/admin/api/candidates/<prop>?state=ready\|pool\|removed` | admin | |
| GET | `/admin/api/candidate/<id>` | admin | annotated gates |
| POST | `/admin/api/promote/<id>` | admin | overrides `{difficulty,tags,max_throw}` |
| POST | `/admin/api/reject/<id>` `/admin/api/restore/<id>` | admin | |
| POST | `/admin/api/backup` `/admin/api/prune` | admin | |
| GET | `/admin/suggestions` | – | 302 → `/admin/crowd` (legacy) |

**Auth gates:** `@login_required_user` checks `session['user_id']`
(30-day cookie). Admin `@login_required` accepts either
`users.is_admin` **or** a fresh `session['admin_logged_in_at']` (≤1 h)
set by the env-password `/admin/login`. `?next=` is restricted to
same-site relative paths.

---

## 6. Constants (`pylib/configuration/consts.py`)

| Name | Value | Used by |
|---|---|---|
| `MAX_TRICK_NAME_LENGTH / SITESWAP_X / COMMENT` | 100 / 200 / 500 | submit validation |
| `USERNAME_RE`, `PASSWORD_MIN/MAX_LENGTH` | `[A-Za-z0-9_ ]{3,24}`, 6/128 | auth |
| `USER_SESSION_DAYS`, `ADMIN_SESSION_SECONDS` | 30, 3600 | sessions |
| `RATING_SET_SIZE`, `RATING_CONTROL_FRACTION` | 8, 0.375 | pair_picker |
| `CONTROL_MIN_GAP` | 15 | compare control validity |
| `CANDIDATE_INIT_SIGMA`, `SIGMA_DECAY`, `ELO_SCALE` | 25.0, 0.97, 30.0 | elo |
| `TAG_UNLOCK_SIGMA` | 8.0 | metadata-eligibility |
| `TAG_VOTE_THRESHOLD`, `MIN_TAG_VOTES`, `MIN_THROW_VOTES` | 0.30, 5, 5 | aggregate |
| `PROMOTE_MIN_COMPARISONS / MAX_SIGMA / MAX_UNKNOWN_RATIO / MIN_AGE_HOURS` | 20 / 6.0 / 0.4 / 48 | promote gates |
| `FLAG_REASONS`, `FLAG_REMOVE_MIN`, `FLAG_REMOVE_RATIO` | 4 reasons, 5, 0.10 | queue for deletion when ≥5 flags AND >10% of exposures |
| `W_HARDER / W_TAG / W_THROW` | 1.0 / 1.5 / 1.2 | hub ordering |
| `LEADERBOARD_TOP_N`, `LEADERBOARD_PERIODS` | 20, `{all,30d}` | leaderboard |
| `RAW_VOTE_RETENTION_DAYS`, `PENDING_RETENTION_DAYS`, `PRUNE_BATCH_SIZE` | 45, 14, 5000 | prune |
| `THROW_STEPPER_MIN/MAX` | 3 / 15 | throw UI |
| `PROP_RELEVANT_CATEGORIES` | per-prop `TagCategory` list | tag game / promote gate |
| `ANON_VOTE_WEIGHT` | 0.3 | **unused** since games are login-only (kept for `throw_vote_summary` anon fallback) |

---

## 7. Startup / lifecycle

1. `database.db_manager` import → `DBManager()` → `init_db()` (DDL).
2. `pylib.utils.trick_registry` import → `seed_tricks_from_csv()` (per-prop:
   seeds only props with 0 rows) → `load_tricks_from_db()` × props →
   `ALL_PROPS_TRICKS/SETTINGS/JSON`.
3. `app.py` registers blueprints (`auth_bp`, `games_bp`, `games_api`, `api`).
4. `wsgi.py` (gunicorn) additionally calls `init_db()` +
   `delete_inactive_urls()` — both idempotent.

Adding a new prop = add enum value + (optionally) a CSV file → next
restart seeds just that prop.

---

## 8. Backup & retention

### 8.1 `database/backup.py:backup_db()`
1. `sqlite3.Connection.backup()` → `backups/jugglefit_<ts>.db` (online-safe).
2. `_prune()` local snapshots: keep newest `BACKUP_KEEP_LOCAL` (default 1).
3. `meta.last_backup_at = ts`.

Triggers: pre-promote, `POST /admin/api/backup`, daily `backup.sh`,
`python -m database.backup`.

### 8.2 Off-box (`deploy/oci-ubuntu/backup.sh`)
`snapshot in-container → docker cp to host /tmp → rclone copy → remote
prune (14 daily + 8 weekly) → rm host copy → prune()`. Uses `rclone
copy` + per-file `deletefile` (not `sync`) so partial failures don't
wipe the remote. **No-op** if `RCLONE_REMOTE` unset or `rclone` missing.
Host setup: `apt install rclone; rclone config; echo
RCLONE_REMOTE=gdrive:jugglefit-backups >> .env`.

### 8.3 `database/prune.py:prune()`
Primary vote/flag deletion happens **synchronously at settle time** via
`db_manager.purge_candidate_votes()`. `prune()` is the nightly
safety-net sweep. Batched (`LIMIT 5000`) deletes per table, looped
until `<batch`, then `VACUUM`. Row is prunable iff:
* `comparisons` (anchor-vs-anchor / control): `created_at < now-45d`.
* `comparisons/tag_votes/throw_votes/trick_flags` (candidate-touching):
  candidate is settled (promoted or removed). No age gate — these should
  already be gone via the synchronous purge; this catches crash leftovers.
* `pending_tricks`: `created_at < now-14d`.
* `url_mappings`: `last_accessed_at < now-3mo`.

Correctness after prune:
* μ/σ, all `n_*` counters, reliability — already on
  `candidate_tricks`/`users`.
* All-time game boards — read `users.n_*`.
* 30-day boards — retention 45d > 30d.
* Active-candidate flag ratio / tag-throw resolution — active rows are
  never pruned.

---

## 9. Security summary

* **SQLi:** every user-supplied value goes through `?`/`:name`
  placeholders. The handful of f-string queries interpolate only
  server-side constants (validated enum/int). `leaderboard._sql`
  whitelists `kind`/`period` before composition.
* **XSS:** Jinja autoescape; all `innerHTML` insertions escape via
  `GameEngine.esc()`/local `esc()`.
* **Auth:** pbkdf2:sha256 hashes; case-insensitive UNIQUE username +
  IntegrityError catch on race; 30-day user session, 1-hour admin
  session; same-site `?next=` only.
* **CSRF:** session-token guard on all mutating requests
  (`app._csrf_protect`); forms carry `{{ csrf_token() }}`, JS `fetch()`
  auto-attaches `X-CSRF-Token` via a `<head>` shim in `base.html`.
* **Cookies:** `HttpOnly`, `SameSite=Lax`, `Secure` in production.
* **Input bounds:** name/siteswap/comment/password length caps,
  `props_count ∈ [1,13]`, captcha for anon submit,
  `MAX_CONTENT_LENGTH=64KB` on all requests, `long_url ≤ 8KB`.
* **Open-redirect:** `/api/shorten_url` + `/shortener/<code>` reject
  off-site targets via `_is_same_origin()`.
* **Task tokens:** `itsdangerous` signed with `app.secret_key`, 1 h TTL
  — server is stateless between `next_set` and `answer`, client cannot
  see or forge control/expected fields.
* **No app-level rate limiter** — nginx `limit_req` (5 r/s, burst 10)
  covers the common case; add `flask-limiter` if abuse appears.

---

## 10. Scaling characteristics

| Path | Cost per request | Bound |
|---|---|---|
| `suggest_trick` | 3 indexed point queries + 2 inserts | O(1) |
| `needs` | 1 aggregate over active candidates | O(active/prop), index-only |
| `next_set` (any game) | ≤8-row LIMIT on candidates + ≤~12 `ORDER BY RANDOM() LIMIT 1` on `tricks` | O(set_size) queries; each anchor query is O(tricks/prop) scan — see caveat |
| `answer` | 1 insert + 2-4 point updates | O(1) |
| `flag` | 1 insert + 1 update + 1 UNION-count | O(votes for that candidate) |
| leaderboard `all` | `users` table only | O(users) |
| leaderboard `30d` | indexed range scan on vote table | O(votes in window) |
| prune | batched, runs off-peak | O(prunable) |

**Known caveats at very large scale:**
* `ORDER BY RANDOM()` on `tricks` is a full-index scan; swap to rowid
  sampling if master grows past ~100 K.
* `ALL_PROPS_TRICKS` loads full master into memory at boot — fine for
  the crowd pipeline (which doesn't use it) but `route_generator` /
  `filter_tricks` will need their own SQL path eventually.
* `admin/api/candidates?state=pool` is unbounded — add `limit/offset`
  when admin paging is needed.

---

## 11. Extending

* **New game:** add a builder to `pair_picker._BUILDERS`, a handler to
  `answer._HANDLERS`, a `users.n_<game>` column + `bump_user_game_counter`
  case, a hub `GAME_META` entry, and a template under `templates/games/`.
* **New prop:** add `Prop.<Name> = "value"`, optionally a seed CSV, and
  a `PROP_RELEVANT_CATEGORIES` entry. Restart.
* **Batch refit:** replay `comparisons` (anchors fixed) with
  Bradley-Terry MLE → overwrite `candidate_tricks.mu/sigma`. Only
  meaningful for **active** candidates since settled ones are frozen and
  their raw rows are pruned.
