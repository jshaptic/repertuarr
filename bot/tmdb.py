import logging
import requests
import json
import hashlib
import time
from typing import Dict, List, Optional, Any

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
        self.keyword_cache: Dict[str, int] = {}
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
                    error=error_msg
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
        
    def _resolve_keywords(self, keyword_names: List[str]) -> List[int]:
        """Resolve a list of keyword names to TMDB keyword IDs."""
        resolved_ids = []
        for kw in keyword_names:
            kw_lower = kw.lower()
            if kw_lower in self.keyword_cache:
                resolved_ids.append(self.keyword_cache[kw_lower])
                continue
                
            # Search TMDB for keyword
            url = f"{self.base_url}/search/keyword"
            params = {"query": kw, "page": 1}
            try:
                resp = self._make_request(url, params=params, timeout=5)
                results = resp.json().get('results', [])
                if results:
                    # Take the first exact match, or just the first result
                    best_match = next((r for r in results if r['name'].lower() == kw_lower), results[0])
                    self.keyword_cache[kw_lower] = best_match['id']
                    resolved_ids.append(best_match['id'])
                else:
                    logger.warning(f"TMDB keyword not found: {kw}")
            except Exception as e:
                logger.error(f"Error resolving TMDB keyword '{kw}': {e}")
                
        return resolved_ids

    def _map_items(self, items: List[dict], media_type: str) -> List[dict]:
        """Map TMDB response to a unified format."""
        mapped = []
        for item in items:
            mapped.append({
                'id': item.get('id'),
                'title': item.get('title') if media_type == 'movie' else item.get('name'),
                'original_title': item.get('original_title') if media_type == 'movie' else item.get('original_name'),
                'year': item.get('release_date', '')[:4] if media_type == 'movie' else item.get('first_air_date', '')[:4],
                'overview': item.get('overview', ''),
                'media_type': media_type,
                'vote_average': item.get('vote_average', 0.0),
                'genre_ids': item.get('genre_ids', []),
                'popularity': item.get('popularity', 0.0)
            })
        return mapped

    def discover(self, filter_config: dict, language: str, media_type: str, page: int = 1) -> List[dict]:
        """Discover items based on filter config."""
        if not filter_config:
            return []
            
        endpoint = "movie" if media_type == 'movie' else "tv"
        url = f"{self.base_url}/discover/{endpoint}"
        
        # Build params
        params = {
            "language": language,
            "sort_by": "popularity.desc",
            "include_adult": "false"
        }
        
        # Genres
        genres = filter_config.get('genres', [])
        if genres:
            genre_map = self.movie_genres if media_type == 'movie' else self.tv_genres
            genre_ids = []
            for g in genres:
                gid = genre_map.get(g.lower())
                if gid:
                    genre_ids.append(str(gid))
                else:
                    logger.warning(f"Unknown TMDB {media_type} genre: {g}")
            if genre_ids:
                params["with_genres"] = ",".join(genre_ids) # AND
                
        # Keywords
        keywords = filter_config.get('keywords', [])
        if keywords:
            keyword_ids = self._resolve_keywords(keywords)
            if keyword_ids:
                params["with_keywords"] = "|".join(map(str, keyword_ids)) # OR for keywords to broaden search
                
        # Year
        year_from = filter_config.get('year_from')
        if year_from:
            if media_type == 'movie':
                params["primary_release_date.gte"] = f"{year_from}-01-01"
            else:
                params["first_air_date.gte"] = f"{year_from}-01-01"
                
        year_to = filter_config.get('year_to')
        if year_to:
            if media_type == 'movie':
                params["primary_release_date.lte"] = f"{year_to}-12-31"
            else:
                params["first_air_date.lte"] = f"{year_to}-12-31"
                
        # Original Language
        orig_lang = filter_config.get('original_language')
        if orig_lang:
            if isinstance(orig_lang, list):
                params["with_original_language"] = "|".join(orig_lang)
            else:
                params["with_original_language"] = orig_lang
            
        # Votes
        vote_avg = filter_config.get('vote_average_min')
        if vote_avg is not None:
            params["vote_average.gte"] = vote_avg
            
        vote_count = filter_config.get('vote_count_min')
        if vote_count is not None:
            params["vote_count.gte"] = vote_count
            
        params["page"] = page
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

    def get_candidates(self, filter_config: dict, language: str, excluded_tmdb_ids: list = None) -> List[dict]:
        """Orchestrator to get a combined pool of candidates."""
        excluded_ids = set(excluded_tmdb_ids or [])
        
        # Check cache
        excluded_hash = hashlib.md5(",".join(sorted(excluded_ids)).encode('utf-8')).hexdigest()
        cache_key_str = json.dumps(filter_config, sort_keys=True) + language + excluded_hash
        cache_key = hashlib.md5(cache_key_str.encode('utf-8')).hexdigest()
        
        if cache_key in self.candidates_cache:
            timestamp, data = self.candidates_cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                logger.info("Returning TMDB candidates from cache.")
                return data
                
        logger.info("Fetching fresh TMDB candidates...")
        
        combined_items = []
        seen = set()
        
        def fetch_until_quota(fetch_func, target_count: int, **kwargs):
            results = []
            for p in range(1, 6): # max 5 pages
                if len(results) >= target_count:
                    break
                items = fetch_func(page=p, **kwargs)
                if not items:
                    break
                for item in items:
                    if str(item.get('id')) not in excluded_ids and item.get('id') and item.get('title'):
                        # deduplicate globally
                        key = (item['media_type'], item['id'])
                        if key not in seen:
                            seen.add(key)
                            results.append(item)
                            if len(results) >= target_count:
                                break
            return results
            
        # Add popular and top rated
        combined_items.extend(fetch_until_quota(self.get_popular, 8, language=language, media_type='movie'))
        combined_items.extend(fetch_until_quota(self.get_popular, 7, language=language, media_type='tv'))
        
        combined_items.extend(fetch_until_quota(self.get_top_rated, 8, language=language, media_type='movie'))
        combined_items.extend(fetch_until_quota(self.get_top_rated, 7, language=language, media_type='tv'))
        
        # Discover with filters
        if filter_config:
            combined_items.extend(fetch_until_quota(self.discover, 35, filter_config=filter_config, language=language, media_type='movie'))
            combined_items.extend(fetch_until_quota(self.discover, 35, filter_config=filter_config, language=language, media_type='tv'))
            
        unique_items = []
        for item in combined_items:
            # Map genre names for display in prompt
            genre_names = []
            genre_map_inv = {v: k for k, v in (self.movie_genres.items() if item['media_type'] == 'movie' else self.tv_genres.items())}
            for gid in item.get('genre_ids', []):
                if gid in genre_map_inv:
                    genre_names.append(genre_map_inv[gid].title())
            
            item['genres'] = ", ".join(genre_names) if genre_names else "Unknown"
            unique_items.append(item)
                
        # Sort by popularity or vote average (combining the two heuristically)
        unique_items.sort(key=lambda x: (x.get('vote_average', 0) * 10) + x.get('popularity', 0), reverse=True)
        
        logger.info(f"TMDB fetched {len(unique_items)} unique candidates.")
        
        # Save to cache
        self.candidates_cache[cache_key] = (time.time(), unique_items)
        
        return unique_items
