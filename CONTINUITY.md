# Continuity Ledger

## Snapshot
**Date:** 2026-07-19
**Goal:** `[USER]` Multi-title and URL ADD_MEDIA (list URL → extract titles → batch carousel + Add all).
**Now:** `[CODE]` 2026-07-19 RU phrases added for list-extract / multi-add / Add all (`ru.yaml` + `lang_overlay_data.py`).
**Next:** `[USER]` Restart bot and live-test: bare list URL, multi-title message, Add all (RU prefs).
**Open Questions:** None.

## Done (recent)
- `[CODE]` 2026-07-19 Multi-title/URL ADD_MEDIA: `AddMediaItem`/`ListExtractResponse`; intent prompt URL+multi rules; `bot/list_extractor.py` + `list_extract.mustache`; `bot/add_media.py` normalize/resolve; carousel `batch` column + Add all; tests `tests/test_add_media.py`.
- `[CODE]` 2026-07-08 Telegram image support rebased: `bot/telegram_image.py`; vision intent + multimodal inquiry/recommend; `IntentResponse.image_description`; `tests/test_telegram_image.py`.
- `[CODE]` 2026-07-05 Custom recommendation pools (Phase 1): filter planner + TMDB filters; inquiry tool loop; intent titles-vs-facts rule.
- `[TOOL]` 2026-07-05 Local Poetry is 1.8.3 but pyproject is PEP-621 (Poetry 2.x): do NOT run `poetry lock` with 1.8.x.
- `[CODE]` 2026-06-30 Intent-specific thinking phrases; request_queued Telegram timeout fixes; phrase system milestone (compressed).

## Working Set
- `bot/models.py`
- `bot/prompts/intent_classification.mustache`
- `bot/prompts/list_extract.mustache`
- `bot/list_extractor.py`
- `bot/add_media.py`
- `bot/telegram_bot.py`
- `bot/database/chat.py`
- `bot/phrases/keys.py`
- `bot/phrases/data/en.yaml`
- `config.yaml`
- `main.py`
- `tests/test_add_media.py`

## Decisions
- `D022 ACTIVE:` `[USER]` 2026-07-19 URL list titles via LLM + native `web_search` list_extract (not HTML scrape / site APIs). Multi-title UX: one best-match carousel + Add all; single title keeps top-5 search carousel.
- `D001 ACTIVE:` Use `INQUIRY` as the intent identifier.
- `D019 ACTIVE:` `[USER]` 2026-07-05 Title-set answers → RECOMMEND; INQUIRY is facts/prose only.
- `D020 ACTIVE:` `[CODE]` 2026-07-05 Filter planner is separate nano-tier call; activates only when config entry exists.
- `D021 ACTIVE:` `[CODE]` 2026-07-05 Inquiry tools on one LLM call with iteration cap.
- `D018 ACTIVE:` `[USER]` 2026-06-29 Successful Add keeps carousel markup; progress via separate messages.
- `D014 ACTIVE:` `[CODE]` 2026-06-30 Phrase catalogs in `bot/phrases/data/*.yaml`; style-specific thinking keys.
- `D019 ACTIVE:` `[CODE]` 2026-07-02 Telegram photos via vision intent + `image_description`.
