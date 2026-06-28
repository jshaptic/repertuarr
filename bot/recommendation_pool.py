"""
Recommendation candidate pool orchestration for TMDB.

Resolves per-user recommendation_sources config, validates source entries,
and fetches/deduplicates candidates from popular, top_rated, and discover endpoints.
Discover filters use TMDB API query parameter names and syntax directly.
"""

import hashlib
import json
import logging
import time
from typing import Any, Callable, List, Optional, Set

logger = logging.getLogger(__name__)

VALID_SOURCE_TYPES = frozenset({'popular', 'top_rated', 'discover'})
VALID_MEDIA_TYPES = frozenset({'movie', 'tv'})
SOURCE_TYPE_LABELS = {
    'popular': 'Popular',
    'top_rated': 'Top rated',
    'discover': 'Discover',
}
MEDIA_TYPE_LABELS = {
    'movie': 'movies',
    'tv': 'TV shows',
}
LOCAL_SORT_FIELDS = {
    'popularity': 'popularity',
    'vote_average': 'vote_average',
    'vote_count': 'vote_count',
    'release_date': 'release_date',
    'primary_release_date': 'release_date',
    'first_air_date': 'release_date',
}


class RecommendationSourceError(ValueError):
    """Invalid recommendation_sources configuration."""


def validate_source(source: dict, index: int) -> None:
    """Validate a single recommendation source entry."""
    prefix = f"recommendation_sources[{index}]"

    name = source.get('name')
    if name is not None and (not isinstance(name, str) or not name.strip()):
        raise RecommendationSourceError(f"{prefix}: name must be a non-empty string when provided")

    source_type = source.get('type')
    if source_type not in VALID_SOURCE_TYPES:
        raise RecommendationSourceError(
            f"{prefix}: unknown type {source_type!r}; expected one of {sorted(VALID_SOURCE_TYPES)}"
        )

    media_type = source.get('media_type')
    if media_type not in VALID_MEDIA_TYPES:
        raise RecommendationSourceError(
            f"{prefix}: unknown media_type {media_type!r}; expected 'movie' or 'tv'"
        )

    count = source.get('count')
    if not isinstance(count, int) or count <= 0:
        raise RecommendationSourceError(f"{prefix}: count must be a positive integer, got {count!r}")

    if source_type == 'discover':
        filter_params = source.get('filter')
        if not filter_params or not isinstance(filter_params, dict):
            raise RecommendationSourceError(f"{prefix}: discover source requires a non-empty 'filter' dict")

    sort_by = source.get('sort_by')
    if sort_by is not None:
        if not isinstance(sort_by, str) or not sort_by.strip():
            raise RecommendationSourceError(f"{prefix}: sort_by must be a non-empty string")
        _validate_sort_by(sort_by, source_type, prefix)


def get_source_name(source: dict) -> str:
    """Return configured source name or a readable generated fallback."""
    name = source.get('name')
    if isinstance(name, str) and name.strip():
        return name.strip()

    source_type = SOURCE_TYPE_LABELS[source['type']]
    media_type = MEDIA_TYPE_LABELS[source['media_type']]
    return f"{source_type} {media_type}"


def _validate_sort_by(sort_by: str, source_type: str, prefix: str) -> None:
    """Validate sort_by format; non-discover sources must use locally sortable fields."""
    if '.' not in sort_by:
        raise RecommendationSourceError(
            f"{prefix}: sort_by must be in TMDB format, e.g. 'popularity.desc' or 'vote_average.asc'"
        )
    field, direction = sort_by.rsplit('.', 1)
    if direction not in ('desc', 'asc'):
        raise RecommendationSourceError(
            f"{prefix}: sort_by direction must be 'desc' or 'asc', got {direction!r}"
        )
    if source_type != 'discover' and field not in LOCAL_SORT_FIELDS:
        raise RecommendationSourceError(
            f"{prefix}: sort_by field {field!r} is not supported for type {source_type!r}; "
            f"use one of {sorted(LOCAL_SORT_FIELDS)}"
        )


def resolve_recommendation_sources(user_prefs: dict) -> List[dict]:
    """Resolve recommendation sources from user preferences."""
    if 'recommendation_sources' not in user_prefs:
        raise RecommendationSourceError("preferences.recommendation_sources is required")

    sources = user_prefs['recommendation_sources']
    if not isinstance(sources, list) or not sources:
        raise RecommendationSourceError("recommendation_sources must be a non-empty list")

    for i, source in enumerate(sources):
        validate_source(source, i)
    return sources


def _fetch_until_quota(
    fetch_func: Callable,
    target_count: int,
    excluded_ids: Set[str],
    seen: Set[tuple],
    **kwargs,
) -> List[dict]:
    """Fetch pages until target_count unique, non-excluded items are collected."""
    results = []
    for page in range(1, 6):
        if len(results) >= target_count:
            break
        items = fetch_func(page=page, **kwargs)
        if not items:
            break
        for item in items:
            if str(item.get('id')) in excluded_ids or not item.get('id') or not item.get('title'):
                continue
            key = (item['media_type'], item['id'])
            if key in seen:
                continue
            seen.add(key)
            results.append(item)
            if len(results) >= target_count:
                break
    return results


def _sort_items(items: List[dict], sort_by: str) -> List[dict]:
    """Sort fetched items locally (for popular/top_rated sources)."""
    field, direction = sort_by.rsplit('.', 1)
    key_field = LOCAL_SORT_FIELDS[field]
    reverse = direction == 'desc'

    def sort_key(item: dict):
        val = item.get(key_field)
        if val is None or val == '':
            return (1, '')
        return (0, val)

    return sorted(items, key=sort_key, reverse=reverse)


def _enrich_genre_names(tmdb_client, item: dict) -> dict:
    """Add human-readable genre names for LLM prompt display."""
    genre_names = []
    genre_map = tmdb_client.movie_genres if item['media_type'] == 'movie' else tmdb_client.tv_genres
    genre_map_inv = {v: k for k, v in genre_map.items()}
    for gid in item.get('genre_ids', []):
        if gid in genre_map_inv:
            genre_names.append(genre_map_inv[gid].title())
    item['genres'] = ", ".join(genre_names) if genre_names else "Unknown"
    return item


def _fetch_from_source(tmdb_client, source: dict, language: str, excluded_ids: Set[str], seen: Set[tuple]) -> List[dict]:
    """Fetch candidates for a single configured source."""
    source_type = source['type']
    media_type = source['media_type']
    count = source['count']

    if source_type == 'popular':
        fetch_func = tmdb_client.get_popular
        kwargs = {'language': language, 'media_type': media_type}
    elif source_type == 'top_rated':
        fetch_func = tmdb_client.get_top_rated
        kwargs = {'language': language, 'media_type': media_type}
    else:
        fetch_func = tmdb_client.discover
        filter_params = dict(source['filter'])
        if source.get('sort_by'):
            filter_params['sort_by'] = source['sort_by']
        kwargs = {
            'filter_params': filter_params,
            'language': language,
            'media_type': media_type,
        }

    items = _fetch_until_quota(fetch_func, count, excluded_ids, seen, **kwargs)
    sort_by = source.get('sort_by')
    if sort_by and source_type != 'discover':
        items = _sort_items(items, sort_by)
    return items


def _build_cache_key(sources: List[dict], language: str, excluded_ids: Set[str], mode: str) -> str:
    """Build a stable cache key for a candidate fetch shape."""
    excluded_hash = hashlib.md5(",".join(sorted(excluded_ids)).encode('utf-8')).hexdigest()
    cache_key_str = json.dumps(sources, sort_keys=True) + language + excluded_hash + mode
    return hashlib.md5(cache_key_str.encode('utf-8')).hexdigest()


def fetch_candidate_groups_from_sources(
    tmdb_client,
    sources: List[dict],
    language: str,
    excluded_tmdb_ids: Optional[List[Any]] = None,
) -> List[dict]:
    """Fetch TMDB candidates grouped by configured recommendation source."""
    excluded_ids = {str(i) for i in (excluded_tmdb_ids or [])}
    cache_key = _build_cache_key(sources, language, excluded_ids, 'groups')
    if cache_key in tmdb_client.candidates_cache:
        timestamp, data = tmdb_client.candidates_cache[cache_key]
        if time.time() - timestamp < tmdb_client.cache_ttl:
            logger.info("Returning grouped TMDB candidates from cache.")
            return data

    logger.info("Fetching fresh TMDB candidates from %d source(s)...", len(sources))

    groups = []
    seen: Set[tuple] = set()

    for source in sources:
        items = _fetch_from_source(tmdb_client, source, language, excluded_ids, seen)
        enriched_items = [_enrich_genre_names(tmdb_client, item) for item in items]
        if enriched_items:
            groups.append({
                'name': get_source_name(source),
                'source_type': source['type'],
                'media_type': source['media_type'],
                'items': enriched_items,
            })

    total_items = sum(len(group['items']) for group in groups)
    logger.info("TMDB fetched %d unique candidates in %d group(s).", total_items, len(groups))
    tmdb_client.candidates_cache[cache_key] = (time.time(), groups)
    return groups


def fetch_candidates_from_sources(
    tmdb_client,
    sources: List[dict],
    language: str,
    excluded_tmdb_ids: Optional[List[Any]] = None,
) -> List[dict]:
    """Fetch and combine TMDB candidates from configured recommendation sources."""
    groups = fetch_candidate_groups_from_sources(tmdb_client, sources, language, excluded_tmdb_ids)
    unique_items = [item for group in groups for item in group['items']]
    unique_items.sort(
        key=lambda x: (x.get('vote_average', 0) * 10) + x.get('popularity', 0),
        reverse=True,
    )

    logger.info("TMDB fetched %d unique candidates.", len(unique_items))
    return unique_items
