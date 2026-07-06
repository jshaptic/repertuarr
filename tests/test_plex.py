"""Unit tests for the Plex API client (search, watch history, URL building)."""

from unittest.mock import MagicMock, patch

from bot.plex import PlexClient


def _response(payload):
    resp = MagicMock()
    resp.status_code = 200
    resp.text = "{}"
    resp.json.return_value = payload
    resp.raise_for_status = MagicMock()
    return resp


_IDENTITY = {"MediaContainer": {"machineIdentifier": "mach-123"}}


def _search_payload(items):
    return {"MediaContainer": {"Metadata": items}}


def test_search_item_matches_by_tmdb_id():
    client = PlexClient("http://plex.local:32400", "admin-token")
    search = _search_payload([
        {"ratingKey": "9", "type": "movie", "title": "Wrong One", "Guid": [{"id": "tmdb://111"}]},
        {"ratingKey": "42", "type": "movie", "title": "Inception", "Guid": [{"id": "tmdb://27205"}]},
    ])
    with patch("bot.plex.make_service_request", side_effect=[_response(search), _response(_IDENTITY)]):
        url = client.search_item("Inception", "movie", tmdb_id="27205")
    assert url == "http://plex.local:32400/web/index.html#!/server/mach-123/details?key=%2Flibrary%2Fmetadata%2F42"


def test_search_item_matches_by_tvdb_id_for_series():
    client = PlexClient("http://plex.local:32400", "admin-token")
    search = _search_payload([
        {"ratingKey": "7", "type": "show", "title": "The Show", "Guid": [{"id": "tvdb://555"}]},
    ])
    with patch("bot.plex.make_service_request", side_effect=[_response(search), _response(_IDENTITY)]):
        url = client.search_item("The Show", "series", tvdb_id="555")
    assert "%2Flibrary%2Fmetadata%2F7" in url


def test_search_item_falls_back_to_title_when_no_provider_id():
    client = PlexClient("http://plex.local:32400", "admin-token")
    search = _search_payload([
        {"ratingKey": "3", "type": "movie", "title": "Solo Result", "Guid": []},
    ])
    with patch("bot.plex.make_service_request", side_effect=[_response(search), _response(_IDENTITY)]):
        url = client.search_item("Solo Result", "movie")
    assert "%2Flibrary%2Fmetadata%2F3" in url


def test_search_item_returns_none_when_provider_id_absent():
    client = PlexClient("http://plex.local:32400", "admin-token")
    search = _search_payload([
        {"ratingKey": "3", "type": "movie", "title": "Other", "Guid": [{"id": "tmdb://999"}]},
    ])
    with patch("bot.plex.make_service_request", return_value=_response(search)):
        url = client.search_item("Inception", "movie", tmdb_id="27205")
    assert url is None


def test_search_item_ignores_wrong_media_type():
    client = PlexClient("http://plex.local:32400", "admin-token")
    search = _search_payload([
        {"ratingKey": "3", "type": "show", "title": "A Series", "Guid": []},
    ])
    with patch("bot.plex.make_service_request", return_value=_response(search)):
        url = client.search_item("A Series", "movie")
    assert url is None


def test_get_item_url_caches_machine_identifier():
    client = PlexClient("http://plex.local:32400", "admin-token")
    with patch("bot.plex.make_service_request", return_value=_response(_IDENTITY)) as mock_req:
        first = client.get_item_url("100")
        second = client.get_item_url("200")
    assert first.endswith("%2Flibrary%2Fmetadata%2F100")
    assert second.endswith("%2Flibrary%2Fmetadata%2F200")
    # /identity fetched only once and reused
    assert mock_req.call_count == 1


def test_get_watched_items_collects_watched_titles():
    client = PlexClient("http://plex.local:32400", "admin-token")
    sections = {"MediaContainer": {"Directory": [
        {"key": "1", "type": "movie"},
        {"key": "2", "type": "show"},
        {"key": "3", "type": "photo"},  # ignored
    ]}}
    movies = {"MediaContainer": {"Metadata": [
        {"title": "Watched Movie", "viewCount": 2},
        {"title": "Unwatched Movie", "viewCount": 0},
    ]}}
    shows = {"MediaContainer": {"Metadata": [
        {"title": "Watched Show", "viewedLeafCount": 5},
        {"title": "Unstarted Show", "viewedLeafCount": 0},
    ]}}
    with patch("bot.plex.make_service_request", side_effect=[
        _response(sections), _response(movies), _response(shows),
    ]):
        titles = client.get_watched_items({"token": "user-token"})
    assert set(titles) == {"Watched Movie", "Watched Show"}


def test_get_watched_items_without_token_returns_empty():
    client = PlexClient("http://plex.local:32400", "admin-token")
    assert client.get_watched_items({}) == []
