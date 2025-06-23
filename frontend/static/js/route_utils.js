/**
 * Generates HTML for displaying a route
 * @param {Object} route - The route object to display
 * @returns {string} HTML string for the route display
 */
export function generateRouteDisplay(route) {
    let html = `
        <div class="route-page">
            <div class="route-header">
                <h1 class="route-title">${route.name}</h1>
            </div>

            <div class="route-container">
                <div class="route-content">
                    <div class="route-sections">
    `;

    let currentPropsCount = null;
    let trickCounter = 1;

    route.tricks.forEach((trick, index) => {
        if (currentPropsCount !== trick.props_count) {
            if (currentPropsCount !== null) {
                html += '</div></div>';
            }
            
            html += `
                <div class="prop-section">
                    <div class="prop-color-bar" data-props="${trick.props_count}" data-prop-type="${route.prop}">
                        <div class="prop-count">
                            <div class="prop-count-text">X ${trick.props_count}</div>
                        </div>
                    </div>
                    <div class="trick-container">
            `;
            
            currentPropsCount = trick.props_count;
        }

        html += `
            <div class="prop-details-frame">
                <div class="trick-content">
                    <div class="trick-main">
                        <span class="trick-number">${trickCounter}.</span>
                        <span class="trick-name">${trick.name}</span>
                        ${trick.comment ? `<span class="trick-comment">[${trick.comment}]</span>` : ''}
                    </div>
                </div>
            </div>
        `;

        trickCounter++;
    });

    if (currentPropsCount !== null) {
        html += '</div></div>';
    }

    html += `
                    </div>
                </div>
            </div>
        </div>
    `;

    return html;
}

/**
 * Adds checkboxes to all tricks in a route display
 * @param {Element} container - The container element containing the route display
 */
export function addTrickCheckboxes(container) {
    const trickContents = container.querySelectorAll('.trick-content');
    trickContents.forEach(content => {
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.className = 'trick-checkbox no-print';
        
        checkbox.addEventListener('change', function() {
            const trickNumber = content.querySelector('.trick-number');
            const trickName = content.querySelector('.trick-name');
            const trickComment = content.querySelector('.trick-comment');
            
            if (this.checked) {
                if (trickNumber) trickNumber.style.textDecoration = 'line-through';
                if (trickName) trickName.style.textDecoration = 'line-through';
                if (trickComment) trickComment.style.textDecoration = 'line-through';
            } else {
                if (trickNumber) trickNumber.style.textDecoration = 'none';
                if (trickName) trickName.style.textDecoration = 'none';
                if (trickComment) trickComment.style.textDecoration = 'none';
            }
        });
        
        content.insertBefore(checkbox, content.firstChild);
    });
} 