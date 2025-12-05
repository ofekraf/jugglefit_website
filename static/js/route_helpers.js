// Exports helpers for route pages: fetchTricks, updatePropsSliderRange, updateRelevantTags, setMaxThrowForProp

export async function fetchTricks(filters = {}) {
    try {
        // Prevent multiple concurrent fetches for the same prop
        const propType = filters.prop_type || filters.propType || filters.prop || null;
        if (propType && window._currentFetchPromise && window._currentFetchProp === propType) {
            
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
                    if (typeof window.updateSearchTricks === 'function') window.updateSearchTricks();
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
                    if (typeof window.updateSearchTricks === 'function') window.updateSearchTricks();
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
        window.refreshFromRoute = refreshFromRoute;
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
// Centralized refresh function that updates all GUI elements from a route object
export function refreshFromRoute(route = null) {
    const routeToUse = route || window.currentRoute;
    if (!routeToUse) return;
    
    // Update route name input and title
    const routeNameInput = document.getElementById('route_name');
    if (routeNameInput) {
        routeNameInput.value = routeToUse.name || '';
    }
    
    // Also update route title if it exists (for created_route.html)
    const routeTitle = document.getElementById('route-title');
    if (routeTitle) {
        routeTitle.textContent = routeToUse.name || 'Untitled Route';
    }
    
    // Update duration slider and input
    const durationMinutes = Math.floor((routeToUse.duration_seconds || 600) / 60);
    const durationSlider = document.getElementById('route-duration-slider');
    const durationValue = document.getElementById('route-duration-value');
    const durationInput = document.getElementById('route-duration-input');
    
    if (durationSlider) durationSlider.value = durationMinutes;
    if (durationValue) durationValue.textContent = durationMinutes;
    if (durationInput) durationInput.value = durationMinutes;
    
    // Update prop selection
    if (routeToUse.prop) {
        const propInput = document.querySelector(`input[name="prop"][value="${routeToUse.prop}"]`);
        if (propInput) {
            propInput.checked = true;
            const propOption = propInput.closest('.prop-option');
            if (propOption) {
                // Remove selected class from all options
                document.querySelectorAll('.prop-option').forEach(opt => opt.classList.remove('selected'));
                // Add selected class to current option
                propOption.classList.add('selected');
            }
            
            // Update prop-specific settings
            const propSettings = window.propsSettings && window.propsSettings[routeToUse.prop];
            if (propSettings) {
                // Update relevant tags
                if (typeof updateRelevantTags === 'function') {
                    updateRelevantTags(propSettings.relevant_tags, 'available');
                }
                
                // Set max throw for this prop
                if (typeof setMaxThrowForProp === 'function') {
                    setMaxThrowForProp(propSettings);
                }
                
                // Update custom trick props range
                if (typeof updateCustomTrickPropsRange === 'function') {
                    updateCustomTrickPropsRange(propSettings.min_props, propSettings.max_props);
                }
            }
        }
    }
    
    // Update route display
    updateRouteDisplay(routeToUse);
    
    // Check and apply siteswap-x toggle state
    const siteswapToggle = document.getElementById('toggle-siteswap-x-checkbox');
    if (siteswapToggle && typeof window.toggleSiteswapXEverywhere === 'function') {
        window.toggleSiteswapXEverywhere();
    }
}

// Route display functionality (updated to accept route parameter)
export function updateRouteDisplay(route = null) {
    const routeToUse = route || window.currentRoute;
    const routeSections = document.getElementById('route-sections');
    if (!routeSections || !routeToUse) {
        return;
    }

    // Determine context: build page (editable) vs. created_route page (read-only)
    const isBuildPage = document.querySelector('.route-form') !== null;

    routeSections.innerHTML = '';

    if (!routeToUse.tricks || routeToUse.tricks.length === 0) {
        console.log('No tricks to display');
        return;
    }

    let currentPropsCount = null;
    let currentSection = null;
    let trickCounter = 1;

    routeToUse.tricks.forEach((trick, index) => {
        if (currentPropsCount !== trick.props_count ||
            (index > 0 && routeToUse.tricks[index - 1].props_count !== trick.props_count)) {
            if (currentSection) {
                currentSection.querySelector('.trick-container').appendChild(document.createElement('div'));
            }

            const section = document.createElement('div');
            section.className = 'prop-section';
            section.setAttribute('data-props-count', trick.props_count);

            const colorBar = document.createElement('div');
            colorBar.className = 'prop-color-bar';
            colorBar.setAttribute('data-props', trick.props_count);
            colorBar.setAttribute('data-prop-type', routeToUse.prop);

            if (isBuildPage) {
                colorBar.setAttribute('draggable', 'true');
                colorBar.addEventListener('dragstart', handleSectionDragStart);
                colorBar.addEventListener('dragover', handleSectionDragOver);
                colorBar.addEventListener('drop', handleSectionDrop);
                colorBar.addEventListener('dragend', handleSectionDragEnd);
            }

            const propCount = document.createElement('div');
            propCount.className = 'prop-count';
            const propCountText = document.createElement('div');
            propCountText.className = 'prop-count-text';
            propCountText.textContent = `X ${trick.props_count}`;
            propCount.appendChild(propCountText);
            colorBar.appendChild(propCount);
            section.appendChild(colorBar);

            const trickContainer = document.createElement('div');
            trickContainer.className = 'trick-container';
            trickContainer.setAttribute('data-props-count', trick.props_count);
            section.appendChild(trickContainer);
            routeSections.appendChild(section);

            currentSection = section;
            currentPropsCount = trick.props_count;
        }

        const frame = document.createElement('div');
        frame.className = 'prop-details-frame';
        frame.setAttribute('data-trick-name', trick.name || trick.siteswap_x || '');

        const trickContent = document.createElement('div');
        trickContent.className = 'trick-content';

        const displayName = trick.name || '';
        const siteswapToggle = document.getElementById('toggle-siteswap-x-checkbox');
        const showSiteswap = siteswapToggle && siteswapToggle.checked;

        const containerOptions = {
            editable: isBuildPage,
            addCheckbox: !isBuildPage,
            onNameBlur: isBuildPage ? (newName) => { trick.name = newName; frame.setAttribute('data-trick-name', newName); } : null,
            onCommentBlur: isBuildPage ? (newComment) => { trick.comment = newComment; } : null,
            showSiteswap: showSiteswap
        };

        const container = window.CreateTrickContainer ?
            window.CreateTrickContainer(displayName, trick.comment || '', trick.siteswap_x || null, containerOptions) :
            createFallbackTrickContainer(trick);

        const number = document.createElement('span');
        number.className = 'trick-number';
        number.textContent = `${trickCounter}.`;
        const innerMain = container.querySelector('.trick-main');
        if (innerMain && innerMain.firstChild) {
            innerMain.insertBefore(number, innerMain.firstChild);
        } else if (innerMain) {
            innerMain.appendChild(number);
        }

        trickContent.appendChild(container);

        if (isBuildPage) {
            frame.setAttribute('draggable', 'true');
            const removeButton = document.createElement('button');
            removeButton.className = 'remove-trick';
            removeButton.textContent = '×';
            removeButton.onclick = () => removeTrick(trick);
            trickContent.appendChild(removeButton);

            frame.addEventListener('dragstart', handleDragStart);
            frame.addEventListener('dragover', handleDragOver);
            frame.addEventListener('drop', handleDrop);
            frame.addEventListener('dragend', handleDragEnd);
        }

        frame.appendChild(trickContent);
        currentSection.querySelector('.trick-container').appendChild(frame);
        trickCounter++;
    });
}

function createFallbackTrickContainer(trick) {
    const container = document.createElement('div');
    container.className = 'trick-container-fallback';
    const name = document.createElement('div');
    // Show siteswap-x if no name, empty string if neither
    name.textContent = trick.name || trick.siteswap_x || '';
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
        }
    }
    
    // Normalize trick fields to expected shape so display logic works
    const normalized = Object.assign({}, trick);
    if (typeof normalized.props_count === 'undefined' && typeof normalized.propsCount !== 'undefined') normalized.props_count = normalized.propsCount;
    if (typeof normalized.props_count === 'undefined') normalized.props_count = Number(normalized.props) || 3;
    if (typeof normalized.difficulty === 'undefined') normalized.difficulty = Number(normalized.diff) || 30;
    if (!Array.isArray(normalized.tags)) normalized.tags = normalized.tags ? [normalized.tags] : [];
    if (typeof normalized.comment === 'undefined') normalized.comment = null;
    if (normalized.siteswap_x === '') normalized.siteswap_x = null;

    // Check if a trick with the same name and props_count already exists
    const isDuplicate = window.currentRoute.tricks.some(t => {
        const propsMatch = Number(t.props_count) === Number(normalized.props_count);
        if (!propsMatch) return false;

        const nameMatch = t.name && normalized.name && t.name === normalized.name;
        const siteswapMatch = t.siteswap_x && normalized.siteswap_x && t.siteswap_x === normalized.siteswap_x;

        return nameMatch || siteswapMatch;
    });
    
    if (isDuplicate) {
        if (typeof window.showToast === 'function') {
            window.showToast('This trick is already in your route.');
        }
        return;
    }
    
    // Add the trick to the route and refresh display
    window.currentRoute.tricks.push(Object.assign({}, normalized));
    refreshFromRoute();
}

export function removeTrick(trick) {
    if (!window.currentRoute) return;
    
    window.currentRoute.tricks = window.currentRoute.tricks.filter(t => t.name !== trick.name);
    refreshFromRoute();
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
        const displayName = frame.getAttribute('data-trick-name');
        const trick = window.currentRoute.tricks.find(t => 
            (t.name && t.name === displayName) || 
            (!t.name && t.siteswap_x === displayName)
        );
        if (trick) {
            newTricks.push(trick);
        }
    });
    
    window.currentRoute.tricks = newTricks;
    refreshFromRoute();
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
            const displayName = frame.getAttribute('data-trick-name');
            const trick = window.currentRoute.tricks.find(t => 
                (t.name && t.name === displayName) || 
                (!t.name && t.siteswap_x === displayName)
            );
            if (trick) newTricks.push(trick);
        });
    });
    window.currentRoute.tricks = newTricks;
    
    // Update the route display to reflect the new order and numbers
    refreshFromRoute();
    
    // Update the tricks list to reflect the new order
    if (typeof window.updateSearchTricks === 'function') {
        window.updateSearchTricks();
    }
}

export function initializePropSelection() {
    // Prevent redundant initialization calls
    if (window._propSelectionInitialized) {
        return;
    }
    
    const propOptions = document.querySelectorAll('.prop-option');
    const propInputs = document.querySelectorAll('.prop-option-input');

    function updateSelectedState() {
        propOptions.forEach(option => {
            const input = option.querySelector('.prop-option-input');
            if (input.checked) {
                option.classList.add('selected');
                
                // Clear tricks when prop changes (not during initialization)
                if (window.currentRoute && window.currentRoute.prop && window.currentRoute.prop !== input.value) {
                    console.log('Prop changed from', window.currentRoute.prop, 'to', input.value, '- clearing tricks');
                    window.currentRoute.tricks = [];
                }
                
                // Always update the current route prop
                if (window.currentRoute) {
                    window.currentRoute.prop = input.value;
                }
                
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
                
                // Only fetch tricks if we don't already have them for this prop
                const needsFetch = !window.allTricks || window.allTricks.length === 0 || 
                                 (window.lastFetchedProp && window.lastFetchedProp !== input.value);
                
                if (needsFetch && typeof window.fetchTricks === 'function') {
                    window.lastFetchedProp = input.value;
                    window.fetchTricks({ propType: input.value })
                        .then(tricks => {
                            window.allTricks = tricks;
                            if (typeof window.UpdateAvailableTricks === 'function') {
                                window.UpdateAvailableTricks();
                            }
                            // After rendering, ensure the siteswap-x view is correct.
                            if (typeof window.toggleSiteswapXEverywhere === 'function') {
                                window.toggleSiteswapXEverywhere();
                            }
                        })
                        .catch(error => {
                            window.lastFetchedProp = null; // Reset on error
                            if (!window.allTricks || window.allTricks.length === 0) {
                                if (typeof window.showToast === 'function') {
                                    window.showToast('Error loading tricks. Please try again.');
                                }
                            }
                        });
                } else if (!needsFetch) {
                    // Still update the display with existing tricks
                    if (typeof window.UpdateAvailableTricks === 'function') {
                        window.UpdateAvailableTricks();
                    }
                    // Also apply toggle here for cases where fetch is skipped
                    if (typeof window.toggleSiteswapXEverywhere === 'function') {
                        window.toggleSiteswapXEverywhere();
                    }
                }
                
                // Update route display (whether we have tricks or not)
                if (typeof window.updateRouteDisplay === 'function' && window.currentRoute) {
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
    
    // Mark as initialized to prevent redundant calls
    window._propSelectionInitialized = true;
    
    return updateSelectedState;
}

/**
 * Load and display a serialized route from URL parameter
 * @param {string} serializedRoute - The serialized route string from URL
 */
export function loadRoute(serializedRoute, callback) {
    try {
        console.log('Loading route from serialized string:', serializedRoute.substring(0, 100) + '...');
        
        // The route is zlib compressed then base64 encoded (Python: zlib.compress -> base64.b64encode)
        let routeData;
        try {
            console.log('Deserializing route:', serializedRoute.substring(0, 50) + '...');
            
            // Check if pako library is available for decompression
            if (typeof pako === 'undefined') {
                throw new Error('Pako compression library not loaded');
            }
            
            // Decode from base64
            const compressedData = atob(serializedRoute);
            console.log('Base64 decoded, compressed length:', compressedData.length);
            
            // Convert string to Uint8Array for pako
            const compressedBytes = new Uint8Array(compressedData.length);
            for (let i = 0; i < compressedData.length; i++) {
                compressedBytes[i] = compressedData.charCodeAt(i);
            }
            
            // Decompress using pako (zlib)
            const decompressed = pako.inflate(compressedBytes, { to: 'string' });
            console.log('Decompressed JSON length:', decompressed.length);
            
            // Parse the JSON
            routeData = JSON.parse(decompressed);
            console.log('Successfully deserialized route:', routeData.name);
            
        } catch (e) {
            console.error('Failed to deserialize route:', e);
            
            // Extract some basic info from the URL if possible
            const urlParams = new URLSearchParams(window.location.search);
            const routeName = urlParams.get('name') || 'Failed to Load Route';
            
            // Create a fallback route with error message
            routeData = {
                name: routeName,
                duration_seconds: 600,
                prop: 'balls',
                tricks: []
            };
            showError('Failed to deserialize route data: ' + e.message);
        }
        
        console.log('Deserialized route data:', routeData);
        
        // Set up global route data
        window.currentRoute = {
            name: routeData.name || 'Untitled Route',
            duration_seconds: routeData.duration_seconds || 600,
            prop: routeData.prop || 'balls',
            tricks: routeData.tricks || []
        };
        
        // Update page title
        document.title = `${window.currentRoute.name} - JuggleFit`;
        
        // Use refreshFromRoute for consistent display
        refreshFromRoute();
        
        // Set up siteswap-x toggle if not already present
        addSiteswapToggle();
        
        // Check for siteswap-x URL parameter and set checkbox
        const urlParams = new URLSearchParams(window.location.search);
        const siteswapXParam = urlParams.get('siteswapx');
        if (siteswapXParam === '1') {
            const siteswapToggle = document.getElementById('toggle-siteswap-x-checkbox');
            if (siteswapToggle) {
                siteswapToggle.checked = true;
                // Trigger the toggle function to show siteswap-x
                if (typeof window.toggleSiteswapXEverywhere === 'function') {
                    window.toggleSiteswapXEverywhere();
                }
            }
        }
        
        // Removed routeLoaded event dispatch to prevent post-load interference
        if (typeof callback === 'function') {
            callback();
        }
    } catch (error) {
        console.error('Error loading route:', error);
        // Fallback to server-side deserialization
        loadRouteFromServer(serializedRoute);
    }
}



/**
 * Display the loaded route on the page
 */
function displayLoadedRoute(route) {
    const routeSections = document.getElementById('route-sections');
    if (!routeSections) {
        console.error('route-sections element not found');
        return;
    }
    
    // Clear existing content
    routeSections.innerHTML = '';
    
    if (!route.tricks || route.tricks.length === 0) {
        routeSections.innerHTML = '<div class="no-tricks">No tricks in this route.</div>';
        return;
    }
    
    let currentPropsCount = null;
    let currentSection = null;
    let trickCounter = 1;

    route.tricks.forEach((trick, index) => {
        // Check if we need to create a new section
        if (currentPropsCount !== trick.props_count) {
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
            colorBar.setAttribute('data-prop-type', route.prop);
            
            const propCount = document.createElement('div');
            propCount.className = 'prop-count';
            
            const propCountText = document.createElement('div');
            propCountText.className = 'prop-count-text';
            propCountText.textContent = `X ${trick.props_count}`;
            
            propCount.appendChild(propCountText);
            colorBar.appendChild(propCount);
            section.appendChild(colorBar);
            
            const trickContainer = document.createElement('div');
            trickContainer.className = 'trick-container';
            trickContainer.setAttribute('data-props-count', trick.props_count);
            
            section.appendChild(trickContainer);
            routeSections.appendChild(section);
            
            currentSection = section;
            currentPropsCount = trick.props_count;
        }

        // Create trick frame
        const frame = document.createElement('div');
        frame.className = 'prop-details-frame';

        const trickContent = document.createElement('div');
        trickContent.className = 'trick-content';

        // Use CreateTrickContainer to build consistent inner DOM
        // Always pass the actual name (empty if not set) - siteswap-x will show when name is empty
        const displayName = trick.name || '';
        const container = window.CreateTrickContainer ? window.CreateTrickContainer(displayName, trick.comment || '', trick.siteswap_x || null, {
            editable: false,  // Read-only for created route
            addCheckbox: true  // Add checkbox for line-through functionality
        }) : createFallbackTrickContainer(trick);

        // Insert trick number before the name
        const number = document.createElement('span');
        number.className = 'trick-number';
        number.textContent = `${trickCounter}.`;
        const innerMain = container.querySelector('.trick-main');
        if (innerMain && innerMain.firstChild) {
            innerMain.insertBefore(number, innerMain.firstChild);
        } else if (innerMain) {
            innerMain.appendChild(number);
        }

        trickContent.appendChild(container);
        frame.appendChild(trickContent);
        
        currentSection.querySelector('.trick-container').appendChild(frame);
        trickCounter++;
    });
}

/**
 * Add siteswap-x toggle to the page if not present
 */
function addSiteswapToggle() {
    // Check if toggle already exists
    if (document.getElementById('toggle-siteswap-x-checkbox')) {
        return;
    }
    
    // Create toggle container
    const toggleContainer = document.createElement('div');
    toggleContainer.className = 'siteswap-x-toggle-row center-row no-print';
    toggleContainer.innerHTML = `
        <label class="siteswap-x-toggle-label">
            <input type="checkbox" id="toggle-siteswap-x-checkbox" class="siteswap-x-toggle-checkbox"> Siteswap-X
        </label>
    `;
    
    // Insert after route title or at the beginning of route content
    const routePage = document.querySelector('.route-page');
    const routeLayout = document.querySelector('.route-layout');
    
    if (routeLayout && routePage) {
        routePage.insertBefore(toggleContainer, routeLayout);
    } else if (routePage) {
        routePage.insertBefore(toggleContainer, routePage.firstChild);
    }
    
    // Set up event listener
    const checkbox = document.getElementById('toggle-siteswap-x-checkbox');
    if (checkbox && window.toggleSiteswapXEverywhere) {
        checkbox.addEventListener('change', window.toggleSiteswapXEverywhere);
        // Initialize display
        window.toggleSiteswapXEverywhere();
    }
}

/**
 * Show error message to user
 */
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    errorDiv.style.cssText = 'background: #f44336; color: white; padding: 1rem; margin: 1rem; border-radius: 4px; text-align: center;';
    
    const routePage = document.querySelector('.route-page');
    if (routePage) {
        routePage.insertBefore(errorDiv, routePage.firstChild);
    } else {
        document.body.appendChild(errorDiv);
    }
}

// Removed aggressive protection system - fixed by removing post-load interference

/**
 * Initialize route loading from URL parameter - immediate loading
 */
export function initRouteLoading(callback) {
    const urlParams = new URLSearchParams(window.location.search);
    const routeParam = urlParams.get('route');
    
    if (routeParam) {
        console.log('Found route parameter, loading route immediately...');
        loadRoute(routeParam, callback);
    } else {
        console.log('No route parameter found in URL');
        // Set a default empty route
        window.currentRoute = {
            name: 'No Route Data',
            duration_seconds: 600,
            prop: 'balls',
            tricks: []
        };
        refreshFromRoute();
        const routeTitle = document.getElementById('route-title');
        if (routeTitle) routeTitle.textContent = 'No Route Data';
        showError('No route data found in URL. Please check the link and try again.');
        
        // Still check for siteswap-x URL parameter even without route data
        const urlParams = new URLSearchParams(window.location.search);
        const siteswapXParam = urlParams.get('siteswapx');
        if (siteswapXParam === '1') {
            const siteswapToggle = document.getElementById('toggle-siteswap-x-checkbox');
            if (siteswapToggle) {
                siteswapToggle.checked = true;
                if (typeof window.toggleSiteswapXEverywhere === 'function') {
                    window.toggleSiteswapXEverywhere();
                }
            }
        }
    }
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
