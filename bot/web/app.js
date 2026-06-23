document.addEventListener('DOMContentLoaded', () => {
    // --- Tab Navigation Logic ---
    const navItems = document.querySelectorAll('.nav-item');
    const tabPanes = document.querySelectorAll('.tab-pane');
    const currentTabTitle = document.getElementById('current-tab-title');

    // Elements for User Details
    const backToUsersBtn = document.getElementById('back-to-users');
    const userDetailsPane = document.getElementById('user-details');

    function switchTab(targetId, title) {
        navItems.forEach(nav => nav.classList.remove('active'));
        tabPanes.forEach(pane => pane.classList.remove('active'));

        const matchingNav = Array.from(navItems).find(nav => nav.getAttribute('data-target') === targetId);
        if (matchingNav) matchingNav.classList.add('active');

        document.getElementById(targetId).classList.add('active');
        if (title) currentTabTitle.textContent = title;
    }

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const targetId = item.getAttribute('data-target');
            switchTab(targetId, item.textContent.trim());
        });
    });

    backToUsersBtn.addEventListener('click', () => {
        switchTab('users', 'Users');
    });

    // --- Data Fetching Logic ---
    const refreshBtn = document.getElementById('refresh-btn');
    const refreshIcon = refreshBtn.querySelector('svg');

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
            const [usersRes, llmRes] = await Promise.all([
                fetch('/admin/api/users'),
                fetch('/admin/api/llm-logs')
            ]);

            const users = await usersRes.json();
            const llmLogs = await llmRes.json();

            renderUsers(users);
            renderGlobalLlmLogs(llmLogs);

            // Update Overview Stats
            document.getElementById('stat-users').textContent = users.length || 0;
            const totalReq = users.reduce((sum, u) => sum + (u.requests_count || 0), 0);
            const totalFb = users.reduce((sum, u) => sum + (u.feedback_count || 0), 0);
            document.getElementById('stat-requests').textContent = totalReq;
            document.getElementById('stat-feedback').textContent = totalFb;
            document.getElementById('stat-llm').textContent = llmLogs.length || 0;

        } catch (error) {
            console.error('Error fetching data:', error);
        }
    }

    async function showUserDetails(userId, userName) {
        switchTab('user-details', `User Details: ${userName}`);
        document.getElementById('detail-user-id').textContent = `User: ${userName}`;

        try {
            const [reqRes, fbRes, llmRes] = await Promise.all([
                fetch(`/admin/api/requests?user_id=${userId}`),
                fetch(`/admin/api/feedback?user_id=${userId}`),
                fetch(`/admin/api/llm-logs?user_id=${userId}`)
            ]);

            renderUserRequests(await reqRes.json());
            renderUserFeedback(await fbRes.json());
            renderUserLlmLogs(await llmRes.json());
        } catch (error) {
            console.error('Error fetching user details:', error);
        }
    }

    function formatDate(dateString) {
        if (!dateString) return 'N/A';
        const parsed = new Date(dateString);
        return isNaN(parsed) ? dateString : parsed.toLocaleString(undefined, {
            month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit'
        });
    }

    function renderUsers(data) {
        document.getElementById('users-count').textContent = data.length || 0;
        const tbody = document.getElementById('users-tbody');
        if (!data || data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="loading-state">No users found</td></tr>';
            return;
        }

        tbody.innerHTML = '';
        data.forEach(item => {
            const tr = document.createElement('tr');

            const radarrTooltip = `Radarr: ${item.radarr_name}\nProfile: ${item.radarr_profile}`;
            const sonarrTooltip = `Sonarr: ${item.sonarr_name}\nProfile: ${item.sonarr_profile}`;

            const servicesHtml = `
                <div style="display: flex; gap: 12px; align-items: center;">
                    <img src="https://cdn.jsdelivr.net/gh/selfhst/icons/svg/radarr-light-hybrid.svg" alt="Radarr" title="${escapeHtml(radarrTooltip)}" width="20" height="20">
                    <img src="https://cdn.jsdelivr.net/gh/homarr-labs/dashboard-icons/svg/sonarr.svg" alt="Sonarr" title="${escapeHtml(sonarrTooltip)}" width="20" height="20">
                </div>
            `;

            tr.innerHTML = `
                <td style="font-weight: 500; color: var(--primary-color)">${escapeHtml(item.name)}</td>
                <td>${servicesHtml}</td>
                <td>${item.requests_count || 0}</td>
                <td>${item.feedback_count || 0}</td>
                <td>${item.llm_count || 0}</td>
                <td style="color: var(--text-secondary)">${formatDate(item.last_active)}</td>
            `;
            tr.addEventListener('click', () => showUserDetails(item.user_id, item.name));
            tbody.appendChild(tr);
        });
    }

    function renderUserRequests(data) {
        document.getElementById('user-requests-count').textContent = data.length || 0;
        const tbody = document.getElementById('user-requests-tbody');
        if (!data || data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="loading-state">No requests</td></tr>';
            return;
        }
        tbody.innerHTML = data.map(item => `
            <tr>
                <td>${formatDate(item.created_at)}</td>
                <td style="font-weight: 500">${escapeHtml(item.title)}</td>
                <td class="type-label">${escapeHtml(item.media_type || 'N/A')}</td>
                <td><span class="status-label status-${(item.status || 'pending').toLowerCase()}">${escapeHtml(item.status || 'pending')}</span></td>
            </tr>
        `).join('');
    }

    function renderUserFeedback(data) {
        document.getElementById('user-feedback-count').textContent = data.length || 0;
        const tbody = document.getElementById('user-feedback-tbody');
        if (!data || data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="loading-state">No feedback</td></tr>';
            return;
        }
        tbody.innerHTML = data.map(item => `
            <tr>
                <td>${formatDate(item.created_at)}</td>
                <td style="font-weight: 500">${escapeHtml(item.title || 'N/A')}</td>
                <td class="type-label">${escapeHtml(item.content_type || 'N/A')}</td>
                <td><span class="status-label feedback-${(item.feedback_type || '').toLowerCase()}">${escapeHtml(item.feedback_type || 'N/A')}</span></td>
            </tr>
        `).join('');
    }

    function renderUserLlmLogs(data) {
        const filteredData = data.filter(item => item.intent !== 'CLASSIFY_INTENT');
        document.getElementById('user-llm-count').textContent = filteredData.length || 0;
        const tbody = document.getElementById('user-llm-tbody');
        if (!filteredData || filteredData.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="loading-state">No LLM interactions</td></tr>';
            return;
        }
        tbody.innerHTML = filteredData.map(item => {
            let suggestionsHtml = '<span style="color: var(--text-secondary)">None</span>';
            if (item.llm_response) {
                try {
                    const parsed = JSON.parse(item.llm_response);
                    if (parsed && Array.isArray(parsed.items) && parsed.items.length > 0) {
                        const badges = parsed.items.map(media => {
                            const title = media.title || 'Unknown';
                            return `<span class="suggestion-badge" title="${escapeHtml(title)}">${escapeHtml(title)}</span>`;
                        }).join('');
                        suggestionsHtml = `<div class="suggestions-container">${badges}</div>`;
                    }
                } catch (e) { }
            }
            return `
            <tr>
                <td>${formatDate(item.created_at)}</td>
                <td style="max-width: 250px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${escapeHtml(item.user_message)}">${escapeHtml(item.user_message || '-')}</td>
                <td>${suggestionsHtml}</td>
                <td><span class="status-label status-notified">${escapeHtml(item.intent || 'N/A')}</span></td>
            </tr>
            `;
        }).join('');
    }

    function renderGlobalLlmLogs(data) {
        document.getElementById('llm-count').textContent = data.length || 0;
        const tbody = document.getElementById('llm-tbody');
        if (!data || data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="loading-state">No LLM interactions found</td></tr>';
            return;
        }

        tbody.innerHTML = '';
        data.forEach(item => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${formatDate(item.created_at)}</td>
                <td style="color: var(--text-secondary)">${item.user_id || 'N/A'}</td>
                <td style="color: var(--text-secondary); font-size: 0.75rem;">
                    <div>${escapeHtml(item.model || 'N/A')}</div>
                    <div><strong>${item.tokens || 0}</strong> tkns</div>
                </td>
                <td>${item.duration_ms ? item.duration_ms + 'ms' : '-'}</td>
                <td><button class="btn primary" style="padding: 0.25rem 0.75rem; font-size: 0.75rem;">View Messages</button></td>
            `;
            tr.addEventListener('click', () => openLlmModal(item));
            tbody.appendChild(tr);
        });
    }

    // --- Modal Logic ---
    const modal = document.getElementById('llm-modal');
    const modalCloseBtn = document.getElementById('modal-close');
    const modalBody = document.getElementById('modal-body');

    modalCloseBtn.addEventListener('click', () => modal.classList.remove('open'));
    modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.classList.remove('open');
    });

    function openLlmModal(logItem) {
        modalBody.innerHTML = '';
        let messages = [];

        if (logItem.llm_request) {
            try {
                // LLM requests are usually JSON arrays of messages
                const parsed = JSON.parse(logItem.llm_request);
                if (Array.isArray(parsed)) {
                    messages = parsed;
                } else {
                    messages = [{ role: 'user', content: logItem.llm_request }]; // String prompt
                }
            } catch (e) {
                messages = [{ role: 'user', content: logItem.llm_request }];
            }
        }

        if (messages.length === 0) {
            modalBody.innerHTML = '<div class="loading-state">No messages logged</div>';
        } else {
            messages.forEach(msg => {
                const div = document.createElement('div');
                const role = msg.role || 'unknown';
                div.className = `chat-message chat-${role}`;

                const roleLabel = document.createElement('div');
                roleLabel.className = 'chat-role';
                roleLabel.textContent = role;

                const content = document.createElement('div');
                content.textContent = msg.content || '';

                div.appendChild(roleLabel);
                div.appendChild(content);
                modalBody.appendChild(div);
            });
        }

        modal.classList.add('open');
    }

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
