"""Unit tests for custom recommendation pool construction from planner filters."""

from unittest.mock import MagicMock

from bot.models import RecommendationFilters, RecommendationPlan
from bot.recommendation_filters import (
    build_candidate_groups_for_request,
    build_custom_source,
    fetch_person_tv_group,
    resolve_genre_ids,
    resolve_person_ids,
)


def _make_tmdb_client():
    client = MagicMock()
    client.movie_genres = {'comedy': 35, 'science fiction': 878, 'thriller': 53}
    client.tv_genres = {'comedy': 35, 'drama': 18}
    return client


def _tv_item(item_id, title, year, popularity=10.0, vote_average=7.0, genre_ids=None):
    return {
        'id': item_id,
        'title': title,
        'original_title': title,
        'year': str(year),
        'release_date': f'{year}-05-01',
        'overview': '',
        'media_type': 'tv',
        'vote_average': vote_average,
        'vote_count': 100,
        'genre_ids': genre_ids or [18],
        'popularity': popularity,
    }


def _plan(**filter_kwargs):
    return RecommendationPlan(
        has_filters=True,
        filters=RecommendationFilters(**filter_kwargs),
        pool_label='Test pool',
    )


# ── resolve_person_ids ────────────────────────────────────────────────

def test_resolve_person_ids_prefers_popularity_then_acting():
    client = _make_tmdb_client()
    client.search_person.return_value = [
        {'id': 1, 'name': 'A Director', 'popularity': 30.0, 'known_for_department': 'Directing'},
        {'id': 2, 'name': 'A Actor', 'popularity': 30.0, 'known_for_department': 'Acting'},
        {'id': 3, 'name': 'A Nobody', 'popularity': 1.0, 'known_for_department': 'Acting'},
    ]
    resolved, unresolved = resolve_person_ids(client, ['Anne Hathaway'])
    assert resolved == [2]
    assert unresolved == []


def test_resolve_person_ids_reports_unresolved():
    client = _make_tmdb_client()
    client.search_person.return_value = []
    resolved, unresolved = resolve_person_ids(client, ['Nonexistent Person'])
    assert resolved == []
    assert unresolved == ['Nonexistent Person']


# ── resolve_genre_ids ─────────────────────────────────────────────────

def test_resolve_genre_ids_exact_and_substring():
    client = _make_tmdb_client()
    assert resolve_genre_ids(client, ['Comedy'], 'movie') == [35]
    assert resolve_genre_ids(client, ['science'], 'movie') == [878]


def test_resolve_genre_ids_drops_unresolved():
    client = _make_tmdb_client()
    assert resolve_genre_ids(client, ['Jazz'], 'movie') == []


# ── build_custom_source ───────────────────────────────────────────────

def test_build_custom_source_full_movie_mapping():
    client = _make_tmdb_client()
    client.search_person.side_effect = [
        [{'id': 1813, 'name': 'Anne Hathaway', 'popularity': 50.0, 'known_for_department': 'Acting'}],
        [{'id': 5064, 'name': 'Meryl Streep', 'popularity': 40.0, 'known_for_department': 'Acting'}],
    ]
    filters = RecommendationFilters(
        media_type='movie',
        genres=['Comedy'],
        people=['Anne Hathaway', 'Meryl Streep'],
        year_from=1990,
        year_to=1999,
        min_rating=6.5,
        original_language='en',
    )
    source = build_custom_source(client, filters, 'Label', 50)

    assert source['type'] == 'discover'
    assert source['media_type'] == 'movie'
    assert source['count'] == 50
    assert source['name'] == 'Label'
    assert source['filter'] == {
        'with_people': '1813,5064',
        'with_genres': '35',
        'primary_release_date.gte': '1990-01-01',
        'primary_release_date.lte': '1999-12-31',
        'vote_average.gte': 6.5,
        'vote_count.gte': 100,
        'with_original_language': 'en',
    }


def test_build_custom_source_none_when_people_unresolved():
    client = _make_tmdb_client()
    client.search_person.return_value = []
    filters = RecommendationFilters(media_type='movie', genres=['Comedy'], people=['Unknown Person'])
    assert build_custom_source(client, filters, 'Label', 50) is None


def test_build_custom_source_none_when_nothing_resolves():
    client = _make_tmdb_client()
    filters = RecommendationFilters(media_type='movie', genres=['Jazz'])
    assert build_custom_source(client, filters, 'Label', 50) is None


def test_build_custom_source_tv_uses_air_date_bounds():
    client = _make_tmdb_client()
    filters = RecommendationFilters(media_type='tv', genres=['Drama'], year_from=2000)
    source = build_custom_source(client, filters, 'Label', 50)
    assert source['filter'] == {'with_genres': '18', 'first_air_date.gte': '2000-01-01'}


# ── fetch_person_tv_group ─────────────────────────────────────────────

def test_fetch_person_tv_group_filters_and_caps():
    client = _make_tmdb_client()
    client.search_person.return_value = [
        {'id': 17419, 'name': 'Bryan Cranston', 'popularity': 60.0, 'known_for_department': 'Acting'},
    ]
    client.get_person_credits.return_value = [
        _tv_item(1, 'Old Show', 1985),
        _tv_item(2, 'Low Rated', 2010, vote_average=5.0),
        _tv_item(3, 'Excluded Show', 2012),
        _tv_item(4, 'Wrong Genre', 2013, genre_ids=[35]),
        _tv_item(5, 'Good Show', 2014, popularity=99.0),
        _tv_item(6, 'Another Good', 2015),
        _tv_item(7, 'Overflow', 2016),
    ]
    filters = RecommendationFilters(
        media_type='tv', people=['Bryan Cranston'], genres=['Drama'],
        year_from=2000, min_rating=6.0,
    )

    group = fetch_person_tv_group(
        client, filters, 'Cranston shows', 2, 'en',
        excluded_ids={'3'}, excluded_titles=set(),
    )

    assert group['name'] == 'Cranston shows'
    assert group['media_type'] == 'tv'
    assert group['source_type'] == 'person_credits'
    assert [item['id'] for item in group['items']] == [5, 6]


def test_fetch_person_tv_group_intersects_multiple_people():
    client = _make_tmdb_client()
    client.search_person.side_effect = [
        [{'id': 10, 'name': 'P1', 'popularity': 10.0, 'known_for_department': 'Acting'}],
        [{'id': 20, 'name': 'P2', 'popularity': 10.0, 'known_for_department': 'Acting'}],
    ]
    client.get_person_credits.side_effect = [
        [_tv_item(1, 'Shared', 2010), _tv_item(2, 'Only P1', 2011)],
        [_tv_item(1, 'Shared', 2010), _tv_item(3, 'Only P2', 2012)],
    ]
    filters = RecommendationFilters(media_type='tv', people=['P1', 'P2'])

    group = fetch_person_tv_group(client, filters, 'Both', 10, 'en', set(), set())

    assert [item['id'] for item in group['items']] == [1]


def test_fetch_person_tv_group_none_when_person_unresolved():
    client = _make_tmdb_client()
    client.search_person.return_value = []
    filters = RecommendationFilters(media_type='tv', people=['Unknown'])
    assert fetch_person_tv_group(client, filters, 'X', 10, 'en', set(), set()) is None


# ── build_candidate_groups_for_request ────────────────────────────────

PREFS = {'recommendation_sources': [
    {'type': 'popular', 'media_type': 'movie', 'count': 20},
]}


def _custom_group(items):
    return {'name': 'Test pool', 'source_type': 'discover', 'media_type': 'movie', 'items': items}


def _predefined_group(items):
    return {'name': 'Popular movies', 'source_type': 'popular', 'media_type': 'movie', 'items': items}


def _movie_items(*ids):
    return [{'id': i, 'title': f'M{i}', 'original_title': f'M{i}'} for i in ids]


def test_no_plan_uses_predefined_sources():
    client = _make_tmdb_client()
    client.get_candidate_groups.return_value = [_predefined_group(_movie_items(1, 2))]

    groups, is_custom, media_type = build_candidate_groups_for_request(
        client, None, PREFS, 'en', set(), set(), 10, 50,
    )

    assert is_custom is False
    assert media_type == 'movie'
    assert groups == [_predefined_group(_movie_items(1, 2))]
    client.get_candidate_groups.assert_called_once()


def test_custom_pool_sufficient_skips_predefined():
    client = _make_tmdb_client()
    client.get_candidate_groups.return_value = [_custom_group(_movie_items(1, 2, 3))]
    plan = _plan(media_type='movie', genres=['Comedy'])

    groups, is_custom, media_type = build_candidate_groups_for_request(
        client, plan, PREFS, 'en', set(), set(), 3, 50,
    )

    assert is_custom is True
    assert len(groups) == 1
    client.get_candidate_groups.assert_called_once()
    assert client.get_candidate_groups.call_args[1]['use_cache'] is False


def test_custom_pool_short_tops_up_with_deduped_predefined():
    client = _make_tmdb_client()
    client.get_candidate_groups.side_effect = [
        [_custom_group(_movie_items(1, 2))],
        [_predefined_group(_movie_items(2, 3, 4))],
    ]
    plan = _plan(media_type='movie', genres=['Comedy'])

    groups, is_custom, _ = build_candidate_groups_for_request(
        client, plan, PREFS, 'en', set(), set(), 5, 50,
    )

    assert is_custom is True
    assert [item['id'] for item in groups[0]['items']] == [1, 2]
    assert [item['id'] for item in groups[1]['items']] == [3, 4]


def test_unusable_filters_fall_back_to_predefined():
    client = _make_tmdb_client()
    client.get_candidate_groups.return_value = [_predefined_group(_movie_items(7))]
    plan = _plan(media_type='movie', genres=['Jazz'])  # unresolvable genre

    groups, is_custom, _ = build_candidate_groups_for_request(
        client, plan, PREFS, 'en', set(), set(), 10, 50,
    )

    assert is_custom is False
    assert groups == [_predefined_group(_movie_items(7))]


def test_custom_pool_survives_missing_predefined_sources():
    client = _make_tmdb_client()
    client.get_candidate_groups.return_value = [_custom_group(_movie_items(1))]
    plan = _plan(media_type='movie', genres=['Comedy'])

    groups, is_custom, _ = build_candidate_groups_for_request(
        client, plan, {}, 'en', set(), set(), 10, 50,
    )

    assert is_custom is True
    assert len(groups) == 1


def test_tv_people_plan_returns_series_media_type():
    client = _make_tmdb_client()
    client.search_person.return_value = [
        {'id': 17419, 'name': 'Bryan Cranston', 'popularity': 60.0, 'known_for_department': 'Acting'},
    ]
    client.get_person_credits.return_value = [_tv_item(i, f'Show {i}', 2010 + i) for i in range(1, 12)]
    plan = _plan(media_type='tv', people=['Bryan Cranston'])

    groups, is_custom, media_type = build_candidate_groups_for_request(
        client, plan, PREFS, 'en', set(), set(), 10, 50,
    )

    assert is_custom is True
    assert media_type == 'tv'
    assert groups[0]['source_type'] == 'person_credits'
    assert len(groups[0]['items']) == 11
    client.get_candidate_groups.assert_not_called()
