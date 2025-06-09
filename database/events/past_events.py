from py_lib.event import CompetitorResult, PastEvent, RouteResult
from py_lib.route import Route
from py_lib.prop import Prop
from py_lib.trick import Trick
from datetime import date

# Keep ordered by date
FRONT_PAGE_PAST_EVENTS = [
    PastEvent(
        name="Sapir Juggling Convention 2025",
        date=date(2025, 1, 17),
        location="Sapir, Israel", 
        image_url="/static/images/sapir_juggling_convention_2025_winners.png",
        results=[
            RouteResult(
                route=Route(
                    name="Sapir 2025 - Balls open",
                    prop=Prop.Balls,
                    duration_seconds=600,
                    tricks=[
                        Trick(name="6 neck throws in a run", props_count=3),
                        Trick(name="3c blindfolded cascade -> 3c 531 -> 3c blindfolded cascade", props_count=3),
                        Trick(name="3c reverse shoulders -> backrosses", props_count=3),
                        Trick(name="fountain -> 74414 -> fountain", props_count=4),
                        Trick(name="24c 714", props_count=4, comment="Entrance: 55"),
                        Trick(name="24c 744", props_count=5),
                        Trick(name="3 X (5c 97531 -> cascade)", props_count=5),
                        Trick(name="(6x,4)* -> (4x,6)*", props_count=5),
                        Trick(name="2 X (3up 360 -> cascade)", props_count=5),
                        Trick(name="3 consecutive 6c ANY", props_count=6),
                        Trick(name="7c on the knees", props_count=7)             
                    ]
                ),
                competitors={1: CompetitorResult(name="Dror Lotan", seconds=257)}
            ),
            RouteResult(
                route=Route(
                    name="Sapir 2025 - Clubs open",
                    prop=Prop.Clubs,
                    duration_seconds=600,
                    tricks=[
                        Trick(name="10 backrosses in a run", props_count=3),
                        Trick(name="10c triples", props_count=3),
                        Trick(name="531 -> mills mess", props_count=3),
                        Trick(name="blindfolded cascade", props_count=3),
                        Trick(name="3up 360 -> cascade", props_count=3),
                        Trick(name="4c flats -> fountain", props_count=4),
                        Trick(name="4c 7333 -> 53", props_count=4),
                        Trick(name="4c 6631 -> async fountain", props_count=4),
                        Trick(name="isolated doubles cascade", props_count=5)
                    ]
                ),
                competitors={1: CompetitorResult(name="Daniel Ackerman", seconds=135)}
            ),
            RouteResult(
                route=Route(
                    name="Sapir 2025 - Balls U18",
                    prop=Prop.Balls,
                    duration_seconds=600,
                    tricks=[
                        Trick(name="10 penguins in a run", props_count=3),
                        Trick(name="box -> 1up 360 in box -> box", props_count=3),
                        Trick(name="overheads -> 441 overheads -> overheads", props_count=3),
                        Trick(name="consecutive (6c 3 in left hand, 6c 3 in right hand)", props_count=3),
                        Trick(name="3up 360 -> cascade", props_count=3),
                        Trick(name="backrosses -> 531", props_count=3),
                        Trick(name="sync fountain -> shower", props_count=4, comment="transition: (6x,4)"),
                        Trick(name="6c 633 -> 16c 53", props_count=4),
                        Trick(name="20c isolated cascade", props_count=5),
                        Trick(name="6c ANY", props_count=6)
                    ]
                ),
                competitors={1: CompetitorResult(name="Eshel Halachmi", seconds=152)}
            )
        ]
    ),
    PastEvent(
        name="Israeli Juggling Convention 2025 (IJC)",
        date=date(2025, 4, 17),
        location="Gan Hashlosha, Israel",
        image_url="/static/images/ijc_2025_winners.jpg",
        results=[
            RouteResult(
                route=Route(
                    name="IJC 2025 - Balls open",
                    prop=Prop.Balls,
                    duration_seconds=600,
                    tricks=[
                        Trick(name="8c 7531, under the leg 1's", props_count=4),
                        Trick(name="async fountain -> 4up 360 -> 2up 360 -> sync fountain", props_count=4),
                        Trick(name="half shower -> overheads -> other side half shower", props_count=5),
                        Trick(name="5c cascade -> 7c b444444 -> backrosses", props_count=5),
                        Trick(name="cascade -> 8c 7733, neck throws 3's", props_count=5),
                        Trick(name="20c a5753", props_count=6),
                        Trick(name="(8,4)* -> (c,4)(4,c)(c,8)(2,2)(2,2) 4up 720 -> (8,4)*", props_count=6),
                        Trick(name="867 -> 1 high 4 low 360 -> (8,6x)*", props_count=7, comment="spin notation: ex9x89x822"),
                        Trick(name="cc111111111, around the body 1's", props_count=3),
                        Trick(name="24c 996", props_count=8),
                    ]
                ),
                competitors={
                    1: CompetitorResult(name="Sise juggler", tricks_accomplished=5),
                    2: CompetitorResult(name="Spencer Androli", tricks_accomplished=5),
                    3: CompetitorResult(name="Luca Pferdmenges", tricks_accomplished=5)
                }
            ),
            RouteResult(
                route=Route(
                    name="IJC 2025 - Clubs open",
                    prop=Prop.Clubs,
                    duration_seconds=600,
                    tricks=[
                        Trick(name="18c reverse spin", props_count=3),
                        Trick(name="4c singles -> 4c doubles -> 4c triples -> 4c singles", props_count=4),
                        Trick(name="534, flatfront 5", props_count=4),
                        Trick(name="cascade -> 5c 66751 -> cascade", props_count=5),
                        Trick(name="cascade -> 5up 180 -> cascade", props_count=5),
                        Trick(name="21c 7575164", props_count=5),
                        Trick(name="20c triples backrosses", props_count=5),
                        Trick(name="cascade -> 5c 94444, lazies 4's -> cascade", props_count=5),
                        Trick(name="6c fountain -> 6c flats", props_count=6),
                        Trick(name="cascade -> 3c 966", props_count=7),
                    ]
                ),
                competitors={
                    1: CompetitorResult(name="Spencer Androli", seconds=205),
                    2: CompetitorResult(name="Luca Pferdmenges", tricks_accomplished=7),
                    3: CompetitorResult(name="Sise Juggler", tricks_accomplished=6)
                }
            ),
            RouteResult(
                route=Route(
                    name="IJC 2025 - Balls U18",
                    prop=Prop.Balls,
                    duration_seconds=600,
                    tricks=[
                        Trick(name="24c 531 on the knees", props_count=3),
                        Trick(name="5 X (1up 360) in a run", props_count=3),
                        Trick(name="10c 44133, backrosses 3's", props_count=3),
                        Trick(name="cascade -> 74400 3up 360 -> cascade", props_count=3),
                        Trick(name="18c 633", props_count=4),
                        Trick(name="4c sync fountain -> (8x,6)(2,2) up 360 -> shower", props_count=4),
                        Trick(name="cascade -> 6c 663 -> cascade", props_count=5),
                        Trick(name="cascade -> 5c 88441 -> cascade", props_count=5),
                        Trick(name="sync fountain", props_count=6),
                        Trick(name="cascade", props_count=7),
                    ]
                ),
                competitors={
                    1: CompetitorResult(name="Noam Fruchter", seconds=151),
                    2: CompetitorResult(name="Yuval Levi", seconds=344),
                    3: CompetitorResult(name="Eshel Halachmi", seconds=402)
                }
            ),
            RouteResult(
                route=Route(
                    name="IJC 2025 - Clubs U18",
                    prop=Prop.Clubs,
                    duration_seconds=600,
                    tricks=[
                        Trick(name="3c cascade -> 3c 531, single 5, single 3 -> cascade", props_count=3),
                        Trick(name="triples cascade", props_count=3),
                        Trick(name="441, behind the back 1", props_count=3),
                        Trick(name="20c 45123", props_count=3),
                        Trick(name="10c 53534", props_count=4),
                        Trick(name="4c async fountain -> 4c 7441 -> 4c async fountain", props_count=4),
                        Trick(name="async fountain doubles -> sync fountain doubles", props_count=4, comment="Transition: 5x,4"),
                        Trick(name="4c async fountain -> 4c flats", props_count=4),
                        Trick(name="cascade", props_count=5),
                        Trick(name="5c cascade on the knees", props_count=5),
                    ]
                ),
                competitors={
                    1: CompetitorResult(name="Eshel Halachmi", seconds=212),
                    2: CompetitorResult(name="Noam Fruchter", seconds=298),
                    3: CompetitorResult(name="Nami Segev", tricks_accomplished=5)
                }
            ),
        ]
    ),
    PastEvent(
        name="Netherlands Juggling Festival 2025 (NJF)",
        date=date(2025, 5, 31),
        location="Waalwijk, the Netherlands",
        image_url="/static/images/njf_2025_competitors.jpg",
        results=[
            RouteResult(
                route=Route(
                    name="NJF 2025 - Balls open",
                    prop=Prop.Balls,
                    duration_seconds=600,
                    tricks=[
                        Trick(name="sync fountain -> 2 connected 2up 360 -> sync fountain", props_count=4),
                        Trick(name="20c 55613", props_count=4),
                        Trick(name="9440022 3up 2-stage -> cascade", props_count=3),
                        Trick(name="30c 801", props_count=3),
                        Trick(name="overheads cascade laying on the back", props_count=5),
                        Trick(name="(6,4x)* -> shower", props_count=5, comment="Transition: (8,6x)"),
                        Trick(name="50c sync fountain", props_count=6),
                        Trick(name="6c async any -> 4c 9555, backrosses 5's -> async any", props_count=6),
                        Trick(name="cascade -> 10c 99944 -> cascade", props_count=7),
                        Trick(name="(8x,6)* -> 5up 360 -> (8x,6)*", props_count=7),
                    ]
                ),
                competitors={
                    1: CompetitorResult(name="Luca Pferdmenges", tricks_accomplished=8),
                    2: CompetitorResult(name="Mees Jager", tricks_accomplished=7),
                    3: CompetitorResult(name="Diminik Harant", tricks_accomplished=7)
                }
            ),
            RouteResult(
                route=Route(
                    name="NJF 2025 - Clubs open",
                    prop=Prop.Clubs,
                    duration_seconds=600,
                    tricks=[
                        Trick(name="3c backrosses singles -> flatfronts flats", props_count=3),
                        Trick(name="cascade -> 2 connected 2up 360", props_count=3),
                        Trick(name="4c any -> 10c 73451 -> async fountain", props_count=4),
                        Trick(name="sync fountain -> (8,8)(4,4)(0,0) 4up 360 -> sync fountain", props_count=4),
                        Trick(name="6c 663 -> 5c 88441 -> cascade", props_count=5),
                        Trick(name="cascade -> 97522 3up 360 -> cascade", props_count=5),
                        Trick(name="15c 771", props_count=5, comment="entrance: 75"),
                        Trick(name="6c triples -> 6c doubles", props_count=6),
                        Trick(name="6c 75 -> 6c 774", props_count=6),
                        Trick(name="10c cascade", props_count=7),
                    ]
                ),
                competitors={
                    1: CompetitorResult(name="Luca Pferdmenges", tricks_accomplished=8),
                    2: CompetitorResult(name="Dominik Harant", tricks_accomplished=5),
                    3: CompetitorResult(name="Jasper Moens", tricks_accomplished=5)
                }
            ),
            RouteResult(
                route=Route(
                    name="IJC 2025 - Balls U18",
                    prop=Prop.Balls,
                    duration_seconds=600,
                    tricks=[
                        Trick(name="3 X (1up 360) in a run", props_count=3),
                        Trick(name="8c 5511, around the body 1's", props_count=3),
                        Trick(name="4c async fountain -> 6c 633 -> 4c async fountain", props_count=4),
                        Trick(name="async overheads -> sync overheads", props_count=4),
                        Trick(name="20c 741", props_count=4),
                        Trick(name="cascade -> 5up clap -> cascade", props_count=5),
                        Trick(name="5c cascade -> 3up 180 -> cascade", props_count=5),
                        Trick(name="6c sync fountain -> 4c (8,8)(4,4) -> 6c sync fountain", props_count=6),
                        Trick(name="3 consecutive (7c cascade -> collect)", props_count=7),
                        Trick(name="7c half shower", props_count=7),
                    ]
                ),
                competitors={
                    1: CompetitorResult(name="Boris de Schipper", tricks_accomplished=3),
                }
            ),
        ]
    ),
]

# Move here events to remove it from the website's front page
# Keep ordered by date
NON_FRONT_PAGE_PAST_EVENTS = [
    
]

# @TODO: order by date from oldest to newest
ALL_PAST_EVENTS = FRONT_PAGE_PAST_EVENTS + NON_FRONT_PAGE_PAST_EVENTS
ALL_PAST_EVENTS.sort(key=lambda x: x.date)