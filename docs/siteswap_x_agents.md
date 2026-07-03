# Siteswap & Siteswap-X — Agent Reference

Reference for agents that generate, derive, or validate `siteswap_x` values in
this repo. **Do not invent notation.** If a trick name contains any construct
not covered below, leave `siteswap_x` empty rather than guess.

Authoritative sources (read these if in doubt):
- `pylib/classes/siteswap_x_modifiers.py` — the **only** legal modifier codes
- `templates/siteswap_x.html` — user-facing spec + raw-format examples
- `static/js/siteswap_x.js` — de-facto grammar (tokeniser regex)
- `hardcoded_database/tricks/*.csv` — corpus of vetted (name, siteswap_x) pairs

---

## 1. Vanilla siteswap (prerequisite)

A siteswap is a sequence of throw heights. Each character is one throw,
alternating hands (async) unless written in sync form.

- Digits `0`–`9`, then `a`=10, `b`=11, `c`=12, … (`[0-9a-z]`).
- `0` = empty hand, `1` = handoff, `2` = hold.
- **Validity:** the average of the digits equals the number of props.
  `531` → (5+3+1)/3 = 3 props. `97531` → 25/5 = 5 props. `744` → 15/3 = 5 props.
- **Sync:** `(L,R)(L,R)…`. An `x` after a digit means it crosses: `(4x,4x)`.
  `*` after the pattern means "then repeat mirrored": `(6x,4)*`.
- Base patterns: `n`-prop cascade = `n` (odd n); `n`-prop async fountain = `n`
  (even n); sync fountain = `(n,n)`; shower = `(2n)1…` or sync `(2x,2n-2)`.

If asked to emit a siteswap, **verify the digit average = props_count** before
returning it.

---

## 2. Siteswap-X: per-throw modifier braces

Siteswap-X = vanilla siteswap where any digit may be followed by `{…}`:

```
digit{ThrowModifier Spin / CatchModifier}
```

All three parts inside `{}` are optional, but at least one must be present.
`/` appears **only** if there is a catch modifier.

### Throw modifiers (before the `/`)

| Code | Meaning        |
|------|----------------|
| `B`  | Backcross      |
| `S`  | Shoulder       |
| `Ou` | Outside        |
| `In` | Inside         |
| `Ul` | Under the leg  |
| `N`  | Neck           |
| `Oh` | Overhead       |
| `F`  | Flatfront      |
| `Pc` | Pancake        |

### Spin (immediately after the throw modifier, or alone)

Integer, may be negative. Clubs/rings only in practice.

| Word           | Code  |
|----------------|-------|
| flat           | `0`   |
| single         | `1`   |
| double         | `2`   |
| triple         | `3`   |
| quad           | `4`   |
| reverse-spin single | `-1` |
| reverse-spin double | `-2` |

Combined: `B2` = backcross double, `F0` = flat flatfront, `Oh2` = overhead
double.

### Catch modifiers (after the `/`)

| Code | Meaning            |
|------|--------------------|
| `Pe` | Penguin            |
| `Rb` | Reverse backcross  |
| `Rs` | Reverse shoulder   |
| `L`  | Lazy               |
| `Ul` | Under the leg      |

### Canonical examples (from `templates/siteswap_x.html`)

| Raw            | Meaning                                            |
|----------------|----------------------------------------------------|
| `3{B}`         | backcross                                          |
| `5{Ul}`        | under-the-leg 5                                    |
| `3{B/Pe}`      | backcross thrown, penguin caught                   |
| `53{B}4{/Rs}`  | 534, backcross 3, reverse-shoulder-catch 4         |
| `5{F0}5555`    | every 5th throw flat flatfront                     |
| `3{-1/L}`      | reverse-spin singles caught as lazies              |
| `4{S1/L}23{0}` | 423: shoulder-single-lazy 4, flat 3                |

**These are the only legal codes.** If a name mentions helicopters, slapbacks,
chops, claws, tomahawks, etc. — there is no code; leave `siteswap_x` blank.

---

## 3. Outer / structural syntax

The tokeniser (`static/js/siteswap_x.js`) only recognises `[0-9a-z]` optionally
followed by `{…}`. Everything else is passed through verbatim, so the
"structural" wrapper is **free text by convention**:

| Construct        | Meaning                              | Example                         |
|------------------|--------------------------------------|---------------------------------|
| `Nc PATTERN`     | N catches of PATTERN                 | `10c 3{N}`                      |
| `N rounds SS`    | N repetitions of siteswap SS         | `2 rounds 441{B}`               |
| `N sides SS`     | N repetitions of odd-period SS       | `4 sides 5{1}6{1}1`             |
| `A -> B -> …`    | transition between segments          | `3{/L} -> 3{B}`                 |
| bare word        | named base pattern kept as text      | `cascade`, `any`, `sync fountain`, `half shower` |

`->` is rendered as `→`. Spacing is ` -> ` (one space each side).

Both `1 round` and `1 rounds` appear in the corpus; either is accepted. Prefer
grammatical (`1 round`, `2 rounds`).

### Base-pattern segments — two accepted styles

For a plain cascade/fountain segment inside a `->` chain, the corpus uses
**either** the bare digit **or** the word. Both are valid; be consistent
within one string.

| props | word style       | digit style |
|-------|------------------|-------------|
| 3     | `cascade`        | `3`         |
| 4     | `async fountain` | `4`         |
| 5     | `cascade`        | `5`         |
| 6     | `async fountain` | `6`         |
| n     | `any`            | `any`       |

---

## 4. Name → Siteswap-X derivation rules

Apply per ` -> `-segment. If **any** segment fails, return `None` for the
whole trick. `n` = `props_count`.

| Name pattern (segment)                         | Siteswap-X                                  | Attested at |
|------------------------------------------------|---------------------------------------------|-------------|
| `cascade` / `fountain` / `any` / `sync fountain` / `half shower` | verbatim                | balls.csv, clubs.csv |
| bare siteswap `SSS` (period ≥ 2)               | `SSS`                                       | everywhere |
| sync `(…,…)*`                                  | verbatim                                    | balls.csv:18 |
| `Nc SSS` / `N rounds SSS` / `N sides SSS`      | keep prefix, recurse on `SSS`               | everywhere |
| `<mod>` alone (e.g. `overheads`, `backrosses`) | `n{Mod}`                                    | balls.csv:154, clubs.csv:56 |
| `<spin>` alone (e.g. `triples`, `flats`)       | `n{spin}`                                   | clubs.csv:67-81 |
| `<mod>` `<spin>` / `<spin>` `<mod>`            | `n{ModSpin}`                                | clubs.csv:57 |
| `<spin> cascade` / `<mod> cascade`             | `n{…}`                                      | clubs.csv:70 |
| `SSS, <mod> D` / `SSS, <mod> D's`              | attach `{Mod}` to every `D` in `SSS`        | balls.csv:152-166 |
| `SSS, D's <mod>`                               | same                                        | EJC2025.py:47 |
| `SSS, <spin> D`                                | attach `{spin}` to every `D` in `SSS`       | EJC2025.py:44 |
| `SSS, <mod> D, <mod2> E`                       | attach both                                 | balls.csv:166, clubs.csv:55 |
| `SSS <mod-plural>` (e.g. `531 overheads`)      | attach `{Mod}` to **every** digit           | balls.csv:168 |
| `behind the back D` / `around the body D's`    | `{B}` on the `D`s (both map to backcross)   | balls.csv:156, NJF2026.py:44 |

Typo tolerance: `backross(es)` = `backcross(es)`.

### Sync + modifier

Modifier attaches to the digit, `x` stays adjacent. Corpus is inconsistent
(`4{B}x` vs `4x{B}`); prefer **modifier before `x`**: `(4{B}x,4x)*`.

---

## 5. Constructs siteswap-X CANNOT express — leave blank

If the name contains any of these, `siteswap_x` must be empty (or the segment
kept as plain words if it's only one part of a `->` chain and the rest is
expressible — but when unsure, bail out entirely):

- Pirouettes / body turns: `1up 360`, `3up 180`, `5up 720`, `Nup`, `N-stage`
- Body posture: `on the knees`, `laying on the back`, `isolated`,
  `blindfolded`, `one hand`, `left hand`, `right hand`
- Whole-pattern styles with no per-throw encoding: `mills mess`, `box`,
  `inverted box`, `reverse cascade`, `helicopters`, `slapbacks`, `chops`
- Meta / structure: `in a run`, `consecutive`, `connected`, `N X (…)`,
  `cold start`, `collect`, `kick up`, `multiplex`, `swap`
- Catches with no code: `ass catch`, `underarm catch`, `pulldown`, `clap`
- Anything mentioning a modifier word **not** in the tables in §2.

---

## 6. Validation checklist before emitting a `siteswap_x`

1. Every `{…}` contains only: optional ThrowModifier code, optional signed
   integer, optional `/` + CatchModifier code. Codes are **case-sensitive**
   and must exactly match §2 (e.g. `Rb` not `RB`, `Pe` not `P`).
2. No `{…}` follows anything other than a single `[0-9a-z]` char.
3. Any bare siteswap fragment averages to `props_count` (or is a recognised
   sync pattern for that count).
4. Structural words are limited to: `Nc`, `N round(s)`, `N sides`, `->`,
   `cascade`, `fountain`, `sync fountain`, `async fountain`, `any`,
   `half shower`, `shower`, `sync`, `async`.
5. **If the derived value contains no `{…}` modifier, discard it.** A
   `siteswap_x` that is just the name restated (`30c 801` → `30c 801`,
   `sync fountain -> shower` → same) adds no information and only creates
   redundant dedup keys. Only emit when at least one `{…}` appears.
6. When in doubt → **return empty**. A missing `siteswap_x` is harmless; a
   wrong one pollutes dedup (`find_master_match` matches on it).

---

## 7. Known data-quality issues (do NOT replicate)

- `clubs.csv:1` header is missing the `siteswap_x` column though rows use it.
- `clubs.csv:74,79` have a stray extra comma → 8 fields.
- `clubs.csv:57` `4c{B2}` is missing the siteswap digit (should be `4c 3{B2}`).
- `EJC2025.py:97` uses `{/RB}`; correct code is `{/Rb}`.
- `4{B}x` vs `4x{B}` both appear; standardise on `4{B}x`.
- `1 rounds` (clubs.csv:64) — accepted but prefer `1 round`.

---

## 8. Quick reference — worked derivations

| props | name                                              | siteswap_x                                  |
|------:|---------------------------------------------------|---------------------------------------------|
| 3 | `2 rounds 441, backcross 1`                           | `2 rounds 441{B}`                           |
| 3 | `10c 44133, backrosses 3's`                           | `10c 4413{B}3{B}`                           |
| 3 | `overheads -> 3 rounds 531 overheads`                 | `3{Oh} -> 3 rounds 5{Oh}3{Oh}1{Oh}`         |
| 3 | `3c reverse shoulders -> backrosses`                  | `3c 3{/Rs} -> 3{B}`                         |
| 4 | `8c 7531, under the leg 1's`                          | `8c 7531{Ul}`                               |
| 5 | `cascade -> 2 rounds 97531, behind the back 1 -> cascade` | `cascade -> 2 rounds 97531{B} -> cascade` |
| 5 | `singles -> triples -> singles`                       | `5{1} -> 5{3} -> 5{1}`                      |
| 5 | `5c cascade -> 5c reverse spin doubles -> 5c cascade` | `5c 5 -> 5c 5{-2} -> 5c 5`                  |
| 6 | `6c triples -> 6c doubles`                            | `6c 6{3} -> 6c 6{2}`                        |
| 3 | `24c 531 on the knees`                                | *(blank — §5)*                              |
| 5 | `cascade -> 5up 360 -> cascade`                       | *(blank — §5)*                              |
| 3 | `10 backrosses in a run`                              | *(blank — §5)*                              |
