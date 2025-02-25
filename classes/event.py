from dataclasses import dataclass
from typing import Dict, List
from classes.route import Route
from route_generator.exceptions import WinnerNotSetException

@dataclass(kw_only=True)
class CompetitorResult:
    name: str
    seconds: int
    
@dataclass(kw_only=True)
class RouteResult(Route):
    # dict[place] -> Competitor
    competitors: Dict[int, CompetitorResult]   
    
    def __post_init__(self):
        if 1 not in self.competitors:
            raise WinnerNotSetException()
    
@dataclass(kw_only=True)
class BaseEvent:
    # Make sure to include hosting event if exists
    name: str
    location: str
    
    # dd/mm/yyyy
    date: str

@dataclass(kw_only=True)
class PastEvent(BaseEvent):
    results: List[RouteResult]
    
    # Could be a full web URL or relative to web root
    image_url: str
    
@dataclass(kw_only=True)
class UpcomingEvent(BaseEvent):
    # URL to event\hosting event
    url: str
    routes: List[str]
    