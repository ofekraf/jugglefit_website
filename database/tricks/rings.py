from route_generator.tricks.base_trick import Trick
from route_generator.tricks.tags import Tag

# @todo: Difficulties are wrong
# @todo: Add TONS of trick

RINGS_TRICKS = [
    # Base Patterns
    Trick(name="20c cascade", props_count=5, difficulty=20, tags={Tag.BasePattern}),
    Trick(name="ANY", props_count=6, difficulty=50, tags={Tag.BasePattern}),
    Trick(name="7c cascade", props_count=7, difficulty=55, tags={Tag.BasePattern}),
    
    # Spin Control
    Trick(name="20c isolated singles cascade", props_count=5, difficulty=33, tags={Tag.BasePattern, Tag.SpinControl}),
    
    # Spins
    Trick(name="1up 360 -> cascade", props_count=3, difficulty=3, tags={Tag.Spin}),
    Trick(name="3up 360 -> cascade", props_count=3, difficulty=15, tags={Tag.Spin}),
    Trick(name="3up 360 -> cascade", props_count=5, difficulty=35, tags={Tag.Spin}),
    
    # Siteswaps
    Trick(name="cascade -> 3c 531 ->cascade", props_count=3, difficulty=3, tags={Tag.Siteswap}),
    Trick(name="cascade -> 441 ->cascade", props_count=3, difficulty=5, tags={Tag.Siteswap}),
    Trick(name="12c 744", props_count=5, difficulty=25, tags={Tag.Siteswap}),
    Trick(name="12c 645", props_count=5, difficulty=25, tags={Tag.Siteswap}),
    
    # Body throws
    Trick(name="backrosses", props_count=3, difficulty=15, tags={Tag.BodyThrows}),
    
]