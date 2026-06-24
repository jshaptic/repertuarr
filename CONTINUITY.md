# Continuity Ledger

## Snapshot
**Date:** 2026-06-24
**Goal:** Add `original_title` to LLM responses; display localized title/overview in Telegram, search Radarr/Sonarr with original title. Fix Telegram button payload limits.
**Now:** Fixed Telegram `Button_data_invalid` error by truncating callback data and recovering full titles from message captions. Verified with unit tests.
**Next:** Run the bot locally, test with a non-English language user to confirm localized carousel, successful Radarr/Sonarr lookups, and watched/disliked feedback logging.
**Open Questions:** None.

## Done (recent)
- `[CODE]` 2026-06-24 Fixed `Button_data_invalid` by safely truncating callback data titles (under 60 bytes) and recovering full titles from captions in `telegram_bot.py`.
- `[CODE]` 2026-06-24 Added `original_title` field to `RecommendationItem` in `models.py`.
- `[CODE]` 2026-06-24 Updated `recommendation.mustache` — split language instruction: title/overview in user lang, original_title in original lang.
- `[CODE]` 2026-06-24 Updated `inquiry.mustache` — added `{{#language}}` block with original_title guidance.
- `[CODE]` 2026-06-24 Updated `telegram_bot.py` — pass `language` to inquiry prompt, use `original_title` for Radarr/Sonarr lookups, preserve localized display fields (`_display_title`/`_display_overview`).
- `[CODE]` 2026-06-24 Rewrote admin UI files (HTML, CSS, JS) — branding, modal, responsive.
- `[CODE]` 2026-06-23 Implemented `get_users_summary` in `bot/database.py`.

## Working Set
- `bot/models.py`
- `bot/prompts/recommendation.mustache`
- `bot/prompts/inquiry.mustache`
- `bot/telegram_bot.py`

## Decisions
- `D001 ACTIVE:` Use `INQUIRY` as the intent identifier.
- `D003 ACTIVE:` INQUIRY responses are parsed as structured `InquiryResponse`, returning a `reply_text` and an optional `items` list.
- `D004 ACTIVE:` Use `client.responses.parse()` API with `web_search_preview` tool for INQUIRY and RECOMMEND intents.
- `D005 ACTIVE:` Admin UI is served on the same `aiohttp` server as the webhook, unauthenticated by default.
- `D006 ACTIVE:` Admin UI branding renamed to "Repertuarr".
- `D007 ACTIVE:` LLM returns `original_title` alongside localized `title`; Radarr/Sonarr lookups use `original_title`, Telegram display uses localized `title`/`overview`.
