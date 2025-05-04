from dataclasses import dataclass


@dataclass(kw_only=True)
class TeamMember:
    name: str
    residence: str
    image_url: str