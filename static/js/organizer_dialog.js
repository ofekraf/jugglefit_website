// "Organizer: Run this live event" dialog (templates/macros/organizer_dialog.html).
// The password creates a live final for this route, or resumes the one that
// is already live, then opens its admin view.
(function () {
    'use strict';

    const dialog = document.getElementById('organizer-dialog');
    const form = document.getElementById('organizer-form');
    const errorEl = document.getElementById('organizer-error');
    const submitBtn = document.getElementById('organizer-submit');
    const countInput = document.getElementById('organizer-count');
    const namesInput = document.getElementById('organizer-names');
    const routePayload = JSON.parse(document.getElementById('organizer-config').textContent).route;

    function showError(message) {
        errorEl.textContent = message;
        errorEl.classList.remove('hidden');
    }

    document.querySelectorAll('[data-organizer-open]').forEach(button => {
        button.addEventListener('click', e => {
            e.preventDefault();
            errorEl.classList.add('hidden');
            dialog.showModal();
            document.getElementById('organizer-password').focus();
        });
    });

    document.getElementById('organizer-cancel').addEventListener('click', () => dialog.close());

    form.addEventListener('submit', async e => {
        e.preventDefault();
        errorEl.classList.add('hidden');
        const body = {
            password: document.getElementById('organizer-password').value,
            route: routePayload,
        };
        if (countInput) {
            body.competitor_count = parseInt(countInput.value, 10);
            body.names = namesInput.value.split('\n').map(n => n.trim()).filter(Boolean);
        }
        submitBtn.disabled = true;
        try {
            const res = await fetch('/api/finals', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body),
            });
            if (res.status === 429) {
                showError('Too many attempts. Wait a few seconds and try again.');
                return;
            }
            if (res.status === 404) {
                showError('Live events are not enabled on this server.');
                return;
            }
            const data = await res.json().catch(() => ({}));
            if (!res.ok) {
                showError(data.error || 'Could not start the live event.');
                return;
            }
            window.location.href = data.live_url;
        } catch (err) {
            showError('No connection. Try again.');
        } finally {
            submitBtn.disabled = false;
        }
    });
})();
