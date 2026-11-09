// /feature_requests: submit form, category tabs, upvotes.
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

    // Upvotes (click again = remove)
    function setVoted(btn, voted) {
        btn.classList.toggle('active', voted);
        btn.setAttribute('aria-pressed', voted ? 'true' : 'false');
        btn.querySelector('.fr-vote-label').textContent = voted ? 'Upvoted' : 'Upvote';
    }
    document.querySelectorAll('.fr-vote').forEach(btn => btn.addEventListener('click', async () => {
        const voted = !btn.classList.contains('active');
        const countEl = btn.querySelector('.fr-vote-count');
        const before = Number(countEl.textContent);
        setVoted(btn, voted);
        countEl.textContent = before + (voted ? 1 : -1);
        btn.disabled = true;
        try {
            const res = await fetch(`/api/feature_requests/${btn.dataset.id}/vote`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ voted }),
            });
            if (!res.ok) throw new Error(res.status);
            const data = await res.json();
            countEl.textContent = data.votes;
        } catch (e) {
            setVoted(btn, !voted);
            countEl.textContent = before;
            toast('Could not save your vote. Please try again.');
        } finally {
            btn.disabled = false;
        }
    }));
})();
