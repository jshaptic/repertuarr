# Continuity Ledger

## Snapshot
**Date:** 2026-07-08
**Goal:** `[USER]` Agent architecture (filter planner, tool-based inquiry, Plex, CI/CD) plus Telegram photo support rebased on top.
**Now:** `[CODE]` 2026-07-08 Rebased local photo commit onto `origin/main`; conflicts resolved in `telegram_bot.py` (intent_handlers + multimodal inquiry) and `CONTINUITY.md`.
**Next:** `[USER]` Restart bot and live-test photo flows (poster, scene still, recommend-with-image) alongside new agent features; add `agent.prompts.filter_planner` to config.yaml if not present.
**Open Questions:** None.

## Done (recent)
- `[CODE]` 2026-07-08 Telegram image support rebased: `bot/telegram_image.py`; vision intent + multimodal inquiry/recommend; `IntentResponse.image_description`; `tests/test_telegram_image.py`.
- `[CODE]` 2026-07-05 Custom recommendation pools (Phase 1): `RecommendationPlan/Filters` models; `bot/filter_planner.py`; `bot/recommendation_filters.py`; `tmdb.py` search/credits; tests `test_tmdb_search.py`, `test_recommendation_filters.py`.
- `[CODE]` 2026-07-05 Inquiry tool loop (Phase 2): `bot/inquiry_tools.py` + `bot/inquiry_agent.py`; `handle_inquiry_request` delegates to `run_inquiry`; tests `test_inquiry_agent.py`.
- `[CODE]` 2026-07-05 Intent prompt titles-vs-facts rule; `intent_handlers` registry in `telegram_bot.py`.
- `[TOOL]` 2026-07-05 Local Poetry is 1.8.3 but pyproject is PEP-621 (Poetry 2.x): `poetry install` resolves nothing; deps were pip-installed into the poetry venv directly. Do NOT run `poetry lock` with 1.8.x (it empties the lock; was restored via git checkout).
- `[CODE]` 2026-06-30 Intent-specific thinking phrases: `thinking_inquiry`, `thinking_recommend`, `thinking_add_media` per style; removed witty/cinephile; ADD_MEDIA shows thinking message; non-en catalogs in `lang_overlay_data.py` + `build_lang_yamls.py`.
- `[CODE]` 2026-06-30 Fixed `request_queued` Telegram timeouts: Arr add moved to `asyncio.to_thread`, lifecycle sends retry transient Telegram errors, `queued_notified_at` tracks delivery, Grab/monitor backfill missed queued messages, ApplicationBuilder timeouts raised to 30s.
- `[CODE]` 2026-06-28..29 Milestone (compressed): download failure detection + request status messages (`media_requests` lifecycle, webhooks, `download_monitor.py`); admin user page refactor + chat restyle; TMDB pre-filter with pagination backfill; phrase system (5 styles × 30 langs, recommend button short-circuit); normalized `user_content_feedback`; `recommendation_carousel_count`; service API logging. Details in git history 2026-06-28..30.

## Working Set
- `bot/telegram_bot.py`
- `bot/models.py`
- `bot/tmdb.py`
- `bot/recommendation_pool.py`
- `bot/recommendation_filters.py`
- `bot/filter_planner.py`
- `bot/inquiry_tools.py`
- `bot/inquiry_agent.py`
- `bot/prompts/filter_planner.mustache`
- `bot/prompts/intent_classification.mustache`
- `bot/prompts/inquiry.mustache`
- `main.py`

## Decisions
- `D001 ACTIVE:` Use `INQUIRY` as the intent identifier.
- `D019 ACTIVE:` `[USER]` 2026-07-05 "TMDB query" and "custom recommendation" are ONE capability: any request whose answer is a set of titles routes to RECOMMEND (unified title discovery: filter planner -> TMDB pool -> curation -> carousel), regardless of result-set size; INQUIRY answers facts/prose only. RECOMMEND literal kept for analytics continuity.
- `D020 ACTIVE:` `[CODE]` 2026-07-05 Filter extraction is a separate nano-tier planner call (`agent.prompts.filter_planner`), NOT part of the intent prompt (intent runs on every message; planner needs the live TMDB genre vocabulary). Planner failure degrades to predefined sources; feature activates only when the config entry exists.
- `D021 ACTIVE:` `[CODE]` 2026-07-05 Inquiry sub-capabilities are function tools on one LLM call (native web_search + tmdb_search + tmdb_person_credits), not routed branches; loop threads context via explicit input concatenation (not previous_response_id) so every request round-trips through the existing LLM logging; `bot.inquiry_max_tool_iterations` caps the loop, then `tool_choice="none"` forces an answer.
- `D017 ACTIVE:` `[CODE]` 2026-06-29 Download failure detection uses a hybrid Arr approach: lifecycle webhooks for `Grab`/`Download`/`ManualInteractionRequired`, plus a background Arr API monitor for the no-native-event case where automatic search yields no acceptable release candidate; qBittorrent is not required for the core feature.
- `D018 ACTIVE:` `[USER]` 2026-06-29 Successful Add keeps the carousel button/markup unchanged; request progress is communicated with separate Telegram messages (`request_queued`, `download_started`, then ready/failure/unavailable).
- `D016 ACTIVE:` `[CODE]` 2026-06-29 Recommendation exclusions apply at TMDB candidate pre-filter only (IDs + titles, per-source backfill); LLM output is shown as-is with no post-filter.
- `D015 ACTIVE:` `[CODE]` 2026-06-29 Feedback state is one row per normalized content key with `watched` boolean, nullable `feedback` (`like|dislike`), and `excluded` boolean; legacy `feedback_type` rows migrate on DB init.
- `D019 ACTIVE:` `[CODE]` 2026-07-02 Telegram photos: largest-size download, vision intent via optional `vision_llm`, `image_description` on `IntentResponse`, image passed to inquiry/recommend only for current turn; history stores `[Image]` text summaries.
- `D014 ACTIVE:` `[CODE]` 2026-06-30 Bot hardcoded copy lives in `bot/phrases/data/*.yaml`; `preferences.bot_style` selects tone (`default|casual|warm|sarcastic|wizarding`); intent-specific thinking keys (`thinking_inquiry`, `thinking_recommend`, `thinking_add_media`) are style-specific; other keys use shared phrases with English fallback for non-en langs.
- `D013 ACTIVE:` `[CODE]` 2026-06-29 Recommendation source names are optional; prompt display uses configured `name` or generated labels like `Popular movies`/`Top rated TV shows`. RECOMMEND uses separate OpenAI input messages: system contains stable instructions plus user name/preferences/guidelines; user messages contain feedback history and current request/candidates.
