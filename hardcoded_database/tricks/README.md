# Hardcoded trick lists

One CSV per `Prop` value (`balls.csv`, `clubs.csv`, `rings.csv`,
`club passing.csv`, `balance.csv`). These files are the only source of
tricks: `pylib/utils/trick_registry.py` loads them at import time, so an
edit takes effect on the next app restart. There is no database copy.

## Columns

```
name,props_count,difficulty,tags,comment,max_throw,siteswap_x
```

| Column | Rules |
|---|---|
| `name` | Required, max 100 chars. Written in the notation below. |
| `props_count` | Number of props in the trick (not in the entry/exit pattern). |
| `difficulty` | Integer 0-100. Relative scale, compare with neighbours (see below). |
| `tags` | `\|`-separated values of `pylib/classes/tag.py::Tag`. Unknown tags fail loading. |
| `comment` | Optional: entrance siteswap, transition, start position, nickname. |
| `max_throw` | Highest siteswap throw in the trick (spins: count the up throw). Used by the "max throw" filter. |
| `siteswap_x` | Optional. Only when it adds a `{...}` modifier. Rules: `docs/siteswap_x_agents.md`. |

Rows are sorted by `difficulty`, then `props_count`, then `name`. Quote
`name`, `tags`, `comment` and `siteswap_x`; a row with more columns than the
header fails loading.

## Name notation

| Construct | Meaning | Example |
|---|---|---|
| `N catches PATTERN` | N catches of PATTERN, counted from the first catch (`1 catch` for one) | `20 catches cascade` |
| `N rounds SS` | N repetitions of siteswap SS | `6 rounds 534` |
| `N sides SS` | N repetitions of an odd-period siteswap (one side = one period) | `4 sides 561` |
| `exactly ...` | Exactly that many repetitions, no more | `53 -> exactly 1 round 633 -> other sided 53` |
| `A -> B` | Transition from A straight into B, no throws in between | `cascade -> 1 round 97531 -> cascade` |
| `SS, <mod> D` | Apply a body throw / spin to throw D of SS | `8 rounds 423, backcross 3` |
| `SS <mods>` | Apply to every throw | `3 rounds 531 overheads` |
| `Nup 360` | Pirouette under N props in the air | `cascade -> 3up 360 -> cascade` |
| `SSSSS Nup 360` | Siteswap that launches the pirouette | `75300 3up 360 -> cascade` |
| `N X (...)` / `N consecutive` / `in a run` | Repetitions with nothing else between them | `3 X (1up 360) in a run` |
| `-> collect` | End by catching everything (used after cold starts / spins) | `8 catches ANY -> 4up 360 -> collect` |

Always spell out `catches`; do not abbreviate to `Nc` (older event files
still use `20c cascade`, which means the same thing).

Base pattern words: `cascade` (odd), `async fountain` / `sync fountain`
(even), `ANY` (any base pattern, sync or async, the juggler's choice),
`half shower`, `shower`. A bare `cascade` / `fountain` with no count
means "qualify": at least 2 x props catches.

**Catches vs rounds.** Use `N catches` for base patterns and body-throw /
spin-control runs (`20 catches cascade`, `6 catches backcrosses`,
`10 catches triples`). Use `N rounds` for siteswaps (`6 rounds 534`,
`1 round 97531`), so the length always matches the siteswap period. Never
write `5 catches 53534`: half a round is ambiguous. Exception: a
deliberate odd count kept as `exactly N catches ...`
(e.g. `6 catches 60 -> exactly 5 catches 50505 -> 6 catches 60`).

## Siteswap notation (short reference)

Siteswap describes a pattern as a repeating list of throw heights, one
number per beat, hands alternating (right, left, right, ...).

- **Throw values:** `0-9`, then letters `a`=10, `b`=11, `c`=12, `d`=13.
  The number is how many beats later the prop lands again. Odd numbers
  cross to the other hand, even numbers come back to the same hand.
  - `0` = empty hand (no prop), `1` = quick hand-off to the other hand,
    `2` = hold (normally no throw), `3` = 3-ball cascade height,
    `4` = 4-ball fountain height, and so on.
- **Prop count** = average of the values. `531` -> (5+3+1)/3 = 3 props;
  `744` -> 5 props; `97531` -> 5 props. If the average is not
  `props_count`, the trick is wrong.
- **Valid pattern:** no two props may land on the same beat: for every
  position `i`, `(i + value) mod period` must be different.
  `543` is invalid (all land together); `534` is valid.
- **Base patterns:** n props = `n` repeated (`3` = cascade, `4` = async
  fountain, `5` = cascade). Showers: `51` (3), `71` (4). Half shower is
  written by name.
- **One round** = the written sequence once. `1 round 441` = 3 throws.
  Period-odd siteswaps (`531`) start on alternate hands each round;
  "side" = one round from one hand. `N sides 561` = N rounds.
- **Transitions** (`cascade -> 1 round 97531 -> cascade`): the siteswap
  must fit between the patterns. Long entries are written in `comment`
  (`Entrance: 46` means throw 4 then 6 before starting `801`).
- **Spin launches:** `75300 3up 360` = throw 7, 5, 3, then two empty
  beats (`00`) while you turn under 3 props in the air.
- **Sync** (both hands throw together): `(L,R)` per beat, values are even,
  `x` = crosses. `(4,4)` = 4-ball sync fountain, `(6x,4)*` = 5 balls.
  `*` = repeat with hands swapped. `(4x,4x)` = crossing sync. A sync beat
  counts 2 catches.
- **Multiplex** `[43]` = two props thrown at once from one hand. Rare
  here; written by name.
- **Siteswap-X** adds per-throw modifiers in braces (`3{B}` backcross,
  `4{S}` shoulder, `5{1}` single spin). Full rules:
  `docs/siteswap_x_agents.md`.

## Duplicates

Two rows are the same trick if they have the same `props_count` and,
after these rewrites, the same name:

1. **Flash = N catches of the base pattern.** `1 round 666666 flash ->
   collect` is `6 catches async fountain`; `1 round (6,6)(6,6)(6,6)` is
   `6 catches sync fountain`. Write flashes as
   `N catches <base pattern>` with N = props_count.
2. **Rounds = catches.** `N rounds SS` is `N x (catches per round)
   catches SS`: `4 rounds 94444` = `20 catches 94444`. Siteswaps are always
   written as `N rounds` (see "Catches vs rounds").
3. **`Nc` = `N catches`** (old abbreviation, still in event files).
4. **Base pattern synonyms.** For odd N: `cascade` = `N`; for even N:
   `fountain` = `async fountain` = `N`. `ANY` is **not** a synonym of
   `async fountain` (it also allows sync).
5. **One-round transitions.** `cascade -> 1 round 88441 -> cascade` =
   `cascade -> 5 catches 88441 -> cascade`; also
   `N catches cascade -> ...` vs `cascade -> ...` differ only in entry
   length: keep one.
6. Spelling variants (`backross` / `backcross`, `1 round` / `1 rounds`).

Not duplicates (keep): the same pattern with clearly different catch
counts (`10` / `20` / `50 catches cascade`): they form a difficulty ladder.
Also distinct: `cascade -> X` vs `X -> cascade` (entry vs exit), and a
trick with vs without "isolated" / "on the knees" / "blindfolded".

Before adding a trick, search both its name and its rewritten form.

## Difficulty scale

Integer 0-100, relative within a prop. Rough anchors:

| Difficulty | Balls | Clubs |
|---|---|---|
| 0-5 | 1-2 ball drills, short 3 ball cascade | 1 club spins, 2 club exchange |
| 5-10 | 3 ball tricks (441, overheads, half shower, 1up 360) | 3 club cascade runs, doubles |
| 10-15 | box, mills mess, 3 ball backcrosses, 4 ball fountain runs | 3 club siteswaps, single body throws |
| 15-20 | 3 in one hand, 4 ball siteswaps, 5 ball flash | lazies / flats / triples, 4 club fountain |
| 20-40 | 5 ball cascade runs, 3 ball multi body throws | 3 club body throw runs, 4 club siteswaps, 5 club flash |
| 40-70 | 6-7 balls, 5 ball 360s | 5 clubs, 4 club spins |
| 70-100 | 7+ ball spins, 8-9 balls | 6-7 clubs, 5+ club spins |

The same trick name is usually harder with clubs than with balls. Long
catch counts raise difficulty, but less than adding a prop.

## Limitations

- **No siteswap for:** pirouettes, body posture (knees, sitting, lying,
  blindfolded, one leg), whole-pattern styles (mills mess, box name,
  reverse cascade, tennis, chops, claws, windmill, helicopters,
  slapbacks), balances, kick ups, multiplexes, collects. These rely on
  the name only; leave `siteswap_x` empty (see
  `docs/siteswap_x_agents.md` section 5).
- **1-2 props:** don't write `siteswap_x` with digit 3 for a 1 or 2 prop
  trick; the digit has to fit the prop count (`1 catch 1{Ul}`).
- **Not used on purpose:** alberts / treblas (leg-through throws), burke's
  barrage and yo-yo are left out of the lists.
- **Box** is `(4,2x)*` (3 balls).
- **Prop-specific catches:** balls are caught as **penguins**, clubs as
  **lazies**. Don't add "lazy" ball tricks or "penguin" club tricks.
- **1-2 props:** `in a run` (a continuous pattern) is only defined for 3+
  props. With 1-2 props, use "in a row" for repeated throws, or a plain
  catch count for normal throws (`10 catches 1 ball cascade`). Simple
  body throws (backcrosses, under the leg, overheads) with 2 props are not
  tricks; write 2-prop patterns as siteswaps where possible
  (`4 rounds 330` = 2 in one hand, switching hands every 2 throws).
- **1 prop spins are not trivial:** `1 catch 1up 360` is ~12 with balls,
  `1 catch 1up 720` ~20 (clubs a little higher).
- **Difficulty is hand-assigned**, not measured. Many values come from
  past events or were set by analogy; adjust them when real results
  disagree.
- **User feedback:** generated routes show Dislike / Too hard / Too easy
  buttons per trick. Review the votes with
  `python scripts/trick_feedback_report.py` and edit this CSV by hand.
  Votes are never applied automatically: a few votes are noise, and a
  "too hard" vote often means the trick suits a different prop count or
  route, not that its number is wrong.
- The name is free text: the app does not parse it. Only `siteswap_x`
  is rendered as notation.
