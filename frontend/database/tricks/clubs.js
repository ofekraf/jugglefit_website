const CLUBS_TRICKS = [
    // BASE PATTERNS
    // 4 props base patterns
    {name: "sync fountain -> async fountain", difficulty: 20, props_count: 4, tags: ["sync base pattern", "async base pattern"], comment: "transition: (5x,4)"},
    {name: "sync fountain -> 2up 360 -> sync fountain", difficulty: 22, props_count: 4, tags: ["360 spin"]},
    {name: "20c flats", difficulty: 30, props_count: 4, tags: ["flats"]},
    // 5 props base patterns
    {name: "50c isolated cascade", props_count: 5, difficulty: 37, tags: ["isolated", "async base pattern"]},
    // 6 props base patterns
    {name: "fountain", props_count: 6, difficulty: 55, tags: ["any base pattern"]},
    {name: "6c sync fountain", props_count: 6, difficulty: 46, tags: ["sync base pattern"]},
    // 7 props base patterns
    {name: "7c cascade", props_count: 7, difficulty: 54, tags: ["async base pattern"]},
    {name: "cascade", props_count: 7, difficulty: 70, tags: ["async base pattern"]},
    // SPINS
    // 3 props spins
    {name: "cascade -> 3up 360 -> cascade", props_count: 3, difficulty: 20, tags: ["360 spin"]},
    {name: "531 -> 75300 3up 360 -> cascade", props_count: 3, difficulty: 27, tags: ["360 spin", "async siteswap"]},
    {name: "441 -> 66300 3up 360 -> 441", props_count: 3, difficulty: 29, tags: ["360 spin", "async siteswap"]},
    {name: "cascade -> 1up 720 -> flats", props_count: 3, difficulty: 28, tags: ["720 spin"]},
    {name: "9440022 3up 2-stage -> cascade", props_count: 3, difficulty: 34, tags: ["multi stage"]},
    {name: "backrosses -> 3up 360 in backrosses -> backrosses", props_count: 3, difficulty: 42, tags: ["360 spin", "backcrosses"]},
    {name: "3up 360 -> 1up 360 -> 3up 360", props_count: 3, difficulty: 34, tags: ["360 spin"]},
    // 4 props spins
    {name: "sync fountain -> (8,8)(4,4)(0,0) 4up 360 -> sync fountain", props_count: 4, difficulty: 36, tags: ["360 spin", "sync siteswap"]},
    {name: "async fountain -> 955500 4up 360 -> async fountain", props_count: 4, difficulty: 38, tags: ["360 spin", "async siteswap"]},
    {name: "async fountain -> 6822622 2up 2-stage -> async fountain", props_count: 4, difficulty: 35, tags: ["multi stage", "async siteswap"]},
    // 5 props spins
    {name: "cascade -> 5up 180 -> cascade", props_count: 5, difficulty: 44, tags: ["180 spin"]},
    {name: "cascade -> 97522 3up 360 -> cascade", props_count: 5, difficulty: 40, tags: ["360 spin", "async siteswap"]},
    {name: "cascade -> b66227722 3up 2-stage -> cascade", props_count: 5, difficulty: 52, tags: ["multi stage", "async siteswap"]},
    {name: "6c 663 -> 88522 3up 360 -> 6c 663", props_count: 5, difficulty: 50, tags: ["360 spin", "async siteswap"]},
    {name: "744 -> 96622 3up 360 -> singles cascade", props_count: 5, difficulty: 46, tags: ["360 spin", "async siteswap", "spin control"]},
    // 6 props spins
    {name: "6c async fountain -> 4up 360 -> ANY", props_count: 6, difficulty: 75, tags: ["360 spin"]},
    // 7 props spins
    {name: "7c cascade -> 5up 720 -> 7c cascade", props_count: 7, difficulty: 100, tags: ["720 spin"]},
    // SITESWAPS
    // 3 props siteswaps
    {name: "24c 531", props_count: 3, difficulty: 13, tags: ["async siteswap"]},
    {name: "36c 801", props_count: 3, difficulty: 42, tags: ["async siteswap"], comment: "Entrance: 46"},
    {name: "20c 45123", props_count: 3, difficulty: 16, tags: ["async siteswap"]},
    {name: "30c 44133", props_count: 3, difficulty: 14, tags: ["async siteswap"]},
    // 4 props siteswaps
    {name: "18c 552", props_count: 4, difficulty: 22, tags: ["async siteswap"]},
    {name: "18c 633", props_count: 4, difficulty: 27, tags: ["async siteswap"]},
    {name: "18c 741", props_count: 4, difficulty: 28, tags: ["async siteswap"], comment: "entrance: 5"},
    {name: "18c 534, single 5, double 3", props_count: 4, difficulty: 45, tags: ["async siteswap", "spin control"]},
    {name: "20c 55550", props_count: 4, difficulty: 25, tags: ["async siteswap"]},
    {name: "20c 56450", props_count: 4, difficulty: 28, tags: ["async siteswap"]},
    // 5 props siteswaps
    {name: "30c 771", props_count: 5, difficulty: 45, tags: ["async siteswap"], comment: "entrance: 75"},
    {name: "30c 672", props_count: 5, difficulty: 47, tags: ["async siteswap"], comment: "entrance 6"},
    {name: "30c 744 isolated", props_count: 5, difficulty: 42, tags: ["async siteswap", "isolated"]},
    {name: "cascade -> 5c 66751 -> cascade", props_count: 5, difficulty: 33, tags: ["async siteswap"]},
    {name: "10c 94444", props_count: 5, difficulty: 37, tags: ["async siteswap"]},
    {name: "20c 94633", props_count: 5, difficulty: 52, tags: ["async siteswap"]},
    {name: "cascade -> 10c 77335 -> cascade", props_count: 5, difficulty: 40, tags: ["async siteswap"]},
    {name: "cascade -> 10c 74464 -> cascade", props_count: 5, difficulty: 37, tags: ["async siteswap"]},
    {name: "30c 84445", props_count: 5, difficulty: 50, tags: ["async siteswap"]},
    {name: "14c 7575164", props_count: 5, difficulty: 43, tags: ["async siteswap"]},
    // 6 props siteswaps
    {name: "6c 756", props_count: 6, difficulty: 46, tags: ["async siteswap"]},
    {name: "6c fountain -> 6c 864 -> 6c fountain", props_count: 6, difficulty: 57, tags: ["async siteswap"]},
    {name: "10c 77781", props_count: 6, difficulty: 82, tags: ["async siteswap"], comment: "entrance: 7"},
    // 7 props siteswaps
    {name: "cascade -> 3c 966", props_count: 7, difficulty: 75, tags: ["async siteswap"]},
    // BODY THROWS
    {name: "20c backrosses", props_count: 3, difficulty: 20, tags: ["backcrosses"]},
    {name: "under the leg throws", props_count: 3, difficulty: 16, tags: ["under legs"]},
    {name: "lazies", props_count: 3, difficulty: 14, tags: ["lazies"]},
    {name: "24c 423, shoulder throw 4", difficulty: 23, props_count: 3, tags: ["shoulders", "async siteswap"]},
    {name: "12c 423, shoulder throw lazy 4", props_count: 3, difficulty: 25, tags: ["shoulders", "lazies", "async siteswap"]},
    {name: "lazies -> backrosses", props_count: 3, difficulty: 20, tags: ["lazies", "backcrosses"]},
    {name: "4c bacrosses singles -> 4c backrosses doubles -> 4c backrosses triples ", props_count: 3, difficulty: 22, tags: ["backcrosses", "spin control"]},
    {name: "overheads", props_count: 4, difficulty: 32, tags: ["overheads"]},
    {name: "534, backross 5", props_count: 4, difficulty: 35, tags: ["backcrosses", "async siteswap"]},
    {name: "552 -> 6c 552, backrosses 5's -> 552", props_count: 4, difficulty: 37, tags: ["backcrosses", "async siteswap"]},
    {name: "5c cascade -> 4c 7733, backrosses 3's -> cascade", props_count: 5, difficulty: 55, tags: ["backcrosses", "async siteswap"]},
    {name: "20c triples backrosses", props_count: 5, difficulty: 48, tags: ["backcrosses"]},
    {name: "cascade -> 5c 94444, lazies 4's -> cascade", props_count: 5, difficulty: 58, tags: ["lazies", "async siteswap"]},
    {name: "6c ANY -> 4c 9555, backrosses 5's -> 6c ANY", props_count: 6, difficulty: 73, tags: ["backcrosses", "async siteswap"]},
    // SPIN CONTROL
    {name: "20c reverse spin singles", props_count: 3, difficulty: 14, tags: ["spin control"]},
    {name: "10c helicopters", props_count: 3, difficulty: 20, tags: ["spin control"]},
    {name: "30c flats", props_count: 3, difficulty: 15, tags: ["spin control", "flats"]},
    {name: "12c triples", props_count: 3, difficulty: 15, tags: ["spin control"]},
    {name: "10c slapbacks", props_count: 3, difficulty: 18, tags: ["spin control"]},
    {name: "10c singles -> 10c doubles  -> 10c triples", props_count: 3, difficulty: 18, tags: ["spin control"]},
    {name: "flat flatfronts -> 3c 441 double flatfronts 4's -> single flatfronts", props_count: 3, difficulty: 25, tags: ["spin control", "async siteswap"]},
    {name: "18c 534 singles", props_count: 4, difficulty: 26, tags: ["spin control", "async siteswap"]},
    {name: "18c 633 singles", props_count: 4, difficulty: 40, tags: ["spin control", "async siteswap"]},
    {name: "534, flat 4", props_count: 4, difficulty: 27, tags: ["spin control", "async siteswap", "flats"]},
    {name: "4c singles -> 4c doubles -> 4c triples -> 4c singles", props_count: 4, difficulty: 26, tags: ["spin control"]},
    {name: "534, flatfront 5", props_count: 4, difficulty: 29, tags: ["spin control", "async siteswap"]},
    {name: "10c singles", props_count: 5, difficulty: 28, tags: ["spin control"]},
    {name: "10c triples", props_count: 5, difficulty: 30, tags: ["spin control"]},
    {name: "6c triples -> 6c singles", props_count: 5, difficulty: 30, tags: ["spin control"]},
    {name: "cascade -> 12c 744, flat 4's", props_count: 5, difficulty: 48, tags: ["spin control", "async siteswap", "flats"]},
    {name: "6c singles", props_count: 5, difficulty: 51, tags: ["spin control"]},
    {name: "6c fountain -> 6c flats", props_count: 6, difficulty: 60, tags: ["spin control", "flats"]},
];
if (typeof module !== 'undefined' && typeof module.exports !== 'undefined') {
    module.exports = CLUBS_TRICKS;
} 