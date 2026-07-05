"""
Custom recommendation pool construction from user-expressed constraints.

Translates a planner-extracted RecommendationPlan (genres, people, years, rating,
language) into TMDB candidate pools: a synthesized discover source for filterable
constraints, and a person-credits path for TV+people requests (TMDB /discover/tv
does not support with_people/with_cast). Falls back to, or tops up with, the
user's configured recommendation sources so the curation LLM always has enough
material. Used by the RECOMMEND handler in bot/telegram_bot.py.
"""

import logging
from datetime import date
from typing import List, Optional, Set, Tuple

from bot.models import RecommendationFilters, RecommendationPlan
from bot.recommendation_pool import (
    RecommendationSourceError,
    _enrich_genre_names,
    _is_excluded_item,
    resolve_recommendation_sources,
)

logger = logging.getLogger(__name__)


def resolve_person_ids(tmdb_client, names: List[str]) -> Tuple[List[int], List[str]]:
    """Resolve person names to TMDB person ids.

    Picks the most popular match per name, preferring actors on close calls.
    Returns (resolved_ids, unresolved_names).
    """
    resolved = []
    unresolved = []
    for name in names:
        candidates = tmdb_client.search_person(name)
        if not candidates:
            unresolved.append(name)
            continue
        best = max(
            candidates,
            key=lambda p: (p.get('popularity', 0.0), p.get('known_for_department') == 'Acting'),
        )
        logger.info("Resolved person %r -> %s (%s)", name, best['id'], best['name'])
        resolved.append(best['id'])
    if unresolved:
        logger.warning("Could not resolve people on TMDB: %s", unresolved)
    return resolved, unresolved


def resolve_genre_ids(tmdb_client, names: List[str], media_type: str) -> List[int]:
    """Resolve genre names to TMDB genre ids via the cached genre map.

    Exact lowercase match first, substring match as a safety net; unresolved
    names are dropped with a warning.
    """
    genre_map = tmdb_client.movie_genres if media_type == 'movie' else tmdb_client.tv_genres
    ids = []
    for name in names:
        key = name.strip().lower()
        if not key:
            continue
        if key in genre_map:
            ids.append(genre_map[key])
            continue
        partial = next(
            (gid for gname, gid in genre_map.items() if key in gname or gname in key),
            None,
        )
        if partial is not None:
            ids.append(partial)
        else:
            logger.warning("Could not resolve genre %r for %s", name, media_type)
    return ids


def _date_bounds(filters: RecommendationFilters, media_type: str) -> dict:
    """Map year_from/year_to to TMDB discover date range params."""
    prefix = 'primary_release_date' if media_type == 'movie' else 'first_air_date'
    params = {}
    if filters.year_from:
        params[f'{prefix}.gte'] = f'{filters.year_from}-01-01'
    if filters.year_to:
        params[f'{prefix}.lte'] = f'{filters.year_to}-12-31'
    return params


def build_custom_source(
    tmdb_client,
    filters: RecommendationFilters,
    pool_label: str,
    count: int,
) -> Optional[dict]:
    """Synthesize a discover source dict shaped like a recommendation_sources entry.

    Returns None when no constraint resolves to a usable TMDB filter (the caller
    falls back to the user's configured sources).
    """
    media_type = filters.media_type
    filter_params = {}

    if filters.people:
        if media_type != 'movie':
            raise ValueError("build_custom_source cannot handle TV people; use fetch_person_tv_group")
        person_ids, _ = resolve_person_ids(tmdb_client, filters.people)
        if not person_ids:
            # People were the point of the request; a person-less pool would mislead.
            return None
        filter_params['with_people'] = ",".join(str(i) for i in person_ids)

    if filters.genres:
        genre_ids = resolve_genre_ids(tmdb_client, filters.genres, media_type)
        if genre_ids:
            filter_params['with_genres'] = ",".join(str(i) for i in genre_ids)

    filter_params.update(_date_bounds(filters, media_type))

    if filters.min_rating:
        filter_params['vote_average.gte'] = filters.min_rating
        filter_params['vote_count.gte'] = 100

    if filters.original_language:
        filter_params['with_original_language'] = filters.original_language

    if not filter_params:
        return None

    return {
        'name': pool_label,
        'type': 'discover',
        'media_type': media_type,
        'count': count,
        'filter': filter_params,
    }


def fetch_person_tv_group(
    tmdb_client,
    filters: RecommendationFilters,
    pool_label: str,
    count: int,
    language: str,
    excluded_ids: Set[str],
    excluded_titles: Set[str],
) -> Optional[dict]:
    """Build a TV candidate group from person credits.

    /discover/tv has no with_people/with_cast, so TV+people requests intersect
    the credited shows of each requested person, then apply the remaining
    constraints (genres, years, rating) and exclusions locally.
    """
    person_ids, _ = resolve_person_ids(tmdb_client, filters.people)
    if not person_ids:
        return None

    items_by_id = None
    for person_id in person_ids:
        credits = {item['id']: item for item in tmdb_client.get_person_credits(person_id, 'tv', language)}
        items_by_id = credits if items_by_id is None else {
            i: item for i, item in items_by_id.items() if i in credits
        }
    items = sorted(items_by_id.values(), key=lambda x: x.get('popularity', 0.0), reverse=True)

    genre_ids = set(resolve_genre_ids(tmdb_client, filters.genres, 'tv')) if filters.genres else set()
    today_str = date.today().isoformat()

    selected = []
    for item in items:
        if not item.get('id') or not item.get('title') or not item.get('year'):
            continue
        if (item.get('release_date') or '') > today_str:
            continue
        if _is_excluded_item(item, excluded_ids, excluded_titles):
            continue
        if genre_ids and not genre_ids.intersection(item.get('genre_ids', [])):
            continue
        year = int(item['year'])
        if filters.year_from and year < filters.year_from:
            continue
        if filters.year_to and year > filters.year_to:
            continue
        if filters.min_rating and item.get('vote_average', 0.0) < filters.min_rating:
            continue
        selected.append(_enrich_genre_names(tmdb_client, item))
        if len(selected) >= count:
            break

    if not selected:
        return None
    return {
        'name': pool_label,
        'source_type': 'person_credits',
        'media_type': 'tv',
        'items': selected,
    }


def build_candidate_groups_for_request(
    tmdb_client,
    plan: Optional[RecommendationPlan],
    user_prefs: dict,
    language: str,
    excluded_tmdb_ids,
    excluded_titles,
    carousel_count: int,
    custom_pool_count: int,
) -> Tuple[List[dict], bool, str]:
    """Build candidate groups for a recommend request, custom-first.

    Returns (groups, is_custom_pool, media_type). When the plan carries filters,
    a custom pool leads; the user's configured sources back-fill when the custom
    pool is smaller than the carousel. Without usable filters this is exactly the
    predefined-sources behavior.
    """
    normalized_ids = {str(i) for i in (excluded_tmdb_ids or [])}
    normalized_titles = {t.lower() for t in (excluded_titles or set()) if t}

    filters = plan.filters if (plan and plan.has_filters and plan.filters) else None
    custom_groups = []
    media_type = 'movie'
    if filters:
        media_type = filters.media_type
        pool_label = plan.pool_label.strip() or 'Custom selection'
        if filters.media_type == 'tv' and filters.people:
            group = fetch_person_tv_group(
                tmdb_client, filters, pool_label, custom_pool_count,
                language, normalized_ids, normalized_titles,
            )
            custom_groups = [group] if group else []
        else:
            source = build_custom_source(tmdb_client, filters, pool_label, custom_pool_count)
            if source:
                custom_groups = tmdb_client.get_candidate_groups(
                    [source], language, excluded_tmdb_ids, excluded_titles, use_cache=False,
                )

    is_custom = bool(custom_groups)
    groups = list(custom_groups)
    custom_item_count = sum(len(g['items']) for g in custom_groups)
    if is_custom and custom_item_count >= carousel_count:
        return groups, True, media_type

    try:
        sources = resolve_recommendation_sources(user_prefs)
    except RecommendationSourceError as e:
        if is_custom:
            logger.warning("Skipping predefined top-up, sources not configured: %s", e)
            return groups, True, media_type
        raise

    predefined_groups = tmdb_client.get_candidate_groups(
        sources, language, excluded_tmdb_ids, excluded_titles,
    )
    if is_custom:
        custom_ids = {item['id'] for g in custom_groups for item in g['items']}
        for group in predefined_groups:
            deduped = [item for item in group['items'] if item['id'] not in custom_ids]
            if deduped:
                groups.append({**group, 'items': deduped})
        logger.info(
            "Custom pool %d item(s) < carousel %d; topped up with %d predefined group(s)",
            custom_item_count, carousel_count, len(groups) - len(custom_groups),
        )
    else:
        groups = predefined_groups
    return groups, is_custom, media_type
