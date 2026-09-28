from datetime import date
from pylib.classes.event import CompetitorResult, PastEvent, RouteResult
from pylib.classes.prop import Prop
from pylib.classes.route import Route
from pylib.classes.trick import Trick

MJC2026 = PastEvent(
    name="Melbourne Juggling Convention 2026 (MJC)",
    date=date(2026, 9, 26),
    location="Melbourne, Australia",
    image_url="/static/images/mjc_2026_winners.jpg",
    results=[
        RouteResult(
            route=Route(
                name="MJC 2026 - Balls Open",
                prop=Prop.Balls,
                duration_seconds=600,
                tricks=[
                    Trick(name="cascade -> 1up 360 -> ball caught as elbow stall", props_count=3),
                    Trick(name="5 rounds 423, 4 and 3 as penguins", props_count=3),
                    Trick(name="shower -> mills mess -> shower to the other side", props_count=4),
                    Trick(name="cascade + ball balanced as temple (side of the head)", props_count=4),
                    Trick(name="6 rounds 63641", props_count=4),
                    Trick(name="sprung cascade -> 3up 360 in sprung -> sprung cascade", props_count=4),
                    Trick(name="while cascade: stand -> sit -> lay back shoulders to the ground -> stand", props_count=5),
                    Trick(name="6 rounds 75751", props_count=5),
                    Trick(name="async fountain -> 84", props_count=6, comment="4 in 1 hand + 2 in the other. transition: 7"),
                    Trick(name="5up 360 from cold start -> cascade", props_count=7),
                ]
            ),
            competitors={
                1: CompetitorResult(name="Ryan Hooper", tricks_accomplished=10),
                2: CompetitorResult(name="Richard Sullivan", tricks_accomplished=6),
                3: CompetitorResult(name="Joe Fisher", tricks_accomplished=6),
            }
        ),
        RouteResult(
            route=Route(
                name="MJC 2026 - Clubs Open",
                prop=Prop.Clubs,
                duration_seconds=600,
                tricks=[
                    Trick(name="overhead doubles", props_count=3),
                    Trick(name="10 sides box flats", props_count=3, comment="siteswap: (2x,4)*"),
                    Trick(name="cascade -> 2 rounds 55113, second 1 behind the back", props_count=3, siteswap_x="2 rounds 5511{B}3"),
                    Trick(name="4 rounds 53 -> exactly 1 round 633 -> 4 rounds 53", props_count=4),
                    Trick(name="12c flat-double-double", props_count=4, siteswap_x="4 round 4{0}4{2}4{2}"),
                    Trick(name="any -> 2up 360 -> 2up 360 to the other side -> any", props_count=4),
                    Trick(name="singles -> triples -> singles", props_count=5),
                    Trick(name="cascade -> 1 round 88441, under the leg 1 -> cascade", props_count=5),
                    Trick(name="cascade -> 3up 180 in backcrosses -> cascade", props_count=5),
                    Trick(name="sync fountain doubles", props_count=6),
                ]
            ),
            # All finished the route; times were not documented
            competitors={
                1: CompetitorResult(name="Joe Fisher", tricks_accomplished=10),
                2: CompetitorResult(name="Kenny Cheung", tricks_accomplished=10),
                3: CompetitorResult(name="Ryan Hooper", tricks_accomplished=10),
            }
        ),
    ]
)
