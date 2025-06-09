from py_lib.event import UpcomingEvent
from datetime import date

# Keep ordered by date
UPCOMING_EVENTS = [
    UpcomingEvent(
        name="European Juggling Convention 2025 (EJC)",
        date=date(2025, 8, 8),
        location="Arnhem, The Netherlands",
        url="https://ejc2025.org",
        routes=[
            "Balls Open",
            "Clubs Open",
            "Rings Open",
            "Balls U18",
            "Clubs U18",
            "Rings U18",
        ]
    ),
]
