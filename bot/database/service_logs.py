"""
Outbound Radarr, Sonarr, and Jellyfin API request logs for the admin UI.

Persists HTTP method, endpoint, params/body, timing, and response data so
Media Management and Media Servers activity can be inspected alongside TMDB logs.
"""

import json
import logging
import sqlite3
from datetime import datetime
from typing import List, Optional

logger = logging.getLogger(__name__)


class ServiceLogMixin:
    """Service API log CRUD — mixed into Database."""

    def _init_service_log_schema(self, cursor: sqlite3.Cursor) -> None:
        """Create service_api_logs table and indexes."""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS service_api_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service TEXT NOT NULL,
                method TEXT NOT NULL,
                endpoint TEXT,
                params TEXT,
                request_body TEXT,
                duration_ms INTEGER,
                status_code INTEGER,
                response_body TEXT,
                error TEXT,
                session_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_service_api_logs_created
            ON service_api_logs(created_at)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_service_api_logs_session
            ON service_api_logs(session_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_service_api_logs_service
            ON service_api_logs(service)
        """)

    def log_service_api_request(
        self,
        service: str,
        method: str,
        endpoint: str,
        params: Optional[dict] = None,
        request_body: Optional[str] = None,
        duration_ms: Optional[int] = None,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
        error: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> None:
        """Log an outbound Radarr, Sonarr, or Jellyfin API request."""
        params_str = json.dumps(params) if params else None

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO service_api_logs (
                    service, method, endpoint, params, request_body,
                    duration_ms, status_code, response_body, error,
                    session_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                service,
                method,
                endpoint,
                params_str,
                request_body,
                duration_ms,
                status_code,
                response_body,
                error,
                session_id,
                datetime.now(),
            ))
            conn.commit()
        except Exception as e:
            logger.error(f"Failed to log service API request: {e}")
        finally:
            conn.close()

    def get_service_api_logs(
        self,
        limit: int = 100,
        services: Optional[List[str]] = None,
    ) -> List[dict]:
        """Get recent service API logs with user_id resolved via session."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if services:
            placeholders = ",".join("?" * len(services))
            cursor.execute(f"""
                SELECT l.*, s.user_id
                FROM service_api_logs l
                LEFT JOIN sessions s ON s.id = l.session_id
                WHERE l.service IN ({placeholders})
                ORDER BY l.created_at DESC
                LIMIT ?
            """, (*services, limit))
        else:
            cursor.execute("""
                SELECT l.*, s.user_id
                FROM service_api_logs l
                LEFT JOIN sessions s ON s.id = l.session_id
                ORDER BY l.created_at DESC
                LIMIT ?
            """, (limit,))

        logs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return logs

    def get_service_api_logs_for_session(self, session_id: str) -> List[dict]:
        """Return ordered service API logs for a single session."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM service_api_logs
            WHERE session_id = ?
            ORDER BY created_at ASC
        """, (session_id,))

        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows
