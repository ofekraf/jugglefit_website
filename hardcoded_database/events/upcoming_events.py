from pylib.classes.event import UpcomingEvent
from datetime import date

# Keep ordered by date
UPCOMING_EVENTS = [
    UpcomingEvent(
        name="EJC 2026",
        date=date(2026, 8, 6),
        location="Ptuj, Slovenia",
        url="https://eja.net/event/ejc2026/",
        routes=[
            "Balls Open",
            "Clubs Open",
            "Rings Open",
            "Balls U18",
        ]
    ),
    UpcomingEvent(
        name="Tohuwabohu 2026",
        date=date(2026, 10, 2),
        location="Halle, Germany",
        url="https://nica.network/en/hullabaloo/",
        routes=[
            "Balls Open",
            "Clubs Open",
        ]
    ),
]
