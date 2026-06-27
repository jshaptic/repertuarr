"""Unit tests for LLM pricing extraction and cost calculation."""

from dataclasses import dataclass
from types import SimpleNamespace

from bot.llm_pricing import TokenUsage, calculate_cost, extract_token_usage


@dataclass
class _Details:
    cached_tokens: int = 0


def test_extract_chat_completions_usage():
    response = SimpleNamespace(
        usage=SimpleNamespace(
            prompt_tokens=1000,
            completion_tokens=200,
            total_tokens=1200,
            prompt_tokens_details=_Details(cached_tokens=800),
        )
    )
    usage = extract_token_usage(response)
    assert usage.input_tokens == 1000
    assert usage.output_tokens == 200
    assert usage.cached_input_tokens == 800
    assert usage.total_tokens == 1200


def test_extract_responses_api_usage():
    response = SimpleNamespace(
        usage=SimpleNamespace(
            input_tokens=500,
            output_tokens=150,
            total_tokens=650,
            input_tokens_details=_Details(cached_tokens=100),
        )
    )
    usage = extract_token_usage(response)
    assert usage.input_tokens == 500
    assert usage.output_tokens == 150
    assert usage.cached_input_tokens == 100
    assert usage.total_tokens == 650


def test_calculate_cost_with_cached_tokens():
    usage = TokenUsage(input_tokens=1000, output_tokens=200, cached_input_tokens=800, total_tokens=1200)
    pricing = {
        'input_per_million': 2.50,
        'output_per_million': 10.00,
        'cached_input_per_million': 1.25,
    }
    # non_cached=200, cached=800, output=200
    # (200/1e6)*2.5 + (800/1e6)*1.25 + (200/1e6)*10 = 0.0005 + 0.001 + 0.002 = 0.0035
    assert calculate_cost(usage, pricing) == 0.0035


def test_calculate_cost_missing_pricing():
    usage = TokenUsage(input_tokens=100, output_tokens=50, total_tokens=150)
    assert calculate_cost(usage, None) is None
    assert calculate_cost(usage, {'input_per_million': 1.0}) is None


def test_log_llm_interaction_persists_cost_fields(tmp_path):
    from bot.database import Database

    db = Database(db_path=str(tmp_path / 'test.db'))
    db.log_llm_interaction(
        user_id=1,
        user_message='hello',
        llm_request='req',
        llm_response='resp',
        duration_ms=100,
        model='gpt-4o',
        tokens=1200,
        session_id='sess-1',
        prompt_name='intent',
        input_tokens=1000,
        output_tokens=200,
        cached_input_tokens=800,
        cost_usd=0.0035,
        llm_name='default',
        status_code=200,
    )
    logs = db.get_recent_llm_logs(limit=1)
    assert len(logs) == 1
    row = logs[0]
    assert row['input_tokens'] == 1000
    assert row['output_tokens'] == 200
    assert row['cached_input_tokens'] == 800
    assert row['cost_usd'] == 0.0035
    assert row['llm_name'] == 'default'
    assert row['status_code'] == 200


def test_get_users_summary_includes_llm_cost(tmp_path):
    from bot.database import Database

    db = Database(db_path=str(tmp_path / 'test.db'))
    db.log_llm_interaction(
        user_id=42,
        user_message='hi',
        llm_request='r',
        llm_response='s',
        duration_ms=50,
        model='gpt-4o',
        tokens=100,
        cost_usd=0.01,
    )
    db.log_llm_interaction(
        user_id=42,
        user_message='hi2',
        llm_request='r2',
        llm_response='s2',
        duration_ms=50,
        model='gpt-4o',
        tokens=100,
        cost_usd=None,
    )
    summary = db.get_users_summary()
    user = next(u for u in summary if u['user_id'] == 42)
    assert user['llm_cost_usd'] == 0.01
