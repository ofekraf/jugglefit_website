from pylib.classes.event import UpcomingEvent
from datetime import date

# Keep ordered by date
UPCOMING_EVENTS = [
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
