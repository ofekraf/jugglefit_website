from datetime import date
from pylib.classes.event import CompetitorResult, PastEvent, RouteResult
from pylib.classes.prop import Prop
from pylib.classes.route import Route
from pylib.classes.trick import Trick

# @Todo: add image_url when available
Tubingen2025 = PastEvent(
    name="Tübingen Con 2025",
    date=date(2025, 10, 4),
    location="Tubingen, Germany",
    image_url="/static/images/Tubingen_2025_competitors.jpg",
    results=[
        RouteResult(
            route=Route(
                name="Tubingen 2025 - Balls Open",
                prop=Prop.Balls,
                duration_seconds=600,
                tricks=[
                    Trick(name="overheads -> 1 round 74400 3up clap in overheads -> overheads", props_count=3),
                    Trick(name="1 round 771111, 1´s under alternating legs", props_count=3),
                    Trick(name="10c 4 in one hand", props_count=4),
                    Trick(name="cascade -> 2 rounds 97531, behind the back 1 -> cascade", props_count=5),
                    Trick(name="cascade -> 9994400 5up 360 -> cascade", props_count=5, comment="2 high 3 low 5up 360"),
                    Trick(name="5c cascade -> 1 round 7733, backrosses 3's -> cascade", props_count=5),
                    Trick(name="(6x,4)* -> shower", props_count=5, comment="Transition: (8x,6)"),
                    Trick(name="90c any isolated", props_count=6),
                    Trick(name="sync fountain -> 1 round (a,a)(6,6)(2,2) penguin 2's -> sync fountain", props_count=6),
                    Trick(name="cascade -> half shower -> cascade", props_count=7),
                ]
            ),
            competitors={
                1: CompetitorResult(name="Kevin Niitttyviita", tricks_accomplished=8),
                2: CompetitorResult(name="Florian Lange", tricks_accomplished=8),
                3: CompetitorResult(name="Julian Kloos", tricks_accomplished=8)
            }
        ),
        RouteResult(
            route=Route(
                name="Tubingen 2025 - Clubs open",
                prop=Prop.Clubs,
                duration_seconds=600,
                tricks=[
                    Trick(name="2 rounds 531, flatfront 5, reverse spin flatfront 3", props_count=3),
                    Trick(name="reverse spin lazies", props_count=3),
                    Trick(name="20c (4,4) double and flat, alternating", props_count=4),
                    Trick(name="4c any -> 2 rounds 75314, behind the back 1", props_count=4),
                    Trick(name="any -> 2c lazies -> 2c 53 backrosses -> any", props_count=4),
                    Trick(name="5c cascade -> 5c reverse spin -> 5c cascade", props_count=5),
                    Trick(name="4 clubs fountain -> kick up -> 4 rounds 744", props_count=5),
                    Trick(name="singles -> triples -> singles", props_count=5),
                    Trick(name="2 rounds 645 -> 8678600 5 up 360 -> cascade", props_count=5),
                    Trick(name="6c fountain -> 4c 8844 -> 6c fountain", props_count=6),
                ]
            ),
            competitors={
                1: CompetitorResult(name="Kevin Niitttyviita", tricks_accomplished=9),
                2: CompetitorResult(name="Julian Kloos", tricks_accomplished=9),
                3: CompetitorResult(name="Florian Lange", tricks_accomplished=8)
            }
        ),
    ]
)