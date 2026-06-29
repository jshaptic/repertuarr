# Continuity Ledger

## Snapshot
**Date:** 2026-06-29
**Goal:** `[USER]` 2026-06-29 Feedback refactor: watched boolean, like/dislike feedback, excluded boolean, toggleable carousel controls.
**Now:** `[CODE]` 2026-06-29 Feedback refactor implemented; full tests pass (`PYTHONPATH=. poetry run pytest`: 61 passed).
**Next:** `[USER]` Restart bot and verify live Telegram button layout/auto-advance behavior.
**Open Questions:** None.

## Done (recent)
- `[CODE]` 2026-06-29 Phrase system: `bot/phrases/` with 5 styles, ≥3 variants, full `thinking` × 30 langs; `recommend_button` translated; persistent ReplyKeyboard on text replies; recommend-button tap short-circuits to RECOMMEND; `tests/test_phrases.py` (10 tests).
- `[CODE]` 2026-06-29 Feedback refactor: normalized `user_content_feedback` schema (`watched`, `feedback`, `excluded`) with legacy migration; Telegram carousel row order ignore/watched/disliked/liked, add row, nav row; feedback toggles auto-advance; admin UI columns updated; `tests/test_feedback.py`.
- `[CODE]` 2026-06-29 `bot.recommendation_carousel_count`: limits LLM ask + carousel display + recent-recommendation cooldown; default 10 in `config.yaml`; test in `test_recommendation_prompt.py`.
- `[CODE]` 2026-06-29 Service API logging: `bot/service_request.py` wrapper; `bot/database/service_logs.py` (`ServiceLogMixin`, `service_api_logs`); wired in `jellyfin.py` + `telegram_bot.py`; `GET /admin/api/service-logs`; admin Logs tabs Media Management (Radarr/Sonarr) and Media Servers (Jellyfin); session timeline pills; tests in `tests/test_service_request.py`.
- `[CODE]` 2026-06-28 Recommendation prompt restructure: optional `recommendation_sources[].name` with generated fallback labels; grouped TMDB candidate fetch; new `bot/recommendation_prompt.py` builds system/profile/feedback/request OpenAI messages; `recommendation.mustache` renders source headers + TMDB overviews.
- `[CODE]` 2026-06-29 Recommendation prompt follow-up: moved user name/preferences/guidelines into the RECOMMEND system message and named Lena's discover sources in `config.yaml`.
- `[TOOL]` 2026-06-29 Full tests passed with `PYTHONPATH=. poetry run pytest` (59 passed).
- `[CODE]` 2026-06-28 Recommendation cooldown: `bot/database/recommendations.py` (`RecentRecommendationsMixin`, table `recent_recommendations`); merge recent TMDB IDs/titles into RECOMMEND exclusions; record shown carousel items; `/clear` wipes cooldown; config `bot.recommendation_exclude_ttl_hours`; tests in `tests/test_recent_recommendations.py`.

## Working Set
- `bot/database/__init__.py`
- `bot/telegram_bot.py`
- `bot/admin_ui.py`
- `bot/web/index.html`
- `bot/web/app.js`
- `tests/test_feedback.py`

## Decisions
- `D001 ACTIVE:` Use `INQUIRY` as the intent identifier.
- `D015 ACTIVE:` `[CODE]` 2026-06-29 Feedback state is one row per normalized content key with `watched` boolean, nullable `feedback` (`like|dislike`), and `excluded` boolean; legacy `feedback_type` rows migrate on DB init.
- `D014 ACTIVE:` `[CODE]` 2026-06-29 Bot hardcoded copy lives in `bot/phrases/data/*.yaml`; `preferences.bot_style` selects tone (`default|casual|warm|witty|cinephile`); `thinking` is style-specific; other keys use shared phrases with English fallback for non-en langs.
- `D013 ACTIVE:` `[CODE]` 2026-06-29 Recommendation source names are optional; prompt display uses configured `name` or generated labels like `Popular movies`/`Top rated TV shows`. RECOMMEND uses separate OpenAI input messages: system contains stable instructions plus user name/preferences/guidelines; user messages contain feedback history and current request/candidates.
