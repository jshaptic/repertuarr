"""Unit tests for ADD_MEDIA normalize/resolve helpers and list extract."""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from bot.add_media import (
    cap_add_items,
    is_item_already_available,
    normalize_add_items,
    pick_best_match,
    resolve_add_candidates,
)
from bot.list_extractor import run_list_extract
from bot.models import AddMediaItem, IntentResponse, ListExtractResponse


def test_normalize_prefers_titles_list():
    intent = IntentResponse(
        intent='ADD_MEDIA',
        title='Ignored',
        media_type='movie',
        titles=[
            AddMediaItem(title='Dune', media_type='movie'),
            AddMediaItem(title='The Office', media_type='series'),
        ],
    )
    items = normalize_add_items(intent)
    assert [i.title for i in items] == ['Dune', 'The Office']
    assert items[1].media_type == 'series'


def test_normalize_falls_back_to_legacy_title():
    intent = IntentResponse(intent='ADD_MEDIA', title='  Inception  ', media_type='movie')
    items = normalize_add_items(intent)
    assert items == [AddMediaItem(title='Inception', media_type='movie')]


def test_normalize_empty_when_no_slots():
    intent = IntentResponse(intent='ADD_MEDIA', source_url='https://example.com/list')
    assert normalize_add_items(intent) == []


def test_cap_add_items():
    items = [AddMediaItem(title=f'T{i}') for i in range(5)]
    assert len(cap_add_items(items, 3)) == 3
    with pytest.raises(ValueError):
        cap_add_items(items, 0)


def test_pick_best_match_filters_unreleased_and_sorts():
    results = [
        {'title': 'A', 'status': 'released', 'popularity': 10},
        {'title': 'B', 'status': 'announced', 'popularity': 99},
        {'title': 'C', 'status': 'released', 'popularity': 50},
    ]
    best = pick_best_match(results)
    assert best['title'] == 'C'


def test_resolve_add_candidates_best_match_and_misses():
    items = [
        AddMediaItem(title='Hit', media_type='movie'),
        AddMediaItem(title='Miss', media_type='movie'),
    ]

    def fake_request(db, service, method, url, **kwargs):
        term = kwargs['params']['term']
        resp = MagicMock()
        resp.raise_for_status = MagicMock()
        if term == 'Hit':
            resp.json.return_value = [
                {'title': 'Hit', 'status': 'released', 'popularity': 1, 'tmdbId': 11},
            ]
        else:
            resp.json.return_value = []
        return resp

    def resolve_arr(user_info, media_type):
        return 'http://radarr', 'key'

    resolved, misses, config_errors = resolve_add_candidates(
        MagicMock(), items, resolve_arr, {}, make_request=fake_request,
    )
    assert len(resolved) == 1
    assert resolved[0]['tmdbId'] == 11
    assert resolved[0]['_batch_media_type'] == 'movie'
    assert misses == ['Miss']
    assert config_errors == []


def test_is_item_already_available_arr_managed():
    assert is_item_already_available({'id': 5, 'tmdbId': 1}, 'movie') is True
    assert is_item_already_available({'id': 0, 'tmdbId': 1}, 'movie') is False


def test_is_item_already_available_media_server():
    server = MagicMock()
    server.search_item.return_value = 'http://play'
    assert is_item_already_available(
        {'id': 0, 'tmdbId': 9, 'title': 'Dune'}, 'movie', server,
    ) is True
    server.search_item.assert_called_once()


def _build_llm_kwargs(cfg, **base_kwargs):
    return base_kwargs


def _message_response(items=None):
    parsed = ListExtractResponse(items=items or [])
    return SimpleNamespace(output=[SimpleNamespace(type='message')], output_parsed=parsed)


@patch('bot.list_extractor.log_llm_call')
def test_list_extract_returns_parsed_items(mock_log):
    client = MagicMock()
    client.responses.parse.return_value = _message_response([
        AddMediaItem(title='Heat', media_type='movie'),
    ])
    result = run_list_extract(
        client=client,
        llm_cfg={'model': 'test-model'},
        build_llm_kwargs=_build_llm_kwargs,
        db=MagicMock(),
        messages=[{"role": "system", "content": "sys"}],
        session_id='s1',
        user_id=1,
        user_text='https://example.com/list',
    )
    assert result is not None
    assert result.items[0].title == 'Heat'
    assert client.responses.parse.call_count == 1
    assert mock_log.call_args[1]['prompt_name'] == 'list_extract'
    kwargs = client.responses.parse.call_args[1]
    assert kwargs['tools'] == [{"type": "web_search"}]
    assert kwargs['text_format'] is ListExtractResponse


@patch('bot.list_extractor.log_llm_call')
def test_list_extract_forces_final_after_max_iterations(mock_log):
    client = MagicMock()
    tool_call = SimpleNamespace(
        type='function_call', name='noop', arguments='{}', call_id='c1',
    )
    client.responses.parse.side_effect = [
        SimpleNamespace(output=[tool_call], output_parsed=None),
        SimpleNamespace(output=[tool_call], output_parsed=None),
        _message_response([]),
    ]
    result = run_list_extract(
        client=client,
        llm_cfg={'model': 'test-model'},
        build_llm_kwargs=_build_llm_kwargs,
        db=MagicMock(),
        messages=[{"role": "system", "content": "sys"}],
        session_id='s1',
        user_id=1,
        user_text='https://example.com/list',
        max_iterations=2,
    )
    assert result is not None
    assert result.items == []
    assert client.responses.parse.call_count == 3
    assert mock_log.call_args_list[-1][1]['prompt_name'] == 'list_extract_final'
    assert client.responses.parse.call_args_list[-1][1]['tool_choice'] == 'none'
