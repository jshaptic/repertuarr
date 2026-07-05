"""Unit tests for TMDB search_person, search_media, and get_person_credits."""

from unittest.mock import MagicMock, patch

from bot.tmdb import TmdbClient


def _make_client():
    client = TmdbClient("test-token")
    client.db = None
    return client


def _mock_request(client, payload):
    mock_response = MagicMock()
    mock_response.json.return_value = payload
    mock_response.raise_for_status = MagicMock()
    return patch.object(client, '_make_request', return_value=mock_response)


def test_search_person_passes_params_and_maps_fields():
    client = _make_client()
    payload = {'results': [
        {'id': 1813, 'name': 'Anne Hathaway', 'popularity': 55.2, 'known_for_department': 'Acting'},
        {'id': 99, 'popularity': 1.0},  # missing optional fields default
    ]}

    with _mock_request(client, payload) as mock_request:
        results = client.search_person("Anne Hathaway")

    url, = mock_request.call_args[0]
    params = mock_request.call_args[1]['params']
    assert url.endswith('/search/person')
    assert params['query'] == 'Anne Hathaway'
    assert params['include_adult'] == 'false'
    assert results[0] == {
        'id': 1813, 'name': 'Anne Hathaway',
        'popularity': 55.2, 'known_for_department': 'Acting',
    }


def test_search_person_skips_results_without_id():
    client = _make_client()
    payload = {'results': [{'name': 'Ghost', 'popularity': 3.0}]}

    with _mock_request(client, payload):
        assert client.search_person("Ghost") == []


def test_search_media_movie_endpoint_and_year():
    client = _make_client()
    payload = {'results': [{'id': 77, 'title': 'Inception', 'original_title': 'Inception',
                            'release_date': '2010-07-15', 'vote_average': 8.3}]}

    with _mock_request(client, payload) as mock_request:
        results = client.search_media("Inception", 'movie', 'en', year=2010)

    url, = mock_request.call_args[0]
    params = mock_request.call_args[1]['params']
    assert url.endswith('/search/movie')
    assert params['query'] == 'Inception'
    assert params['year'] == 2010
    assert results[0]['title'] == 'Inception'
    assert results[0]['year'] == '2010'
    assert results[0]['media_type'] == 'movie'


def test_search_media_tv_endpoint_uses_first_air_date_year():
    client = _make_client()
    payload = {'results': [{'id': 5, 'name': 'The Office', 'original_name': 'The Office',
                            'first_air_date': '2005-03-24'}]}

    with _mock_request(client, payload) as mock_request:
        results = client.search_media("The Office", 'tv', 'en', year=2005)

    url, = mock_request.call_args[0]
    params = mock_request.call_args[1]['params']
    assert url.endswith('/search/tv')
    assert params['first_air_date_year'] == 2005
    assert results[0]['title'] == 'The Office'
    assert results[0]['media_type'] == 'tv'


def test_get_person_credits_merges_dedupes_and_sorts():
    client = _make_client()
    payload = {
        'cast': [
            {'id': 1, 'title': 'A', 'original_title': 'A', 'release_date': '2001-01-01', 'popularity': 5.0},
            {'id': 2, 'title': 'B', 'original_title': 'B', 'release_date': '2002-01-01', 'popularity': 50.0},
        ],
        'crew': [
            {'id': 2, 'title': 'B', 'original_title': 'B', 'release_date': '2002-01-01', 'popularity': 50.0},
            {'id': 3, 'title': 'C', 'original_title': 'C', 'release_date': '2003-01-01', 'popularity': 20.0},
        ],
    }

    with _mock_request(client, payload) as mock_request:
        results = client.get_person_credits(1813, 'movie', 'en')

    url, = mock_request.call_args[0]
    assert url.endswith('/person/1813/movie_credits')
    assert [item['id'] for item in results] == [2, 3, 1]


def test_get_person_credits_tv_endpoint():
    client = _make_client()
    payload = {'cast': [{'id': 9, 'name': 'Show', 'original_name': 'Show',
                         'first_air_date': '2010-01-01', 'popularity': 1.0}], 'crew': []}

    with _mock_request(client, payload) as mock_request:
        results = client.get_person_credits(17419, 'tv', 'en')

    url, = mock_request.call_args[0]
    assert url.endswith('/person/17419/tv_credits')
    assert results[0]['media_type'] == 'tv'
    assert results[0]['title'] == 'Show'
