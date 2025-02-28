document.addEventListener('DOMContentLoaded', function() {
    // Workout name placeholder handling
    const workoutInput = document.getElementById('route_name');
    if (workoutInput) {
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
    }

    // Slider setup with noUISlider for props
    const propsSlider = document.getElementById('props-slider');
    const minPropsInput = document.getElementById('min_props');
    const maxPropsInput = document.getElementById('max_props');
    const propsRangeValue = document.getElementById('propsRangeValue');
    const maxHeight = document.getElementById('max_height');
    const maxHeightValue = document.getElementById('maxHeightValue');

    if (propsSlider) {
        noUiSlider.create(propsSlider, {
            start: [3, 7],
            connect: true,
            range: {
                'min': 3,
                'max': 9
            },
            step: 1,
            behaviour: 'drag-tap'
        });

        propsSlider.noUiSlider.on('update', function(values, handle) {
            const min = Math.round(values[0]);
            const max = Math.round(values[1]);
            minPropsInput.value = min;
            maxPropsInput.value = max;
            propsRangeValue.textContent = `${min} - ${max}`;
        });
    }

    const heightSlider = document.getElementById('height-slider');
    const maxHeightInput = document.getElementById('max_height');

    if (heightSlider) {
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
            maxHeightValue.textContent = value;
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

    // Stopwatch Functionality
    const stopwatch = document.getElementById('stopwatch');
    const stopwatchToggle = document.getElementById('stopwatch-toggle');
    let time = 10 * 60; // 10 minutes in seconds
    let timer = null;
    let isPaused = true;

    function updateStopwatch() {
        if (!isPaused) {
            time--;
            if (time <= 0) {
                clearInterval(timer);
                stopwatch.textContent = '00:00';
                isPaused = true;
                stopwatchToggle.textContent = 'START';
                return;
            }
            const minutes = Math.floor(time / 60);
            const seconds = time % 60;
            stopwatch.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }
    }

    if (stopwatch && stopwatchToggle) {
        stopwatchToggle.addEventListener('click', function() {
            if (isPaused) {
                timer = setInterval(updateStopwatch, 1000);
                isPaused = false;
                stopwatchToggle.textContent = 'STOP';
            } else {
                clearInterval(timer);
                isPaused = true;
                stopwatchToggle.textContent = 'START';
            }
        });
    }

    // Toggle Route Visibility
    function toggle_route(container_id) {
        const container = document.getElementById(container_id);
        if (container.style.display === 'none' || container.style.display === '') {
            container.style.display = 'block';
        } else {
            container.style.display = 'none';
        }
    }
});