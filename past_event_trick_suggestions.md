# Past-event tricks to suggest

Tricks that appeared in past-event routes but are **not** in the stable
master trick list (`hardcoded_database/tricks/*.csv`). These will be
submitted to `/api/suggest_trick` so they enter the crowd rating pipeline.

Match rule (same as `db_manager.find_master_match`): same `prop_type` +
`props_count` and case-insensitive equality on `name` **or** `siteswap_x`.

## Summary

| Prop | Master tricks | New from past events |
|---|---:|---:|
| balls | 174 | 91 |
| clubs | 81 | 63 |
| rings | 13 | 1 |
| club passing | 7 | 0 |
| balance | 2 | 0 |
| **Total** | **277** | **155** |

- Past-event trick occurrences scanned: **180** (across 6 events)
- Unique new tricks to submit: **155**
- Siteswap-X coverage: 19 from source, **24 auto-derived** (†), **5 manual** (‡), 107 left blank (not expressible — see `docs/siteswap_x_agents.md` §5)

### Per event (total tricks in routes)

- Sapir Con 2025: 30
- Israeli Juggling Convention 2025 (IJC): 40
- Netherlands Juggling Festival 2025 (NJF): 30
- European Juggling Convention 2025 (EJC): 40
- Tübingen Con 2025: 20
- Netherlands Juggling Festival 2026 (NJF): 20

## balls (91)

| # | Props | Name | Siteswap-X | Comment | Seen in |
|---:|---:|---|---|---|---|
| 1 | 3 | 1 round 771111, 1´s under alternating legs |  |  | Tübingen Con 2025 |
| 2 | 3 | 10 penguins in a run |  |  | Sapir Con 2025 |
| 3 | 3 | 10c 44133, backrosses 3's | 10c 4413{B}3{B} † |  | Israeli Juggling Convention 2025 (IJC) |
| 4 | 3 | 24c 531 on the knees |  |  | Israeli Juggling Convention 2025 (IJC) |
| 5 | 3 | 3 X (1up 360) in a run |  |  | Netherlands Juggling Festival 2025 (NJF) |
| 6 | 3 | 30c 801 |  |  | Netherlands Juggling Festival 2025 (NJF) |
| 7 | 3 | 3c blindfolded cascade -> 3c 531 -> 3c blindfolded cascade |  |  | Sapir Con 2025 |
| 8 | 3 | 3c cascade -> 3c reverse shoulders -> 3c backrosses -> 3c overheads | 3c 3 -> 3c 3{/RB} -> 3c 3{B} -> 3c 3{Oh} |  | European Juggling Convention 2025 (EJC) |
| 9 | 3 | 3c reverse shoulders -> backrosses | 3c 3{/Rs} -> 3{B} † |  | Sapir Con 2025 |
| 10 | 3 | 6 neck throws in a run |  |  | Sapir Con 2025 |
| 11 | 3 | 8c 5511, around the body 1's | 8c 551{B}1{B} † |  | Netherlands Juggling Festival 2025 (NJF) |
| 12 | 3 | 944005500 3up 2-stage -> cascade |  |  | European Juggling Convention 2025 (EJC) |
| 13 | 3 | backrosses -> 531 | 3{B} -> 531 † |  | Sapir Con 2025 |
| 14 | 3 | box -> 1up 360 in box -> box |  |  | Sapir Con 2025 |
| 15 | 3 | cc111111111, around the body 1's | cc1{B}1{B}1{B}1{B}1{B}1{B}1{B}1{B}1{B} † |  | Israeli Juggling Convention 2025 (IJC) |
| 16 | 3 | consecutive (6c 3 in left hand, 6c 3 in right hand) |  |  | Sapir Con 2025 |
| 17 | 3 | overheads -> 1 round 74400 3up clap in overheads -> overheads |  |  | Tübingen Con 2025 |
| 18 | 3 | overheads -> 3 rounds 531 overheads | 3{Oh} -> 3 rounds 5{Oh}3{Oh}1{Oh} † |  | Netherlands Juggling Festival 2026 (NJF) |
| 19 | 3 | overheads -> 441 overheads -> overheads | 3{Oh} -> 4{Oh}4{Oh}1{Oh} -> 3{Oh} † |  | Sapir Con 2025 |
| 20 | 4 | 10c 4 in one hand |  |  | Tübingen Con 2025 |
| 21 | 4 | 12c 561 -> 12c 741 |  | entrance: 5 | European Juggling Convention 2025 (EJC) |
| 22 | 4 | 18c 633 |  |  | Israeli Juggling Convention 2025 (IJC) |
| 23 | 4 | 20c 55613 |  |  | Netherlands Juggling Festival 2025 (NJF) |
| 24 | 4 | 20c 741 |  |  | Netherlands Juggling Festival 2025 (NJF) |
| 25 | 4 | 24c 714 |  | Entrance: 55 | Sapir Con 2025 |
| 26 | 4 | 4 rounds (4x,4x) alternating backcross | 4 rounds (4{B}x,4x)* | scissors | Netherlands Juggling Festival 2026 (NJF) |
| 27 | 4 | 4 rounds 5561551 |  |  | Netherlands Juggling Festival 2026 (NJF) |
| 28 | 4 | 4c async fountain -> 6c 633 -> 4c async fountain |  |  | Netherlands Juggling Festival 2025 (NJF) |
| 29 | 4 | 4c sync fountain -> (8x,6)(2,2) up 360 -> shower |  |  | Israeli Juggling Convention 2025 (IJC) |
| 30 | 4 | 6 rounds 66161 |  | entrance: 5 | European Juggling Convention 2025 (EJC) |
| 31 | 4 | 6c 633 -> 16c 53 |  |  | Sapir Con 2025 |
| 32 | 4 | 8c 7531, under the leg 1's | 8c 7531{Ul} † |  | Israeli Juggling Convention 2025 (IJC) |
| 33 | 4 | async overheads -> sync overheads |  |  | Netherlands Juggling Festival 2025 (NJF) |
| 34 | 4 | fountain -> 74414 -> fountain |  |  | Sapir Con 2025 |
| 35 | 4 | shower -> 4up 360 in shower -> shower |  |  | Netherlands Juggling Festival 2026 (NJF) |
| 36 | 4 | sync -> (c,c)(2x,2x)(2x,2x)(2x,2x)(2x,2x) -> sync |  | 4 swaps | European Juggling Convention 2025 (EJC) |
| 37 | 4 | sync fountain -> 2 connected 2up 360 -> sync fountain |  |  | Netherlands Juggling Festival 2025 (NJF) |
| 38 | 4 | sync fountain -> shower |  | transition: (6x,4) | Sapir Con 2025 |
| 39 | 5 | (6,4x)* -> shower |  | Transition: (8,6x) | Netherlands Juggling Festival 2025 (NJF) |
| 40 | 5 | (6x,4)* -> (4x,6)* |  |  | Sapir Con 2025 |
| 41 | 5 | (6x,4)* -> shower |  | transition: (8x,6) | European Juggling Convention 2025 (EJC), Tübingen Con 2025 |
| 42 | 5 | 2 X (3up 360 -> cascade) |  |  | Sapir Con 2025 |
| 43 | 5 | 20c 94444 |  |  | European Juggling Convention 2025 (EJC) |
| 44 | 5 | 20c isolated cascade |  |  | Sapir Con 2025 |
| 45 | 5 | 24c 744 |  |  | Sapir Con 2025 |
| 46 | 5 | 3 X (5c 97531 -> cascade) |  |  | Sapir Con 2025 |
| 47 | 5 | 5c cascade -> 1 round 7733, backrosses 3's -> cascade | 5c 5 -> 1 round 773{B}3{B} -> 5 |  | Tübingen Con 2025 |
| 48 | 5 | 5c cascade -> 3up 180 -> 5up 360 -> cascade |  |  | European Juggling Convention 2025 (EJC) |
| 49 | 5 | 5c cascade -> 3up 180 -> cascade |  |  | Netherlands Juggling Festival 2025 (NJF) |
| 50 | 5 | 5c cascade -> 7c b444444 -> backrosses | 5c cascade -> 7c b444444 -> 5{B} † |  | Israeli Juggling Convention 2025 (IJC) |
| 51 | 5 | cascade -> 1 round 94444, shoulders 4's -> overheads | 5 -> 1 round 94{S}4{S}4{S}4{S} -> 5{Oh} |  | European Juggling Convention 2025 (EJC) |
| 52 | 5 | cascade -> 2 rounds 97531, behind the back 1 -> cascade | cascade -> 2 rounds 97531{B} -> cascade † |  | Tübingen Con 2025 |
| 53 | 5 | cascade -> 2 rounds b444444 -> cascade |  |  | Netherlands Juggling Festival 2026 (NJF) |
| 54 | 5 | cascade -> 5c 88441 -> cascade |  |  | Israeli Juggling Convention 2025 (IJC) |
| 55 | 5 | cascade -> 5up clap -> cascade |  |  | Netherlands Juggling Festival 2025 (NJF) |
| 56 | 5 | cascade -> 6c 663 -> cascade |  |  | Israeli Juggling Convention 2025 (IJC) |
| 57 | 5 | cascade -> 8c 7733, neck throws 3's | cascade -> 8c 773{N}3{N} † |  | Israeli Juggling Convention 2025 (IJC) |
| 58 | 5 | cascade -> 9994400 5up 360 -> cascade |  | 2 high 3 low 5up 360 | Tübingen Con 2025 |
| 59 | 5 | cold start 5up 360 in multiplexes -> cascade |  |  | Netherlands Juggling Festival 2026 (NJF) |
| 60 | 5 | overheads cascade laying on the back |  |  | Netherlands Juggling Festival 2025 (NJF) |
| 61 | 5 | reverse cascade -> 18c mills mess |  |  | European Juggling Convention 2025 (EJC) |
| 62 | 6 | 20c a5753 |  |  | Israeli Juggling Convention 2025 (IJC) |
| 63 | 6 | 3 consecutive 6c ANY |  |  | Sapir Con 2025 |
| 64 | 6 | 3 rounds 9555855 |  |  | European Juggling Convention 2025 (EJC) |
| 65 | 6 | 50c sync fountain |  |  | Netherlands Juggling Festival 2025 (NJF) |
| 66 | 6 | 60c sync fountain |  |  | Netherlands Juggling Festival 2026 (NJF) |
| 67 | 6 | 6c ANY |  |  | Sapir Con 2025 |
| 68 | 6 | 6c any -> 6c b97531 -> half shower |  |  | European Juggling Convention 2025 (EJC) |
| 69 | 6 | 6c async any -> 4c 9555, backrosses 5's -> async any | 6c async any -> 4c 95{B}5{B}5{B} -> async any † |  | Netherlands Juggling Festival 2025 (NJF) |
| 70 | 6 | 6c async fountain -> 999522 4up 360 -> 756 |  |  | European Juggling Convention 2025 (EJC) |
| 71 | 6 | 6c sync fountain -> 4c (8,8)(4,4) -> 6c sync fountain |  |  | Netherlands Juggling Festival 2025 (NJF) |
| 72 | 6 | 6c sync fountain -> 8c (c,c)(4,4)(4,4)(4,4) -> sync fountain |  |  | European Juggling Convention 2025 (EJC) |
| 73 | 6 | 90c any isolated |  |  | Tübingen Con 2025 |
| 74 | 6 | any -> 1 round b97531, 1 up the back -> any |  |  | Netherlands Juggling Festival 2026 (NJF) |
| 75 | 6 | async fountain -> 1 round 8844, shoulder 4's -> async fountain | 6 -> 1 round 884{S}4{S} -> 6 |  | Netherlands Juggling Festival 2026 (NJF) |
| 76 | 6 | async fountain -> sync fountain -> async fountain |  |  | European Juggling Convention 2025 (EJC) |
| 77 | 6 | sync fountain |  |  | Israeli Juggling Convention 2025 (IJC) |
| 78 | 6 | sync fountain -> 1 round (a,a)(6,6)(2,2) penguin 2's -> sync fountain |  |  | Tübingen Con 2025 |
| 79 | 7 | (8x,6)* -> 5up 360 -> (8x,6)* |  |  | Netherlands Juggling Festival 2025 (NJF) |
| 80 | 7 | 3 consecutive (7c cascade -> collect) |  |  | Netherlands Juggling Festival 2025 (NJF) |
| 81 | 7 | 70c isolated cascade |  |  | European Juggling Convention 2025 (EJC) |
| 82 | 7 | 7c cascade -> 5c 99944 -> 7c cascade |  |  | European Juggling Convention 2025 (EJC) |
| 83 | 7 | 7c cascade -> 5up 360 -> cascade |  |  | European Juggling Convention 2025 (EJC) |
| 84 | 7 | 7c cascade -> db97522 5up 360 -> cascade |  |  | European Juggling Convention 2025 (EJC) |
| 85 | 7 | 7c half shower |  |  | Netherlands Juggling Festival 2025 (NJF) |
| 86 | 7 | 7c on the knees |  |  | Sapir Con 2025 |
| 87 | 7 | cascade -> 10c 99944 -> cascade |  |  | Netherlands Juggling Festival 2025 (NJF) |
| 88 | 7 | cascade -> half shower -> cascade |  |  | Tübingen Con 2025 |
| 89 | 7 | half shower |  |  | Netherlands Juggling Festival 2026 (NJF) |
| 90 | 8 | 24c 996 |  |  | Israeli Juggling Convention 2025 (IJC) |
| 91 | 8 | 24c any |  |  | European Juggling Convention 2025 (EJC) |

## clubs (63)

| # | Props | Name | Siteswap-X | Comment | Seen in |
|---:|---:|---|---|---|---|
| 1 | 3 | 10 backrosses in a run |  |  | Sapir Con 2025 |
| 2 | 3 | 10c flat underarm catches |  |  | European Juggling Convention 2025 (EJC) |
| 3 | 3 | 10c triples | 10c 3{3} † |  | Sapir Con 2025 |
| 4 | 3 | 18c reverse spin | 18c 3{-1} † |  | Israeli Juggling Convention 2025 (IJC) |
| 5 | 3 | 2 rounds 531, flatfront 5, reverse spin flatfront 3 | 2 rounds 5{F}3{F-1}1 ‡ |  | Tübingen Con 2025 |
| 6 | 3 | 20c 45123 |  |  | Israeli Juggling Convention 2025 (IJC) |
| 7 | 3 | 3c backrosses singles -> flatfronts flats | 3c 3{B1} -> 3{F0} † |  | Netherlands Juggling Festival 2025 (NJF) |
| 8 | 3 | 3c cascade -> 3c 531, single 5, single 3 -> cascade | 3c cascade -> 3c 5{1}3{1}1 -> cascade † |  | Israeli Juggling Convention 2025 (IJC) |
| 9 | 3 | 3up 360 -> cascade |  |  | Sapir Con 2025 |
| 10 | 3 | 441, behind the back 1 | 2 rounds 441{B} ‡ |  | Israeli Juggling Convention 2025 (IJC) |
| 11 | 3 | 531 -> mills mess |  |  | Sapir Con 2025 |
| 12 | 3 | 6 sides box flats |  | siteswap: (2x,4)* | Netherlands Juggling Festival 2026 (NJF) |
| 13 | 3 | blindfolded cascade |  |  | Sapir Con 2025 |
| 14 | 3 | cascade -> 2 connected 2up 360 |  |  | Netherlands Juggling Festival 2025 (NJF) |
| 15 | 3 | cascade -> 2 rounds 55113, second 1 behind the back | 2 rounds 5511{B}3 |  | Netherlands Juggling Festival 2026 (NJF) |
| 16 | 3 | overhead doubles | 3{Oh2} † |  | Netherlands Juggling Festival 2026 (NJF) |
| 17 | 3 | reverse spin lazies | 3{-1/L} |  | Tübingen Con 2025 |
| 18 | 3 | triples cascade | 3{3} † |  | Israeli Juggling Convention 2025 (IJC) |
| 19 | 4 | 10c 53534 |  |  | Israeli Juggling Convention 2025 (IJC) |
| 20 | 4 | 12c flat-double-double | 4 round 4{0}4{2}4{2} |  | Netherlands Juggling Festival 2026 (NJF) |
| 21 | 4 | 20c (4,4) double and flat, alternating | 20c (4{2},4{0})* |  | Tübingen Con 2025 |
| 22 | 4 | 4 rounds 53 -> 1 round 633-> 4 rounds 53 |  |  | Netherlands Juggling Festival 2026 (NJF) |
| 23 | 4 | 4 sides 561, single 5, single 6 | 4 sides 5{1}6{1}1 |  | Netherlands Juggling Festival 2026 (NJF) |
| 24 | 4 | 4c 6631 -> async fountain |  |  | Sapir Con 2025 |
| 25 | 4 | 4c 7333 -> 53 |  |  | Sapir Con 2025 |
| 26 | 4 | 4c any -> 10c 73451 -> async fountain |  |  | Netherlands Juggling Festival 2025 (NJF) |
| 27 | 4 | 4c any -> 2 rounds 75314, behind the back 1 | 4c any -> 2 rounds 7531{B}4 |  | Tübingen Con 2025 |
| 28 | 4 | 4c async fountain -> 4c 7441 -> 4c async fountain |  |  | Israeli Juggling Convention 2025 (IJC) |
| 29 | 4 | 4c async fountain -> 4c flats | 4c 4 -> 4c 4{0} ‡ |  | Israeli Juggling Convention 2025 (IJC) |
| 30 | 4 | 4c flats -> fountain | 4c 4{0} -> 4 ‡ |  | Sapir Con 2025 |
| 31 | 4 | 534, flatfront 5 | 5{F}34 † |  | Israeli Juggling Convention 2025 (IJC) |
| 32 | 4 | 6 rounds 741, single 7 | 6 rounds 7{1}41 | entrance: 5 | European Juggling Convention 2025 (EJC) |
| 33 | 4 | any -> 2c lazies -> 2c 53 backrosses -> any | any -> 2c 4{/L} -> 2c 5{B}3{B} -> any |  | Tübingen Con 2025 |
| 34 | 4 | any -> 2up 180 -> 2up 360 -> any |  |  | Netherlands Juggling Festival 2026 (NJF) |
| 35 | 4 | async fountain doubles -> sync fountain doubles |  | Transition: 5x,4 | Israeli Juggling Convention 2025 (IJC) |
| 36 | 5 | 15c 771 |  | entrance: 75 | Netherlands Juggling Festival 2025 (NJF) |
| 37 | 5 | 2 rounds 645 -> 8678600 5 up 360 -> cascade |  |  | Tübingen Con 2025 |
| 38 | 5 | 20c triples backrosses | 20c 5{B3} † |  | Israeli Juggling Convention 2025 (IJC) |
| 39 | 5 | 21c 7575164 |  |  | Israeli Juggling Convention 2025 (IJC) |
| 40 | 5 | 4 clubs fountain -> kick up -> 4 rounds 744 |  |  | Tübingen Con 2025 |
| 41 | 5 | 5c cascade -> 2 connected 3up 360 -> cascade |  |  | European Juggling Convention 2025 (EJC) |
| 42 | 5 | 5c cascade -> 4c 7733, backrosses 3's -> cascade | 5c 5 -> 1 round 773{B}3{B} -> 5 |  | European Juggling Convention 2025 (EJC) |
| 43 | 5 | 5c cascade -> 5c reverse spin -> 5c cascade | 5c cascade -> 5c 5{-1} -> 5c cascade † |  | Tübingen Con 2025 |
| 44 | 5 | 5c cascade -> 5c reverse spin doubles -> 5c cascade | 5c 5 -> 5c 5{-2} -> 5c 5 |  | European Juggling Convention 2025 (EJC) |
| 45 | 5 | 5c cascade on the knees |  |  | Israeli Juggling Convention 2025 (IJC) |
| 46 | 5 | 6c 663 -> 5c 88441 -> cascade |  |  | Netherlands Juggling Festival 2025 (NJF) |
| 47 | 5 | cascade |  |  | Israeli Juggling Convention 2025 (IJC) |
| 48 | 5 | cascade -> 1 round 7733, backcrosses 3's -> cascade | cascade -> 1 round 773{B}3{B} -> cascade |  | Netherlands Juggling Festival 2026 (NJF) |
| 49 | 5 | cascade -> 3 rounds 75751 -> cascade |  |  | Netherlands Juggling Festival 2026 (NJF) |
| 50 | 5 | cascade -> 5c 94444, lazies 4's -> cascade | cascade -> 5c 94{/L}4{/L}4{/L}4{/L} -> cascade † |  | Israeli Juggling Convention 2025 (IJC) |
| 51 | 5 | cascade -> 6c a86411, 1's around the body -> singles | 5 -> 1 round a86411{B} -> 5{1} ‡ |  | European Juggling Convention 2025 (EJC) |
| 52 | 5 | isolated doubles cascade |  |  | Sapir Con 2025 |
| 53 | 5 | singles -> triples -> singles | 5{1} -> 5{3} -> 5{1} |  | Tübingen Con 2025, Netherlands Juggling Festival 2026 (NJF) |
| 54 | 6 | 10c 75774 |  |  | European Juggling Convention 2025 (EJC) |
| 55 | 6 | 6c 75 -> 6c 774 |  |  | Netherlands Juggling Festival 2025 (NJF) |
| 56 | 6 | 6c fountain -> 4c 8844 -> 6c fountain |  |  | Tübingen Con 2025 |
| 57 | 6 | 6c fountain -> 6c flats | 6c fountain -> 6c 6{0} † |  | Israeli Juggling Convention 2025 (IJC) |
| 58 | 6 | 6c triples -> 6c doubles | 6c 6{3} -> 6c 6{2} † |  | Netherlands Juggling Festival 2025 (NJF) |
| 59 | 6 | 75 -> 6c b55555 -> any |  |  | European Juggling Convention 2025 (EJC) |
| 60 | 6 | sync fountain |  |  | European Juggling Convention 2025 (EJC) |
| 61 | 7 | 10c cascade |  |  | Netherlands Juggling Festival 2025 (NJF) |
| 62 | 7 | 7c triples -> 7c quads | 7c 7{3} -> 7c 7{4} |  | European Juggling Convention 2025 (EJC) |
| 63 | 7 | cascade -> 3c 966 |  |  | Israeli Juggling Convention 2025 (IJC) |

## rings (1)

| # | Props | Name | Siteswap-X | Comment | Seen in |
|---:|---:|---|---|---|---|
| 1 | 4 | 6c (4x,4x) alternating backross | 6c (4x,4x{B}) | scissors | European Juggling Convention 2025 (EJC) |

† auto-derived from name per `docs/siteswap_x_agents.md`.  ‡ manual override (`SX_OVERRIDES` in `scripts/gen_past_event_diff.py`).
