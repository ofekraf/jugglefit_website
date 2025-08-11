from pylib.classes.event import UpcomingEvent
from datetime import date

# Keep ordered by date
UPCOMING_EVENTS = [
    UpcomingEvent(
        name="BürokratCon Tübingen 2025",
        date=date(2025, 10, 4),
        location="Tübingen, Germany",
        url="https://jonglaria.org/conventions/",
        routes=[
            "Balls Open",
            "Clubs Open",
            "Balls U18",
        ]
    ),
]
