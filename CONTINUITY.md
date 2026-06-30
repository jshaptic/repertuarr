# Continuity Ledger

## Snapshot
**Date:** 2026-06-30
**Goal:** `[USER]` 2026-06-29 Send separate request lifecycle messages for title requests/webhooks instead of changing the carousel button after Add.
**Now:** `[CODE]` 2026-06-30 Merged `play_button` into `download_ready`; carousel reuses link label via `get_jellyfin_play_label()`.
**Next:** `[USER]` Restart the bot to load notification copy changes.
**Open Questions:** None.

## Done (recent)
- `[CODE]` 2026-06-30 Fixed RECOMMEND error `'RecommendationItem' object has no attribute 'get'`: `record_recent_recommendations` uses type-safe field access; carousel id extraction handles Pydantic `tmdb_id`; test for mixed None TMDB IDs.
- `[CODE]` 2026-06-30 Fixed `request_queued` Telegram timeouts: Arr add moved to `asyncio.to_thread`, lifecycle sends retry transient Telegram errors, `queued_notified_at` tracks delivery, Grab/monitor backfill missed queued messages, ApplicationBuilder timeouts raised to 30s. `poetry run pytest` passed 77 tests with existing sqlite datetime warnings.
- `[CODE]` 2026-06-29 Request status messages: added `request_queued` and `download_started` phrases (en/ru); Add success sends a normal queued chat message instead of editing the inline button; Radarr/Sonarr Grab webhook and monitor queue detection send download-started before marking grabbed; lifecycle/phrase tests updated; `poetry run pytest` passed 72 tests with existing sqlite datetime warnings.
- `[CODE]` 2026-06-29 Download failure detection: `media_requests` now stores Arr service/instance/id/download lifecycle fields; Add flow records created Arr IDs and recovers when Arr creates an item but the POST times out; webhooks acknowledge `MovieAdded`/`SeriesAdd`, mark `Grab`, and notify/mark `ManualInteractionRequired`; `download_monitor.py` polls active requests for no acceptable candidates and blocked queues; English/Russian failure phrases added; `tests/test_download_failure_detection.py`; `pyproject.toml` sets pytest `pythonpath`; `poetry run pytest` passed 70 tests with existing sqlite datetime warnings.
- `[CODE]` 2026-06-29 User-detail chat restyle: removed visible chat panel header in `index.html`; `styles.css` gives `.chat-workspace` a real grid gap, removes chat divider borders, softens `.chat-panel`, adjusts transcript height, and keeps responsive layout borderless. `ReadLints` found no issues in edited files.
- `[CODE]` 2026-06-29 Admin user page refactor/polish: removed Media Library sub-tab + sub-tab bar; left sidebar now rectangular clickable aggregate tiles with larger label/help text (Recently shown, Requested, Watched [all watched, overlaps], Liked, Disliked, Not interested); top-bar breadcrumbs (`Users / current user`) hidden outside user detail; chat panel widened by 100px with header/title; `api_exclusions` returns `retained/requested/watched/liked/disliked/not_interested`; dropped `/admin/api/media-library` route; `.user-stat*` CSS avoids dashboard `.stat-card` clash. 66 tests pass.
- `[CODE]` 2026-06-29 TMDB pre-filter: `recommendation_pool` excludes by TMDB ID + title (feedback + recent cooldown), backfills per source via pagination (max 20 pages); post-LLM filter removed from `telegram_bot.py`; tests in `test_recommendation_pool.py`.
- `[CODE]` 2026-06-29 Phrase system: `bot/phrases/` with 5 styles, ≥3 variants, full `thinking` × 30 langs; `recommend_button` translated; persistent ReplyKeyboard on text replies; recommend-button tap short-circuits to RECOMMEND; `tests/test_phrases.py` (10 tests).
- `[CODE]` 2026-06-29 Feedback refactor: normalized `user_content_feedback` schema (`watched`, `feedback`, `excluded`) with legacy migration; Telegram carousel row order ignore/watched/disliked/liked, add row, nav row; feedback toggles auto-advance; admin UI columns updated; `tests/test_feedback.py`.
- `[CODE]` 2026-06-29 `bot.recommendation_carousel_count`: limits LLM ask + carousel display + recent-recommendation cooldown; default 10 in `config.yaml`; test in `test_recommendation_prompt.py`.
- `[CODE]` 2026-06-29 Service API logging: `bot/service_request.py` wrapper; `bot/database/service_logs.py` (`ServiceLogMixin`, `service_api_logs`); wired in `jellyfin.py` + `telegram_bot.py`; `GET /admin/api/service-logs`; admin Logs tabs Media Management (Radarr/Sonarr) and Media Servers (Jellyfin); session timeline pills; tests in `tests/test_service_request.py`.
- `[CODE]` 2026-06-28..29 Recommendation prompt/cooldown milestone: source labels, prompt message split, recent recommendation exclusions, and related tests are in place.

## Working Set
- `bot/database/__init__.py`
- `bot/telegram_bot.py`
- `bot/webhook.py`
- `bot/webhook_events.py`
- `bot/download_monitor.py`
- `main.py`
- `bot/phrases/keys.py`
- `bot/phrases/data/en.yaml`
- `bot/phrases/data/ru.yaml`
- `tests/test_download_failure_detection.py`
- `tests/test_phrases.py`
- `pyproject.toml`

## Decisions
- `D001 ACTIVE:` Use `INQUIRY` as the intent identifier.
- `D017 ACTIVE:` `[CODE]` 2026-06-29 Download failure detection uses a hybrid Arr approach: lifecycle webhooks for `Grab`/`Download`/`ManualInteractionRequired`, plus a background Arr API monitor for the no-native-event case where automatic search yields no acceptable release candidate; qBittorrent is not required for the core feature.
- `D018 ACTIVE:` `[USER]` 2026-06-29 Successful Add keeps the carousel button/markup unchanged; request progress is communicated with separate Telegram messages (`request_queued`, `download_started`, then ready/failure/unavailable).
- `D016 ACTIVE:` `[CODE]` 2026-06-29 Recommendation exclusions apply at TMDB candidate pre-filter only (IDs + titles, per-source backfill); LLM output is shown as-is with no post-filter.
- `D015 ACTIVE:` `[CODE]` 2026-06-29 Feedback state is one row per normalized content key with `watched` boolean, nullable `feedback` (`like|dislike`), and `excluded` boolean; legacy `feedback_type` rows migrate on DB init.
- `D014 ACTIVE:` `[CODE]` 2026-06-29 Bot hardcoded copy lives in `bot/phrases/data/*.yaml`; `preferences.bot_style` selects tone (`default|casual|warm|witty|cinephile|sarcastic|wizarding`); `thinking` is style-specific; other keys use shared phrases with English fallback for non-en langs.
- `D013 ACTIVE:` `[CODE]` 2026-06-29 Recommendation source names are optional; prompt display uses configured `name` or generated labels like `Popular movies`/`Top rated TV shows`. RECOMMEND uses separate OpenAI input messages: system contains stable instructions plus user name/preferences/guidelines; user messages contain feedback history and current request/candidates.
