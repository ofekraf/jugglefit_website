from datetime import date
from pylib.classes.event import CompetitorResult, PastEvent, RouteResult
from pylib.classes.prop import Prop
from pylib.classes.route import Route
from pylib.classes.trick import Trick

EJC2026 = PastEvent(
    name="European Juggling Convention 2026 (EJC)",
    date=date(2026, 8, 6),
    location="Ptuj, Slovenia",
    image_url="/static/images/ejc_2026_competitors.jpg",
    results=[
        RouteResult(
            route=Route(
                name="EJC 2026 - Balls Open",
                prop=Prop.Balls,
                duration_seconds=600,
                tricks=[
                    Trick(name="seated async overheads -> seated sync overheads", props_count=4),
                    Trick(name="cascade -> shower", props_count=5, comment="transition: 678"),
                    Trick(name="mills mess -> crossed arms reverse cascade", props_count=5),
                    Trick(name="5c cascade -> 2 rounds 753, under the leg 3 -> 5c cascade", props_count=5, siteswap_x="5c cascade -> 2 rounds 753{Ul} -> 5c cascade"),
                    Trick(name="cascade -> 3up 360 -> 3up 360 spin to the other size -> cascade", props_count=5),
                    Trick(name="4 rounds 645, backcross 5", props_count=5, siteswap_x="4 rounds 645{B}"),
                    Trick(name="12 rounds 864", props_count=6),
                    Trick(name="sync fountain -> (a,a)(6,6)(2,2) 4up 360 -> sync fountain", props_count=6, comment="sync 2 high 2 low 360"),
                    Trick(name="7c cascade -> 1 round ANY with 1, 1 under the leg -> cascade", props_count=7),
                    Trick(name="cascade -> 1 round aa555 -> cascade", props_count=7),
                ]
            ),
            competitors={
                1: CompetitorResult(name="Kevin Niitttyviita", seconds=403),
                2: CompetitorResult(name="Komiken", seconds=439),
                3: CompetitorResult(name="Luca Pferdmenges", seconds=568),
            }
        ),
        RouteResult(
            route=Route(
                name="EJC 2026 - Clubs Open",
                prop=Prop.Clubs,
                duration_seconds=600,
                tricks=[
                    Trick(name="6 rounds 642, reverse spin 2", props_count=4, siteswap_x="6 rounds 642{-1}"),
                    Trick(name="6 rounds 534, backcross 5", props_count=4, siteswap_x="6 rounds 5{B}34"),
                    Trick(name="3c cascade -> 1up 540 -> overheads", props_count=3),
                    Trick(name="triples -> singles -> triples -> singles", props_count=5),
                    Trick(name="5c cascade -> 1 round 995511, around the body 1's -> cascade", props_count=5, siteswap_x="5 -> 1 round 995511{B} -> 5"),
                    Trick(name="5c cascade -> 3 rounds 744, flat 4's -> 5c cascade", props_count=5, siteswap_x="5c cascade -> 3 rounds 74{0}4{0} -> 5c cascade"),
                    Trick(name="2 rounds 97531 -> 3up 360 -> cascade", props_count=5),
                    Trick(name="sync doubles fountain", props_count=6),
                    Trick(name="6c any -> 1 round 8844 -> 6c any", props_count=6),
                    Trick(name="7c quads", props_count=7),
                ]
            ),
            competitors={
                1: CompetitorResult(name="Kevin Niitttyviita", tricks_accomplished=9),
                2: CompetitorResult(name="Luca Pferdmenges", tricks_accomplished=7),
                3: CompetitorResult(name="Matt Walmsley", tricks_accomplished=5),
            }
        ),
        RouteResult(
            route=Route(
                name="EJC 2026 - Rings Open",
                prop=Prop.Rings,
                duration_seconds=600,
                tricks=[
                    Trick(name="sync fountain -> 4up 180 in flatfronts -> sync fountain", props_count=4),
                    Trick(name="20c (6x,2x)*", props_count=4, comment="sprung cascade. entrance from sync: (6,4)"),
                    Trick(name="4 rounds 56662, finger-spin 2", props_count=5),
                    Trick(name="6 rounds 8444", props_count=5),
                    Trick(name="30c every 3'rd throw as flatfront", props_count=5, siteswap_x="10 rounds 5{F}55"),
                    Trick(name="cold start sync 6up 360 -> sync fountain", props_count=6),
                    Trick(name="6c any -> 1 round any with 1, behind the back 1 -> 6c any", props_count=6),
                    Trick(name="sync columns", props_count=6),
                    Trick(name="6c any -> 1 round b55555 -> any", props_count=6),
                    Trick(name="any -> pulldown", props_count=8),
                ]
            ),
            competitors={
                1: CompetitorResult(name="Kevin Niitttyviita", seconds=287),
            }
        ),
        RouteResult(
            route=Route(
                name="EJC 2026 - Balls U18",
                prop=Prop.Balls,
                duration_seconds=600,
                tricks=[
                    Trick(name="53 -> exactly 1 round 633 -> other sided 53", props_count=4),
                    Trick(name="16c (4,4) one sided overheads", props_count=4),
                    Trick(name="sync fountain -> 2up 180 -> 2up 360 -> sync fountain", props_count=4),
                    Trick(name="4 neck throws in a run", props_count=3),
                    Trick(name="blindfolded: 3c cascade -> 1 round 441 -> 3c cascade", props_count=3),
                    Trick(name="5c cascade -> 1 round 663, under the leg 3 -> cascade", props_count=5),
                    Trick(name="full slow spin while half shower", props_count=5),
                    Trick(name="full slow spin to the other direction while half shower to the other side", props_count=5),
                    Trick(name="20c sync fountain seated", props_count=6),
                    Trick(name="8c any -> 4up 360 -> collect", props_count=8),
                ]
            ),
            competitors={
                1: CompetitorResult(name="Komiken", seconds=186),
                2: CompetitorResult(name="Kevin Niitttyviita", seconds=235),
                3: CompetitorResult(name="Nino", tricks_accomplished=9),
            }
        ),
    ]
)
