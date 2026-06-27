# Continuity Ledger

## Snapshot
**Date:** 2026-06-28
**Goal:** DB-backed chat history + message-linked carousels; remove pickle persistence.
**Now:** Chat transcript + carousel state persisted in SQLite (`bot/database/chat.py`); pickle removed; per-card carousel navigation; admin user page has compact Chat tab; edit sync via `edited_message` + `/clear` command.
**Next:** Verify live with Telegram traffic (edits, old-card navigation, /clear).
**Open Questions:** None.

## Done (recent)
- `[CODE]` 2026-06-28 DB-backed chat + linked carousels: new `bot/database/chat.py` (`ChatMixin`, tables `chat_messages` + `carousel_state`); `add_to_history`/history reads now hit DB; carousels keyed by Telegram `message_id` (any past card stays scrollable); removed `PicklePersistence` from `main.py`; `edited_message` handler + `/clear` command; admin `GET /admin/api/chat` + Chat sub-tab on user page (`app.js?v=23`, `styles.css?v=15`).
- `[CODE]` 2026-06-28 Chat tab assistant turns show LLM cost + "View titles" button: `carousel_state.session_id` column links carousel to its session; `get_session_costs` (logs.py) + `get_carousels_by_sessions` (chat.py); `api_chat` attaches `cost_usd`/`carousel` to the last assistant message per session; frontend price chip + modal media table; cache `app.js?v=25`, `styles.css?v=17`.
- `[CODE]` 2026-06-28 Admin Chat tab compact layout: transcript-specific classes avoid collision with modal `.chat-user` styles; tighter bubbles/meta; cache bumped to `app.js?v=24`, `styles.css?v=16`.
- `[CODE]` 2026-06-27 TMDB-native discover filters: pass-through query params in `bot/tmdb.py`; removed genre/keyword name resolution and `discovery_filter` migration; config uses TMDB IDs/syntax; tests in `tests/test_tmdb_discover.py`.
- `[CODE]` 2026-06-26 Raw view: request/response side-by-side (`.modal-raw-columns` grid) for AI Raw tab and TMDB modal; modal widens to 1100px via `.modal-wide`; `styles.css?v=13`, `app.js?v=21`.
- `[CODE]` 2026-06-26 Sessions expand redesign: compact timeline cards with colored left accent border (removed dot markers); `styles.css?v=11`, `app.js?v=18`.
- `[CODE]` 2026-06-26 Sessions table: user display names; session ID + status on row (removed from expand meta).
- `[CODE]` 2026-06-25 TMDB logs: user column via session join; modal shows HTTP request/response blocks instead of chat-style user/assistant bubbles.
- `[CODE]` 2026-06-25 AI Activity table: user display names instead of IDs; prompts shown as plain text (no color pills).
- `[CODE]` 2026-06-25 LLM cost tracking: `bot/llm_pricing.py`, pricing in `llms[].pricing`, token breakdown + `cost_usd` on `llm_logs`, cost in Logs (Sessions/AI Activity/modal) and Users aggregate.
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
- `bot/telegram_bot.py`
- `bot/database/chat.py`
- `bot/database/__init__.py`
- `bot/admin_ui.py`
- `bot/web/index.html`
- `bot/web/app.js`
- `bot/web/styles.css`
- `main.py`

## Decisions
- `D001 ACTIVE:` Use `INQUIRY` as the intent identifier.
- `D003 ACTIVE:` INQUIRY responses are parsed as structured `InquiryResponse`, returning a `reply_text` and an optional `items` list.
- `D004 ACTIVE:` Use `client.responses.parse()` API with `web_search_preview` tool for INQUIRY and RECOMMEND intents.
- `D005 ACTIVE:` Admin UI is served on the same `aiohttp` server as the webhook, unauthenticated by default.
- `D006 ACTIVE:` Admin UI branding renamed to "Repertuarr".
- `D007 ACTIVE:` LLM returns `original_title` alongside localized `title`; Radarr/Sonarr lookups use `original_title`, Telegram display uses localized `title`/`overview`.
- `D008 ACTIVE:` User Details page uses tabbed sub-navigation instead of stacked tables; Conversations tab has expandable rows with nested suggested media sub-tables.
- `D009 ACTIVE:` Per-user `recommendation_sources` array; discover `filter` uses TMDB API param names/syntax (`.gte`/`.lte`, comma=AND, pipe=OR); genre/keyword IDs required in config.
- `D010 ACTIVE:` Bot interaction sessions (UUID per user message) group LLM + TMDB logs; prompt_name uses agent config keys (`intent`, `inquiry`, `recommend`); raw API payloads stored alongside processed logs.
- `D011 ACTIVE:` Per-LLM `pricing` in config (`input_per_million`, `output_per_million`, `cached_input_per_million` USD); cost computed at log time; missing pricing logs request with `cost_usd` NULL (UI shows em dash).
- `D012 ACTIVE:` No PTB persistence; chat transcript (`chat_messages`) and carousel state (`carousel_state`) live in SQLite. Transcript = user msgs + bot text answers (transient "thinking"/status not stored). Carousel state keyed by `(chat_id, message_id)` so every card is independently navigable. Edits synced via `edited_message` (no LLM re-run); `/clear` wipes a user's chat + carousels. Telegram delivers no delete/clear events to normal bots, so those are out of scope.
