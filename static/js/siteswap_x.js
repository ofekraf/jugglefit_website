// Fix for build_route.html: define toggleRouteSiteswapX globally so it can be called from inline HTML and MutationObserver
// Unified toggle for both route and available tricks
function toggleSiteswapXEverywhere() {
    const checked = document.getElementById('toggle-route-siteswap-x-checkbox')?.checked;
    // Route section
    const routeSections = document.getElementById('route-sections');
    if (routeSections) {
        const trickNames = routeSections.querySelectorAll('.trick-name');
        const siteswapXs = routeSections.querySelectorAll('.trick-siteswap-x');
        for (let i = 0; i < trickNames.length; i++) {
            const siteswapText = siteswapXs[i] ? siteswapXs[i].textContent.trim() : '';
            const hasSiteswap = siteswapText !== '' && siteswapText.toLowerCase() !== 'none';
            if (checked && hasSiteswap) {
                trickNames[i].style.display = 'none';
                siteswapXs[i].style.display = '';
            } else {
                trickNames[i].style.display = '';
                if (siteswapXs[i]) siteswapXs[i].style.display = 'none';
            }
        }
    }
    // Available tricks section
    const allTricks = document.getElementById('all_tricks');
    if (allTricks) {
        const trickNames = allTricks.querySelectorAll('.trick-name');
        const siteswapXs = allTricks.querySelectorAll('.trick-siteswap-x');
        for (let i = 0; i < trickNames.length; i++) {
            const siteswapText = siteswapXs[i] ? siteswapXs[i].textContent.trim() : '';
            const hasSiteswap = siteswapText !== '' && siteswapText.toLowerCase() !== 'none';
            if (checked && hasSiteswap) {
                trickNames[i].style.display = 'none';
                siteswapXs[i].style.display = '';
            } else {
                trickNames[i].style.display = '';
                if (siteswapXs[i]) siteswapXs[i].style.display = 'none';
            }
        }
    }
}
window.toggleSiteswapXEverywhere = toggleSiteswapXEverywhere;
