// Navigation functionality
document.addEventListener('DOMContentLoaded', function() {
    const dropdowns = document.querySelectorAll('.dropdown');
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const mainNav = document.querySelector('.main-nav');
    let isMobile = window.innerWidth <= 1024;

    // Toggle mobile menu
    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', function() {
            this.classList.toggle('active');
            mainNav.classList.toggle('active');
            document.body.style.overflow = mainNav.classList.contains('active') ? 'hidden' : '';
        });
    }

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
        // For mobile, the entire list item is the trigger area for dropdowns
        // But we need to distinguish between clicking the link and clicking to toggle dropdown
        
        // Find the text node and the arrow
        const navItemText = dropdown.childNodes[0];
        const arrow = dropdown.querySelector('.dropdown-arrow');
        
        if (arrow) {
            arrow.addEventListener('click', (e) => {
                if (isMobile) {
                    e.preventDefault();
                    e.stopPropagation();
                    closeOtherDropdowns(dropdown);
                    dropdown.classList.toggle('active');
                }
            });
        }
        
        // Also allow clicking the parent li to toggle on mobile if it's not a link click
        dropdown.addEventListener('click', (e) => {
            if (isMobile && e.target === dropdown) {
                e.preventDefault();
                closeOtherDropdowns(dropdown);
                dropdown.classList.toggle('active');
            }
        });
    });

    // Close dropdowns when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.dropdown') && !e.target.closest('.mobile-menu-btn')) {
            // Only close dropdowns on desktop, or if clicking outside nav on mobile
            if (!isMobile || !e.target.closest('.main-nav')) {
                dropdowns.forEach(dropdown => {
                    dropdown.classList.remove('active');
                });
            }
        }
        
        // Close mobile menu when clicking outside
        if (isMobile && mainNav.classList.contains('active') &&
            !e.target.closest('.main-nav') && !e.target.closest('.mobile-menu-btn')) {
            mobileMenuBtn.classList.remove('active');
            mainNav.classList.remove('active');
            document.body.style.overflow = '';
        }
    });

    // Handle window resize
    window.addEventListener('resize', () => {
        const newIsMobile = window.innerWidth <= 1024;
        if (newIsMobile !== isMobile) {
            isMobile = newIsMobile;
            // Reset all dropdowns when switching between mobile and desktop
            dropdowns.forEach(dropdown => {
                dropdown.classList.remove('active');
            });
            
            // Reset mobile menu state
            if (!isMobile) {
                if (mobileMenuBtn) mobileMenuBtn.classList.remove('active');
                if (mainNav) mainNav.classList.remove('active');
                document.body.style.overflow = '';
            }
        }
    });
});