// Generic Siteswap-X viewer for rendering formatted siteswap-x notation
// Usage: siteswapXViewer(pattern, numberSize)
// Returns HTML string
function siteswapXViewer(pattern, numberSize = '1.5em') {
    // Parse pattern: e.g. '53{U/P} 4{S}'
    // Each throw: digit/letter, optional {mod/catch_mod}, preserve whitespace
    // Split pattern by whitespace, process each word
    const wordRe = /\S+/g;
    let html = '<span class="siteswap-x-visual" style="font-size:' + numberSize + '; vertical-align:middle;">';
    let lastIndex = 0;
    let wordMatch;
    let prevPlain = false;
    while ((wordMatch = wordRe.exec(pattern)) !== null) {
        // Add any whitespace before this word
        if (wordMatch.index > lastIndex) {
            if (prevPlain) {
                html += ' ';
            } else {
                html += '<span class="siteswap-x-space">&nbsp;</span>';
            }
        }
        const word = wordMatch[0];
        // Check if word contains any modifiers
        const tokenRe = /([0-9a-zA-Z])(?:\{([^}/]*)(?:\/([^}]*)?)?\})?/g;
        let hasModifier = false;
        let tokens = [];
        let tokenMatch;
        while ((tokenMatch = tokenRe.exec(word)) !== null) {
            const mod = tokenMatch[2] || '';
            const catchMod = tokenMatch[3] || '';
            if (mod || catchMod) hasModifier = true;
            tokens.push(tokenMatch);
        }
        if (!hasModifier) {
            // No modifiers in this word: render as plain text
            html += word;
            prevPlain = true;
        } else {
            // Render each token in the word
            tokens.forEach(tokenMatch => {
                const number = tokenMatch[1];
                const mod = tokenMatch[2] || '';
                const catchMod = tokenMatch[3] || '';
                html += '<span class="siteswap-x-throw">';
                html += '<span class="siteswap-x-throw-mod">' + (mod || '\u00A0') + '</span>';
                html += '<span class="siteswap-x-number">' + number + '</span>';
                if (catchMod) {
                    html += '<span class="siteswap-x-catch-mod">' + catchMod + '</span>';
                }
                html += '</span>';
            });
            prevPlain = false;
        }
        lastIndex = wordRe.lastIndex;
    }
    html += '</span>';
    return html;
}
