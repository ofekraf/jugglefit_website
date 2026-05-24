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
                name="NJF 2026 - Balls Open",
                prop=Prop.Balls,
                duration_seconds=600,
                tricks=[
                    Trick(name="overheads -> 3 rounds 531 overheads", props_count=3),
                    Trick(name="4 rounds 5561551", props_count=4),
                    Trick(name="4 rounds (4x,4x) alternating backcross", props_count=4, comment="scissors"),
                    Trick(name="shower -> 4up 360 in shower -> shower", props_count=4),
                    Trick(name="cold start 5up 360 in multiplexes -> cascade", props_count=5),
                    Trick(name="cascade -> 2 rounds b444444 -> cascade", props_count=5),
                    Trick(name="half shower", props_count=7),
                    Trick(name="60c sync fountain", props_count=6),
                    Trick(name="async fountain -> 1 round 8844, shoulder 4's -> async fountain", props_count=6),
                    Trick(name="any -> 1 round b97531, 1 up the back -> any", props_count=6),
                ]
            ),
            competitors={
                1: CompetitorResult(name="Jonny Moore", tricks_accomplished=9),
                2: CompetitorResult(name="Dan Wood", tricks_accomplished=9),
            }
        ),
        RouteResult(
            route=Route(
                name="NJF 2026 - Clubs Open",
                prop=Prop.Clubs,
                duration_seconds=600,
                tricks=[
                    Trick(name="overhead doubles", props_count=3),
                    Trick(name="6 sides box flats", props_count=3, comment="siteswap: (2x,4)*"),
                    Trick(name="cascade -> 2 rounds 55113, second 1 behind the back", props_count=3),
                    Trick(name="4 rounds 53 -> 1 round 633-> 4 rounds 53", props_count=4),
                    Trick(name="4 sides 561, single 5, single 6", props_count=4),
                    Trick(name="12c flat-double-double", props_count=4),
                    Trick(name="any -> 2up 180 -> 2up 360 -> any", props_count=4),
                    Trick(name="singles -> triples -> singles", props_count=5),
                    Trick(name="cascade -> 3 rounds 75751 -> cascade", props_count=5),
                    Trick(name="cascade -> 1 round 7733, backcrosses 3's -> cascade", props_count=5),
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
