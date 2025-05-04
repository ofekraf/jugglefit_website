// Navigation functionality
document.addEventListener('DOMContentLoaded', function() {
    const dropdowns = document.querySelectorAll('.dropdown');
    const isMobile = window.innerWidth <= 768;

    // Function to close all dropdowns except the specified one
    function closeOtherDropdowns(currentDropdown) {
        dropdowns.forEach(dropdown => {
            if (dropdown !== currentDropdown) {
                dropdown.classList.remove('active');
            }
        });
    }

    // Add click event listeners to dropdowns
    dropdowns.forEach(dropdown => {
        const link = dropdown.querySelector('a');
        
        // Handle click on the link
        link.addEventListener('click', (e) => {
            if (isMobile) {
                // If clicking the arrow (::after), prevent default and toggle dropdown
                if (e.target === link || e.target.parentElement === link) {
                    // Check if the click was on the text or the arrow
                    const rect = link.getBoundingClientRect();
                    const arrowWidth = 20; // Approximate width of the arrow
                    const clickX = e.clientX - rect.left;
                    
                    if (clickX > rect.width - arrowWidth) {
                        // Click was on the arrow
                        e.preventDefault();
                        closeOtherDropdowns(dropdown);
                        dropdown.classList.toggle('active');
                    }
                    // If click was on the text, let it navigate normally
                }
            }
        });
    });

    // Close dropdowns when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.dropdown')) {
            dropdowns.forEach(dropdown => {
                dropdown.classList.remove('active');
            });
        }
    });

    // Handle window resize
    window.addEventListener('resize', () => {
        const newIsMobile = window.innerWidth <= 768;
        if (newIsMobile !== isMobile) {
            // Reset all dropdowns when switching between mobile and desktop
            dropdowns.forEach(dropdown => {
                dropdown.classList.remove('active');
            });
        }
    });
}); 