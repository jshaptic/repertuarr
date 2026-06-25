# Continuity Ledger

## Snapshot
**Date:** 2026-06-25
**Goal:** Refactor admin Logs to group activity by bot sessions with raw LLM API payloads.
**Now:** Sessions refactor complete — DB schema, bot instrumentation, admin API + UI.
**Next:** Manual verification with live bot traffic.
**Open Questions:** None.

## Done (recent)
- `[CODE]` 2026-06-25 Admin Logs sessions refactor: `sessions` table, session_id on llm/tmdb logs, prompt_name + raw_request/raw_response on LLM logs, Sessions tab in admin UI, Processed/Raw modal tabs.
- `[CODE]` 2026-06-25 Added `tmdb_id` to `RecommendationItem` in `models.py` and to the `recommendation.mustache` prompt template.
- `[CODE]` 2026-06-24 Renamed "AI Activity" to "Logs" in Admin UI and added a new sub-section to view TMDB requests/responses. Logs are now saved to `tmdb_logs` in `bot/database.py`.
- `[CODE]` 2026-06-24 Enforced strict LLM recommendation pool and modified TMDB fetching to retrieve exactly 15 popular, 15 top ranked, and 70 discovery candidates excluding ignored/watched items (`bot/tmdb.py`, `bot/telegram_bot.py`, `recommendation.mustache`).
- `[CODE]` 2026-06-24 Added TMDB integration: `bot/tmdb.py` client, `discovery_filter` in `config.yaml`, updated `recommendation.mustache` and `telegram_bot.py`.
- `[CODE]` 2026-06-24 Reworked User Details page — replaced 3 stacked tables with tabbed sub-navigation (Conversations/Requests/Feedback) in `index.html`, `app.js`, `styles.css`.
- `[CODE]` 2026-06-24 Added expandable conversation rows with nested suggested media sub-table (Title, Original Title, Type, Year).
- `[CODE]` 2026-06-24 Fixed "Bot Iteraction" typo → renamed to "Conversations".
- `[CODE]` 2026-06-24 Fixed `Button_data_invalid` by safely truncating callback data titles in `telegram_bot.py`.
- `[CODE]` 2026-06-24 Added `original_title` field to `RecommendationItem` in `models.py`.
- `[CODE]` 2026-06-24 Rewrote admin UI files (HTML, CSS, JS) — branding, modal, responsive.
- `[CODE]` 2026-06-23 Implemented `get_users_summary` in `bot/database.py`.

## Working Set
- `bot/database/logs.py`
- `bot/session_context.py`
- `bot/llm_logging.py`
- `bot/web/index.html`
- `bot/web/app.js`
- `bot/web/styles.css`

## Decisions
- `D001 ACTIVE:` Use `INQUIRY` as the intent identifier.
- `D003 ACTIVE:` INQUIRY responses are parsed as structured `InquiryResponse`, returning a `reply_text` and an optional `items` list.
- `D004 ACTIVE:` Use `client.responses.parse()` API with `web_search_preview` tool for INQUIRY and RECOMMEND intents.
- `D005 ACTIVE:` Admin UI is served on the same `aiohttp` server as the webhook, unauthenticated by default.
- `D006 ACTIVE:` Admin UI branding renamed to "Repertuarr".
- `D007 ACTIVE:` LLM returns `original_title` alongside localized `title`; Radarr/Sonarr lookups use `original_title`, Telegram display uses localized `title`/`overview`.
- `D008 ACTIVE:` User Details page uses tabbed sub-navigation instead of stacked tables; Conversations tab has expandable rows with nested suggested media sub-tables.
- `D009 ACTIVE:` Integrate TMDB Discover APIs to fetch pre-filtered candidate pool of media based on user's `discovery_filter`, then pass to LLM as candidates.
- `D010 ACTIVE:` Bot interaction sessions (UUID per user message) group LLM + TMDB logs; prompt_name uses agent config keys (`intent`, `inquiry`, `recommend`); raw API payloads stored alongside processed logs.
