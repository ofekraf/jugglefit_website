from pylib.classes.event import UpcomingEvent
from datetime import date

# Keep ordered by date
UPCOMING_EVENTS = [
    UpcomingEvent(
        name="Melbourne Juggling Convention 2026",
        date=date(2026, 9, 26),
        location="Melbourne, Australia",
        url="https://www.melbournejugglingconvention.com.au/",
        routes=[
            "Balls - Open",
            "Clubs - Open",
        ]
    ),
    UpcomingEvent(
        name="Halle 2026 (Tohuwabohu)",
        date=date(2026, 10, 2),
        location="Halle (Saale), Germany",
        url="https://nica.network/en/hullabaloo/",
        routes=[
            "Balls Open",
            "Clubs Open",
        ]
    ),
    UpcomingEvent(
        name="Muenchen Con XXL 2026",
        date=date(2026, 11, 4),
        location="Munich, Germany",
        url="https://muenchen-con.de/",
        routes=[
            "Balls - Open",
            "Clubs - Open",
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
    UpcomingEvent(
        name="EJC 2027",
        date=date(2027, 8, 5),
        location="Azores, Portugal",
        url="https://eja.net/news/%F0%9F%8C%8D-ejc-2027-awarded-to-the-azores/",
        routes=[
            "Balls - Open",
            "Clubs - Open",
            "Balls - U18",
        ]
    ),
]
