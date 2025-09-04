from datetime import date
from pylib.classes.event import CompetitorResult, PastEvent, RouteResult
from pylib.classes.prop import Prop
from pylib.classes.route import Route
from pylib.classes.trick import Trick


Sapir2025 = PastEvent(
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
                    Trick(name="3c reverse shoulders -> backcrosses", props_count=3),
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
                    Trick(name="10 backcrosses in a run", props_count=3),
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
                    Trick(name="backcrosses -> 531", props_count=3),
                    Trick(name="sync fountain -> shower", props_count=4, comment="transition: (6x,4)"),
                    Trick(name="6c 633 -> 16c 53", props_count=4),
                    Trick(name="20c isolated cascade", props_count=5),
                    Trick(name="6c ANY", props_count=6)
                ]
            ),
            competitors={1: CompetitorResult(name="Eshel Halachmi", seconds=152)}
        )
    ]
)