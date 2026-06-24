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
    const modalBody = document.getElementById('modal-body');
    const modalMeta = document.getElementById('modal-meta');

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
    let refreshInterval = setInterval(fetchData, 30000);

    refreshBtn.addEventListener('click', () => {
        refreshIcon.classList.add('spin-anim');
        fetchData().finally(() => {
            setTimeout(() => refreshIcon.classList.remove('spin-anim'), 500);
        });
        clearInterval(refreshInterval);
        refreshInterval = setInterval(fetchData, 30000);
    });

    fetchData();

    async function fetchData() {
        try {
            const [usersRes, llmRes, tmdbRes] = await Promise.all([
                fetch('/admin/api/users'),
                fetch('/admin/api/llm-logs'),
                fetch('/admin/api/tmdb-logs')
            ]);

            const users = await usersRes.json();
            const llmLogs = await llmRes.json();
            const tmdbLogs = await tmdbRes.json();

            renderUsers(users);
            renderGlobalLlmLogs(llmLogs);
            renderTmdbLogs(tmdbLogs);

            // Update dashboard stats
            document.getElementById('stat-users').textContent = users.length || 0;
            const totalReq = users.reduce((sum, u) => sum + (u.requests_count || 0), 0);
            const totalFb = users.reduce((sum, u) => sum + (u.feedback_count || 0), 0);
            document.getElementById('stat-requests').textContent = totalReq;
            document.getElementById('stat-feedback').textContent = totalFb;
            document.getElementById('stat-llm').textContent = llmLogs.length || 0;

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

    /** Build an empty-state table row. */
    function emptyRow(colspan, message, iconSvg) {
        const icon = iconSvg || '<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" opacity="0.25"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>';
        return `<tr><td colspan="${colspan}" class="empty-state"><div class="empty-state-inner">${icon}<span>${escapeHtml(message)}</span></div></td></tr>`;
    }

    /** Pick a pill color class based on an intent string. */
    function intentPillClass(intent) {
        const map = {
            'RECOMMEND': 'pill-violet',
            'ADD_MEDIA': 'pill-emerald',
            'INQUIRY': 'pill-blue',
            'CLASSIFY_INTENT': 'pill-muted'
        };
        return map[intent] || 'pill-muted';
    }

    // ── Render: Users table ─────────────────────────────────────────
    function renderUsers(data) {
        document.getElementById('users-count').textContent = data.length || 0;
        const tbody = document.getElementById('users-tbody');

        if (!data || data.length === 0) {
            tbody.innerHTML = emptyRow(6, 'No users found');
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
        const filteredData = data.filter(item => item.intent !== 'CLASSIFY_INTENT');
        document.getElementById('user-llm-count').textContent = filteredData.length || 0;
        const tbody = document.getElementById('user-llm-tbody');

        if (!filteredData || filteredData.length === 0) {
            tbody.innerHTML = emptyRow(4, 'No conversations yet');
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
                <td><span class="pill ${intentPillClass(item.intent)}">${escapeHtml(item.intent || '—')}</span></td>
            `;
            tbody.appendChild(mainRow);

            // Expanded row with suggested media sub-table
            if (hasMedia) {
                const expandRow = document.createElement('tr');
                expandRow.className = 'expanded-content';
                const expandCell = document.createElement('td');
                expandCell.colSpan = 4;

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

    // ── Render: Global AI Activity table ────────────────────────────
    function renderGlobalLlmLogs(data) {
        document.getElementById('llm-count').textContent = data.length || 0;
        const tbody = document.getElementById('llm-tbody');

        if (!data || data.length === 0) {
            tbody.innerHTML = emptyRow(7, 'No AI activity yet');
            return;
        }

        tbody.innerHTML = '';
        data.forEach(item => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td title="${escapeHtml(fullDate(item.created_at))}">${timeAgo(item.created_at)}</td>
                <td style="color:var(--text-primary);font-weight:500">${item.user_id || '—'}</td>
                <td><span class="pill ${intentPillClass(item.intent)}">${escapeHtml(item.intent || '—')}</span></td>
                <td style="font-size:0.75rem;color:var(--text-muted)">${escapeHtml(item.model || '—')}</td>
                <td style="font-size:0.75rem;font-weight:600">${item.tokens != null ? item.tokens.toLocaleString() : '—'}</td>
                <td style="font-size:0.75rem">${formatDuration(item.duration_ms)}</td>
                <td>
                    <button class="btn-view" title="View conversation">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                    </button>
                </td>
            `;
            tr.addEventListener('click', () => openLlmModal(item));
            tbody.appendChild(tr);
        });
    }

    // ── Render: TMDB Logs table ────────────────────────────────────
    function renderTmdbLogs(data) {
        document.getElementById('tmdb-count').textContent = data.length || 0;
        const tbody = document.getElementById('tmdb-tbody');

        if (!data || data.length === 0) {
            tbody.innerHTML = emptyRow(5, 'No TMDB activity yet');
            return;
        }

        tbody.innerHTML = '';
        data.forEach(item => {
            const tr = document.createElement('tr');
            
            // Status pill
            const statusClass = item.status_code >= 200 && item.status_code < 300 ? 'pill-emerald' : 'pill-rose';
            
            tr.innerHTML = `
                <td title="${escapeHtml(fullDate(item.created_at))}">${timeAgo(item.created_at)}</td>
                <td style="color:var(--text-primary);font-weight:500;max-width:250px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="${escapeHtml(item.endpoint)}">${escapeHtml(item.endpoint || '—')}</td>
                <td><span class="pill ${statusClass}">${item.status_code || 'Error'}</span></td>
                <td style="font-size:0.75rem">${formatDuration(item.duration_ms)}</td>
                <td>
                    <button class="btn-view" title="View details">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                    </button>
                </td>
            `;
            tr.addEventListener('click', () => openTmdbModal(item));
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

    /**
     * Open the LLM conversation modal for a given log item.
     *
     * Renders:
     *  1. A metadata bar (model, tokens, duration, intent)
     *  2. All messages from `llm_request` (system/user prompts sent to the LLM)
     *  3. The assistant's response from `llm_response` — this was the missing piece!
     */
    function openLlmModal(logItem) {
        // ── Render metadata bar ──
        modalMeta.innerHTML = `
            <div class="meta-item"><strong>Intent:</strong> <span class="pill ${intentPillClass(logItem.intent)}" style="font-size:0.625rem">${escapeHtml(logItem.intent || '—')}</span></div>
            <div class="meta-item"><strong>Model:</strong> ${escapeHtml(logItem.model || '—')}</div>
            <div class="meta-item"><strong>Tokens:</strong> ${logItem.tokens != null ? logItem.tokens.toLocaleString() : '—'}</div>
            <div class="meta-item"><strong>Duration:</strong> ${formatDuration(logItem.duration_ms)}</div>
        `;

        // ── Render conversation messages ──
        modalBody.innerHTML = '';
        let messages = [];

        if (logItem.llm_request) {
            try {
                const parsed = JSON.parse(logItem.llm_request);
                if (Array.isArray(parsed)) {
                    messages = parsed;
                } else {
                    // Single string prompt (e.g. RECOMMEND uses a rendered template)
                    messages = [{ role: 'user', content: logItem.llm_request }];
                }
            } catch (e) {
                // Not JSON — treat as a raw prompt string
                messages = [{ role: 'user', content: logItem.llm_request }];
            }
        }

        if (messages.length === 0 && !logItem.llm_response) {
            modalBody.innerHTML = '<div class="empty-state"><div class="empty-state-inner"><span>No messages logged for this interaction</span></div></div>';
            modal.classList.add('open');
            return;
        }

        // Render each input message (system prompt, user message, etc.)
        messages.forEach(msg => {
            modalBody.appendChild(createChatBubble(msg.role || 'unknown', msg.content || ''));
        });

        // Show the raw response as-is (no formatting/pretty-printing)
        if (logItem.llm_response) {
            modalBody.appendChild(createChatBubble('assistant', logItem.llm_response));
        }

        modal.classList.add('open');
    }

    function openTmdbModal(item) {
        // Render metadata bar
        const statusClass = item.status_code >= 200 && item.status_code < 300 ? 'pill-emerald' : 'pill-rose';
        modalMeta.innerHTML = `
            <div class="meta-item"><strong>Status:</strong> <span class="pill ${statusClass}" style="font-size:0.625rem">${item.status_code || 'Error'}</span></div>
            <div class="meta-item"><strong>Duration:</strong> ${formatDuration(item.duration_ms)}</div>
        `;

        // Render request/response in modal
        modalBody.innerHTML = '';
        
        let formattedParams = item.params || 'None';
        try {
            if (item.params) {
                formattedParams = JSON.stringify(JSON.parse(item.params), null, 2);
            }
        } catch (e) {}

        let formattedBody = item.response_body || '';
        try {
            if (item.response_body) {
                formattedBody = JSON.stringify(JSON.parse(item.response_body), null, 2);
            }
        } catch (e) {}

        modalBody.appendChild(createChatBubble('user', `Endpoint: ${item.endpoint}\n\nParams:\n${formattedParams}`));
        
        if (item.error) {
            modalBody.appendChild(createChatBubble('assistant', `Error:\n${item.error}`));
        } else if (formattedBody) {
            modalBody.appendChild(createChatBubble('assistant', formattedBody));
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
