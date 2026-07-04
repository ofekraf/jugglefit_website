/**
 * Generic single-task-at-a-time game loop shared by all crowd games.
 *
 * GameEngine.start({game, renderCard, keymap, loggedIn, onCardMounted?, onResult?})
 *   renderCard(task, answer) → DOM node; call answer(payload) to submit.
 *
 * Gamification: per-set score with instant +N flash, level bar fed by
 * /api/games/me, badge-unlock toasts, and an impact summary on the
 * set-done screen. No streak mechanics.
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

    // ---- score / level -----------------------------------------------------
    let ME = null;           // last /api/games/me payload
    let BADGE_META = {};

    function paintScore(state) {
        if ($('score_val')) $('score_val').textContent = state.score;
    }

    function paintLevel(d) {
        const bar = $('level_bar'), lbl = $('level_label');
        if (!bar || !lbl || !d || !d.level) return;
        const L = d.level;
        lbl.innerHTML = `<strong>Lv ${L.level}</strong> · ${esc(L.title)}`
            + (L.next_at != null
               ? ` <span class="muted">· ${L.to_next} to ${esc(L.next_title)}</span>`
               : ' <span class="muted">· max</span>');
        bar.style.width = Math.round(L.pct * 100) + '%';
    }

    function flash(kind, text) {
        const el = flashEl();
        if (!el) return;
        el.className = 'feedback-flash show ' + kind;
        el.textContent = text;
        setTimeout(() => { el.className = 'feedback-flash'; el.textContent = ''; }, 450);
    }

    function toast(html) {
        let host = $('toast_host');
        if (!host) {
            host = document.createElement('div');
            host.id = 'toast_host';
            host.className = 'toast-host';
            document.body.appendChild(host);
        }
        const t = document.createElement('div');
        t.className = 'toast';
        t.innerHTML = html;
        host.appendChild(t);
        requestAnimationFrame(() => t.classList.add('show'));
        setTimeout(() => {
            t.classList.remove('show');
            setTimeout(() => t.remove(), 300);
        }, 3500);
    }

    function toastBadges(ids) {
        (ids || []).forEach(id => {
            const m = BADGE_META[id] || {};
            toast(`<span class="badge-emoji">${m.emoji || '🏅'}</span>
                   <span><strong>${esc(m.label || id)}</strong><br>
                   <small>${esc(m.desc || '')}</small></span>`);
        });
    }

    function award(state, result) {
        let outcome = 'neutral';
        if (typeof result.correct === 'boolean') {
            outcome = result.correct ? 'hit' : 'miss';
        }
        if (outcome === 'hit') {
            state.score += 10;
            flash('correct', '+10');
        } else if (outcome === 'miss') {
            flash('wrong', '✗');
        } else {
            state.score += 5;
            flash('neutral', '+5');
        }
        paintScore(state);
        if (result.new_badges && result.new_badges.length) {
            toastBadges(result.new_badges);
            refreshMe();   // level may have changed too
        }
    }

    // ---- flag UI -----------------------------------------------------------
    const REASON_LABELS = {
        invalid:     'Not a valid trick',
        not_a_trick: 'Not a valid trick',   // legacy alias
        duplicate:   'Duplicate',
        offensive:   'Offensive / spam',
        wrong_prop:  'Wrong prop / count'
    };

    function renderFlag(task, opts, advance) {
        const area = flagEl();
        if (!area) return;
        if (!task.flaggable) { area.innerHTML = ''; return; }
        if (!opts.loggedIn) {
            area.innerHTML = '<span title="Log in to flag invalid tricks">⚑</span>';
            return;
        }
        const reasons = window.JF_FLAG_REASONS || ['invalid','duplicate','offensive','wrong_prop'];
        area.innerHTML = `<span class="flag-menu" id="flag_menu">
            <button type="button" id="flag_btn">⚑ Invalid trick</button>
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

    function refreshMe() {
        return fetch(`/api/games/me?prop=${encodeURIComponent(selectedProp())}`)
            .then(r => r.json()).then(d => {
                ME = d;
                BADGE_META = d.badge_meta || BADGE_META;
                if (!d.logged_in) { if (relEl()) relEl().textContent = ''; return d; }
                if (relEl()) {
                    relEl().textContent =
                        `${d.n_total} answers · reliability ${Math.round(d.reliability * 100)}%`;
                }
                paintLevel(d);
                return d;
            }).catch(() => {});
    }
    // Back-compat alias (harmless if any template still calls it).
    const refreshReliability = refreshMe;

    // ---- main loop ---------------------------------------------------------
    function start(opts) {
        let tasks = [];
        let idx = 0;
        let busy = false;
        const keymap = opts.keymap || {};
        const state = { score: 0 };
        paintScore(state);
        const urlFocus = new URLSearchParams(location.search).get('focus');

        function loadSet() {
            cardEl().innerHTML = '<p>Loading…</p><div id="flash" class="feedback-flash"></div>';
            flagEl().innerHTML = '';
            state.score = 0; paintScore(state);
            const qs = new URLSearchParams({prop: selectedProp()});
            if (urlFocus) qs.set('focus', urlFocus);
            fetch(`/api/games/${opts.game}/next_set?${qs}`)
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

        function renderSetDone() {
            renderProgress(tasks.length, tasks.length);
            flagEl().innerHTML = '';
            cardEl().innerHTML = `<div class="set-done">
                <div>Set complete!</div>
                <div class="big">🎉 ${state.score} pts</div>
                <div class="impact" id="set_impact"><small>…</small></div>
                <p style="margin-top:1rem">
                    <button id="next_set_btn" class="primary-button">Next set ▶</button>
                    <a class="secondary-button" href="/contribute/games/?prop=${encodeURIComponent(selectedProp())}">Other games</a>
                </p>
            </div>`;
            $('next_set_btn').addEventListener('click', loadSet);
            refreshMe().then(d => {
                if (!d || !d.logged_in) return;
                const el = $('set_impact');
                if (!el) return;
                const bits = [];
                if (d.n_tricks_promoted > 0)
                    bits.push(`helped promote <strong>${d.n_tricks_promoted}</strong> trick${d.n_tricks_promoted===1?'':'s'}`);
                bits.push(`rated <strong>${d.pool_rated}</strong>/<strong>${d.pool_size}</strong> ${esc(d.prop)} candidates`);
                bits.push(`Lv <strong>${d.level.level}</strong> ${esc(d.level.title)}`
                    + (d.level.next_at != null ? ` — ${d.level.to_next} to ${esc(d.level.next_title)}` : ''));
                el.innerHTML = bits.join(' · ');
            });
        }

        function show() {
            if (idx >= tasks.length) {
                renderSetDone();
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
            if (typeof opts.onCardMounted === 'function') {
                try { opts.onCardMounted(node, task); } catch (_) {}
            }
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
            .then(res => {
                res = res || {};
                award(state, res);
                let hold = 300;
                if (typeof opts.onResult === 'function') {
                    // onResult may return ms to hold before advancing
                    // (e.g. harder-game 'you vs. crowd' reveal).
                    try { hold = opts.onResult(task, payload, res, cardEl()) || hold; }
                    catch (_) {}
                }
                busy = false;
                idx++;
                setTimeout(show, hold);
            })
            .catch(() => {
                busy = false;
                idx++;
                setTimeout(show, 300);
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

        refreshMe();
        loadSet();
    }

    window.GameEngine = { start, esc, renderTrick, refreshMe, toast };
})();
