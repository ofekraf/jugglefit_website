// Fix for build_route.html: define toggleRouteSiteswapX globally so it can be called from inline HTML and MutationObserver
function toggleRouteSiteswapX() {
    // Example logic: toggle a class or update the UI for siteswap-x mode
    const checkbox = document.getElementById('toggle-route-siteswap-x-checkbox');
    const routeSections = document.getElementById('route-sections');
    if (!checkbox || !routeSections) return;
    if (checkbox.checked) {
        routeSections.classList.add('siteswap-x-enabled');
    } else {
        routeSections.classList.remove('siteswap-x-enabled');
    }
}
// Make it available globally
window.toggleRouteSiteswapX = toggleRouteSiteswapX;
