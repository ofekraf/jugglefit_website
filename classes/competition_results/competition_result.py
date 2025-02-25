from dataclasses import dataclass
from typing import Dict
from classes.route import Route

@dataclass(kw_only=True)
class RouteCompetitor:
    name: str
    result_seconds: int

@dataclass(kw_only=True)
class CompetitionResult:
    route: Route
    winners: Dict[int, RouteCompetitor]