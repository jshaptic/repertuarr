"""
Media-server abstraction: a common interface and factory for the bot's
media server backends (Jellyfin, Plex).

The rest of the app talks to a single active media server through the
`MediaServerClient` protocol and never branches on the concrete type. Which
backend is built is decided by `build_media_server_client` from the
`media_servers` config entry's `type` field (defaults to "jellyfin" for
backward compatibility). Only one media server is active at a time — Plex is
configured as an alternative to Jellyfin, not alongside it.
"""

import logging
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable

from bot.jellyfin import JellyfinClient
from bot.plex import PlexClient

logger = logging.getLogger(__name__)


@runtime_checkable
class MediaServerClient(Protocol):
    """Shared surface implemented by every media-server backend."""

    #: Human-readable name shown in play-button labels, e.g. "Jellyfin"/"Plex".
    display_name: str
    #: Database handle, injected after construction for request logging.
    db: Any

    def get_watched_items(self, user_media_config: Dict[str, Any]) -> List[str]:
        """Return watched titles for the user described by their
        `media_server` config dict (Jellyfin reads `user_id`, Plex `token`)."""
        ...

    def search_item(
        self,
        title: str,
        media_type: str,
        tmdb_id: Optional[str] = None,
        tvdb_id: Optional[str] = None,
    ) -> Optional[str]:
        """Return a web URL to the matching library item, or None."""
        ...

    def get_item_url(self, item_id: str) -> str:
        """Build a web URL for an item id (no API call, may cache metadata)."""
        ...


def build_media_server_client(
    cfg: Optional[Dict[str, Any]],
) -> Optional[MediaServerClient]:
    """
    Build the configured media-server client from a `media_servers` entry.

    Returns None when no server is configured. `type` defaults to "jellyfin"
    so existing configs without the field keep working.
    """
    if not cfg:
        logger.info("No media server configured, skipping watch history sync")
        return None

    server_type = (cfg.get('type') or 'jellyfin').lower()
    url = cfg.get('url')
    api_key = cfg.get('api_key')

    if not url or not api_key:
        logger.info("Media server '%s' missing url/api_key, skipping", cfg.get('name'))
        return None

    if server_type == 'jellyfin':
        logger.info("Jellyfin client initialized")
        return JellyfinClient(url, api_key)
    if server_type == 'plex':
        logger.info("Plex client initialized")
        return PlexClient(url, api_key)

    raise ValueError(f"Unknown media server type: {server_type!r}")
