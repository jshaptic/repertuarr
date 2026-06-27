"""
Session and activity log persistence for the admin UI.

Provides a mixin used by Database for sessions, LLM logs, and TMDB request logs.
Groups bot interactions by session ID so AI calls and TMDB requests from a single
user message can be viewed together in the admin panel.
"""

import json
import logging
import sqlite3
from datetime import datetime
from typing import List, Optional

logger = logging.getLogger(__name__)


class LogMixin:
    """Session and log CRUD methods — mixed into Database."""

    def _init_log_schema(self, cursor: sqlite3.Cursor) -> None:
        """Create or migrate sessions, llm_logs, and tmdb_logs tables."""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                user_message TEXT,
                detected_intent TEXT,
                status TEXT,
                duration_ms INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sessions_created
            ON sessions(created_at)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_sessions_user
            ON sessions(user_id)
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS llm_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                user_message TEXT,
                intent TEXT,
                llm_request TEXT,
                llm_response TEXT,
                duration_ms INTEGER,
                model TEXT,
                tokens INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_llm_logs_created
            ON llm_logs(created_at)
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tmdb_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                endpoint TEXT,
                params TEXT,
                duration_ms INTEGER,
                status_code INTEGER,
                response_body TEXT,
                error TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tmdb_logs_created
            ON tmdb_logs(created_at)
        """)

        for stmt in (
            "ALTER TABLE llm_logs ADD COLUMN session_id TEXT",
            "ALTER TABLE llm_logs ADD COLUMN prompt_name TEXT",
            "ALTER TABLE llm_logs ADD COLUMN raw_request TEXT",
            "ALTER TABLE llm_logs ADD COLUMN raw_response TEXT",
            "ALTER TABLE llm_logs ADD COLUMN input_tokens INTEGER",
            "ALTER TABLE llm_logs ADD COLUMN output_tokens INTEGER",
            "ALTER TABLE llm_logs ADD COLUMN cached_input_tokens INTEGER",
            "ALTER TABLE llm_logs ADD COLUMN cost_usd REAL",
            "ALTER TABLE llm_logs ADD COLUMN llm_name TEXT",
            "ALTER TABLE llm_logs ADD COLUMN status_code INTEGER",
            "ALTER TABLE tmdb_logs ADD COLUMN session_id TEXT",
        ):
            try:
                cursor.execute(stmt)
            except sqlite3.OperationalError:
                pass

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_llm_logs_session
            ON llm_logs(session_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tmdb_logs_session
            ON tmdb_logs(session_id)
        """)

    # ── Sessions ────────────────────────────────────────────────────

    def create_session(self, session_id: str, user_id: int, user_message: str) -> None:
        """Record the start of a bot interaction session."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO sessions (id, user_id, user_message, status, created_at)
            VALUES (?, ?, ?, 'in_progress', ?)
        """, (session_id, user_id, user_message, datetime.now()))
        conn.commit()
        conn.close()

    def complete_session(
        self,
        session_id: str,
        detected_intent: Optional[str],
        status: str,
        duration_ms: int,
    ) -> None:
        """Mark a session as completed or failed."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE sessions
            SET detected_intent = ?, status = ?, duration_ms = ?
            WHERE id = ?
        """, (detected_intent, status, duration_ms, session_id))
        conn.commit()
        conn.close()

    def get_recent_sessions(
        self, limit: int = 50, user_id: Optional[int] = None
    ) -> List[dict]:
        """List recent sessions with aggregate LLM and TMDB call counts."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if user_id:
            cursor.execute("""
                SELECT s.*,
                       (SELECT COALESCE(SUM(cost_usd), 0) FROM llm_logs WHERE session_id = s.id) AS llm_cost_usd
                FROM sessions s
                WHERE s.user_id = ?
                ORDER BY s.created_at DESC
                LIMIT ?
            """, (user_id, limit))
        else:
            cursor.execute("""
                SELECT s.*,
                       (SELECT COALESCE(SUM(cost_usd), 0) FROM llm_logs WHERE session_id = s.id) AS llm_cost_usd
                FROM sessions s
                ORDER BY s.created_at DESC
                LIMIT ?
            """, (limit,))

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_session_detail(self, session_id: str) -> Optional[dict]:
        """Return session metadata plus ordered LLM and TMDB logs."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
        session_row = cursor.fetchone()
        if not session_row:
            conn.close()
            return None

        cursor.execute("""
            SELECT * FROM llm_logs WHERE session_id = ? ORDER BY created_at ASC
        """, (session_id,))
        llm_logs = [dict(row) for row in cursor.fetchall()]

        cursor.execute("""
            SELECT * FROM tmdb_logs WHERE session_id = ? ORDER BY created_at ASC
        """, (session_id,))
        tmdb_logs = [dict(row) for row in cursor.fetchall()]

        conn.close()
        return {
            "session": dict(session_row),
            "llm_logs": llm_logs,
            "tmdb_logs": tmdb_logs,
        }

    def get_session_costs(self, session_ids: List[str]) -> dict:
        """Map session_id -> total LLM cost (USD) for the given sessions."""
        ids = [s for s in session_ids if s]
        if not ids:
            return {}
        placeholders = ",".join("?" * len(ids))
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT session_id, COALESCE(SUM(cost_usd), 0)
            FROM llm_logs
            WHERE session_id IN ({placeholders})
            GROUP BY session_id
        """, ids)
        out = {row[0]: row[1] for row in cursor.fetchall()}
        conn.close()
        return out

    # ── LLM Logs ────────────────────────────────────────────────────

    def log_llm_interaction(
        self,
        user_id: int,
        user_message: str,
        llm_request: str,
        llm_response: str,
        duration_ms: int,
        model: str,
        tokens: int,
        session_id: Optional[str] = None,
        prompt_name: Optional[str] = None,
        raw_request: Optional[str] = None,
        raw_response: Optional[str] = None,
        intent: Optional[str] = None,
        input_tokens: Optional[int] = None,
        output_tokens: Optional[int] = None,
        cached_input_tokens: Optional[int] = None,
        cost_usd: Optional[float] = None,
        llm_name: Optional[str] = None,
        status_code: Optional[int] = None,
    ) -> None:
        """Log an LLM interaction to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO llm_logs (
                user_id, user_message, intent, llm_request, llm_response,
                duration_ms, model, tokens, session_id, prompt_name,
                raw_request, raw_response, input_tokens, output_tokens,
                cached_input_tokens, cost_usd, llm_name, status_code, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            user_message,
            intent,
            llm_request,
            llm_response,
            duration_ms,
            model,
            tokens,
            session_id,
            prompt_name,
            raw_request,
            raw_response,
            input_tokens,
            output_tokens,
            cached_input_tokens,
            cost_usd,
            llm_name,
            status_code,
            datetime.now(),
        ))
        conn.commit()
        conn.close()

    def get_recent_llm_logs(
        self, limit: int = 50, user_id: Optional[int] = None
    ) -> List[dict]:
        """Get recent LLM logs for the admin UI."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if user_id:
            cursor.execute("""
                SELECT * FROM llm_logs
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (user_id, limit))
        else:
            cursor.execute("""
                SELECT * FROM llm_logs
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))

        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    # ── TMDB Logs ───────────────────────────────────────────────────

    def log_tmdb_request(
        self,
        endpoint: str,
        params: Optional[dict] = None,
        duration_ms: Optional[int] = None,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
        error: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> None:
        """Log a TMDB API request and response."""
        params_str = json.dumps(params) if params else None

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO tmdb_logs (
                    endpoint, params, duration_ms, status_code,
                    response_body, error, session_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                endpoint,
                params_str,
                duration_ms,
                status_code,
                response_body,
                error,
                session_id,
                datetime.now(),
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Failed to log TMDB request: {e}")
        finally:
            conn.close()

    def get_tmdb_logs(self, limit: int = 100) -> List[dict]:
        """Get recent TMDB logs with user_id resolved via session."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT t.*, s.user_id
            FROM tmdb_logs t
            LEFT JOIN sessions s ON s.id = t.session_id
            ORDER BY t.created_at DESC
            LIMIT ?
        """, (limit,))

        logs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return logs
