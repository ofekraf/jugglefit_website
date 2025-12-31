/**
 * Verification Game Interaction
 *
 * Handles trick selection, visual feedback, and form validation
 * for the two-round verification game.
 */

document.addEventListener('DOMContentLoaded', function() {
    const trickBoxes = document.querySelectorAll('.trick-box');
    const submitButton = document.querySelector('.submit-button');
    const hiddenInput = document.getElementById('selected-trick-input');
    let selectedBox = null;

    /**
     * Dynamically adjust font size for long trick names
     * Ensures all text remains visible within the fixed-width boxes
     */
    function adjustTrickNameFontSizes() {
        trickBoxes.forEach(box => {
            const trickName = box.querySelector('.trick-name');
            if (!trickName) return;

            // Use textContent to get actual text length (excluding HTML tags)
            const textLength = trickName.textContent.trim().length;

            // Reset to default size first
            trickName.style.fontSize = '';

            // Apply font size based on text length - more aggressive scaling
            if (textLength > 70) {
                trickName.style.fontSize = '0.85rem';
            } else if (textLength > 50) {
                trickName.style.fontSize = '0.95rem';
            } else if (textLength > 35) {
                trickName.style.fontSize = '1.1rem';
            }
            // Default 1.3rem for shorter names (handled by CSS)
        });
    }

    // Adjust font sizes on page load
    adjustTrickNameFontSizes();

    /**
     * Handle trick box selection
     */
    trickBoxes.forEach(box => {
        // Mouse click handler
        box.addEventListener('click', function() {
            selectBox(this);
        });

        // Keyboard handler (Enter or Space)
        box.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                selectBox(this);
            }
        });
    });

    /**
     * Select a trick box and update visual states
     * @param {HTMLElement} box - The trick box element to select
     */
    function selectBox(box) {
        // Remove previous selection state from all boxes
        trickBoxes.forEach(b => {
            b.classList.remove('selected');
            b.classList.remove('unselected');
        });

        // Mark all boxes as unselected first
        trickBoxes.forEach(b => {
            b.classList.add('unselected');
        });

        // Mark clicked box as selected
        box.classList.remove('unselected');
        box.classList.add('selected');
        selectedBox = box;

        // Update hidden input with selection
        const trickPosition = box.getAttribute('data-trick');
        hiddenInput.value = trickPosition;

        // Enable submit button
        submitButton.disabled = false;
    }

    /**
     * Form submission validation
     */
    const form = document.getElementById('verify-form');
    form.addEventListener('submit', function(e) {
        if (!hiddenInput.value) {
            e.preventDefault();
            alert('Please select a trick before submitting');
        }
    });
});
