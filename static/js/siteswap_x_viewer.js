// Generic Siteswap-X viewer for rendering formatted siteswap-x notation
// Usage: siteswapXViewer(pattern, numberSize)
// Returns HTML string
function siteswapXViewer(pattern, numberSize = '1.5em') {
    // Parse pattern: e.g. '53{U/P} 4{S}'
    // Each throw: digit/letter, optional {mod/catch_mod}, preserve whitespace
    const tokenRe = /([0-9a-zA-Z])(?:\{([^}/]*)(?:\/([^}]*)?)?\})?|\s+/g;
    let html = '<span class="siteswap-x-visual" style="font-size:' + numberSize + '; vertical-align:middle;">';
    let match;
    while ((match = tokenRe.exec(pattern)) !== null) {
        if (match[0].trim() === '') {
            // Whitespace: preserve as a span for spacing
            html += '<span class="siteswap-x-space">&nbsp;</span>';
            continue;
        }
        const number = match[1];
        const mod = match[2] || '';
        const catchMod = match[3] || '';
        html += '<span class="siteswap-x-throw">';
        html += '<span class="siteswap-x-throw-mod">' + (mod || '\u00A0') + '</span>';
        html += '<span class="siteswap-x-number">' + number + '</span>';
        if (catchMod) {
            html += '<span class="siteswap-x-catch-mod">' + catchMod + '</span>';
        }
        html += '</span>';
    }
    html += '</span>';
    return html;
}
