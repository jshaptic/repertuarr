"""
Reliable Telegram delivery helpers for request lifecycle notifications.

Arr add/search calls can block for a minute; lifecycle messages use retries and
are tracked in the database so a later Grab webhook can still deliver a missed
request_queued notification.
"""

import asyncio
import logging

from telegram.error import NetworkError, TimedOut

from bot.phrases import get_media_type_label, get_phrase
from bot.phrases import keys as phrase_keys

logger = logging.getLogger(__name__)

MAX_SEND_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 2


async def send_lifecycle_message(bot, chat_id: int, text: str, *, parse_mode: str = 'Markdown') -> bool:
    """Send a lifecycle message, retrying transient Telegram network errors."""
    for attempt in range(1, MAX_SEND_ATTEMPTS + 1):
        try:
            await bot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode)
            return True
        except (TimedOut, NetworkError) as exc:
            if attempt == MAX_SEND_ATTEMPTS:
                logger.error(
                    "Failed to send lifecycle message to chat %s after %s attempts: %s",
                    chat_id,
                    MAX_SEND_ATTEMPTS,
                    exc,
                )
                return False
            logger.warning(
                "Lifecycle message to chat %s timed out (attempt %s/%s), retrying",
                chat_id,
                attempt,
                MAX_SEND_ATTEMPTS,
            )
            await asyncio.sleep(RETRY_DELAY_SECONDS)


async def notify_request_queued(db, bot, request_id: int, telegram_id: int, prefs: dict, title: str) -> bool:
    """Send request_queued once and persist delivery in the database."""
    request = db.get_media_request(request_id)
    if not request or request.get('queued_notified_at'):
        return bool(request and request.get('queued_notified_at'))

    title = request.get('title') or 'requested item'
    media_type = request.get('media_type') or 'movie'
    type_label = get_media_type_label(prefs, media_type)
    text = get_phrase(prefs, phrase_keys.REQUEST_QUEUED, title=title, type=type_label)
    if await send_lifecycle_message(bot, telegram_id, text):
        db.mark_request_queued_notified(request_id)
        return True
    return False


async def ensure_request_queued(db, bot, request: dict, prefs: dict) -> bool:
    """Deliver request_queued if an earlier Add flow failed to notify the user."""
    if request.get('queued_notified_at'):
        return True
    title = request.get('title') or 'requested item'
    return await notify_request_queued(
        db,
        bot,
        request['id'],
        request['telegram_id'],
        prefs,
        title,
    )
