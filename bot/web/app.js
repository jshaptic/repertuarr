/**
 * Repertuarr Admin — Client-side application logic.
 *
 * Handles tab navigation, data fetching from the admin API, rendering tables
 * and stat cards, user details drill-down, and the LLM conversation modal
 * (including the assistant response that was previously missing).
 */

document.addEventListener('DOMContentLoaded', () => {
    // ── Element references ──────────────────────────────────────────
    const navItems = document.querySelectorAll('.nav-item');
    const tabPanes = document.querySelectorAll('.tab-pane');
    const currentTabTitle = document.getElementById('current-tab-title');
    const currentTabSubtitle = document.getElementById('current-tab-subtitle');
    const backToUsersBtn = document.getElementById('back-to-users');
    const refreshBtn = document.getElementById('refresh-btn');
    const refreshIcon = document.getElementById('refresh-icon');
    const lastRefreshedEl = document.getElementById('last-refreshed');

    // Modal elements
    const modal = document.getElementById('llm-modal');
    const modalCloseBtn = document.getElementById('modal-close');
    const modalTitle = document.getElementById('modal-title');
    const modalBody = document.getElementById('modal-body');
    const modalMeta = document.getElementById('modal-meta');
    const modalTabs = document.getElementById('modal-tabs');

    // Mobile sidebar elements
    const mobileToggle = document.getElementById('mobile-toggle');
    const sidebar = document.getElementById('sidebar');
    const sidebarOverlay = document.getElementById('sidebar-overlay');

    // Tab → subtitle mapping
    const tabSubtitles = {
        'dashboard': 'System overview',
        'users': 'Manage bot users',
        'logs': 'System logs & activity',
        'user-details': 'User profile'
    };

    // ── Tab Navigation ──────────────────────────────────────────────
    function switchTab(targetId, title) {
        navItems.forEach(nav => nav.classList.remove('active'));
        tabPanes.forEach(pane => pane.classList.remove('active'));

        const matchingNav = Array.from(navItems).find(
            nav => nav.getAttribute('data-target') === targetId
        );
        if (matchingNav) matchingNav.classList.add('active');

        document.getElementById(targetId).classList.add('active');
        if (title) currentTabTitle.textContent = title;
        currentTabSubtitle.textContent = tabSubtitles[targetId] || '';
    }

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            switchTab(item.getAttribute('data-target'), item.textContent.trim());
            closeMobileSidebar();
        });
    });

    backToUsersBtn.addEventListener('click', () => {
        switchTab('users', 'Users');
    });

    // ── Detail sub-tab navigation ───────────────────────────────────
    const detailTabs = document.querySelectorAll('.detail-tab');
    const detailPanes = document.querySelectorAll('.detail-tab-pane');
    let pendingSessionExpandId = null;

    function switchLogsSubTab(targetId) {
        const logsPane = document.getElementById('logs');
        if (!logsPane) return;
        const siblingTabs = logsPane.querySelectorAll('.detail-tab');
        const siblingPanes = logsPane.querySelectorAll('.detail-tab-pane');
        siblingTabs.forEach(t => t.classList.remove('active'));
        siblingPanes.forEach(p => p.classList.remove('active'));
        const tab = logsPane.querySelector(`.detail-tab[data-detail-target="${targetId}"]`);
        const pane = document.getElementById(targetId);
        if (tab) tab.classList.add('active');
        if (pane) pane.classList.add('active');
    }

    detailTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetId = tab.getAttribute('data-detail-target');
            const parentPane = tab.closest('.tab-pane');
            const siblingTabs = parentPane.querySelectorAll('.detail-tab');
            const siblingPanes = parentPane.querySelectorAll('.detail-tab-pane');
            
            siblingTabs.forEach(t => t.classList.remove('active'));
            siblingPanes.forEach(p => p.classList.remove('active'));
            
            tab.classList.add('active');
            document.getElementById(targetId).classList.add('active');
        });
    });

    // ── Mobile sidebar ──────────────────────────────────────────────
    function closeMobileSidebar() {
        sidebar.classList.remove('open');
        sidebarOverlay.classList.remove('open');
    }

    mobileToggle.addEventListener('click', () => {
        sidebar.classList.toggle('open');
        sidebarOverlay.classList.toggle('open');
    });

    sidebarOverlay.addEventListener('click', closeMobileSidebar);

    // ── Data fetching ───────────────────────────────────────────────
    refreshBtn.addEventListener('click', () => {
        refreshIcon.classList.add('spin-anim');
        fetchData().finally(() => {
            setTimeout(() => refreshIcon.classList.remove('spin-anim'), 500);
        });
    });

    fetchData();

    /** user_id → display name from the last users fetch. */
    let userNameById = {};

    async function fetchData() {
        try {
            const [usersRes, llmRes, tmdbRes, sessionsRes] = await Promise.all([
                fetch('/admin/api/users'),
                fetch('/admin/api/llm-logs'),
                fetch('/admin/api/tmdb-logs'),
                fetch('/admin/api/sessions')
            ]);

            const users = await usersRes.json();
            const llmLogs = await llmRes.json();
            const tmdbLogs = await tmdbRes.json();
            const sessions = await sessionsRes.json();

            userNameById = Object.fromEntries(
                users.map(u => [u.user_id, u.name || String(u.user_id)])
            );

            renderUsers(users);
            renderSessions(sessions);
            renderGlobalLlmLogs(llmLogs);
            renderTmdbLogs(tmdbLogs);

            // Update dashboard stats
            document.getElementById('stat-users').textContent = users.length || 0;
            const totalReq = users.reduce((sum, u) => sum + (u.requests_count || 0), 0);
            const totalFb = users.reduce((sum, u) => sum + (u.feedback_count || 0), 0);
            document.getElementById('stat-requests').textContent = totalReq;
            document.getElementById('stat-feedback').textContent = totalFb;
            document.getElementById('stat-llm').textContent = llmLogs.length || 0;
            const totalAiCost = users.reduce((sum, u) => sum + (u.llm_cost_usd || 0), 0);
            document.getElementById('stat-ai-cost').textContent = formatCost(totalAiCost);

            // Update last refreshed timestamp
            lastRefreshedEl.textContent = `Updated ${new Date().toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' })}`;

        } catch (error) {
            console.error('Error fetching data:', error);
        }
    }

    // ── User Details drill-down ──────────────────────────────────────
    async function showUserDetails(userId, userName) {
        switchTab('user-details', userName);
        currentTabSubtitle.textContent = 'User profile';

        // Reset sub-tabs to Conversations
        const userPane = document.getElementById('user-details');
        const userDetailTabs = userPane.querySelectorAll('.detail-tab');
        const userDetailPanes = userPane.querySelectorAll('.detail-tab-pane');
        userDetailTabs.forEach(t => t.classList.remove('active'));
        userDetailPanes.forEach(p => p.classList.remove('active'));
        if (userDetailTabs.length > 0) userDetailTabs[0].classList.add('active');
        if (userDetailPanes.length > 0) userDetailPanes[0].classList.add('active');

        // Set avatar initials
        const initials = userName.split(' ').map(w => w[0]).join('').slice(0, 2);
        document.getElementById('detail-avatar').textContent = initials || '?';
        document.getElementById('detail-user-name').textContent = userName;

        try {
            const [mediaRes, llmRes] = await Promise.all([
                fetch(`/admin/api/media-library?user_id=${userId}`),
                fetch(`/admin/api/llm-logs?user_id=${userId}`)
            ]);

            renderMediaLibrary(await mediaRes.json());
            renderUserLlmLogs(await llmRes.json());
        } catch (error) {
            console.error('Error fetching user details:', error);
        }
    }

    // ── Formatting helpers ──────────────────────────────────────────

    /** Format an ISO date string as a relative "time ago" string. */
    function timeAgo(dateString) {
        if (!dateString) return '—';
        const date = new Date(dateString);
        if (isNaN(date)) return dateString;

        const seconds = Math.floor((Date.now() - date.getTime()) / 1000);
        if (seconds < 60) return 'just now';
        if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
        if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
        if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
        return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
    }

    /** Format an ISO date string as a full locale date/time for tooltips. */
    function fullDate(dateString) {
        if (!dateString) return '';
        const parsed = new Date(dateString);
        return isNaN(parsed) ? dateString : parsed.toLocaleString(undefined, {
            year: 'numeric', month: 'short', day: 'numeric',
            hour: '2-digit', minute: '2-digit', second: '2-digit'
        });
    }

    /** Format a duration in ms as a human-readable string. */
    function formatDuration(ms) {
        if (!ms && ms !== 0) return '—';
        if (ms < 1000) return `${ms}ms`;
        return `${(ms / 1000).toFixed(1)}s`;
    }

    /** Format USD cost for display; null/undefined shows em dash. */
    function formatCost(usd) {
        if (usd == null || usd === '') return '—';
        if (usd === 0) return '$0.00';
        if (usd < 0.01) return `$${usd.toFixed(4)}`;
        return `$${usd.toFixed(2)}`;
    }

    /** Format token breakdown (input / output / cached) for a log row. */
    function formatTokenBreakdown(item) {
        if (item.input_tokens == null && item.output_tokens == null) {
            return item.tokens != null ? item.tokens.toLocaleString() : '—';
        }
        const parts = [];
        if (item.input_tokens != null) parts.push(`${item.input_tokens.toLocaleString()} in`);
        if (item.output_tokens != null) parts.push(`${item.output_tokens.toLocaleString()} out`);
        if (item.cached_input_tokens > 0) {
            parts.push(`${item.cached_input_tokens.toLocaleString()} cached`);
        }
        return parts.join(' · ') || '—';
    }

    /** Build an empty-state table row. */
    function emptyRow(colspan, message, iconSvg) {
        const icon = iconSvg || '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" opacity="0.25"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>';
        return `<tr><td colspan="${colspan}" class="empty-state"><div class="empty-state-inner">${icon}<span>${escapeHtml(message)}</span></div></td></tr>`;
    }

    /** Pick a pill color class based on a prompt name. */
    function promptPillClass(promptName) {
        const map = {
            'recommend': 'pill-violet',
            'inquiry': 'pill-blue',
            'intent': 'pill-muted'
        };
        return map[promptName] || 'pill-muted';
    }

    /** Short display form of a session UUID. */
    function shortSessionId(sessionId) {
        if (!sessionId) return '—';
        return sessionId.slice(0, 8);
    }

    /** Resolve a user display name from the users cache. */
    function userDisplayName(userId) {
        if (userId == null || userId === '') return '—';
        return userNameById[userId] || String(userId);
    }

    /** Pick a pill color class for a session status. */
    function sessionStatusPillClass(status) {
        if (status === 'failed') return 'pill-rose';
        if (status === 'in_progress') return 'pill-amber';
        return 'pill-emerald';
    }

    /** Resolve prompt name from a log row (new or legacy). */
    function logPromptName(item) {
        if (item.prompt_name) return item.prompt_name;
        if (item.intent === 'CLASSIFY_INTENT') return 'intent';
        if (item.intent === 'INQUIRY') return 'inquiry';
        if (item.intent === 'RECOMMEND') return 'recommend';
        return item.intent || '—';
    }

    // ── Render: Users table ─────────────────────────────────────────
    function renderUsers(data) {
        document.getElementById('users-count').textContent = data.length || 0;
        const tbody = document.getElementById('users-tbody');

        if (!data || data.length === 0) {
            tbody.innerHTML = emptyRow(7, 'No users found');
            return;
        }

        tbody.innerHTML = '';
        data.forEach(item => {
            const tr = document.createElement('tr');

            const radarrTooltip = `Radarr: ${item.radarr_name}\nProfile: ${item.radarr_profile}`;
            const sonarrTooltip = `Sonarr: ${item.sonarr_name}\nProfile: ${item.sonarr_profile}`;

            const servicesHtml = `
                <div style="display:flex;gap:10px;align-items:center;">
                    <img src="https://cdn.jsdelivr.net/gh/selfhst/icons/svg/radarr-light-hybrid.svg" alt="Radarr" title="${escapeHtml(radarrTooltip)}" width="18" height="18">
                    <img src="https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/svg/sonarr.svg" alt="Sonarr" title="${escapeHtml(sonarrTooltip)}" width="18" height="18">
                </div>
            `;

            tr.innerHTML = `
                <td style="font-weight:600;color:var(--text-primary)">${escapeHtml(item.name)}</td>
                <td>${servicesHtml}</td>
                <td>${item.requests_count || 0}</td>
                <td>${item.feedback_count || 0}</td>
                <td>${item.llm_count || 0}</td>
                <td style="font-size:0.75rem;font-weight:600">${formatCost(item.llm_cost_usd)}</td>
                <td title="${escapeHtml(fullDate(item.last_active))}">${timeAgo(item.last_active)}</td>
            `;
            tr.addEventListener('click', () => showUserDetails(item.user_id, item.name));
            tbody.appendChild(tr);
        });
    }

    // ── Render: User detail — Media Library (merged requests + feedback) ─
    function renderMediaLibrary(data) {
        document.getElementById('user-media-count').textContent = data.length || 0;
        const tbody = document.getElementById('user-media-tbody');
        if (!data || data.length === 0) {
            tbody.innerHTML = emptyRow(7, 'No media interactions yet');
            return;
        }

        // Helpers for rendering feedback/status/excluded pills
        function requestPill(status) {
            if (!status) return '<span class="pill pill-muted">—</span>';
            const map = {
                'pending': 'pill-amber',
                'notified': 'pill-emerald',
            };
            const cls = map[status.toLowerCase()] || 'pill-muted';
            return `<span class="pill ${cls}">${escapeHtml(status)}</span>`;
        }

        function feedbackPill(type) {
            if (!type) return '<span class="pill pill-muted">—</span>';
            const normalized = type.toLowerCase();
            // Handle both old (dislike/ignore) and new (disliked/ignored) values
            if (normalized === 'watched') {
                return '<span class="pill pill-emerald">👍 Liked</span>';
            } else if (normalized === 'disliked' || normalized === 'dislike') {
                return '<span class="pill pill-rose">👎 Disliked</span>';
            } else if (normalized === 'ignored' || normalized === 'ignore') {
                return '<span class="pill pill-muted">—</span>';
            }
            return `<span class="pill pill-muted">${escapeHtml(type)}</span>`;
        }

        function excludedPill(type) {
            if (!type) return '';
            const normalized = type.toLowerCase();
            if (normalized === 'ignored' || normalized === 'ignore') {
                return '<span class="pill pill-rose">🚫 Excluded</span>';
            }
            return '';
        }

        function idsColumn(tmdb_id, tvdb_id) {
            let parts = [];
            if (tmdb_id) parts.push(`<span class="type-label">TMDB:</span> ${escapeHtml(tmdb_id)}`);
            if (tvdb_id) parts.push(`<span class="type-label">TVDB:</span> ${escapeHtml(tvdb_id)}`);
            return parts.length > 0 ? parts.join('<br>') : '<span class="pill pill-muted">—</span>';
        }

        tbody.innerHTML = data.map(item => `
            <tr>
                <td title="${escapeHtml(fullDate(item.created_at))}">${timeAgo(item.created_at)}</td>
                <td style="font-weight:500;color:var(--text-primary)">${escapeHtml(item.title || '—')}</td>
                <td class="type-label">${escapeHtml(item.media_type || '—')}</td>
                <td style="font-size: 0.85em; color: var(--text-secondary); line-height: 1.4;">${idsColumn(item.tmdb_id, item.tvdb_id)}</td>
                <td>${requestPill(item.request_status)}</td>
                <td>${feedbackPill(item.feedback_type)}</td>
                <td>${excludedPill(item.feedback_type)}</td>
            </tr>
        `).join('');
    }

    // ── Render: User detail — LLM interactions ──────────────────────
    function renderUserLlmLogs(data) {
        const filteredData = data.filter(item =>
            item.prompt_name !== 'intent' && item.intent !== 'CLASSIFY_INTENT'
        );
        document.getElementById('user-llm-count').textContent = filteredData.length || 0;
        const tbody = document.getElementById('user-llm-tbody');

        if (!filteredData || filteredData.length === 0) {
            tbody.innerHTML = emptyRow(5, 'No conversations yet');
            return;
        }

        tbody.innerHTML = '';
        filteredData.forEach((item, idx) => {
            // Parse suggested media items from LLM response
            let mediaItems = [];
            if (item.llm_response) {
                try {
                    const parsed = JSON.parse(item.llm_response);
                    if (parsed && Array.isArray(parsed.items) && parsed.items.length > 0) {
                        mediaItems = parsed.items;
                    }
                } catch (e) { /* non-JSON response, ignore */ }
            }

            const hasMedia = mediaItems.length > 0;
            const chevronHtml = hasMedia
                ? `<span class="expand-chevron"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg></span>`
                : '';

            // Main row
            const mainRow = document.createElement('tr');
            mainRow.className = hasMedia ? 'expandable-row' : '';
            mainRow.innerHTML = `
                <td>${chevronHtml}</td>
                <td title="${escapeHtml(fullDate(item.created_at))}">${timeAgo(item.created_at)}</td>
                <td style="max-width:300px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:var(--text-primary)" title="${escapeHtml(item.user_message)}">${escapeHtml(item.user_message || '—')}</td>
                <td><span class="pill ${promptPillClass(logPromptName(item))}">${escapeHtml(logPromptName(item))}</span></td>
                <td style="font-size:0.75rem;font-weight:600">${formatCost(item.cost_usd)}</td>
            `;
            tbody.appendChild(mainRow);

            // Expanded row with suggested media sub-table
            if (hasMedia) {
                const expandRow = document.createElement('tr');
                expandRow.className = 'expanded-content';
                const expandCell = document.createElement('td');
                expandCell.colSpan = 5;

                let tableRows = mediaItems.map(media => `
                    <tr>
                        <td>${escapeHtml(media.title || '—')}</td>
                        <td>${escapeHtml(media.original_title || '—')}</td>
                        <td>${media.year || '—'}</td>
                        <td class="overview-cell" title="${escapeHtml(media.overview || '')}">${escapeHtml(media.overview || '—')}</td>
                    </tr>
                `).join('');

                expandCell.innerHTML = `
                    <div class="expanded-inner">
                        <h4>Suggested Media (${mediaItems.length})</h4>
                        <table class="suggested-table">
                            <thead><tr><th>Title</th><th>Original Title</th><th>Year</th><th>Overview</th></tr></thead>
                            <tbody>${tableRows}</tbody>
                        </table>
                    </div>
                `;
                expandRow.appendChild(expandCell);
                tbody.appendChild(expandRow);

                // Toggle expand on click
                mainRow.addEventListener('click', () => {
                    mainRow.classList.toggle('expanded');
                    expandRow.classList.toggle('open');
                });
            }
        });
    }

    // ── Render: Sessions table ─────────────────────────────────────
    const SESSION_COLSPAN = 8;
    const chevronSvg = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>';

    function buildSessionTimelineElement(detail) {
        const wrapper = document.createElement('div');
        wrapper.className = 'session-timeline';

        const entries = [
            ...detail.llm_logs.map(log => ({ type: 'llm', created_at: log.created_at, data: log })),
            ...detail.tmdb_logs.map(log => ({ type: 'tmdb', created_at: log.created_at, data: log }))
        ].sort((a, b) => new Date(a.created_at) - new Date(b.created_at));

        if (entries.length === 0) {
            wrapper.innerHTML = '<div class="empty-state"><div class="empty-state-inner"><span>No activity recorded for this session</span></div></div>';
            return wrapper;
        }

        entries.forEach(entry => {
            const row = document.createElement('div');
            row.className = `timeline-entry timeline-${entry.type}`;

            if (entry.type === 'llm') {
                const log = entry.data;
                const promptName = logPromptName(log);
                row.innerHTML = `
                    <div class="timeline-marker"></div>
                    <div class="timeline-content">
                        <div class="timeline-header">
                            <span class="pill ${promptPillClass(promptName)}" style="font-size:0.625rem">AI · ${escapeHtml(promptName)}</span>
                            <span class="timeline-meta">${escapeHtml(log.model || '—')} · ${formatTokenBreakdown(log)} · ${formatCost(log.cost_usd)} · ${formatDuration(log.duration_ms)}</span>
                        </div>
                        <button class="timeline-view-btn" type="button">View details</button>
                    </div>
                `;
                row.querySelector('.timeline-view-btn').addEventListener('click', (e) => {
                    e.stopPropagation();
                    openLlmModal(log);
                });
            } else {
                const log = entry.data;
                const statusClass = log.status_code >= 200 && log.status_code < 300 ? 'pill-emerald' : 'pill-rose';
                row.innerHTML = `
                    <div class="timeline-marker"></div>
                    <div class="timeline-content">
                        <div class="timeline-header">
                            <span class="pill pill-blue" style="font-size:0.625rem">TMDB</span>
                            <span class="timeline-meta">${escapeHtml(log.endpoint || '—')} · <span class="pill ${statusClass}" style="font-size:0.625rem">${log.status_code || 'Error'}</span> · ${formatDuration(log.duration_ms)}</span>
                        </div>
                        <button class="timeline-view-btn" type="button">View details</button>
                    </div>
                `;
                row.querySelector('.timeline-view-btn').addEventListener('click', (e) => {
                    e.stopPropagation();
                    openTmdbModal({ ...log, user_id: detail.session.user_id });
                });
            }

            wrapper.appendChild(row);
        });

        return wrapper;
    }

    async function loadSessionExpandContent(sessionId, container) {
        container.innerHTML = '<div class="expanded-inner"><span class="session-loading">Loading calls…</span></div>';
        try {
            const res = await fetch(`/admin/api/sessions/${sessionId}`);
            if (!res.ok) throw new Error('Session not found');
            const detail = await res.json();
            const inner = document.createElement('div');
            inner.className = 'expanded-inner';
            inner.innerHTML = `
                <h4>Calls (${(detail.llm_logs.length + detail.tmdb_logs.length)})</h4>
            `;
            inner.appendChild(buildSessionTimelineElement(detail));
            container.innerHTML = '';
            container.appendChild(inner);
            container.dataset.loaded = 'true';
        } catch (error) {
            console.error('Error loading session:', error);
            container.innerHTML = '<div class="expanded-inner"><span class="session-loading">Failed to load session calls</span></div>';
        }
    }

    async function toggleSessionRow(mainRow, expandRow, sessionId) {
        const isOpen = mainRow.classList.contains('expanded');
        if (isOpen) {
            mainRow.classList.remove('expanded');
            expandRow.classList.remove('open');
            return;
        }

        mainRow.classList.add('expanded');
        expandRow.classList.add('open');

        const container = expandRow.querySelector('td');
        if (container.dataset.loaded !== 'true') {
            await loadSessionExpandContent(sessionId, container);
        }
    }

    async function expandSessionById(sessionId) {
        const mainRow = document.querySelector(`#sessions-tbody tr[data-session-id="${sessionId}"]`);
        if (!mainRow) return false;
        const expandRow = mainRow.nextElementSibling;
        if (!mainRow.classList.contains('expanded')) {
            await toggleSessionRow(mainRow, expandRow, sessionId);
        } else {
            const container = expandRow.querySelector('td');
            if (container.dataset.loaded !== 'true') {
                await loadSessionExpandContent(sessionId, container);
            }
        }
        mainRow.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        return true;
    }

    function navigateToSession(sessionId) {
        pendingSessionExpandId = sessionId;
        switchTab('logs', 'Logs');
        switchLogsSubTab('logs-sessions');
        expandSessionById(sessionId).then(found => {
            if (!found) pendingSessionExpandId = sessionId;
        });
    }

    function renderSessions(data) {
        document.getElementById('sessions-count').textContent = data.length || 0;
        const tbody = document.getElementById('sessions-tbody');

        if (!data || data.length === 0) {
            tbody.innerHTML = emptyRow(SESSION_COLSPAN, 'No sessions yet');
            return;
        }

        tbody.innerHTML = '';
        data.forEach(item => {
            const mainRow = document.createElement('tr');
            mainRow.className = 'expandable-row';
            mainRow.dataset.sessionId = item.id;
            const statusClass = sessionStatusPillClass(item.status);
            mainRow.innerHTML = `
                <td><span class="expand-chevron">${chevronSvg}</span></td>
                <td title="${escapeHtml(fullDate(item.created_at))}">${timeAgo(item.created_at)}</td>
                <td style="color:var(--text-primary);font-weight:500">${escapeHtml(userDisplayName(item.user_id))}</td>
                <td style="font-size:0.7rem;font-family:monospace;color:var(--text-muted)" title="${escapeHtml(item.id || '')}">${escapeHtml(shortSessionId(item.id))}</td>
                <td><span class="pill ${statusClass}" style="font-size:0.625rem">${escapeHtml(item.status || '—')}</span></td>
                <td style="max-width:220px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:var(--text-primary)" title="${escapeHtml(item.user_message)}">${escapeHtml(item.user_message || '—')}</td>
                <td style="font-size:0.75rem">${formatDuration(item.duration_ms)}</td>
                <td style="font-size:0.75rem;font-weight:600">${formatCost(item.llm_cost_usd)}</td>
            `;

            const expandRow = document.createElement('tr');
            expandRow.className = 'expanded-content';
            const expandCell = document.createElement('td');
            expandCell.colSpan = SESSION_COLSPAN;
            expandRow.appendChild(expandCell);

            mainRow.addEventListener('click', () => toggleSessionRow(mainRow, expandRow, item.id));
            tbody.appendChild(mainRow);
            tbody.appendChild(expandRow);
        });

        if (pendingSessionExpandId) {
            const id = pendingSessionExpandId;
            pendingSessionExpandId = null;
            expandSessionById(id);
        }
    }

    // ── Render: Global AI Activity table ────────────────────────────
    function renderGlobalLlmLogs(data) {
        document.getElementById('llm-count').textContent = data.length || 0;
        const tbody = document.getElementById('llm-tbody');

        if (!data || data.length === 0) {
            tbody.innerHTML = emptyRow(9, 'No AI activity yet');
            return;
        }

        tbody.innerHTML = '';
        data.forEach(item => {
            const promptName = logPromptName(item);
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td title="${escapeHtml(fullDate(item.created_at))}">${timeAgo(item.created_at)}</td>
                <td style="color:var(--text-primary);font-weight:500">${escapeHtml(userDisplayName(item.user_id))}</td>
                <td>${escapeHtml(promptName)}</td>
                <td style="font-size:0.7rem;font-family:monospace;color:var(--text-muted)" title="${escapeHtml(item.session_id || '')}">${escapeHtml(shortSessionId(item.session_id))}</td>
                <td style="font-size:0.75rem;color:var(--text-muted)">${escapeHtml(item.model || '—')}</td>
                <td style="font-size:0.75rem;font-weight:600">${formatTokenBreakdown(item)}</td>
                <td style="font-size:0.75rem;font-weight:600">${formatCost(item.cost_usd)}</td>
                <td style="font-size:0.75rem">${formatDuration(item.duration_ms)}</td>
                <td>
                    <button class="btn-view" title="View conversation">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                    </button>
                </td>
            `;
            tr.addEventListener('click', (e) => {
                if (e.target.closest('.session-link')) return;
                openLlmModal(item);
            });
            const sessionCell = tr.children[3];
            if (item.session_id) {
                sessionCell.classList.add('session-link');
                sessionCell.style.cursor = 'pointer';
                sessionCell.style.color = 'var(--accent-blue)';
                sessionCell.addEventListener('click', (e) => {
                    e.stopPropagation();
                    navigateToSession(item.session_id);
                });
            }
            tbody.appendChild(tr);
        });
    }

    // ── Render: TMDB Logs table ────────────────────────────────────
    function renderTmdbLogs(data) {
        document.getElementById('tmdb-count').textContent = data.length || 0;
        const tbody = document.getElementById('tmdb-tbody');

        if (!data || data.length === 0) {
            tbody.innerHTML = emptyRow(7, 'No TMDB activity yet');
            return;
        }

        tbody.innerHTML = '';
        data.forEach(item => {
            const tr = document.createElement('tr');
            
            // Status pill
            const statusClass = item.status_code >= 200 && item.status_code < 300 ? 'pill-emerald' : 'pill-rose';
            
            tr.innerHTML = `
                <td title="${escapeHtml(fullDate(item.created_at))}">${timeAgo(item.created_at)}</td>
                <td style="color:var(--text-primary);font-weight:500">${escapeHtml(userDisplayName(item.user_id))}</td>
                <td style="color:var(--text-primary);font-weight:500;max-width:250px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="${escapeHtml(item.endpoint)}">${escapeHtml(item.endpoint || '—')}</td>
                <td style="font-size:0.7rem;font-family:monospace;color:var(--text-muted)" title="${escapeHtml(item.session_id || '')}">${escapeHtml(shortSessionId(item.session_id))}</td>
                <td><span class="pill ${statusClass}">${item.status_code || 'Error'}</span></td>
                <td style="font-size:0.75rem">${formatDuration(item.duration_ms)}</td>
                <td>
                    <button class="btn-view" title="View details">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                    </button>
                </td>
            `;
            tr.addEventListener('click', () => openTmdbModal(item));
            const sessionCell = tr.children[3];
            if (item.session_id) {
                sessionCell.style.cursor = 'pointer';
                sessionCell.style.color = 'var(--accent-blue)';
                sessionCell.addEventListener('click', (e) => {
                    e.stopPropagation();
                    navigateToSession(item.session_id);
                });
            }
            tbody.appendChild(tr);
        });
    }

    // ── Modal Logic ─────────────────────────────────────────────────
    modalCloseBtn.addEventListener('click', () => modal.classList.remove('open'));
    modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.classList.remove('open');
    });
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.classList.contains('open')) {
            modal.classList.remove('open');
        }
    });

    modalTabs.querySelectorAll('.modal-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            modalTabs.querySelectorAll('.modal-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            const target = tab.getAttribute('data-modal-tab');
            modalBody.querySelectorAll('.modal-pane').forEach(p => {
                p.classList.toggle('active', p.getAttribute('data-pane') === target);
            });
        });
    });

    function setModalTabVisibility(show) {
        modalTabs.style.display = show ? 'flex' : 'none';
        modalTabs.querySelectorAll('.modal-tab').forEach((t, i) => t.classList.toggle('active', i === 0));
    }

    /**
     * Open the LLM conversation modal for a given log item.
     */
    function openLlmModal(logItem) {
        const promptName = logPromptName(logItem);
        modalTitle.textContent = 'AI Activity';
        setModalTabVisibility(true);

        modalMeta.innerHTML = `
            <div class="meta-item"><strong>Prompt:</strong> <span class="pill ${promptPillClass(promptName)}" style="font-size:0.625rem">${escapeHtml(promptName)}</span></div>
            <div class="meta-item"><strong>Model:</strong> ${escapeHtml(logItem.model || '—')}</div>
            <div class="meta-item"><strong>Tokens:</strong> ${formatTokenBreakdown(logItem)}</div>
            <div class="meta-item"><strong>Cost:</strong> ${formatCost(logItem.cost_usd)}</div>
            <div class="meta-item"><strong>Duration:</strong> ${formatDuration(logItem.duration_ms)}</div>
        `;

        modalBody.innerHTML = '';

        const processedPane = document.createElement('div');
        processedPane.className = 'modal-pane active';
        processedPane.setAttribute('data-pane', 'processed');

        let messages = [];
        if (logItem.llm_request) {
            try {
                const parsed = JSON.parse(logItem.llm_request);
                if (Array.isArray(parsed)) {
                    messages = parsed;
                } else {
                    messages = [{ role: 'user', content: logItem.llm_request }];
                }
            } catch (e) {
                messages = [{ role: 'user', content: logItem.llm_request }];
            }
        }

        if (messages.length === 0 && !logItem.llm_response) {
            processedPane.innerHTML = '<div class="empty-state"><div class="empty-state-inner"><span>No messages logged for this interaction</span></div></div>';
        } else {
            messages.forEach(msg => {
                processedPane.appendChild(createChatBubble(msg.role || 'unknown', msg.content || ''));
            });
            if (logItem.llm_response) {
                processedPane.appendChild(createChatBubble('assistant', logItem.llm_response));
            }
        }

        const rawPane = document.createElement('div');
        rawPane.className = 'modal-pane';
        rawPane.setAttribute('data-pane', 'raw');

        if (logItem.raw_request || logItem.raw_response) {
            if (logItem.raw_request) {
                rawPane.appendChild(createChatBubble('request', formatJsonBlock(logItem.raw_request)));
            }
            if (logItem.raw_response) {
                rawPane.appendChild(createChatBubble('response', formatJsonBlock(logItem.raw_response)));
            }
        } else {
            rawPane.innerHTML = '<div class="empty-state"><div class="empty-state-inner"><span>No raw API data recorded (legacy log entry)</span></div></div>';
        }

        modalBody.appendChild(processedPane);
        modalBody.appendChild(rawPane);
        modal.classList.add('open');
    }

    function formatJsonBlock(text) {
        try {
            return JSON.stringify(JSON.parse(text), null, 2);
        } catch (e) {
            return text;
        }
    }

    function openTmdbModal(item) {
        modalTitle.textContent = 'TMDB Request';
        setModalTabVisibility(false);
        const statusClass = item.status_code >= 200 && item.status_code < 300 ? 'pill-emerald' : 'pill-rose';
        modalMeta.innerHTML = `
            <div class="meta-item"><strong>User:</strong> ${escapeHtml(userDisplayName(item.user_id))}</div>
            <div class="meta-item"><strong>Endpoint:</strong> <code style="font-size:0.75rem">${escapeHtml(item.endpoint || '—')}</code></div>
            <div class="meta-item"><strong>Status:</strong> <span class="pill ${statusClass}" style="font-size:0.625rem">${item.status_code || 'Error'}</span></div>
            <div class="meta-item"><strong>Duration:</strong> ${formatDuration(item.duration_ms)}</div>
        `;

        modalBody.innerHTML = '';

        const paramsText = item.params ? formatJsonBlock(item.params) : 'None';
        modalBody.appendChild(createChatBubble('request', `GET ${item.endpoint || ''}\n\nParams:\n${paramsText}`));

        if (item.error) {
            modalBody.appendChild(createChatBubble('error', item.error));
        } else if (item.response_body) {
            modalBody.appendChild(createChatBubble('response', formatJsonBlock(item.response_body)));
        } else {
            modalBody.appendChild(createChatBubble('response', '(empty response)'));
        }

        modal.classList.add('open');
    }

    /** Create a styled chat bubble DOM element for the modal. */
    function createChatBubble(role, content) {
        const div = document.createElement('div');
        div.className = `chat-message chat-${role}`;

        const roleLabel = document.createElement('div');
        roleLabel.className = 'chat-role';
        roleLabel.textContent = role;

        const body = document.createElement('pre');
        body.style.whiteSpace = 'pre-wrap';
        body.style.wordBreak = 'break-word';
        body.style.margin = '0';
        body.style.fontFamily = 'inherit';
        body.style.fontSize = 'inherit';
        body.textContent = content;

        div.appendChild(roleLabel);
        div.appendChild(body);
        return div;
    }



    // ── Utilities ───────────────────────────────────────────────────
    function escapeHtml(unsafe) {
        if (unsafe == null) return '';
        return String(unsafe)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
});
