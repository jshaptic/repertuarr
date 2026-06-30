"""
Temporary storage for recently recommended items.

Tracks titles and TMDB IDs shown in RECOMMEND carousels so repeat requests
can exclude them until a configurable TTL expires.
"""

import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Any, Iterable, List, Set

logger = logging.getLogger(__name__)


def _carousel_item_field(item: Any, name: str, *dict_aliases: str) -> Any:
    """Read a field from a carousel item (Pydantic model or API dict)."""
    if isinstance(item, dict):
        for key in (name, *dict_aliases):
            if key in item:
                return item[key]
        return None
    return getattr(item, name, None)


class RecentRecommendationsMixin:
    """Recent recommendation cooldown CRUD — mixed into Database."""

    def _init_recommendations_schema(self, cursor: sqlite3.Cursor) -> None:
        """Create recent_recommendations table."""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recent_recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                original_title TEXT,
                tmdb_id TEXT,
                recommended_at TIMESTAMP NOT NULL
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_recent_rec_user_time
            ON recent_recommendations(user_id, recommended_at)
        """)

    def _purge_expired_recent_recommendations(self, user_id: int, ttl_seconds: int) -> None:
        """Delete rows older than the TTL for a user."""
        cutoff = (datetime.now() - timedelta(seconds=ttl_seconds)).isoformat()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM recent_recommendations WHERE user_id = ? AND recommended_at < ?",
            (user_id, cutoff),
        )
        conn.commit()
        conn.close()

    def record_recent_recommendations(self, user_id: int, items: Iterable[Any]) -> None:
        """Persist items shown in a RECOMMEND carousel."""
        now = datetime.now().isoformat()
        rows = []
        for item in items:
            title = _carousel_item_field(item, 'title')
            if not title:
                continue
            original_title = _carousel_item_field(item, 'original_title')
            tmdb_id = _carousel_item_field(item, 'tmdb_id', 'tmdbId')
            rows.append((
                user_id,
                title,
                original_title,
                str(tmdb_id) if tmdb_id is not None else None,
                now,
            ))

        if not rows:
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.executemany("""
            INSERT INTO recent_recommendations
                (user_id, title, original_title, tmdb_id, recommended_at)
            VALUES (?, ?, ?, ?, ?)
        """, rows)
        conn.commit()
        conn.close()
        logger.info("Recorded %d recent recommendation(s) for user %s", len(rows), user_id)

    def get_recent_excluded_tmdb_ids(self, user_id: int, ttl_seconds: int) -> Set[str]:
        """Return TMDB IDs recommended within the TTL window."""
        self._purge_expired_recent_recommendations(user_id, ttl_seconds)
        cutoff = (datetime.now() - timedelta(seconds=ttl_seconds)).isoformat()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT tmdb_id FROM recent_recommendations
            WHERE user_id = ? AND recommended_at >= ? AND tmdb_id IS NOT NULL
        """, (user_id, cutoff))
        rows = cursor.fetchall()
        conn.close()
        return {row[0] for row in rows if row[0]}

    def get_recent_excluded_titles(self, user_id: int, ttl_seconds: int) -> Set[str]:
        """Return localized and original titles recommended within the TTL window."""
        self._purge_expired_recent_recommendations(user_id, ttl_seconds)
        cutoff = (datetime.now() - timedelta(seconds=ttl_seconds)).isoformat()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT title, original_title FROM recent_recommendations
            WHERE user_id = ? AND recommended_at >= ?
        """, (user_id, cutoff))
        rows = cursor.fetchall()
        conn.close()

        titles: Set[str] = set()
        for title, original_title in rows:
            if title:
                titles.add(title.lower())
            if original_title:
                titles.add(original_title.lower())
        return titles

    def get_recent_recommendations(self, user_id: int, ttl_seconds: int) -> List[dict]:
        """Return active (non-expired) recently recommended items for the admin UI.

        Each row includes the original recommendation timestamp and the computed
        expiry time so the UI can show how long a title stays on cooldown.
        """
        self._purge_expired_recent_recommendations(user_id, ttl_seconds)
        cutoff = (datetime.now() - timedelta(seconds=ttl_seconds)).isoformat()
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT title, original_title, tmdb_id, recommended_at
            FROM recent_recommendations
            WHERE user_id = ? AND recommended_at >= ?
            ORDER BY recommended_at DESC
        """, (user_id, cutoff))
        rows = cursor.fetchall()
        conn.close()

        items = []
        for row in rows:
            data = dict(row)
            expires_at = None
            recommended_at = data.get('recommended_at')
            if recommended_at:
                try:
                    expires_at = (
                        datetime.fromisoformat(recommended_at) + timedelta(seconds=ttl_seconds)
                    ).isoformat()
                except ValueError:
                    expires_at = None
            data['expires_at'] = expires_at
            items.append(data)
        return items

    def clear_recent_recommendations(self, user_id: int) -> int:
        """Delete all recent recommendation rows for a user. Returns rows removed."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM recent_recommendations WHERE user_id = ?",
            (user_id,),
        )
        removed = cursor.rowcount
        conn.commit()
        conn.close()
        return removed
