// Trick feedback buttons (Dislike / Too hard / Too easy) on /created_route.
// Loaded only for routes this browser generated with /generate_route (the
// server decides; see blueprints/trick_feedback.py). Votes are stored for
// manual review only - they never change trick difficulties automatically.
(function () {
    const cfg = window.TRICK_FEEDBACK;
    if (!cfg) return;

    const votes = Object.assign({}, cfg.votes || {});   // {index: vote}
    const OPTIONS = [
        { vote: 'too_easy', label: 'Too easy', icon: 'fa-solid fa-angles-down' },
        { vote: 'too_hard', label: 'Too hard', icon: 'fa-solid fa-angles-up' },
        { vote: 'dislike', label: 'Dislike', icon: 'fa-regular fa-thumbs-down' },
    ];

    function toast(msg) {
        if (typeof window.showToast === 'function') window.showToast(msg);
    }

    function paint(group, index) {
        group.querySelectorAll('button').forEach(btn => {
            const active = votes[index] === btn.dataset.vote;
            btn.classList.toggle('active', active);
            btn.setAttribute('aria-pressed', active ? 'true' : 'false');
        });
    }

    async function send(group, index, vote) {
        const previous = votes[index];
        const next = previous === vote ? null : vote;   // click again = undo
        if (next) votes[index] = next; else delete votes[index];
        paint(group, index);
        try {
            const res = await fetch('/api/trick_feedback', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ route: cfg.route, trick_index: index, vote: next }),
            });
            if (!res.ok) throw new Error(res.status);
            toast(next ? 'Thanks for the feedback!' : 'Feedback removed');
        } catch (e) {
            if (previous) votes[index] = previous; else delete votes[index];
            paint(group, index);
            toast('Could not save feedback. Please try again.');
        }
    }

    // Called by updateRouteDisplay() (route_helpers.js) for each read-only row.
    window.decorateTrickRow = function (trickContent, trick, index) {
        const group = document.createElement('div');
        group.className = 'trick-feedback no-print';
        group.setAttribute('role', 'group');
        group.setAttribute('aria-label', 'Rate this trick');
        OPTIONS.forEach(opt => {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'trick-feedback-btn';
            btn.dataset.vote = opt.vote;
            btn.title = opt.label;
            btn.setAttribute('aria-label', opt.label);
            btn.innerHTML = `<i class="${opt.icon}" aria-hidden="true"></i>`;
            btn.addEventListener('click', () => send(group, index, opt.vote));
            group.appendChild(btn);
        });
        paint(group, index);
        trickContent.appendChild(group);
    };
})();
