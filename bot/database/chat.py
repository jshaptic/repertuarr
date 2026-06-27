"""
Chat transcript and carousel state persistence.

Provides a mixin used by Database that stores the per-user conversational
transcript (user messages + bot text answers) and the navigation state of
each interactive carousel card.

Two tables back these features:
  - chat_messages: one row per stored conversational turn, keyed by the
    Telegram (chat_id, message_id) so edits can be synced and the admin UI
    can render the full transcript.
  - carousel_state: one row per carousel card (keyed by its Telegram
    message_id) holding the candidate list and the current scroll index, so
    every card stays independently navigable across restarts.
"""

import json
import logging
import sqlite3
from datetime import datetime
from typing import Any, List, Optional

logger = logging.getLogger(__name__)


class ChatMixin:
    """Chat transcript and carousel state CRUD — mixed into Database."""

    def _init_chat_schema(self, cursor: sqlite3.Cursor) -> None:
        """Create chat_messages and carousel_state tables."""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                chat_id INTEGER NOT NULL,
                message_id INTEGER,
                role TEXT NOT NULL,
                text TEXT,
                session_id TEXT,
                edited_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_chat_messages_user
            ON chat_messages(user_id, created_at)
        """)
        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_chat_messages_msg
            ON chat_messages(chat_id, message_id)
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS carousel_state (
                chat_id INTEGER NOT NULL,
                message_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                media_type TEXT NOT NULL,
                idx INTEGER NOT NULL DEFAULT 0,
                results_json TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (chat_id, message_id)
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_carousel_state_user
            ON carousel_state(user_id)
        """)

        for stmt in (
            "ALTER TABLE carousel_state ADD COLUMN session_id TEXT",
        ):
            try:
                cursor.execute(stmt)
            except sqlite3.OperationalError:
                pass

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_carousel_state_session
            ON carousel_state(session_id)
        """)

    # ── Chat transcript ─────────────────────────────────────────────

    def add_chat_message(
        self,
        user_id: int,
        chat_id: int,
        role: str,
        text: str,
        message_id: Optional[int] = None,
        session_id: Optional[str] = None,
    ) -> int:
        """Store a conversational turn and return its row id."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO chat_messages
                (user_id, chat_id, message_id, role, text, session_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, chat_id, message_id, role, text, session_id, datetime.now()))
        row_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return row_id

    def update_chat_message_text(self, chat_id: int, message_id: int, text: str) -> bool:
        """Update the text of an existing message (used for edit sync)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE chat_messages
            SET text = ?, edited_at = ?
            WHERE chat_id = ? AND message_id = ?
        """, (text, datetime.now(), chat_id, message_id))
        changed = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return changed

    def get_chat_messages(self, user_id: int, limit: int = 30) -> List[dict]:
        """Return the most recent transcript turns for a user, oldest first."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM (
                SELECT * FROM chat_messages
                WHERE user_id = ?
                ORDER BY id DESC
                LIMIT ?
            )
            ORDER BY id ASC
        """, (user_id, limit))
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows

    def clear_chat(self, user_id: int) -> int:
        """Delete all stored chat messages for a user. Returns rows removed."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chat_messages WHERE user_id = ?", (user_id,))
        removed = cursor.rowcount
        conn.commit()
        conn.close()
        logger.info(f"Cleared {removed} chat messages for user {user_id}")
        return removed

    # ── Carousel state ──────────────────────────────────────────────

    def save_carousel_state(
        self,
        chat_id: int,
        message_id: int,
        user_id: int,
        media_type: str,
        results: List[Any],
        index: int = 0,
        session_id: Optional[str] = None,
    ) -> None:
        """Persist (or replace) the full state of a carousel card."""
        results_json = json.dumps(results, default=_json_default)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO carousel_state
                (chat_id, message_id, user_id, media_type, idx, results_json, session_id, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (chat_id, message_id, user_id, media_type, index, results_json, session_id, datetime.now()))
        conn.commit()
        conn.close()

    def get_carousels_by_sessions(self, session_ids: List[str]) -> dict:
        """Map session_id -> {media_type, items} for the carousels in those sessions.

        When a session produced several carousel cards, the most recently
        updated one wins.
        """
        ids = [s for s in session_ids if s]
        if not ids:
            return {}
        placeholders = ",".join("?" * len(ids))
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT session_id, media_type, results_json
            FROM carousel_state
            WHERE session_id IN ({placeholders})
            ORDER BY updated_at ASC
        """, ids)
        out = {}
        for row in cursor.fetchall():
            out[row['session_id']] = {
                'media_type': row['media_type'],
                'items': json.loads(row['results_json']),
            }
        conn.close()
        return out

    def get_carousel_state(self, chat_id: int, message_id: int) -> Optional[dict]:
        """Return the stored state of a carousel card, with results decoded."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM carousel_state WHERE chat_id = ? AND message_id = ?
        """, (chat_id, message_id))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        state = dict(row)
        state['results'] = json.loads(state.pop('results_json'))
        return state

    def update_carousel_index(self, chat_id: int, message_id: int, index: int) -> None:
        """Update only the scroll index of a carousel card."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE carousel_state SET idx = ?, updated_at = ?
            WHERE chat_id = ? AND message_id = ?
        """, (index, datetime.now(), chat_id, message_id))
        conn.commit()
        conn.close()

    def update_carousel_results(
        self, chat_id: int, message_id: int, results: List[Any]
    ) -> None:
        """Replace the stored candidate list (used after lazy metadata loads)."""
        results_json = json.dumps(results, default=_json_default)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE carousel_state SET results_json = ?, updated_at = ?
            WHERE chat_id = ? AND message_id = ?
        """, (results_json, datetime.now(), chat_id, message_id))
        conn.commit()
        conn.close()

    def clear_user_carousels(self, user_id: int) -> int:
        """Delete all carousel state for a user. Returns rows removed."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM carousel_state WHERE user_id = ?", (user_id,))
        removed = cursor.rowcount
        conn.commit()
        conn.close()
        return removed


def _json_default(obj: Any):
    """Serialize Pydantic models (recommendation items) to plain dicts."""
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")
