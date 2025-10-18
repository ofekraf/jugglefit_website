from pylib.classes.event import UpcomingEvent
from datetime import date

# Keep ordered by date
UPCOMING_EVENTS = [
    UpcomingEvent(
        name="Israeli Juggling Convention 2026 (IJC)",
        date=date(2026, 4, 5),
        location="Gan Hashlosha, Israel",
        url="https://www.ijc.co.il/",
        routes=[
            "Balls Open",
            "Clubs Open",
            "Balls U18",
        ]
    ),
    UpcomingEvent(
        name="EJC 2025",
        date=date(2026, 8, 4),
        location="Ptuj, Slovenia",
        url="https://eja.net/event/ejc2026/",
        routes=[
            "Balls Open",
            "Clubs Open",
            "Rings Open",
            "Balls U18",
        ]
    ),
]
