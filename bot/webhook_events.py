"""
Helpers for Radarr/Sonarr webhook lifecycle events.

The aiohttp route handlers in bot.webhook keep HTTP parsing and response logic,
while this module owns request matching, grab state updates, and failure
notifications for Arr events that are not final download-ready notifications.
"""

import logging

from .phrases import get_media_type_label, get_phrase
from .phrases import keys as phrase_keys
from .telegram_notify import ensure_request_queued, send_lifecycle_message

logger = logging.getLogger(__name__)


def build_user_prefs_map(users_config: list, messenger_name: str) -> dict:
    """Build a lookup of Telegram user id to bot preferences."""
    user_prefs_map = {}
    for user in users_config:
        account = user.get('messenger', {})
        if account.get('messenger_name') == messenger_name:
            uid = account.get('user_id')
            if uid:
                user_prefs_map[uid] = user.get('preferences', {})
    return user_prefs_map


async def mark_grabbed(
    db,
    bot_app,
    user_prefs_map: dict,
    payload: dict,
    title: str,
    media_type: str,
    arr_service: str,
    arr_id: int = None,
    tmdb_id: str = None,
    tvdb_id: str = None,
):
    """Record that Radarr/Sonarr successfully sent a release to a client."""
    download_id = payload.get('downloadId')
    requests_found = db.find_active_requests(
        title=title,
        tmdb_id=tmdb_id,
        tvdb_id=tvdb_id,
        media_type=media_type,
        arr_service=arr_service,
        arr_id=arr_id,
        download_id=download_id,
    )

    if not requests_found:
        logger.info(f"No active requests matched {arr_service} grab for '{title}'")
        return

    for req in requests_found:
        display_title = title or req.get('title') or 'requested item'
        if req.get('status') == 'pending':
            telegram_id = req['telegram_id']
            prefs = user_prefs_map.get(telegram_id, {'language': 'en', 'bot_style': 'default'})
            await ensure_request_queued(db, bot_app.bot, req, prefs)
            type_label = get_media_type_label(prefs, media_type)
            text = get_phrase(
                prefs,
                phrase_keys.DOWNLOAD_STARTED,
                title=display_title,
                type=type_label,
            )
            if not await send_lifecycle_message(bot_app.bot, telegram_id, text):
                continue

        db.mark_request_grabbed(req['id'], download_id=download_id)
        logger.info(f"Marked request {req['id']} as grabbed for '{display_title}'")


def _failure_detail(payload: dict) -> str:
    release = payload.get('release') or {}
    download_info = payload.get('downloadInfo') or {}
    release_title = release.get('releaseTitle') or download_info.get('title')
    download_client = payload.get('downloadClient')
    if release_title and download_client:
        return f"{release_title} via {download_client}"
    return release_title or download_client or 'Manual interaction required'


async def notify_failed_requests(
    db,
    bot_app,
    user_prefs_map: dict,
    payload: dict,
    title: str,
    media_type: str,
    arr_service: str,
    arr_id: int = None,
    tmdb_id: str = None,
    tvdb_id: str = None,
    reason: str = 'download_failed',
    status: str = 'failed',
):
    """Notify users about Arr lifecycle failures for matching requests."""
    download_id = payload.get('downloadId')
    requests_found = db.find_active_requests(
        title=title,
        tmdb_id=tmdb_id,
        tvdb_id=tvdb_id,
        media_type=media_type,
        arr_service=arr_service,
        arr_id=arr_id,
        download_id=download_id,
    )

    if not requests_found:
        logger.info(f"No active requests matched {arr_service} failure for '{title}'")
        return

    detail = _failure_detail(payload)
    for req in requests_found:
        telegram_id = req['telegram_id']
        prefs = user_prefs_map.get(telegram_id, {'language': 'en', 'bot_style': 'default'})
        type_label = get_media_type_label(prefs, media_type)
        text = get_phrase(prefs, phrase_keys.DOWNLOAD_FAILED, title=title, type=type_label)

        try:
            await bot_app.bot.send_message(
                chat_id=telegram_id,
                text=text,
                parse_mode='Markdown',
            )
            db.mark_request_failed(req['id'], reason=reason, detail=detail, status=status)
            logger.info(f"Notified user {telegram_id} about failed request '{title}'")
        except Exception as e:
            logger.error(f"Failed to notify user {telegram_id} about failed request '{title}': {e}")
