"""Tests for download failure detection across request storage, webhooks, and monitoring."""

import asyncio
import socket
import sqlite3
from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from aiohttp import ClientSession

from bot.database import Database
from bot.download_monitor import inspect_download_request
from bot import webhook as webhook_mod
from bot.webhook import start_webhook_server


def _response(payload):
    response = MagicMock()
    response.status_code = 200
    response.text = "{}"
    response.json.return_value = payload
    response.raise_for_status = MagicMock()
    return response


def _free_port() -> int:
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


def _set_created_at(db_path, request_id: int, age: timedelta):
    created_at = datetime.now() - age
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE media_requests SET created_at = ? WHERE id = ?",
        (created_at.isoformat(timespec="seconds"), request_id),
    )
    conn.commit()
    conn.close()


def test_media_request_lifecycle_helpers(tmp_path):
    db = Database(db_path=str(tmp_path / "test.db"))

    request_id = db.add_media_request(
        telegram_id=100,
        title="Example Movie",
        media_type="movie",
        tmdb_id="123",
        chat_id=10,
        message_id=20,
        arr_service="radarr",
        arr_instance="radarr-main",
        arr_id=42,
    )

    request = db.get_media_request(request_id)
    assert request["status"] == "pending"
    assert request["arr_service"] == "radarr"
    assert request["arr_id"] == 42

    assert db.mark_request_grabbed(request_id, download_id="abc") is True
    request = db.get_media_request(request_id)
    assert request["status"] == "grabbed"
    assert request["download_id"] == "abc"
    assert db.mark_request_grabbed(request_id, download_id="abc") is False

    assert db.mark_request_queued_notified(request_id) is True
    request = db.get_media_request(request_id)
    assert request["queued_notified_at"] is not None
    assert db.mark_request_queued_notified(request_id) is False

    active = db.find_active_requests(arr_service="radarr", arr_id=42, media_type="movie")
    assert [row["id"] for row in active] == [request_id]

    assert db.mark_request_failed(
        request_id,
        reason="manual_interaction_required",
        detail="Import blocked",
        status="failed",
    ) is True
    request = db.get_media_request(request_id)
    assert request["status"] == "failed"
    assert request["failure_reason"] == "manual_interaction_required"
    assert db.mark_request_failed(request_id, reason="again") is False


async def _exercise_webhook_events(tmp_path):
    db = Database(db_path=str(tmp_path / "webhook.db"))
    bot_app = SimpleNamespace(bot=SimpleNamespace(send_message=AsyncMock()))
    users = [{
        "messenger": {"messenger_name": "telegram-main", "user_id": 100},
        "preferences": {"language": "en", "bot_style": "default"},
    }]
    port = _free_port()
    with patch.object(webhook_mod, "LISTEN_PORT", port):
        runner = await start_webhook_server(
            config={},
            db=db,
            media_server_client=None,
            bot_app=bot_app,
            users_config=users,
            messenger_name="telegram-main",
        )

    try:
        request_id = db.add_media_request(
            telegram_id=100,
            title="Example Movie",
            media_type="movie",
            tmdb_id="123",
            arr_service="radarr",
            arr_instance="radarr-main",
            arr_id=42,
        )
        async with ClientSession() as session:
            grab_payload = {
                "eventType": "Grab",
                "movie": {"id": 42, "title": "Example Movie", "tmdbId": 123},
                "downloadId": "download-1",
            }
            response = await session.post(f"http://127.0.0.1:{port}/webhook/radarr", json=grab_payload)
            assert response.status == 200

            request = db.get_media_request(request_id)
            assert request["status"] == "grabbed"
            assert request["download_id"] == "download-1"
            assert request["queued_notified_at"] is not None
            assert bot_app.bot.send_message.await_count == 2
            queued_call = bot_app.bot.send_message.await_args_list[0]
            started_call = bot_app.bot.send_message.await_args_list[1]
            assert queued_call.kwargs["chat_id"] == 100
            assert "queued" in queued_call.kwargs["text"].lower()
            assert started_call.kwargs["chat_id"] == 100
            assert "started downloading" in started_call.kwargs["text"]

            fail_payload = {
                "eventType": "ManualInteractionRequired",
                "movie": {"id": 42, "title": "Example Movie", "tmdbId": 123},
                "downloadId": "download-1",
                "release": {"releaseTitle": "Example.Movie.2026.1080p"},
                "downloadClient": "qBittorrent",
            }
            response = await session.post(f"http://127.0.0.1:{port}/webhook/radarr", json=fail_payload)
            assert response.status == 200

        assert bot_app.bot.send_message.await_count == 3
        failed_call = bot_app.bot.send_message.await_args_list[2]
        assert "manual help" in failed_call.kwargs["text"]
        request = db.get_media_request(request_id)
        assert request["status"] == "failed"
        assert request["failure_reason"] == "manual_interaction_required"
        assert "Example.Movie.2026.1080p" in request["failure_detail"]
    finally:
        await runner.cleanup()


def test_webhook_grab_and_manual_interaction_required(tmp_path):
    asyncio.run(_exercise_webhook_events(tmp_path))


async def _exercise_monitor_no_candidates(tmp_path):
    db = Database(db_path=str(tmp_path / "monitor.db"))
    request_id = db.add_media_request(
        telegram_id=100,
        title="No Seeds Movie",
        media_type="movie",
        tmdb_id="555",
        arr_service="radarr",
        arr_instance="radarr-main",
        arr_id=55,
    )
    _set_created_at(db.db_path, request_id, timedelta(minutes=30))
    request = db.get_media_request(request_id)
    bot_app = SimpleNamespace(bot=SimpleNamespace(send_message=AsyncMock()))
    config = {
        "radarrs": {"radarr-main": {"url": "http://radarr.local", "key": "key"}},
        "download_monitor": {"no_grab_after_minutes": 1},
    }

    with patch("bot.download_monitor_arr.make_service_request", side_effect=[
        _response({"records": []}),
        _response([]),
    ]):
        await inspect_download_request(
            config,
            db,
            bot_app,
            request,
            {"language": "en", "bot_style": "default"},
            datetime.now(),
        )

    bot_app.bot.send_message.assert_awaited_once()
    request = db.get_media_request(request_id)
    assert request["status"] == "unavailable"
    assert request["failure_reason"] == "no_candidates"
    assert db.get_download_monitor_candidates() == []


def test_monitor_marks_no_candidates_unavailable_once(tmp_path):
    asyncio.run(_exercise_monitor_no_candidates(tmp_path))


async def _exercise_monitor_download_started(tmp_path):
    db = Database(db_path=str(tmp_path / "started.db"))
    request_id = db.add_media_request(
        telegram_id=100,
        title="Started Movie",
        media_type="movie",
        tmdb_id="888",
        arr_service="radarr",
        arr_instance="radarr-main",
        arr_id=88,
    )
    request = db.get_media_request(request_id)
    bot_app = SimpleNamespace(bot=SimpleNamespace(send_message=AsyncMock()))
    config = {
        "radarrs": {"radarr-main": {"url": "http://radarr.local", "key": "key"}},
    }
    queue_payload = {
        "records": [{
            "movieId": 88,
            "downloadId": "download-88",
            "trackedDownloadState": "downloading",
        }]
    }

    with patch("bot.download_monitor_arr.make_service_request", return_value=_response(queue_payload)):
        await inspect_download_request(
            config,
            db,
            bot_app,
            request,
            {"language": "en", "bot_style": "default"},
            datetime.now(),
        )

    assert bot_app.bot.send_message.await_count == 2
    queued_call = bot_app.bot.send_message.await_args_list[0]
    started_call = bot_app.bot.send_message.await_args_list[1]
    assert "Started Movie" in queued_call.kwargs["text"]
    assert "Started Movie" in started_call.kwargs["text"]
    assert "started downloading" in started_call.kwargs["text"]
    request = db.get_media_request(request_id)
    assert request["status"] == "grabbed"
    assert request["download_id"] == "download-88"
    assert request["queued_notified_at"] is not None


def test_monitor_sends_download_started_for_queue_record(tmp_path):
    asyncio.run(_exercise_monitor_download_started(tmp_path))


async def _exercise_monitor_stalled_warning_waits_for_threshold(tmp_path):
    db = Database(db_path=str(tmp_path / "stalled_wait.db"))
    request_id = db.add_media_request(
        telegram_id=100,
        title="Midnight Sun",
        media_type="movie",
        tmdb_id="419478",
        arr_service="radarr",
        arr_instance="radarr-main",
        arr_id=96,
    )
    _set_created_at(db.db_path, request_id, timedelta(minutes=30))
    request = db.get_media_request(request_id)
    bot_app = SimpleNamespace(bot=SimpleNamespace(send_message=AsyncMock()))
    config = {
        "radarrs": {"radarr-main": {"url": "http://radarr.local", "key": "key"}},
        "download_monitor": {"stalled_after_hours": 1},
    }
    queue_payload = {
        "records": [{
            "movieId": 96,
            "downloadId": "download-96",
            "trackedDownloadState": "downloading",
            "trackedDownloadStatus": "ok",
            "status": "warning",
            "errorMessage": "The download is stalled with no connections",
        }]
    }

    with patch("bot.download_monitor_arr.make_service_request", return_value=_response(queue_payload)):
        await inspect_download_request(
            config,
            db,
            bot_app,
            request,
            {"language": "en", "bot_style": "default"},
            datetime.now(),
        )

    bot_app.bot.send_message.assert_not_awaited()
    request = db.get_media_request(request_id)
    assert request["status"] == "pending"
    assert request["download_id"] is None
    assert request["last_checked_at"] is not None


def test_monitor_does_not_mark_stalled_warning_as_grabbed_before_threshold(tmp_path):
    asyncio.run(_exercise_monitor_stalled_warning_waits_for_threshold(tmp_path))


async def _exercise_monitor_stalled_warning_fails_after_threshold(tmp_path):
    db = Database(db_path=str(tmp_path / "stalled_fail.db"))
    request_id = db.add_media_request(
        telegram_id=100,
        title="Midnight Sun",
        media_type="movie",
        tmdb_id="419478",
        arr_service="radarr",
        arr_instance="radarr-main",
        arr_id=96,
    )
    _set_created_at(db.db_path, request_id, timedelta(hours=2))
    request = db.get_media_request(request_id)
    bot_app = SimpleNamespace(bot=SimpleNamespace(send_message=AsyncMock()))
    config = {
        "radarrs": {"radarr-main": {"url": "http://radarr.local", "key": "key"}},
        "download_monitor": {"stalled_after_hours": 1},
    }
    queue_payload = {
        "records": [{
            "movieId": 96,
            "downloadId": "download-96",
            "trackedDownloadState": "downloading",
            "trackedDownloadStatus": "ok",
            "status": "warning",
            "errorMessage": "The download is stalled with no connections",
        }]
    }

    with patch("bot.download_monitor_arr.make_service_request", return_value=_response(queue_payload)):
        await inspect_download_request(
            config,
            db,
            bot_app,
            request,
            {"language": "en", "bot_style": "default"},
            datetime.now(),
        )

    bot_app.bot.send_message.assert_awaited_once()
    request = db.get_media_request(request_id)
    assert request["status"] == "failed"
    assert request["failure_reason"] == "queue_blocked"
    assert request["failure_detail"] == "The download is stalled with no connections"


def test_monitor_marks_stalled_warning_failed_after_threshold(tmp_path):
    asyncio.run(_exercise_monitor_stalled_warning_fails_after_threshold(tmp_path))


async def _exercise_monitor_queue_blocked(tmp_path):
    db = Database(db_path=str(tmp_path / "blocked.db"))
    request_id = db.add_media_request(
        telegram_id=100,
        title="Blocked Show",
        media_type="series",
        tvdb_id="777",
        arr_service="sonarr",
        arr_instance="sonarr-main",
        arr_id=77,
    )
    db.mark_request_grabbed(request_id, download_id="download-77")
    _set_created_at(db.db_path, request_id, timedelta(hours=30))
    request = db.get_media_request(request_id)
    bot_app = SimpleNamespace(bot=SimpleNamespace(send_message=AsyncMock()))
    config = {
        "sonarrs": {"sonarr-main": {"url": "http://sonarr.local", "key": "key"}},
        "download_monitor": {"stalled_after_hours": 1},
    }
    queue_payload = {
        "records": [{
            "seriesId": 77,
            "downloadId": "download-77",
            "trackedDownloadState": "importBlocked",
            "statusMessages": [{"title": "Automatic import is not possible", "messages": []}],
        }]
    }

    with patch("bot.download_monitor_arr.make_service_request", return_value=_response(queue_payload)):
        await inspect_download_request(
            config,
            db,
            bot_app,
            request,
            {"language": "en", "bot_style": "default"},
            datetime.now(),
        )

    bot_app.bot.send_message.assert_awaited_once()
    request = db.get_media_request(request_id)
    assert request["status"] == "failed"
    assert request["failure_reason"] == "queue_blocked"
    assert "Automatic import is not possible" in request["failure_detail"]


def test_monitor_marks_queue_blocked_failed(tmp_path):
    asyncio.run(_exercise_monitor_queue_blocked(tmp_path))


def _media_server_mock(url=None):
    client = MagicMock()
    client.display_name = "Plex"
    client.search_item.return_value = url
    return client


async def _exercise_monitor_grabbed_found_on_media_server(tmp_path):
    db = Database(db_path=str(tmp_path / "ready.db"))
    request_id = db.add_media_request(
        telegram_id=100,
        title="Ready Movie",
        media_type="movie",
        tmdb_id="999",
        arr_service="radarr",
        arr_instance="radarr-main",
        arr_id=99,
    )
    db.mark_request_grabbed(request_id, download_id="download-99")
    request = db.get_media_request(request_id)
    bot_app = SimpleNamespace(bot=SimpleNamespace(send_message=AsyncMock()))
    config = {
        "radarrs": {"radarr-main": {"url": "http://radarr.local", "key": "key"}},
    }
    media_server = _media_server_mock(url="http://plex.local/web/Ready%20Movie")

    with patch("bot.download_monitor_arr.make_service_request", return_value=_response({"records": []})):
        await inspect_download_request(
            config,
            db,
            bot_app,
            request,
            {"language": "en", "bot_style": "default"},
            datetime.now(),
            media_server_client=media_server,
        )

    media_server.search_item.assert_called_once_with(
        "Ready Movie", "movie", tmdb_id="999", tvdb_id=None,
    )
    bot_app.bot.send_message.assert_awaited_once()
    assert "Ready Movie" in bot_app.bot.send_message.await_args.kwargs["text"]
    assert "Plex" in bot_app.bot.send_message.await_args.kwargs["text"]
    request = db.get_media_request(request_id)
    assert request["status"] == "notified"


def test_monitor_notifies_when_grabbed_found_on_media_server(tmp_path):
    asyncio.run(_exercise_monitor_grabbed_found_on_media_server(tmp_path))


async def _exercise_monitor_grabbed_missing_on_media_server(tmp_path):
    db = Database(db_path=str(tmp_path / "missing.db"))
    request_id = db.add_media_request(
        telegram_id=100,
        title="Missing Movie",
        media_type="movie",
        tmdb_id="1001",
        arr_service="radarr",
        arr_instance="radarr-main",
        arr_id=101,
    )
    db.mark_request_grabbed(request_id, download_id="download-101")
    request = db.get_media_request(request_id)
    bot_app = SimpleNamespace(bot=SimpleNamespace(send_message=AsyncMock()))
    config = {
        "radarrs": {"radarr-main": {"url": "http://radarr.local", "key": "key"}},
    }
    media_server = _media_server_mock(url=None)

    with patch("bot.download_monitor_arr.make_service_request", return_value=_response({"records": []})):
        await inspect_download_request(
            config,
            db,
            bot_app,
            request,
            {"language": "en", "bot_style": "default"},
            datetime.now(),
            media_server_client=media_server,
        )

    media_server.search_item.assert_called_once()
    bot_app.bot.send_message.assert_not_awaited()
    request = db.get_media_request(request_id)
    assert request["status"] == "grabbed"
    assert request["last_checked_at"] is not None


def test_monitor_keeps_grabbed_when_media_server_misses(tmp_path):
    asyncio.run(_exercise_monitor_grabbed_missing_on_media_server(tmp_path))


async def _exercise_monitor_grabbed_still_queued_skips_media_server(tmp_path):
    db = Database(db_path=str(tmp_path / "queued.db"))
    request_id = db.add_media_request(
        telegram_id=100,
        title="Queued Movie",
        media_type="movie",
        tmdb_id="1002",
        arr_service="radarr",
        arr_instance="radarr-main",
        arr_id=102,
    )
    db.mark_request_grabbed(request_id, download_id="download-102")
    request = db.get_media_request(request_id)
    bot_app = SimpleNamespace(bot=SimpleNamespace(send_message=AsyncMock()))
    config = {
        "radarrs": {"radarr-main": {"url": "http://radarr.local", "key": "key"}},
    }
    media_server = _media_server_mock(url="http://plex.local/should-not-matter")
    queue_payload = {
        "records": [{
            "movieId": 102,
            "downloadId": "download-102",
            "trackedDownloadState": "downloading",
        }]
    }

    with patch("bot.download_monitor_arr.make_service_request", return_value=_response(queue_payload)):
        await inspect_download_request(
            config,
            db,
            bot_app,
            request,
            {"language": "en", "bot_style": "default"},
            datetime.now(),
            media_server_client=media_server,
        )

    media_server.search_item.assert_not_called()
    bot_app.bot.send_message.assert_not_awaited()
    request = db.get_media_request(request_id)
    assert request["status"] == "grabbed"


def test_monitor_skips_media_server_while_still_queued(tmp_path):
    asyncio.run(_exercise_monitor_grabbed_still_queued_skips_media_server(tmp_path))


async def _exercise_monitor_grabbed_no_media_server_client(tmp_path):
    db = Database(db_path=str(tmp_path / "no_client.db"))
    request_id = db.add_media_request(
        telegram_id=100,
        title="No Client Movie",
        media_type="movie",
        tmdb_id="1003",
        arr_service="radarr",
        arr_instance="radarr-main",
        arr_id=103,
    )
    db.mark_request_grabbed(request_id, download_id="download-103")
    request = db.get_media_request(request_id)
    bot_app = SimpleNamespace(bot=SimpleNamespace(send_message=AsyncMock()))
    config = {
        "radarrs": {"radarr-main": {"url": "http://radarr.local", "key": "key"}},
    }

    with patch("bot.download_monitor_arr.make_service_request", return_value=_response({"records": []})) as mock_req:
        await inspect_download_request(
            config,
            db,
            bot_app,
            request,
            {"language": "en", "bot_style": "default"},
            datetime.now(),
            media_server_client=None,
        )

    mock_req.assert_called_once()
    bot_app.bot.send_message.assert_not_awaited()
    request = db.get_media_request(request_id)
    assert request["status"] == "grabbed"
    assert request["last_checked_at"] is not None


def test_monitor_grabbed_without_media_server_only_marks_checked(tmp_path):
    asyncio.run(_exercise_monitor_grabbed_no_media_server_client(tmp_path))
