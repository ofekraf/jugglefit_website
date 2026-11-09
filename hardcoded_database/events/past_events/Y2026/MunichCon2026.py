from datetime import date
from pylib.classes.event import CompetitorResult, PastEvent, RouteResult
from pylib.classes.prop import Prop
from pylib.classes.route import Route
from pylib.classes.trick import Trick

MunichCon2026 = PastEvent(
    name="Muenchen Con 2026",
    date=date(2026, 11, 6),
    location="Munich, Germany",
    image_url="/static/images/munich_2026_competitors.jpg",
    results=[
        RouteResult(
            route=Route(
                name="Munich 2026 - Balls - Finals",
                prop=Prop.Balls,
                duration_seconds=600,
                tricks=[
                    Trick(name="crossed arm any", props_count=4),
                    Trick(name="wimpy -> 4 catches backcrosses in wimpy -> wimpy", props_count=4),
                    Trick(name="half shower -> 4up 180 in half shower -> other sided half shower", props_count=4),
                    Trick(name="3 rounds 94444 standing on 1 leg", props_count=5),
                    Trick(name="full slow 360 while 5 balls shower", props_count=5),
                    Trick(name="(6,4) -> 5up 360 in (6,4) -> (6,4)", props_count=5),
                    Trick(name="one sided overheads any", props_count=6),
                    Trick(name="4 rounds 7777716", props_count=6),
                    Trick(name="non-comfortable side half shower", props_count=7),
                    Trick(name="7 catches cascade -> 1 rounds 99999911, around the body 1's -> cascade", props_count=7),
                ]
            ),
            competitors={
                1: CompetitorResult(name="Kevin Niittyviita", seconds=148),
                2: CompetitorResult(name="Florian Lange", seconds=283),
                3: CompetitorResult(name="Luca Pferdmenges", seconds=488),
            }
        ),
        RouteResult(
            route=Route(
                name="Munich 2026 - Clubs - Finals",
                prop=Prop.Clubs,
                duration_seconds=600,
                tricks=[
                    Trick(name="mills mess doubles", props_count=3),
                    Trick(name="cascade -> 1 up 180 -> overheads", props_count=3),
                    Trick(name="sync flatfronts -> async flatfronts -> sync flatfronts", props_count=4),
                    Trick(name="3 rounds 66611, around the body 1's", props_count=4),
                    Trick(name="4 rounds 534, backcross 5", props_count=4),
                    Trick(name="triples -> flats", props_count=5),
                    Trick(name="10 catches half spin", props_count=5),
                    Trick(name="645 -> 3up 360 in 645 -> 645", props_count=5),
                    Trick(name="40 catches any", props_count=6),
                    Trick(name="6 catches triples -> 6 catches quads", props_count=6),
                ]
            ),
            competitors={
                1: CompetitorResult(name="Florian Lange", seconds=225),
                2: CompetitorResult(name="Kevin Niittyviita", seconds=264),
                3: CompetitorResult(name="Luca Pferdmenges", seconds=389),
            }
        ),
    ]
)
