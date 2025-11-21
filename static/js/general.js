// Toast notification function
function showToast(message, focusElementId = null) {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.classList.add('show');
    
    // Focus on the specified element if provided
    if (focusElementId) {
        const element = document.getElementById(focusElementId);
        if (element) {
            element.focus();
            element.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Make showToast globally available
if (typeof window !== 'undefined') {
    window.showToast = showToast;
}
