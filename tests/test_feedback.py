"""Tests for normalized feedback storage and recommendation exclusions."""

import sqlite3

from bot.database import Database


def test_legacy_feedback_schema_migrates_to_normalized_columns(tmp_path):
    db_path = tmp_path / "legacy.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE user_content_feedback (
            user_id INTEGER NOT NULL,
            content_id TEXT NOT NULL,
            content_type TEXT NOT NULL,
            title TEXT,
            feedback_type TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, content_id, feedback_type)
        )
    """)
    cursor.executemany("""
        INSERT INTO user_content_feedback
            (user_id, content_id, content_type, title, feedback_type, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, [
        (1, "101", "movie", "Watched Movie", "watched", "2026-01-01T10:00:00"),
        (1, "102", "movie", "Bad Movie", "disliked", "2026-01-01T11:00:00"),
        (1, "103", "movie", "Ignored Movie", "ignored", "2026-01-01T12:00:00"),
        (1, "0", "movie", "No ID Movie", "disliked", "2026-01-01T13:00:00"),
    ])
    conn.commit()
    conn.close()

    db = Database(db_path=str(db_path))

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(user_content_feedback)")
    columns = {row[1] for row in cursor.fetchall()}
    conn.close()

    assert "feedback_type" not in columns
    assert {"watched", "feedback", "excluded"}.issubset(columns)
    assert db.get_content_feedback_state(1, "101")["watched"] is True
    assert db.get_content_feedback_state(1, "102")["feedback"] == "dislike"
    assert db.get_content_feedback_state(1, "103")["excluded"] is True
    no_id_key = db.normalize_content_id("movie", "0", "No ID Movie")
    assert db.get_content_feedback_state(1, no_id_key)["feedback"] == "dislike"


def test_feedback_toggle_semantics(tmp_path):
    db = Database(db_path=str(tmp_path / "test.db"))

    state = db.toggle_feedback_state(1, "101", "movie", "Example", "like", tmdb_id="101")
    assert state["watched"] is True
    assert state["feedback"] == "like"
    assert state["excluded"] is False

    state = db.toggle_feedback_state(1, "101", "movie", "Example", "like", tmdb_id="101")
    assert state["watched"] is False
    assert state["feedback"] is None

    state = db.toggle_feedback_state(1, "101", "movie", "Example", "watched", tmdb_id="101")
    assert state["watched"] is True
    assert state["feedback"] is None

    state = db.toggle_feedback_state(1, "101", "movie", "Example", "dislike", tmdb_id="101")
    assert state["watched"] is True
    assert state["feedback"] == "dislike"

    state = db.toggle_feedback_state(1, "101", "movie", "Example", "ignore", tmdb_id="101")
    assert state["watched"] is True
    assert state["feedback"] == "dislike"
    assert state["excluded"] is True


def test_feedback_helpers_use_separate_columns(tmp_path):
    db = Database(db_path=str(tmp_path / "test.db"))
    db.set_feedback_state(1, "101", "movie", "Watched", watched=True, tmdb_id="101")
    db.set_feedback_state(1, "102", "movie", "Liked", watched=True, feedback="like", tmdb_id="102")
    db.set_feedback_state(1, "103", "movie", "Disliked", watched=True, feedback="dislike", tmdb_id="103")
    db.set_feedback_state(1, "104", "movie", "Ignored", excluded=True, tmdb_id="104")

    assert set(db.get_feedback_titles(1, "watched")) == {"Watched", "Liked", "Disliked"}
    assert db.get_feedback_titles(1, "disliked") == ["Disliked"]
    assert db.get_excluded_tmdb_ids(1) == {"101", "102", "103", "104"}
    assert db.get_excluded_titles(1) == {"watched", "liked", "disliked", "ignored"}

    library = {row["title"]: row for row in db.get_user_media_library(1)}
    assert library["Watched"]["watched"] == 1
    assert library["Liked"]["feedback"] == "like"
    assert library["Ignored"]["excluded"] == 1
