function parse_siteswap_x(siteswap_x) {
	// Matches: number, {modifier}
	const regex = /(\d|[a-z])(?:\{([^}]*)\})?/gi;
	let match;
	const result = [];
	while ((match = regex.exec(siteswap_x)) !== null) {
		result.push({
			number: match[1],
			mod: match[2] || ''
		});
	}
	return result;
}

// Render a Siteswap X string as HTML (returns a string)
function render_siteswap_x(pattern, numberSize = '1em') {
    const parsed = parse_siteswap_x(pattern);
    return parsed.map(item => `
        <span class="siteswap-x-throw">
            <span class="siteswap-x-throw-mod" style="font-size:calc(${numberSize} * 0.5);">${item.mod ? item.mod : '\u00A0'}</span>
            <span class="siteswap-x-number" style="font-size:${numberSize};">${item.number}</span>
        </span>
    `).join('');
}