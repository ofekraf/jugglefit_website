from pylib.classes.trick import Trick
from pylib.classes.tag import Tag

# @todo: Add TONS of trick
BALLS_TRICKS = [

    ########## BASE PATTERNS ##########
    
    ### 3 props base patterns ###
    
    ### 4 props base patterns ###
    Trick(name="20c sync fountain -> 20c async fountain", props_count=4, difficulty=10, tags={Tag.SyncBasePattern, Tag.AsyncBasePattern}, comment="Transition: (5x,4)"),
    
    ### 5 props base patterns ###
    Trick(name="20c cascade", props_count=5, difficulty=13, tags={Tag.AsyncBasePattern}),
    Trick(name="50c isolated cascade", props_count=5, difficulty=29, tags={Tag.AsyncBasePattern, Tag.Isolated}),
    Trick(name="30c reverse cascade", props_count=5, difficulty=37, tags={Tag.AsyncBasePattern}),
    
    ### 6 props base patterns ###
    Trick(name="ANY", props_count=6, difficulty=24, tags={Tag.BasePattern}),
    Trick(name="async fountain", props_count=6, difficulty=29, tags={Tag.AsyncBasePattern}),
    Trick(name="20c async fountain", props_count=6, difficulty=30, tags={Tag.AsyncBasePattern}),
    Trick(name="isolated sync fountain", props_count=6, difficulty=32, tags={Tag.SyncBasePattern, Tag.Isolated}),
    Trick(name="sync fountain -> async fountain", props_count=6, difficulty=34, tags={Tag.SyncBasePattern, Tag.AsyncBasePattern}, comment="transition: (7x,6)(7x,6)"),
    Trick(name="async fountain -> sync fountain", props_count=6, difficulty=34, tags={Tag.AsyncBasePattern, Tag.SyncBasePattern}, comment="transition: 7x67x6"),
    Trick(name="ANY on the knees", props_count=6, difficulty=28, tags={Tag.BasePattern, Tag.OnTheKnees}),
    
    ### 7 props base patterns ###
    Trick(name="7c cascade", props_count=7, difficulty=26, tags={Tag.AsyncBasePattern}),
    Trick(name="cascade", props_count=7, difficulty=34, tags={Tag.AsyncBasePattern}),
    Trick(name="7c cascade on the knees", props_count=7, difficulty=32, tags={Tag.AsyncBasePattern, Tag.OnTheKnees}),
    Trick(name="isolated cascade", props_count=7, difficulty=35, tags={Tag.AsyncBasePattern, Tag.Isolated}),
    
    ### 8 props base patterns ###
    Trick(name="8c sync fountain", props_count=8, difficulty=43, tags={Tag.SyncBasePattern}),
    Trick(name="8c async fountain", props_count=8, difficulty=45, tags={Tag.AsyncBasePattern}),
    Trick(name="16c async ANY", props_count=8, difficulty=68, tags={Tag.AsyncBasePattern}),
    
    
    ### 9 props base patterns ###
    Trick(name="9c cascade", props_count=9, difficulty=61, tags={Tag.AsyncBasePattern}),
    Trick(name="cascade", props_count=9, difficulty=80, tags={Tag.AsyncBasePattern}),
    
    ########## SPINS ##########
    
    ### 3 props spins ###
    # base 360
    Trick(name="3up 360 -> cascade", props_count=3, difficulty=10, tags={Tag.Spin360}),
    Trick(name="5 X (1up 360) in a run", props_count=3, difficulty=20, tags={Tag.Spin360}),
    Trick(name="5 X (3up 360) in a run", props_count=3, difficulty=32, tags={Tag.Spin360}),
    Trick(name="75300 3up 360 -> cascade", props_count=3, difficulty=13, tags={Tag.Spin360, Tag.AsyncSiteswap}),
    Trick(name="cascade -> 74400 3up 360 -> cascade", props_count=3, difficulty=20, tags={Tag.Spin360, Tag.AsyncSiteswap}),

    # base 720
    Trick(name="3up 720 -> cascade", props_count=3, difficulty=32, tags={Tag.Spin720}),
    
    # multi-stage
    Trick(name="9440022 3up 2-stage -> cascade", props_count=3, difficulty=29, tags={Tag.MultiStage}),
    
    # connections
    Trick(name="441 -> 66300 3up 360 -> 441", props_count=3, difficulty=21, tags={Tag.Spin360, Tag.AsyncSiteswap}),
    Trick(name="cascade -> 3up 360 -> overheads", props_count=3, difficulty=18, tags={Tag.Spin360, Tag.Overheads}),
    Trick(name="3up 360 -> backrosses", props_count=3, difficulty=21, tags={Tag.Spin360, Tag.Backcrosses}),
    Trick(name="backrosses -> 3up 360 in backrosses -> backrosses", props_count=3, difficulty=40, tags={Tag.Spin360, Tag.Backcrosses}),
    Trick(name="overheads -> 3up 360 in overheads -> 531", props_count=3, difficulty=27, tags={Tag.Spin360, Tag.Overheads, Tag.AsyncSiteswap}),
    
    
    ### 4 props spins ###
    # base 360
    Trick(name="4up 360 -> async fountain", props_count=4, difficulty=22, tags={Tag.Spin360}),
    Trick(name="777300 4up 360 -> async fountain", props_count=4, difficulty=29, tags={Tag.Spin360, Tag.AsyncSiteswap}),
    Trick(name="sync fountain -> (8,8)(4,4)(0,0) 4up 360 -> sync fountain", props_count=4, difficulty=25, tags={Tag.Spin360, Tag.SyncSiteswap}),
    
    # base 720
    Trick(name="async fountain -> 2up 720 -> 534", props_count=4, difficulty=37, tags={Tag.Spin720}),
    Trick(name="async fountain -> 4up 720 -> 53534", props_count=4, difficulty=44, tags={Tag.Spin720, Tag.AsyncSiteswap}),
    
    # multi-stage
    Trick(name="(6,6)(8,8)(0,0)(2,2) 4up 2-stage -> sync fountain", props_count=4, difficulty=33, tags={Tag.MultiStage, Tag.SyncSiteswap}),
    
    # connections
    Trick(name="4up 360 -> 12c 534 in overheads", props_count=4, difficulty=39, tags={Tag.Spin360, Tag.Overheads, Tag.AsyncSiteswap}),
    Trick(name="3 consecutive 4up 360 -> fountain", props_count=4, difficulty=43, tags={Tag.Spin360}),
    Trick(name="sync fountain -> 2up 360 -> 4up 360 -> sync fountain ", props_count=4, difficulty=30, tags={Tag.Spin360}),
    Trick(name="async fountain -> 666700 4up 360 -> 561 ", props_count=4, difficulty=32, tags={Tag.Spin360, Tag.AsyncSiteswap}),
    Trick(name="async fountain -> 667700 4up 360 -> 714 ", props_count=4, difficulty=38, tags={Tag.Spin360, Tag.AsyncSiteswap}),
    Trick(name="async fountain -> 4up 360 -> 2up 360 -> sync fountain", props_count=4, difficulty=30, tags={Tag.Spin360}),
    Trick(name="4c sync fountain -> (8x,6)(2,2) 2up 360 -> shower", props_count=4, difficulty=30, tags={Tag.Spin360, Tag.SyncSiteswap}),
    
    ### 5 props spins ###
    # base 360
    Trick(name="3up 360 -> cascade", props_count=5, difficulty=26, tags={Tag.Spin360}),
    Trick(name="5up 360 -> cascade", props_count=5, difficulty=33, tags={Tag.Spin360}),
    Trick(name="744 -> 96622 3up 360 -> 744", props_count=5, difficulty=35, tags={Tag.Spin360, Tag.AsyncSiteswap}),
    Trick(name="6c 753 -> 97522 3up 360 -> cascade", props_count=5, difficulty=36, tags={Tag.Spin360, Tag.AsyncSiteswap}),
    Trick(name="cascade -> 97522 3up 360 -> cascade", props_count=5, difficulty=29, tags={Tag.Spin360, Tag.AsyncSiteswap}),
    Trick(name="cascade -> aa55500 5up 360 -> cascade", props_count=5, difficulty=47, tags={Tag.Spin360, Tag.AsyncSiteswap}),
    Trick(name="cascade -> b666600 5up 360 -> cascade", props_count=5, difficulty=38, tags={Tag.Spin360, Tag.AsyncSiteswap}),
    Trick(name="cascade -> 5up 360 -> (6x,4)*", props_count=5, difficulty=36, tags={Tag.Spin360, Tag.SyncSiteswap}, comment="spin notation: 8x78x78x"),
    
    # base 720
    Trick(name="3up 720 -> cascade", props_count=5, difficulty=45, tags={Tag.Spin720}),
    
    # multi-spin
    Trick(name="cascade -> 77779007722 5up 2-stage -> cascade", props_count=5, difficulty=51, tags={Tag.MultiStage, Tag.AsyncSiteswap}),
    Trick(name="744 -> d6688 5up 2-stage -> cascade", props_count=5, difficulty=72, tags={Tag.MultiStage, Tag.AsyncSiteswap}),
    Trick(name="(6x,4)* -> (8x,4)(6,ax)(2,2)(8x,6)(2,2) 3up 2-stage -> (6x,4)*", props_count=5, difficulty=42, tags={Tag.Spin360, Tag.SyncSiteswap}),
    
    # Connections
    Trick(name="97531 -> b975300 5up 360 -> 97531", props_count=5, difficulty=49, tags={Tag.Spin360, Tag.AsyncSiteswap}),
    Trick(name="cascade -> 5up 360 -> 3up 360 -> 744", props_count=5, difficulty=40, tags={Tag.Spin360}),
    Trick(name="cascade -> 3 connected 3up 360 -> cascade", props_count=5, difficulty=48, tags={Tag.Spin360}),
    Trick(name="5up 360 -> overheads", props_count=5, difficulty=48, tags={Tag.Spin360, Tag.Overheads}),
    
    ### 6 props spins ###
    # base 360
    Trick(name="async fountain -> aa6622 4up 360 -> async fountain", props_count=6, difficulty=66, tags={Tag.Spin360, Tag.AsyncSiteswap}),
    Trick(name="6c async fountain -> bbb555 6up 360 -> async fountain", props_count=6, difficulty=75, tags={Tag.Spin360, Tag.AsyncSiteswap}),
    
    # base 720
    Trick(name="async fountain -> cc882222 4up 720 -> 864", props_count=6, difficulty=73, tags={Tag.Spin720, Tag.AsyncSiteswap}),
    Trick(name="(8,4)* -> (c,4)(4,c)(c,8)(2,2)(2,2) 4up 720 -> (8,4)*", props_count=6, difficulty=75, tags={Tag.Spin720, Tag.SyncSiteswap}),
    
    # multi-spin
    Trick(name="sync fountain -> (8,8)(a,a)(2,2)(8,8)(2,2) 4up 2-stage -> sync fountain", props_count=6, difficulty=65, tags={Tag.MultiStage, Tag.SyncSiteswap}),
    
    # connections
    Trick(name="10c 95556 -> b77722 4up 360 -> 756", props_count=6, difficulty=69, tags={Tag.Spin360, Tag.AsyncSiteswap}),
    
    ### 7 props spins ###
    # base 360
    Trick(name="5up 360 -> cascade", props_count=7, difficulty=68, tags={Tag.Spin360}),
    Trick(name="cascade -> aaaa522 5up 360 -> cascade", props_count=7, difficulty=80, tags={Tag.Spin360, Tag.AsyncSiteswap}),
    
    # base 720
    Trick(name="cascade -> 5up 720 -> cascade", props_count=7, difficulty=90, tags={Tag.Spin720}),
    
    # multi-spin
    Trick(name="cascade -> 9999b22999922 5up 2-stage -> cascade", props_count=7, difficulty=81, tags={Tag.MultiStage, Tag.AsyncSiteswap}),
    
    # connections
    Trick(name="12c 966 -> d888822 5up 360 -> cascade", props_count=7, difficulty=73, tags={Tag.Spin360, Tag.AsyncSiteswap}),
    Trick(name="867 -> 1 high 4 low 360 -> (8,6x)*", props_count=7, difficulty=85, tags={Tag.Spin360, Tag.SyncSiteswap}, comment="spin notation: ex9x89x822"),
    
    ########## SITESWAPS ##########
    
    ### 3 props siteswaps ###
    # period 3
    Trick(name="24c 531", props_count=3, difficulty=7, tags={Tag.AsyncSiteswap}),
    Trick(name="24c 531 on the knees", props_count=3, difficulty=10, tags={Tag.AsyncSiteswap, Tag.OnTheKnees}),
    Trick(name="36c 801", props_count=3, difficulty=23, tags={Tag.AsyncSiteswap}, comment="Entrance: 46"),
    
    # period 5
    Trick(name="20c 45123", props_count=3, difficulty=9, tags={Tag.AsyncSiteswap}),
    Trick(name="30c 44133", props_count=3, difficulty=8, tags={Tag.AsyncSiteswap}),
    
    # other period
    
    
    # connections
    Trick(name="6c 60 -> exactly 5c 50505 -> 6c 60", props_count=3, difficulty=21, tags={Tag.AsyncSiteswap}, comment="start: 3 in one hand"),
    Trick(name="box -> 8c inverted box -> box", props_count=3, difficulty=15, tags={Tag.AsyncSiteswap}),
    
    ### 4 props siteswaps ###
    # period 3
    Trick(name="24c 534", props_count=4, difficulty=12, tags={Tag.AsyncSiteswap}),
    Trick(name="18c 633", props_count=4, difficulty=17, tags={Tag.AsyncSiteswap}),
    Trick(name="24c 714", props_count=4, difficulty=22, tags={Tag.AsyncSiteswap}, comment="Entrance: 55"),
    Trick(name="60c 741", props_count=4, difficulty=22, tags={Tag.AsyncSiteswap}, comment="Entrance: 5"),
    Trick(name="60c 561", props_count=4, difficulty=20, tags={Tag.AsyncSiteswap}, comment="Entrance: 5"),
    Trick(name="42c 831", props_count=4, difficulty=23, tags={Tag.AsyncSiteswap}, comment="Entrance: 6"),

    # period 4
    Trick(name="8c 7531, under the leg 1", props_count=4, difficulty=24, tags={Tag.AsyncSiteswap, Tag.UnderLegs}),
    
    # period 5
    Trick(name="24c 53534", props_count=4, difficulty=19, tags={Tag.AsyncSiteswap}),
    Trick(name="30c 63551", props_count=4, difficulty=22, tags={Tag.AsyncSiteswap}),
    Trick(name="20c 55613", props_count=4, difficulty=24, tags={Tag.AsyncSiteswap}),
    Trick(name="50c 66161", props_count=4, difficulty=22, tags={Tag.AsyncSiteswap}, comment="Entrance: 5"),
    Trick(name="50c 73334", props_count=4, difficulty=19, tags={Tag.AsyncSiteswap}),
    Trick(name="40c 74414", props_count=4, difficulty=17, tags={Tag.AsyncSiteswap}),
    Trick(name="30c 75314", props_count=4, difficulty=18, tags={Tag.AsyncSiteswap}),
    Trick(name="20c 66314", props_count=4, difficulty=18, tags={Tag.AsyncSiteswap}),
    Trick(name="10c 83531", props_count=4, difficulty=17, tags={Tag.AsyncSiteswap}),
    
    # other period
    Trick(name="32c (6x,4)(4,2x)*", props_count=4, difficulty=15, tags={Tag.SyncSiteswap}),
    Trick(name="32c (4x,6)(4,2x)*", props_count=4, difficulty=16, tags={Tag.SyncSiteswap}),
    
    # connections
    Trick(name="async fountain -> sync fountain -> async fountain", props_count=4, difficulty=12, tags={Tag.AsyncSiteswap}, comment="transitions: 5x4, (5x,4)"),
    Trick(name="18c 534 -> 20c 53444", props_count=4, difficulty=15, tags={Tag.AsyncSiteswap}),
    
    ### 5 props siteswaps ###
    # period 3
    Trick(name="30c 744", props_count=5, difficulty=25, tags={Tag.AsyncSiteswap}),
    Trick(name="18c 645", props_count=5, difficulty=24, tags={Tag.AsyncSiteswap}),
    Trick(name="cascade -> 6c 663 -> cascade", props_count=5, difficulty=26, tags={Tag.AsyncSiteswap}),
    Trick(name="30c 771", props_count=5, difficulty=38, tags={Tag.AsyncSiteswap}, comment="entrance: 75"),
    Trick(name="24c 834", props_count=5, difficulty=37, tags={Tag.AsyncSiteswap}, comment="entrance: 6"),
    Trick(name="30c 933", props_count=5, difficulty=62, tags={Tag.AsyncSiteswap}, comment="entrance: 7"),
    
    # period 5
    Trick(name="cascade -> 5c 97531 -> cascade", props_count=5, difficulty=28, tags={Tag.AsyncSiteswap}),
    Trick(name="cascade -> 5c 88441 -> cascade", props_count=5, difficulty=30, tags={Tag.AsyncSiteswap}),
    Trick(name="40c 64645", props_count=5, difficulty=33, tags={Tag.AsyncSiteswap}),
    Trick(name="50c 66364", props_count=5, difficulty=37, tags={Tag.AsyncSiteswap}),
    Trick(name="30c 67363", props_count=5, difficulty=41, tags={Tag.AsyncSiteswap}),
    Trick(name="30c 74734", props_count=5, difficulty=36, tags={Tag.AsyncSiteswap}),
    Trick(name="30c 64753", props_count=5, difficulty=41, tags={Tag.AsyncSiteswap}),
    Trick(name="50c 74635", props_count=5, difficulty=41, tags={Tag.AsyncSiteswap}),
    Trick(name="50c 75751", props_count=5, difficulty=37, tags={Tag.AsyncSiteswap}),
    Trick(name="30c 77335", props_count=5, difficulty=45, tags={Tag.AsyncSiteswap}),
    Trick(name="30c 78451", props_count=5, difficulty=47, tags={Tag.AsyncSiteswap}),
    Trick(name="30c 74464", props_count=5, difficulty=31, tags={Tag.AsyncSiteswap}),
    Trick(name="20c 84463", props_count=5, difficulty=36, tags={Tag.AsyncSiteswap}),
    Trick(name="20c 94444", props_count=5, difficulty=32, tags={Tag.AsyncSiteswap}),
    
    # connections
    Trick(name="744 -> 5c 97531 -> 645", props_count=5, difficulty=30, tags={Tag.AsyncSiteswap}),
    Trick(name="6c 753 -> 5c 97531 -> cascade", props_count=5, difficulty=30, tags={Tag.AsyncSiteswap}),
    Trick(name="5c cascade -> 7c b444444 -> backrosses", props_count=5, difficulty=45, tags={Tag.AsyncSiteswap, Tag.Backcrosses}),
    
    # other period
    Trick(name="32c (6x,4x)(6,4x)*", props_count=5, difficulty=29, tags={Tag.SyncSiteswap}),
    Trick(name="24c (6,4)(6x,4)*", props_count=5, difficulty=28, tags={Tag.SyncSiteswap}),
    Trick(name="36c (6,4)(6x,4)(6x,4x)*", props_count=5, difficulty=33, tags={Tag.SyncSiteswap}),
    
    ### 6 props siteswaps ###
    # period 3
    Trick(name="36c 756", props_count=6, difficulty=38, tags={Tag.AsyncSiteswap}),
    Trick(name="30c a44", props_count=6, difficulty=57, tags={Tag.AsyncSiteswap}, comment="entrance: 8"),
    Trick(name="30c 891", props_count=6, difficulty=67, tags={Tag.AsyncSiteswap}, comment="entrance: 778"),
    
    # period 5
    Trick(name="30c 96636", props_count=6, difficulty=61, tags={Tag.AsyncSiteswap}),
    Trick(name="30c 77736", props_count=6, difficulty=58, tags={Tag.AsyncSiteswap}),
    Trick(name="30c 78456", props_count=6, difficulty=59, tags={Tag.AsyncSiteswap}),
    Trick(name="50c 85845", props_count=6, difficulty=59, tags={Tag.AsyncSiteswap}),
    Trick(name="30c 88446", props_count=6, difficulty=54, tags={Tag.AsyncSiteswap}),
    Trick(name="20c 79455", props_count=6, difficulty=54, tags={Tag.AsyncSiteswap}),
    Trick(name="20c 95556", props_count=6, difficulty=47, tags={Tag.AsyncSiteswap}),
    Trick(name="30c 79635", props_count=6, difficulty=58, tags={Tag.AsyncSiteswap}),
    Trick(name="20c 99444", props_count=6, difficulty=51, tags={Tag.AsyncSiteswap}),
    Trick(name="20c a5753", props_count=6, difficulty=65, tags={Tag.AsyncSiteswap}),
    
    ### 7 props siteswaps ###
    # period 3
    Trick(name="cascade -> 966", props_count=7, difficulty=55, tags={Tag.AsyncSiteswap}),
    
    # period 5
    Trick(name="7c cascade -> 5c aa555 -> 7c cascade", props_count=7, difficulty=53, tags={Tag.AsyncSiteswap}),
    Trick(name="7c cascade -> 5c 99944 -> 7c cascade", props_count=7, difficulty=51, tags={Tag.AsyncSiteswap}),
    Trick(name="7c cascade -> 6c 975 -> 7c cascade", props_count=7, difficulty=50, tags={Tag.AsyncSiteswap}),
    Trick(name="cascade -> 5c b9753 -> cascade", props_count=7, difficulty=57, tags={Tag.AsyncSiteswap}),
    
    ### 8 props siteswaps ###
    # period 3
    Trick(name="978", props_count=8, difficulty=72, tags={Tag.AsyncSiteswap}),
    Trick(name="996", props_count=8, difficulty=74, tags={Tag.AsyncSiteswap}),
    
    # period 5
    Trick(name="97996", props_count=8, difficulty=79, tags={Tag.AsyncSiteswap}),
    
    ########## BODY THROWS ##########
    
    ### 3 props body throws ###
    Trick(name="backrosses", props_count=3, difficulty=15, tags={Tag.Backcrosses}),
    Trick(name="10c neck throws", props_count=3, difficulty=24, tags={Tag.Necks}),
    Trick(name="24c 423, backross 3", props_count=3, difficulty=19, tags={Tag.Backcrosses, Tag.AsyncSiteswap}),
    Trick(name="24c 423, shoulder 4", props_count=3, difficulty=23, tags={Tag.Shoulders, Tag.AsyncSiteswap}),
    Trick(name="overheads -> 3c overhead reverse shoulder -> 3c backrosses -> overheads", props_count=3, difficulty=33, tags={Tag.Overheads, Tag.ReverseShoulders, Tag.Backcrosses}, comment="The impossible trick"),
    Trick(name="6c under the leg throws", props_count=3, difficulty=19, tags={Tag.UnderLegs}),
    Trick(name="cc111111111, around the body 1's", props_count=3, difficulty=70, tags={Tag.SpecialBodyThrows}),
    Trick(name="10c 44133, backrosses 3's", props_count=3, difficulty=18, tags={Tag.Backcrosses, Tag.AsyncSiteswap}),
    
    ### 4 props body throws ###
    Trick(name="reverse shoulders async fountain", props_count=4, difficulty=42, tags={Tag.ReverseShoulders, Tag.AsyncSiteswap}),
    Trick(name="4c ANY -> 1c ass catch -> ANY", props_count=4, difficulty=41, tags={Tag.SpecialBodyThrows}),
    Trick(name="fountain -> 2c reverse shoulders -> 2c shoulders -> fountain", props_count=4, difficulty=28, tags={Tag.ReverseShoulders, Tag.Shoulders}),
    Trick(name="8c penguins", props_count=4, difficulty=26, tags={Tag.SpecialBodyThrows}),
    Trick(name="20c laying on the back", props_count=4, difficulty=25, tags={Tag.OnTheBack, Tag.Overheads}),
    Trick(name="overheads -> 4c overhead reverse shoulders -> 4c shoulders -> overheads", props_count=4, difficulty=49, tags={Tag.Overheads, Tag.ReverseShoulders, Tag.Shoulders}, comment="The impossible trick"),
    
    ### 5 props body throws ###
    Trick(name="5c 94444, shoulders 4's", props_count=5, difficulty=43, tags={Tag.Shoulders, Tag.AsyncSiteswap}),
    Trick(name="18c 645, shoulder 4", props_count=5, difficulty=45, tags={Tag.Shoulders, Tag.AsyncSiteswap}),
    Trick(name="30c overheads", props_count=5, difficulty=36, tags={Tag.Overheads}),
    Trick(name="overheads -> 6c 744 overheads -> overheads", props_count=5, difficulty=40, tags={Tag.Overheads, Tag.AsyncSiteswap}),
    Trick(name="10c laying on the back", props_count=5, difficulty=32, tags={Tag.OnTheBack, Tag.Overheads}),
    Trick(name="half shower -> overheads -> other side half shower", props_count=5, difficulty=40, tags={Tag.Overheads}),
    Trick(name="cascade -> 8c 7733, neck throws 3's", props_count=5, difficulty=82, tags={Tag.Necks, Tag.AsyncSiteswap}),
    
    ### 6 props body throws ###
    Trick(name="756 -> 6c 756, backross 5 -> 756", props_count=6, difficulty=66, tags={Tag.Backcrosses, Tag.AsyncSiteswap}),
    Trick(name="6c fountain -> 6c overheads -> 6c fountain", props_count=6, difficulty=45, tags={Tag.Overheads}),
    
    ### 7 props body throws ###
    Trick(name="cascade -> 7c backrosses", props_count=7, difficulty=74, tags={Tag.Backcrosses})
]
