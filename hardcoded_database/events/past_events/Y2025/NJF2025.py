from datetime import date
from pylib.classes.event import CompetitorResult, PastEvent, RouteResult
from pylib.classes.prop import Prop
from pylib.classes.route import Route
from pylib.classes.trick import Trick

NJF2025 = PastEvent(
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
                name="NJF 2025 - Balls U18",
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
)