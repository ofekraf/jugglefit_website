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

    // Slider value displays and validation
    const minProps = document.getElementById('min_props');
    const maxProps = document.getElementById('max_props');
    const maxHeight = document.getElementById('max_height');
    const minPropsValue = document.getElementById('minPropsValue');
    const maxPropsValue = document.getElementById('maxPropsValue');
    const maxHeightValue = document.getElementById('maxHeightValue');

    // Initial values
    minPropsValue.textContent = minProps.value;
    maxPropsValue.textContent = maxProps.value;
    maxHeightValue.textContent = maxHeight.value;

    // Update displays and validate min/max props
    minProps.addEventListener('input', function() {
        minPropsValue.textContent = this.value;
        if (parseInt(this.value) > parseInt(maxProps.value)) {
            maxProps.value = this.value;
            maxPropsValue.textContent = this.value;
        }
    });

    maxProps.addEventListener('input', function() {
        maxPropsValue.textContent = this.value;
        if (parseInt(this.value) < parseInt(minProps.value)) {
            minProps.value = this.value;
            minPropsValue.textContent = this.value;
        }
    });

    maxHeight.addEventListener('input', function() {
        maxHeightValue.textContent = this.value;
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