document.addEventListener('DOMContentLoaded', function() {
    // Workout name placeholder handling
    const workoutInput = document.getElementById('workout_name');
    workoutInput.value = workoutInput.placeholder;

    workoutInput.addEventListener('focus', function() {
        if (this.value === this.placeholder) {
            this.value = '';
            this.style.color = 'black';
        }
    });

    workoutInput.addEventListener('blur', function() {
        if (this.value === '') {
            this.value = this.placeholder;
            this.style.color = 'grey';
        }
    });

    // Slider setup with noUISlider for props
    const propsSlider = document.getElementById('props-slider');
    const minPropsInput = document.getElementById('min_props');
    const maxPropsInput = document.getElementById('max_props');
    const propsRangeValue = document.getElementById('propsRangeValue');
    const maxHeight = document.getElementById('max_height');
    const maxHeightValue = document.getElementById('maxHeightValue');

    // Initialize noUISlider
    noUiSlider.create(propsSlider, {
        start: [3, 7], // Initial min and max values
        connect: true,  // Show range between handles
        range: {
            'min': 3,
            'max': 9
        },
        step: 1,        // Move in increments of 1
        behaviour: 'drag-tap' // Allow dragging and tapping
    });

    // Update hidden inputs and display when slider changes
    propsSlider.noUiSlider.on('update', function(values, handle) {
        const min = Math.round(values[0]);
        const max = Math.round(values[1]);
        minPropsInput.value = min;
        maxPropsInput.value = max;
        propsRangeValue.textContent = `${min} - ${max}`;
    });

    const heightSlider = document.getElementById('height-slider');
    const maxHeightInput = document.getElementById('max_height');

    noUiSlider.create(heightSlider, {
        start: [3], // Single value
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
        maxHeightValue.textContent = value;
    });

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
});