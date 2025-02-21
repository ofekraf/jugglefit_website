document.addEventListener("DOMContentLoaded", function () {
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