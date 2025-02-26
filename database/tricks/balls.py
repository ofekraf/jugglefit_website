# @todo: Add TONS of trick

from route_generator.tricks.base_trick import Trick
from route_generator.tricks.tags import Tag


BALLS_TRICKS = [
    
    ########## BASE PATTERNS ##########
    # 5 props base patterns
    Trick(name="20c cascade", props_count=5, difficulty=13, tags={Tag.BasePattern}),
    Trick(name="50c isolated cascade", props_count=5, difficulty=29, tags={Tag.BasePattern}),
    
    # 6 props base patterns
    Trick(name="ANY", props_count=6, difficulty=24, tags={Tag.BasePattern}),
    
    # 7 props base patterns
    Trick(name="7c cascade", props_count=7, difficulty=27, tags={Tag.BasePattern}),
    Trick(name="cascade", props_count=7, difficulty=36, tags={Tag.BasePattern}),
    Trick(name="7c cascade on the knees", props_count=7, difficulty=34, tags={Tag.BasePattern}),
    
    # 8 props base patterns
    Trick(name="16c async ANY", props_count=8, difficulty=68, tags={Tag.BasePattern}),
    
    ########## SPINS ##########
    # 3 props spins
    Trick(name="3up 360 -> cascade", props_count=3, difficulty=10, tags={Tag.Spin}),
    Trick(name="75300 3up 360 -> cascade", props_count=3, difficulty=12, tags={Tag.Spin}),
    Trick(name="9440022 3up 2-stage -> cascade", props_count=3, difficulty=24, tags={Tag.MultiSpin}),
    Trick(name="3up 720 -> cascade", props_count=3, difficulty=26, tags={Tag.MultiSpin}),
    
    # 4 props spins
    Trick(name="4up 360 -> async fountain", props_count=4, difficulty=22, tags={Tag.Spin}),
    Trick(name="777300 4up 360 -> async fountain", props_count=4, difficulty=29, tags={Tag.Spin}),
    
    # 5 props spins
    Trick(name="3up 360 -> cascade", props_count=5, difficulty=26, tags={Tag.Spin}),
    Trick(name="97522 3up 360 -> cascade", props_count=5, difficulty=29, tags={Tag.Spin}),
    Trick(name="5up 360 -> cascade", props_count=5, difficulty=33, tags={Tag.Spin}),
    Trick(name="aa55500 5up 360 -> cascade", props_count=5, difficulty=47, tags={Tag.Spin}),
    Trick(name="b666600 5up 360 -> cascade", props_count=5, difficulty=38, tags={Tag.Spin}),
    Trick(name="3up 720 -> cascade", props_count=5, difficulty=41, tags={Tag.MultiSpin}),
    
    # 6 props spins
    Trick(name="aa6622 4up 360 -> cascade", props_count=6, difficulty=66, tags={Tag.Spin}),
    
    # 7 props spins
    Trick(name="5up 360 -> cascade", props_count=7, difficulty=68, tags={Tag.Spin}),
    
    ########## SITESWAPS ##########
    # 3 props siteswaps
    Trick(name="36c 801", props_count=3, difficulty=23, tags={Tag.Siteswap}, comment="[entrance: 46]"),
    
    # 4 props siteswaps
    Trick(name="24c 714", props_count=4, difficulty=22, tags={Tag.Siteswap}),
    Trick(name="30c 63551", props_count=4, difficulty=22, tags={Tag.Siteswap}),
    Trick(name="60c 741", props_count=4, difficulty=22, tags={Tag.Siteswap}),
    
    # 5 props siteswaps
    Trick(name="cascade -> 5c 97531 -> cascade", props_count=5, difficulty=28, tags={Tag.Siteswap}),
    Trick(name="30c 744", props_count=5, difficulty=25, tags={Tag.Siteswap}),
    Trick(name="36c 645", props_count=5, difficulty=25, tags={Tag.Siteswap}),
    
    # 6 props siteswaps
    Trick(name="30c 77335", props_count=5, difficulty=46, tags={Tag.Siteswap}),
    Trick(name="30c 78451", props_count=5, difficulty=47, tags={Tag.Siteswap}),
    Trick(name="30c 74464", props_count=5, difficulty=34, tags={Tag.Siteswap}),
    
    # 7 props siteswaps
    Trick(name="cascade -> 966", props_count=7, difficulty=58, tags={Tag.Siteswap}),
    Trick(name="30c 96636", props_count=6, difficulty=61, tags={Tag.Siteswap}),
    
    ########## BODY THROWS ##########
    # 3 props body throws
    Trick(name="backrosses", props_count=3, difficulty=15, tags={Tag.BodyThrows}),
    Trick(name="10c neck throws", props_count=3, difficulty=24, tags={Tag.BodyThrows}),
    
    # 4 props body throws
    Trick(name="reverse sholders async fountain", props_count=4, difficulty=42, tags={Tag.BodyThrows}),
    
    # 5 props body throws
    Trick(name="5c 94444 with 4's as sholders", props_count=5, difficulty=43, tags={Tag.BodyThrows, Tag.Siteswap}),
    
    # 6 props body throws
    Trick(name="756 -> 6c 756 with 5's as backrosses -> 756", props_count=6, difficulty=66, tags={Tag.BodyThrows, Tag.Siteswap}),
    
    # 7 props body throws
    Trick(name="cascade -> 7c backrosses", props_count=7, difficulty=74, tags={Tag.BodyThrows}),
]