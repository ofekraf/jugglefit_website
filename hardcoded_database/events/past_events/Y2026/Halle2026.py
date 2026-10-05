from datetime import date
from pylib.classes.event import CompetitorResult, PastEvent, RouteResult
from pylib.classes.prop import Prop
from pylib.classes.route import Route
from pylib.classes.trick import Trick

Halle2026 = PastEvent(
    name="Halle 2026 (Tohuwabohu)",
    date=date(2026, 10, 2),
    location="Halle (Saale), Germany",
    image_url="/static/images/halle_2026_competitors.jpg",
    results=[
        RouteResult(
            route=Route(
                name="Halle 2026 - Balls Open",
                prop=Prop.Balls,
                duration_seconds=600,
                tricks=[
                    Trick(name="4 rounds 7441", props_count=4),
                    Trick(name="shower -> 2up 360 in shower -> high-low shower", props_count=4),
                    Trick(name="blindfolded reverse cascade", props_count=3),
                    Trick(name="3c cascade -> 2c backcrosses -> 1c neck throw -> cascade", props_count=3),
                    Trick(name="sit down and stand up while cascade", props_count=5),
                    Trick(name="5c cascade -> 2 rounds a44444 -> cascade", props_count=5),
                    Trick(name="5c cascade -> 1 round 66661, behind the back 1 -> 5c overheads", props_count=5),
                    Trick(name="21 catches standing on 1 leg", props_count=7),
                    Trick(name="20c (6,6)(6x,6x)", props_count=6),
                    Trick(name="6c any -> 1 round 8888811, around the body 1's -> 4up 360 -> any", props_count=6),
                ]
            ),
            competitors={
                1: CompetitorResult(name="Florian Lange", seconds=520),
                2: CompetitorResult(name="Fabian Fehlhaber", tricks_accomplished=9),
                3: CompetitorResult(name="Luca Haase", tricks_accomplished=9),
            }
        ),
        RouteResult(
            route=Route(
                name="Halle 2026 - Clubs Open",
                prop=Prop.Clubs,
                duration_seconds=600,
                tricks=[
                    Trick(name="12c flat-single-double mills mess", props_count=3),
                    Trick(name="3c cascade -> 1up 180 -> overheads", props_count=3),
                    Trick(name="exactly 3 rounds 70701 -> collect", props_count=3, comment="start: 3|0"),
                    Trick(name="sync fountain -> 2up 360 -> shower", props_count=4, comment="siteswap: (8x,6)(2,2)"),
                    Trick(name="2 rounds 633 -> 2 rounds 633, flat 3's", props_count=4, siteswap_x="2 rounds 633 -> 2 rounds 63{0}3{0}"),
                    Trick(name="10c half spin", props_count=5),
                    Trick(name="total of 4 flatfronts in a run", props_count=5),
                    Trick(name="cascade -> 1 round 753, backcross 3 -> cascade", props_count=5, siteswap_x="cascade -> 1 round 753{B} -> cascade"),
                    Trick(name="5up 360 cold start -> cascade", props_count=5),
                    Trick(name="5c cascade -> kickup -> 6c any", props_count=6),
                ]
            ),
            competitors={
                1: CompetitorResult(name="Florian Lange", seconds=550),
                2: CompetitorResult(name="Markus Utke", tricks_accomplished=7),
                3: CompetitorResult(name="Luca Haase", tricks_accomplished=7),
            }
        ),
    ]
)
