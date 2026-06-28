"""Unit tests for Radarr, Sonarr, and Jellyfin API request logging."""

import json
from unittest.mock import MagicMock, patch

import pytest

from bot.database import Database
from bot.service_request import make_service_request
from bot.session_context import reset_session_id, set_session_id


@pytest.fixture
def db(tmp_path):
    return Database(db_path=str(tmp_path / "test.db"))


def _mock_response(status_code=200, text='{"ok": true}'):
    resp = MagicMock()
    resp.status_code = status_code
    resp.text = text
    resp.raise_for_status = MagicMock()
    return resp


def test_make_service_request_logs_row(db):
    session_token = set_session_id('sess-radarr-1')
    try:
        with patch('bot.service_request.requests.get', return_value=_mock_response()) as mock_get:
            resp = make_service_request(
                db, 'radarr', 'GET',
                'http://radarr.local/api/v3/movie/lookup',
                headers={'X-Api-Key': 'secret-key'},
                params={'term': 'Inception'},
            )
    finally:
        reset_session_id(session_token)

    assert resp.status_code == 200
    mock_get.assert_called_once()

    logs = db.get_service_api_logs(limit=10)
    assert len(logs) == 1
    row = logs[0]
    assert row['service'] == 'radarr'
    assert row['method'] == 'GET'
    assert row['endpoint'] == '/api/v3/movie/lookup'
    assert json.loads(row['params']) == {'term': 'Inception'}
    assert row['status_code'] == 200
    assert row['session_id'] == 'sess-radarr-1'
    assert 'secret-key' not in (row['params'] or '')
    assert 'secret-key' not in (row['request_body'] or '')
    assert 'secret-key' not in (row['response_body'] or '')


def test_make_service_request_logs_post_body(db):
    payload = {'title': 'Test Movie', 'monitored': True}
    with patch('bot.service_request.requests.post', return_value=_mock_response(status_code=201, text='{}')):
        make_service_request(
            db, 'sonarr', 'POST',
            'http://sonarr.local/api/v3/series',
            headers={'X-Api-Key': 'key'},
            json_body=payload,
        )

    logs = db.get_service_api_logs(limit=10, services=['sonarr'])
    assert len(logs) == 1
    assert logs[0]['method'] == 'POST'
    assert json.loads(logs[0]['request_body']) == payload


def test_get_service_api_logs_filters_by_service(db):
    db.log_service_api_request(service='radarr', method='GET', endpoint='/a')
    db.log_service_api_request(service='sonarr', method='GET', endpoint='/b')
    db.log_service_api_request(service='jellyfin', method='GET', endpoint='/c')

    mgmt = db.get_service_api_logs(limit=10, services=['radarr', 'sonarr'])
    services = {row['service'] for row in mgmt}
    assert services == {'radarr', 'sonarr'}

    servers = db.get_service_api_logs(limit=10, services=['jellyfin'])
    assert len(servers) == 1
    assert servers[0]['service'] == 'jellyfin'


def test_get_session_detail_includes_service_api_logs(db):
    session_id = 'sess-detail-1'
    db.create_session(session_id, user_id=100, user_message='add movie')
    db.log_service_api_request(
        service='radarr',
        method='GET',
        endpoint='/api/v3/movie/lookup',
        session_id=session_id,
    )
    db.log_service_api_request(
        service='jellyfin',
        method='GET',
        endpoint='/Items',
        session_id=session_id,
    )

    detail = db.get_session_detail(session_id)
    assert detail is not None
    assert len(detail['service_api_logs']) == 2
    assert {log['service'] for log in detail['service_api_logs']} == {'radarr', 'jellyfin'}


def test_make_service_request_logs_error_on_failure(db):
    with patch('bot.service_request.requests.get') as mock_get:
        resp = _mock_response(status_code=500, text='error')
        resp.raise_for_status.side_effect = Exception('HTTP 500')
        mock_get.return_value = resp

        with pytest.raises(Exception):
            make_service_request(
                db, 'jellyfin', 'GET',
                'http://jellyfin.local/Items',
                headers={'X-Emby-Token': 'token'},
            )

    logs = db.get_service_api_logs(limit=10, services=['jellyfin'])
    assert len(logs) == 1
    assert logs[0]['status_code'] == 500
    assert logs[0]['error'] is not None
