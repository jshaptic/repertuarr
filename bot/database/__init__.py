"""
SQLite persistence layer for user feedback, media requests, and admin activity logs.

The Database class owns schema initialization and CRUD for feedback/requests.
Session and log methods live in bot.database.logs.LogMixin.
"""

import sqlite3
import logging
from datetime import datetime
from typing import List, Optional, Literal
import os

from bot.database.logs import LogMixin
from bot.database.chat import ChatMixin

logger = logging.getLogger(__name__)

FeedbackType = Literal['watched', 'disliked', 'ignored']


class Database(LogMixin, ChatMixin):
    def __init__(self, db_path: str = "data/media_bot.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_content_feedback (
                user_id INTEGER NOT NULL,
                content_id TEXT NOT NULL,
                content_type TEXT NOT NULL,
                title TEXT,
                feedback_type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, content_id, feedback_type)
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_feedback
            ON user_content_feedback(user_id, feedback_type)
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS media_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                media_type TEXT NOT NULL,
                tmdb_id TEXT,
                tvdb_id TEXT,
                chat_id INTEGER,
                message_id INTEGER,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        for stmt in (
            "ALTER TABLE media_requests ADD COLUMN chat_id INTEGER",
            "ALTER TABLE media_requests ADD COLUMN message_id INTEGER",
            "ALTER TABLE user_content_feedback ADD COLUMN tmdb_id TEXT",
            "ALTER TABLE user_content_feedback ADD COLUMN tvdb_id TEXT",
        ):
            try:
                cursor.execute(stmt)
            except sqlite3.OperationalError:
                pass

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_media_requests_status
            ON media_requests(status)
        """)

        self._init_log_schema(cursor)
        self._init_chat_schema(cursor)

        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {self.db_path}")

    # ── Content feedback methods ──────────────────────────────────────

    def add_feedback(
        self,
        user_id: int,
        content_id: str,
        content_type: str,
        title: str,
        feedback_type: FeedbackType,
        tmdb_id: str = None,
        tvdb_id: str = None
    ):
        """Add or update user feedback for content"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO user_content_feedback
            (user_id, content_id, content_type, title, feedback_type, tmdb_id, tvdb_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, content_id, content_type, title, feedback_type, tmdb_id, tvdb_id, datetime.now()))

        conn.commit()
        conn.close()
        logger.info(f"Added {feedback_type} feedback for user {user_id}, content {content_id}")

    def get_user_feedback(
        self,
        user_id: int,
        feedback_type: Optional[FeedbackType] = None
    ) -> List[dict]:
        """Get all feedback for a user, optionally filtered by type"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if feedback_type:
            cursor.execute("""
                SELECT * FROM user_content_feedback
                WHERE user_id = ? AND feedback_type = ?
            """, (user_id, feedback_type))
        else:
            cursor.execute("""
                SELECT * FROM user_content_feedback
                WHERE user_id = ?
            """, (user_id,))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_excluded_content_ids(self, user_id: int) -> set:
        """Get set of content IDs that should be excluded from recommendations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT DISTINCT content_id FROM user_content_feedback
            WHERE user_id = ? AND feedback_type IN ('watched', 'disliked', 'ignored', 'dislike', 'ignore')
        """, (user_id,))

        rows = cursor.fetchall()
        conn.close()

        return {row[0] for row in rows}

    def get_excluded_titles(self, user_id: int) -> set:
        """Get set of titles that should be excluded from recommendations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT DISTINCT title FROM user_content_feedback
            WHERE user_id = ? AND feedback_type IN ('watched', 'disliked', 'ignored', 'dislike', 'ignore')
        """, (user_id,))

        rows = cursor.fetchall()
        conn.close()

        return {row[0].lower() for row in rows if row[0]}

    def get_excluded_tmdb_ids(self, user_id: int) -> set:
        """Get set of TMDB IDs that should be excluded from TMDB candidate pool"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT DISTINCT tmdb_id FROM user_content_feedback
            WHERE user_id = ?
              AND tmdb_id IS NOT NULL
              AND feedback_type IN ('watched', 'disliked', 'ignored', 'dislike', 'ignore')
        """, (user_id,))

        rows = cursor.fetchall()
        conn.close()

        return {row[0] for row in rows if row[0]}

    def get_feedback_titles(self, user_id: int, feedback_type: FeedbackType) -> list:
        """Get list of titles for a specific feedback type (for prompt context)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT title FROM user_content_feedback
            WHERE user_id = ? AND feedback_type = ?
            ORDER BY created_at DESC
        """, (user_id, feedback_type))

        rows = cursor.fetchall()
        conn.close()

        return [row[0] for row in rows if row[0]]

    def has_feedback(
        self,
        user_id: int,
        content_id: str,
        feedback_type: FeedbackType
    ) -> bool:
        """Check if user has already given specific feedback for content"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 1 FROM user_content_feedback
            WHERE user_id = ? AND content_id = ? AND feedback_type = ?
        """, (user_id, content_id, feedback_type))

        result = cursor.fetchone()
        conn.close()

        return result is not None

    # ── Media request methods ─────────────────────────────────────────

    def add_media_request(
        self,
        telegram_id: int,
        title: str,
        media_type: str,
        tmdb_id: str = None,
        tvdb_id: str = None,
        chat_id: int = None,
        message_id: int = None
    ):
        """Record that a user requested a media item via the bot"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO media_requests (telegram_id, title, media_type, tmdb_id, tvdb_id, chat_id, message_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (telegram_id, title, media_type, tmdb_id, tvdb_id, chat_id, message_id))

        conn.commit()
        conn.close()
        logger.info(f"Recorded media request: user={telegram_id}, title='{title}', type={media_type}")

    def find_pending_requests(
        self,
        title: str = None,
        tmdb_id: str = None,
        tvdb_id: str = None
    ) -> List[dict]:
        """Find pending media requests matching downloaded media by ID or title"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        conditions = ["status = 'pending'"]
        params = []

        id_conditions = []
        if tmdb_id:
            id_conditions.append("tmdb_id = ?")
            params.append(str(tmdb_id))
        if tvdb_id:
            id_conditions.append("tvdb_id = ?")
            params.append(str(tvdb_id))
        if title:
            id_conditions.append("LOWER(title) = LOWER(?)")
            params.append(title)

        if not id_conditions:
            conn.close()
            return []

        conditions.append(f"({' OR '.join(id_conditions)})")

        query = f"SELECT * FROM media_requests WHERE {' AND '.join(conditions)}"
        cursor.execute(query, params)

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def mark_request_notified(self, request_id: int):
        """Mark a media request as notified after sending the download notification"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE media_requests SET status = 'notified' WHERE id = ?
        """, (request_id,))

        conn.commit()
        conn.close()
        logger.info(f"Marked media request {request_id} as notified")

    def get_recent_media_requests(self, limit: int = 50, user_id: Optional[int] = None) -> List[dict]:
        """Get recent media requests for the admin UI"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if user_id:
            cursor.execute("""
                SELECT * FROM media_requests
                WHERE telegram_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (user_id, limit))
        else:
            cursor.execute("""
                SELECT * FROM media_requests
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_recent_feedback(self, limit: int = 50, user_id: Optional[int] = None) -> List[dict]:
        """Get recent user feedback for the admin UI"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if user_id:
            cursor.execute("""
                SELECT * FROM user_content_feedback
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (user_id, limit))
        else:
            cursor.execute("""
                SELECT * FROM user_content_feedback
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_user_media_library(self, user_id: int, limit: int = 200) -> List[dict]:
        """Get a unified media library view combining requests and feedback for the admin UI."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                f.title,
                f.content_type as media_type,
                r.status as request_status,
                f.feedback_type,
                COALESCE(f.tmdb_id, r.tmdb_id) as tmdb_id,
                COALESCE(f.tvdb_id, r.tvdb_id) as tvdb_id,
                f.created_at
            FROM user_content_feedback f
            LEFT JOIN media_requests r
                ON r.telegram_id = ? AND LOWER(f.title) = LOWER(r.title)
            WHERE f.user_id = ?

            UNION ALL

            SELECT
                r2.title,
                r2.media_type,
                r2.status as request_status,
                NULL as feedback_type,
                r2.tmdb_id,
                r2.tvdb_id,
                r2.created_at
            FROM media_requests r2
            WHERE r2.telegram_id = ?
              AND NOT EXISTS (
                  SELECT 1 FROM user_content_feedback f2
                  WHERE f2.user_id = ? AND LOWER(f2.title) = LOWER(r2.title)
              )

            ORDER BY created_at DESC
            LIMIT ?
        """, (user_id, user_id, user_id, user_id, limit))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_users_summary(self) -> List[dict]:
        """Get unique users and their stats"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT user_id,
                   (SELECT COUNT(*) FROM media_requests WHERE telegram_id = u.user_id) as requests_count,
                   (SELECT COUNT(*) FROM user_content_feedback WHERE user_id = u.user_id) as feedback_count,
                   (SELECT COUNT(*) FROM llm_logs WHERE user_id = u.user_id) as llm_count,
                   (SELECT COALESCE(SUM(cost_usd), 0) FROM llm_logs WHERE user_id = u.user_id) as llm_cost_usd,
                   (SELECT MAX(created_at) FROM (
                       SELECT created_at FROM media_requests WHERE telegram_id = u.user_id
                       UNION ALL
                       SELECT created_at FROM user_content_feedback WHERE user_id = u.user_id
                       UNION ALL
                       SELECT created_at FROM llm_logs WHERE user_id = u.user_id
                   )) as last_active
            FROM (
                SELECT telegram_id as user_id FROM media_requests
                UNION
                SELECT user_id FROM user_content_feedback
                UNION
                SELECT user_id FROM llm_logs
            ) u
            ORDER BY last_active DESC
        """)

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]
