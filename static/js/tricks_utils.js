function filterTricks(tricks, minProps, maxProps, minDifficulty, maxDifficulty, excludedTags) {
    // Filter tricks based on criteria
    const filteredTricks = tricks.filter(trick => {
        const propsInRange = trick.props_count >= minProps && trick.props_count <= maxProps;
        const difficultyInRange = trick.difficulty >= minDifficulty && trick.difficulty <= maxDifficulty;
        const hasExcludedTag = excludedTags.length > 0 && trick.tags.some(tag => excludedTags.includes(tag));
        return propsInRange && difficultyInRange && !hasExcludedTag;
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
