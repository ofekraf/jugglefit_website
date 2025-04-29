from dataclasses import dataclass


@dataclass(kw_only=True)
class Affiliate:
    name: str
    residence: str
    image_url: str