# homelab-bot - Agent Instructions

This file serves as the canonical guidelines for any AI agents or tools interacting with the `homelab-bot` codebase. It outlines the project's architecture, technology stack, and strict rules for contributing to the project to maintain code quality, security, and continuity.

## Tech Stack & Architecture

**Core Technologies:**
- **Language:** Python 3.10+
- **Dependency Management:** Poetry (`pyproject.toml`)
- **Bot Framework:** `python-telegram-bot` (using ContextTypes, ApplicationBuilder, and Webhooks/Polling)
- **External Services:** 
  - **Media Management:** Radarr (Movies), Sonarr (Series)
  - **Media Server:** Jellyfin (watch history sync, playing)
  - **AI / LLM:** OpenAI API (`openai` package) for intent classification and media recommendations based on watch history.
- **Other Utilities:** `requests`, `aiohttp` for async HTTP processing, `pyyaml` for configuration handling, `chevron` for prompt rendering, `pydantic` for structured data from LLM.

**Architecture Overview:**
- **Entrypoint:** `main.py` is the orchestrator that loads the configuration from `config.yaml`, initializes messengers (Telegram), media servers (Jellyfin/Radarr/Sonarr), and kicks off the bot polling and the aiohttp-based webhook server.
- **Bot Logic:** Contained within the `bot/` directory.
  - `telegram_bot.py`: Main handlers for commands, messages, LLM classification, searching media, generating carousels, and inline button callbacks.
  - `models.py`: Pydantic models (e.g., `IntentResponse`, `RecommendationResponse`) for structured LLM parsing.
  - `database.py`: Local database operations for saving user feedback (watched/disliked), media requests, etc.
  - `webhook.py`: An `aiohttp` web server to receive notifications from Radarr/Sonarr to notify the user.
  - `jellyfin.py`: Client to interact with Jellyfin API.
  - `translations.py`: Localization strings mapping based on languages.
  - `prompts/`: Mustache templates used for LLM interaction.

## Important rules

* **File Descriptions**: Place a detailed description at the beginning of each file explaining what the file is for, what it's doing, and a general description.
* **Build modular first**: No code files longer than 300 lines of code! Documentation, plans, etc. can be as long as needed, but code files must be modular. 
  *(Note: The current `bot/telegram_bot.py` is over 700 lines. Refactoring this into smaller modules should be prioritized in future structural changes.)*
* **Think ahead!**: Do not write code that you know will need to be changed later without planning for that change now. So keep entrypoints stable and isolate logic into smaller modules from the start!
* **Do not limit yourself due to the LOC limit!**: If a task requires more code, split it into multiple files/modules/functions.
* **No default fallbacks during development**: If something fails, let it fail, so we can fix it!
* **No empty try-catch blocks**: Do not leave empty try-catch blocks anywhere! Handle exceptions explicitly or let them bubble up.
* **Do not reinvent the wheel**: Use open source, self-hosted libraries when needed. Ask the user, and help them qualify their selection. 
* **Design UI for the end-user, not for the schema**: Prioritize user experience (e.g., the Telegram carousel and inline buttons UX) over the raw data structures returned by the APIs.
* **Running Python in terminal**: If python needs to be run in the terminal, it should be called using poetry (e.g., `poetry run python3 ...`).

## Secrets and sensitive data

- Never print secrets (tokens, private keys, credentials) to terminal output.
- Do not request users paste secrets.
- Avoid commands that might expose secrets (e.g., dumping env vars broadly, `cat ~/.ssh/*`, or accidentally exposing `config.yaml` with keys).
- Prefer existing authenticated CLIs; redact sensitive strings in any displayed output.

## Continuity Ledger (compaction-safe)

Maintain a single continuity file for this workspace: `CONTINUITY.md`.
`CONTINUITY.md` is the canonical briefing designed to survive compaction; do not rely on earlier chat/tool output unless it's reflected there.

### Operating rule
- At the start of each assistant turn: read `CONTINUITY.md` before acting.
- Update `CONTINUITY.md` only when there is a meaningful delta in: Goal/success criteria, Invariants/constraints, Decisions, State (Done/Now/Next), Open questions, Working set, or important tool outcomes.

### Keep it bounded (anti-bloat)
- Keep `CONTINUITY.md` short and high-signal:
  - `Snapshot`: ≤ 25 lines.
  - `Done (recent)`: ≤ 7 bullets.
  - `Working set`: ≤ 12 paths.
  - `Receipts`: keep last 10–20 entries.
- If sections exceed caps, compress older items into milestone bullets with pointers (commit/PR/log path/doc path). Do not paste raw logs.

### Anti-drift rules
- Facts only, no transcripts.
- Every entry must include:
  - a date or ISO timestamp (e.g., `2026-01-13` or `2026-01-13T09:42Z`)
  - a provenance tag: `[USER]`, `[CODE]`, `[TOOL]`, `[ASSUMPTION]`
- If unknown, write `UNCONFIRMED` (never guess). If something changes, supersede it explicitly (don't silently rewrite history).

### Decisions and incidents
- Record durable choices in `Decisions` as ADR-lite entries (e.g., `D001 ACTIVE: …`).
- For recurring weirdness, create a small, stable incident capsule (Symptoms / Evidence pointers / Mitigation / Status).

### Plan tool vs ledger
- Use `update_plan` for short-term execution scaffolding (3–7 steps).
- Use `CONTINUITY.md` for long-running continuity ("what/why/current state"), not micro task lists.
- Keep them consistent at the intent/progress level.

### In replies
- Start with a brief "Ledger Snapshot" (Goal + Now + Next + Open Questions).
- Print the full ledger only when it materially changed or the user requests it.
