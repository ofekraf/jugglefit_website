// Live final grid for /live_event (see blueprints/finals.py).
// Columns = competitors, rows = tricks + "Finished". Everyone polls the
// server state; the admin can also move competitors (drag, tap a cell, or
// the -/+ buttons). Admin actions are queued in localStorage and re-sent in
// order if the network drops, each with the time the admin made it.
(function () {
    'use strict';

    const config = JSON.parse(document.getElementById('live-final-config').textContent);
    const FINAL_ID = config.finalId;
    const IS_ADMIN = config.isAdmin;
    const TRICKS = config.tricks;
    const PROP = config.prop;
    const ROUTE_LENGTH = TRICKS.length;
    const DURATION_MS = (config.durationSeconds || 600) * 1000;
    const POLL_INTERVAL_MS = 3000;
    const POLL_JITTER_MS = 1000;
    const RETRY_DELAY_MS = 2000;
    const QUEUE_KEY = `live-final-queue-${FINAL_ID}`;
    const API = `/api/finals/${encodeURIComponent(FINAL_ID)}`;

    let state = null;           // last state from the server
    let clockOffsetMs = 0;      // server clock - local clock
    let pollTimer = null;
    let queue = loadQueue();    // pending admin actions
    let sending = false;
    let dragging = false;       // a figure is being dragged
    let renderDeferred = false; // a render was skipped during a drag or name edit
    let timeUpRendered = false;

    const grid = document.getElementById('final-grid');
    const statusEl = document.getElementById('final-status');
    const saveStatusEl = document.getElementById('final-save-status');
    const timerEl = document.getElementById('final-timer');

    // ------------------------------------------------------------------
    // server state
    // ------------------------------------------------------------------
    async function poll() {
        pollTimer = null;
        try {
            const since = state ? `?since=${state.version}` : '';
            const res = await fetch(`${API}/state${since}`, { cache: 'no-store' });
            if (res.status === 404) {
                // Final deleted (test cleanup): reload into local mode.
                window.location.reload();
                return;
            }
            if (res.status === 200) {
                const data = await res.json();
                clockOffsetMs = data.server_now - Date.now();
                state = data;
                render();
            }
            setConnection(true);
        } catch (e) {
            setConnection(false);
        }
        schedulePoll();
    }

    function schedulePoll() {
        if (pollTimer || document.hidden) return;
        if (state && state.status === 'ended') return;
        pollTimer = setTimeout(poll, POLL_INTERVAL_MS + Math.random() * POLL_JITTER_MS);
    }

    document.addEventListener('visibilitychange', function () {
        if (document.hidden) {
            clearTimeout(pollTimer);
            pollTimer = null;
        } else {
            poll();
        }
    });

    function setConnection(ok) {
        statusEl.classList.toggle('final-status-offline', !ok);
        if (!ok) {
            statusEl.textContent = 'Connection lost - retrying';
        } else if (state && state.status === 'ended') {
            statusEl.textContent = 'The final has ended';
        } else if (state && state.started_at) {
            statusEl.textContent = 'Live';
        } else {
            statusEl.textContent = 'Waiting for the final to start';
        }
    }

    // ------------------------------------------------------------------
    // admin action queue
    // ------------------------------------------------------------------
    function loadQueue() {
        try {
            return JSON.parse(localStorage.getItem(QUEUE_KEY)) || [];
        } catch (e) {
            return [];
        }
    }

    function saveQueue() {
        try {
            localStorage.setItem(QUEUE_KEY, JSON.stringify(queue));
        } catch (e) { /* private mode: keep the queue in memory only */ }
    }

    function enqueue(action, body) {
        queue.push({ action: action, body: Object.assign({ client_at: Date.now() }, body) });
        saveQueue();
        render();
        sendQueue();
    }

    async function sendQueue() {
        if (sending) return;
        sending = true;
        while (queue.length) {
            updateSaveStatus();
            const item = queue[0];
            let res;
            try {
                res = await fetch(`${API}/${item.action}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(item.body),
                });
            } catch (e) {
                res = null;
            }
            // No connection, server error, or rate limited (429): keep the
            // action and retry; only a definite rejection drops it.
            if (!res || res.status >= 500 || res.status === 429) {
                updateSaveStatus(true);
                await new Promise(r => setTimeout(r, RETRY_DELAY_MS));
                continue;
            }
            queue.shift();
            saveQueue();
            if (!res.ok) {
                let message = 'Action rejected';
                try { message = (await res.json()).error || message; } catch (e) { /* not JSON */ }
                showMessage(message);
            }
        }
        sending = false;
        updateSaveStatus();
        // Pick up the result of the actions at once.
        clearTimeout(pollTimer);
        poll();
    }

    function updateSaveStatus(failed) {
        if (!saveStatusEl) return;
        saveStatusEl.classList.toggle('final-save-failed', !!failed);
        if (!queue.length) {
            saveStatusEl.textContent = 'All changes saved';
        } else if (failed) {
            saveStatusEl.textContent = `Not saved - ${queue.length} waiting, retrying`;
        } else {
            saveStatusEl.textContent = `Saving (${queue.length})...`;
        }
    }

    // Server state with the not-yet-sent admin actions applied on top.
    function effectiveCompetitors() {
        const competitors = state.competitors.map(c => Object.assign({}, c));
        const byId = new Map(competitors.map(c => [c.id, c]));
        queue.forEach(item => {
            const c = byId.get(item.body.competitor_id);
            if (item.action === 'move' && c) {
                c.stage = item.body.to_stage;
                c.finished_at = c.stage >= ROUTE_LENGTH ? item.body.client_at : null;
            } else if (item.action === 'rename' && c) {
                c.name = item.body.name;
            } else if (item.action === 'start') {
                competitors.forEach(x => {
                    if (!x.started_at && (item.body.competitor_id == null || x.id === item.body.competitor_id)) {
                        x.started_at = item.body.client_at;
                    }
                });
            }
        });
        return competitors;
    }

    function moveCompetitor(competitor, toStage) {
        if (toStage < 0 || toStage > ROUTE_LENGTH || toStage === competitor.stage) return;
        if (!competitor.started_at) {
            showMessage(`Start ${competitor.name} first`);
            return;
        }
        enqueue('move', { competitor_id: competitor.id, to_stage: toStage });
    }

    // ------------------------------------------------------------------
    // rendering
    // ------------------------------------------------------------------
    function stickFigure(finished) {
        const ns = 'http://www.w3.org/2000/svg';
        const svg = document.createElementNS(ns, 'svg');
        svg.setAttribute('viewBox', '0 0 24 40');
        svg.setAttribute('class', 'stick-figure' + (finished ? ' stick-figure-finished' : ''));
        svg.setAttribute('aria-hidden', 'true');
        const parts = finished
            // Arms up when finished.
            ? [['circle', { cx: 12, cy: 6, r: 4 }], ['line', { x1: 12, y1: 10, x2: 12, y2: 25 }],
               ['line', { x1: 12, y1: 14, x2: 4, y2: 4 }], ['line', { x1: 12, y1: 14, x2: 20, y2: 4 }],
               ['line', { x1: 12, y1: 25, x2: 5, y2: 38 }], ['line', { x1: 12, y1: 25, x2: 19, y2: 38 }]]
            : [['circle', { cx: 12, cy: 6, r: 4 }], ['line', { x1: 12, y1: 10, x2: 12, y2: 25 }],
               ['line', { x1: 12, y1: 15, x2: 3, y2: 12 }], ['line', { x1: 12, y1: 15, x2: 21, y2: 12 }],
               ['circle', { cx: 3, cy: 9, r: 1.5 }], ['circle', { cx: 21, cy: 9, r: 1.5 }],
               ['circle', { cx: 12, cy: 1.5, r: 1.2 }],
               ['line', { x1: 12, y1: 25, x2: 5, y2: 38 }], ['line', { x1: 12, y1: 25, x2: 19, y2: 38 }]];
        parts.forEach(([tag, attrs]) => {
            const el = document.createElementNS(ns, tag);
            Object.entries(attrs).forEach(([k, v]) => el.setAttribute(k, v));
            svg.appendChild(el);
        });
        return svg;
    }

    function el(tag, className, text) {
        const node = document.createElement(tag);
        if (className) node.className = className;
        if (text != null) node.textContent = text;
        return node;
    }

    // Colored "X n" bar spanning a run of tricks with the same prop count,
    // like the route display (.prop-color-bar in prop-selection.css).
    function propCell(propsCount, rowSpan) {
        const td = el('td', 'final-prop-cell');
        td.rowSpan = rowSpan;
        const bar = el('div', 'prop-color-bar');
        bar.dataset.props = propsCount;
        bar.dataset.propType = PROP;
        const count = el('div', 'prop-count');
        count.appendChild(el('div', 'prop-count-text', `X ${propsCount}`));
        bar.appendChild(count);
        td.appendChild(bar);
        return td;
    }

    function propRunLength(start) {
        let end = start;
        while (end < ROUTE_LENGTH && TRICKS[end].props_count === TRICKS[start].props_count) end++;
        return end - start;
    }

    function trickHeader(trick, index) {
        const th = el('th', 'final-trick-cell');
        th.scope = 'row';
        const main = el('div', 'final-trick-main');
        main.appendChild(el('span', 'final-trick-number', `${index + 1}.`));
        if (window.CreateTrickContainer) {
            main.appendChild(window.CreateTrickContainer(trick.name, trick.comment || '', trick.siteswap_x || '',
                                                         { editable: false }));
        } else {
            main.appendChild(el('span', 'trick-name', trick.name));
        }
        th.appendChild(main);
        return th;
    }

    function render() {
        if (!state) return;
        // Rebuilding the table would cancel a drag or a name edit in progress.
        const active = document.activeElement;
        if (dragging || (active && active.classList.contains('final-name-input'))) {
            renderDeferred = true;
            return;
        }
        renderDeferred = false;
        const competitors = effectiveCompetitors();
        const ended = state.status === 'ended';
        const table = el('table', 'final-table');

        // Header: one column per competitor.
        const thead = el('thead');
        const headRow = el('tr');
        const corner = el('th', 'final-corner', 'Trick');
        corner.colSpan = 2;
        headRow.appendChild(corner);
        competitors.forEach(c => {
            const th = el('th', 'final-competitor-head');
            th.scope = 'col';
            if (IS_ADMIN && !ended) {
                const input = el('input', 'final-name-input');
                input.type = 'text';
                input.maxLength = 50;
                input.value = c.name;
                input.setAttribute('aria-label', 'Competitor name');
                input.addEventListener('keydown', e => { if (e.key === 'Enter') input.blur(); });
                input.addEventListener('blur', () => {
                    const name = input.value.trim();
                    // Let blur finish so render() does not see the input as focused.
                    setTimeout(() => {
                        if (name && name !== c.name) {
                            enqueue('rename', { competitor_id: c.id, name: name });
                        } else if (renderDeferred) {
                            render();
                        }
                    }, 0);
                });
                th.appendChild(input);
                const controls = el('div', 'final-competitor-controls');
                if (!c.started_at) {
                    const start = el('button', 'final-btn final-btn-start', 'Start');
                    start.type = 'button';
                    start.addEventListener('click', () => enqueue('start', { competitor_id: c.id }));
                    controls.appendChild(start);
                } else {
                    const back = el('button', 'final-btn', '-');
                    back.type = 'button';
                    back.title = 'Back one trick';
                    back.disabled = c.stage <= 0;
                    back.addEventListener('click', () => moveCompetitor(c, c.stage - 1));
                    const fwd = el('button', 'final-btn final-btn-forward', '+');
                    fwd.type = 'button';
                    fwd.title = 'Forward one trick';
                    fwd.disabled = c.stage >= ROUTE_LENGTH;
                    fwd.addEventListener('click', () => moveCompetitor(c, c.stage + 1));
                    controls.appendChild(back);
                    controls.appendChild(fwd);
                }
                th.appendChild(controls);
            } else {
                th.appendChild(el('span', 'final-name', c.name));
            }
            headRow.appendChild(th);
        });
        thead.appendChild(headRow);
        table.appendChild(thead);

        // Body: one row per trick, then Finished.
        const tbody = el('tbody');
        for (let stage = 0; stage <= ROUTE_LENGTH; stage++) {
            const row = el('tr', stage === ROUTE_LENGTH ? 'final-finished-row' : '');
            if (stage < ROUTE_LENGTH) {
                if (stage === 0 || TRICKS[stage - 1].props_count !== TRICKS[stage].props_count) {
                    row.appendChild(propCell(TRICKS[stage].props_count, propRunLength(stage)));
                }
                row.appendChild(trickHeader(TRICKS[stage], stage));
            } else {
                const th = el('th', 'final-trick-cell final-finished-label', 'Finished');
                th.scope = 'row';
                th.colSpan = 2;
                row.appendChild(th);
            }
            competitors.forEach(c => {
                const td = el('td', 'final-cell');
                td.dataset.competitorId = c.id;
                td.dataset.stage = stage;
                if (stage < c.stage) td.classList.add('final-cell-done');
                if (stage === c.stage) {
                    td.classList.add('final-cell-current');
                    if (!c.started_at) td.classList.add('final-cell-waiting');
                    const figure = stickFigure(stage === ROUTE_LENGTH);
                    figure.setAttribute('aria-label', c.name);
                    if (IS_ADMIN && !ended) {
                        figure.classList.add('stick-figure-draggable');
                        figure.addEventListener('pointerdown', e => startDrag(e, c));
                    }
                    td.appendChild(figure);
                }
                if (IS_ADMIN && !ended) {
                    td.classList.add('final-cell-admin');
                    td.addEventListener('click', () => moveCompetitor(c, stage));
                }
                row.appendChild(td);
            });
            tbody.appendChild(row);
        }
        table.appendChild(tbody);

        grid.replaceChildren(table);
        if (window.toggleSiteswapXEverywhere) window.toggleSiteswapXEverywhere();

        const startAll = document.getElementById('final-start-all');
        if (startAll) startAll.disabled = ended || competitors.every(c => c.started_at);
        document.querySelectorAll('.final-admin-live-only').forEach(b => { b.disabled = ended; });

        renderPodium(competitors);
        setConnection(true);
        updateTimer();
    }

    // ------------------------------------------------------------------
    // drag (pointer events: works for mouse and touch)
    // ------------------------------------------------------------------
    function startDrag(e, competitor) {
        e.preventDefault();
        e.stopPropagation();
        const figure = e.currentTarget;
        figure.setPointerCapture(e.pointerId);
        figure.classList.add('dragging');
        dragging = true;
        let target = null;

        function cellAt(ev) {
            const hit = document.elementFromPoint(ev.clientX, ev.clientY);
            const cell = hit && hit.closest('.final-cell');
            return cell && Number(cell.dataset.competitorId) === competitor.id ? cell : null;
        }
        function onMove(ev) {
            const cell = cellAt(ev);
            if (cell === target) return;
            if (target) target.classList.remove('drag-over');
            target = cell;
            if (target) target.classList.add('drag-over');
        }
        function onUp(ev) {
            figure.removeEventListener('pointermove', onMove);
            figure.removeEventListener('pointerup', onUp);
            figure.removeEventListener('pointercancel', onUp);
            figure.classList.remove('dragging');
            dragging = false;
            const cell = ev.type === 'pointerup' ? cellAt(ev) : null;
            if (target) target.classList.remove('drag-over');
            if (cell && Number(cell.dataset.stage) !== competitor.stage) {
                moveCompetitor(competitor, Number(cell.dataset.stage));
            } else if (renderDeferred) {
                render();
            }
        }
        figure.addEventListener('pointermove', onMove);
        figure.addEventListener('pointerup', onUp);
        figure.addEventListener('pointercancel', onUp);
    }

    // ------------------------------------------------------------------
    // timer + podium
    // ------------------------------------------------------------------
    function formatDuration(ms) {
        const total = Math.max(0, Math.floor(ms / 1000));
        const minutes = Math.floor(total / 60);
        const seconds = total % 60;
        return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    }

    function updateTimer() {
        if (!timerEl) return;
        if (!state || !state.started_at) {
            timerEl.textContent = formatDuration(DURATION_MS);
            return;
        }
        const end = state.ended_at || (Date.now() + clockOffsetMs);
        const left = state.started_at + DURATION_MS - end;
        timerEl.textContent = left > 0 ? formatDuration(left) : "Time's up!";
        if (left <= 0 && !timeUpRendered) {
            // Non-finishers join the podium when time is up.
            timeUpRendered = true;
            renderPodium(effectiveCompetitors());
        }
    }
    setInterval(updateTimer, 250);

    function renderPodium(competitors) {
        const section = document.getElementById('final-podium');
        const finishers = competitors
            .filter(c => c.finished_at && c.started_at)
            .map(c => ({ c: c, elapsed: c.finished_at - c.started_at }))
            .sort((a, b) => a.elapsed - b.elapsed);
        const timeUp = state.started_at && (Date.now() + clockOffsetMs) > state.started_at + DURATION_MS;
        const showOthers = state.status === 'ended' || timeUp;
        const others = showOthers
            ? competitors.filter(c => !c.finished_at).sort((a, b) => b.stage - a.stage)
            : [];
        const ranking = finishers.map(f => ({ name: f.c.name, result: formatDuration(f.elapsed) }))
            .concat(others.map(c => ({ name: c.name, result: `${c.stage}/${ROUTE_LENGTH}` })));

        section.classList.toggle('hidden', ranking.length === 0);
        for (let place = 1; place <= 3; place++) {
            const entry = ranking[place - 1];
            document.getElementById(`final-podium-name-${place}`).textContent = entry ? entry.name : '-';
            document.getElementById(`final-podium-result-${place}`).textContent = entry ? entry.result : '-';
        }
    }

    // ------------------------------------------------------------------
    // admin toolbar
    // ------------------------------------------------------------------
    function showMessage(message) {
        const toast = el('div', 'toast-notification', message);
        document.body.appendChild(toast);
        setTimeout(() => toast.classList.add('show'), 100);
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    if (IS_ADMIN) {
        const startAll = document.getElementById('final-start-all');
        const endBtn = document.getElementById('final-end');
        const restartBtn = document.getElementById('final-restart');
        if (restartBtn) restartBtn.addEventListener('click', async () => {
            const pending = queue.length ? ` ${queue.length} unsaved change(s) will be lost.` : '';
            if (!window.confirm('Start over? This final ends (its log is kept) and a new one starts '
                                + 'with the same competitors, all back at trick 1.' + pending)) return;
            try {
                const res = await fetch(`${API}/restart`, { method: 'POST' });
                const data = await res.json();
                if (!res.ok) throw new Error(data.error || 'Could not start over');
                queue = [];
                saveQueue();
                window.location.href = data.live_url;
            } catch (e) {
                showMessage(e.message || 'No connection. Try again.');
            }
        });
        if (startAll) startAll.addEventListener('click', () => enqueue('start', {}));
        if (endBtn) endBtn.addEventListener('click', () => {
            if (window.confirm('End the final? The audience banner goes away and moves are locked.')) {
                enqueue('end', {});
            }
        });
        updateSaveStatus();
        if (queue.length) sendQueue();
    }

    const siteswapToggle = document.getElementById('toggle-siteswap-x-checkbox');
    if (siteswapToggle && window.toggleSiteswapXEverywhere) {
        siteswapToggle.addEventListener('change', window.toggleSiteswapXEverywhere);
    }

    poll();
})();
