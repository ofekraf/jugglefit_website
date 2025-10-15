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

// Render tricks into the #all_tricks container grouped by props_count
function renderTricks(tricks) {
    const container = document.getElementById('all_tricks');
    if (!container) return;
    container.innerHTML = '';

    if (!Array.isArray(tricks) || tricks.length === 0) {
        const empty = document.createElement('div');
        empty.className = 'no-tricks';
        empty.textContent = 'No tricks available for the selected filters.';
        container.appendChild(empty);
        return;
    }

    const grouped = groupTricksByPropsCount(tricks);
    // Sort prop counts ascending
    const counts = Object.keys(grouped).map(k => Number(k)).sort((a,b) => a-b);
    counts.forEach(count => {
        const groupEl = document.createElement('div');
        groupEl.className = 'trick-group';
        const header = document.createElement('div');
        header.className = 'trick-group-header';
        header.textContent = `${count} ${count === 1 ? 'prop' : 'props'}`;
        groupEl.appendChild(header);

        const list = document.createElement('div');
        list.className = 'trick-group-list';
        grouped[count].forEach(trick => {
            // Use same structure as route display's trick frame so comments and styling match
            const frame = document.createElement('div');
            frame.className = 'prop-details-frame trick-item';
            frame.setAttribute('data-trick-name', trick.name);
            frame.setAttribute('data-props-count', trick.props_count);

            const trickContent = document.createElement('div');
            trickContent.className = 'trick-content';

            const trickMain = document.createElement('div');
            trickMain.className = 'trick-main';

            const nameSpan = document.createElement('span');
            nameSpan.className = 'trick-name';
            nameSpan.textContent = trick.name;
            trickMain.appendChild(nameSpan);

            if (trick.comment) {
                const commentSpan = document.createElement('span');
                commentSpan.className = 'trick-comment';
                commentSpan.textContent = ` [${trick.comment}]`;
                trickMain.appendChild(commentSpan);
            }

            trickContent.appendChild(trickMain);

            // Add button (placed where remove button is in route display)
            const addBtn = document.createElement('button');
            addBtn.type = 'button';
            addBtn.className = 'add-trick';
            addBtn.textContent = 'Add';
            addBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                if (window && typeof window.addTrickToRoute === 'function') {
                    window.addTrickToRoute(trick);
                } else if (typeof addTrickToRoute === 'function') {
                    addTrickToRoute(trick);
                } else {
                    console.warn('addTrickToRoute is not available');
                }
            });

            trickContent.appendChild(addBtn);

            frame.appendChild(trickContent);
            list.appendChild(frame);
        });

        groupEl.appendChild(list);
        container.appendChild(groupEl);
    });
}

// Apply current UI filters to allTricks and render
function updateSearchTricks() {
    try {
        const minProps = parseInt(document.getElementById('min-props-input').value) || 0;
        const maxProps = parseInt(document.getElementById('max-props-input').value) || 999;
        const minDifficulty = parseInt(document.getElementById('min-difficulty-input').value) || 0;
        const maxDifficulty = parseInt(document.getElementById('max-difficulty-input').value) || 100;
        const excludedTags = Array.from(document.querySelectorAll('input[name="exclude_tags"]:checked')).map(cb => cb.value);
        const maxThrowElem = document.getElementById('max-throw-enabled');
        const maxThrow = maxThrowElem && maxThrowElem.checked ? parseInt(document.getElementById('max-throw-input').value) : null;

        // Do NOT auto-fetch here. Fetching should only happen explicitly on prop selection
        // (prop change handler calls fetchTricks and populates window.allTricks).
        if (!Array.isArray(window.allTricks) || window.allTricks.length === 0) {
            // No tricks cached for the selected prop yet — render empty state and return.
            renderTricks([]);
            return;
        }

        const filtered = filterTricks(window.allTricks || [], minProps, maxProps, minDifficulty, maxDifficulty, excludedTags, maxThrow);
        renderTricks(filtered);
    } catch (e) {
        console.error('updateSearchTricks error:', e);
    }
}
