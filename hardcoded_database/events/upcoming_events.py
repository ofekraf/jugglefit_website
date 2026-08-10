from pylib.classes.event import UpcomingEvent
from datetime import date

# Keep ordered by date
UPCOMING_EVENTS = [
    UpcomingEvent(
        name="Tohuwabohu",
        date=date(2026, 10, 2),
        location="Halle (Saale), Germany",
        url="https://nica.network/en/hullabaloo/",
        routes=[
            "Balls Open",
            "Clubs Open",
        ]
    ),
    UpcomingEvent(
        name="IJC 2027",
        date=date(2027, 4, 23),
        location="Israel",
        url="https://www.ijc.co.il/",
        routes=[
            "Balls Open",
            "Clubs Open",
            "Balls U18",
        ]
    ),
]
