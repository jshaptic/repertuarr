# Continuity Ledger

## Snapshot
**Date:** 2026-07-19
**Goal:** `[USER]` Admin + auto sync for chat history and flagged-title clearance.
**Now:** `[CODE]` 2026-07-20 Messenger clear probe also runs on `/start`.
**Next:** `[USER]` Live-test: clear Telegram chat, send `/start`, confirm Repertuarr chat wipe + sync ack.
**Open Questions:** None.

## Done (recent)
- `[CODE]` 2026-07-19 Chat/flags maintenance: `bot/chat_maintenance.py`, `bot/admin_clear.py`; DB clears for feedback/requests; admin UI clear buttons; messenger `copy_message` probe; removed `/clear`; tests `tests/test_chat_maintenance.py`.
- `[CODE]` 2026-07-19 Multi-title/URL ADD_MEDIA: `AddMediaItem`/`ListExtractResponse`; intent prompt URL+multi rules; `bot/list_extractor.py` + `list_extract.mustache`; `bot/add_media.py` normalize/resolve; carousel `batch` column + Add all; tests `tests/test_add_media.py`.
- `[CODE]` 2026-07-08 Telegram image support rebased: `bot/telegram_image.py`; vision intent + multimodal inquiry/recommend; `IntentResponse.image_description`; `tests/test_telegram_image.py`.
- `[CODE]` 2026-07-05 Custom recommendation pools (Phase 1): filter planner + TMDB filters; inquiry tool loop; intent titles-vs-facts rule.
- `[TOOL]` 2026-07-05 Local Poetry is 1.8.3 but pyproject is PEP-621 (Poetry 2.x): do NOT run `poetry lock` with 1.8.x.

## Working Set
- `bot/chat_maintenance.py`
- `bot/admin_clear.py`
- `bot/admin_ui.py`
- `bot/webhook.py`
- `bot/telegram_bot.py`
- `bot/database/chat.py`
- `bot/database/__init__.py`
- `bot/web/index.html`
- `bot/web/app.js`
- `bot/web/styles.css`
- `bot/phrases/keys.py`
- `tests/test_chat_maintenance.py`

## Decisions
- `D023 ACTIVE:` `[USER]` 2026-07-19 Admin clear chat = wipe transcript+carousels+recently shown + Telegram notify to clear messenger UI. Messenger-clear detect uses same wipe scope. `/clear` command removed. Per-bucket + master clear for flagged titles (requested = DB only).
- `D022 ACTIVE:` `[USER]` 2026-07-19 URL list titles via LLM + native `web_search` list_extract (not HTML scrape / site APIs). Multi-title UX: one best-match carousel + Add all; single title keeps top-5 search carousel.
- `D001 ACTIVE:` Use `INQUIRY` as the intent identifier.
- `D019 ACTIVE:` `[USER]` 2026-07-05 Title-set answers → RECOMMEND; INQUIRY is facts/prose only.
- `D020 ACTIVE:` `[CODE]` 2026-07-05 Filter planner is separate nano-tier call; activates only when config entry exists.
- `D021 ACTIVE:` `[CODE]` 2026-07-05 Inquiry tools on one LLM call with iteration cap.
- `D018 ACTIVE:` `[USER]` 2026-06-29 Successful Add keeps carousel markup; progress via separate messages.
- `D014 ACTIVE:` `[CODE]` 2026-06-30 Phrase catalogs in `bot/phrases/data/*.yaml`; style-specific thinking keys.
