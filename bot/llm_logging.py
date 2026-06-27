"""
LLM call serialization and database logging helpers.

Captures both processed (human-readable) and raw (full API payload) request/response
data for the admin AI Activity logs.
"""

import json
import logging
from typing import Any, Optional

from bot.llm_pricing import calculate_cost, extract_token_usage

logger = logging.getLogger(__name__)


def _json_safe(value: Any) -> Any:
    """Recursively convert values to JSON-serializable forms."""
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if hasattr(value, '__name__'):
        return value.__name__
    if hasattr(value, 'model_dump'):
        return value.model_dump(mode='json')
    if hasattr(value, 'dict'):
        return value.dict()
    return str(value)


def serialize_llm_kwargs(kwargs: dict) -> str:
    """Serialize API kwargs, replacing non-JSON types with class names."""
    return json.dumps(_json_safe(kwargs), ensure_ascii=False, indent=2)


def serialize_llm_response(response: Any) -> str:
    """Serialize the full OpenAI API response object."""
    if hasattr(response, 'model_dump'):
        return json.dumps(response.model_dump(mode='json'), ensure_ascii=False, indent=2)
    if hasattr(response, 'dict'):
        return json.dumps(response.dict(), ensure_ascii=False, indent=2)
    return str(response)


def build_processed_request(kwargs: dict) -> str:
    """Build human-readable request text for the admin modal."""
    if 'messages' in kwargs:
        return json.dumps(kwargs['messages'], ensure_ascii=False)
    if 'input' in kwargs:
        inp = kwargs['input']
        if isinstance(inp, list):
            return json.dumps(inp, ensure_ascii=False)
        return str(inp)
    return json.dumps(_json_safe(kwargs), ensure_ascii=False)


def build_processed_response(parsed: Any) -> str:
    """Build human-readable parsed response for the admin modal."""
    if hasattr(parsed, 'model_dump'):
        return json.dumps(parsed.model_dump(), ensure_ascii=False)
    if hasattr(parsed, 'dict'):
        return json.dumps(parsed.dict(), ensure_ascii=False)
    return str(parsed)


def log_llm_call(
    db,
    *,
    session_id: str,
    user_id: int,
    user_message: str,
    prompt_name: str,
    kwargs: dict,
    response: Any,
    parsed: Any,
    duration_ms: int,
    pricing: Optional[dict] = None,
    llm_name: Optional[str] = None,
) -> None:
    """Log an LLM call with processed and raw request/response data."""
    usage = extract_token_usage(response)
    tokens = usage.total_tokens
    cost_usd = calculate_cost(usage, pricing)

    model = getattr(response, 'model', None) or kwargs.get('model', '')

    try:
        db.log_llm_interaction(
            user_id=user_id,
            user_message=user_message,
            session_id=session_id,
            prompt_name=prompt_name,
            llm_request=build_processed_request(kwargs),
            llm_response=build_processed_response(parsed),
            raw_request=serialize_llm_kwargs(kwargs),
            raw_response=serialize_llm_response(response),
            duration_ms=duration_ms,
            model=model,
            tokens=tokens,
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
            cached_input_tokens=usage.cached_input_tokens,
            cost_usd=cost_usd,
            llm_name=llm_name,
            status_code=200,
        )
    except Exception as log_e:
        logger.error(f"Failed to log LLM interaction: {log_e}")
