# Continuity Ledger

## Snapshot
**Date:** 2026-06-28
**Goal:** `[USER]` 2026-06-28 Recommendation Prompt Restructure.
**Now:** `[CODE]` 2026-06-29 RECOMMEND system message includes user name/preferences/guidelines; user messages are feedback history + current request/candidates; Lena discover sources have explicit names.
**Next:** `[TOOL]` 2026-06-28 Optional live Telegram RECOMMEND smoke test with real TMDB/OpenAI credentials.
**Open Questions:** None.

## Done (recent)
- `[CODE]` 2026-06-28 Recommendation prompt restructure: optional `recommendation_sources[].name` with generated fallback labels; grouped TMDB candidate fetch; new `bot/recommendation_prompt.py` builds system/profile/feedback/request OpenAI messages; `recommendation.mustache` renders source headers + TMDB overviews.
- `[CODE]` 2026-06-29 Recommendation prompt follow-up: moved user name/preferences/guidelines into the RECOMMEND system message and named Lena's discover sources in `config.yaml`.
- `[TOOL]` 2026-06-29 Full tests passed with `PYTHONPATH=. poetry run pytest` (43 passed, 3 sqlite datetime adapter deprecation warnings).
- `[TOOL]` 2026-06-28 Full tests passed with `PYTHONPATH=. poetry run pytest` (43 passed, 3 sqlite datetime adapter deprecation warnings). Plain focused `poetry run pytest ...` failed collection because `bot` was not on `PYTHONPATH`.
- `[CODE]` 2026-06-28 Chat workspace full-width + visual divider: removed max-width cap; gap:0; chat-state gets subtle bg/padding; chat-panel gets border-left rule; responsive gets border-top instead; cache `styles.css?v=25`.
- `[CODE]` 2026-06-28 Admin Chat layout tweak: Chat State moved to primary left column and transcript moved to narrower right column; timestamp restored inside bubble header; intent/price/actions remain under bubbles; cache `app.js?v=32`, `styles.css?v=24`.
- `[CODE]` 2026-06-28 Admin Chat refinements: narrowed chat workspace/stack; moved intent, price, timestamp, and carousel action under bubbles; carousel action now says "View N titles"; stronger intent-specific border + text colors; cache `app.js?v=31`, `styles.css?v=23`.
- `[CODE]` 2026-06-28 Admin Chat two-column UX: transcript left, recommendation context right; session cost moved from assistant row to user row in `/admin/api/chat`; intent no longer uses `Intent:` label/badge and instead appears as plain value with intent-specific user bubble border color; cache `app.js?v=30`, `styles.css?v=22`.
- `[CODE]` 2026-06-28 Admin Chat visual overhaul: bubble markup now has speaker/meta header; intent changed from colored badge to quiet `Intent: ...` metadata; Chat panel/exclusion strip flattened with fewer borders/shadows and cleaner spacing; cache `app.js?v=29`, `styles.css?v=21`.
- `[CODE]` 2026-06-28 Admin User Details Chat redesign: removed Conversations sub-tab and user-specific `/admin/api/llm-logs` fetch/render path; Chat is default; `/admin/api/chat` attaches session `detected_intent` to user rows via `get_session_intents`; user bubbles render intent chips; transcript spacing widened; cache `app.js?v=28`, `styles.css?v=20`.
- `[CODE]` 2026-06-28 Refined Chat tab exclusion block layout/labels: "Recent cooldown" and "Feedback exclusions" compact summary cards; counts + disabled/enabled "View titles" buttons; modal details tables for retained cooldown items and permanent feedback exclusions; cache `app.js?v=27`, `styles.css?v=19`.
- `[CODE]` 2026-06-28 Admin Chat tab exclusions block: shows "Temporarily retained" (recent_recommendations cooldown, with per-title expiry countdown) and "Permanently excluded" (watched/disliked/ignored feedback) titles. New `get_recent_recommendations(user_id, ttl_seconds)` (recommendations.py) + `GET /admin/api/exclusions` (admin_ui.py, ttl wired via `register_admin_routes(..., recommendation_exclude_ttl_hours)` from webhook.py); frontend `renderExclusions` + `.exclusions-*` styles; cache `app.js?v=26`, `styles.css?v=18`; tests added in test_recent_recommendations.py.
- `[CODE]` 2026-06-28 Recommendation cooldown: `bot/database/recommendations.py` (`RecentRecommendationsMixin`, table `recent_recommendations`); merge recent TMDB IDs/titles into RECOMMEND exclusions; record shown carousel items; `/clear` wipes cooldown; config `bot.recommendation_exclude_ttl_hours`; tests in `tests/test_recent_recommendations.py`.
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
- `bot/recommendation_pool.py`
- `bot/recommendation_prompt.py`
- `bot/tmdb.py`
- `bot/telegram_bot.py`
- `bot/prompts/recommendation.mustache`
- `tests/test_recommendation_pool.py`
- `tests/test_recommendation_prompt.py`

## Decisions
- `D001 ACTIVE:` Use `INQUIRY` as the intent identifier.
- `D003 ACTIVE:` INQUIRY responses are parsed as structured `InquiryResponse`, returning a `reply_text` and an optional `items` list.
- `D004 ACTIVE:` Use `client.responses.parse()` API with `web_search_preview` tool for INQUIRY and RECOMMEND intents.
- `D005 ACTIVE:` Admin UI is served on the same `aiohttp` server as the webhook, unauthenticated by default.
- `D006 ACTIVE:` Admin UI branding renamed to "Repertuarr".
- `D007 ACTIVE:` LLM returns `original_title` alongside localized `title`; Radarr/Sonarr lookups use `original_title`, Telegram display uses localized `title`/`overview`.
- `D008 ACTIVE:` User Details page uses tabbed sub-navigation with Chat and Media Library; Chat is the default pane and replaces the removed Conversations section.
- `D009 ACTIVE:` Per-user `recommendation_sources` array; discover `filter` uses TMDB API param names/syntax (`.gte`/`.lte`, comma=AND, pipe=OR); genre/keyword IDs required in config.
- `D010 ACTIVE:` Bot interaction sessions (UUID per user message) group LLM + TMDB logs; prompt_name uses agent config keys (`intent`, `inquiry`, `recommend`); raw API payloads stored alongside processed logs.
- `D011 ACTIVE:` Per-LLM `pricing` in config (`input_per_million`, `output_per_million`, `cached_input_per_million` USD); cost computed at log time; missing pricing logs request with `cost_usd` NULL (UI shows em dash).
- `D012 ACTIVE:` No PTB persistence; chat transcript (`chat_messages`) and carousel state (`carousel_state`) live in SQLite. Transcript = user msgs + bot text answers (transient "thinking"/status not stored). Carousel state keyed by `(chat_id, message_id)` so every card is independently navigable. Edits synced via `edited_message` (no LLM re-run); `/clear` wipes a user's chat + carousels. Telegram delivers no delete/clear events to normal bots, so those are out of scope.
- `D013 ACTIVE:` `[CODE]` 2026-06-29 Recommendation source names are optional; prompt display uses configured `name` or generated labels like `Popular movies`/`Top rated TV shows`. RECOMMEND uses separate OpenAI input messages: system contains stable instructions plus user name/preferences/guidelines; user messages contain feedback history and current request/candidates.
