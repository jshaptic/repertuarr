"""
ADD_MEDIA helpers: normalize intent slots and resolve Arr best matches.

Keeps title-list normalization and Radarr/Sonarr lookup selection out of
telegram_bot.py so multi-title and URL flows stay modular.
"""

import logging
from typing import Any, Callable, List, Optional, Tuple

from bot.arr_add import arr_service
from bot.models import AddMediaItem, IntentResponse
from bot.service_request import make_service_request

logger = logging.getLogger(__name__)

UNRELEASED_STATUSES = frozenset({'announced', 'upcoming', 'tba'})


def normalize_add_items(intent: IntentResponse) -> List[AddMediaItem]:
    """Prefer `titles`; fall back to legacy single `title` + top-level media_type."""
    if intent.titles:
        return [
            AddMediaItem(title=item.title.strip(), media_type=item.media_type)
            for item in intent.titles
            if item.title and item.title.strip()
        ]
    if intent.title and intent.title.strip():
        return [AddMediaItem(title=intent.title.strip(), media_type=intent.media_type)]
    return []


def cap_add_items(items: List[AddMediaItem], max_titles: int) -> List[AddMediaItem]:
    """Truncate to the configured title cap, preserving order."""
    if max_titles <= 0:
        raise ValueError("max_titles must be a positive integer")
    return items[:max_titles]


def filter_released_results(results: List[dict]) -> List[dict]:
    """Drop announced/upcoming/tba Arr lookup rows."""
    filtered = []
    for item in results:
        status = (item.get('status') or '').lower()
        if status in UNRELEASED_STATUSES:
            continue
        filtered.append(item)
    return filtered


def pick_best_match(results: List[dict]) -> Optional[dict]:
    """Pick the highest-popularity released candidate from Arr lookup results."""
    filtered = filter_released_results(results)
    if not filtered:
        return None
    filtered.sort(key=lambda x: x.get('popularity', 0) or 0, reverse=True)
    return filtered[0]


def lookup_best_match(
    db,
    title: str,
    media_type: str,
    base_url: str,
    api_key: str,
    *,
    make_request: Callable = make_service_request,
) -> Optional[dict]:
    """Look up a title in Arr and return the best released match, or None."""
    endpoint = "movie" if media_type == "movie" else "series"
    lookup_endpoint = f"{base_url}/api/v3/{endpoint}/lookup"
    logger.info("Best-match lookup: %s term=%s", lookup_endpoint, title)
    resp = make_request(
        db,
        arr_service(media_type),
        'GET',
        lookup_endpoint,
        headers={'X-Api-Key': api_key},
        params={'term': title},
    )
    resp.raise_for_status()
    results = resp.json()
    if not results:
        return None
    return pick_best_match(results)


def resolve_add_candidates(
    db,
    items: List[AddMediaItem],
    resolve_arr: Callable[[dict, str], Tuple[Optional[str], Optional[str]]],
    user_info: dict,
    *,
    make_request: Callable = make_service_request,
) -> Tuple[List[dict], List[str], List[str]]:
    """Resolve each item to an Arr dict.

    Returns (resolved_items, miss_titles, config_errors) where config_errors
    are human-readable messages when Radarr/Sonarr is missing for a type.
    """
    resolved: List[dict] = []
    misses: List[str] = []
    config_errors: List[str] = []
    seen_keys = set()

    for item in items:
        base_url, api_key = resolve_arr(user_info, item.media_type)
        if not base_url:
            label = 'Radarr' if item.media_type == 'movie' else 'Sonarr'
            msg = f"{label} not configured for '{item.title}'"
            if msg not in config_errors:
                config_errors.append(msg)
            misses.append(item.title)
            continue

        match = lookup_best_match(
            db, item.title, item.media_type, base_url, api_key, make_request=make_request,
        )
        if not match:
            misses.append(item.title)
            continue

        # Tag media type for mixed-batch carousels / ADD_ALL.
        match = dict(match)
        match['_batch_media_type'] = item.media_type
        id_key = (
            match.get('tmdbId') if item.media_type == 'movie' else match.get('tvdbId')
        )
        dedupe_key = (item.media_type, id_key or item.title.lower())
        if dedupe_key in seen_keys:
            continue
        seen_keys.add(dedupe_key)
        resolved.append(match)

    return resolved, misses, config_errors


def provider_id_for_item(item: dict, media_type: str) -> Optional[Any]:
    """Return tmdbId or tvdbId for an Arr/carousel item dict."""
    if media_type == 'movie':
        return item.get('tmdbId')
    return item.get('tvdbId')


def is_item_already_available(item: dict, media_type: str, media_server_client=None) -> bool:
    """True when the title is on the media server or already managed in Arr."""
    id_val = provider_id_for_item(item, media_type)
    if id_val and media_server_client:
        title = item.get('_display_title') or item.get('title') or ''
        tmdb_id = str(id_val) if media_type == 'movie' else None
        tvdb_id = str(id_val) if media_type == 'series' else None
        if media_server_client.search_item(
            title, media_type, tmdb_id=tmdb_id, tvdb_id=tvdb_id,
        ):
            return True
    if item.get('id', 0) > 0:
        return True
    return False
