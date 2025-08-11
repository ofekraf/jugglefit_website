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
]
