"""
Admin API handlers for clearing chat history and flagged titles.

Mounted under /admin/api/users/{user_id}/… so the admin UI can wipe
Repertuarr state and (for chat clear) notify the user in Telegram.
"""

from __future__ import annotations

import json
import logging

from aiohttp import web

from bot.chat_maintenance import (
    FLAGGED_BUCKETS,
    clear_everything,
    clear_flagged_bucket,
    clear_chat_state,
)
from bot.phrases import get_phrase
from bot.phrases import keys as phrase_keys
from bot.telegram_notify import send_lifecycle_message
from bot.webhook_events import build_user_prefs_map

logger = logging.getLogger(__name__)


def register_admin_clear_routes(
    app: web.Application,
    db,
    users_config: list,
    messenger_name: str,
    bot_app,
) -> None:
    """Register mutating clear endpoints on the admin aiohttp app."""
    user_prefs_map = build_user_prefs_map(users_config, messenger_name)

    def _parse_user_id(request) -> int:
        return int(request.match_info["user_id"])

    async def api_clear_chat(request):
        try:
            user_id = _parse_user_id(request)
            counts = clear_chat_state(db, user_id)
            prefs = user_prefs_map.get(user_id, {})
            text = get_phrase(prefs, phrase_keys.ADMIN_CLEAR_CHAT_NOTIFY)
            notified = False
            if bot_app is None:
                logger.error("Cannot notify user %s: bot_app is not configured", user_id)
            else:
                notified = await send_lifecycle_message(bot_app.bot, user_id, text)
            return web.json_response({
                "ok": True,
                "user_id": user_id,
                "cleared": counts,
                "notified": notified,
            })
        except ValueError as exc:
            return web.json_response({"error": str(exc)}, status=400)
        except Exception as exc:
            logger.error("Error clearing chat: %s", exc)
            return web.json_response({"error": str(exc)}, status=500)

    async def api_clear_flags(request):
        try:
            user_id = _parse_user_id(request)
            try:
                body = await request.json()
            except json.JSONDecodeError as exc:
                return web.json_response({"error": f"Invalid JSON: {exc}"}, status=400)
            bucket = (body or {}).get("bucket")
            if not bucket:
                return web.json_response({"error": "bucket is required"}, status=400)
            if bucket not in FLAGGED_BUCKETS:
                return web.json_response(
                    {"error": f"Unsupported bucket: {bucket}"},
                    status=400,
                )
            removed = clear_flagged_bucket(db, user_id, bucket)
            return web.json_response({
                "ok": True,
                "user_id": user_id,
                "bucket": bucket,
                "removed": removed,
            })
        except ValueError as exc:
            return web.json_response({"error": str(exc)}, status=400)
        except Exception as exc:
            logger.error("Error clearing flags: %s", exc)
            return web.json_response({"error": str(exc)}, status=500)

    async def api_clear_everything(request):
        try:
            user_id = _parse_user_id(request)
            counts = clear_everything(db, user_id)
            prefs = user_prefs_map.get(user_id, {})
            text = get_phrase(prefs, phrase_keys.ADMIN_CLEAR_CHAT_NOTIFY)
            notified = False
            if bot_app is None:
                logger.error("Cannot notify user %s: bot_app is not configured", user_id)
            else:
                notified = await send_lifecycle_message(bot_app.bot, user_id, text)
            return web.json_response({
                "ok": True,
                "user_id": user_id,
                "cleared": counts,
                "notified": notified,
            })
        except ValueError as exc:
            return web.json_response({"error": str(exc)}, status=400)
        except Exception as exc:
            logger.error("Error clearing everything: %s", exc)
            return web.json_response({"error": str(exc)}, status=500)

    app.router.add_post("/admin/api/users/{user_id}/clear-chat", api_clear_chat)
    app.router.add_post("/admin/api/users/{user_id}/clear-flags", api_clear_flags)
    app.router.add_post(
        "/admin/api/users/{user_id}/clear-everything", api_clear_everything,
    )
    logger.info("Registered Admin clear API routes")
