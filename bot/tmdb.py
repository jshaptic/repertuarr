"""
TMDB API client for media discovery and candidate fetching.

Provides low-level access to TMDB discover, popular, and top_rated endpoints.
Candidate pool orchestration lives in bot/recommendation_pool.py.
"""

import logging
import requests
import time
from datetime import date
from typing import Dict, List, Optional

from bot.session_context import get_session_id

logger = logging.getLogger(__name__)

class TmdbClient:
    def __init__(self, bearer_token: str, cache_ttl_seconds: int = 21600): # 6 hours default TTL
        self.bearer_token = bearer_token
        self.base_url = "https://api.themoviedb.org/3"
        self.headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.bearer_token}"
        }
        self.cache_ttl = cache_ttl_seconds
        
        # Caches
        self.movie_genres: Dict[str, int] = {}
        self.tv_genres: Dict[str, int] = {}
        self.candidates_cache: Dict[str, tuple[float, List[dict]]] = {} # hash -> (timestamp, data)
        self.db = None # Will be set by main app for logging

    def _make_request(self, url: str, params: dict, timeout: int = 10) -> requests.Response:
        logger.info(f"TMDB Request: GET {url} params={params}")
        start_time = time.time()
        error_msg = None
        status_code = None
        response_body = None
        try:
            resp = requests.get(url, headers=self.headers, params=params, timeout=timeout)
            status_code = resp.status_code
            response_body = resp.text
            resp.raise_for_status()
            return resp
        except Exception as e:
            error_msg = str(e)
            raise
        finally:
            duration_ms = int((time.time() - start_time) * 1000)
            if self.db:
                endpoint = url.replace(self.base_url, "")
                self.db.log_tmdb_request(
                    endpoint=endpoint,
                    params=params,
                    duration_ms=duration_ms,
                    status_code=status_code,
                    response_body=response_body,
                    error=error_msg,
                    session_id=get_session_id(),
                )
        
    def initialize(self):
        """Fetch genre lists on startup."""
        logger.info("Initializing TMDB Client and fetching genres...")
        try:
            self._fetch_genres('movie')
            self._fetch_genres('tv')
        except Exception as e:
            logger.error(f"Failed to initialize TMDB Client: {e}")
            
    def _fetch_genres(self, media_type: str):
        url = f"{self.base_url}/genre/{media_type}/list"
        params = {"language": "en"}
        resp = self._make_request(url, params=params, timeout=10)
        
        genres_data = resp.json().get('genres', [])
        mapping = {g['name'].lower(): g['id'] for g in genres_data}
        
        if media_type == 'movie':
            self.movie_genres = mapping
        else:
            self.tv_genres = mapping
            
        logger.info(f"Fetched {len(mapping)} {media_type} genres from TMDB.")

    def _map_items(self, items: List[dict], media_type: str) -> List[dict]:
        """Map TMDB response to a unified format."""
        mapped = []
        for item in items:
            mapped.append({
                'id': item.get('id'),
                'title': item.get('title') if media_type == 'movie' else item.get('name'),
                'original_title': item.get('original_title') if media_type == 'movie' else item.get('original_name'),
                'year': item.get('release_date', '')[:4] if media_type == 'movie' else item.get('first_air_date', '')[:4],
                'release_date': item.get('release_date') if media_type == 'movie' else item.get('first_air_date'),
                'overview': item.get('overview', ''),
                'media_type': media_type,
                'vote_average': item.get('vote_average', 0.0),
                'vote_count': item.get('vote_count', 0),
                'genre_ids': item.get('genre_ids', []),
                'popularity': item.get('popularity', 0.0)
            })
        return mapped

    def _apply_released_only_filter(self, params: dict, media_type: str, today: Optional[date] = None) -> None:
        """
        Exclude unreleased titles by capping the release date at today.

        TMDB has no dedicated unreleased flag; primary_release_date.lte / first_air_date.lte
        is the standard approach. Skipped when the caller already set the .lte bound.
        """
        today_str = (today or date.today()).isoformat()
        if media_type == 'movie':
            if 'primary_release_date.lte' not in params:
                params['primary_release_date.lte'] = today_str
        elif 'first_air_date.lte' not in params:
            params['first_air_date.lte'] = today_str

    def discover(self, filter_params: dict, language: str, media_type: str, page: int = 1) -> List[dict]:
        """
        Discover items using TMDB API query parameters passed through from config.

        Filter keys and values follow TMDB discover syntax, e.g.:
          with_genres: "878,53"           (AND, comma-separated IDs)
          with_keywords: "4565|9887"      (OR, pipe-separated IDs)
          vote_average.gte: 6.5
          primary_release_date.gte: "2000-01-01"

        Unreleased titles are excluded automatically via primary_release_date.lte /
        first_air_date.lte set to today when not provided in the filter.
        """
        if not filter_params:
            return []

        endpoint = "movie" if media_type == 'movie' else "tv"
        url = f"{self.base_url}/discover/{endpoint}"

        params = dict(filter_params)
        params["language"] = language
        params["page"] = page
        if "include_adult" not in params:
            params["include_adult"] = "false"
        if "sort_by" not in params:
            params["sort_by"] = "popularity.desc"
        self._apply_released_only_filter(params, media_type)

        try:
            resp = self._make_request(url, params=params, timeout=10)
            results = resp.json().get('results', [])
            return self._map_items(results, media_type)
        except Exception as e:
            logger.error(f"Error discovering {media_type}s on page {page}: {e}")
            return []

    def get_popular(self, language: str, media_type: str, page: int = 1) -> List[dict]:
        endpoint = "movie" if media_type == 'movie' else "tv"
        url = f"{self.base_url}/{endpoint}/popular"
        
        params = {"language": language, "page": page}
        try:
            resp = self._make_request(url, params=params, timeout=10)
            results = resp.json().get('results', [])
            return self._map_items(results, media_type)
        except Exception as e:
            logger.error(f"Error fetching popular {media_type}s: {e}")
            return []
        
    def get_top_rated(self, language: str, media_type: str, page: int = 1) -> List[dict]:
        endpoint = "movie" if media_type == 'movie' else "tv"
        url = f"{self.base_url}/{endpoint}/top_rated"
        
        params = {"language": language, "page": page}
        try:
            resp = self._make_request(url, params=params, timeout=10)
            results = resp.json().get('results', [])
            return self._map_items(results, media_type)
        except Exception as e:
            logger.error(f"Error fetching top rated {media_type}s: {e}")
            return []

    def get_candidates(self, sources: list, language: str, excluded_tmdb_ids: list = None) -> List[dict]:
        """Fetch combined candidate pool from configured recommendation sources."""
        from bot.recommendation_pool import fetch_candidates_from_sources

        return fetch_candidates_from_sources(self, sources, language, excluded_tmdb_ids)

    def get_candidate_groups(self, sources: list, language: str, excluded_tmdb_ids: list = None) -> List[dict]:
        """Fetch candidate pool grouped by configured recommendation source."""
        from bot.recommendation_pool import fetch_candidate_groups_from_sources

        return fetch_candidate_groups_from_sources(self, sources, language, excluded_tmdb_ids)
