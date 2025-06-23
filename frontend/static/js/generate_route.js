import {
    MIN_TRICK_PROPS_COUNT,
    MAX_TRICK_PROPS_COUNT,
    DEFAULT_MIN_TRICK_PROPS_COUNT,
    DEFAULT_MAX_TRICK_PROPS_COUNT,
    MIN_TRICK_DIFFICULTY,
    MAX_TRICK_DIFFICULTY,
    DEFAULT_MIN_TRICK_DIFFICULTY,
    DEFAULT_MAX_TRICK_DIFFICULTY,
    DEFAULT_FINALS_ROUTE_LENGTH,
    DEFAULT_FINALS_ROUTE_DURATION
} from '../globals/globals.js';

import { filterTricks } from './tricks_utils.js';

/**
 * @returns {Object} Generated route with selected tricks
 * @throws {Error} If not enough tricks match the criteria
 */
function generateRoute({
    tricks,
    minProps = DEFAULT_MIN_TRICK_PROPS_COUNT,
    maxProps = DEFAULT_MAX_TRICK_PROPS_COUNT,
    minDifficulty = DEFAULT_MIN_TRICK_DIFFICULTY,
    maxDifficulty = DEFAULT_MAX_TRICK_DIFFICULTY,
    routeLength = DEFAULT_FINALS_ROUTE_LENGTH,
    excludeTags = [],
    name = '',
    durationSeconds = DEFAULT_FINALS_ROUTE_DURATION
} = {}) {
    // Input validation
    if (!tricks || !Array.isArray(tricks)) {
        throw new Error('Tricks array must be provided');
    }

    // Validate and clamp input values to their constraints
    minProps = Math.max(MIN_TRICK_PROPS_COUNT, Math.min(maxProps, minProps));
    maxProps = Math.min(MAX_TRICK_PROPS_COUNT, Math.max(minProps, maxProps));
    minDifficulty = Math.max(MIN_TRICK_DIFFICULTY, Math.min(maxDifficulty, minDifficulty));
    maxDifficulty = Math.min(MAX_TRICK_DIFFICULTY, Math.max(minDifficulty, maxDifficulty));

    // Get filtered tricks
    const relevantTricks = filterTricks(
        tricks,
        minProps,
        maxProps,
        minDifficulty,
        maxDifficulty,
        excludeTags
    );

    if (relevantTricks.length < routeLength) {
        throw new Error(
            `Not enough tricks found matching the criteria. Found ${relevantTricks.length} tricks, but need ${routeLength}. ` +
            `Try adjusting the difficulty range (${minDifficulty}-${maxDifficulty}) or props range (${minProps}-${maxProps}).`
        );
    }

    // Randomly shuffle the relevant tricks
    const shuffledTricks = [...relevantTricks]
        .sort(() => Math.random() - 0.5);

    // Take first routeLength tricks and sort by difficulty and props count
    const selectedTricks = shuffledTricks
        .slice(0, routeLength)
        .sort((a, b) => {
            // Sort first by props_count, then by difficulty
            if (a.props_count !== b.props_count) {
                return a.props_count - b.props_count;
            }
            return a.difficulty - b.difficulty;
        });

    return {
        name,
        prop,
        tricks: selectedTricks,
        durationSeconds
    };
}

export { generateRoute }; 