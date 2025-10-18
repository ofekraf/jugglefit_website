

from hardcoded_database.events.past_events.Tubingen2025 import Tubingen2025
from hardcoded_database.events.past_events.Y2025.EJC2025 import EJC2025
from hardcoded_database.events.past_events.Y2025.IJC2025 import IJC2025
from hardcoded_database.events.past_events.Y2025.NJF2025 import NJF2025
from hardcoded_database.events.past_events.Y2025.sapir2025 import Sapir2025

# Keep ordered by date
FRONT_PAGE_PAST_EVENTS = [
    Sapir2025,
    IJC2025,
    NJF2025,
    EJC2025,
    Tubingen2025
]

# Move here events to remove it from the website's front page
# Keep ordered by date
NON_FRONT_PAGE_PAST_EVENTS = [
    
]

# @TODO: order by date from oldest to newest
ALL_PAST_EVENTS = FRONT_PAGE_PAST_EVENTS + NON_FRONT_PAGE_PAST_EVENTS
ALL_PAST_EVENTS.sort(key=lambda x: x.date)