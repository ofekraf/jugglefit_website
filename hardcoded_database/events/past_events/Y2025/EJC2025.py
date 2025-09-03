from datetime import date
from pylib.classes.event import CompetitorResult, PastEvent, RouteResult
from pylib.classes.prop import Prop
from pylib.classes.route import Route
from pylib.classes.trick import Trick

EJC2025 = PastEvent(
    name="European Juggling Convention 2025 (EJC)",
    date=date(2025, 8, 8),
    location="Arnhem, the Netherlands",
    image_url="/static/images/ejc_2025_competitors.jpg",
    results=[
        RouteResult(
            route=Route(
                name="EJC 2025 - Balls open",
                prop=Prop.Balls,
                duration_seconds=600,
                tricks=[
                    Trick(name="30c 66161", props_count=4, comment="entrance: 5"),
                    Trick(name="5c cascade -> 3up 180 -> 5up 360 -> cascade", props_count=5),
                    Trick(name="reverse cascade -> 18c mills mess", props_count=5),
                    Trick(name="cascade -> 5c 94444, shoulders 4's -> overheads", props_count=5),
                    Trick(name="21c 9555855", props_count=6),
                    Trick(name="6c sync fountain -> 8c (c,c)(4,4)(4,4)(4,4) -> sync fountain", props_count=6),
                    Trick(name="6c async fountain -> 999522 4up 360 -> 756", props_count=6),
                    Trick(name="70c isolated cascade", props_count=7),
                    Trick(name="7c cascade -> db97522 5up 360 -> cascade", props_count=7),
                    Trick(name="24c any", props_count=8)
                ]
            ),
            competitors={
                1: CompetitorResult(name="Spencer Androli", seconds=232),
                2: CompetitorResult(name="Luca Pferdmenges", tricks_accomplished=430),
                3: CompetitorResult(name="Florian Lange", tricks_accomplished=478)
            }
        ),
        RouteResult(
            route=Route(
                name="EJC 2025 - Clubs Open",
                prop=Prop.Clubs,
                duration_seconds=600,
                tricks=[
                    Trick(name="10c flat underarm catches", props_count=3),
                    Trick(name="18c 741, single 7", props_count=4, comment="entrance: 5"),
                    Trick(name="5c cascade -> 5c reverse spin doubles -> 5c cascade", props_count=5),
                    Trick(name="5c cascade -> 4c 7733, backrosses 3's -> cascade", props_count=5),
                    Trick(name="cascade -> 6c a86411, 1's around the body -> singles", props_count=5),
                    Trick(name="5c cascade -> 2 connected 3up 360 -> cascade", props_count=5),
                    Trick(name="sync fountain", props_count=6),
                    Trick(name="75 -> 6c b55555 -> any", props_count=6),
                    Trick(name="10c 75774", props_count=6),
                    Trick(name="7c triples -> 7c quads", props_count=7),
                ]
            ),
            competitors={
                1: CompetitorResult(name="Spencer Androli", seconds=416),
                2: CompetitorResult(name="Florian Lange", tricks_accomplished=3),
                3: CompetitorResult(name="Kevin Niitttyviita", tricks_accomplished=2)
            }
        ),
        RouteResult(
            route=Route(
                name="EJC 2025 - Rings Open",
                prop=Prop.Rings,
                duration_seconds=600,
                tricks=[
                    Trick(name="cascade -> 5c 88441 -> cascade", props_count=5),
                    Trick(name="(6x,4)* -> (4x,6)*", props_count=5),
                    Trick(name="3up 360 -> 5up 360 -> cascade", props_count=5),
                    Trick(name="18c 534 flatfronts", props_count=4),
                    Trick(name="6c (4x,4x) alternating backross", props_count=4, comment="scissors"),
                    Trick(name="4c sync fountain -> (a,a)(4,4)(0,0)(2,2) 4up 2-stage 720 -> sync fountain", props_count=6, comment="2 high 2 low 2-stage 720"),
                    Trick(name="async fountain -> sync fountain -> async fountain", props_count=6),
                    Trick(name="any -> 1 ring pulldown + cascade -> fountain", props_count=6),
                    Trick(name="6c 75 -> 4c 9555, pancakes 5's -> 6c any", props_count=6),
                    Trick(name="40c cascade -> pulldown", props_count=7),
                ]
            ),
            competitors={
                1: CompetitorResult(name="Spencer Androli", seconds=239),
                2: CompetitorResult(name="Kevin Niitttyviita", seconds=300),
                3: CompetitorResult(name="Itamar Hai", tricks_accomplished=575)
            }
        ),
        RouteResult(
            route=Route(
                name="EJC 2025 - Balls U18",
                prop=Prop.Balls,
                duration_seconds=600,
                tricks=[
                    Trick(name="12c 561 -> 12c 741", props_count=4, comment="entrance: 5"),
                    Trick(name="sync -> (c,c)(2x,2x)(2x,2x)(2x,2x)(2x,2x) -> sync", props_count=4, comment="4 swaps"),
                    Trick(name="20c 94444", props_count=5),
                    Trick(name="(6x,4)* -> shower", props_count=5, comment="transition: (8x,6)"),
                    Trick(name="async fountain -> sync fountain -> async fountain", props_count=6),
                    Trick(name="6c any -> 6c b97531 -> half shower", props_count=6),
                    Trick(name="3c cascade -> 3c reverse shoulders -> 3c backrosses -> 3c overheads", props_count=3),
                    Trick(name="944005500 3up 2-stage -> cascade", props_count=3),
                    Trick(name="7c cascade -> 5c 99944 -> 7c cascade", props_count=7),
                    Trick(name="7c cascade -> 5up 360 -> cascade", props_count=7)
                ]
            ),
            competitors={
                1: CompetitorResult(name="Kevin Niitttyviita", seconds=229),
                2: CompetitorResult(name="Mikael Elias Eide", tricks_accomplished=5),
                3: CompetitorResult(name="Eshel Halachmi", tricks_accomplished=5),
            }
        ),
    ]
)