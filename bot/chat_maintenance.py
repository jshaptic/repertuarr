"""
Shared chat and flagged-title clearance helpers.

Used by the admin API (manual wipe + notify) and by the Telegram message
handler (auto-sync when the user clears messenger history first). Keeps the
wipe scope in one place so admin and messenger probe stay aligned:
transcript + carousels + recently shown recommendations.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from telegram.error import BadRequest

logger = logging.getLogger(__name__)

FLAGGED_BUCKETS = frozenset({
    "retained",
    "requested",
    "watched",
    "liked",
    "disliked",
    "not_interested",
})

_NOT_FOUND_MARKERS = (
    "message to copy not found",
    "message not found",
    "message to forward not found",
    "message can't be copied",
)


def clear_chat_state(db, user_id: int) -> dict:
    """Wipe transcript, carousels, and recently shown titles for a user."""
    messages = db.clear_chat(user_id)
    carousels = db.clear_user_carousels(user_id)
    retained = db.clear_recent_recommendations(user_id)
    return {
        "messages": messages,
        "carousels": carousels,
        "retained": retained,
    }


def clear_flagged_bucket(db, user_id: int, bucket: str) -> int:
    """Delete one admin flagged-title bucket. Returns rows removed."""
    if bucket not in FLAGGED_BUCKETS:
        raise ValueError(f"Unsupported flagged bucket: {bucket}")

    if bucket == "retained":
        return db.clear_recent_recommendations(user_id)
    if bucket == "requested":
        return db.clear_media_requests(user_id)
    if bucket == "watched":
        return db.clear_user_feedback(user_id, watched=True)
    if bucket == "liked":
        return db.clear_user_feedback(user_id, feedback="like")
    if bucket == "disliked":
        return db.clear_user_feedback(user_id, feedback="dislike")
    return db.clear_user_feedback(user_id, excluded=True)


def clear_all_flagged(db, user_id: int) -> dict:
    """Clear all six flagged-title buckets for a user."""
    return {
        "retained": db.clear_recent_recommendations(user_id),
        "requested": db.clear_media_requests(user_id),
        "feedback": db.clear_user_feedback(user_id),
    }


def clear_everything(db, user_id: int) -> dict:
    """Clear chat state and every flagged-title bucket."""
    chat = clear_chat_state(db, user_id)
    # retained was already wiped by clear_chat_state; remaining buckets follow.
    flagged = clear_all_flagged(db, user_id)
    flagged["retained"] = chat["retained"]
    return {"chat": chat, "flagged": flagged}


def _is_message_not_found(exc: BadRequest) -> bool:
    message = str(exc).lower()
    return any(marker in message for marker in _NOT_FOUND_MARKERS)


async def messenger_history_missing(bot, chat_id: int, message_id: int) -> bool:
    """Return True when a previously stored Telegram message is gone.

    Probes by copying the message into the same chat, then deleting the copy.
    A BadRequest that indicates the source message is missing means the user
    cleared messenger history.
    """
    try:
        copied = await bot.copy_message(
            chat_id=chat_id,
            from_chat_id=chat_id,
            message_id=message_id,
        )
    except BadRequest as exc:
        if _is_message_not_found(exc):
            return True
        raise

    copy_id = copied.message_id if hasattr(copied, "message_id") else copied
    try:
        await bot.delete_message(chat_id=chat_id, message_id=copy_id)
    except BadRequest as exc:
        logger.warning(
            "Failed to delete messenger history probe copy %s in chat %s: %s",
            copy_id,
            chat_id,
            exc,
        )
    return False


async def sync_if_messenger_cleared(db, bot, user_id: int) -> bool:
    """If messenger history is gone, wipe chat state.

    Returns True only when a non-empty Repertuarr transcript was wiped, so
    callers can send a user-facing sync ack. If the DB transcript is already
    empty, returns False (no ack).
    """
    probe: Optional[dict[str, Any]] = db.get_history_probe(user_id)
    if not probe:
        return False

    # Nothing stored on our side — no sync notice to send.
    if not db.get_chat_messages(user_id, limit=1):
        return False

    missing = await messenger_history_missing(
        bot, probe["chat_id"], probe["message_id"],
    )
    if not missing:
        return False

    counts = clear_chat_state(db, user_id)
    logger.info(
        "Messenger history missing for user %s; cleared chat state %s",
        user_id,
        counts,
    )
    return counts["messages"] > 0
