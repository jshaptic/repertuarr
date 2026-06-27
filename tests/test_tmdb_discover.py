"""Unit tests for TMDB discover pass-through filters."""

from datetime import date
from unittest.mock import MagicMock, patch

from bot.tmdb import TmdbClient


def _make_client():
    client = TmdbClient("test-token")
    client.db = None
    return client


def _mock_discover_request(client):
    mock_response = MagicMock()
    mock_response.json.return_value = {'results': []}
    mock_response.raise_for_status = MagicMock()
    return patch.object(client, '_make_request', return_value=mock_response)


@patch('bot.tmdb.date')
def test_discover_passes_filter_params_to_api(mock_date):
    mock_date.today.return_value = date(2026, 6, 27)
    client = _make_client()
    filter_params = {
        'with_genres': '878,53',
        'with_keywords': '4565|9887',
        'vote_average.gte': 6.5,
        'primary_release_date.gte': '2000-01-01',
    }

    with _mock_discover_request(client) as mock_request:
        client.discover(filter_params, 'en', 'movie', page=2)

    mock_request.assert_called_once()
    url, = mock_request.call_args[0]
    params = mock_request.call_args[1]['params']

    assert url.endswith('/discover/movie')
    assert params['with_genres'] == '878,53'
    assert params['with_keywords'] == '4565|9887'
    assert params['vote_average.gte'] == 6.5
    assert params['primary_release_date.gte'] == '2000-01-01'
    assert params['primary_release_date.lte'] == '2026-06-27'
    assert params['language'] == 'en'
    assert params['page'] == 2
    assert params['include_adult'] == 'false'
    assert params['sort_by'] == 'popularity.desc'


@patch('bot.tmdb.date')
def test_discover_adds_primary_release_date_lte_when_missing(mock_date):
    mock_date.today.return_value = date(2026, 6, 27)
    client = _make_client()

    with _mock_discover_request(client) as mock_request:
        client.discover({'with_genres': '35'}, 'en', 'movie')

    params = mock_request.call_args[1]['params']
    assert params['primary_release_date.lte'] == '2026-06-27'


@patch('bot.tmdb.date')
def test_discover_keeps_existing_primary_release_date_lte(mock_date):
    mock_date.today.return_value = date(2026, 6, 27)
    client = _make_client()

    with _mock_discover_request(client) as mock_request:
        client.discover({'primary_release_date.lte': '2010-12-31'}, 'en', 'movie')

    params = mock_request.call_args[1]['params']
    assert params['primary_release_date.lte'] == '2010-12-31'


@patch('bot.tmdb.date')
def test_discover_adds_first_air_date_lte_for_tv(mock_date):
    mock_date.today.return_value = date(2026, 6, 27)
    client = _make_client()

    with _mock_discover_request(client) as mock_request:
        client.discover({'with_genres': '18'}, 'en', 'tv')

    params = mock_request.call_args[1]['params']
    assert params['first_air_date.lte'] == '2026-06-27'
    assert 'primary_release_date.lte' not in params


def test_discover_sort_by_in_filter_params():
    client = _make_client()
    filter_params = {'with_genres': '35', 'sort_by': 'popularity.desc'}

    mock_response = MagicMock()
    mock_response.json.return_value = {'results': []}
    mock_response.raise_for_status = MagicMock()

    with patch.object(client, '_make_request', return_value=mock_response) as mock_request:
        client.discover(filter_params, 'en', 'movie')

    params = mock_request.call_args[1]['params']
    assert params['sort_by'] == 'popularity.desc'


def test_discover_allows_sort_by_override():
    client = _make_client()
    filter_params = {'sort_by': 'vote_average.desc', 'with_genres': '35'}

    mock_response = MagicMock()
    mock_response.json.return_value = {'results': []}
    mock_response.raise_for_status = MagicMock()

    with patch.object(client, '_make_request', return_value=mock_response) as mock_request:
        client.discover(filter_params, 'ru', 'tv')

    params = mock_request.call_args[1]['params']
    assert params['sort_by'] == 'vote_average.desc'
    assert mock_request.call_args[0][0].endswith('/discover/tv')


def test_discover_empty_filter_returns_empty():
    client = _make_client()
    assert client.discover({}, 'en', 'movie') == []
