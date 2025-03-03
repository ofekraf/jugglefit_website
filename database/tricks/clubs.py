from route_generator.tricks.base_trick import Trick
from route_generator.tricks.tags import Tag

# @todo: Add TONS of trick
# @todo - Tamuz, go over difficulties + assign difficulties where I didn't put them


CLUBS_TRICKS = [
    ########## BASE PATTERNS ##########
    
    ### 3 props base patterns ###

                                                    # ~ like 50c isolated balls
    Trick(name="20c reverse spin", props_count=3, difficulty=29, tags={Tag.SpinControl}),
    Trick(name="10c helicopters", props_count=3,  tags={Tag.SpinControl}), # todo - difficulty
    Trick(name="30c flats", props_count=3, tags={Tag.SpinControl}), # todo - difficulty
    Trick(name="10c slapbacks", props_count=3, tags={Tag.BasePattern}), # todo - difficulty

                                                                            # ~ like 50c isolated balls
    Trick(name="10c singles -> 10c doubles  -> 10c triples ", props_count=3, difficulty=28, tags={Tag.SpinControl, Tag.BasePattern}),

    ### 4 props base patterns ###

    Trick(name="sync fountain -> sync fountain ", props_count=4, tags={Tag.BasePattern}), #todo - difficulty
    Trick(name="sync fountain -> 2up 360 -> 4up 360 -> sync fountain ", props_count=4, tags={Tag.Spin}),   #todo - difficulty
    Trick(name="20c flats", props_count=4, tags={Tag.SpinControl}), # todo - difficulty

    ### 5 props base patterns ###

                                                        #~4up 360 -> 12c 534 in overheads
    Trick(name="50c isolated cascade", props_count=5, difficulty=39, tags={Tag.BasePattern}),
    Trick(name="10c singles", props_count=5, tags={Tag.SpinControl, Tag.BasePattern}), # todo
    Trick(name="10c triples", props_count=5, tags={Tag.SpinControl, Tag.BasePattern}), # todo

    ### 6 props base patterns ###
    Trick(name="ANY", props_count=6, tags={Tag.BasePattern}), # todo - difficulty
    
    ### 7 props base patterns ###
    Trick(name="7c cascade", props_count=7, tags={Tag.BasePattern}), # todo - - difficulty
    Trick(name="cascade", props_count=7, tags={Tag.BasePattern}), # todo - - difficulty
        
    ########## SPINS ##########
    
    ### 3 props spins ###
    # base 360

    
    # base 720
    
    # multi-stage
    
    # connections
    Trick(name="6c albert's -> 6c trebla ", props_count=3, tags={Tag.BodyThrows}),  # todo - difficulty
    Trick(name="6c lazies -> 6c backrosses", props_count=3, tags={Tag.BodyThrows}),  # todo - difficulty
    Trick(name="6c hellicopters -> 6c reverse helicopters", props_count=3, tags={Tag.BodyThrows}),  # todo - difficulty

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
    Trick(name="24c 531", props_count=3, tags={Tag.Siteswap}), # todo - difficulty
    Trick(name="36c 801", props_count=3, tags={Tag.Siteswap}, comment="Entrance: 46"), # todo - difficulty
    
    # period 5
    Trick(name="20c 45123", props_count=3, tags={Tag.Siteswap}), # todo - difficulty
    Trick(name="30c 44133", props_count=3, tags={Tag.Siteswap}), # todo - difficulty
    Trick(name="30c 53142", props_count=3, tags={Tag.Siteswap}), # todo - difficulty

    ### 4 props siteswaps ###
    # period 3
    Trick(name="16c 552", props_count=4, tags={Tag.Siteswap}), # todo - difficulty
    Trick(name="16c 804", props_count=4, tags={Tag.Siteswap}), # todo - difficulty
    Trick(name="16c a11", props_count=4, tags={Tag.Siteswap}), # todo - difficulty
    Trick(name="16c 534, 5 as singles, 3 as doubles", props_count=4, tags={Tag.Siteswap, Tag.SpinControl}), # todo - difficulty

    # period 5
    Trick(name="24c 55550", props_count=4, tags={Tag.Siteswap}), # todo - difficulty
    Trick(name="24c 64505", props_count=4, tags={Tag.Siteswap}), # todo - difficulty + do both 64550 and 64550 work?

    ### 5 props siteswaps ###
    # period 3
    Trick(name="30c 771", props_count=5, tags={Tag.Siteswap}, comment="entrance: 75"), # todo - difficulty
    Trick(name="30c 726", props_count=5, tags={Tag.Siteswap}, comment="entrance ?"), # todo - difficulty + entrance?

    # period 5
    Trick(name="20c 94444", props_count=5, tags={Tag.Siteswap}), # todo - difficulty
    Trick(name="20c 94633", props_count=5, tags={Tag.Siteswap}), # todo - difficulty

    ### 6 props siteswaps ###
    # period 3
    Trick(name="36c 756", props_count=6, tags={Tag.Siteswap}), # todo - difficulty

    # period 5
    Trick(name="30c 78636", props_count=6, tags={Tag.Siteswap}), # todo - difficulty

    
    ### 7 props siteswaps ###
    
    
    ########## BODY THROWS ##########
    
    ### 3 props body throws ###
                                                # ~ like 24c 53534 balls
    Trick(name="20c backrosses", props_count=3, difficulty=20, tags={Tag.BodyThrows, Tag.BasePattern}),  # ~ like 24c 53534 balls
    Trick(name="6c under the leg throws", props_count=3, tags={Tag.BodyThrows}),  # todo - difficulty
    Trick(name="6c lazies", props_count=3, tags={Tag.BodyThrows}),  # todo - difficulty
    Trick(name="24c 423 with 4's as shoulder throws", props_count=3, tags={Tag.BodyThrows, Tag.Siteswap}),   # todo - difficulty
    Trick(name="12c 423 with 4's as shoulder throws, caught as lazies", props_count=3, tags={Tag.BodyThrows, Tag.Siteswap}),   # todo - difficulty
    Trick(name="10c neck throws", props_count=3, tags={Tag.BodyThrows}),  # todo - difficulty

    ### 4 props body throws ###
    Trick(name="overheads", props_count=4, tags={Tag.BodyThrows}),  # todo - difficulty
    Trick(name="534, 5 as backrosses", props_count=4, tags={Tag.BodyThrows}),  # todo - difficulty

    ### 5 props body throws ###
    
    ### 6 props body throws ###
    
    ### 7 props body throws ###
    
]