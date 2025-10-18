// Exports helpers for route pages: fetchTricks, updatePropsSliderRange, updateRelevantTags, setMaxThrowForProp

export async function fetchTricks(filters = {}) {
    try {
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

        console.debug('fetchTricks payload:', payload);
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
        return Array.isArray(data) ? data : (data.tricks || data || []);
    } catch (e) {
        console.error('fetchTricks failed', e);
        throw e;
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
        console.debug('setMaxThrowForProp called with', propSettings);
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
        if (maxThrowContainer) console.debug('setMaxThrowForProp container state:', { classList: maxThrowContainer.classList.toString(), inlineDisplay: maxThrowContainer.style.display });
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
    }
} catch (e) {}
