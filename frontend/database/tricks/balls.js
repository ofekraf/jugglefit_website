const BALLS_TRICKS = [

    /* BASE PATTERNS */
    
    // 4 props base patterns
    {name: "20c sync fountain -> 20c async fountain", props_count: 4, difficulty: 10, tags: ["sync base pattern", "async base pattern"], comment: "Transition: (5x,4)"},
    
    // 5 props base patterns
    {name: "20c cascade", props_count: 5, difficulty: 13, tags: ["async base pattern"]},
    {name: "50c isolated cascade", props_count: 5, difficulty: 29, tags: ["async base pattern", "isolated"]},
    {name: "30c reverse cascade", props_count: 5, difficulty: 37, tags: ["async base pattern"]},
    
    // 6 props base patterns
    {name: "ANY", props_count: 6, difficulty: 24, tags: ["any base pattern"]},
    {name: "async fountain", props_count: 6, difficulty: 29, tags: ["async base pattern"]},
    {name: "20c async fountain", props_count: 6, difficulty: 30, tags: ["async base pattern"]},
    {name: "isolated sync fountain", props_count: 6, difficulty: 32, tags: ["sync base pattern", "isolated"]},
    {name: "sync fountain -> async fountain", props_count: 6, difficulty: 34, tags: ["sync base pattern", "async base pattern"], comment: "transition: (7x,6)(7x,6)"},
    {name: "async fountain -> sync fountain", props_count: 6, difficulty: 34, tags: ["async base pattern", "sync base pattern"], comment: "transition: 7x67x6"},
    {name: "ANY on the knees", props_count: 6, difficulty: 28, tags: ["any base pattern", "on the knees"]},
    
    // 7 props base patterns
    {name: "7c cascade", props_count: 7, difficulty: 26, tags: ["async base pattern"]},
    {name: "cascade", props_count: 7, difficulty: 34, tags: ["async base pattern"]},
    {name: "7c cascade on the knees", props_count: 7, difficulty: 32, tags: ["async base pattern", "on the knees"]},
    {name: "isolated cascade", props_count: 7, difficulty: 35, tags: ["async base pattern", "isolated"]},
    
    // 8 props base patterns
    {name: "8c sync fountain", props_count: 8, difficulty: 43, tags: ["sync base pattern"]},
    {name: "8c async fountain", props_count: 8, difficulty: 45, tags: ["async base pattern"]},
    {name: "16c async ANY", props_count: 8, difficulty: 68, tags: ["async base pattern"]},
    
    
    // 9 props base patterns
    {name: "9c cascade", props_count: 9, difficulty: 61, tags: ["async base pattern"]},
    {name: "cascade", props_count: 9, difficulty: 80, tags: ["async base pattern"]},
    
    /* SPINS */
    
    // 3 props spins
    // base 360
    {name: "3up 360 -> cascade", props_count: 3, difficulty: 10, tags: ["360 spin"]},
    {name: "5 X (1up 360) in a run", props_count: 3, difficulty: 20, tags: ["360 spin"]},
    {name: "5 X (3up 360) in a run", props_count: 3, difficulty: 32, tags: ["360 spin"]},
    {name: "75300 3up 360 -> cascade", props_count: 3, difficulty: 13, tags: ["360 spin", "async siteswap"]},
    {name: "cascade -> 74400 3up 360 -> cascade", props_count: 3, difficulty: 20, tags: ["360 spin", "async siteswap"]},

    // base 720
    {name: "3up 720 -> cascade", props_count: 3, difficulty: 32, tags: ["720 spin"]},
    
    // multi-stage
    {name: "9440022 3up 2-stage -> cascade", props_count: 3, difficulty: 29, tags: ["multi stage"]},
    
    // connections
    {name: "441 -> 66300 3up 360 -> 441", props_count: 3, difficulty: 21, tags: ["360 spin", "async siteswap"]},
    {name: "cascade -> 3up 360 -> overheads", props_count: 3, difficulty: 18, tags: ["360 spin", "overheads"]},
    {name: "3up 360 -> backrosses", props_count: 3, difficulty: 21, tags: ["360 spin", "backcrosses"]},
    {name: "backrosses -> 3up 360 in backrosses -> backrosses", props_count: 3, difficulty: 40, tags: ["360 spin", "backcrosses"]},
    {name: "overheads -> 3up 360 in overheads -> 531", props_count: 3, difficulty: 27, tags: ["360 spin", "overheads", "async siteswap"]},
    
    
    // 4 props spins
    // base 360
    {name: "4up 360 -> async fountain", props_count: 4, difficulty: 22, tags: ["360 spin"]},
    {name: "777300 4up 360 -> async fountain", props_count: 4, difficulty: 29, tags: ["360 spin", "async siteswap"]},
    {name: "sync fountain -> (8,8)(4,4)(0,0) 4up 360 -> sync fountain", props_count: 4, difficulty: 25, tags: ["360 spin", "sync siteswap"]},
    
    // base 720
    {name: "async fountain -> 2up 720 -> 534", props_count: 4, difficulty: 37, tags: ["720 spin"]},
    {name: "async fountain -> 4up 720 -> 53534", props_count: 4, difficulty: 44, tags: ["720 spin", "async siteswap"]},
    
    // multi-stage
    {name: "(6,6)(8,8)(0,0)(2,2) 4up 2-stage -> sync fountain", props_count: 4, difficulty: 33, tags: ["multi stage", "sync siteswap"]},
    
    // connections
    {name: "4up 360 -> 12c 534 in overheads", props_count: 4, difficulty: 39, tags: ["360 spin", "overheads", "async siteswap"]},
    {name: "3 consecutive 4up 360 -> fountain", props_count: 4, difficulty: 43, tags: ["360 spin"]},
    {name: "sync fountain -> 2up 360 -> 4up 360 -> sync fountain ", props_count: 4, difficulty: 30, tags: ["360 spin"]},
    {name: "async fountain -> 666700 4up 360 -> 561 ", props_count: 4, difficulty: 32, tags: ["360 spin", "async siteswap"]},
    {name: "async fountain -> 667700 4up 360 -> 714 ", props_count: 4, difficulty: 38, tags: ["360 spin", "async siteswap"]},
    {name: "async fountain -> 4up 360 -> 2up 360 -> sync fountain", props_count: 4, difficulty: 30, tags: ["360 spin"]},
    {name: "4c sync fountain -> (8x,6)(2,2) 2up 360 -> shower", props_count: 4, difficulty: 30, tags: ["360 spin", "sync siteswap"]},
    
    // 5 props spins
    // base 360
    {name: "3up 360 -> cascade", props_count: 5, difficulty: 26, tags: ["360 spin"]},
    {name: "5up 360 -> cascade", props_count: 5, difficulty: 33, tags: ["360 spin"]},
    {name: "744 -> 96622 3up 360 -> 744", props_count: 5, difficulty: 35, tags: ["360 spin", "async siteswap"]},
    {name: "6c 753 -> 97522 3up 360 -> cascade", props_count: 5, difficulty: 36, tags: ["360 spin", "async siteswap"]},
    {name: "cascade -> 97522 3up 360 -> cascade", props_count: 5, difficulty: 29, tags: ["360 spin", "async siteswap"]},
    {name: "cascade -> aa55500 5up 360 -> cascade", props_count: 5, difficulty: 47, tags: ["360 spin", "async siteswap"]},
    {name: "cascade -> b666600 5up 360 -> cascade", props_count: 5, difficulty: 38, tags: ["360 spin", "async siteswap"]},
    {name: "cascade -> 5up 360 -> (6x,4)*", props_count: 5, difficulty: 36, tags: ["360 spin", "sync siteswap"], comment: "spin notation: 8x78x78x"},
    
    // base 720
    {name: "3up 720 -> cascade", props_count: 5, difficulty: 45, tags: ["720 spin"]},
    
    // multi-spin
    {name: "cascade -> 77779007722 5up 2-stage -> cascade", props_count: 5, difficulty: 51, tags: ["multi stage", "async siteswap"]},
    {name: "744 -> d6688 5up 2-stage -> cascade", props_count: 5, difficulty: 72, tags: ["multi stage", "async siteswap"]},
    {name: "(6x,4)* -> (8x,4)(6,ax)(2,2)(8x,6)(2,2) 3up 2-stage -> (6x,4)*", props_count: 5, difficulty: 42, tags: ["360 spin", "sync siteswap"]},
    
    // Connections
    {name: "97531 -> b975300 5up 360 -> 97531", props_count: 5, difficulty: 49, tags: ["360 spin", "async siteswap"]},
    {name: "cascade -> 5up 360 -> 3up 360 -> 744", props_count: 5, difficulty: 40, tags: ["360 spin"]},
    {name: "cascade -> 3 connected 3up 360 -> cascade", props_count: 5, difficulty: 48, tags: ["360 spin"]},
    {name: "5up 360 -> overheads", props_count: 5, difficulty: 48, tags: ["360 spin", "overheads"]},
    
    // 6 props spins
    // base 360
    {name: "async fountain -> aa6622 4up 360 -> async fountain", props_count: 6, difficulty: 66, tags: ["360 spin", "async siteswap"]},
    {name: "6c async fountain -> bbb555 6up 360 -> async fountain", props_count: 6, difficulty: 75, tags: ["360 spin", "async siteswap"]},
    
    // base 720
    {name: "async fountain -> cc882222 4up 720 -> 864", props_count: 6, difficulty: 73, tags: ["720 spin", "async siteswap"]},
    {name: "(8,4)* -> (c,4)(4,c)(c,8)(2,2)(2,2) 4up 720 -> (8,4)*", props_count: 6, difficulty: 75, tags: ["720 spin", "sync siteswap"]},
    
    // multi-spin
    {name: "sync fountain -> (8,8)(a,a)(2,2)(8,8)(2,2) 4up 2-stage -> sync fountain", props_count: 6, difficulty: 65, tags: ["multi stage", "sync siteswap"]},
    
    // connections
    {name: "10c 95556 -> b77722 4up 360 -> 756", props_count: 6, difficulty: 69, tags: ["360 spin", "async siteswap"]},
    
    // 7 props spins
    // base 360
    {name: "5up 360 -> cascade", props_count: 7, difficulty: 68, tags: ["360 spin"]},
    {name: "cascade -> aaaa522 5up 360 -> cascade", props_count: 7, difficulty: 80, tags: ["360 spin", "async siteswap"]},
    
    // base 720
    {name: "cascade -> 5up 720 -> cascade", props_count: 7, difficulty: 90, tags: ["720 spin"]},
    
    // multi-spin
    {name: "cascade -> 9999b22999922 5up 2-stage -> cascade", props_count: 7, difficulty: 81, tags: ["multi stage", "async siteswap"]},
    
    // connections
    {name: "12c 966 -> d888822 5up 360 -> cascade", props_count: 7, difficulty: 73, tags: ["360 spin", "async siteswap"]},
    {name: "867 -> 1 high 4 low 360 -> (8,6x)*", props_count: 7, difficulty: 85, tags: ["360 spin", "sync siteswap"], comment: "spin notation: ex9x89x822"},
    
    /* SITESWAPS */
    
    // 3 props siteswaps
    // period 3
    {name: "24c 531", props_count: 3, difficulty: 7, tags: ["async siteswap"]},
    {name: "24c 531 on the knees", props_count: 3, difficulty: 10, tags: ["async siteswap", "on the knees"]},
    {name: "36c 801", props_count: 3, difficulty: 23, tags: ["async siteswap"], comment: "Entrance: 46"},
    
    // period 5
    {name: "20c 45123", props_count: 3, difficulty: 9, tags: ["async siteswap"]},
    {name: "30c 44133", props_count: 3, difficulty: 8, tags: ["async siteswap"]},
    
    // other period
    
    
    // connections
    {name: "6c 60 -> exactly 5c 50505 -> 6c 60", props_count: 3, difficulty: 21, tags: ["async siteswap"], comment: "start: 3 in one hand"},
    {name: "box -> 8c inverted box -> box", props_count: 3, difficulty: 15, tags: ["async siteswap"]},
    
    // 4 props siteswaps
    // period 3
    {name: "24c 534", props_count: 4, difficulty: 12, tags: ["async siteswap"]},
    {name: "18c 633", props_count: 4, difficulty: 17, tags: ["async siteswap"]},
    {name: "24c 714", props_count: 4, difficulty: 22, tags: ["async siteswap"], comment: "Entrance: 55"},
    {name: "60c 741", props_count: 4, difficulty: 22, tags: ["async siteswap"], comment: "Entrance: 5"},
    {name: "60c 561", props_count: 4, difficulty: 20, tags: ["async siteswap"], comment: "Entrance: 5"},
    {name: "42c 831", props_count: 4, difficulty: 23, tags: ["async siteswap"], comment: "Entrance: 6"},

    // period 4
    {name: "8c 7531, under the leg 1", props_count: 4, difficulty: 24, tags: ["async siteswap", "under legs"]},
    
    // period 5
    {name: "24c 53534", props_count: 4, difficulty: 19, tags: ["async siteswap"]},
    {name: "30c 63551", props_count: 4, difficulty: 22, tags: ["async siteswap"]},
    {name: "20c 55613", props_count: 4, difficulty: 24, tags: ["async siteswap"]},
    {name: "50c 66161", props_count: 4, difficulty: 22, tags: ["async siteswap"], comment: "Entrance: 5"},
    {name: "50c 73334", props_count: 4, difficulty: 19, tags: ["async siteswap"]},
    {name: "40c 74414", props_count: 4, difficulty: 17, tags: ["async siteswap"]},
    {name: "30c 75314", props_count: 4, difficulty: 18, tags: ["async siteswap"]},
    {name: "20c 66314", props_count: 4, difficulty: 18, tags: ["async siteswap"]},
    {name: "10c 83531", props_count: 4, difficulty: 17, tags: ["async siteswap"]},
    
    // other period
    {name: "32c (6x,4)(4,2x)*", props_count: 4, difficulty: 15, tags: ["sync siteswap"]},
    {name: "32c (4x,6)(4,2x)*", props_count: 4, difficulty: 16, tags: ["sync siteswap"]},
    
    // connections
    {name: "async fountain -> sync fountain -> async fountain", props_count: 4, difficulty: 12, tags: ["async siteswap"], comment: "transitions: 5x4, (5x,4)"},
    {name: "18c 534 -> 20c 53444", props_count: 4, difficulty: 15, tags: ["async siteswap"]},
    
    // 5 props siteswaps
    // period 3
    {name: "30c 744", props_count: 5, difficulty: 25, tags: ["async siteswap"]},
    {name: "18c 645", props_count: 5, difficulty: 24, tags: ["async siteswap"]},
    {name: "cascade -> 6c 663 -> cascade", props_count: 5, difficulty: 26, tags: ["async siteswap"]},
    {name: "30c 771", props_count: 5, difficulty: 38, tags: ["async siteswap"], comment: "entrance: 75"},
    {name: "24c 834", props_count: 5, difficulty: 37, tags: ["async siteswap"], comment: "entrance: 6"},
    {name: "30c 933", props_count: 5, difficulty: 62, tags: ["async siteswap"], comment: "entrance: 7"},
    
    // period 5
    {name: "cascade -> 5c 97531 -> cascade", props_count: 5, difficulty: 28, tags: ["async siteswap"]},
    {name: "cascade -> 5c 88441 -> cascade", props_count: 5, difficulty: 30, tags: ["async siteswap"]},
    {name: "40c 64645", props_count: 5, difficulty: 33, tags: ["async siteswap"]},
    {name: "50c 66364", props_count: 5, difficulty: 37, tags: ["async siteswap"]},
    {name: "30c 67363", props_count: 5, difficulty: 41, tags: ["async siteswap"]},
    {name: "30c 74734", props_count: 5, difficulty: 36, tags: ["async siteswap"]},
    {name: "30c 64753", props_count: 5, difficulty: 41, tags: ["async siteswap"]},
    {name: "50c 74635", props_count: 5, difficulty: 41, tags: ["async siteswap"]},
    {name: "50c 75751", props_count: 5, difficulty: 37, tags: ["async siteswap"]},
    {name: "30c 77335", props_count: 5, difficulty: 45, tags: ["async siteswap"]},
    {name: "30c 78451", props_count: 5, difficulty: 47, tags: ["async siteswap"]},
    {name: "30c 74464", props_count: 5, difficulty: 31, tags: ["async siteswap"]},
    {name: "20c 84463", props_count: 5, difficulty: 36, tags: ["async siteswap"]},
    {name: "20c 94444", props_count: 5, difficulty: 32, tags: ["async siteswap"]},
    
    // connections
    {name: "744 -> 5c 97531 -> 645", props_count: 5, difficulty: 30, tags: ["async siteswap"]},
    {name: "6c 753 -> 5c 97531 -> cascade", props_count: 5, difficulty: 30, tags: ["async siteswap"]},
    {name: "5c cascade -> 7c b444444 -> backrosses", props_count: 5, difficulty: 45, tags: ["async siteswap", "backcrosses"]},
    
    // other period
    {name: "32c (6x,4x)(6,4x)*", props_count: 5, difficulty: 29, tags: ["sync siteswap"]},
    {name: "24c (6,4)(6x,4)*", props_count: 5, difficulty: 28, tags: ["sync siteswap"]},
    {name: "36c (6,4)(6x,4)(6x,4x)*", props_count: 5, difficulty: 33, tags: ["sync siteswap"]},
    
    // 6 props siteswaps
    // period 3
    {name: "36c 756", props_count: 6, difficulty: 38, tags: ["async siteswap"]},
    {name: "30c a44", props_count: 6, difficulty: 57, tags: ["async siteswap"], comment: "entrance: 8"},
    {name: "30c 891", props_count: 6, difficulty: 67, tags: ["async siteswap"], comment: "entrance: 778"},
    
    // period 5
    {name: "30c 96636", props_count: 6, difficulty: 61, tags: ["async siteswap"]},
    {name: "30c 77736", props_count: 6, difficulty: 58, tags: ["async siteswap"]},
    {name: "30c 78456", props_count: 6, difficulty: 59, tags: ["async siteswap"]},
    {name: "50c 85845", props_count: 6, difficulty: 59, tags: ["async siteswap"]},
    {name: "30c 88446", props_count: 6, difficulty: 54, tags: ["async siteswap"]},
    {name: "20c 79455", props_count: 6, difficulty: 54, tags: ["async siteswap"]},
    {name: "20c 95556", props_count: 6, difficulty: 47, tags: ["async siteswap"]},
    {name: "30c 79635", props_count: 6, difficulty: 58, tags: ["async siteswap"]},
    {name: "20c 99444", props_count: 6, difficulty: 51, tags: ["async siteswap"]},
    {name: "20c a5753", props_count: 6, difficulty: 65, tags: ["async siteswap"]},
    
    // 7 props siteswaps
    // period 3
    {name: "cascade -> 966", props_count: 7, difficulty: 55, tags: ["async siteswap"]},
    {name: "30c 867", props_count: 7, difficulty: 52, tags: ["async siteswap"]},
    {name: "30c 957", props_count: 7, difficulty: 63, tags: ["async siteswap"]},
    {name: "30c b46", props_count: 7, difficulty: 88, tags: ["async siteswap"], comment: "entrance: 9"},
    {name: "30c a47", props_count: 7, difficulty: 85, tags: ["async siteswap"], comment: "entrance: 8"},
    
    // period 5
    {name: "20c a6667", props_count: 7, difficulty: 70, tags: ["async siteswap"]},
    {name: "30c 98837", props_count: 7, difficulty: 68, tags: ["async siteswap"]},
    {name: "20c 97775", props_count: 7, difficulty: 67, tags: ["async siteswap"]},
    {name: "20c 99665", props_count: 7, difficulty: 65, tags: ["async siteswap"]},
    {name: "30c b6667", props_count: 7, difficulty: 82, tags: ["async siteswap"]},
    {name: "20c b8557", props_count: 7, difficulty: 84, tags: ["async siteswap"]},
    
    // 8 props siteswaps
    // period 3
    {name: "8c async fountain -> 978", props_count: 8, difficulty: 72, tags: ["async siteswap"]},
    
    /* BODY THROWS */
    // 3 props body throws
    {name: "12c overheads", props_count: 3, difficulty: 12, tags: ["overheads"]},
    {name: "backrosses", props_count: 3, difficulty: 15, tags: ["backcrosses"]},
    {name: "24c backrosses", props_count: 3, difficulty: 19, tags: ["backcrosses"]},
    {name: "shoulders", props_count: 3, difficulty: 20, tags: ["shoulders"]},
    {name: "24c full reverse", props_count: 3, difficulty: 23, tags: ["shoulders"]},
    {name: "overheads -> backrosses -> overheads", props_count: 3, difficulty: 25, tags: ["overheads", "backcrosses"]},
    {name: "cascade -> under 1 leg -> cascade", props_count: 3, difficulty: 5, tags: ["under legs"]},
    {name: "cascade -> albert -> cascade", props_count: 3, difficulty: 15, tags: ["under legs"]},
    {name: "cascade -> trebla -> cascade", props_count: 3, difficulty: 18, tags: ["under legs"]},
    
    // 4 props body throws
    {name: "12c 534 in overheads", props_count: 4, difficulty: 32, tags: ["overheads"]},
    
    // 5 props body throws
    {name: "overheads", props_count: 5, difficulty: 41, tags: ["overheads"]},
    {name: "24c overheads", props_count: 5, difficulty: 43, tags: ["overheads"]},
    {name: "backrosses", props_count: 5, difficulty: 46, tags: ["backcrosses"]},
    {name: "shoulders", props_count: 5, difficulty: 55, tags: ["shoulders"]},
    {name: "overheads -> backrosses -> overheads", props_count: 5, difficulty: 58, tags: ["overheads", "backcrosses"]},

]
if (typeof module !== 'undefined' && typeof module.exports !== 'undefined') {
    module.exports = BALLS_TRICKS;
}
