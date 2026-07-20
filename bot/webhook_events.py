"""
Helpers for Radarr/Sonarr webhook lifecycle events and download-ready notices.

The aiohttp route handlers in bot.webhook keep HTTP parsing and response logic,
while this module owns request matching, grab state updates, failure
notifications, and the shared "media is ready" Telegram notify path used by
both media-server webhooks and the download monitor.
"""

import logging
from typing import Optional

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


async def notify_request_ready(
    db,
    bot_app,
    request: dict,
    prefs: dict,
    media_server_client=None,
    media_url: Optional[str] = None,
    require_url: bool = False,
) -> bool:
    """
    Notify a user that their requested title is ready to play.

    Resolves a play URL via the media server when needed. When ``require_url``
    is True (download-monitor path), a missing URL means "not ready yet" and
    no notification is sent. Returns True when the request was marked notified.
    """
    telegram_id = request['telegram_id']
    request_id = request['id']
    title = request.get('title') or 'requested item'
    media_type = request.get('media_type') or 'movie'
    type_label = get_media_type_label(prefs, media_type)

    if not media_url and media_server_client:
        media_url = media_server_client.search_item(
            title,
            media_type,
            tmdb_id=request.get('tmdb_id'),
            tvdb_id=request.get('tvdb_id'),
        )
        logger.info(
            "%s search URL for '%s': %s",
            media_server_client.display_name,
            title,
            media_url,
        )

    if require_url and not media_url:
        return False

    if media_url and media_server_client:
        text = get_phrase(
            prefs,
            phrase_keys.DOWNLOAD_READY,
            title=title,
            type=type_label,
            url=media_url,
            server=media_server_client.display_name,
        )
    else:
        text = get_phrase(
            prefs,
            phrase_keys.DOWNLOAD_READY_NO_URL,
            title=title,
            type=type_label,
        )

    try:
        await bot_app.bot.send_message(
            chat_id=telegram_id,
            text=text,
            parse_mode='Markdown',
        )
        db.mark_request_notified(request_id)
        logger.info(f"Notified user {telegram_id} about '{title}'")
        return True
    except Exception as e:
        logger.error(f"Failed to notify user {telegram_id} about '{title}': {e}")
        return False


async def notify_matching_requests(
    db,
    bot_app,
    user_prefs_map: dict,
    title: str,
    media_type: str,
    media_server_client=None,
    tmdb_id: str = None,
    tvdb_id: str = None,
    media_url: str = None,
):
    """Match a downloaded item against active requests and notify each user."""
    requests_found = db.find_pending_requests(title=title, tmdb_id=tmdb_id, tvdb_id=tvdb_id)

    if not requests_found:
        logger.info(f"No pending requests matched for '{title}'")
        return

    for req in requests_found:
        prefs = user_prefs_map.get(
            req['telegram_id'],
            {'language': 'en', 'bot_style': 'default'},
        )
        # Prefer the request's stored title; fall back to webhook title.
        notify_req = dict(req)
        if not notify_req.get('title'):
            notify_req['title'] = title
        if not notify_req.get('media_type'):
            notify_req['media_type'] = media_type
        await notify_request_ready(
            db=db,
            bot_app=bot_app,
            request=notify_req,
            prefs=prefs,
            media_server_client=media_server_client,
            media_url=media_url,
            require_url=False,
        )
