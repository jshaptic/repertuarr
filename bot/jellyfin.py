"""
Jellyfin API client for watch history sync and media search.

Fetches watched titles for recommendation exclusions and resolves Jellyfin
web URLs for carousel play buttons and download notifications.
"""

import logging
from typing import List, Optional

from bot.service_request import make_service_request

logger = logging.getLogger(__name__)


class JellyfinClient:
    display_name = "Jellyfin"

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'X-Emby-Token': api_key,
            'Content-Type': 'application/json',
        }
        self.db = None

    def get_watched_items(self, user_media_config: dict) -> List[str]:
        """
        Fetch watched movies and TV shows for a Jellyfin user.
        `user_media_config` is the user's `media_server` config dict; the
        Jellyfin user UUID is read from its `user_id` field.
        Returns list of titles.
        """
        user_id = (user_media_config or {}).get('user_id')
        if not user_id:
            logger.warning("No Jellyfin user ID provided")
            return []

        watched_titles = []

        try:
            movies = self._get_watched_by_type(user_id, 'Movie')
            watched_titles.extend(movies)

            series = self._get_watched_by_type(user_id, 'Series')
            watched_titles.extend(series)

            logger.info(f"Fetched {len(watched_titles)} watched items from Jellyfin for user {user_id}")
            return watched_titles

        except Exception as e:
            logger.error(f"Error fetching Jellyfin watched items: {e}")
            return []

    def _get_watched_by_type(self, user_id: str, item_type: str) -> List[str]:
        """Fetch watched items of a specific type"""
        url = f"{self.base_url}/Users/{user_id}/Items"

        params = {
            'IncludeItemTypes': item_type,
            'Recursive': 'true',
            'IsPlayed': 'true',
            'Fields': 'Name',
            'SortBy': 'DatePlayed',
            'SortOrder': 'Descending',
        }

        try:
            response = make_service_request(
                self.db, 'jellyfin', 'GET', url,
                headers=self.headers, params=params, timeout=10,
            )
            data = response.json()

            items = data.get('Items', [])
            titles = [item.get('Name') for item in items if item.get('Name')]

            logger.debug(f"Fetched {len(titles)} {item_type}s from Jellyfin")
            return titles

        except Exception as e:
            logger.error(f"Jellyfin API error for {item_type}: {e}")
            return []

    def search_item(self, title: str, media_type: str, tmdb_id: str = None, tvdb_id: str = None) -> Optional[str]:
        """
        Search Jellyfin for a media item and return a web URL to it.
        Uses provider IDs (TMDB/TVDB) for precise matching when available,
        falls back to title search otherwise.
        Returns URL like {base_url}/web/#/details?id={ItemId} or None.
        """
        item_type = 'Movie' if media_type == 'movie' else 'Series'
        url = f"{self.base_url}/Items"

        params = {
            'searchTerm': title,
            'IncludeItemTypes': item_type,
            'Recursive': 'true',
            'Limit': '10',
            'Fields': 'Name,ProviderIds',
        }

        logger.info(f"Jellyfin search: title='{title}', type={item_type}, tmdb={tmdb_id}, tvdb={tvdb_id}")

        try:
            response = make_service_request(
                self.db, 'jellyfin', 'GET', url,
                headers=self.headers, params=params, timeout=10,
            )
            data = response.json()

            items = data.get('Items', [])
            logger.info(f"Jellyfin search returned {len(items)} result(s) for '{title}'")

            if items and (tmdb_id or tvdb_id):
                for item in items:
                    provider_ids = item.get('ProviderIds', {})
                    item_id = item.get('Id')
                    item_name = item.get('Name', '?')
                    logger.info(f"  Checking '{item_name}' (id={item_id}, providers={provider_ids})")

                    if tmdb_id and provider_ids.get('Tmdb') == str(tmdb_id):
                        logger.info(f"Jellyfin match by TMDB ID: '{item_name}' (id={item_id})")
                        return f"{self.base_url}/web/#/details?id={item_id}"
                    if tvdb_id and provider_ids.get('Tvdb') == str(tvdb_id):
                        logger.info(f"Jellyfin match by TVDB ID: '{item_name}' (id={item_id})")
                        return f"{self.base_url}/web/#/details?id={item_id}"

                logger.info(f"No Jellyfin match by provider ID for '{title}'")
                return None

            if items:
                item_id = items[0].get('Id')
                item_name = items[0].get('Name', '?')
                logger.info(f"Jellyfin match by title: '{item_name}' (id={item_id})")
                if item_id:
                    return f"{self.base_url}/web/#/details?id={item_id}"

            logger.info(f"No Jellyfin match found for '{title}' ({item_type})")
            return None

        except Exception as e:
            logger.error(f"Jellyfin search error for '{title}': {e}")
            return None

    def get_item_url(self, item_id: str) -> str:
        """Build a Jellyfin web URL from an item ID (no API call needed)."""
        return f"{self.base_url}/web/#/details?id={item_id}"
