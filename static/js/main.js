function initMainJS() {
    // Route name placeholder handling
    const routeInput = document.getElementById('route_name');
    if (routeInput) {
        // Only set the placeholder text if the input is currently empty; do not override
        // values that may have been populated from the URL or server.
        if (!routeInput.value) {
            routeInput.value = routeInput.placeholder;
            routeInput.style.color = 'grey';
        }

        routeInput.addEventListener('focus', function() {
            if (this.value === this.placeholder) {
                this.value = '';
                this.style.color = 'black';
            }
        });

        routeInput.addEventListener('blur', function() {
            if (this.value === '') {
                this.value = this.placeholder;
                this.style.color = 'grey';
            }
        });
    }

    // Props slider initialization is handled by number_of_props_macro.html
    // No initialization needed here to avoid conflicts

    // Initialize the difficulty slider
    const difficultySlider = document.getElementById('difficulty-slider');
    if (difficultySlider && !difficultySlider.noUiSlider) {  // Check if slider exists and not already initialized
        const difficultyRange = document.getElementById('difficulty-range');
        const difficultyMinInput = document.getElementById('min-difficulty-input');
        const difficultyMaxInput = document.getElementById('max-difficulty-input');

        noUiSlider.create(difficultySlider, {
            start: [20, 30],
            connect: true,
            range: {
                'min': 0,
                'max': 100
            },
            format: {
                to: (value) => Math.round(value),
                from: (value) => parseFloat(value)
            }
        });

        // Add event listener for difficulty slider updates
        difficultySlider.noUiSlider.on('update', function(values) {
            difficultyRange.textContent = `Min: ${values[0]}, Max: ${values[1]}`;
            difficultyMinInput.value = Math.round(values[0]);
            difficultyMaxInput.value = Math.round(values[1]);
        });
    }

    const heightSlider = document.getElementById('height-slider');
    if (heightSlider && !heightSlider.noUiSlider) {  // Check if slider exists and not already initialized
        const maxHeightInput = document.getElementById('max_height');
        const maxHeightValue = document.getElementById('max-height-value');

        noUiSlider.create(heightSlider, {
            start: [3],
            range: {
                'min': 3,
                'max': 15
            },
            step: 1,
            behaviour: 'drag-tap'
        });

        heightSlider.noUiSlider.on('update', function(values) {
            const value = Math.round(values[0]);
            maxHeightInput.value = value;
            if (maxHeightValue) {
                maxHeightValue.textContent = value;
            }
        });
    }

    // Mutually exclusive checkboxes for Include/Exclude tricks
    const includeCheckboxes = document.querySelectorAll('input[name="include_tricks"]');
    const excludeCheckboxes = document.querySelectorAll('input[name="exclude_tricks"]');

    function updateCheckboxState(sourceCheckbox, targetCheckboxes) {
        const value = sourceCheckbox.value;
        targetCheckboxes.forEach(target => {
            if (target.value === value) {
                target.disabled = sourceCheckbox.checked;
                if (sourceCheckbox.checked) {
                    target.checked = false;
                }
            }
        });
    }

    includeCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', () => updateCheckboxState(checkbox, excludeCheckboxes));
    });

    excludeCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', () => updateCheckboxState(checkbox, includeCheckboxes));
    });

    // Toggle Route Visibility
    function toggle_route(container_id) {
        const container = document.getElementById(container_id);
        if (container.style.display === 'none' || container.style.display === '') {
            container.style.display = 'block';
        } else {
            container.style.display = 'none';
        }
    }

    // Prop selection handling
    const propOptions = document.querySelectorAll('.prop-option');
    const propInputs = document.querySelectorAll('.prop-option-input');

    // Function to update selected state
    function updateSelectedState() {
        propOptions.forEach(option => {
            const input = option.querySelector('.prop-option-input');
            if (input.checked) {
                option.classList.add('selected');
            } else {
                option.classList.remove('selected');
            }
        });
    }

    // Set initial state
    updateSelectedState();

    // Add click event listeners to all prop options
    propOptions.forEach(option => {
        option.addEventListener('click', function(e) {
            // Allow default behavior for label-like elements and set the radio programmatically
            const input = this.querySelector('.prop-option-input');
            if (!input) return;
            // If input is already checked, do nothing
            if (!input.checked) {
                input.checked = true;
                // Dispatch a change event so other listeners react
                input.dispatchEvent(new Event('change', { bubbles: true }));
            }
            updateSelectedState();
        });
    });

    // Add change event listeners to all radio inputs
    propInputs.forEach(input => {
        input.addEventListener('change', updateSelectedState);
    });
}

// Initialize now if document already loaded, otherwise wait for DOMContentLoaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initMainJS);
} else {
    initMainJS();
}