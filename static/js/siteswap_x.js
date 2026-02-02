// Unified toggle for both route and available tricks
function toggleSiteswapXEverywhere() {
    const cb = document.getElementById('toggle-siteswap-x-checkbox');
    const checked = cb && cb.checked;
    try {
        const containers = document.querySelectorAll('.trick-container');
        containers.forEach(container => {
            try {
                toggleSiteswapX(container, checked);
            } catch (e) {
                // per-container errors shouldn't abort the whole operation
                console.error('Error toggling trick container', container, e);
            }
        });
    } catch (err) {
        console.error('Error while toggling trick displays:', err);
    }
}

// Toggle a single trick container's display between name and siteswap-x.
// Accepts either the .trick-container element, the .trick-main element, or any ancestor.
// Optional second argument `showX` (boolean) forces showing siteswap-x when true,
// showing name when false. If omitted, the function toggles the current visible state.
function toggleSiteswapX(trickElement, showX) {
    if (!trickElement) return;
    // If a container was passed, prefer its .trick-main child
    let trickMain = trickElement.classList && trickElement.classList.contains('trick-main') ? trickElement : null;
    if (!trickMain) {
        trickMain = trickElement.querySelector && trickElement.querySelector('.trick-main') ? trickElement.querySelector('.trick-main') : null;
    }
    if (!trickMain) return;

    const nameEl = trickMain.querySelector('.trick-name');
    const xEl = trickMain.querySelector('.trick-siteswap-x');

    // Determine whether this trick has siteswap content
    let siteswapText = '';
    if (xEl) {
        siteswapText = xEl.textContent ? xEl.textContent.trim() : '';
        if (!siteswapText && xEl.dataset && typeof xEl.dataset.hasSiteswapX !== 'undefined') {
            siteswapText = xEl.dataset.hasSiteswapX === '1' ? 'x' : '';
        }
    }
    const hasSiteswap = siteswapText !== '' && siteswapText.toLowerCase() !== 'none';
    
    // Check if name exists (not empty and not just the siteswap fallback)
    const nameText = nameEl ? nameEl.textContent.trim() : '';
    const hasName = nameText !== '' && nameText !== siteswapText;

    // Symmetrical logic: If one is empty, always show the other
    if (!hasName && hasSiteswap) {
        // No name but has siteswap - always show siteswap
        if (nameEl) nameEl.style.display = 'none';
        if (xEl) xEl.style.display = '';
        return;
    }
    
    if (hasName && !hasSiteswap) {
        // Has name but no siteswap - always show name
        if (nameEl) nameEl.style.display = '';
        if (xEl) xEl.style.display = 'none';
        return;
    }

    // Both exist - respect the toggle state
    if (hasName && hasSiteswap) {
        // If showX not provided, toggle current state (show X if name currently visible)
        if (typeof showX === 'undefined') {
            const nameVisible = nameEl ? window.getComputedStyle(nameEl).display !== 'none' : false;
            showX = !!nameVisible; // if name is visible, toggling should show X
        }

        if (showX) {
            if (nameEl) nameEl.style.display = 'none';
            if (xEl) xEl.style.display = '';
        } else {
            if (nameEl) nameEl.style.display = '';
            if (xEl) xEl.style.display = 'none';
        }
        return;
    }

    // Neither exists - show name element (will be empty)
    if (nameEl) nameEl.style.display = '';
    if (xEl) xEl.style.display = 'none';
}

// Accepts either a string (returns formatted HTML) or an Element (sets element.innerHTML and returns it)
function formatSiteswapX(siteswapString) {
    // Mirror the server-side formatter: parse tokens and produce markup with
    // .siteswap-x-digit-container, .siteswap-x-throw-mod, .siteswap-x-digit, .siteswap-x-catch-mod
    if (typeof siteswapString !== 'string') return '';
    const escapeHtml = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    const escaped = escapeHtml(siteswapString).replace(/-&gt;|->/g, '→');

    // New parsing logic: find either a modified digit or a block of plain text.
    // This avoids regex greediness issues with consecutive modifiers.
    const tokenRe = /([0-9a-z→])(?:\{([^{}\/]*)?(?:\/([^{}]*))?\})|([0-9a-z→])/gi;
    let out = '';
    let lastIndex = 0;
    let match;
    while ((match = tokenRe.exec(escaped))) {
        // Add any text between the last match and this one
        if (match.index > lastIndex) {
            out += '<span>' + escaped.slice(lastIndex, match.index) + '</span>';
        }

        const mainDigit = match[1] || match[4];
        const throwMod = match[2];
        const catchMod = match[3];

        let html = '<span class="siteswap-x-digit-container">';
        if (throwMod) html += '<span class="siteswap-x-throw-mod">' + throwMod + '</span>';
        html += '<span class="siteswap-x-digit">' + mainDigit + '</span>';
        if (catchMod) html += '<span class="siteswap-x-catch-mod">' + catchMod + '</span>';
        html += '</span>';
        out += html;

        lastIndex = tokenRe.lastIndex;
    }
    // Add any remaining text after the last match
    if (lastIndex < escaped.length) {
        out += '<span>' + escaped.slice(lastIndex) + '</span>';
    }
    return out;
}

// Build a DOM element for a siteswap-x string (no innerHTML used).
// Returns a <span class="trick-siteswap-x"> element containing
// .siteswap-x-digit-container children with optional .siteswap-x-throw-mod
// and .siteswap-x-catch-mod spans.
function createSiteswapXElement(siteswapString) {
    if (typeof siteswapString !== 'string' || !siteswapString.trim()) return null;
    // Normalize arrows
    const normalized = siteswapString.replace(/-&gt;|->/g, '→');
    const container = document.createElement('span');
    container.className = 'trick-siteswap-x';
    container.style.display = 'none';

    // Use the same robust parsing logic as formatSiteswapX
    const tokenRe = /([0-9a-z→])(?:\{([^{}\/]*)?(?:\/([^{}]*))?\})|([0-9a-z→])/gi;
    let lastIndex = 0;
    let match;
    while ((match = tokenRe.exec(normalized))) {
        if (match.index > lastIndex) {
            const textSpan = document.createElement('span');
            textSpan.textContent = normalized.slice(lastIndex, match.index);
            container.appendChild(textSpan);
        }

        const mainDigit = match[1] || match[4];
        const throwMod = match[2];
        const catchMod = match[3];

        const digitContainer = document.createElement('span');
        digitContainer.className = 'siteswap-x-digit-container';

        if (throwMod) {
            const throwEl = document.createElement('span');
            throwEl.className = 'siteswap-x-throw-mod';
            throwEl.textContent = throwMod;
            digitContainer.appendChild(throwEl);
        }

        const digitEl = document.createElement('span');
        digitEl.className = 'siteswap-x-digit';
        digitEl.textContent = mainDigit;
        digitContainer.appendChild(digitEl);

        if (catchMod) {
            const catchEl = document.createElement('span');
            catchEl.className = 'siteswap-x-catch-mod';
            catchEl.textContent = catchMod;
            digitContainer.appendChild(catchEl);
        }
        
        // Add a non-breaking space after the digit container to create a gap
        // This ensures spacing between digits even when font size scales up
        container.appendChild(digitContainer);
        // container.appendChild(document.createTextNode('\u00A0')); // Removed: caused too much spacing

        lastIndex = tokenRe.lastIndex;
    }
    if (lastIndex < normalized.length) {
        const textSpan = document.createElement('span');
        textSpan.textContent = normalized.slice(lastIndex);
        container.appendChild(textSpan);
    }
    container.dataset.hasSiteswapX = '1';
    return container;
}

// Create a trick container element. name is required; comment and siteswapX are optional.
// options: { onNameBlur: fn(newName), onCommentBlur: fn(newComment), onAdd: fn(event) }
function CreateTrickContainer(name, comment = '', siteswapX = '', options = {}) {
    const container = document.createElement('div');
    container.className = 'trick-container trick-widget';

    const main = document.createElement('div');
    main.className = 'trick-main';

    const nameEl = document.createElement('span');
    nameEl.className = 'trick-name';
    // Only show the actual name (or empty string if no name)
    nameEl.textContent = name || '';
    // Respect editable option (false = non-editable view like created-route)
    nameEl.contentEditable = options.editable !== false;
    nameEl.addEventListener('blur', function() {
        const newName = this.textContent.trim();
        if (typeof options.onNameBlur === 'function') options.onNameBlur(newName);
    });
    main.appendChild(nameEl);

    // Add siteswap-x after name
    let xEl = null;
    if (siteswapX) {
        const built = createSiteswapXElement(siteswapX);
        if (built) {
            xEl = built;
            main.appendChild(xEl);
        }
    }

    // Add comment after siteswap-x
    let commentEl = null;
    if (comment) {
        commentEl = document.createElement('span');
        commentEl.className = 'trick-comment';
        commentEl.textContent = `[${comment}]`;
        commentEl.contentEditable = options.editable !== false;
        commentEl.addEventListener('blur', function() {
            const newComment = this.textContent.replace(/\[|\]/g, '').trim();
            if (typeof options.onCommentBlur === 'function') options.onCommentBlur(newComment);
            this.textContent = newComment ? `[${newComment}]` : '';
        });
        main.appendChild(commentEl);
    }
    
    // Set up initial display state based on symmetrical logic
    const hasName = name && name.trim() !== '';
    const hasSiteswap = siteswapX && siteswapX.trim() !== '';
    
    if (!hasName && hasSiteswap) {
        // No name but has siteswap - hide name div, show only siteswap div
        nameEl.style.display = 'none';
        if (xEl) xEl.style.display = '';
    } else if (hasName && !hasSiteswap) {
        // Has name but no siteswap - show name, hide siteswap
        nameEl.style.display = '';
        if (xEl) xEl.style.display = 'none';
    } else if (hasName && hasSiteswap) {
        // Both exist - show name by default, hide siteswap (can be toggled)
        if (options.showSiteswap) {
            nameEl.style.display = 'none';
            if (xEl) xEl.style.display = '';
        } else {
            nameEl.style.display = '';
            if (xEl) xEl.style.display = 'none';
        }
    } else {
        // Neither exists - show name element (will be empty)
        nameEl.style.display = '';
        if (xEl) xEl.style.display = 'none';
    }

    // Optional checkbox (for route display to toggle line-through / selection)
    let checkboxEl = null;
    if (options.addCheckbox) {
        checkboxEl = document.createElement('input');
        checkboxEl.type = 'checkbox';
        checkboxEl.className = 'trick-checkbox';
        checkboxEl.style.marginRight = '0.5em';
        // Wire change handler: prefer explicit callback, otherwise try global toggleLinethrough
        checkboxEl.addEventListener('change', function(e) {
            if (typeof options.onCheckboxChange === 'function') {
                options.onCheckboxChange(e.target);
            } else if (typeof window.toggleLinethrough === 'function') {
                window.toggleLinethrough(e.target);
            }
        });
        // Insert checkbox before name
        main.insertBefore(checkboxEl, nameEl);
    }

    container.appendChild(main);

    // Expose helper references for external code
    container._nameEl = nameEl;
    container._siteswapEl = xEl;
    container._commentEl = comment ? container.querySelector('.trick-comment') : null;
    container._checkboxEl = checkboxEl;

    // If an onAdd callback is provided, create an add button wrapper (caller may append it elsewhere)
    if (typeof options.onAdd === 'function') {
        const addBtn = document.createElement('button');
        addBtn.type = 'button';
        addBtn.className = 'add-trick';
        addBtn.textContent = 'Add';
        addBtn.addEventListener('click', function(e) { options.onAdd(e); });
        container._addButton = addBtn;
    }

    return container;
}
// Expose the public API expected by templates and inline handlers.
window.CreateTrickContainer = CreateTrickContainer;
window.toggleSiteswapXEverywhere = toggleSiteswapXEverywhere;
window.toggleSiteswapX = toggleSiteswapX;
window.formatSiteswapX = formatSiteswapX;