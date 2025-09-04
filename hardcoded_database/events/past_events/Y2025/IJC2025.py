from datetime import date
from pylib.classes.event import CompetitorResult, PastEvent, RouteResult
from pylib.classes.prop import Prop
from pylib.classes.route import Route
from pylib.classes.trick import Trick

IJC2025 = PastEvent(
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
                    Trick(name="5c cascade -> 7c b444444 -> backcrosses", props_count=5),
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
                    Trick(name="20c triples backcrosses", props_count=5),
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
                    Trick(name="10c 44133, backcrosses 3's", props_count=3),
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
)