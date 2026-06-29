"""Unit tests for recommendation pool source resolution and fetching."""

import pytest
from unittest.mock import MagicMock

from bot.recommendation_pool import (
    RecommendationSourceError,
    fetch_candidate_groups_from_sources,
    fetch_candidates_from_sources,
    get_source_name,
    resolve_recommendation_sources,
    validate_source,
)


def _make_item(item_id: int, media_type: str, title: str = "Test") -> dict:
    return {
        'id': item_id,
        'title': title,
        'original_title': title,
        'year': '2020',
        'overview': 'Overview',
        'media_type': media_type,
        'vote_average': 8.0,
        'genre_ids': [878],
        'popularity': 50.0,
    }


def _make_tmdb_client(**method_returns):
    client = MagicMock()
    client.cache_ttl = 21600
    client.candidates_cache = {}
    client.movie_genres = {'science fiction': 878}
    client.tv_genres = {'drama': 18}
    for method, return_value in method_returns.items():
        getattr(client, method).side_effect = return_value
    return client


def test_custom_sources_passed_through():
    custom = [
        {'type': 'popular', 'media_type': 'movie', 'count': 10},
        {
            'type': 'discover',
            'media_type': 'tv',
            'count': 20,
            'filter': {'with_genres': '18', 'vote_average.gte': 7.0},
        },
    ]
    sources = resolve_recommendation_sources({'recommendation_sources': custom})
    assert sources == custom


def test_missing_recommendation_sources_raises():
    with pytest.raises(RecommendationSourceError, match="recommendation_sources is required"):
        resolve_recommendation_sources({})


def test_empty_recommendation_sources_raises():
    with pytest.raises(RecommendationSourceError):
        resolve_recommendation_sources({'recommendation_sources': []})


def test_source_name_is_optional_with_generated_fallback():
    named_source = {'name': 'Cozy family picks', 'type': 'discover', 'media_type': 'movie', 'count': 5, 'filter': {'with_genres': '35'}}
    fallback_source = {'type': 'top_rated', 'media_type': 'tv', 'count': 5}

    validate_source(named_source, 0)
    validate_source(fallback_source, 1)

    assert get_source_name(named_source) == 'Cozy family picks'
    assert get_source_name(fallback_source) == 'Top rated TV shows'


def test_empty_source_name_raises():
    with pytest.raises(RecommendationSourceError, match="name must be a non-empty string"):
        validate_source({'name': '  ', 'type': 'popular', 'media_type': 'movie', 'count': 5}, 0)


def test_invalid_type_raises():
    with pytest.raises(RecommendationSourceError, match="unknown type"):
        validate_source({'type': 'trending', 'media_type': 'movie', 'count': 5}, 0)


def test_invalid_media_type_raises():
    with pytest.raises(RecommendationSourceError, match="unknown media_type"):
        validate_source({'type': 'popular', 'media_type': 'show', 'count': 5}, 0)


def test_discover_without_filter_raises():
    with pytest.raises(RecommendationSourceError, match="requires a non-empty 'filter'"):
        validate_source({'type': 'discover', 'media_type': 'movie', 'count': 5}, 0)


def test_invalid_count_raises():
    with pytest.raises(RecommendationSourceError, match="count must be a positive integer"):
        validate_source({'type': 'popular', 'media_type': 'movie', 'count': 0}, 0)


def test_invalid_sort_by_format_raises():
    with pytest.raises(RecommendationSourceError, match="sort_by must be in TMDB format"):
        validate_source({'type': 'discover', 'media_type': 'movie', 'count': 5, 'sort_by': 'invalid', 'filter': {'with_genres': '35'}}, 0)


def test_sort_by_unsupported_for_popular_raises():
    with pytest.raises(RecommendationSourceError, match="not supported for type 'popular'"):
        validate_source({'type': 'popular', 'media_type': 'movie', 'count': 5, 'sort_by': 'revenue.desc'}, 0)


def test_discover_sort_by_passed_to_client():
    client = _make_tmdb_client(
        discover=lambda **kwargs: (
            [{'id': 1, 'title': 'A', 'media_type': kwargs['media_type'], 'genre_ids': []}]
            if kwargs.get('page') == 1 else []
        ),
    )
    sources = [{
        'type': 'discover',
        'media_type': 'movie',
        'count': 1,
        'sort_by': 'vote_average.desc',
        'filter': {'with_genres': '878'},
    }]
    fetch_candidates_from_sources(client, sources, 'en', [])
    call_kwargs = client.discover.call_args[1]
    assert call_kwargs['filter_params']['sort_by'] == 'vote_average.desc'


def test_popular_sort_by_applied_locally():
    low = _make_item(1, 'movie', 'Low')
    low['vote_average'] = 5.0
    high = _make_item(2, 'movie', 'High')
    high['vote_average'] = 9.0
    client = _make_tmdb_client(
        get_popular=lambda **kwargs: [low, high] if kwargs.get('page') == 1 else [],
    )
    sources = [{
        'type': 'popular',
        'media_type': 'movie',
        'count': 2,
        'sort_by': 'vote_average.desc',
    }]
    results = fetch_candidates_from_sources(client, sources, 'en', [])
    assert [r['title'] for r in results] == ['High', 'Low']


def test_deduplication_across_sources():
    shared_item = _make_item(1, 'movie', 'Shared')
    client = _make_tmdb_client(
        get_popular=lambda **kwargs: [shared_item] if kwargs.get('page') == 1 else [],
        get_top_rated=lambda **kwargs: [shared_item] if kwargs.get('page') == 1 else [],
    )
    sources = [
        {'type': 'popular', 'media_type': 'movie', 'count': 1},
        {'type': 'top_rated', 'media_type': 'movie', 'count': 1},
    ]
    results = fetch_candidates_from_sources(client, sources, 'en', [])
    assert len(results) == 1
    assert results[0]['title'] == 'Shared'


def test_excluded_ids_filtered():
    item = _make_item(99, 'movie')
    client = _make_tmdb_client(
        get_popular=lambda **kwargs: [item] if kwargs.get('page') == 1 else [],
    )
    sources = [{'type': 'popular', 'media_type': 'movie', 'count': 1}]
    results = fetch_candidates_from_sources(client, sources, 'en', ['99'])
    assert results == []


def test_fetch_respects_source_counts_and_types():
    movie_item = _make_item(1, 'movie', 'Movie')
    tv_item = _make_item(2, 'tv', 'Show')
    client = _make_tmdb_client(
        get_popular=lambda **kwargs: (
            [movie_item] if kwargs.get('media_type') == 'movie' and kwargs.get('page') == 1 else
            [tv_item] if kwargs.get('media_type') == 'tv' and kwargs.get('page') == 1 else
            []
        ),
    )
    sources = [
        {'type': 'popular', 'media_type': 'movie', 'count': 1},
        {'type': 'popular', 'media_type': 'tv', 'count': 1},
    ]
    results = fetch_candidates_from_sources(client, sources, 'en', [])
    assert len(results) == 2
    titles = {r['title'] for r in results}
    assert titles == {'Movie', 'Show'}


def test_grouped_fetch_preserves_source_names_and_overviews():
    movie_item = _make_item(1, 'movie', 'Movie')
    movie_item['overview'] = 'Movie overview from TMDB'
    tv_item = _make_item(2, 'tv', 'Show')
    tv_item['overview'] = 'Show overview from TMDB'
    client = _make_tmdb_client(
        get_popular=lambda **kwargs: [movie_item] if kwargs.get('page') == 1 else [],
        get_top_rated=lambda **kwargs: [tv_item] if kwargs.get('page') == 1 else [],
    )
    sources = [
        {'name': 'Configured movie source', 'type': 'popular', 'media_type': 'movie', 'count': 1},
        {'type': 'top_rated', 'media_type': 'tv', 'count': 1},
    ]

    groups = fetch_candidate_groups_from_sources(client, sources, 'en', [])

    assert [group['name'] for group in groups] == ['Configured movie source', 'Top rated TV shows']
    assert groups[0]['items'][0]['overview'] == 'Movie overview from TMDB'
    assert groups[1]['items'][0]['overview'] == 'Show overview from TMDB'


def test_grouped_fetch_deduplicates_across_sources():
    shared_item = _make_item(1, 'movie', 'Shared')
    client = _make_tmdb_client(
        get_popular=lambda **kwargs: [shared_item] if kwargs.get('page') == 1 else [],
        get_top_rated=lambda **kwargs: [shared_item] if kwargs.get('page') == 1 else [],
    )
    sources = [
        {'type': 'popular', 'media_type': 'movie', 'count': 1},
        {'type': 'top_rated', 'media_type': 'movie', 'count': 1},
    ]

    groups = fetch_candidate_groups_from_sources(client, sources, 'en', [])

    assert len(groups) == 1
    assert groups[0]['name'] == 'Popular movies'
    assert groups[0]['items'][0]['title'] == 'Shared'


def test_genre_names_enriched():
    item = _make_item(1, 'movie')
    client = _make_tmdb_client(
        get_popular=lambda **kwargs: [item] if kwargs.get('page') == 1 else [],
    )
    sources = [{'type': 'popular', 'media_type': 'movie', 'count': 1}]
    results = fetch_candidates_from_sources(client, sources, 'en', [])
    assert results[0]['genres'] == 'Science Fiction'


def test_cache_hit():
    item = _make_item(1, 'movie')
    client = _make_tmdb_client(
        get_popular=lambda **kwargs: [item] if kwargs.get('page') == 1 else [],
    )
    sources = [{'type': 'popular', 'media_type': 'movie', 'count': 1}]
    fetch_candidates_from_sources(client, sources, 'en', [])
    client.get_popular.reset_mock()
    fetch_candidates_from_sources(client, sources, 'en', [])
    client.get_popular.assert_not_called()


def test_title_exclusion_with_backfill():
    excluded = _make_item(1, 'movie', 'Excluded Movie')
    valid = _make_item(2, 'movie', 'Valid Movie')

    def get_popular(**kwargs):
        if kwargs.get('page') == 1:
            return [excluded]
        if kwargs.get('page') == 2:
            return [valid]
        return []

    client = _make_tmdb_client(get_popular=get_popular)
    sources = [{'type': 'popular', 'media_type': 'movie', 'count': 1}]
    results = fetch_candidates_from_sources(
        client, sources, 'en', [], {'excluded movie'}
    )
    assert len(results) == 1
    assert results[0]['title'] == 'Valid Movie'
    assert client.get_popular.call_count == 2


def test_title_exclusion_by_original_title():
    item = _make_item(1, 'movie', 'Localized')
    item['original_title'] = 'Original Excluded'
    client = _make_tmdb_client(
        get_popular=lambda **kwargs: [item] if kwargs.get('page') == 1 else [],
    )
    sources = [{'type': 'popular', 'media_type': 'movie', 'count': 1}]
    results = fetch_candidates_from_sources(
        client, sources, 'en', [], {'original excluded'}
    )
    assert results == []


def test_combined_id_and_title_exclusion():
    by_id = _make_item(10, 'movie', 'By Id')
    by_title = _make_item(11, 'movie', 'By Title')
    client = _make_tmdb_client(
        get_popular=lambda **kwargs: [by_id, by_title] if kwargs.get('page') == 1 else [],
    )
    sources = [{'type': 'popular', 'media_type': 'movie', 'count': 2}]
    results = fetch_candidates_from_sources(
        client, sources, 'en', ['10'], {'by title'}
    )
    assert results == []


def test_quota_shortfall_when_all_excluded(caplog):
    items = [_make_item(i, 'movie', f'Movie {i}') for i in range(1, 4)]
    client = _make_tmdb_client(
        get_popular=lambda **kwargs: items if kwargs.get('page') == 1 else [],
    )
    sources = [{'type': 'popular', 'media_type': 'movie', 'count': 2}]
    excluded_titles = {item['title'].lower() for item in items}
    results = fetch_candidates_from_sources(client, sources, 'en', [], excluded_titles)
    assert results == []
    assert any('TMDB pool exhausted' in record.message for record in caplog.records)


def test_cache_bust_on_excluded_titles_change():
    item = _make_item(1, 'movie')
    client = _make_tmdb_client(
        get_popular=lambda **kwargs: [item] if kwargs.get('page') == 1 else [],
    )
    sources = [{'type': 'popular', 'media_type': 'movie', 'count': 1}]
    fetch_candidates_from_sources(client, sources, 'en', [], set())
    client.get_popular.reset_mock()
    fetch_candidates_from_sources(client, sources, 'en', [], {'other title'})
    client.get_popular.assert_called_once()
