#!/usr/bin/env python3
"""Run a fictional live final against a JuggleFit server.

Creates a *test* final on a made-up route (``SIMULATION <id>``, so it can
never match a printed route), then:

1. an admin session starts it and moves every competitor to Finished,
   with some random take-backs;
2. N viewer threads poll the public state like the browser does;
3. it checks the final state and the CSV log against the moves it made,
   and measures how long viewers took to see each move.

Exit code 0 when every check passes. Examples::

    python scripts/simulate_final.py --base-url http://localhost:5001 --password test
    JUGGLEFIT_ADMIN_PASSWORD=... python scripts/simulate_final.py \\
        --base-url https://<domain> --viewers 20 --cleanup

Only needs ``requests`` (no app imports), so it can run from any machine.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import os
import random
import re
import statistics
import sys
import threading
import time
import uuid
import zlib
from base64 import b64encode
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import requests

_CSRF_RE = re.compile(r'<meta name="csrf-token" content="([^"]+)"')
REQUEST_TIMEOUT_S = 10


def fictional_route(tricks: int, duration_seconds: int) -> str:
    """Serialized route in the same format as ``Route.serialize``."""
    route = {
        "name": f"SIMULATION {uuid.uuid4().hex[:8]}",
        "prop": "balls",
        "duration_seconds": duration_seconds,
        "tricks": [{"name": f"Simulation trick {i + 1}", "props_count": 3 + i // 3,
                    "difficulty": 1, "tags": [], "comment": None, "max_throw": None,
                    "siteswap_x": None} for i in range(tricks)],
    }
    return b64encode(zlib.compress(json.dumps(route).encode("utf-8"))).decode("utf-8")


def plan_moves(competitor_ids: List[int], route_length: int, take_back_rate: float,
               rng: random.Random) -> List[Tuple[int, int]]:
    """(competitor_id, to_stage) moves that take every competitor to
    Finished, interleaved at random, with occasional take-backs."""
    stage = {cid: 0 for cid in competitor_ids}
    moves = []
    while any(s < route_length for s in stage.values()):
        cid = rng.choice([c for c, s in stage.items() if s < route_length])
        if stage[cid] > 0 and rng.random() < take_back_rate:
            stage[cid] -= 1
        else:
            stage[cid] += 1
        moves.append((cid, stage[cid]))
    return moves


@dataclass
class Report:
    checks: List[Tuple[str, bool, str]] = field(default_factory=list)
    info: List[str] = field(default_factory=list)

    def check(self, name: str, ok: bool, detail: str = "") -> None:
        self.checks.append((name, ok, detail))

    @property
    def ok(self) -> bool:
        return bool(self.checks) and all(ok for _, ok, _ in self.checks)

    def text(self) -> str:
        lines = [f"  {'PASS' if ok else 'FAIL'}  {name}" + (f" - {detail}" if detail else "")
                 for name, ok, detail in self.checks]
        lines += [f"  info  {line}" for line in self.info]
        return "\n".join(lines)


class Viewer(threading.Thread):
    """Polls /state like static/js/live_final.js and records when each
    version was first seen."""

    def __init__(self, base_url: str, final_id: str, interval_s: float, stop: threading.Event):
        super().__init__(daemon=True)
        self.url = f"{base_url}/api/finals/{final_id}/state"
        self.interval_s = interval_s
        self.stop = stop
        self.session = requests.Session()
        self.first_seen: Dict[int, float] = {}
        self.requests = 0
        self.errors = 0
        self.cache_hits = 0

    def run(self) -> None:
        version: Optional[int] = None
        # Spread the first polls like real page loads.
        self.stop.wait(random.random() * self.interval_s)
        while not self.stop.is_set():
            self.requests += 1
            try:
                params = {"since": version} if version is not None else None
                res = self.session.get(self.url, params=params, timeout=REQUEST_TIMEOUT_S)
                if res.headers.get("X-Cache-Status") == "HIT":
                    self.cache_hits += 1
                if res.status_code == 200:
                    version = res.json()["version"]
                    self.first_seen.setdefault(version, time.monotonic())
                elif res.status_code != 204:
                    self.errors += 1
            except requests.RequestException:
                self.errors += 1
            self.stop.wait(self.interval_s + random.random())


def _percentile(values: List[float], pct: float) -> float:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(round(pct / 100 * (len(ordered) - 1))))]


def run_simulation(base_url: str, password: str, competitors: int = 6, viewers: int = 20,
                   tricks: int = 8, duration_s: float = 60, poll_interval_s: float = 3,
                   take_back_rate: float = 0.1, max_p95_s: float = 8, max_error_rate: float = 0.01,
                   cleanup: bool = False, seed: Optional[int] = None) -> Report:
    base_url = base_url.rstrip("/")
    rng = random.Random(seed)
    report = Report()
    admin = requests.Session()

    def post(path: str, **body) -> requests.Response:
        return admin.post(f"{base_url}{path}", json=body, headers={"X-CSRF-Token": csrf},
                          timeout=REQUEST_TIMEOUT_S)

    # --- create + log in as admin ----------------------------------------
    html = admin.get(f"{base_url}/", timeout=REQUEST_TIMEOUT_S).text
    match = _CSRF_RE.search(html)
    if not match:
        report.check("read CSRF token from the home page", False)
        return report
    csrf = match.group(1)
    names = [f"Sim {i + 1}" for i in range(competitors)]
    payload = fictional_route(tricks, int(duration_s) + 60)
    res = post("/api/finals", password=password, route=payload, competitor_count=competitors,
               names=names, test=True)
    report.check("create test final", res.status_code == 201, f"HTTP {res.status_code}")
    if res.status_code != 201:
        return report
    final_id = res.json()["final_id"]
    report.info.append(f"final id: {final_id}")
    res = admin.get(res.json()["admin_url"], allow_redirects=False, timeout=REQUEST_TIMEOUT_S)
    report.check("admin link logs in", res.status_code == 302, f"HTTP {res.status_code}")

    stop = threading.Event()
    viewer_threads = [Viewer(base_url, final_id, poll_interval_s, stop) for _ in range(viewers)]
    try:
        state = admin.get(f"{base_url}/api/finals/{final_id}/state", timeout=REQUEST_TIMEOUT_S).json()
        route_length = state["route_length"]
        competitor_ids = [c["id"] for c in state["competitors"]]
        viewers_started = time.monotonic()
        for viewer in viewer_threads:
            viewer.start()

        # --- start + moves ------------------------------------------------
        admin_errors = 0
        res = post(f"/api/finals/{final_id}/start", client_at=int(time.time() * 1000))
        admin_errors += res.status_code != 200
        moves = plan_moves(competitor_ids, route_length, take_back_rate, rng)
        gap_s = duration_s / max(1, len(moves))
        sent: List[Tuple[int, float]] = []  # (version, monotonic time sent)
        for competitor_id, to_stage in moves:
            t = time.monotonic()
            res = post(f"/api/finals/{final_id}/move", competitor_id=competitor_id,
                       to_stage=to_stage, client_at=int(time.time() * 1000))
            if res.status_code == 200:
                sent.append((res.json()["version"], t))
            else:
                admin_errors += 1
            time.sleep(max(0.0, gap_s - (time.monotonic() - t)))
        report.check("admin actions accepted", admin_errors == 0,
                     f"{len(moves)} moves, {admin_errors} rejected")

        # Give viewers one more poll cycle to catch up.
        stop.wait(poll_interval_s + 2)
        stop.set()
        for viewer in viewer_threads:
            viewer.join(timeout=REQUEST_TIMEOUT_S)
        viewers_elapsed_s = time.monotonic() - viewers_started

        # --- final state ------------------------------------------------------
        final_state = admin.get(f"{base_url}/api/finals/{final_id}/state",
                                timeout=REQUEST_TIMEOUT_S).json()
        stages = [c["stage"] for c in final_state["competitors"]]
        report.check("every competitor is Finished", stages == [route_length] * competitors,
                     f"stages {stages}")
        report.check("every finisher has a finish time",
                     all(c["finished_at"] for c in final_state["competitors"]))

        # --- CSV log ----------------------------------------------------------
        res = admin.get(f"{base_url}/api/finals/{final_id}/log.csv", timeout=REQUEST_TIMEOUT_S)
        rows = list(csv.DictReader(io.StringIO(res.text)))
        expected_visits = {name: ["1"] for name in names}
        name_of = dict(zip(competitor_ids, names))
        for competitor_id, to_stage in moves:
            expected_visits[name_of[competitor_id]].append(
                str(to_stage + 1) if to_stage < route_length else "")
        actual_visits: Dict[str, List[str]] = {name: [] for name in names}
        for row in rows:
            actual_visits.setdefault(row["competitor"], []).append(row["trick_number"])
        report.check("CSV log matches the moves", actual_visits == expected_visits,
                     f"{len(rows)} rows")

        # --- viewers ----------------------------------------------------------
        latencies = []
        missed = 0
        for version, t in sent:
            for viewer in viewer_threads:
                seen = [ts for v, ts in viewer.first_seen.items() if v >= version]
                if seen:
                    latencies.append(max(0.0, min(seen) - t))
                else:
                    missed += 1
        total_requests = sum(v.requests for v in viewer_threads)
        total_errors = sum(v.errors for v in viewer_threads)
        error_rate = total_errors / max(1, total_requests)
        report.check("viewers saw every move", bool(sent) and missed == 0,
                     f"{len(sent)} moves, {missed} missed")
        if latencies:
            p95 = _percentile(latencies, 95)
            report.check(f"p95 delay to viewers <= {max_p95_s}s", p95 <= max_p95_s,
                         f"median {statistics.median(latencies):.2f}s, p95 {p95:.2f}s, "
                         f"max {max(latencies):.2f}s")
        report.check(f"viewer error rate <= {max_error_rate:.0%}", error_rate <= max_error_rate,
                     f"{total_errors}/{total_requests} requests failed")
        report.info.append(f"viewer load: {viewers} viewers, "
                           f"{total_requests / viewers_elapsed_s:.1f} state requests/s")
        hits = sum(v.cache_hits for v in viewer_threads)
        if hits:
            report.info.append(f"nginx cache hits: {hits}/{total_requests}")
    finally:
        stop.set()
        post(f"/api/finals/{final_id}/end")
        if cleanup:
            res = post(f"/api/finals/{final_id}/delete")
            report.check("delete test final", res.status_code == 200, f"HTTP {res.status_code}")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--base-url", default="http://localhost:5001")
    parser.add_argument("--password", default=os.environ.get("JUGGLEFIT_ADMIN_PASSWORD"),
                        help="ADMIN_PASSWORD of the server (default: $JUGGLEFIT_ADMIN_PASSWORD)")
    parser.add_argument("--competitors", type=int, default=6)
    parser.add_argument("--viewers", type=int, default=20)
    parser.add_argument("--tricks", type=int, default=8)
    parser.add_argument("--duration", type=float, default=60, help="seconds to spread the moves over")
    parser.add_argument("--poll-interval", type=float, default=3)
    parser.add_argument("--max-p95", type=float, default=8, help="max p95 delay to viewers (s)")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--cleanup", action="store_true", help="delete the test final afterwards")
    args = parser.parse_args()
    if not args.password:
        parser.error("--password or $JUGGLEFIT_ADMIN_PASSWORD is required")

    print(f"Simulating a final on {args.base_url}: {args.competitors} competitors, "
          f"{args.viewers} viewers, ~{args.duration:.0f}s")
    report = run_simulation(args.base_url, args.password, competitors=args.competitors,
                            viewers=args.viewers, tricks=args.tricks, duration_s=args.duration,
                            poll_interval_s=args.poll_interval, max_p95_s=args.max_p95,
                            cleanup=args.cleanup, seed=args.seed)
    print(report.text())
    print("OK" if report.ok else "FAILED")
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())
