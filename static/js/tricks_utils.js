// Format a siteswap-x string with throw/catch modifiers as HTML
// Example: 5{a/b} -> 5 with 'a' above in red, 'b' below in blue
function formatSiteswapX(siteswap) {
    if (!siteswap) return '';
    // Match throw (multi-char), optional {mod} or {mod1/mod2}
    // e.g. 10c{N}, 3{a/b}, 975{foo/bar}
    // Also preserve non-matching text (arrows, spaces, etc.)
    const regex = /(\w+)(\{([^{}\/]*)?(?:\/([^{}]*)?)?\})?/g;
    let result = '';
    let lastIndex = 0;
    let match;
    while ((match = regex.exec(siteswap)) !== null) {
        // Add any text between matches (arrows, spaces, etc.)
        if (match.index > lastIndex) {
            result += siteswap.slice(lastIndex, match.index);
        }
        const throwVal = match[1];
        const hasMod = !!match[2];
        let throwMod = '', catchMod = '';
        if (hasMod) {
            if (match[4]) {
                throwMod = match[3] || '';
                catchMod = match[4] || '';
            } else {
                throwMod = match[3] || '';
            }
        }
        result += `<span class="siteswap-x-digit-container">`;
        if (throwMod) result += `<span class="siteswap-x-throw-mod">${throwMod}</span>`;
        result += `<span class="siteswap-x-digit">${throwVal}</span>`;
        if (catchMod) result += `<span class="siteswap-x-catch-mod">${catchMod}</span>`;
        result += `</span>`;
        lastIndex = regex.lastIndex;
    }
    // Add any trailing text
    if (lastIndex < siteswap.length) {
        result += siteswap.slice(lastIndex);
    }
    return result;
}
window.formatSiteswapX = formatSiteswapX;
// Generalized function to toggle all trick names/siteswap-x in a given container
// containerSelector: CSS selector for the container holding the tricks (e.g., '#all_tricks')
// checkboxId: ID of the controlling checkbox (e.g., 'toggle-alltricks-siteswap-x-checkbox')
function toggleAllTricksSiteswapX(containerSelector = '#all_tricks', checkboxId = 'toggle-alltricks-siteswap-x-checkbox') {
    var checked = document.getElementById(checkboxId)?.checked;
    var tricksGrid = document.querySelector(containerSelector);
    if (!tricksGrid) return;
    var trickNames = tricksGrid.querySelectorAll('.trick-name');
    var siteswapXs = tricksGrid.querySelectorAll('.trick-siteswap-x');
    for (var i = 0; i < trickNames.length; i++) {
        var siteswapText = siteswapXs[i] ? siteswapXs[i].textContent.trim() : '';
        var hasSiteswap = siteswapText !== '' && siteswapText.toLowerCase() !== 'none';
        if (checked && hasSiteswap) {
            trickNames[i].style.display = 'none';
            siteswapXs[i].style.display = '';
        } else {
            trickNames[i].style.display = '';
            if (siteswapXs[i]) siteswapXs[i].style.display = 'none';
        }
    }
}
// Make available globally
window.toggleAllTricksSiteswapX = toggleAllTricksSiteswapX;
function filterTricks(tricks, minProps, maxProps, minDifficulty, maxDifficulty, excludedTags, maxThrow = null) {
    // Filter tricks based on criteria
    const filteredTricks = tricks.filter(trick => {
        const propsInRange = trick.props_count >= minProps && trick.props_count <= maxProps;
        const difficultyInRange = trick.difficulty >= minDifficulty && trick.difficulty <= maxDifficulty;
        const hasExcludedTag = excludedTags.length > 0 && trick.tags.some(tag => excludedTags.includes(tag));
        const withinThrow = (maxThrow === null || maxThrow === undefined) || ((trick.max_throw !== null && trick.max_throw !== undefined) && (trick.max_throw <= maxThrow));
        return propsInRange && difficultyInRange && !hasExcludedTag && withinThrow;
    });

    return filteredTricks;
}

function groupTricksByPropsCount(tricks) {
    const groupedTricks = {};
    tricks.forEach(trick => {
        if (!groupedTricks[trick.props_count]) {
            groupedTricks[trick.props_count] = [];
        }
        groupedTricks[trick.props_count].push(trick);
    });
    return groupedTricks;
}

async function fetchTricks({
    propType = null,
    minProps = null,
    maxProps = null,
    minDifficulty = null,
    maxDifficulty = null,
    excludedTags = null,
    maxThrow = null
} = {}) {
    try {
        // Create request body with only non-null values
        const requestBody = {};
        if (propType !== null) requestBody.prop_type = propType;
        if (minProps !== null) requestBody.min_props = minProps;
        if (maxProps !== null) requestBody.max_props = maxProps;
        if (minDifficulty !== null) requestBody.min_difficulty = minDifficulty;
        if (maxDifficulty !== null) requestBody.max_difficulty = maxDifficulty;
        if (excludedTags !== null) requestBody.exclude_tags = excludedTags;
        if (maxThrow !== null) requestBody.max_throw = maxThrow;

        const response = await fetch('/api/fetch_tricks', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error fetching tricks:', error);
        throw error;
    }
}

function fetchRandomTrickForDifficulty(difficulty) {
    const tricks = fetchTricks({ minDifficulty: difficulty, maxDifficulty: difficulty });
    return tricks[Math.floor(Math.random() * tricks.length)];
}

function getRandomTrickForDifficulty(tricks, difficulty, minProps, maxProps, excludedTags, maxThrow = null) {
	const filteredTricks = filterTricks(tricks, minProps, maxProps, difficulty, difficulty, excludedTags, maxThrow);
	return filteredTricks[Math.floor(Math.random() * filteredTricks.length)];
}

function filterTricksIncludeTags(tricks, includeTags) {
    if (!includeTags || includeTags.length === 0) {
        return tricks;
    }
    
    return tricks.filter(trick => {
        // Check if trick has all the required tags
        return includeTags.every(tag => trick.tags.includes(tag));
    });
}

function trickExists(tricks, name, propsCount) {
    return tricks.some(trick => 
        trick.name.toLowerCase() === name.toLowerCase() && 
        trick.props_count === propsCount
    );
}
