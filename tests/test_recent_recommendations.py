"""Unit tests for recent recommendation cooldown storage."""

import sqlite3
from datetime import datetime, timedelta

import pytest

from bot.database import Database
from bot.models import RecommendationItem


def _make_item(title: str, original_title: str = None, tmdb_id: int = None) -> RecommendationItem:
    return RecommendationItem(
        title=title,
        original_title=original_title or title,
        year=2020,
        overview="Overview",
        tmdb_id=tmdb_id,
    )


@pytest.fixture
def db(tmp_path):
    return Database(db_path=str(tmp_path / "test.db"))


def test_record_and_read_back_within_ttl(db):
    user_id = 42
    items = [
        _make_item("Localized One", "Original One", 101),
        _make_item("Localized Two", "Original Two", 102),
    ]
    db.record_recent_recommendations(user_id, items)

    ttl = 3600
    assert db.get_recent_excluded_tmdb_ids(user_id, ttl) == {"101", "102"}
    titles = db.get_recent_excluded_titles(user_id, ttl)
    assert "localized one" in titles
    assert "original one" in titles
    assert "localized two" in titles
    assert "original two" in titles


def test_items_outside_ttl_are_not_returned(db):
    user_id = 7
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    old_time = (datetime.now() - timedelta(hours=100)).isoformat()
    cursor.execute("""
        INSERT INTO recent_recommendations
            (user_id, title, original_title, tmdb_id, recommended_at)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, "Old Title", "Old Original", "999", old_time))
    conn.commit()
    conn.close()

    ttl = 3600
    assert db.get_recent_excluded_tmdb_ids(user_id, ttl) == set()
    assert db.get_recent_excluded_titles(user_id, ttl) == set()


def test_re_record_same_tmdb_id_stays_excluded(db):
    user_id = 5
    db.record_recent_recommendations(user_id, [_make_item("First", "First", 55)])
    db.record_recent_recommendations(user_id, [_make_item("First Again", "First", 55)])

    ttl = 3600
    assert db.get_recent_excluded_tmdb_ids(user_id, ttl) == {"55"}
    titles = db.get_recent_excluded_titles(user_id, ttl)
    assert "first" in titles
    assert "first again" in titles


def test_clear_recent_recommendations(db):
    user_id = 99
    db.record_recent_recommendations(user_id, [_make_item("A", tmdb_id=1)])
    db.record_recent_recommendations(user_id, [_make_item("B", tmdb_id=2)])

    removed = db.clear_recent_recommendations(user_id)
    assert removed == 2
    assert db.get_recent_excluded_tmdb_ids(user_id, 3600) == set()
    assert db.get_recent_excluded_titles(user_id, 3600) == set()


def test_get_recent_recommendations_lists_active_items(db):
    user_id = 11
    db.record_recent_recommendations(
        user_id,
        [_make_item("Localized", "Original", 321)],
    )

    rows = db.get_recent_recommendations(user_id, 3600)
    assert len(rows) == 1
    row = rows[0]
    assert row["title"] == "Localized"
    assert row["original_title"] == "Original"
    assert row["tmdb_id"] == "321"
    assert row["expires_at"] is not None


def test_get_recent_recommendations_excludes_expired(db):
    user_id = 12
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    old_time = (datetime.now() - timedelta(hours=100)).isoformat()
    cursor.execute("""
        INSERT INTO recent_recommendations
            (user_id, title, original_title, tmdb_id, recommended_at)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, "Old", "Old", "777", old_time))
    conn.commit()
    conn.close()

    assert db.get_recent_recommendations(user_id, 3600) == []


def test_record_skips_items_without_title(db):
    user_id = 1
    db.record_recent_recommendations(user_id, [{"overview": "no title"}])

    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM recent_recommendations WHERE user_id = ?", (user_id,))
    count = cursor.fetchone()[0]
    conn.close()
    assert count == 0


def test_purge_on_read_removes_expired_rows(db):
    user_id = 3
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    old_time = (datetime.now() - timedelta(hours=200)).isoformat()
    cursor.execute("""
        INSERT INTO recent_recommendations
            (user_id, title, original_title, tmdb_id, recommended_at)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, "Expired", "Expired", "888", old_time))
    conn.commit()
    conn.close()

    db.get_recent_excluded_tmdb_ids(user_id, 3600)

    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM recent_recommendations WHERE user_id = ?", (user_id,))
    count = cursor.fetchone()[0]
    conn.close()
    assert count == 0
