from .base_trick import Trick
from .tags import Tag

# @todo: Add TONS of trick

BALLS_TRICKS = [
    # Base Patterns
    Trick(name="20c cascade", props_count=5, difficulty=13, tags={Tag.BasePattern}),
    Trick(name="ANY", props_count=6, difficulty=24, tags={Tag.BasePattern}),
    Trick(name="7c cascade", props_count=7, difficulty=27, tags={Tag.BasePattern}),
    Trick(name="50c isolated cascade", props_count=5, difficulty=29, tags={Tag.BasePattern, Tag.Isolation}),
    
    # Spins
    Trick(name="3up 360 -> cascade", props_count=3, difficulty=10, tags={Tag.Spins, Tag.s360}),
    Trick(name="3up 360 -> cascade", props_count=5, difficulty=26, tags={Tag.Spins, Tag.s360}),
    Trick(name="5up 360 -> cascade", props_count=5, difficulty=33, tags={Tag.Spins, Tag.s360}),
    
    # Siteswaps
    Trick(name="24c 714", props_count=4, difficulty=22, tags={Tag.Siteswap}),
    Trick(name="cascade -> 5c 97531 ->cascade", props_count=5, difficulty=28, tags={Tag.Siteswap}),
    Trick(name="30c 744", props_count=5, difficulty=25, tags={Tag.Siteswap}),
    Trick(name="36c 645", props_count=5, difficulty=25, tags={Tag.Siteswap}),
    
    # Body throws
    Trick(name="backrosses", props_count=3, difficulty=15, tags={Tag.BodyThrows}),
    
    
]