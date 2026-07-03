"""
Submit every past-event trick that isn't in the master list to
POST /api/suggest_trick.

Reuses the dataset built by gen_past_event_diff.py (so SX_OVERRIDES and
auto-derived siteswap_x are included). Idempotent: the API returns
`dup_master` / `dup_candidate` for anything already present.

Usage:
    set JF_BASE=https://jugglefit.org
    set JF_SESSION=<flask session cookie value>
    set JF_CSRF=<csrf token matching that session>
    python scripts/submit_past_event_tricks.py [--dry-run] [--limit N]
"""
from __future__ import annotations
import argparse
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Importing the diff generator builds `new_tricks` (OrderedDict of entries)
# and, as a side effect, writes past_event_trick_suggestions.md — harmless.
import gen_past_event_diff as diff  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=os.environ.get("JF_BASE", "https://jugglefit.org"))
    ap.add_argument("--session", default=os.environ.get("JF_SESSION"))
    ap.add_argument("--csrf", default=os.environ.get("JF_CSRF"))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--sleep", type=float, default=0.15,
                    help="seconds between requests")
    ap.add_argument("--insecure", action="store_true",
                    help="skip TLS cert verification (corporate MITM proxies)")
    args = ap.parse_args()

    entries = list(diff.new_tricks.values())
    if args.limit:
        entries = entries[: args.limit]
    print(f"Submitting {len(entries)} tricks to {args.base}/api/suggest_trick "
          f"{'(dry-run)' if args.dry_run else ''}")

    if not args.dry_run and (not args.session or not args.csrf):
        print("ERROR: JF_SESSION and JF_CSRF (or --session/--csrf) required.",
              file=sys.stderr)
        return 2

    ctx = ssl.create_default_context()
    if args.insecure:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

    counts = {"accepted": 0, "dup_master": 0, "dup_candidate": 0, "error": 0}

    for i, e in enumerate(entries, 1):
        payload = {
            "prop_type": e["prop"].value,
            "props_count": e["props_count"],
            "name": e["name"],
            "siteswap_x": e["siteswap_x"] or "",
            "comment": e["comment"] or "",
        }
        label = (f"[{i:3}/{len(entries)}] {payload['prop_type']:<5} "
                 f"{payload['props_count']}  {payload['name'] or payload['siteswap_x']}")
        if args.dry_run:
            print(label, "->", payload["siteswap_x"] or "-")
            continue

        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{args.base}/api/suggest_trick",
            data=body,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "X-CSRF-Token": args.csrf,
                "Cookie": f"session={args.session}",
                "Origin": args.base,
                "Referer": f"{args.base}/contribute/add_tricks",
                "User-Agent": "jugglefit-seed/1.0",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
                data = json.loads(r.read().decode("utf-8"))
            status = data.get("status", "?")
            counts[status] = counts.get(status, 0) + 1
            extra = ""
            if status == "accepted":
                extra = f"pending={data.get('pending_id')} cand={data.get('candidate_id')}"
            elif status.startswith("dup"):
                m = data.get("match") or {}
                extra = f"matched id={m.get('id')}"
            print(f"{label}  => {status} {extra}")
        except urllib.error.HTTPError as ex:
            counts["error"] += 1
            try:
                err = ex.read().decode("utf-8", "replace")
            except Exception:
                err = str(ex)
            print(f"{label}  => HTTP {ex.code} {err}")
            if ex.code in (401, 403):
                print("Auth failed — aborting.", file=sys.stderr)
                return 1
        except Exception as ex:  # noqa: BLE001
            counts["error"] += 1
            print(f"{label}  => ERROR {ex}")
        time.sleep(args.sleep)

    print()
    print("Summary:", ", ".join(f"{k}={v}" for k, v in counts.items() if v))
    return 0 if counts["error"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
