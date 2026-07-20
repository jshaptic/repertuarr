"""
Background monitoring for Radarr/Sonarr requests that do not reach download-ready webhooks.

Radarr and Sonarr notify us when a release is grabbed, imported, or needs manual
interaction, but they do not emit an event when an automatic search finds no
acceptable candidates. This module periodically inspects active media requests,
queries the relevant Arr API, and notifies the requesting Telegram user once
when a request appears unavailable or blocked.

When a media server (Plex/Jellyfin) is configured, grabbed requests whose Arr
queue is empty are also searched on the media server. A hit triggers the same
download-ready notification as a library webhook — a fallback when Plex
library.new (or similar) never fires.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional

from bot.download_monitor_arr import (
    first_download_id,
    has_acceptable_release,
    queue_block_reason,
    queue_records,
    release_candidates,
    resolve_arr,
)
from bot.phrases import get_media_type_label, get_phrase
from bot.phrases import keys as phrase_keys
from bot.telegram_notify import ensure_request_queued, send_lifecycle_message
from bot.webhook_events import notify_request_ready

logger = logging.getLogger(__name__)

DEFAULT_MONITOR_CONFIG = {
    'enabled': True,
    'poll_interval_minutes': 1,
    'no_grab_after_minutes': 1,
    'stalled_after_hours': 1,
}


def _monitor_config(config: dict) -> dict:
    monitor_config = dict(DEFAULT_MONITOR_CONFIG)
    monitor_config.update(config.get('download_monitor') or {})
    return monitor_config


def _parse_timestamp(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value))


def _request_age(request: dict, now: datetime) -> timedelta:
    created_at = _parse_timestamp(request.get('created_at'))
    if not created_at:
        return timedelta()
    return now - created_at


def _build_user_prefs_map(users_config: list, messenger_name: str) -> dict:
    user_prefs_map = {}
    for user in users_config:
        account = user.get('messenger', {})
        if account.get('messenger_name') == messenger_name:
            uid = account.get('user_id')
            if uid:
                user_prefs_map[uid] = user.get('preferences', {})
    return user_prefs_map


async def _notify_failure(
    bot_app,
    db,
    request: dict,
    prefs: dict,
    phrase_key: str,
    reason: str,
    status: str,
    detail: str = None,
):
    title = request.get('title') or 'requested item'
    media_type = request.get('media_type') or 'movie'
    type_label = get_media_type_label(prefs, media_type)
    text = get_phrase(prefs, phrase_key, title=title, type=type_label)
    if not await send_lifecycle_message(bot_app.bot, request['telegram_id'], text):
        return
    db.mark_request_failed(request['id'], reason=reason, detail=detail, status=status)


async def _mark_download_started(
    bot_app,
    db,
    request: dict,
    prefs: dict,
    download_id: str,
):
    if request.get('status') == 'pending':
        await ensure_request_queued(db, bot_app.bot, request, prefs)
        title = request.get('title') or 'requested item'
        media_type = request.get('media_type') or 'movie'
        type_label = get_media_type_label(prefs, media_type)
        text = get_phrase(prefs, phrase_keys.DOWNLOAD_STARTED, title=title, type=type_label)
        if not await send_lifecycle_message(bot_app.bot, request['telegram_id'], text):
            return
    db.mark_request_grabbed(request['id'], download_id=download_id)


async def inspect_download_request(
    config: dict,
    db,
    bot_app,
    request: dict,
    prefs: dict,
    now: datetime,
    media_server_client=None,
) -> None:
    monitor_config = _monitor_config(config)
    base_url, api_key = resolve_arr(config, request)
    if not base_url or not api_key:
        raise ValueError(f"Incomplete Arr config for request {request.get('id')}")

    records = queue_records(db, request, base_url, api_key)
    block_reason = queue_block_reason(records)
    if block_reason and _request_age(request, now) >= timedelta(hours=monitor_config['stalled_after_hours']):
        await _notify_failure(
            bot_app,
            db,
            request,
            prefs,
            phrase_keys.DOWNLOAD_FAILED,
            reason='queue_blocked',
            status='failed',
            detail=block_reason,
        )
        return
    if records:
        if block_reason:
            db.mark_request_checked(request['id'])
            return

        download_id = first_download_id(records)
        if download_id and request.get('status') == 'pending':
            await _mark_download_started(bot_app, db, request, prefs, download_id)
            return
        if download_id and not request.get('download_id'):
            db.mark_request_grabbed(request['id'], download_id=download_id)
            return
        db.mark_request_checked(request['id'])
        return

    if request.get('status') == 'grabbed' and media_server_client:
        notified = await notify_request_ready(
            db=db,
            bot_app=bot_app,
            request=request,
            prefs=prefs,
            media_server_client=media_server_client,
            require_url=True,
        )
        if notified:
            return
        db.mark_request_checked(request['id'])
        return

    if request.get('status') == 'pending' and _request_age(request, now) >= timedelta(minutes=monitor_config['no_grab_after_minutes']):
        releases = release_candidates(db, request, base_url, api_key)
        if not has_acceptable_release(releases):
            reason = 'no_candidates' if not releases else 'all_candidates_rejected'
            await _notify_failure(
                bot_app,
                db,
                request,
                prefs,
                phrase_keys.DOWNLOAD_UNAVAILABLE,
                reason=reason,
                status='unavailable',
                detail=f"{len(releases)} release candidates returned",
            )
            return

    db.mark_request_checked(request['id'])


async def check_download_requests(
    config: dict,
    db,
    bot_app,
    users_config: list,
    messenger_name: str,
    media_server_client=None,
) -> None:
    user_prefs_map = _build_user_prefs_map(users_config, messenger_name)
    now = datetime.now()

    for request in db.get_download_monitor_candidates():
        prefs = user_prefs_map.get(request['telegram_id'], {'language': 'en', 'bot_style': 'default'})
        try:
            await inspect_download_request(
                config,
                db,
                bot_app,
                request,
                prefs,
                now,
                media_server_client=media_server_client,
            )
        except Exception as exc:
            db.mark_request_checked(request['id'])
            logger.error("Download monitor failed for request %s: %s", request.get('id'), exc)


async def run_download_monitor(
    config: dict,
    db,
    bot_app,
    users_config: list,
    messenger_name: str,
    media_server_client=None,
) -> None:
    monitor_config = _monitor_config(config)
    interval = int(monitor_config['poll_interval_minutes']) * 60
    logger.info("Download monitor started with %ss interval", interval)

    while True:
        await check_download_requests(
            config,
            db,
            bot_app,
            users_config,
            messenger_name,
            media_server_client=media_server_client,
        )
        await asyncio.sleep(interval)


def start_download_monitor(
    config: dict,
    db,
    bot_app,
    users_config: list,
    messenger_name: str,
    media_server_client=None,
):
    monitor_config = _monitor_config(config)
    if not monitor_config.get('enabled', True):
        logger.info("Download monitor disabled")
        return None
    return asyncio.create_task(
        run_download_monitor(
            config,
            db,
            bot_app,
            users_config,
            messenger_name,
            media_server_client=media_server_client,
        )
    )
