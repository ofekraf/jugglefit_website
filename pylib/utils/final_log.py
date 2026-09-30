"""Build the live-final timing log (one row per stage visit) from the
append-only ``final_events`` table. Kept free of Flask/DB so it can be
unit-tested with plain dicts."""
from __future__ import annotations

import csv
import io
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

FINISHED_LABEL = "Finished"

CSV_HEADER = ["competitor", "trick_number", "trick_name", "entered_at_utc", "left_at_utc", "duration_s"]


def _event_time(event: Dict[str, Any]) -> int:
    # client_at is when the admin tapped; `at` is when the server got it
    # (later if the admin phone was offline and re-sent the move).
    return event["client_at"] if event.get("client_at") is not None else event["at"]


def _iso(ms: Optional[int]) -> str:
    if ms is None:
        return ""
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).isoformat(timespec="milliseconds")


def build_log_rows(events: List[Dict[str, Any]], competitors: List[Dict[str, Any]],
                   trick_names: List[str]) -> List[List[str]]:
    """Return CSV rows (without header), grouped by competitor in column
    order, visits in the order the server received them. A take-back shows
    up as a later visit to an earlier trick."""
    route_length = len(trick_names)
    by_competitor: Dict[int, List[Dict[str, Any]]] = {c["id"]: [] for c in competitors}
    for event in events:
        by_competitor.setdefault(event["competitor_id"], []).append(event)

    rows: List[List[str]] = []
    for competitor in competitors:
        visits: List[Dict[str, Any]] = []
        for event in by_competitor.get(competitor["id"], []):
            t = _event_time(event)
            if visits and visits[-1]["left_at"] is None:
                visits[-1]["left_at"] = t
            visits.append({"stage": event["to_stage"], "entered_at": t, "left_at": None})
        for visit in visits:
            stage = visit["stage"]
            if stage >= route_length:
                number, name = "", FINISHED_LABEL
            else:
                number, name = str(stage + 1), trick_names[stage]
            duration = ""
            if visit["left_at"] is not None:
                duration = f"{(visit['left_at'] - visit['entered_at']) / 1000:.3f}"
            rows.append([competitor["name"], number, name, _iso(visit["entered_at"]),
                         _iso(visit["left_at"]), duration])
    return rows


def finish_times(events: List[Dict[str, Any]], route_length: int) -> Dict[int, int]:
    """competitor_id -> time of their last move into the Finished stage,
    for competitors whose latest move is into Finished."""
    result: Dict[int, int] = {}
    for event in events:
        if event["to_stage"] >= route_length:
            result[event["competitor_id"]] = _event_time(event)
        else:
            result.pop(event["competitor_id"], None)
    return result


def to_csv(rows: List[List[str]]) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(CSV_HEADER)
    writer.writerows(rows)
    return buf.getvalue()
