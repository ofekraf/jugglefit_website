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

    // If showX not provided, toggle current state (show X if name currently visible)
    if (typeof showX === 'undefined') {
        const nameVisible = nameEl ? window.getComputedStyle(nameEl).display !== 'none' : false;
        showX = !!nameVisible; // if name is visible, toggling should show X
    }

    if (showX && hasSiteswap) {
        if (nameEl) nameEl.style.display = 'none';
        if (xEl) xEl.style.display = '';
    } else {
        if (nameEl) nameEl.style.display = '';
        if (xEl) xEl.style.display = 'none';
    }
}

// Accepts either a string (returns formatted HTML) or an Element (sets element.innerHTML and returns it)
function formatSiteswapX(siteswapString) {
    // Mirror the server-side formatter: parse tokens and produce markup with
    // .siteswap-x-digit-container, .siteswap-x-throw-mod, .siteswap-x-digit, .siteswap-x-catch-mod
    if (typeof siteswapString !== 'string') return '';
    const escapeHtml = (s) => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    const escaped = escapeHtml(siteswapString).replace(/-&gt;|->/g, '→');

    // We'll walk the string and only mark digits that have modifiers (in curly braces).
    // Any plain characters without modifiers are returned as unwrapped text so they keep their original spacing.
    const tokenRe = /([0-9a-z→]+)(?:\{([^{}\/]*)?(?:\/([^{}]*))?\})?([A-Z0-9])?/gi;
    let lastIndex = 0;
    let out = '';
    let m;
    while ((m = tokenRe.exec(escaped)) !== null) {
        const idx = m.index;
        // append literal text between previous match and this match
        if (idx > lastIndex) {
            out += escaped.slice(lastIndex, idx);
        }
        const main = m[1] || '';
        const throwMod = m[2] || '';
        const catchMod = m[3] || '';
        const trailingMod = m[4] || '';

        if (throwMod || catchMod) {
            // If this token has modifiers, wrap the relevant digit(s).
            // If main is more than one character, attach modifier to the last character
            // but leave preceding characters unwrapped (plain text).
            if (main.length > 1) {
                out += escapeHtml(main.slice(0, -1));
            }
            const targetChar = escapeHtml(main.slice(-1));
            let html = '<span class="siteswap-x-digit-container">';
            if (throwMod) html += '<span class="siteswap-x-throw-mod">' + escapeHtml(throwMod) + '</span>';
            html += '<span class="siteswap-x-digit">' + targetChar + '</span>';
            if (catchMod) html += '<span class="siteswap-x-catch-mod">' + escapeHtml(catchMod) + '</span>';
            html += '</span>';
            out += html;
            if (trailingMod) out += escapeHtml(trailingMod);
        } else {
            // No modifiers: keep the token as plain text
            out += escapeHtml(main + (trailingMod || ''));
        }

        lastIndex = tokenRe.lastIndex;
    }
    // append remainder
    if (lastIndex < escaped.length) out += escaped.slice(lastIndex);
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

    const tokenRe = /([0-9a-z→]+)(?:\{([^{}\/]*)?(?:\/([^{}]*))?\})?([A-Z0-9])?/gi;
    let match;
    let lastIndex = 0;
    while ((match = tokenRe.exec(normalized)) !== null) {
        const idx = match.index;
        // append any literal text between tokens (spaces, punctuation)
        if (idx > lastIndex) {
            container.appendChild(document.createTextNode(normalized.slice(lastIndex, idx)));
        }

        const main = match[1] || '';
        const throwMod = match[2] || '';
        const catchMod = match[3] || '';
        const trailingMod = match[4] || '';

        if (throwMod || catchMod) {
            // If main has multiple characters, keep preceding chars as plain text
            if (main.length > 1) {
                container.appendChild(document.createTextNode(main.slice(0, -1)));
            }
            const char = main.slice(-1);
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
            digitEl.textContent = char;
            digitContainer.appendChild(digitEl);

            if (catchMod) {
                const catchEl = document.createElement('span');
                catchEl.className = 'siteswap-x-catch-mod';
                catchEl.textContent = catchMod;
                digitContainer.appendChild(catchEl);
            }

            container.appendChild(digitContainer);
            if (trailingMod) container.appendChild(document.createTextNode(trailingMod));
        } else {
            // No modifiers — append the token text as-is
            container.appendChild(document.createTextNode(main + (trailingMod || '')));
        }

        lastIndex = tokenRe.lastIndex;
    }
    if (lastIndex < normalized.length) {
        container.appendChild(document.createTextNode(normalized.slice(lastIndex)));
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
    main.style.display = 'inline-flex';
    main.style.alignItems = 'center';
    main.style.gap = '0.5em';

    const nameEl = document.createElement('span');
    nameEl.className = 'trick-name';
    nameEl.textContent = name || 'Unnamed Trick';
    nameEl.contentEditable = true;
    nameEl.addEventListener('blur', function() {
        const newName = this.textContent.trim();
        if (newName) {
            if (typeof options.onNameBlur === 'function') options.onNameBlur(newName);
        } else {
            this.textContent = name || 'Unnamed Trick';
            if (typeof options.onNameBlur === 'function') options.onNameBlur(this.textContent);
        }
    });
    main.appendChild(nameEl);

    let xEl = null;
    if (siteswapX) {
        const built = createSiteswapXElement(siteswapX);
        if (built) {
            xEl = built;
            // ensure hidden by default
            xEl.style.display = 'none';
            main.appendChild(xEl);
        }
    }

    if (comment) {
        const commentEl = document.createElement('span');
        commentEl.className = 'trick-comment';
        commentEl.textContent = ` [${comment}]`;
        commentEl.contentEditable = true;
        commentEl.addEventListener('blur', function() {
            const newComment = this.textContent.replace(/\[|\]/g, '').trim();
            if (typeof options.onCommentBlur === 'function') options.onCommentBlur(newComment);
            this.textContent = newComment ? ` [${newComment}]` : '';
        });
        main.appendChild(commentEl);
    }

    container.appendChild(main);

    // Expose helper references for external code
    container._nameEl = nameEl;
    container._siteswapEl = xEl;
    container._commentEl = comment ? container.querySelector('.trick-comment') : null;

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