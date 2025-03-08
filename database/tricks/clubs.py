from route_generator.tricks.base_trick import Trick
from route_generator.tricks.tags import Tag

# @todo: Add TONS of trick
CLUBS_TRICKS = [
    ########## BASE PATTERNS ##########
    
    ### 3 props base patterns ###

    ### 4 props base patterns ###
    Trick(name="sync fountain -> async fountain", difficulty=20, props_count=4, tags={Tag.BasePattern}, comment="transition: (5x,4)"), #todo - difficulty
    Trick(name="sync fountain -> 2up 360 -> sync fountain" , difficulty=22, props_count=4, tags={Tag.Spin}),   #todo - difficulty
    Trick(name="20c flats", difficulty=30, props_count=4, tags={Tag.SpinControl}),

    ### 5 props base patterns ###
    Trick(name="50c isolated cascade", props_count=5, difficulty=37, tags={Tag.BasePattern}),

    ### 6 props base patterns ###
    Trick(name="fountain", props_count=6, difficulty=55, tags={Tag.BasePattern}),
    Trick(name="6c sync fountain", props_count=6, difficulty=46, tags={Tag.BasePattern}),
    
    ### 7 props base patterns ###
    Trick(name="7c cascade", props_count=7, difficulty=54, tags={Tag.BasePattern}),
    Trick(name="cascade", props_count=7, difficulty=70, tags={Tag.BasePattern}),
        
    ########## SPINS ##########
    
    ### 3 props spins ###
    # base 360
    Trick(name="cascade -> 3up 360 -> cascade", props_count=3, difficulty=20, tags={Tag.Spin}),
    Trick(name="531 -> 75300 3up 360 -> cascade", props_count=3, difficulty=27, tags={Tag.Spin}),
    Trick(name="441 -> 66300 3up 360 -> 441", props_count=3, difficulty=29, tags={Tag.Spin}),
    
    # base 720
    Trick(name="cascade -> 1up 720 -> flats", props_count=3, difficulty=28, tags={Tag.MultiSpin}),
    
    # multi-stage
    Trick(name="9440022 3up 2-stage -> cascade", props_count=3, difficulty=34, tags={Tag.MultiSpin}),
    
    # connections
    Trick(name="backrosses -> 3up 360 in backrosses -> backrosses", props_count=3, difficulty=42, tags={Tag.MultiSpin}),
    Trick(name="3up 360 -> 1up 360 -> 3up 360", props_count=3, difficulty=34, tags={Tag.Spin}),

    ### 4 props spins ###
    # base 360
    Trick(name="sync fountain -> (8,8)(4,4)(0,0) 4up 360 -> sync fountain", props_count=4, difficulty=36, tags={Tag.Spin}),
    Trick(name="async fountain -> 955500 4up 360 -> async fountain", props_count=4, difficulty=38, tags={Tag.Spin}),
    
    # base 720
    
    # multi-stage
    Trick(name="async fountain -> 6822622 2up 2-stage -> async fountain", props_count=4, difficulty=35, tags={Tag.MultiSpin}),
    
    # connections
    
    ### 5 props spins ###
    # base 360
    Trick(name="cascade -> 97522 3up 360 -> cascade", props_count=5, difficulty=40, tags={Tag.Spin}),
    
    # base 720
    
    # multi-spin
    Trick(name="cascade -> b66227722 3up 2-stage -> cascade", props_count=5, difficulty=52, tags={Tag.MultiSpin}),
    
    # Connections
    Trick(name="6c 663 -> 88522 3up 360 -> 6c 663", props_count=5, difficulty=50, tags={Tag.Spin, Tag.Siteswap}),
    Trick(name="744 -> 96622 3up 360 -> singles cascade", props_count=5, difficulty=46, tags={Tag.Spin, Tag.Siteswap, Tag.SpinControl}),
    
    ### 6 props spins ###
    # base 360
    Trick(name="6c async fountain -> 4up 360 -> ANY", props_count=6, difficulty=75, tags={Tag.Spin}),
    
    # base 720
    
    # multi-spin
    
    # connections
    
    ### 7 props spins ###
    # base 360
    
    # base 720
    Trick(name="7c cascade -> 5up 720 -> 7c cascade", props_count=7, difficulty=100, tags={Tag.MultiSpin}),
    
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
    
    # other period

    ### 4 props siteswaps ###
    # period 3
    Trick(name="18c 552", props_count=4, difficulty=22, tags={Tag.Siteswap}),
    Trick(name="18c 633", props_count=4, difficulty=27, tags={Tag.Siteswap}),
    Trick(name="18c 741", props_count=4, difficulty=28, tags={Tag.Siteswap}, comment="entrance: 5"),
    Trick(name="18c 534, single 5, double 3", props_count=4, difficulty=45, tags={Tag.Siteswap, Tag.SpinControl}),

    # period 5
    Trick(name="20c 55550", props_count=4, difficulty=25, tags={Tag.Siteswap}),
    Trick(name="20c 56450", props_count=4, difficulty=28, tags={Tag.Siteswap}),
    
    # other period

    ### 5 props siteswaps ###
    # period 3
    Trick(name="30c 771", props_count=5, difficulty=45, tags={Tag.Siteswap}, comment="entrance: 75"),
    Trick(name="30c 672", props_count=5, difficulty=47, tags={Tag.Siteswap}, comment="entrance 6"),
    Trick(name="30c 744 isolated", props_count=5, difficulty=42, tags={Tag.Siteswap}),

    # period 5
    Trick(name="10c 94444", props_count=5, difficulty=34, tags={Tag.Siteswap}),
    Trick(name="20c 94633", props_count=5, difficulty=52, tags={Tag.Siteswap}),
    Trick(name="cascade -> 10c 77335 -> cascade", props_count=5, difficulty=40, tags={Tag.Siteswap}),
    Trick(name="cascade -> 10c 74464 -> cascade", props_count=5, difficulty=37, tags={Tag.Siteswap}),
    Trick(name="30c 84445", props_count=5, difficulty=47, tags={Tag.Siteswap}),
    
    # other period

    ### 6 props siteswaps ###
    # period 3
    Trick(name="6c 756", props_count=6, difficulty=46, tags={Tag.BasePattern}),
    Trick(name="6c fountain -> 6c 864 -> 6c fountain", props_count=6, difficulty=57, tags={Tag.Siteswap}),

    # period 5
    Trick(name="10c 77781", props_count=6, difficulty=82, tags={Tag.Siteswap}),

    # other period
    
    ### 7 props siteswaps ###
    # period 3
    
    # period 5
    
    # other period
    
    
    ########## BODY THROWS ##########
    
    ### 3 props body throws ###
    Trick(name="20c backrosses", props_count=3, difficulty=20, tags={Tag.BodyThrows, Tag.BasePattern}),
    Trick(name="6c under the leg throws", props_count=3, difficulty=16, tags={Tag.BodyThrows}),
    Trick(name="6c lazies", props_count=3, difficulty=14, tags={Tag.BodyThrows}),
    Trick(name="24c 423 with shoulder throw 4", difficulty=23, props_count=3, tags={Tag.BodyThrows}), 
    Trick(name="12c 423 with shoulder throw lazy 4", props_count=3, difficulty=25, tags={Tag.BodyThrows}), 
    Trick(name="6c lazies -> 6c backrosses", props_count=3, difficulty=20, tags={Tag.BodyThrows}),
    Trick(name="4c bacrosses singles -> 4c backrosses doubles -> 4c backrosses triples ", props_count=3, difficulty=22, tags={Tag.BodyThrows}),

    ### 4 props body throws ###
    Trick(name="overheads", props_count=4, difficulty=32, tags={Tag.BodyThrows}),
    Trick(name="534 with backross 5", props_count=4, difficulty=35, tags={Tag.BodyThrows}),
    Trick(name="552 -> 6c 552 with backrosses 5's -> 552", props_count=4, difficulty=37, tags={Tag.BodyThrows}),

    ### 5 props body throws ###
    Trick(name="5c cascade -> 4c 7733 with backrosses 3's -> cascade", props_count=5, difficulty=55, tags={Tag.BodyThrows, Tag.Siteswap}),
    
    ### 6 props body throws ###
    Trick(name="6c ANY -> 4c 9555 with backross 5's -> 6c ANY", props_count=6, difficulty=73, tags={Tag.BodyThrows, Tag.Siteswap}),
    
    ### 7 props body throws ###
    
    
    ########## SPIN CONTROL ##########
    
    ### 3 props spin control ###
    Trick(name="20c reverse spin singles", props_count=3, difficulty=14, tags={Tag.SpinControl}),
    Trick(name="10c helicopters", props_count=3, difficulty=20, tags={Tag.SpinControl}),
    Trick(name="30c flats", props_count=3, difficulty=15, tags={Tag.SpinControl, Tag.BasePattern}),
    Trick(name="12c triples", props_count=3, difficulty=15, tags={Tag.SpinControl, Tag.BasePattern}),
    Trick(name="10c slapbacks", props_count=3, difficulty=18, tags={Tag.SpinControl}),
    Trick(name="10c singles -> 10c doubles  -> 10c triples", props_count=3, difficulty=18, tags={Tag.SpinControl, Tag.BasePattern}),
    Trick(name="flat flatfronts -> 3c 441 double flatfronts 4's -> single flatfronts", props_count=3, difficulty=25, tags={Tag.SpinControl}),
    
    ### 4 props spin control ###
    Trick(name="18c 534 singles", props_count=4, difficulty=26, tags={Tag.SpinControl, Tag.Siteswap}),
    Trick(name="18c 633 singles", props_count=4, difficulty=40, tags={Tag.SpinControl, Tag.Siteswap}),
    Trick(name="534 with flat 4", props_count=4, difficulty=27, tags={Tag.SpinControl, Tag.Siteswap}),
    
    ### 5 props spin control ###
    Trick(name="10c singles", props_count=5, difficulty=28, tags={Tag.SpinControl, Tag.BasePattern}),
    Trick(name="10c triples", props_count=5, difficulty=30, tags={Tag.SpinControl, Tag.BasePattern}),
    Trick(name="6c triples -> 6c singles", props_count=5, difficulty=30, tags={Tag.SpinControl}),
    Trick(name="cascade -> 12c 744 with flat 4's", props_count=5, difficulty=48, tags={Tag.SpinControl}),
    
    ### 6 props spin control ###
    Trick(name="6c singles", props_count=5, difficulty=51, tags={Tag.SpinControl}),
    
    ### 7 props spin control ###
    
    
]