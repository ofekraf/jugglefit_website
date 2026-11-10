// /feature_requests: submit form, category tabs, upvote / dislike.
(function () {
    const form = document.getElementById('fr-form');
    const statusEl = document.getElementById('fr-status');
    const submitBtn = document.getElementById('fr-submit');
    const bugOnly = form.querySelector('.fr-bug-only');

    function toast(msg) {
        if (typeof window.showToast === 'function') window.showToast(msg);
    }

    function selectedCategory() {
        const el = form.querySelector('input[name="category"]:checked');
        return el ? el.value : '';
    }

    function syncBugFields() {
        bugOnly.classList.toggle('hidden', selectedCategory() !== 'website_bug');
    }
    form.querySelectorAll('input[name="category"]').forEach(r => r.addEventListener('change', syncBugFields));
    syncBugFields();

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const fd = new FormData(form);
        const payload = {
            category: selectedCategory(),
            title: (fd.get('title') || '').trim(),
            body: (fd.get('body') || '').trim(),
            contact: (fd.get('contact') || '').trim(),
            page: selectedCategory() === 'website_bug' ? (fd.get('page') || '').trim() : '',
            website: fd.get('website') || '',
        };
        if (payload.title.length < 3) {
            statusEl.textContent = 'Please add a short title.';
            statusEl.className = 'fr-status error';
            document.getElementById('fr-title').focus();
            return;
        }
        submitBtn.disabled = true;
        statusEl.textContent = 'Sending...';
        statusEl.className = 'fr-status';
        try {
            const res = await fetch('/api/feature_requests', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });
            const data = await res.json().catch(() => ({}));
            if (!res.ok) throw new Error(data.error || 'Could not send. Please try again.');
            form.reset();
            syncBugFields();
            statusEl.textContent = 'Thanks! We\'ll review it soon. Approved requests appear in the list below.';
            statusEl.className = 'fr-status success';
        } catch (err) {
            statusEl.textContent = err.message;
            statusEl.className = 'fr-status error';
        } finally {
            submitBtn.disabled = false;
        }
    });

    // Category tabs
    const tabs = document.querySelectorAll('.fr-tab');
    tabs.forEach(tab => tab.addEventListener('click', () => {
        tabs.forEach(t => {
            const on = t === tab;
            t.classList.toggle('active', on);
            t.setAttribute('aria-selected', on ? 'true' : 'false');
        });
        document.querySelectorAll('.fr-list').forEach(list => {
            list.classList.toggle('hidden', list.dataset.list !== tab.dataset.tab);
        });
    }));

    // Upvote / Dislike: one choice per browser, tap the active one again to undo.
    const LABELS = { up: ['Like', 'Liked'], down: ['Dislike', 'Disliked'] };

    function currentVote(group) {
        const active = group.querySelector('.fr-vote.active');
        return active ? active.dataset.vote : 'none';
    }

    function render(group, vote, counts) {
        group.querySelectorAll('.fr-vote').forEach(btn => {
            const on = btn.dataset.vote === vote;
            btn.classList.toggle('active', on);
            btn.setAttribute('aria-pressed', on ? 'true' : 'false');
            btn.querySelector('.fr-vote-label').textContent = LABELS[btn.dataset.vote][on ? 1 : 0];
            const icon = btn.querySelector('i');           // filled icon = your vote
            icon.classList.toggle('fas', on);
            icon.classList.toggle('far', !on);
        });
        group.querySelector('.fr-vote-up .fr-vote-count').textContent = counts.votes;
        group.querySelector('.fr-vote-down .fr-vote-count').textContent = counts.dislikes;
    }

    function readCounts(group) {
        return {
            votes: Number(group.querySelector('.fr-vote-up .fr-vote-count').textContent),
            dislikes: Number(group.querySelector('.fr-vote-down .fr-vote-count').textContent),
        };
    }

    document.querySelectorAll('.fr-votes').forEach(group => {
        group.querySelectorAll('.fr-vote').forEach(btn => btn.addEventListener('click', async () => {
            const before = currentVote(group);
            const beforeCounts = readCounts(group);
            const next = before === btn.dataset.vote ? 'none' : btn.dataset.vote;

            // Optimistic update
            const guess = { ...beforeCounts };
            if (before === 'up') guess.votes--;
            if (before === 'down') guess.dislikes--;
            if (next === 'up') guess.votes++;
            if (next === 'down') guess.dislikes++;
            render(group, next, guess);
            group.querySelectorAll('.fr-vote').forEach(b => { b.disabled = true; });
            try {
                const res = await fetch(`/api/feature_requests/${group.dataset.id}/vote`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ vote: next }),
                });
                if (!res.ok) throw new Error(res.status);
                const data = await res.json();
                render(group, data.vote, data);
            } catch (e) {
                render(group, before, beforeCounts);
                toast('Could not save your vote. Please try again.');
            } finally {
                group.querySelectorAll('.fr-vote').forEach(b => { b.disabled = false; });
            }
        }));
    });
})();
