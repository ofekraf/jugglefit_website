from pylib.classes.event import UpcomingEvent
from datetime import date

# Keep ordered by date
UPCOMING_EVENTS = [
    UpcomingEvent(
        name="Enklawa Festival 2026",
        # Provisional - update once the official competition date is announced
        date=date(2026, 8, 20),
        location="Elbląg, Poland",
        url="https://festiwalenklawa.pl/en",
        routes=[
            "Balls Open",
            "Clubs Open",
        ]
    ),
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
