"""
Plex API client for watch history sync and media search.

Mirrors bot/jellyfin.py so the bot can use Plex as an alternative media
server with the same capabilities: fetching watched titles for recommendation
exclusions and resolving Plex web URLs for carousel play buttons and
download-ready notifications.

Auth model differs from Jellyfin: the server-level token (`api_key`, an admin
X-Plex-Token) is used for search and URL building, while watch history is read
with each user's own per-user token (from their `media_server.token` config).
All HTTP goes through make_service_request for uniform logging (service='plex').
"""

import logging
from typing import Any, Dict, List, Optional

from bot.service_request import make_service_request

logger = logging.getLogger(__name__)

# Plex library section / metadata type codes.
_TYPE_MOVIE = '1'
_TYPE_SHOW = '2'


class PlexClient:
    display_name = "Plex"

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key  # admin X-Plex-Token (search + URL building)
        self.db = None
        self._machine_identifier: Optional[str] = None

    def _headers(self, token: Optional[str] = None) -> Dict[str, str]:
        """Build request headers; Accept JSON so Plex returns JSON not XML."""
        return {
            'X-Plex-Token': token or self.api_key,
            'Accept': 'application/json',
        }

    def get_watched_items(self, user_media_config: Dict[str, Any]) -> List[str]:
        """
        Fetch watched movies and TV shows for a Plex user.
        Uses the per-user token from the user's `media_server` config (`token`).
        Returns list of titles.
        """
        token = (user_media_config or {}).get('token')
        if not token:
            logger.warning("No Plex user token provided")
            return []

        try:
            sections = self._get_sections(token)
            watched_titles: List[str] = []
            for section in sections:
                section_type = section.get('type')
                key = section.get('key')
                if not key or section_type not in ('movie', 'show'):
                    continue
                watched_titles.extend(self._get_watched_in_section(token, key, section_type))

            logger.info(f"Fetched {len(watched_titles)} watched items from Plex")
            return watched_titles
        except Exception as e:
            logger.error(f"Error fetching Plex watched items: {e}")
            return []

    def _get_sections(self, token: str) -> List[Dict[str, Any]]:
        """Return the library sections (Directory entries) for the token."""
        url = f"{self.base_url}/library/sections"
        response = make_service_request(
            self.db, 'plex', 'GET', url,
            headers=self._headers(token), timeout=10,
        )
        container = response.json().get('MediaContainer', {})
        return container.get('Directory', []) or []

    def _get_watched_in_section(self, token: str, key: str, section_type: str) -> List[str]:
        """Fetch watched titles within a single library section."""
        url = f"{self.base_url}/library/sections/{key}/all"
        item_type = _TYPE_MOVIE if section_type == 'movie' else _TYPE_SHOW
        params = {'type': item_type}

        try:
            response = make_service_request(
                self.db, 'plex', 'GET', url,
                headers=self._headers(token), params=params, timeout=10,
            )
            items = response.json().get('MediaContainer', {}).get('Metadata', []) or []
            titles = []
            for item in items:
                # Movies expose viewCount; shows track viewedLeafCount (watched episodes).
                watched = item.get('viewCount', 0) or item.get('viewedLeafCount', 0)
                name = item.get('title')
                if watched and name:
                    titles.append(name)

            logger.debug(f"Fetched {len(titles)} watched {section_type}(s) from Plex")
            return titles
        except Exception as e:
            logger.error(f"Plex API error for section {key}: {e}")
            return []

    def search_item(self, title: str, media_type: str, tmdb_id: str = None, tvdb_id: str = None) -> Optional[str]:
        """
        Search Plex for a media item and return a web URL to it.
        Uses provider IDs (TMDB/TVDB) for precise matching when available,
        falls back to title search otherwise.
        Returns URL like {base_url}/web/index.html#!/server/{mid}/details?key=... or None.
        """
        wanted_type = 'movie' if media_type == 'movie' else 'show'
        url = f"{self.base_url}/library/search"
        params = {'query': title, 'limit': '10'}

        logger.info(f"Plex search: title='{title}', type={wanted_type}, tmdb={tmdb_id}, tvdb={tvdb_id}")

        try:
            response = make_service_request(
                self.db, 'plex', 'GET', url,
                headers=self._headers(), params=params, timeout=10,
            )
            results = self._extract_metadata(response.json())
            candidates = [m for m in results if m.get('type') == wanted_type]
            logger.info(f"Plex search returned {len(candidates)} {wanted_type} result(s) for '{title}'")

            if candidates and (tmdb_id or tvdb_id):
                for item in candidates:
                    rating_key = item.get('ratingKey')
                    guids = {g.get('id') for g in item.get('Guid', []) if g.get('id')}
                    if tmdb_id and f"tmdb://{tmdb_id}" in guids:
                        logger.info(f"Plex match by TMDB ID: '{item.get('title', '?')}' (key={rating_key})")
                        return self.get_item_url(rating_key)
                    if tvdb_id and f"tvdb://{tvdb_id}" in guids:
                        logger.info(f"Plex match by TVDB ID: '{item.get('title', '?')}' (key={rating_key})")
                        return self.get_item_url(rating_key)
                logger.info(f"No Plex match by provider ID for '{title}'")
                return None

            if candidates:
                rating_key = candidates[0].get('ratingKey')
                logger.info(f"Plex match by title: '{candidates[0].get('title', '?')}' (key={rating_key})")
                if rating_key:
                    return self.get_item_url(rating_key)

            logger.info(f"No Plex match found for '{title}' ({wanted_type})")
            return None
        except Exception as e:
            logger.error(f"Plex search error for '{title}': {e}")
            return None

    @staticmethod
    def _extract_metadata(data: dict) -> List[Dict[str, Any]]:
        """Normalize search results across Plex's SearchResult / Metadata shapes."""
        container = data.get('MediaContainer', {})
        if container.get('Metadata'):
            return container['Metadata']
        results = container.get('SearchResult', []) or []
        return [r.get('Metadata') for r in results if r.get('Metadata')]

    def get_item_url(self, item_id: str) -> str:
        """
        Build a Plex web URL from a ratingKey. Fetches the server's
        machineIdentifier once (cached) since Plex web URLs are server-scoped.
        """
        mid = self._get_machine_identifier()
        return (
            f"{self.base_url}/web/index.html#!/server/{mid}"
            f"/details?key=%2Flibrary%2Fmetadata%2F{item_id}"
        )

    def _get_machine_identifier(self) -> str:
        """Return the server's machineIdentifier, fetching and caching it once."""
        if self._machine_identifier:
            return self._machine_identifier
        url = f"{self.base_url}/identity"
        response = make_service_request(
            self.db, 'plex', 'GET', url,
            headers=self._headers(), timeout=10,
        )
        self._machine_identifier = response.json().get('MediaContainer', {}).get('machineIdentifier', '')
        return self._machine_identifier
