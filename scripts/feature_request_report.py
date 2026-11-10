"""
Print feature requests / bug reports from /feature_requests, for review.

Includes private fields (contact, page link, browser). Approve or change status on
/feature_requests/admin; this script only reads.

Usage:
    python scripts/feature_request_report.py [--category website_bug] [--status new] [--csv out.csv]

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

from blueprints.feature_requests import CATEGORIES, STATUS_LABELS  # noqa: E402
from database.db_manager import db_manager  # noqa: E402

COLUMNS = ["id", "category", "status", "votes", "dislikes", "title", "body", "page",
           "contact", "user_agent", "created"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--category", choices=list(CATEGORIES))
    parser.add_argument("--status", choices=list(STATUS_LABELS))
    parser.add_argument("--csv", help="also write the table to this CSV file")
    args = parser.parse_args()

    rows = db_manager.get_all_feature_requests(args.category, args.status)
    if not rows:
        print("No feature requests.")
        return
    for r in rows:
        r["created"] = datetime.fromtimestamp(r["created_at"] / 1000, timezone.utc).strftime("%Y-%m-%d")

    for cat, label in CATEGORIES.items():
        group = [r for r in rows if r["category"] == cat]
        if not group:
            continue
        print(f"\n== {label} ({len(group)}) ==")
        for r in group:
            votes = "" if cat == "website_bug" else f"+{r['votes']:<3} -{r['dislikes']:<3} "
            contact = f"  <{r['contact']}>" if r["contact"] else ""
            print(f"#{r['id']:<4} {r['status']:<11} {votes}{r['created']}  {r['title']}{contact}")

    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
        print(f"\nWrote {args.csv}")


if __name__ == "__main__":
    main()
