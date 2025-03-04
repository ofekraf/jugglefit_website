from route_generator.tricks.base_trick import Trick
from route_generator.tricks.tags import Tag

# @todo: Add TONS of trick
# @todo - Tamuz, go over difficulties + assign difficulties where I didn't put them


CLUBS_TRICKS = [
    ########## BASE PATTERNS ##########
    
    ### 3 props base patterns ###
    Trick(name="20c reverse spin singles", props_count=3, difficulty=14, tags={Tag.SpinControl}),
    Trick(name="10c helicopters", props_count=3, difficulty=20, tags={Tag.SpinControl}),
    Trick(name="30c flats", props_count=3, difficulty=15, tags={Tag.SpinControl}),
    Trick(name="12c triples", props_count=3, difficulty=15, tags={Tag.SpinControl}),
    Trick(name="10c slapbacks", props_count=3, difficulty=18, tags={Tag.SpinControl}),
    Trick(name="10c singles -> 10c doubles  -> 10c triples", props_count=3, difficulty=18, tags={Tag.SpinControl, Tag.BasePattern}),

    ### 4 props base patterns ###
    Trick(name="sync fountain -> async fountain", difficulty=20, props_count=4, tags={Tag.BasePattern}, comment="transition: (5x,4)"), #todo - difficulty
    Trick(name="sync fountain -> 2up 360 -> sync fountain" , difficulty=22, props_count=4, tags={Tag.Spin}),   #todo - difficulty
    Trick(name="20c flats", difficulty=30, props_count=4, tags={Tag.SpinControl}),

    ### 5 props base patterns ###
    Trick(name="50c isolated cascade", props_count=5, difficulty=37, tags={Tag.BasePattern}),
    Trick(name="10c singles", props_count=5, difficulty=28, tags={Tag.SpinControl, Tag.BasePattern}), # todo
    Trick(name="10c triples", props_count=5, difficulty=30, tags={Tag.SpinControl, Tag.BasePattern}), # todo

    ### 6 props base patterns ###
    Trick(name="fountain", props_count=6, difficulty=55, tags={Tag.BasePattern}),
    Trick(name="6c sync fountain", props_count=6, difficulty=46, tags={Tag.BasePattern}),
    
    ### 7 props base patterns ###
    Trick(name="7c cascade", props_count=7, difficulty=60, tags={Tag.BasePattern}), # todo - - difficulty
    Trick(name="cascade", props_count=7, difficulty=73, tags={Tag.BasePattern}), # todo - - difficulty
        
    ########## SPINS ##########
    
    ### 3 props spins ###
    # base 360

    
    # base 720
    
    # multi-stage
    
    # connections

    ### 4 props spins ###
    # base 360
    
    # base 720
    
    # multi-stage
    
    # connections
    
    ### 5 props spins ###
    # base 360
    
    # base 720
    
    # multi-spin
    
    # Connections
    
    ### 6 props spins ###
    # base 360
    
    # base 720
    
    # multi-spin
    
    # connections
    
    ### 7 props spins ###
    # base 360
    
    # base 720
    
    # multi-spin
    
    # connections
    
    ########## SITESWAPS ##########
    
    ### 3 props siteswaps ###
    # period 3
    Trick(name="24c 531", props_count=3, difficulty=13, tags={Tag.Siteswap}),
    Trick(name="36c 801", props_count=3, difficulty=42, tags={Tag.Siteswap}, comment="Entrance: 46"),
    
    # period 5
    Trick(name="20c 45123", props_count=3, difficulty=16, tags={Tag.Siteswap}),
    Trick(name="30c 44133", props_count=3, difficulty=14, tags={Tag.Siteswap}),

    ### 4 props siteswaps ###
    # period 3
    Trick(name="18c 552", props_count=4, difficulty=22, tags={Tag.Siteswap}),
    Trick(name="18c 633", props_count=4, difficulty=27, tags={Tag.Siteswap}),
    Trick(name="18c 741", props_count=4, difficulty=28, tags={Tag.Siteswap}, comment="entrance: 5"),
    Trick(name="18c 534, 5 as singles, 3 as doubles", props_count=4, difficulty=45, tags={Tag.Siteswap, Tag.SpinControl}),

    # period 5
    Trick(name="20c 55550", props_count=4, difficulty=25, tags={Tag.Siteswap}),
    Trick(name="20c 56450", props_count=4, difficulty=28, tags={Tag.Siteswap}),

    ### 5 props siteswaps ###
    # period 3
    Trick(name="30c 771", props_count=5, difficulty=45, tags={Tag.Siteswap}, comment="entrance: 75"),
    Trick(name="30c 672", props_count=5, difficulty=47, tags={Tag.Siteswap}, comment="entrance 6"),

    # period 5
    Trick(name="10c 94444", props_count=5, difficulty=34, tags={Tag.Siteswap}),
    Trick(name="20c 94633", props_count=5, difficulty=52, tags={Tag.Siteswap}),

    ### 6 props siteswaps ###
    # period 3
    Trick(name="6c 756", props_count=6, difficulty=46, tags={Tag.BasePattern}),
    Trick(name="6c fountain -> 6c 864 -> 6c fountain", props_count=6, difficulty=57, tags={Tag.Siteswap}),

    # period 5
    Trick(name="10c 77781", props_count=6, difficulty=82, tags={Tag.Siteswap}),

    
    ### 7 props siteswaps ###
    
    
    ########## BODY THROWS ##########
    
    ### 3 props body throws ###
                                                # ~ like 24c 53534 balls
    Trick(name="20c backrosses", props_count=3, difficulty=20, tags={Tag.BodyThrows, Tag.BasePattern}),  # ~ like 24c 53534 balls
    Trick(name="6c under the leg throws", props_count=3, difficulty=16, tags={Tag.BodyThrows}),
    Trick(name="6c lazies", props_count=3, difficulty=14, tags={Tag.BodyThrows}),
    Trick(name="24c 423 with 4's as shoulder throws", difficulty=23, props_count=3, tags={Tag.BodyThrows, Tag.Siteswap}), 
    Trick(name="12c 423 with 4's as shoulder throws, caught as lazies", props_count=3, difficulty=25, tags={Tag.BodyThrows, Tag.Siteswap}), 
    Trick(name="6c lazies -> 6c backrosses", props_count=3, difficulty=20, tags={Tag.BodyThrows}),

    ### 4 props body throws ###
    Trick(name="overheads", props_count=4, difficulty=32, tags={Tag.BodyThrows}),
    Trick(name="534, 5 as backrosses", props_count=4, difficulty=35, tags={Tag.BodyThrows}),

    ### 5 props body throws ###
    
    ### 6 props body throws ###
    
    ### 7 props body throws ###
    
]