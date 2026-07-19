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
from bot.database.recommendations import RecentRecommendationsMixin
from bot.database.service_logs import ServiceLogMixin

logger = logging.getLogger(__name__)

FeedbackType = Literal['watched', 'liked', 'disliked', 'ignored', 'like', 'dislike', 'ignore']
FeedbackValue = Literal['like', 'dislike']


class Database(LogMixin, ChatMixin, RecentRecommendationsMixin, ServiceLogMixin):
    def __init__(self, db_path: str = "data/media_bot.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        self._init_feedback_schema(cursor)

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
                arr_service TEXT,
                arr_instance TEXT,
                arr_id INTEGER,
                download_id TEXT,
                last_checked_at TIMESTAMP,
                failure_reason TEXT,
                failure_detail TEXT,
                failed_at TIMESTAMP,
                notified_at TIMESTAMP,
                queued_notified_at TIMESTAMP,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        for stmt in (
            "ALTER TABLE media_requests ADD COLUMN chat_id INTEGER",
            "ALTER TABLE media_requests ADD COLUMN message_id INTEGER",
            "ALTER TABLE media_requests ADD COLUMN arr_service TEXT",
            "ALTER TABLE media_requests ADD COLUMN arr_instance TEXT",
            "ALTER TABLE media_requests ADD COLUMN arr_id INTEGER",
            "ALTER TABLE media_requests ADD COLUMN download_id TEXT",
            "ALTER TABLE media_requests ADD COLUMN last_checked_at TIMESTAMP",
            "ALTER TABLE media_requests ADD COLUMN failure_reason TEXT",
            "ALTER TABLE media_requests ADD COLUMN failure_detail TEXT",
            "ALTER TABLE media_requests ADD COLUMN failed_at TIMESTAMP",
            "ALTER TABLE media_requests ADD COLUMN notified_at TIMESTAMP",
            "ALTER TABLE media_requests ADD COLUMN queued_notified_at TIMESTAMP",
        ):
            try:
                cursor.execute(stmt)
            except sqlite3.OperationalError:
                pass

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_media_requests_status
            ON media_requests(status)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_media_requests_arr
            ON media_requests(arr_service, arr_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_media_requests_download
            ON media_requests(download_id)
        """)

        self._init_log_schema(cursor)
        self._init_service_log_schema(cursor)
        self._init_chat_schema(cursor)
        self._init_recommendations_schema(cursor)

        conn.commit()
        conn.close()
        logger.info(f"Database initialized at {self.db_path}")

    # ── Content feedback methods ──────────────────────────────────────

    def _create_feedback_table(self, cursor: sqlite3.Cursor) -> None:
        """Create the normalized feedback table."""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_content_feedback (
                user_id INTEGER NOT NULL,
                content_id TEXT NOT NULL,
                content_type TEXT NOT NULL,
                title TEXT,
                watched INTEGER NOT NULL DEFAULT 0,
                feedback TEXT CHECK (feedback IN ('like', 'dislike') OR feedback IS NULL),
                excluded INTEGER NOT NULL DEFAULT 0,
                tmdb_id TEXT,
                tvdb_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, content_id)
            )
        """)

    def _init_feedback_schema(self, cursor: sqlite3.Cursor) -> None:
        """Create or migrate user feedback to watched/feedback/excluded columns."""
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type = 'table' AND name = 'user_content_feedback'
        """)
        table_exists = cursor.fetchone() is not None

        if not table_exists:
            self._create_feedback_table(cursor)
        else:
            cursor.execute("PRAGMA table_info(user_content_feedback)")
            columns = {row[1] for row in cursor.fetchall()}
            if 'feedback_type' in columns:
                self._migrate_legacy_feedback_schema(cursor)
            else:
                for stmt in (
                    "ALTER TABLE user_content_feedback ADD COLUMN watched INTEGER NOT NULL DEFAULT 0",
                    "ALTER TABLE user_content_feedback ADD COLUMN feedback TEXT",
                    "ALTER TABLE user_content_feedback ADD COLUMN excluded INTEGER NOT NULL DEFAULT 0",
                    "ALTER TABLE user_content_feedback ADD COLUMN tmdb_id TEXT",
                    "ALTER TABLE user_content_feedback ADD COLUMN tvdb_id TEXT",
                    "ALTER TABLE user_content_feedback ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                ):
                    try:
                        cursor.execute(stmt)
                    except sqlite3.OperationalError:
                        pass

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_feedback
            ON user_content_feedback(user_id, watched, feedback, excluded)
        """)

    def _migrate_legacy_feedback_schema(self, cursor: sqlite3.Cursor) -> None:
        """Fold legacy feedback_type rows into one row per content item."""
        logger.info("Migrating user_content_feedback to normalized feedback columns")
        cursor.execute("ALTER TABLE user_content_feedback RENAME TO user_content_feedback_legacy")
        self._create_feedback_table(cursor)

        cursor.execute("SELECT * FROM user_content_feedback_legacy")
        column_names = [description[0] for description in cursor.description]
        rows = [dict(zip(column_names, row)) for row in cursor.fetchall()]
        migrated = {}

        for row in rows:
            content_id = self.normalize_content_id(
                row['content_type'],
                row['content_id'],
                row.get('title'),
            )
            key = (row['user_id'], content_id)
            state = migrated.setdefault(
                key,
                {
                    'user_id': row['user_id'],
                    'content_id': content_id,
                    'content_type': row['content_type'],
                    'title': row.get('title'),
                    'watched': 0,
                    'feedback': None,
                    'excluded': 0,
                    'tmdb_id': row.get('tmdb_id'),
                    'tvdb_id': row.get('tvdb_id'),
                    'created_at': row.get('created_at'),
                    'updated_at': row.get('created_at'),
                },
            )

            for field in ('title', 'tmdb_id', 'tvdb_id'):
                if not state.get(field) and row.get(field):
                    state[field] = row[field]
            if row.get('created_at') and (
                not state.get('created_at') or str(row['created_at']) < str(state['created_at'])
            ):
                state['created_at'] = row['created_at']
            if row.get('created_at') and (
                not state.get('updated_at') or str(row['created_at']) > str(state['updated_at'])
            ):
                state['updated_at'] = row['created_at']

            feedback_type = (row.get('feedback_type') or '').lower()
            if feedback_type == 'watched':
                state['watched'] = 1
            elif feedback_type in ('liked', 'like'):
                state['watched'] = 1
                state['feedback'] = 'like'
            elif feedback_type in ('disliked', 'dislike'):
                state['watched'] = 1
                state['feedback'] = 'dislike'
            elif feedback_type in ('ignored', 'ignore'):
                state['excluded'] = 1

        cursor.executemany("""
            INSERT INTO user_content_feedback
                (user_id, content_id, content_type, title, watched, feedback, excluded,
                 tmdb_id, tvdb_id, created_at, updated_at)
            VALUES
                (:user_id, :content_id, :content_type, :title, :watched, :feedback, :excluded,
                 :tmdb_id, :tvdb_id, :created_at, :updated_at)
        """, list(migrated.values()))
        cursor.execute("DROP TABLE user_content_feedback_legacy")

    @staticmethod
    def normalize_content_id(content_type: str, content_id: str, title: str) -> str:
        """Use provider IDs when available, otherwise derive a stable title key."""
        raw_id = str(content_id or '').strip()
        if raw_id and raw_id != '0':
            return raw_id
        title_key = " ".join(str(title or 'unknown').split()).lower()
        return f"{content_type}:title:{title_key}"

    @staticmethod
    def _feedback_where_clause(feedback_type: FeedbackType) -> str:
        """Translate legacy feedback filters into normalized column predicates."""
        normalized = feedback_type.lower()
        if normalized == 'watched':
            return "watched = 1"
        if normalized in ('liked', 'like'):
            return "feedback = 'like'"
        if normalized in ('disliked', 'dislike'):
            return "feedback = 'dislike'"
        if normalized in ('ignored', 'ignore'):
            return "excluded = 1"
        raise ValueError(f"Unsupported feedback type: {feedback_type}")

    @staticmethod
    def _normalize_feedback_value(feedback: Optional[str]) -> Optional[FeedbackValue]:
        """Normalize public feedback aliases to the stored like/dislike values."""
        if feedback is None:
            return None
        normalized = feedback.lower()
        if normalized in ('liked', 'like'):
            return 'like'
        if normalized in ('disliked', 'dislike'):
            return 'dislike'
        raise ValueError(f"Unsupported feedback value: {feedback}")

    @staticmethod
    def _row_to_feedback_state(row: Optional[sqlite3.Row]) -> dict:
        """Convert a feedback row into the shape used by callbacks and admin APIs."""
        if not row:
            return {'watched': False, 'feedback': None, 'excluded': False}
        data = dict(row)
        data['watched'] = bool(data.get('watched'))
        data['excluded'] = bool(data.get('excluded'))
        return data

    def get_content_feedback_state(self, user_id: int, content_id: str) -> dict:
        """Return watched/feedback/excluded state for a single content item."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM user_content_feedback
            WHERE user_id = ? AND content_id = ?
        """, (user_id, content_id))
        row = cursor.fetchone()
        conn.close()
        return self._row_to_feedback_state(row)

    def set_feedback_state(
        self,
        user_id: int,
        content_id: str,
        content_type: str,
        title: str,
        watched: bool = False,
        feedback: Optional[str] = None,
        excluded: bool = False,
        tmdb_id: str = None,
        tvdb_id: str = None,
    ) -> dict:
        """Set the full feedback state for content and return the stored state."""
        content_id = self.normalize_content_id(content_type, content_id, title)
        feedback_value = self._normalize_feedback_value(feedback)
        now = datetime.now()
        current = self.get_content_feedback_state(user_id, content_id)
        created_at = current.get('created_at') or now
        stored_title = title or current.get('title')
        stored_content_type = content_type or current.get('content_type')
        stored_tmdb_id = tmdb_id if tmdb_id is not None else current.get('tmdb_id')
        stored_tvdb_id = tvdb_id if tvdb_id is not None else current.get('tvdb_id')

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO user_content_feedback
                (user_id, content_id, content_type, title, watched, feedback, excluded,
                 tmdb_id, tvdb_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            content_id,
            stored_content_type,
            stored_title,
            1 if watched else 0,
            feedback_value,
            1 if excluded else 0,
            stored_tmdb_id,
            stored_tvdb_id,
            created_at,
            now,
        ))
        conn.commit()
        conn.close()
        logger.info(
            "Set feedback state for user %s, content %s: watched=%s feedback=%s excluded=%s",
            user_id,
            content_id,
            watched,
            feedback_value,
            excluded,
        )
        return self.get_content_feedback_state(user_id, content_id)

    def toggle_feedback_state(
        self,
        user_id: int,
        content_id: str,
        content_type: str,
        title: str,
        action: str,
        tmdb_id: str = None,
        tvdb_id: str = None,
    ) -> dict:
        """Toggle one carousel feedback action and return the updated state."""
        content_id = self.normalize_content_id(content_type, content_id, title)
        current = self.get_content_feedback_state(user_id, content_id)
        watched = bool(current.get('watched'))
        feedback = current.get('feedback')
        excluded = bool(current.get('excluded'))
        normalized = action.lower()

        if normalized == 'ignore':
            excluded = not excluded
        elif normalized == 'watched':
            if watched and feedback is None:
                watched = False
            else:
                watched = True
                feedback = None
        elif normalized in ('liked', 'like'):
            if watched and feedback == 'like':
                watched = False
                feedback = None
            else:
                watched = True
                feedback = 'like'
        elif normalized in ('disliked', 'dislike'):
            if watched and feedback == 'dislike':
                watched = False
                feedback = None
            else:
                watched = True
                feedback = 'dislike'
        else:
            raise ValueError(f"Unsupported feedback action: {action}")

        return self.set_feedback_state(
            user_id=user_id,
            content_id=content_id,
            content_type=content_type,
            title=title,
            watched=watched,
            feedback=feedback,
            excluded=excluded,
            tmdb_id=tmdb_id,
            tvdb_id=tvdb_id,
        )

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
        """Add feedback using legacy action names."""
        content_id = self.normalize_content_id(content_type, content_id, title)
        current = self.get_content_feedback_state(user_id, content_id)
        watched = bool(current.get('watched'))
        feedback = current.get('feedback')
        excluded = bool(current.get('excluded'))
        normalized = feedback_type.lower()

        if normalized == 'watched':
            watched = True
        elif normalized in ('liked', 'like'):
            watched = True
            feedback = 'like'
        elif normalized in ('disliked', 'dislike'):
            watched = True
            feedback = 'dislike'
        elif normalized in ('ignored', 'ignore'):
            excluded = True
        else:
            raise ValueError(f"Unsupported feedback type: {feedback_type}")

        return self.set_feedback_state(
            user_id=user_id,
            content_id=content_id,
            content_type=content_type,
            title=title,
            watched=watched,
            feedback=feedback,
            excluded=excluded,
            tmdb_id=tmdb_id,
            tvdb_id=tvdb_id,
        )

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
            predicate = self._feedback_where_clause(feedback_type)
            cursor.execute("""
                SELECT * FROM user_content_feedback
                WHERE user_id = ? AND """ + predicate + """
                ORDER BY updated_at DESC
            """, (user_id,))
        else:
            cursor.execute("""
                SELECT * FROM user_content_feedback
                WHERE user_id = ?
                ORDER BY updated_at DESC
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
            WHERE user_id = ?
              AND (watched = 1 OR feedback = 'dislike' OR excluded = 1)
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
            WHERE user_id = ?
              AND (watched = 1 OR feedback = 'dislike' OR excluded = 1)
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
              AND (watched = 1 OR feedback = 'dislike' OR excluded = 1)
        """, (user_id,))

        rows = cursor.fetchall()
        conn.close()

        return {row[0] for row in rows if row[0]}

    def get_feedback_titles(self, user_id: int, feedback_type: FeedbackType) -> list:
        """Get list of titles for a specific feedback type (for prompt context)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        predicate = self._feedback_where_clause(feedback_type)
        cursor.execute("""
            SELECT title FROM user_content_feedback
            WHERE user_id = ? AND """ + predicate + """
            ORDER BY updated_at DESC
        """, (user_id,))

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

        predicate = self._feedback_where_clause(feedback_type)
        cursor.execute("""
            SELECT 1 FROM user_content_feedback
            WHERE user_id = ? AND content_id = ? AND """ + predicate + """
        """, (user_id, content_id))

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
        message_id: int = None,
        arr_service: str = None,
        arr_instance: str = None,
        arr_id: int = None,
    ) -> int:
        """Record that a user requested a media item via the bot"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO media_requests (
                telegram_id, title, media_type, tmdb_id, tvdb_id, chat_id, message_id,
                arr_service, arr_instance, arr_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            telegram_id,
            title,
            media_type,
            tmdb_id,
            tvdb_id,
            chat_id,
            message_id,
            arr_service,
            arr_instance,
            arr_id,
        ))

        request_id = cursor.lastrowid
        conn.commit()
        conn.close()
        logger.info(
            "Recorded media request: id=%s user=%s title='%s' type=%s",
            request_id,
            telegram_id,
            title,
            media_type,
        )
        return request_id

    def find_active_requests(
        self,
        title: str = None,
        tmdb_id: str = None,
        tvdb_id: str = None,
        media_type: str = None,
        arr_service: str = None,
        arr_id: int = None,
        download_id: str = None,
    ) -> List[dict]:
        """Find requests that can still receive lifecycle updates."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        conditions = ["status IN ('pending', 'grabbed')"]
        params = []

        id_conditions = []
        if download_id:
            id_conditions.append("download_id = ?")
            params.append(str(download_id))
        if arr_service and arr_id:
            id_conditions.append("(arr_service = ? AND arr_id = ?)")
            params.extend([arr_service, int(arr_id)])
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
        if media_type:
            conditions.append("media_type = ?")
            params.append(media_type)

        query = f"SELECT * FROM media_requests WHERE {' AND '.join(conditions)}"
        cursor.execute(query, params)

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def find_pending_requests(
        self,
        title: str = None,
        tmdb_id: str = None,
        tvdb_id: str = None
    ) -> List[dict]:
        """Find pending media requests matching downloaded media by ID or title"""
        return self.find_active_requests(title=title, tmdb_id=tmdb_id, tvdb_id=tvdb_id)

    def mark_request_notified(self, request_id: int):
        """Mark a media request as notified after sending the download notification"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE media_requests
            SET status = 'notified', notified_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (request_id,))

        conn.commit()
        conn.close()
        logger.info(f"Marked media request {request_id} as notified")

    def mark_request_queued_notified(self, request_id: int) -> bool:
        """Record that the user received the request_queued lifecycle message."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE media_requests
            SET queued_notified_at = CURRENT_TIMESTAMP
            WHERE id = ? AND queued_notified_at IS NULL
        """, (request_id,))

        conn.commit()
        updated = cursor.rowcount
        conn.close()
        if updated:
            logger.info(f"Marked media request {request_id} as queued-notified")
        return updated > 0

    def mark_request_grabbed(self, request_id: int, download_id: str = None):
        """Mark a request as grabbed by Radarr/Sonarr."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE media_requests
            SET status = 'grabbed',
                download_id = COALESCE(?, download_id),
                last_checked_at = CURRENT_TIMESTAMP
            WHERE id = ?
              AND (
                status = 'pending'
                OR (
                    status = 'grabbed'
                    AND ? IS NOT NULL
                    AND (download_id IS NULL OR download_id != ?)
                )
              )
        """, (download_id, request_id, download_id, download_id))

        conn.commit()
        updated = cursor.rowcount
        conn.close()
        if updated:
            logger.info(f"Marked media request {request_id} as grabbed")
        return updated > 0

    def mark_request_failed(
        self,
        request_id: int,
        reason: str,
        detail: str = None,
        status: str = 'failed',
    ) -> bool:
        """Mark an active request as failed/unavailable after notifying the user."""
        if status not in ('failed', 'unavailable'):
            raise ValueError(f"Unsupported failure status: {status}")

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE media_requests
            SET status = ?,
                failure_reason = ?,
                failure_detail = ?,
                failed_at = CURRENT_TIMESTAMP,
                notified_at = CURRENT_TIMESTAMP
            WHERE id = ? AND status IN ('pending', 'grabbed')
        """, (status, reason, detail, request_id))

        conn.commit()
        updated = cursor.rowcount
        conn.close()
        if updated:
            logger.info(f"Marked media request {request_id} as {status}: {reason}")
        return updated > 0

    def get_download_monitor_candidates(self, limit: int = 100) -> List[dict]:
        """Return active requests with Arr IDs for background monitoring."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM media_requests
            WHERE status IN ('pending', 'grabbed')
              AND arr_service IS NOT NULL
              AND arr_id IS NOT NULL
            ORDER BY COALESCE(last_checked_at, created_at) ASC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def mark_request_checked(self, request_id: int):
        """Record that the monitor inspected a request."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE media_requests
            SET last_checked_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (request_id,))
        conn.commit()
        conn.close()

    def get_media_request(self, request_id: int) -> Optional[dict]:
        """Fetch a single media request row."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM media_requests WHERE id = ?", (request_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

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

    def clear_media_requests(self, user_id: int) -> int:
        """Delete all media request rows for a Telegram user. Returns rows removed."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM media_requests WHERE telegram_id = ?",
            (user_id,),
        )
        removed = cursor.rowcount
        conn.commit()
        conn.close()
        logger.info("Cleared %s media requests for user %s", removed, user_id)
        return removed

    def clear_user_feedback(
        self,
        user_id: int,
        *,
        watched: Optional[bool] = None,
        feedback: Optional[str] = None,
        excluded: Optional[bool] = None,
    ) -> int:
        """Delete feedback rows for a user, optionally filtered by column values.

        With no filters, deletes every feedback row for the user.
        """
        clauses = ["user_id = ?"]
        params: list = [user_id]
        if watched is not None:
            clauses.append("watched = ?")
            params.append(1 if watched else 0)
        if feedback is not None:
            clauses.append("feedback = ?")
            params.append(self._normalize_feedback_value(feedback))
        if excluded is not None:
            clauses.append("excluded = ?")
            params.append(1 if excluded else 0)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM user_content_feedback WHERE " + " AND ".join(clauses),
            params,
        )
        removed = cursor.rowcount
        conn.commit()
        conn.close()
        logger.info("Cleared %s feedback rows for user %s", removed, user_id)
        return removed

    def get_recent_feedback(self, limit: int = 50, user_id: Optional[int] = None) -> List[dict]:
        """Get recent user feedback for the admin UI"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if user_id:
            cursor.execute("""
                SELECT * FROM user_content_feedback
                WHERE user_id = ?
                ORDER BY updated_at DESC
                LIMIT ?
            """, (user_id, limit))
        else:
            cursor.execute("""
                SELECT * FROM user_content_feedback
                ORDER BY updated_at DESC
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
                f.watched,
                f.feedback,
                f.excluded,
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
                0 as watched,
                NULL as feedback,
                0 as excluded,
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
