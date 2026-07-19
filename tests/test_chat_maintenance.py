"""Tests for chat history and flagged-title clearance helpers."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer
from telegram.error import BadRequest

from bot.admin_clear import register_admin_clear_routes
from bot.chat_maintenance import (
    clear_chat_state,
    clear_everything,
    clear_flagged_bucket,
    messenger_history_missing,
    sync_if_messenger_cleared,
)
from bot.database import Database
from bot.models import RecommendationItem


@pytest.fixture
def db(tmp_path):
    return Database(db_path=str(tmp_path / "test.db"))


def _seed_user_state(db: Database, user_id: int = 42) -> None:
    db.add_chat_message(user_id, chat_id=user_id, role="user", text="hi", message_id=10)
    db.add_chat_message(user_id, chat_id=user_id, role="assistant", text="hello", message_id=11)
    db.save_carousel_state(
        chat_id=user_id,
        message_id=11,
        user_id=user_id,
        media_type="movie",
        results=[{"title": "A"}],
    )
    db.record_recent_recommendations(
        user_id,
        [RecommendationItem(title="Recent", original_title="Recent", year=2020, overview="o", tmdb_id=1)],
    )
    db.add_media_request(telegram_id=user_id, title="Requested", media_type="movie", tmdb_id="2")
    db.set_feedback_state(user_id, "101", "movie", "Watched", watched=True, tmdb_id="101")
    db.set_feedback_state(user_id, "102", "movie", "Liked", watched=True, feedback="like", tmdb_id="102")
    db.set_feedback_state(user_id, "103", "movie", "Disliked", watched=True, feedback="dislike", tmdb_id="103")
    db.set_feedback_state(user_id, "104", "movie", "Ignored", excluded=True, tmdb_id="104")


def test_clear_chat_state_wipes_transcript_carousels_and_retained(db):
    _seed_user_state(db)
    counts = clear_chat_state(db, 42)

    assert counts["messages"] == 2
    assert counts["carousels"] == 1
    assert counts["retained"] == 1
    assert db.get_chat_messages(42) == []
    assert db.get_history_probe(42) is None
    assert db.get_recent_recommendations(42, 3600) == []
    # Flagged titles outside chat scope remain.
    assert len(db.get_user_feedback(42)) == 4
    assert len(db.get_recent_media_requests(user_id=42)) == 1


def test_clear_flagged_buckets(db):
    _seed_user_state(db)

    assert clear_flagged_bucket(db, 42, "retained") == 1
    assert clear_flagged_bucket(db, 42, "requested") == 1
    # watched=1 rows include liked/disliked titles marked watched
    assert clear_flagged_bucket(db, 42, "watched") == 3
    assert clear_flagged_bucket(db, 42, "not_interested") == 1

    db.set_feedback_state(42, "202", "movie", "Liked", watched=True, feedback="like", tmdb_id="202")
    assert clear_flagged_bucket(db, 42, "liked") == 1
    db.set_feedback_state(42, "203", "movie", "Disliked", watched=True, feedback="dislike", tmdb_id="203")
    assert clear_flagged_bucket(db, 42, "disliked") == 1


def test_clear_everything(db):
    _seed_user_state(db)
    result = clear_everything(db, 42)

    assert result["chat"]["messages"] == 2
    assert result["flagged"]["requested"] == 1
    assert result["flagged"]["feedback"] == 4
    assert db.get_chat_messages(42) == []
    assert db.get_user_feedback(42) == []
    assert db.get_recent_media_requests(user_id=42) == []
    assert db.get_recent_recommendations(42, 3600) == []


async def _exercise_messenger_probe():
    bot = SimpleNamespace(
        copy_message=AsyncMock(
            side_effect=BadRequest("Message to copy not found"),
        ),
        delete_message=AsyncMock(),
    )
    assert await messenger_history_missing(bot, chat_id=1, message_id=9) is True
    bot.delete_message.assert_not_awaited()

    copied = SimpleNamespace(message_id=99)
    bot.copy_message = AsyncMock(return_value=copied)
    assert await messenger_history_missing(bot, chat_id=1, message_id=9) is False
    bot.delete_message.assert_awaited_once_with(chat_id=1, message_id=99)


def test_messenger_history_missing_probe():
    asyncio.run(_exercise_messenger_probe())


async def _exercise_sync_if_messenger_cleared(db):
    user_id = 42
    db.add_chat_message(user_id, chat_id=user_id, role="user", text="hi", message_id=10)
    db.record_recent_recommendations(
        user_id,
        [RecommendationItem(title="Recent", original_title="Recent", year=2020, overview="o", tmdb_id=1)],
    )

    bot_missing = SimpleNamespace(
        copy_message=AsyncMock(side_effect=BadRequest("Message to copy not found")),
        delete_message=AsyncMock(),
    )
    assert await sync_if_messenger_cleared(db, bot_missing, user_id) is True
    assert db.get_chat_messages(user_id) == []
    assert db.get_recent_recommendations(user_id, 3600) == []

    # Empty Repertuarr transcript → no wipe / no sync ack.
    assert await sync_if_messenger_cleared(db, bot_missing, user_id) is False

    db.add_chat_message(user_id, chat_id=user_id, role="user", text="again", message_id=20)
    bot_ok = SimpleNamespace(
        copy_message=AsyncMock(return_value=SimpleNamespace(message_id=21)),
        delete_message=AsyncMock(),
    )
    assert await sync_if_messenger_cleared(db, bot_ok, user_id) is False
    assert len(db.get_chat_messages(user_id)) == 1


def test_sync_if_messenger_cleared():
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmp:
        db = Database(db_path=str(Path(tmp) / "sync.db"))
        asyncio.run(_exercise_sync_if_messenger_cleared(db))


async def _exercise_admin_clear_routes(tmp_path):
    db = Database(db_path=str(tmp_path / "admin.db"))
    _seed_user_state(db, user_id=7)

    bot = SimpleNamespace(send_message=AsyncMock())
    bot_app = SimpleNamespace(bot=bot)
    users_config = [{
        "name": "Test",
        "messenger": {"messenger_name": "telegram", "user_id": 7},
        "preferences": {"language": "en", "bot_style": "default"},
    }]

    app = web.Application()
    register_admin_clear_routes(app, db, users_config, "telegram", bot_app)

    server = TestServer(app)
    client = TestClient(server)
    await client.start_server()
    try:
        chat_res = await client.post("/admin/api/users/7/clear-chat")
        assert chat_res.status == 200
        chat_body = await chat_res.json()
        assert chat_body["ok"] is True
        assert chat_body["cleared"]["messages"] == 2
        assert chat_body["notified"] is True
        bot.send_message.assert_awaited()
        assert "Clear history" in bot.send_message.await_args.kwargs["text"]

        # clear-chat leaves requested/feedback; wipe requested bucket next.
        flags_res = await client.post(
            "/admin/api/users/7/clear-flags",
            json={"bucket": "requested"},
        )
        assert flags_res.status == 200
        assert (await flags_res.json())["removed"] == 1
        assert db.get_recent_media_requests(user_id=7) == []

        everything_res = await client.post("/admin/api/users/7/clear-everything")
        assert everything_res.status == 200
        body = await everything_res.json()
        assert body["ok"] is True
        assert db.get_user_feedback(7) == []

        bad = await client.post(
            "/admin/api/users/7/clear-flags",
            json={"bucket": "nope"},
        )
        assert bad.status == 400
    finally:
        await client.close()


def test_admin_clear_routes(tmp_path):
    asyncio.run(_exercise_admin_clear_routes(tmp_path))
