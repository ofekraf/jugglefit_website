// Navigation functionality
document.addEventListener('DOMContentLoaded', function() {
    const dropdowns = document.querySelectorAll('.dropdown');
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const mainNav = document.querySelector('.main-nav');
    let isMobile = window.innerWidth <= 1024;

    // Toggle mobile menu
    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', function() {
            const willBeActive = !mainNav.classList.contains('active');
            this.classList.toggle('active', willBeActive);
            mainNav.classList.toggle('active', willBeActive);
            this.setAttribute('aria-expanded', String(willBeActive));
            document.body.style.overflow = willBeActive ? 'hidden' : '';
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
        // On mobile, the label ("nav-item-toggle") is the trigger area for
        // opening/closing the dropdown; the arrow lives inside it.
        const toggle = dropdown.querySelector('.nav-item-toggle');

        if (toggle) {
            toggle.addEventListener('click', (e) => {
                if (isMobile) {
                    e.preventDefault();
                    e.stopPropagation();
                    const willBeActive = !dropdown.classList.contains('active');
                    closeOtherDropdowns(dropdown);
                    dropdown.classList.toggle('active', willBeActive);
                }
            });
        }
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