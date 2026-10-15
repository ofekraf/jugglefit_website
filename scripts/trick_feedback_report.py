"""
Print trick feedback collected from generated routes, for manual review.

Votes come from the Dislike / Too hard / Too easy buttons on /created_route
(generated routes only). This script only reads; fix difficulties by hand
in hardcoded_database/tricks/<prop>.csv.

Usage:
    python scripts/trick_feedback_report.py [--prop balls] [--min-votes 2] [--csv out.csv]

On the deploy host, run it inside the app container so it reads the
production SQLite volume (SQLITE_DB_DIR).
"""
from __future__ import annotations

import argparse
import csv
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from database.db_manager import db_manager  # noqa: E402

COLUMNS = ["prop", "props_count", "trick_name", "siteswap_x", "difficulty",
           "too_easy", "too_hard", "dislike", "total", "last_vote"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--prop", help="only this prop (e.g. balls, clubs)")
    parser.add_argument("--min-votes", type=int, default=1, help="hide tricks with fewer votes")
    parser.add_argument("--csv", help="also write the table to this CSV file")
    args = parser.parse_args()

    rows = [r for r in db_manager.get_trick_feedback_summary(args.prop) if r["total"] >= args.min_votes]
    for r in rows:
        r["last_vote"] = datetime.fromtimestamp(r.pop("last_vote_at") / 1000, timezone.utc).strftime("%Y-%m-%d")

    if not rows:
        print("No trick feedback yet.")
        return

    print(f"{'prop':<7} {'n':>2} {'diff':>4} {'easy':>4} {'hard':>4} {'dis':>4}  trick")
    for r in rows:
        print(f"{r['prop']:<7} {r['props_count']:>2} {str(r['difficulty'] or ''):>4} "
              f"{r['too_easy']:>4} {r['too_hard']:>4} {r['dislike']:>4}  {r['trick_name'] or r['siteswap_x']}")
    print(f"\n{len(rows)} tricks, {sum(r['total'] for r in rows)} votes")

    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=COLUMNS)
            writer.writeheader()
            writer.writerows(rows)
        print(f"Wrote {args.csv}")


if __name__ == "__main__":
    main()
