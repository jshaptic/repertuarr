"""Tests for resilient Telegram lifecycle notification delivery."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from telegram.error import TimedOut

from bot.database import Database
from bot.telegram_notify import ensure_request_queued, notify_request_queued, send_lifecycle_message


async def _exercise_send_lifecycle_message_retries():
    bot = SimpleNamespace(send_message=AsyncMock(side_effect=[TimedOut(), None]))

    delivered = await send_lifecycle_message(bot, chat_id=100, text="hello")

    assert delivered is True
    assert bot.send_message.await_count == 2


def test_send_lifecycle_message_retries_timed_out():
    asyncio.run(_exercise_send_lifecycle_message_retries())


async def _exercise_notify_request_queued_marks_database_once(tmp_path):
    db = Database(db_path=str(tmp_path / "queued.db"))
    request_id = db.add_media_request(
        telegram_id=100,
        title="Example Movie",
        media_type="movie",
        tmdb_id="123",
    )
    bot = SimpleNamespace(send_message=AsyncMock())

    delivered = await notify_request_queued(
        db,
        bot,
        request_id,
        100,
        {"language": "en", "bot_style": "default"},
        "Example Movie",
    )

    assert delivered is True
    request = db.get_media_request(request_id)
    assert request["queued_notified_at"] is not None
    bot.send_message.assert_awaited_once()

    bot.send_message.reset_mock()
    delivered_again = await notify_request_queued(
        db,
        bot,
        request_id,
        100,
        {"language": "en", "bot_style": "default"},
        "Example Movie",
    )
    assert delivered_again is True
    bot.send_message.assert_not_awaited()


def test_notify_request_queued_marks_database_once(tmp_path):
    asyncio.run(_exercise_notify_request_queued_marks_database_once(tmp_path))


async def _exercise_ensure_request_queued_sends_missing_notification(tmp_path):
    db = Database(db_path=str(tmp_path / "ensure.db"))
    request_id = db.add_media_request(
        telegram_id=100,
        title="Wild Tales",
        media_type="movie",
        tmdb_id="265195",
    )
    request = db.get_media_request(request_id)
    bot = SimpleNamespace(send_message=AsyncMock())

    delivered = await ensure_request_queued(
        db,
        bot,
        request,
        {"language": "en", "bot_style": "default"},
    )

    assert delivered is True
    bot.send_message.assert_awaited_once()
    assert "Wild Tales" in bot.send_message.await_args.kwargs["text"]


def test_ensure_request_queued_sends_missing_notification(tmp_path):
    asyncio.run(_exercise_ensure_request_queued_sends_missing_notification(tmp_path))
