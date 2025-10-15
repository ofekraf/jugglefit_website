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
            // Try to read response text for better debugging
            let respText = '';
            try { respText = await response.text(); } catch (e) { respText = '<unable to read response text>'; }
            console.error('fetchTricks response not ok:', response.status, respText);
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error fetching tricks:', error);
        throw error;
    }
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
