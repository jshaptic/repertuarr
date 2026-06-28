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
    const modalContentEl = modal.querySelector('.modal-content');
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
    let latestExclusions = { ttl_hours: null, retained: [], excluded: [] };

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
            const [usersRes, llmRes, tmdbRes, sessionsRes, mediaMgmtRes, mediaServerRes] = await Promise.all([
                fetch('/admin/api/users'),
                fetch('/admin/api/llm-logs'),
                fetch('/admin/api/tmdb-logs'),
                fetch('/admin/api/sessions'),
                fetch('/admin/api/service-logs?services=radarr,sonarr'),
                fetch('/admin/api/service-logs?services=jellyfin'),
            ]);

            const users = await usersRes.json();
            const llmLogs = await llmRes.json();
            const tmdbLogs = await tmdbRes.json();
            const sessions = await sessionsRes.json();
            const mediaMgmtLogs = await mediaMgmtRes.json();
            const mediaServerLogs = await mediaServerRes.json();

            userNameById = Object.fromEntries(
                users.map(u => [u.user_id, u.name || String(u.user_id)])
            );

            renderUsers(users);
            renderSessions(sessions);
            renderGlobalLlmLogs(llmLogs);
            renderTmdbLogs(tmdbLogs);
            renderMediaMgmtLogs(mediaMgmtLogs);
            renderMediaServerLogs(mediaServerLogs);

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

        // Reset sub-tabs to Chat
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
            const [mediaRes, chatRes, exclRes] = await Promise.all([
                fetch(`/admin/api/media-library?user_id=${userId}`),
                fetch(`/admin/api/chat?user_id=${userId}`),
                fetch(`/admin/api/exclusions?user_id=${userId}`)
            ]);

            renderMediaLibrary(await mediaRes.json());
            renderChatTranscript(await chatRes.json());
            renderExclusions(await exclRes.json());
        } catch (error) {
            console.error('Error fetching user details:', error);
        }
    }

    /** Render the full chat transcript as alternating user/assistant bubbles. */
    function renderChatTranscript(messages) {
        const container = document.getElementById('user-chat-transcript');
        const countEl = document.getElementById('user-chat-count');
        if (!container) return;

        const rows = Array.isArray(messages) ? messages : [];
        if (countEl) countEl.textContent = rows.length;

        if (rows.length === 0) {
            container.innerHTML = '<div class="chat-empty">No stored messages for this user.</div>';
            return;
        }

        // Related entities are stashed by row id so action buttons can open them.
        const carouselsByRow = {};
        const sessionsByRow = {};

        container.innerHTML = rows.map(m => {
            const role = m.role === 'user' ? 'user' : 'assistant';
            const speaker = role === 'user' ? 'User' : 'Repertuarr';
            const intentLabel = role === 'user' && m.intent ? formatIntentLabel(m.intent) : '';
            const intentClassName = intentClass(m.intent);
            const edited = m.edited_at
                ? '<span class="chat-transcript-edited" title="Edited">edited</span>'
                : '';
            const ts = fullDate(m.created_at);

            const metaParts = [];
            if (intentLabel) {
                metaParts.unshift(`<span class="chat-transcript-intent">${escapeHtml(intentLabel)}</span>`);
            }
            if (role === 'user' && m.session_id) {
                sessionsByRow[m.id] = m.session_id;
                metaParts.push(`
                    <button class="chat-transcript-view chat-transcript-session" type="button" data-session-row-id="${m.id}" title="${escapeHtml(m.session_id)}">
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3h18v18H3z"/><path d="M7 8h10"/><path d="M7 12h10"/><path d="M7 16h6"/></svg>
                        View session
                    </button>
                `);
            }
            if (role === 'user' && m.cost_usd != null) {
                metaParts.push(`<span class="chat-transcript-cost" title="LLM cost for this turn">${formatCost(m.cost_usd)}</span>`);
            }
            if (edited) metaParts.push(edited);
            const metaHtml = metaParts.length
                ? `<div class="chat-transcript-meta">${metaParts.join('')}</div>`
                : '';

            let viewBtn = '';
            const items = m.carousel && Array.isArray(m.carousel.items) ? m.carousel.items : [];
            if (role === 'assistant' && items.length) {
                carouselsByRow[m.id] = m.carousel;
                viewBtn = `
                    <button class="chat-transcript-view" type="button" data-carousel-id="${m.id}">
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
                        View ${items.length} titles
                    </button>`;
            }

            return `
                <div class="chat-transcript-row chat-transcript-${role} ${intentClassName}">
                    <div class="chat-transcript-stack">
                        <article class="chat-transcript-bubble">
                            <div class="chat-transcript-head">
                                <span class="chat-transcript-speaker">${speaker}</span>
                                <span class="chat-transcript-time">${escapeHtml(ts)}</span>
                            </div>
                            <div class="chat-transcript-text">${escapeHtml(m.text || '')}</div>
                        </article>
                        ${viewBtn}
                        ${metaHtml}
                    </div>
                </div>`;
        }).join('');

        container.querySelectorAll('.chat-transcript-view[data-carousel-id]').forEach(btn => {
            btn.addEventListener('click', () => {
                const carousel = carouselsByRow[btn.getAttribute('data-carousel-id')];
                if (carousel) openCarouselModal(carousel);
            });
        });
        container.querySelectorAll('.chat-transcript-session').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const sessionId = sessionsByRow[btn.getAttribute('data-session-row-id')];
                if (sessionId) openSessionModal(sessionId);
            });
        });
    }

    /** Render recommendation exclusion summary cards for the current user. */
    function renderExclusions(data) {
        const payload = data && typeof data === 'object' ? data : {};
        const retained = Array.isArray(payload.retained) ? payload.retained : [];
        const excluded = Array.isArray(payload.excluded) ? payload.excluded : [];
        const ttlHours = payload.ttl_hours;
        latestExclusions = { ttl_hours: ttlHours, retained, excluded };

        const retainedSub = document.getElementById('retained-sub');
        if (retainedSub) {
            retainedSub.textContent = ttlHours
                ? `Recently shown titles hidden for ${ttlHours}h.`
                : 'Recently shown titles hidden until cooldown expires.';
        }

        const retainedCount = document.getElementById('retained-count');
        if (retainedCount) retainedCount.textContent = retained.length;
        const excludedCount = document.getElementById('excluded-count');
        if (excludedCount) excludedCount.textContent = excluded.length;

        const retainedBtn = document.getElementById('view-retained');
        if (retainedBtn) {
            retainedBtn.disabled = retained.length === 0;
            retainedBtn.onclick = () => openExclusionModal('retained');
        }

        const excludedBtn = document.getElementById('view-excluded');
        if (excludedBtn) {
            excludedBtn.disabled = excluded.length === 0;
            excludedBtn.onclick = () => openExclusionModal('excluded');
        }
    }

    /** Open a modal with retained or permanently excluded titles. */
    function openExclusionModal(type) {
        const retained = type === 'retained';
        const items = retained ? latestExclusions.retained : latestExclusions.excluded;
        modalTitle.textContent = retained ? 'Recent Cooldown Titles' : 'Feedback Exclusion Titles';
        setModalTabVisibility(false);
        setModalWide(true);

        modalMeta.innerHTML = retained
            ? `
                <div class="meta-item"><strong>Rule:</strong> recent recommendation cooldown</div>
                <div class="meta-item"><strong>TTL:</strong> ${latestExclusions.ttl_hours || '—'}h</div>
                <div class="meta-item"><strong>Items:</strong> ${items.length}</div>
            `
            : `
                <div class="meta-item"><strong>Rule:</strong> user feedback exclusion</div>
                <div class="meta-item"><strong>Feedback:</strong> watched / disliked / ignored</div>
                <div class="meta-item"><strong>Items:</strong> ${items.length}</div>
            `;

        modalBody.innerHTML = '';
        const pane = document.createElement('div');
        pane.className = 'modal-pane active';

        if (items.length === 0) {
            pane.innerHTML = '<div class="empty-state"><div class="empty-state-inner"><span>No titles to show</span></div></div>';
        } else if (retained) {
            pane.innerHTML = `
                <table class="suggested-table">
                    <thead><tr><th>Title</th><th>Original Title</th><th>TMDB</th><th>Recommended</th><th>Cooldown</th></tr></thead>
                    <tbody>${items.map(item => `
                        <tr>
                            <td>${escapeHtml(item.title || item.original_title || '—')}</td>
                            <td>${escapeHtml(item.original_title || '—')}</td>
                            <td>${escapeHtml(item.tmdb_id || '—')}</td>
                            <td>${escapeHtml(fullDate(item.recommended_at) || '—')}</td>
                            <td>${escapeHtml(formatExpiry(item.expires_at) || '—')}</td>
                        </tr>
                    `).join('')}</tbody>
                </table>`;
        } else {
            pane.innerHTML = `
                <table class="suggested-table">
                    <thead><tr><th>Title</th><th>Type</th><th>Feedback</th><th>TMDB / TVDB</th><th>Added</th></tr></thead>
                    <tbody>${items.map(item => `
                        <tr>
                            <td>${escapeHtml(item.title || '—')}</td>
                            <td>${escapeHtml(item.content_type || '—')}</td>
                            <td><span class="pill pill-sm ${feedbackPillClass(item.feedback_type)}">${escapeHtml(item.feedback_type || 'excluded')}</span></td>
                            <td>${escapeHtml([item.tmdb_id, item.tvdb_id].filter(Boolean).join(' / ') || '—')}</td>
                            <td>${escapeHtml(fullDate(item.created_at) || '—')}</td>
                        </tr>
                    `).join('')}</tbody>
                </table>`;
        }

        modalBody.appendChild(pane);
        modal.classList.add('open');
    }

    /** Pick a pill color class for permanent feedback exclusions. */
    function feedbackPillClass(feedbackType) {
        const fb = (feedbackType || '').toLowerCase();
        if (fb === 'watched') return 'feedback-watched';
        if (fb === 'disliked' || fb === 'dislike') return 'feedback-disliked';
        return 'feedback-ignored';
    }

    /** Format a future expiry timestamp as a short "in Xh/Xd" string. */
    function formatExpiry(dateString) {
        if (!dateString) return '';
        const date = new Date(dateString);
        if (isNaN(date)) return '';
        const seconds = Math.floor((date.getTime() - Date.now()) / 1000);
        if (seconds <= 0) return 'expiring';
        if (seconds < 3600) return `${Math.max(1, Math.floor(seconds / 60))}m left`;
        if (seconds < 86400) return `${Math.floor(seconds / 3600)}h left`;
        return `${Math.floor(seconds / 86400)}d left`;
    }

    /** Open the shared modal showing the titles from a stored carousel. */
    function openCarouselModal(carousel) {
        const items = Array.isArray(carousel.items) ? carousel.items : [];
        const isSeries = carousel.media_type === 'series';
        modalTitle.textContent = isSeries ? 'Carousel — Shows' : 'Carousel — Movies';
        setModalTabVisibility(false);
        setModalWide(true);

        modalMeta.innerHTML = `
            <div class="meta-item"><strong>Type:</strong> ${isSeries ? 'Series' : 'Movie'}</div>
            <div class="meta-item"><strong>Items:</strong> ${items.length}</div>
        `;

        modalBody.innerHTML = '';
        const pane = document.createElement('div');
        pane.className = 'modal-pane active';

        if (items.length === 0) {
            pane.innerHTML = '<div class="empty-state"><div class="empty-state-inner"><span>No items stored for this carousel</span></div></div>';
        } else {
            const tableRows = items.map(media => {
                const title = media._display_title || media.title || '—';
                const orig = media.original_title || '';
                const year = media.year || '—';
                const overview = media._display_overview || media.overview || '';
                return `
                    <tr>
                        <td>${escapeHtml(title)}</td>
                        <td>${escapeHtml(orig || '—')}</td>
                        <td>${year}</td>
                        <td class="overview-cell" title="${escapeHtml(overview)}">${escapeHtml(overview || '—')}</td>
                    </tr>`;
            }).join('');
            pane.innerHTML = `
                <table class="suggested-table">
                    <thead><tr><th>Title</th><th>Original Title</th><th>Year</th><th>Overview</th></tr></thead>
                    <tbody>${tableRows}</tbody>
                </table>`;
        }

        modalBody.appendChild(pane);
        modal.classList.add('open');
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

    /** Plain monospace HTTP status (no pill/badge). */
    function formatHttpStatus(code) {
        if (code == null) return '<span class="http-status http-status-unknown">—</span>';
        const ok = code >= 200 && code < 300;
        const cls = ok ? 'http-status-ok' : 'http-status-error';
        return `<span class="http-status ${cls}">${code}</span>`;
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

    /** Human-friendly display label for a detected user intent. */
    function formatIntentLabel(intent) {
        const map = {
            'RECOMMEND': 'Recommend',
            'INQUIRY': 'Inquiry',
            'ADD_MEDIA': 'Add media'
        };
        const key = String(intent || '').toUpperCase();
        return map[key] || key.replace(/_/g, ' ').toLowerCase();
    }

    /** CSS accent class for the detected user intent. */
    function intentClass(intent) {
        const map = {
            'RECOMMEND': 'chat-intent-recommend',
            'INQUIRY': 'chat-intent-inquiry',
            'ADD_MEDIA': 'chat-intent-add-media'
        };
        return map[String(intent || '').toUpperCase()] || '';
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

    // ── Render: Sessions table ─────────────────────────────────────
    const SESSION_COLSPAN = 8;
    const chevronSvg = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>';

    function buildSessionTimelineElement(detail) {
        const wrapper = document.createElement('div');
        wrapper.className = 'session-timeline';

        const entries = [
            ...detail.llm_logs.map(log => ({ type: 'llm', created_at: log.created_at, data: log })),
            ...detail.tmdb_logs.map(log => ({ type: 'tmdb', created_at: log.created_at, data: log })),
            ...(detail.service_api_logs || []).map(log => ({
                type: log.service === 'jellyfin' ? 'jellyfin' : 'arr',
                created_at: log.created_at,
                data: log,
            })),
        ].sort((a, b) => new Date(a.created_at) - new Date(b.created_at));

        if (entries.length === 0) {
            wrapper.innerHTML = '<div class="empty-state"><div class="empty-state-inner"><span>No activity recorded for this session</span></div></div>';
            return wrapper;
        }

        entries.forEach(entry => {
            const row = document.createElement('div');
            row.className = `timeline-entry timeline-${entry.type}`;

            const sep = '<span class="timeline-sep">·</span>';

            if (entry.type === 'llm') {
                const log = entry.data;
                const promptName = logPromptName(log);
                const meta = [
                    escapeHtml(log.model || '—'),
                    formatHttpStatus(log.status_code),
                    formatTokenBreakdown(log),
                    formatCost(log.cost_usd),
                    formatDuration(log.duration_ms)
                ].join(sep);
                row.innerHTML = `
                    <div class="timeline-info">
                        <span class="pill ${promptPillClass(promptName)} timeline-pill">AI · ${escapeHtml(promptName)}</span>
                        <span class="timeline-meta">${meta}</span>
                    </div>
                    <button class="timeline-view-btn" type="button">View</button>
                `;
                row.querySelector('.timeline-view-btn').addEventListener('click', (e) => {
                    e.stopPropagation();
                    openLlmModal(log);
                });
            } else if (entry.type === 'tmdb') {
                const log = entry.data;
                const meta = [
                    escapeHtml(log.endpoint || '—'),
                    formatHttpStatus(log.status_code),
                    formatDuration(log.duration_ms)
                ].join(sep);
                row.innerHTML = `
                    <div class="timeline-info">
                        <span class="pill pill-blue timeline-pill">TMDB</span>
                        <span class="timeline-meta">${meta}</span>
                    </div>
                    <button class="timeline-view-btn" type="button">View</button>
                `;
                row.querySelector('.timeline-view-btn').addEventListener('click', (e) => {
                    e.stopPropagation();
                    openTmdbModal({ ...log, user_id: detail.session.user_id });
                });
            } else {
                const log = entry.data;
                const isJellyfin = entry.type === 'jellyfin';
                const serviceLabel = isJellyfin
                    ? 'Media Server · Jellyfin'
                    : `Media Mgmt · ${escapeHtml((log.service || 'arr').charAt(0).toUpperCase() + (log.service || 'arr').slice(1))}`;
                const pillClass = isJellyfin ? 'pill-violet' : 'pill-amber';
                const meta = [
                    escapeHtml(log.method || 'GET'),
                    escapeHtml(log.endpoint || '—'),
                    formatHttpStatus(log.status_code),
                    formatDuration(log.duration_ms)
                ].join(sep);
                row.innerHTML = `
                    <div class="timeline-info">
                        <span class="pill ${pillClass} timeline-pill">${serviceLabel}</span>
                        <span class="timeline-meta">${meta}</span>
                    </div>
                    <button class="timeline-view-btn" type="button">View</button>
                `;
                row.querySelector('.timeline-view-btn').addEventListener('click', (e) => {
                    e.stopPropagation();
                    openServiceApiModal({ ...log, user_id: detail.session.user_id });
                });
            }

            wrapper.appendChild(row);
        });

        return wrapper;
    }

    async function openSessionModal(sessionId) {
        modalTitle.textContent = `Session ${shortSessionId(sessionId)}`;
        setModalTabVisibility(false);
        setModalWide(true);
        modalMeta.innerHTML = `
            <div class="meta-item"><strong>Session:</strong> <code style="font-size:0.75rem">${escapeHtml(sessionId)}</code></div>
        `;
        modalBody.innerHTML = '<span class="session-loading">Loading calls…</span>';
        modal.classList.add('open');

        try {
            const res = await fetch(`/admin/api/sessions/${sessionId}`);
            if (!res.ok) throw new Error('Session not found');
            const detail = await res.json();
            const session = detail.session || {};
            const statusClass = sessionStatusPillClass(session.status);
            const promptCost = (detail.llm_logs || []).reduce((sum, log) => sum + (log.cost_usd || 0), 0);

            modalTitle.textContent = `Session ${shortSessionId(session.id || sessionId)}`;
            modalMeta.innerHTML = `
                <div class="meta-item"><strong>User:</strong> ${escapeHtml(userDisplayName(session.user_id))}</div>
                <div class="meta-item"><strong>Status:</strong> <span class="pill ${statusClass}" style="font-size:0.625rem">${escapeHtml(session.status || '—')}</span></div>
                <div class="meta-item"><strong>Intent:</strong> ${escapeHtml(formatIntentLabel(session.detected_intent) || '—')}</div>
                <div class="meta-item"><strong>Started:</strong> ${escapeHtml(fullDate(session.created_at) || '—')}</div>
                <div class="meta-item"><strong>Duration:</strong> ${formatDuration(session.duration_ms)}</div>
                <div class="meta-item"><strong>AI Cost:</strong> ${formatCost(promptCost)}</div>
            `;

            const pane = document.createElement('div');
            pane.className = 'modal-pane active';
            if (session.user_message) {
                const message = document.createElement('div');
                message.className = 'session-message';
                message.textContent = session.user_message;
                pane.appendChild(message);
            }
            pane.appendChild(buildSessionTimelineElement(detail));
            modalBody.innerHTML = '';
            modalBody.appendChild(pane);
        } catch (error) {
            console.error('Error loading session modal:', error);
            modalBody.innerHTML = '<div class="empty-state"><div class="empty-state-inner"><span>Failed to load session calls</span></div></div>';
        }
    }

    async function loadSessionExpandContent(sessionId, container) {
        container.innerHTML = '<div class="expanded-inner"><span class="session-loading">Loading calls…</span></div>';
        try {
            const res = await fetch(`/admin/api/sessions/${sessionId}`);
            if (!res.ok) throw new Error('Session not found');
            const detail = await res.json();
            const inner = document.createElement('div');
            inner.className = 'expanded-inner';
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
            tbody.innerHTML = emptyRow(10, 'No AI activity yet');
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
                <td>${formatHttpStatus(item.status_code)}</td>
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

            tr.innerHTML = `
                <td title="${escapeHtml(fullDate(item.created_at))}">${timeAgo(item.created_at)}</td>
                <td style="color:var(--text-primary);font-weight:500">${escapeHtml(userDisplayName(item.user_id))}</td>
                <td style="color:var(--text-primary);font-weight:500;max-width:250px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="${escapeHtml(item.endpoint)}">${escapeHtml(item.endpoint || '—')}</td>
                <td style="font-size:0.7rem;font-family:monospace;color:var(--text-muted)" title="${escapeHtml(item.session_id || '')}">${escapeHtml(shortSessionId(item.session_id))}</td>
                <td>${formatHttpStatus(item.status_code)}</td>
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

    function renderServiceLogsTable(data, countId, tbodyId, emptyMessage, modalTitle) {
        document.getElementById(countId).textContent = data.length || 0;
        const tbody = document.getElementById(tbodyId);

        if (!data || data.length === 0) {
            tbody.innerHTML = emptyRow(8, emptyMessage);
            return;
        }

        tbody.innerHTML = '';
        data.forEach(item => {
            const tr = document.createElement('tr');
            const serviceName = item.service
                ? item.service.charAt(0).toUpperCase() + item.service.slice(1)
                : '—';

            tr.innerHTML = `
                <td title="${escapeHtml(fullDate(item.created_at))}">${timeAgo(item.created_at)}</td>
                <td style="color:var(--text-primary);font-weight:500">${escapeHtml(userDisplayName(item.user_id))}</td>
                <td style="color:var(--text-primary);font-weight:500">${escapeHtml(serviceName)}</td>
                <td style="color:var(--text-primary);font-weight:500;max-width:220px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;" title="${escapeHtml(item.endpoint)}">${escapeHtml(item.endpoint || '—')}</td>
                <td style="font-size:0.7rem;font-family:monospace;color:var(--text-muted)" title="${escapeHtml(item.session_id || '')}">${escapeHtml(shortSessionId(item.session_id))}</td>
                <td>${formatHttpStatus(item.status_code)}</td>
                <td style="font-size:0.75rem">${formatDuration(item.duration_ms)}</td>
                <td>
                    <button class="btn-view" title="View details">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                    </button>
                </td>
            `;
            tr.addEventListener('click', () => openServiceApiModal(item, modalTitle));
            const sessionCell = tr.children[4];
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

    function renderMediaMgmtLogs(data) {
        renderServiceLogsTable(
            data,
            'media-mgmt-count',
            'media-mgmt-tbody',
            'No media management activity yet',
            'Media Management Request'
        );
    }

    function renderMediaServerLogs(data) {
        renderServiceLogsTable(
            data,
            'media-server-count',
            'media-server-tbody',
            'No media server activity yet',
            'Media Server Request'
        );
    }

    // ── Modal Logic ─────────────────────────────────────────────────
    function closeModal() {
        modal.classList.remove('open');
        setTimeout(() => modalContentEl.classList.remove('modal-wide'), 300);
    }

    function setModalWide(wide) {
        modalContentEl.classList.toggle('modal-wide', wide);
    }

    modalCloseBtn.addEventListener('click', closeModal);
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.classList.contains('open')) {
            closeModal();
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
        setModalWide(true);

        modalMeta.innerHTML = `
            <div class="meta-item"><strong>Prompt:</strong> <span class="pill ${promptPillClass(promptName)}" style="font-size:0.625rem">${escapeHtml(promptName)}</span></div>
            <div class="meta-item"><strong>Model:</strong> ${escapeHtml(logItem.model || '—')}</div>
            <div class="meta-item"><strong>Tokens:</strong> ${formatTokenBreakdown(logItem)}</div>
            <div class="meta-item"><strong>Cost:</strong> ${formatCost(logItem.cost_usd)}</div>
            <div class="meta-item"><strong>Status:</strong> ${formatHttpStatus(logItem.status_code)}</div>
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
            const rawCols = document.createElement('div');
            rawCols.className = 'modal-raw-columns';
            if (logItem.raw_request) {
                rawCols.appendChild(createChatBubble('request', formatJsonBlock(logItem.raw_request)));
            }
            if (logItem.raw_response) {
                rawCols.appendChild(createChatBubble('response', formatJsonBlock(logItem.raw_response)));
            }
            rawPane.appendChild(rawCols);
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
        setModalWide(true);
        modalMeta.innerHTML = `
            <div class="meta-item"><strong>User:</strong> ${escapeHtml(userDisplayName(item.user_id))}</div>
            <div class="meta-item"><strong>Endpoint:</strong> <code style="font-size:0.75rem">${escapeHtml(item.endpoint || '—')}</code></div>
            <div class="meta-item"><strong>Status:</strong> ${formatHttpStatus(item.status_code)}</div>
            <div class="meta-item"><strong>Duration:</strong> ${formatDuration(item.duration_ms)}</div>
        `;

        modalBody.innerHTML = '';

        const paramsText = item.params ? formatJsonBlock(item.params) : 'None';
        const rawCols = document.createElement('div');
        rawCols.className = 'modal-raw-columns';
        rawCols.appendChild(createChatBubble('request', `GET ${item.endpoint || ''}\n\nParams:\n${paramsText}`));

        if (item.error) {
            rawCols.appendChild(createChatBubble('error', item.error));
        } else if (item.response_body) {
            rawCols.appendChild(createChatBubble('response', formatJsonBlock(item.response_body)));
        } else {
            rawCols.appendChild(createChatBubble('response', '(empty response)'));
        }
        modalBody.appendChild(rawCols);

        modal.classList.add('open');
    }

    function openServiceApiModal(item, title = 'Service API Request') {
        const serviceName = item.service
            ? item.service.charAt(0).toUpperCase() + item.service.slice(1)
            : '—';
        modalTitle.textContent = title;
        setModalTabVisibility(false);
        setModalWide(true);
        modalMeta.innerHTML = `
            <div class="meta-item"><strong>User:</strong> ${escapeHtml(userDisplayName(item.user_id))}</div>
            <div class="meta-item"><strong>Service:</strong> ${escapeHtml(serviceName)}</div>
            <div class="meta-item"><strong>Method:</strong> ${escapeHtml(item.method || 'GET')}</div>
            <div class="meta-item"><strong>Endpoint:</strong> <code style="font-size:0.75rem">${escapeHtml(item.endpoint || '—')}</code></div>
            <div class="meta-item"><strong>Status:</strong> ${formatHttpStatus(item.status_code)}</div>
            <div class="meta-item"><strong>Duration:</strong> ${formatDuration(item.duration_ms)}</div>
        `;

        modalBody.innerHTML = '';

        const paramsText = item.params ? formatJsonBlock(item.params) : 'None';
        const bodyText = item.request_body ? formatJsonBlock(item.request_body) : null;
        let requestContent = `${item.method || 'GET'} ${item.endpoint || ''}\n\nParams:\n${paramsText}`;
        if (bodyText) {
            requestContent += `\n\nBody:\n${bodyText}`;
        }

        const rawCols = document.createElement('div');
        rawCols.className = 'modal-raw-columns';
        rawCols.appendChild(createChatBubble('request', requestContent));

        if (item.error) {
            rawCols.appendChild(createChatBubble('error', item.error));
        } else if (item.response_body) {
            rawCols.appendChild(createChatBubble('response', formatJsonBlock(item.response_body)));
        } else {
            rawCols.appendChild(createChatBubble('response', '(empty response)'));
        }
        modalBody.appendChild(rawCols);

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
