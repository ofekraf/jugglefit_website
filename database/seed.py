"""
One-time (idempotent) import of the CSV trick files into the SQLite
``tricks`` table.

After this runs the CSV files become export artifacts only; the SQLite
``tricks`` table is the source of truth and is what
``pylib.utils.trick_loader.load_tricks_from_db`` reads.

Safe to call on every process start: rows are keyed by
(prop_type, props_count, name, siteswap_x) with a UNIQUE constraint, so
re-seeding is a no-op for already-imported tricks.
"""
from __future__ import annotations

from typing import Dict

from database.db_manager import db_manager
from hardcoded_database.consts import get_trick_csv_path
from pylib.classes.prop import Prop
from pylib.utils.trick_loader import load_tricks_from_csv


def seed_tricks_from_csv(*, force: bool = False) -> Dict[str, int]:
    """Import CSV tricks into the ``tricks`` table.

    Idempotent per prop: a prop is seeded only if it has zero rows in the
    ``tricks`` table (or ``force=True``). This means adding a new ``Prop``
    enum value + CSV file will seed just that prop on next boot without
    touching existing data. Re-seeding an already-populated prop is skipped.
    """
    inserted: Dict[str, int] = {}
    for prop in Prop:
        if not force and db_manager.count_tricks(prop.value) > 0:
            continue
        csv_path = get_trick_csv_path(prop)
        if not csv_path.exists():
            print(f"seed: no CSV for prop '{prop.value}', skipping")
            continue
        count = 0
        for trick in load_tricks_from_csv(csv_path):
            tags = "|".join(sorted(str(t) for t in (trick.tags or [])))
            row_id = db_manager.insert_trick(
                prop_type=prop.value,
                props_count=trick.props_count,
                name=trick.name or None,
                siteswap_x=trick.siteswap_x or None,
                difficulty=trick.difficulty,
                tags=tags,
                max_throw=trick.max_throw,
                comment=trick.comment or None,
                source="seed",
            )
            if row_id is not None:
                count += 1
        inserted[prop.value] = count
    db_manager.set_meta("seeded_from_csv", "1")
    return inserted


if __name__ == "__main__":
    summary = seed_tricks_from_csv(force=True)
    for prop, n in summary.items():
        print(f"{prop}: inserted {n} tricks")
