"""
Generate past_event_trick_suggestions.md: past-event tricks not in master CSVs.

Match rule mirrors db_manager.find_master_match:
    same prop_type AND same props_count AND
    (name equal, case-insensitive  OR  siteswap_x equal, case-insensitive)
None never matches None.
"""
from __future__ import annotations
import re
import sys
from collections import defaultdict, OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pylib.classes.prop import Prop  # noqa: E402
from pylib.utils.trick_loader import load_tricks_from_csv  # noqa: E402
from hardcoded_database.consts import get_trick_csv_path  # noqa: E402
from hardcoded_database.events.past_events import ALL_PAST_EVENTS  # noqa: E402


def norm(s):
    if s is None:
        return None
    s = str(s).strip()
    return s.casefold() if s else None


# ---- master (stable) tricks, indexed for O(1) lookup --------------------
master_by_name: dict[tuple[Prop, int, str], object] = {}
master_by_sx:   dict[tuple[Prop, int, str], object] = {}
master_counts:  dict[Prop, int] = {}

for prop in Prop:
    csv_path = get_trick_csv_path(prop)
    tricks = load_tricks_from_csv(csv_path) if csv_path.exists() else []
    master_counts[prop] = len(tricks)
    for t in tricks:
        n, sx = norm(t.name), norm(t.siteswap_x)
        if n:
            master_by_name[(prop, t.props_count, n)] = t
        if sx:
            master_by_sx[(prop, t.props_count, sx)] = t


# ---- derive siteswap_x from name (conservative, attested patterns only) --
# Legend from pylib/classes/siteswap_x_modifiers.py. Nothing invented; every
# rule below has at least one exemplar in hardcoded_database/tricks/*.csv or
# an event file. If any part of a name is not covered, we return None.

# Segments that are opaque to siteswap-x (kept verbatim as words).
_VERBATIM = {
    "cascade", "any", "fountain", "sync fountain", "async fountain",
    "sync", "async", "shower", "half shower", "async any",
}
# Modifier vocabulary → template applied to a base siteswap digit `d`.
_MOD_WORDS = {
    "backcross": "{B}", "backcrosses": "{B}",
    "backross": "{B}", "backrosses": "{B}",         # common typo in data
    "shoulder": "{S}", "shoulders": "{S}",
    "under the leg": "{Ul}", "under the legs": "{Ul}",
    "neck throw": "{N}", "neck throws": "{N}",
    "overhead": "{Oh}", "overheads": "{Oh}",
    "flatfront": "{F}", "flatfronts": "{F}",
    "pancake": "{Pc}", "pancakes": "{Pc}",
    "reverse shoulder": "{/Rs}", "reverse shoulders": "{/Rs}",
    "reverse backcross": "{/Rb}", "reverse backcrosses": "{/Rb}",
    "penguin": "{/Pe}", "penguins": "{/Pe}",
    "lazy": "{/L}", "lazies": "{/L}",
    "behind the back": "{B}", "around the body": "{B}",  # attested: {B} on 1's
}
_SPIN_WORDS = {
    "flat": 0, "flats": 0,
    "single": 1, "singles": 1,
    "double": 2, "doubles": 2,
    "triple": 3, "triples": 3,
    "quad": 4, "quads": 4,
    "reverse spin": -1, "reverse spins": -1,
    "reverse spin double": -2, "reverse spin doubles": -2,
}
# Constructs siteswap-x cannot express → bail out entirely.
_UNSUPPORTED = re.compile(
    r"\b("
    r"360|720|180|[0-9]+up|[0-9]+ up|[0-9]+-?stage|pirouette|clap|"
    r"knees|laying|isolated|blindfold|mills\s*mess|box|helicopter|"
    r"slapback|consecutive|connected|in a run|one hand|left hand|right hand|"
    r"multiplex|kick\s*up|pulldown|collect|cold start|swap|ass catch|"
    r"underarm|up the back"
    r")\b",
    re.I,
)
_MOD_UNION = "|".join(
    sorted((re.escape(k) for k in list(_MOD_WORDS) + list(_SPIN_WORDS)),
           key=len, reverse=True)
)
_SS_RE = re.compile(r"^[0-9a-f]{2,}$")           # bare siteswap (period ≥ 2)
_SS_ANY = re.compile(r"^[0-9a-f]+$")
_SYNC_RE = re.compile(r"^\([0-9a-fx,]+\)\*?$")   # (6x,4)* etc.
_PREFIX_RE = re.compile(r"^(\d+)\s*(c|rounds?|sides?)\s+(.+)$", re.I)


def _apply_mod_to_digit(ss: str, digit: str, mod: str) -> str | None:
    """Attach `mod` after every occurrence of `digit` in siteswap `ss`."""
    if digit not in ss:
        return None
    return "".join(ch + (mod if ch == digit else "") for ch in ss)


def _apply_mod_to_all(ss: str, mod: str) -> str:
    return "".join(ch + mod for ch in ss)


def _spin_mod(n: int) -> str:
    return "{%d}" % n


def _seg_to_sx(seg: str, props_count: int) -> str | None:
    """Convert one ' -> '-delimited segment. Return None if not confidently
    expressible."""
    s = seg.strip()
    if not s:
        return None
    low = s.lower()

    if low in _VERBATIM:
        return low

    # Bare siteswap (multi-digit) or sync pattern → passthrough.
    if _SS_RE.fullmatch(low) or _SYNC_RE.fullmatch(low):
        return low

    # Strip a leading count/rounds/sides prefix and recurse on the rest.
    m = _PREFIX_RE.match(s)
    prefix = ""
    if m:
        n, unit, rest = m.group(1), m.group(2).lower(), m.group(3)
        # normalise "round" → "rounds" etc. — corpus uses both, keep as-is.
        prefix = f"{n}{unit if unit == 'c' else ' ' + unit} "
        if unit == "c":
            prefix = f"{n}c "
        s = rest.strip()
        low = s.lower()
        if low in _VERBATIM:
            return prefix + low
        if _SS_RE.fullmatch(low) or _SYNC_RE.fullmatch(low):
            return prefix + low

    d = str(props_count)

    # `<mod-word>` alone → base pattern with modifier on the props_count digit.
    #   overheads (5b) → 5{Oh};  triples (5c clubs) → 5{3};  flats (4c) → 4{0}
    if low in _MOD_WORDS:
        return prefix + d + _MOD_WORDS[low]
    if low in _SPIN_WORDS:
        return prefix + d + _spin_mod(_SPIN_WORDS[low])
    # `<spin> cascade` / `<mod> cascade` / `<mod> async fountain`
    m = re.fullmatch(rf"({_MOD_UNION})\s+(cascade|fountain|async fountain)", low)
    if m:
        w = m.group(1)
        mod = _MOD_WORDS.get(w) or _spin_mod(_SPIN_WORDS[w])
        return prefix + d + mod
    # `overhead doubles`, `triples backrosses`, `backrosses singles`
    m = re.fullmatch(rf"({_MOD_UNION})\s+({_MOD_UNION})", low)
    if m:
        a, b = m.group(1), m.group(2)
        tm = _MOD_WORDS.get(a) or _MOD_WORDS.get(b)
        sp = _SPIN_WORDS.get(a) if a in _SPIN_WORDS else _SPIN_WORDS.get(b)
        if tm and sp is not None:
            # merge into one brace: {B2}, {Oh2}, {F0} …
            if tm.startswith("{/"):
                return None  # spin+catch-only combo not attested
            return prefix + d + "{" + tm.strip("{}") + str(sp) + "}"
        return None

    # `SSS, <mod> D['s]`  → attach mod to digit D in SSS.
    m = re.fullmatch(
        rf"([0-9a-f]{{2,}})\s*,\s*({_MOD_UNION})\s+([0-9a-f])(?:'?s)?", low
    )
    if m:
        ss, w, dig = m.group(1), m.group(2), m.group(3)
        mod = _MOD_WORDS.get(w) or _spin_mod(_SPIN_WORDS[w])
        out = _apply_mod_to_digit(ss, dig, mod)
        return (prefix + out) if out else None

    # `SSS <mod-plural>`  (e.g. `531 overheads`) → mod on every digit.
    m = re.fullmatch(rf"([0-9a-f]{{2,}})\s+({_MOD_UNION})", low)
    if m:
        ss, w = m.group(1), m.group(2)
        mod = _MOD_WORDS.get(w) or _spin_mod(_SPIN_WORDS[w])
        return prefix + _apply_mod_to_all(ss, mod)

    # `SSS, D's <mod>`  (e.g. `a86411, 1's around the body`)
    m = re.fullmatch(
        rf"([0-9a-f]{{2,}})\s*,\s*([0-9a-f])(?:'?s)?\s+({_MOD_UNION})", low
    )
    if m:
        ss, dig, w = m.group(1), m.group(2), m.group(3)
        mod = _MOD_WORDS.get(w) or _spin_mod(_SPIN_WORDS[w])
        out = _apply_mod_to_digit(ss, dig, mod)
        return (prefix + out) if out else None

    # `SSS, <spin> D` (e.g. `741, single 7`)
    m = re.fullmatch(
        rf"([0-9a-f]{{2,}})\s*,\s*({_MOD_UNION})\s+([0-9a-f])\s*,\s*"
        rf"({_MOD_UNION})\s+([0-9a-f])", low
    )
    if m:
        ss = m.group(1)
        for w, dig in ((m.group(2), m.group(3)), (m.group(4), m.group(5))):
            mod = _MOD_WORDS.get(w) or _spin_mod(_SPIN_WORDS[w])
            ss2 = _apply_mod_to_digit(ss, dig, mod)
            if ss2 is None:
                return None
            ss = ss2
        return prefix + ss

    return None


# ---- manual overrides ----------------------------------------------------
# Hand-tuned siteswap_x for entries the heuristic gets wrong or under-specifies.
# Key: (prop_value, props_count, name.casefold()). Value: siteswap_x string.
# Edit this dict and re-run the script; overrides always win over derivation.
SX_OVERRIDES: dict[tuple[str, int, str], str] = {
    # clubs 3 — compound spin+flatfront on the 3
    ("clubs", 3, "2 rounds 531, flatfront 5, reverse spin flatfront 3"):
        "2 rounds 5{F}3{F-1}1",
    # clubs 3 — make repeat count explicit
    ("clubs", 3, "441, behind the back 1"):
        "2 rounds 441{B}",
    # clubs 4 — disambiguate async (digit form) instead of bare "fountain"
    ("clubs", 4, "4c flats -> fountain"):
        "4c 4{0} -> 4",
    ("clubs", 4, "4c async fountain -> 4c flats"):
        "4c 4 -> 4c 4{0}",
    # clubs 5 — source (EJC2025.py) is missing the second `->`
    ("clubs", 5, "cascade -> 6c a86411, 1's around the body -> singles"):
        "5 -> 1 round a86411{B} -> 5{1}",
}


def derive_siteswap_x(name: str | None, props_count: int) -> str | None:
    if not name:
        return None
    if _UNSUPPORTED.search(name):
        return None
    parts = re.split(r"\s*->\s*", name)
    out: list[str] = []
    for p in parts:
        sx = _seg_to_sx(p, props_count)
        if sx is None:
            return None
        out.append(sx)
    result = " -> ".join(out)
    # Only worth emitting if it actually encodes something the name doesn't —
    # i.e. at least one {modifier}. Otherwise it's just the name restated.
    if "{" not in result:
        return None
    return result


def in_master(prop: Prop, t) -> bool:
    n, sx = norm(t.name), norm(t.siteswap_x)
    if n and (prop, t.props_count, n) in master_by_name:
        return True
    if sx and (prop, t.props_count, sx) in master_by_sx:
        return True
    return False


# ---- walk past events ----------------------------------------------------
raw_total = 0
per_event_total: dict[str, int] = defaultdict(int)
# key -> {prop, props_count, name, siteswap_x, comment, events:[..]}
new_tricks: "OrderedDict[tuple, dict]" = OrderedDict()

for ev in ALL_PAST_EVENTS:
    ev_name = getattr(ev, "name", None) or ev.__class__.__name__
    for rr in getattr(ev, "results", []) or []:
        route = rr.route
        prop: Prop = route.prop
        for t in route.tricks:
            raw_total += 1
            per_event_total[ev_name] += 1
            if in_master(prop, t):
                continue
            n, sx = norm(t.name), norm(t.siteswap_x)
            key = (prop, t.props_count, n or f"__sx__::{sx}")
            entry = new_tricks.get(key)
            if entry is None:
                # also dedupe against previously-collected via siteswap_x
                dup = None
                if sx:
                    for k, e in new_tricks.items():
                        if k[0] == prop and k[1] == t.props_count and norm(e["siteswap_x"]) == sx:
                            dup = k
                            break
                if dup:
                    entry = new_tricks[dup]
                else:
                    entry = {
                        "prop": prop,
                        "props_count": t.props_count,
                        "name": t.name,
                        "siteswap_x": t.siteswap_x,
                        "sx_derived": False,
                        "comment": t.comment,
                        "events": [],
                    }
                    new_tricks[key] = entry
            # prefer non-empty fields from later occurrences
            if not entry["name"] and t.name:
                entry["name"] = t.name
            if not entry["siteswap_x"] and t.siteswap_x:
                entry["siteswap_x"] = t.siteswap_x
            if not entry["comment"] and t.comment:
                entry["comment"] = t.comment
            if ev_name not in entry["events"]:
                entry["events"].append(ev_name)

# ---- derive missing siteswap_x -------------------------------------------
had_sx = derived_sx = overridden_sx = 0
for e in new_tricks.values():
    okey = (e["prop"].value, e["props_count"], (e["name"] or "").casefold())
    if okey in SX_OVERRIDES:
        e["siteswap_x"] = SX_OVERRIDES[okey]
        e["sx_derived"] = "override"
        overridden_sx += 1
        continue
    if e["siteswap_x"]:
        had_sx += 1
        continue
    sx = derive_siteswap_x(e["name"], e["props_count"])
    if sx:
        # Guard: don't emit a value that would collide with an existing master
        # trick on siteswap_x (would cause spurious dup_master).
        if (e["prop"], e["props_count"], norm(sx)) in master_by_sx:
            continue
        e["siteswap_x"] = sx
        e["sx_derived"] = True
        derived_sx += 1

# ---- group + write -------------------------------------------------------
by_prop: dict[Prop, list[dict]] = defaultdict(list)
for e in new_tricks.values():
    by_prop[e["prop"]].append(e)
for lst in by_prop.values():
    lst.sort(key=lambda e: (e["props_count"], (e["name"] or e["siteswap_x"] or "").casefold()))


def esc(s):
    return "" if s is None else str(s).replace("|", "\\|")


out = ROOT / "past_event_trick_suggestions.md"
lines: list[str] = []
lines.append("# Past-event tricks to suggest")
lines.append("")
lines.append("Tricks that appeared in past-event routes but are **not** in the stable")
lines.append("master trick list (`hardcoded_database/tricks/*.csv`). These will be")
lines.append("submitted to `/api/suggest_trick` so they enter the crowd rating pipeline.")
lines.append("")
lines.append("Match rule (same as `db_manager.find_master_match`): same `prop_type` +")
lines.append("`props_count` and case-insensitive equality on `name` **or** `siteswap_x`.")
lines.append("")
lines.append("## Summary")
lines.append("")
lines.append("| Prop | Master tricks | New from past events |")
lines.append("|---|---:|---:|")
total_new = 0
for prop in Prop:
    n = len(by_prop.get(prop, []))
    total_new += n
    lines.append(f"| {prop.value} | {master_counts[prop]} | {n} |")
lines.append(f"| **Total** | **{sum(master_counts.values())}** | **{total_new}** |")
lines.append("")
lines.append(f"- Past-event trick occurrences scanned: **{raw_total}** "
             f"(across {len(ALL_PAST_EVENTS)} events)")
lines.append(f"- Unique new tricks to submit: **{total_new}**")
still_blank = total_new - had_sx - derived_sx - overridden_sx
lines.append(f"- Siteswap-X coverage: {had_sx} from source, "
             f"**{derived_sx} auto-derived** (†), "
             f"**{overridden_sx} manual** (‡), {still_blank} left blank "
             f"(not expressible — see `docs/siteswap_x_agents.md` §5)")
lines.append("")
lines.append("### Per event (total tricks in routes)")
lines.append("")
for ev, c in per_event_total.items():
    lines.append(f"- {ev}: {c}")
lines.append("")

for prop in Prop:
    entries = by_prop.get(prop, [])
    if not entries:
        continue
    lines.append(f"## {prop.value} ({len(entries)})")
    lines.append("")
    lines.append("| # | Props | Name | Siteswap-X | Comment | Seen in |")
    lines.append("|---:|---:|---|---|---|---|")
    for i, e in enumerate(entries, 1):
        sx = esc(e["siteswap_x"])
        mark = e.get("sx_derived")
        if sx and mark:
            sx = f"{sx} {'‡' if mark == 'override' else '†'}"
        lines.append(
            f"| {i} | {e['props_count']} | {esc(e['name'])} | "
            f"{sx} | {esc(e['comment'])} | "
            f"{', '.join(e['events'])} |"
        )
    lines.append("")
lines.append("† auto-derived from name per `docs/siteswap_x_agents.md`.  "
             "‡ manual override (`SX_OVERRIDES` in `scripts/gen_past_event_diff.py`).")

out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"Wrote {out}")
print(f"Events: {len(ALL_PAST_EVENTS)}  raw trick occurrences: {raw_total}")
print(f"Master tricks total: {sum(master_counts.values())}")
print(f"Unique new tricks to submit: {total_new}")
print(f"siteswap_x: {had_sx} from source, {derived_sx} derived, "
      f"{overridden_sx} manual, {still_blank} left blank")
for prop in Prop:
    n = len(by_prop.get(prop, []))
    if n:
        print(f"  {prop.value}: {n}")
