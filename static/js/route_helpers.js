// Exports helpers for route pages: fetchTricks, updatePropsSliderRange, updateRelevantTags, setMaxThrowForProp

export async function fetchTricks(filters = {}) {
    try {
        // Prevent multiple concurrent fetches for the same prop
        const propType = filters.prop_type || filters.propType || filters.prop || null;
        if (propType && window._currentFetchPromise && window._currentFetchProp === propType) {
            console.log('fetchTricks: returning existing promise for', propType);
            return await window._currentFetchPromise;
        }
        
        // Map common camelCase client keys to the server-expected snake_case keys
        const payload = {
            prop_type: filters.prop_type || filters.propType || filters.prop || null,
            min_props: typeof filters.minProps !== 'undefined' ? filters.minProps : filters.min_props,
            max_props: typeof filters.maxProps !== 'undefined' ? filters.maxProps : filters.max_props,
            min_difficulty: typeof filters.minDifficulty !== 'undefined' ? filters.minDifficulty : filters.min_difficulty,
            max_difficulty: typeof filters.maxDifficulty !== 'undefined' ? filters.maxDifficulty : filters.max_difficulty,
            exclude_tags: Array.isArray(filters.exclude_tags) ? filters.exclude_tags : (Array.isArray(filters.excludeTags) ? filters.excludeTags : (filters.exclude_tags || [])),
            limit: typeof filters.limit !== 'undefined' ? filters.limit : null,
            max_throw: typeof filters.maxThrow !== 'undefined' ? filters.maxThrow : (typeof filters.max_throw !== 'undefined' ? filters.max_throw : null),
        };

        // Remove null/undefined keys to keep payload small
        Object.keys(payload).forEach(k => {
            if (payload[k] === null || typeof payload[k] === 'undefined') delete payload[k];
        });

        // Server requires prop_type; if missing, skip the request and return empty list
        if (!payload.prop_type || String(payload.prop_type).trim() === '') {
            console.warn('fetchTricks aborted: prop_type missing in payload, payload:', payload);
            return [];
        }

        console.log('fetchTricks: starting fetch for', payload.prop_type);
        
        // Store current fetch promise to prevent duplicates
        window._currentFetchProp = payload.prop_type;
        window._currentFetchPromise = (async () => {
            try {
                const resp = await fetch('/api/fetch_tricks', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                if (!resp.ok) {
                    let bodyText = '';
                    try { bodyText = await resp.text(); } catch (e) {}
                    const err = new Error('fetchTricks API error ' + resp.status + ': ' + bodyText);
                    err.status = resp.status;
                    err.body = bodyText;
                    throw err;
                }

                const data = await resp.json();
                const result = Array.isArray(data) ? data : (data.tricks || data || []);
                console.log('fetchTricks: completed for', payload.prop_type, 'got', result.length, 'tricks');
                return result;
            } finally {
                // Clear the current fetch promise
                if (window._currentFetchProp === payload.prop_type) {
                    window._currentFetchPromise = null;
                    window._currentFetchProp = null;
                }
            }
        })();
        
        return await window._currentFetchPromise;
    } catch (e) {
        console.error('fetchTricks failed', e);
        throw e;
    }
}

export function updateCustomTrickPropsRange(minProps, maxProps) {
    try {
        const customTrickPropsSlider = document.getElementById('custom_trick_props');
        const customTrickPropsValue = document.getElementById('custom_trick_props_value');
        
        if (customTrickPropsSlider) {
            // Update slider range
            customTrickPropsSlider.min = minProps;
            customTrickPropsSlider.max = maxProps;
            
            // Adjust current value if it's outside the new range
            const currentValue = parseInt(customTrickPropsSlider.value);
            if (currentValue < minProps) {
                customTrickPropsSlider.value = minProps;
            } else if (currentValue > maxProps) {
                customTrickPropsSlider.value = maxProps;
            }
            
            // Update displayed value
            if (customTrickPropsValue) {
                customTrickPropsValue.textContent = customTrickPropsSlider.value;
            }
        }
    } catch (e) {
        console.error('updateCustomTrickPropsRange failed', e);
    }
}

export function updatePropsSliderRange(minProps, maxProps) {
    try {
        const propsSlider = document.getElementById('props-slider');
        const propsRange = document.getElementById('props-range');
        const propsMinInput = document.getElementById('min-props-input');
        const propsMaxInput = document.getElementById('max-props-input');
        if (!propsSlider) return;
        if (propsSlider.noUiSlider) {
            propsSlider.noUiSlider.updateOptions({
                range: { min: minProps, max: maxProps },
                start: [minProps, maxProps]
            });
            if (propsRange) propsRange.textContent = `Min: ${minProps}, Max: ${maxProps}`;
            if (propsMinInput) propsMinInput.value = minProps;
            if (propsMaxInput) propsMaxInput.value = maxProps;
        } else if (typeof noUiSlider !== 'undefined') {
            noUiSlider.create(propsSlider, {
                start: [minProps, maxProps],
                connect: true,
                range: { 'min': minProps, 'max': maxProps },
                format: { to: v => Math.round(v), from: v => parseFloat(v) }
            });
            propsSlider.noUiSlider.on('update', function(values) {
                if (propsRange) propsRange.textContent = `Min: ${values[0]}, Max: ${values[1]}`;
                if (propsMinInput) propsMinInput.value = Math.round(values[0]);
                if (propsMaxInput) propsMaxInput.value = Math.round(values[1]);
            });
        }
    } catch (e) {
        console.error('updatePropsSliderRange failed', e);
        throw e;
    }
}

export function updateRelevantTags(relevantTagsOrPropSettings = [], naming = '') {
    try {
        const name_suffix = naming ? ('_' + naming) : '';
        let tagsArray = [];
        // Accept either a direct array of tags, or a propSettings object { relevant_tags: [...] }
        if (relevantTagsOrPropSettings && typeof relevantTagsOrPropSettings === 'object' && Array.isArray(relevantTagsOrPropSettings.relevant_tags)) {
            tagsArray = relevantTagsOrPropSettings.relevant_tags.map(t => String(t).toLowerCase());
        } else if (Array.isArray(relevantTagsOrPropSettings)) {
            tagsArray = relevantTagsOrPropSettings.map(t => String(t).toLowerCase());
        } else if (typeof relevantTagsOrPropSettings === 'string') {
            tagsArray = [relevantTagsOrPropSettings.toLowerCase()];
        }

        const containerId = 'exclude_tags' + name_suffix;
        const container = document.getElementById(containerId);
        if (!container) {
            console.warn('updateRelevantTags: container not found for id', containerId, '— will skip tag filtering');
            return;
        }
    const categories = container.querySelectorAll('.tag-category');
    // If no tags provided, show all categories (don't hide everything)
    if (!tagsArray || tagsArray.length === 0) {
        categories.forEach(cat => {
            cat.style.display = '';
            // Ensure individual tag containers are visible
            const tagCheckboxes = cat.querySelectorAll('input.tag-checkbox');
            tagCheckboxes.forEach(cb => { if (cb.parentElement) cb.parentElement.style.display = ''; });
            // Remove expanded state so behavior is natural
            const content = cat.querySelector('.tag-category-content') || cat.querySelector('[class*="tag-category-content"]');
            if (content) content.classList.remove('expanded');
        });
        return;
    }

    // Otherwise, for each category hide non-relevant tags, unhide relevant ones
    categories.forEach(cat => {
        let revealedCount = 0;
    // Only target the actual tag checkboxes (not the header category checkbox)
    const tagCheckboxes = cat.querySelectorAll('input.tag-checkbox');
        tagCheckboxes.forEach(cb => {
            const val = cb.value || cb.getAttribute('value') || '';
            const valLower = String(val).toLowerCase();
            const containerEl = cb.closest('.checkbox-container') || cb.parentElement;
            if (tagsArray.includes(valLower)) {
                if (containerEl) containerEl.style.display = '';
                revealedCount += 1;
            } else {
                if (containerEl) containerEl.style.display = 'none';
                try { cb.checked = false; } catch (e) {}
            }
        });

        if (revealedCount > 0) {
            cat.style.display = '';
            // Leave expansion state to the user (do not auto-expand)
            const content = cat.querySelector('.tag-category-content') || cat.querySelector('[class*="tag-category-content"]');
            if (content) content.classList.remove('expanded');
        } else {
            // No relevant tags in this category — hide the entire category
            cat.style.display = 'none';
        }
    });
    } catch (e) {
        console.error('updateRelevantTags failed', e);
        throw e;
    }
}

export function setMaxThrowForProp(propSettings = {}) {
    // Accept a number as maxThrow for compatibility
    let propMaxThrow;
    if (typeof propSettings === 'number') propMaxThrow = propSettings;
    else if (propSettings && typeof propSettings === 'object') propMaxThrow = propSettings.max_throw;
    else throw new Error('setMaxThrowForProp expects a number or an object with max_throw');
    try {
    // setMaxThrowForProp called
        const maxThrowSlider = document.getElementById('max-throw-slider');
        const maxThrowValue = document.getElementById('max-throw-value');
        const maxThrowInput = document.getElementById('max-throw-input');
        const maxThrowEnabledElem = document.getElementById('max-throw-enabled');
        const maxThrowContainer = document.getElementById('max-throw-input-container');
        if (!maxThrowSlider) {
            console.warn('setMaxThrowForProp: max-throw-slider element missing — skipping');
            return;
        }
        if (Number.isFinite(propMaxThrow)) {
            maxThrowSlider.min = 1;
            maxThrowSlider.max = propMaxThrow;
            maxThrowSlider.value = propMaxThrow;
            if (maxThrowValue) maxThrowValue.textContent = propMaxThrow;
            if (maxThrowEnabledElem && maxThrowEnabledElem.checked && maxThrowInput) {
                maxThrowInput.value = propMaxThrow;
                if (maxThrowContainer) {
                    maxThrowContainer.classList.add('show');
                    maxThrowContainer.classList.remove('hide');
                    try { maxThrowContainer.style.display = 'block'; } catch (e) {}
                }
            }
    // maxThrowContainer state
        } else {
            if (maxThrowValue) maxThrowValue.textContent = maxThrowSlider.value;
        }
    } catch (e) {
        console.error('setMaxThrowForProp failed', e);
    }
}

// Ensure max-throw UI handlers are bound. Exported so pages that import this module
// can call it and guarantee the binding happens (idempotent).
export function initMaxThrowBindings() {
    try {
        if (typeof window === 'undefined') return;
        if (window._maxThrowBindingsInit) return;
        window._maxThrowBindingsInit = true;

        // Delegate change handling for the checkbox to toggle the container and keep inputs in sync
        document.addEventListener('change', function(e) {
            try {
                const t = e.target;
                if (!t) return;
                if (t.id === 'max-throw-enabled') {
                    const container = document.getElementById('max-throw-input-container');
                    const slider = document.getElementById('max-throw-slider');
                    const input = document.getElementById('max-throw-input');
                    if (!container) return;
                    if (t.checked) {
                        container.classList.add('show'); container.classList.remove('hide');
                        try { container.style.display = 'block'; container.style.visibility = 'visible'; container.style.opacity = '1'; container.style.maxHeight = '1000px'; } catch(e){}
                        if (slider && input) input.value = slider.value;
                    } else {
                        container.classList.add('hide'); container.classList.remove('show');
                        try { container.style.display = 'none'; container.style.visibility = 'hidden'; container.style.opacity = '0'; container.style.maxHeight = '0'; } catch(e){}
                        if (input) input.value = '';
                    }
                }
            } catch (e) { /* swallow */ }
        });

        // Make sure label clicks also propagate a change event in case some browsers/markup
        // don't trigger it synchronously.
        document.addEventListener('click', function(e) {
            try {
                const t = e.target;
                if (!t) return;
                if (t.matches && t.matches('label[for="max-throw-enabled"]')) {
                    setTimeout(function() {
                        const cb = document.getElementById('max-throw-enabled');
                        if (cb) cb.dispatchEvent(new Event('change', { bubbles: true }));
                    }, 0);
                }
            } catch (e) {}
        });

        // Keep slider -> hidden input in sync
        document.addEventListener('input', function(e) {
            try {
                const t = e.target;
                if (!t) return;
                if (t.id === 'max-throw-slider') {
                    const valueEl = document.getElementById('max-throw-value');
                    const input = document.getElementById('max-throw-input');
                    const enabled = document.getElementById('max-throw-enabled');
                    if (valueEl) valueEl.textContent = t.value;
                    if (enabled && enabled.checked && input) input.value = t.value;
                }
            } catch (e) {}
        });
    } catch (e) {
        console.error('initMaxThrowBindings failed', e);
    }
}

// Export defaults for backwards compatibility under window if someone expects them
try {
    if (typeof window !== 'undefined') {
        window.routeHelpersLoaded = true;
        // Make functions directly available on window for macro compatibility
        window.updateRouteDisplay = updateRouteDisplay;
        window.addTrickToRoute = addTrickToRoute;
        window.removeTrick = removeTrick;
        window.updateCustomTrickPropsRange = updateCustomTrickPropsRange;
    }
} catch (e) {}

/**
 * Select a random trick appropriate for a target difficulty and constraints.
 * Returns a trick object from the provided allTricks array or null when none match.
 *
 * Parameters:
 * - allTricks: array of trick objects (each should have props_count, difficulty, name, tags[], max_throw)
 * - difficulty: target difficulty number (integer)
 * - minProps/maxProps: numeric props count bounds (inclusive)
 * - excludedTags: array of tag keys to exclude
 * - maxThrow: optional numeric maximum throw to filter tricks by their max_throw attribute
 */
// Prop selection functionality
// Route display and manipulation functionality
export function updateRouteDisplay() {
    console.log('updateRouteDisplay called, currentRoute tricks:', window.currentRoute ? window.currentRoute.tricks.length : 'no currentRoute');
    
    const routeSections = document.getElementById('route-sections');
    if (!routeSections || !window.currentRoute) {
        console.log('Missing routeSections element or currentRoute');
        return;
    }
    
    routeSections.innerHTML = '';

    let currentPropsCount = null;
    let currentSection = null;
    let trickCounter = 1;

    window.currentRoute.tricks.forEach((trick, index) => {
        // Check if we need to create a new section
        if (currentPropsCount !== trick.props_count || 
            (index > 0 && window.currentRoute.tricks[index - 1].props_count !== trick.props_count)) {
            // Close previous section if it exists
            if (currentSection) {
                currentSection.querySelector('.trick-container').appendChild(document.createElement('div'));
            }

            // Create new section
            const section = document.createElement('div');
            section.className = 'prop-section';
            section.setAttribute('data-props-count', trick.props_count);
            
            const colorBar = document.createElement('div');
            colorBar.className = 'prop-color-bar';
            colorBar.setAttribute('data-props', trick.props_count);
            colorBar.setAttribute('data-prop-type', window.currentRoute.prop);
            colorBar.setAttribute('draggable', 'true');
            
            const propCount = document.createElement('div');
            propCount.className = 'prop-count';
            
            const propCountText = document.createElement('div');
            propCountText.className = 'prop-count-text';
            propCountText.textContent = trick.props_count;
            
            propCount.appendChild(propCountText);
            colorBar.appendChild(propCount);
            section.appendChild(colorBar);
            
            const trickContainer = document.createElement('div');
            trickContainer.className = 'trick-container';
            trickContainer.setAttribute('data-props-count', trick.props_count);
            
            section.appendChild(trickContainer);
            routeSections.appendChild(section);
            
            // Add drag and drop event listeners for the color bar
            colorBar.addEventListener('dragstart', handleSectionDragStart);
            colorBar.addEventListener('dragover', handleSectionDragOver);
            colorBar.addEventListener('drop', handleSectionDrop);
            colorBar.addEventListener('dragend', handleSectionDragEnd);
            
            currentSection = section;
            currentPropsCount = trick.props_count;
        }

        // Create trick frame using shared helper
        const frame = document.createElement('div');
        frame.className = 'prop-details-frame';
        frame.setAttribute('draggable', 'true');
        frame.setAttribute('data-trick-name', trick.name);

        const trickContent = document.createElement('div');
        trickContent.className = 'trick-content';

        // Use shared CreateTrickContainer to build consistent inner DOM
        const container = window.CreateTrickContainer ? window.CreateTrickContainer(trick.name, trick.comment || '', trick.siteswap_x || '', {
            onNameBlur: (newName) => { trick.name = newName; frame.setAttribute('data-trick-name', newName); },
            onCommentBlur: (newComment) => { trick.comment = newComment; },
            addCheckbox: true
        }) : createFallbackTrickContainer(trick);

        // Insert trick number before the name inside the container
        const number = document.createElement('span');
        number.className = 'trick-number';
        number.textContent = `${trickCounter}.`;
        const innerMain = container.querySelector('.trick-main');
        if (innerMain && innerMain.firstChild) {
            innerMain.insertBefore(number, innerMain.firstChild);
        } else if (innerMain) {
            innerMain.appendChild(number);
        }

        // Remove button
        const removeButton = document.createElement('button');
        removeButton.className = 'remove-trick';
        removeButton.textContent = '×';
        removeButton.onclick = () => removeTrick(trick);

        trickContent.appendChild(container);
        trickContent.appendChild(removeButton);

        frame.appendChild(trickContent);
        
        // Add drag and drop event listeners for tricks
        frame.addEventListener('dragstart', handleDragStart);
        frame.addEventListener('dragover', handleDragOver);
        frame.addEventListener('drop', handleDrop);
        frame.addEventListener('dragend', handleDragEnd);
        
        currentSection.querySelector('.trick-container').appendChild(frame);
        trickCounter++;
    });
}

function createFallbackTrickContainer(trick) {
    const container = document.createElement('div');
    container.className = 'trick-container-fallback';
    const name = document.createElement('div');
    name.textContent = trick.name;
    name.className = 'trick-name';
    container.appendChild(name);
    return container;
}

export function addTrickToRoute(trick) {
    if (!window.currentRoute) {
        window.currentRoute = { name: '', duration_seconds: 600, prop: '', tricks: [] };
    }
    
    // Ensure the current route has a prop set (use the currently selected prop)
    if (!window.currentRoute.prop) {
        const selectedPropInput = document.querySelector('.prop-option-input:checked');
        if (selectedPropInput) {
            window.currentRoute.prop = selectedPropInput.value;
            console.log('Set currentRoute prop to:', window.currentRoute.prop);
        }
    }
    
    // Check if a trick with the same name and props_count already exists
    const isDuplicate = window.currentRoute.tricks.some(t => 
        t.name === trick.name && t.props_count === trick.props_count
    );
    
    if (isDuplicate) {
        if (typeof window.showToast === 'function') {
            window.showToast('This trick is already in your route.');
        }
        return;
    }
    
    // Add the trick to the end of the route
    window.currentRoute.tricks.push(trick);
    
    console.log('Trick added to route:', trick.name, 'Total tricks:', window.currentRoute.tricks.length);
    console.log('Current route:', window.currentRoute);
    
    // Update the display to show the new trick at the end
    if (typeof window.updateRouteDisplay === 'function') {
        window.updateRouteDisplay();
    } else {
        updateRouteDisplay();
    }
}

export function removeTrick(trick) {
    if (!window.currentRoute) return;
    
    window.currentRoute.tricks = window.currentRoute.tricks.filter(t => t.name !== trick.name);
    updateRouteDisplay();
}

// Drag and drop functionality for route tricks
let draggedItem = null;
let draggedSection = null;

function handleDragStart(e) {
    draggedItem = e.target;
    e.target.classList.add('dragging');
}

function handleDragOver(e) {
    e.preventDefault();
    const frame = e.target.closest('.prop-details-frame');
    if (!frame || frame === draggedItem) return;
    
    const container = frame.parentElement;
    const rect = frame.getBoundingClientRect();
    const midY = rect.top + rect.height / 2;
    
    if (e.clientY < midY) {
        container.insertBefore(draggedItem, frame);
    } else {
        container.insertBefore(draggedItem, frame.nextSibling);
    }
}

function handleDrop(e) {
    e.preventDefault();
    e.target.classList.remove('dragging');
}

function handleDragEnd(e) {
    e.target.classList.remove('dragging');
    draggedItem = null;
    
    // Update the tricks array to match the new DOM order
    const frames = document.querySelectorAll('.prop-details-frame');
    const newTricks = [];
    
    frames.forEach(frame => {
        const name = frame.getAttribute('data-trick-name');
        const trick = window.currentRoute.tricks.find(t => t.name === name);
        if (trick) {
            newTricks.push(trick);
        }
    });
    
    window.currentRoute.tricks = newTricks;
    updateRouteDisplay();
}

function handleSectionDragStart(e) {
    draggedSection = e.target.closest('.prop-section');
    draggedSection.classList.add('dragging');
    draggedSection.style.opacity = '0.5';
}

function handleSectionDragOver(e) {
    e.preventDefault();
    const section = e.target.closest('.prop-section');
    if (!section || section === draggedSection) return;
    
    const container = section.parentElement;
    const rect = section.getBoundingClientRect();
    const midY = rect.top + rect.height / 2;
    
    if (e.clientY < midY) {
        container.insertBefore(draggedSection, section);
    } else {
        container.insertBefore(draggedSection, section.nextSibling);
    }
}

function handleSectionDrop(e) {
    e.preventDefault();
    e.target.classList.remove('dragging');
}

function handleSectionDragEnd(e) {
    e.target.classList.remove('dragging');
    draggedSection.style.opacity = '1';
    draggedSection = null;
    
    // Update the tricks array to match the new section order
    const sections = document.querySelectorAll('.prop-section');
    const newTricks = [];
    sections.forEach(section => {
        const frames = section.querySelectorAll('.prop-details-frame');
        frames.forEach(frame => {
            const name = frame.getAttribute('data-trick-name');
            const trick = window.currentRoute.tricks.find(t => t.name === name);
            if (trick) newTricks.push(trick);
        });
    });
    window.currentRoute.tricks = newTricks;
    
    // Update the route display to reflect the new order and numbers
    updateRouteDisplay();
    
    // Update the tricks list to reflect the new order
    if (typeof window.updateSearchTricks === 'function') {
        window.updateSearchTricks();
    }
}

export function initializePropSelection() {
    const propOptions = document.querySelectorAll('.prop-option');
    const propInputs = document.querySelectorAll('.prop-option-input');

    function updateSelectedState() {
        propOptions.forEach(option => {
            const input = option.querySelector('.prop-option-input');
            if (input.checked) {
                option.classList.add('selected');
                if (window.currentRoute && window.currentRoute.prop !== input.value) {
                    window.currentRoute.tricks = [];
                    window.currentRoute.prop = input.value;
                    
                    // Get prop settings for the selected prop
                    const propSettings = window.propsSettings && window.propsSettings[input.value];
                    if (propSettings) {
                        // Update relevant tags for this prop (with 'available' suffix to match build_route naming)
                        if (typeof window.updateRelevantTags === 'function') {
                            window.updateRelevantTags(propSettings.relevant_tags, 'available');
                        }
                        
                        // Update max throw settings for this prop
                        if (typeof window.setMaxThrowForProp === 'function') {
                            window.setMaxThrowForProp(propSettings);
                        }
                        
                        // Update props slider range if available
                        if (typeof window.updatePropsSliderRange === 'function') {
                            window.updatePropsSliderRange(propSettings.min_props, propSettings.max_props);
                        }
                        
                        // Update custom trick props range
                        if (typeof window.updateCustomTrickPropsRange === 'function') {
                            window.updateCustomTrickPropsRange(propSettings.min_props, propSettings.max_props);
                        }
                    }
                    
                    // Fetch tricks and update available tricks on prop change
                    if (typeof window.fetchTricks === 'function') {
                        console.log('Fetching tricks for prop:', input.value);
                        window.fetchTricks({ propType: input.value })
                            .then(tricks => {
                                console.log('Fetched tricks SUCCESS:', tricks.length, 'tricks');
                                window.allTricks = tricks;
                                if (typeof window.UpdateAvailableTricks === 'function') {
                                    console.log('Calling UpdateAvailableTricks');
                                    window.UpdateAvailableTricks();
                                } else {
                                    console.error('UpdateAvailableTricks function not available');
                                }
                            })
                            .catch(error => {
                                console.error('Error fetching tricks:', error);
                                if (!window.allTricks || window.allTricks.length === 0) {
                                    if (typeof window.showToast === 'function') {
                                        window.showToast('Error loading tricks. Please try again.');
                                    }
                                }
                            });
                    } else {
                        console.error('fetchTricks function not available');
                    }
                } else {
                    // Even if prop hasn't changed, still update UI elements on initial load
                    const propSettings = window.propsSettings && window.propsSettings[input.value];
                    if (propSettings) {
                        // Update relevant tags for this prop
                        if (typeof window.updateRelevantTags === 'function') {
                            window.updateRelevantTags(propSettings.relevant_tags, 'available');
                        }
                        
                        // Update max throw settings for this prop
                        if (typeof window.setMaxThrowForProp === 'function') {
                            window.setMaxThrowForProp(propSettings);
                        }
                        
                        // Update custom trick props range for initial load
                        if (typeof window.updateCustomTrickPropsRange === 'function') {
                            window.updateCustomTrickPropsRange(propSettings.min_props, propSettings.max_props);
                        }
                    }
                    
                    // If tricks aren't loaded yet, fetch them even if prop hasn't changed
                    if ((!window.allTricks || window.allTricks.length === 0) && !window._currentFetchPromise) {
                        console.log('No tricks loaded and no fetch in progress, fetching for current prop:', input.value);
                        if (typeof window.fetchTricks === 'function') {
                            window.fetchTricks({ propType: input.value })
                                .then(tricks => {
                                    console.log('Current prop fetch SUCCESS:', tricks.length, 'tricks loaded');
                                    window.allTricks = tricks;
                                    if (typeof window.UpdateAvailableTricks === 'function') {
                                        window.UpdateAvailableTricks();
                                    }
                                })
                                .catch(error => {
                                    console.error('Current prop fetch FAILED:', error);
                                });
                        }
                    } else {
                        if (typeof window.updateSearchTricks === 'function') {
                            window.updateSearchTricks();
                        }
                    }
                }
                if (typeof window.updateRouteDisplay === 'function') {
                    window.updateRouteDisplay();
                }
            } else {
                option.classList.remove('selected');
            }
        });
    }

    updateSelectedState();

    propOptions.forEach(option => {
        option.addEventListener('click', function() {
            propInputs.forEach(input => input.checked = false);
            const input = this.querySelector('.prop-option-input');
            input.checked = true;
            updateSelectedState();
        });
    });

    propInputs.forEach(input => {
        input.addEventListener('change', updateSelectedState);
    });
    
    // Expose updateSelectedState so it can be called from outside
    window.updatePropSelection = updateSelectedState;
    
    return updateSelectedState;
}

export function getRandomTrickForDifficulty(allTricks, difficulty, minProps, maxProps, excludedTags = [], maxThrow = null) {
    try {
        if (!Array.isArray(allTricks) || allTricks.length === 0) return null;

        // Normalize inputs
        const minP = Number.isFinite(Number(minProps)) ? Number(minProps) : -Infinity;
        const maxP = Number.isFinite(Number(maxProps)) ? Number(maxProps) : Infinity;
        const targetDiff = Number.isFinite(Number(difficulty)) ? Number(difficulty) : null;
        const excluded = Array.isArray(excludedTags) ? excludedTags.map(String) : [];

        // Step 1: filter by props count
        const byProps = allTricks.filter(t => {
            try {
                const props = Number.isFinite(Number(t.props_count)) ? Number(t.props_count) : null;
                if (props === null) return false;
                return props >= minP && props <= maxP;
            } catch (e) { return false; }
        });
        

        // Step 2: filter out excluded tags
        const byTags = byProps.filter(t => {
            try {
                const tTags = Array.isArray(t.tags) ? t.tags.map(x => String(x)) : [];
                for (const ex of excluded) if (tTags.includes(String(ex))) return false;
                return true;
            } catch (e) { return false; }
        });
        

        // Step 3: filter by max_throw if provided
        let candidates = byTags;
        if (Number.isFinite(Number(maxThrow))) {
            candidates = byTags.filter(t => {
                try {
                    if (!Number.isFinite(Number(t.max_throw))) return true; // treat missing max_throw as allowed
                    return Number(t.max_throw) <= Number(maxThrow);
                } catch (e) { return false; }
            });
            
        }
        if (candidates.length > 0) {
            const sample = candidates.slice(0, 5).map(c => ({ name: c.name, props_count: c.props_count, difficulty: c.difficulty, max_throw: c.max_throw }));
            
        }

        // Progressive relaxation: if nothing matched, try loosening filters so tooltip can still show a sample.
        if (candidates.length === 0) {
            
            // 1) ignore max_throw (use byTags)
            if (byTags && byTags.length > 0) {
                candidates = byTags.slice();
                
            }
        }

        if (candidates.length === 0) {
            // 2) ignore excluded tags (use byProps)
            if (byProps && byProps.length > 0) {
                candidates = byProps.slice();
                
            }
        }

        if (candidates.length === 0) {
            // 3) ignore props filter (use allTricks)
            candidates = Array.isArray(allTricks) ? allTricks.slice() : [];
            
        }

        if (candidates.length === 0) return null;

        // If difficulty target provided, only accept exact difficulty matches
        if (targetDiff !== null) {
            const exact = candidates.filter(t => {
                try { return Number.isFinite(Number(t.difficulty)) && Number(t.difficulty) === targetDiff; } catch (e) { return false; }
            });
            
            if (exact.length === 0) return null;
            const idx = Math.floor(Math.random() * exact.length);
            return exact[idx] || null;
        }

        // No target difficulty provided: return a random candidate
        try {
            const idx = Math.floor(Math.random() * candidates.length);
            return candidates[idx] || null;
        } catch (e) {
            console.error('getRandomTrickForDifficulty failed selecting random candidate', e);
            return null;
        }
    } catch (e) {
        console.error('getRandomTrickForDifficulty failed', e);
        return null;
    }
}
