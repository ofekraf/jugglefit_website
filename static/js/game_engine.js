/**
 * Generic single-task-at-a-time game loop shared by all crowd games.
 *
 * GameEngine.start({game, renderCard, keymap, loggedIn})
 *   renderCard(task, answer) → DOM node; call answer(payload) to submit.
 *
 * Gamification: per-set score, streak with multiplier, instant flash
 * feedback (✓ / ✗ / +N), best-streak persisted in localStorage.
 */
(function () {
    'use strict';

    const $ = id => document.getElementById(id);
    const cardEl   = () => $('card');
    const progEl   = () => $('progress');
    const flagEl   = () => $('flag_area');
    const relEl    = () => $('reliability_strip');
    const flashEl  = () => $('flash');

    function esc(s) {
        return String(s == null ? '' : s).replace(/[&<>"']/g, c => (
            {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]
        ));
    }

    function selectedProp() {
        const el = document.querySelector('.prop-option-input:checked');
        return el ? el.value : 'balls';
    }

    function ssxOn() {
        const cb = document.getElementById('toggle-siteswap-x-checkbox');
        return !!(cb && cb.checked);
    }

    /**
     * Render a trick label that participates in the global siteswap-X toggle.
     *
     * - both name + siteswap → toggle swaps between them (siteswap formatted)
     * - only name           → always show the name, toggle has no effect
     * - only siteswap       → always show the formatted siteswap, toggle has no effect
     */
    function renderTrick(t) {
        const hasName = !!t.name;
        const hasSS   = !!t.siteswap_x;
        const fmtSS   = (s) => (typeof window.formatSiteswapX === 'function')
            ? window.formatSiteswapX(s) : esc(s);

        // Only one representation exists → show it plain. Do NOT wrap in
        // .trick-container/.trick-name/.trick-siteswap-x so the global
        // toggle function leaves it alone.
        if (hasName !== hasSS) {
            return hasName
                ? `<span class="trick-only">${esc(t.name)}</span>`
                : `<span class="trick-only trick-ss-only">${fmtSS(t.siteswap_x)}</span>`;
        }
        if (!hasName && !hasSS) {
            return `<span class="trick-only">?</span>`;
        }

        // Both exist → emit both spans so toggleSiteswapXEverywhere() can flip.
        const showSS = ssxOn();
        return `<span class="trick-container"><span class="trick-main">`
            + `<span class="trick-name" style="${showSS ? 'display:none' : ''}">${esc(t.name)}</span>`
            + `<span class="trick-siteswap-x" style="${showSS ? '' : 'display:none'}">${fmtSS(t.siteswap_x)}</span>`
            + `</span></span>`;
    }

    function renderProgress(i, n) {
        let html = '';
        for (let k = 0; k < n; k++) {
            const cls = k < i ? 'done' : (k === i ? 'current' : '');
            html += `<span class="dot ${cls}"></span>`;
        }
        progEl().innerHTML = html;
    }

    // ---- score / streak ----------------------------------------------------
    function bestKey(game) { return 'jf_best_streak_' + game; }
    function getBest(game) { return parseInt(localStorage.getItem(bestKey(game)) || '0', 10); }
    function setBest(game, v) { localStorage.setItem(bestKey(game), String(v)); }

    function paintScore(state) {
        if ($('score_val'))  $('score_val').textContent  = state.score;
        if ($('streak_val')) $('streak_val').textContent = state.streak;
        if ($('best_val'))   $('best_val').textContent   = state.best;
    }

    function flash(kind, text) {
        const el = flashEl();
        if (!el) return;
        el.className = 'feedback-flash show ' + kind;
        el.textContent = text;
        setTimeout(() => { el.className = 'feedback-flash'; el.textContent = ''; }, 450);
    }

    function award(state, result, game) {
        // Decide outcome from server response.
        let outcome = 'neutral';   // neutral | hit | miss
        if (typeof result.correct === 'boolean') {
            outcome = result.correct ? 'hit' : 'miss';
        }
        if (outcome === 'hit') {
            state.streak += 1;
            const pts = 10 + Math.min(40, (state.streak - 1) * 5);
            state.score += pts;
            if (state.streak > state.best) { state.best = state.streak; setBest(game, state.best); }
            flash('correct', '+' + pts);
            const sp = $('streak_pill');
            if (sp) { sp.classList.add('hot'); setTimeout(() => sp.classList.remove('hot'), 400); }
        } else if (outcome === 'miss') {
            state.streak = 0;
            flash('wrong', '✗');
        } else {
            state.score += 5;
            flash('neutral', '+5');
        }
        paintScore(state);
    }

    // ---- flag UI -----------------------------------------------------------
    const REASON_LABELS = {
        not_a_trick: 'Not a real trick',
        duplicate:   'Duplicate',
        offensive:   'Offensive / spam',
        wrong_prop:  'Wrong prop / count'
    };

    function renderFlag(task, opts, advance) {
        const area = flagEl();
        if (!area) return;
        if (!task.flaggable) { area.innerHTML = ''; return; }
        if (!opts.loggedIn) {
            area.innerHTML = '<span title="Log in to flag bad tricks">⚑</span>';
            return;
        }
        const reasons = window.JF_FLAG_REASONS || Object.keys(REASON_LABELS);
        area.innerHTML = `<span class="flag-menu" id="flag_menu">
            <button type="button" id="flag_btn">⚑ Bad trick</button>
            <span class="flag-options">
                ${reasons.map(r =>
                    `<button type="button" data-reason="${r}">${esc(REASON_LABELS[r] || r)}</button>`
                ).join('')}
            </span>
        </span>`;
        const menu = $('flag_menu');
        $('flag_btn').addEventListener('click', e => {
            e.stopPropagation();
            menu.classList.toggle('open');
        });
        document.addEventListener('click', () => menu.classList.remove('open'), {once: true});
        menu.querySelectorAll('[data-reason]').forEach(b =>
            b.addEventListener('click', () => {
                menu.classList.remove('open');
                area.innerHTML = '<span>⚑ Thanks — flagged.</span>';
                fetch('/api/games/flag', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({task_id: task.task_id, reason: b.dataset.reason})
                }).catch(() => {}).finally(advance);
            }));
    }

    function refreshReliability() {
        fetch('/api/games/me').then(r => r.json()).then(d => {
            if (!d.logged_in) { relEl().textContent = ''; return; }
            relEl().textContent =
                `${d.n_harder + d.n_tagging + d.n_throw} answers · ` +
                `reliability ${Math.round(d.reliability * 100)}%`;
        }).catch(() => {});
    }

    // ---- main loop ---------------------------------------------------------
    function start(opts) {
        let tasks = [];
        let idx = 0;
        let busy = false;
        const keymap = opts.keymap || {};
        const state = { score: 0, streak: 0, best: getBest(opts.game) };
        paintScore(state);

        function loadSet() {
            cardEl().innerHTML = '<p>Loading…</p><div id="flash" class="feedback-flash"></div>';
            flagEl().innerHTML = '';
            state.score = 0; state.streak = 0; paintScore(state);
            fetch(`/api/games/${opts.game}/next_set?prop=${encodeURIComponent(selectedProp())}`)
                .then(r => r.json())
                .then(d => {
                    tasks = d.tasks || [];
                    idx = 0;
                    if (!tasks.length) {
                        renderProgress(0, 0);
                        cardEl().innerHTML = `<div class="set-done">
                            <p>Nothing to play for this prop right now.</p>
                            <a class="primary-button" href="/contribute/add_tricks">Add a trick</a>
                        </div>`;
                        return;
                    }
                    show();
                })
                .catch(() => { cardEl().innerHTML = '<p>Failed to load set.</p>'; });
        }

        function show() {
            if (idx >= tasks.length) {
                renderProgress(tasks.length, tasks.length);
                flagEl().innerHTML = '';
                const newBest = state.streak >= state.best && state.best > 0;
                cardEl().innerHTML = `<div class="set-done">
                    <div>Set complete!</div>
                    <div class="big">🎉 ${state.score} pts</div>
                    <div>Best streak: <strong>${state.best}</strong>${newBest ? ' — new record!' : ''}</div>
                    <p style="margin-top:1rem">
                        <button id="next_set_btn" class="primary-button">Next set ▶</button>
                        <a class="secondary-button" href="/contribute/games/?prop=${encodeURIComponent(selectedProp())}">Other games</a>
                    </p>
                </div>`;
                $('next_set_btn').addEventListener('click', loadSet);
                refreshReliability();
                return;
            }
            const task = tasks[idx];
            renderProgress(idx, tasks.length);
            const node = opts.renderCard(task, payload => answer(payload));
            cardEl().innerHTML = '';
            cardEl().appendChild(node);
            // re-attach flash overlay (cardEl was cleared)
            const f = document.createElement('div');
            f.id = 'flash'; f.className = 'feedback-flash';
            cardEl().appendChild(f);
            renderFlag(task, opts, () => { idx++; show(); });
        }

        function answer(payload) {
            if (busy || idx >= tasks.length) return;
            busy = true;
            const task = tasks[idx];
            fetch('/api/games/answer', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({task_id: task.task_id, payload: payload})
            })
            .then(r => r.json())
            .then(res => award(state, res || {}, opts.game))
            .catch(() => {})
            .finally(() => {
                busy = false;
                idx++;
                setTimeout(show, 300);  // let the flash land before swapping card
            });
        }

        document.addEventListener('keydown', e => {
            if (e.target.matches('input,textarea')) return;
            if (!(e.key in keymap)) return;
            const p = keymap[e.key];
            if (p) { e.preventDefault(); answer(p); }
        });
        document.querySelectorAll('input[name="prop"]').forEach(r =>
            r.addEventListener('change', loadSet));
        const ssCb = document.getElementById('toggle-siteswap-x-checkbox');
        if (ssCb && typeof window.toggleSiteswapXEverywhere === 'function') {
            ssCb.addEventListener('change', window.toggleSiteswapXEverywhere);
        }

        refreshReliability();
        loadSet();
    }

    window.GameEngine = { start, esc, renderTrick };
})();
