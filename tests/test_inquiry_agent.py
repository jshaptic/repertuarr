"""Unit tests for the inquiry tool loop and TMDB tool dispatch."""

import json
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from bot.inquiry_agent import run_inquiry
from bot.inquiry_tools import build_inquiry_tools, dispatch_inquiry_tool
from bot.models import InquiryResponse


def _build_llm_kwargs(cfg, **base_kwargs):
    return base_kwargs


def _message_response(reply="Answer"):
    parsed = InquiryResponse(reply_text=reply, items=[])
    return SimpleNamespace(output=[SimpleNamespace(type='message')], output_parsed=parsed)


def _tool_call(name, arguments, call_id):
    return SimpleNamespace(type='function_call', name=name, arguments=arguments, call_id=call_id)


def _tool_response(*calls):
    return SimpleNamespace(output=list(calls), output_parsed=None)


def _run(client, tmdb_client=MagicMock(), max_iterations=4):
    return run_inquiry(
        client=client,
        llm_cfg={'model': 'test-model'},
        build_llm_kwargs=_build_llm_kwargs,
        db=MagicMock(),
        tmdb_client=tmdb_client,
        messages=[{"role": "system", "content": "sys"}],
        session_id='s1',
        user_id=1,
        user_text='question',
        language='en',
        max_iterations=max_iterations,
    )


# ── run_inquiry loop ──────────────────────────────────────────────────

@patch('bot.inquiry_agent.log_llm_call')
def test_answer_without_tools_returns_after_one_call(mock_log):
    client = MagicMock()
    client.responses.parse.return_value = _message_response("Direct answer")

    result = _run(client)

    assert result.reply_text == "Direct answer"
    assert client.responses.parse.call_count == 1
    assert mock_log.call_count == 1
    assert mock_log.call_args[1]['prompt_name'] == 'inquiry'


@patch('bot.inquiry_agent.dispatch_inquiry_tool', return_value='[{"tmdb_id": 1}]')
@patch('bot.inquiry_agent.log_llm_call')
def test_single_tool_call_roundtrip(mock_log, mock_dispatch):
    client = MagicMock()
    client.responses.parse.side_effect = [
        _tool_response(_tool_call('tmdb_search', '{"query": "Dune", "media_type": "movie"}', 'call_1')),
        _message_response("Dune is from 2021"),
    ]

    result = _run(client)

    assert result.reply_text == "Dune is from 2021"
    mock_dispatch.assert_called_once()
    assert mock_dispatch.call_args[0][1] == 'tmdb_search'
    assert mock_dispatch.call_args[0][2] == {"query": "Dune", "media_type": "movie"}

    # Second request must include the function call output threaded back in.
    second_input = client.responses.parse.call_args_list[1][1]['input']
    outputs = [i for i in second_input if isinstance(i, dict) and i.get('type') == 'function_call_output']
    assert outputs == [{"type": "function_call_output", "call_id": "call_1", "output": '[{"tmdb_id": 1}]'}]
    assert mock_log.call_args_list[1][1]['prompt_name'] == 'inquiry_tool_1'


@patch('bot.inquiry_agent.dispatch_inquiry_tool', return_value='[]')
@patch('bot.inquiry_agent.log_llm_call')
def test_parallel_tool_calls_all_dispatched(mock_log, mock_dispatch):
    client = MagicMock()
    client.responses.parse.side_effect = [
        _tool_response(
            _tool_call('tmdb_person_credits', '{"person_name": "A", "media_type": "movie"}', 'call_1'),
            _tool_call('tmdb_person_credits', '{"person_name": "B", "media_type": "movie"}', 'call_2'),
        ),
        _message_response(),
    ]

    _run(client)

    assert mock_dispatch.call_count == 2
    second_input = client.responses.parse.call_args_list[1][1]['input']
    call_ids = [i['call_id'] for i in second_input if isinstance(i, dict) and i.get('type') == 'function_call_output']
    assert call_ids == ['call_1', 'call_2']


@patch('bot.inquiry_agent.dispatch_inquiry_tool', return_value='[]')
@patch('bot.inquiry_agent.log_llm_call')
def test_iteration_cap_forces_tool_free_final_call(mock_log, mock_dispatch):
    client = MagicMock()
    client.responses.parse.side_effect = [
        _tool_response(_tool_call('tmdb_search', '{"query": "A", "media_type": "movie"}', 'c1')),
        _tool_response(_tool_call('tmdb_search', '{"query": "B", "media_type": "movie"}', 'c2')),
        _message_response("Forced final"),
    ]

    result = _run(client, max_iterations=2)

    assert result.reply_text == "Forced final"
    assert client.responses.parse.call_count == 3
    final_kwargs = client.responses.parse.call_args_list[2][1]
    assert final_kwargs['tool_choice'] == 'none'
    assert mock_log.call_args_list[2][1]['prompt_name'] == 'inquiry_final'


@patch('bot.inquiry_agent.log_llm_call')
def test_tools_include_tmdb_only_when_client_present(mock_log):
    client = MagicMock()
    client.responses.parse.return_value = _message_response()

    _run(client, tmdb_client=None)
    tools_without = client.responses.parse.call_args[1]['tools']
    assert tools_without == [{"type": "web_search"}]

    _run(client, tmdb_client=MagicMock())
    tools_with = client.responses.parse.call_args[1]['tools']
    assert {t.get('name') for t in tools_with if t.get('type') == 'function'} == {
        'tmdb_search', 'tmdb_person_credits',
    }


# ── tool definitions ──────────────────────────────────────────────────

def test_build_inquiry_tools_are_strict_flat_function_tools():
    tools = build_inquiry_tools()
    assert [t['name'] for t in tools] == ['tmdb_search', 'tmdb_person_credits']
    for tool in tools:
        assert tool['type'] == 'function'
        assert tool['strict'] is True
        assert tool['parameters']['additionalProperties'] is False
        assert set(tool['parameters']['required']) == set(tool['parameters']['properties'])


# ── dispatch ──────────────────────────────────────────────────────────

def test_dispatch_tmdb_search_returns_compact_json():
    tmdb = MagicMock()
    tmdb.search_media.return_value = [{
        'id': 693134, 'title': 'Dune: Part Two', 'original_title': 'Dune: Part Two',
        'year': '2024', 'vote_average': 8.2, 'media_type': 'movie',
        'overview': 'x' * 500, 'popularity': 100.0,
    }]

    result = json.loads(dispatch_inquiry_tool(
        tmdb, 'tmdb_search', {'query': 'Dune', 'media_type': 'movie'}, 'en',
    ))

    tmdb.search_media.assert_called_once_with('Dune', 'movie', 'en')
    assert result[0]['tmdb_id'] == 693134
    assert len(result[0]['overview']) == 120


def test_dispatch_person_credits_unresolved_person_returns_error():
    tmdb = MagicMock()
    tmdb.search_person.return_value = []

    result = json.loads(dispatch_inquiry_tool(
        tmdb, 'tmdb_person_credits', {'person_name': 'Nobody', 'media_type': 'movie'}, 'en',
    ))

    assert 'error' in result


def test_dispatch_exception_returns_error_json():
    tmdb = MagicMock()
    tmdb.search_media.side_effect = RuntimeError("TMDB down")

    result = json.loads(dispatch_inquiry_tool(
        tmdb, 'tmdb_search', {'query': 'X', 'media_type': 'movie'}, 'en',
    ))

    assert result == {'error': 'TMDB down'}


def test_dispatch_unknown_tool_returns_error_json():
    result = json.loads(dispatch_inquiry_tool(MagicMock(), 'nope', {}, 'en'))
    assert 'error' in result
