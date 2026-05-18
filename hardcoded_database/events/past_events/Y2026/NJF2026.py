from datetime import date
from pylib.classes.event import CompetitorResult, PastEvent, RouteResult
from pylib.classes.prop import Prop
from pylib.classes.route import Route
from pylib.classes.trick import Trick

NJF2026 = PastEvent(
    name="Netherlands Juggling Festival 2026 (NJF)",
    date=date(2026, 5, 15),
    location="Wijk bij Duurrstede, the Netherlands",
    image_url="/static/images/njf_2026_competitors.jpg",
    results=[
        RouteResult(
            route=Route(
                name="NJF 2026 - Balls open",
                prop=Prop.Balls,
                duration_seconds=600,
                tricks=[
                    Trick(name="3 backcrosses -> 1up 360 in backcross -> cascade", props_count=3),
                    Trick(name="8c 3 in one hand", props_count=3),
                    Trick(name="6c 3 in the other hand", props_count=3),
                    Trick(name="2 rounds 7531 -> 1 round 7531, 1 under the leg", props_count=4),
                    Trick(name="sync fountain -> 1 round (6,6)(2,2), penguin 2's -> sync", props_count=4),
                    Trick(name="40c any", props_count=6),
                    Trick(name="cascade -> 2 rounds 88441 -> cascade", props_count=5),
                    Trick(name="shower -> 2 rounds high low shower", props_count=5, comment="siteswap: b171"),
                    Trick(name="half shower", props_count=7),
                    Trick(name="7c cascade -> 1 round b6666 -> 7c cascade", props_count=7),
                ]
            ),
            competitors={
                1: CompetitorResult(name="Jonny Moore", tricks_accomplished=9),
                2: CompetitorResult(name="Dan Wood", tricks_accomplished=9),
            }
        ),
        RouteResult(
            route=Route(
                name="NJF 2026 - Clubs open",
                prop=Prop.Clubs,
                duration_seconds=600,
                tricks=[
                    Trick(name="cascade -> 1up 360 in flat -> cascade", props_count=3),
                    Trick(name="cascade -> 3c backcrosses -> 3c flatfront flats", props_count=3),
                    Trick(name="2 rounds 55113, second 1 behind the back", props_count=3),
                    Trick(name="sync fountain -> async fountain", props_count=4),
                    Trick(name="async fountain -> 1 round 6631 -> any", props_count=4),
                    Trick(name="4 rounds 53 -> 1 round 7531 -> 4 rounds 534", props_count=4),
                    Trick(name="12c double-double-flat", props_count=4),
                    Trick(name="cascade on the knees", props_count=5),
                    Trick(name="5c singles -> 5c doubles -> 5c triples", props_count=5),
                    Trick(name="cascade -> 1 round 94444 -> cascade", props_count=5),
                ]
            ),
            competitors={
                1: CompetitorResult(name="Jasper Moens", tricks_accomplished=9),
                2: CompetitorResult(name="Luca Haase", tricks_accomplished=8),
                3: CompetitorResult(name="Adrian Goldwasser", tricks_accomplished=8),
            }
        ),
    ]
)
