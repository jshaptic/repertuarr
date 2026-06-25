"""
LLM token usage extraction and cost calculation.

Normalizes usage data from OpenAI Chat Completions and Responses API responses,
then computes USD cost from per-LLM pricing configured in config.yaml.
"""

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class TokenUsage:
    """Normalized token counts from an OpenAI API response."""
    input_tokens: int = 0
    output_tokens: int = 0
    cached_input_tokens: int = 0
    total_tokens: int = 0


def _get_attr(obj: Any, *names: str, default: Any = None) -> Any:
    """Read the first present attribute from an object."""
    for name in names:
        if hasattr(obj, name):
            value = getattr(obj, name)
            if value is not None:
                return value
    return default


def _get_cached_tokens(usage: Any, details_attr: str) -> int:
    """Extract cached token count from usage detail objects."""
    details = _get_attr(usage, details_attr)
    if details is None:
        return 0
    return int(_get_attr(details, 'cached_tokens', default=0) or 0)


def extract_token_usage(response: Any) -> TokenUsage:
    """
    Normalize token usage from Chat Completions or Responses API objects.

    Chat Completions: prompt_tokens, completion_tokens, prompt_tokens_details
    Responses API: input_tokens, output_tokens, input_tokens_details
    """
    usage = getattr(response, 'usage', None)
    if usage is None:
        return TokenUsage()

    input_tokens = int(
        _get_attr(usage, 'input_tokens', 'prompt_tokens', default=0) or 0
    )
    output_tokens = int(
        _get_attr(usage, 'output_tokens', 'completion_tokens', default=0) or 0
    )
    total_tokens = int(_get_attr(usage, 'total_tokens', default=0) or 0)

    cached_input_tokens = _get_cached_tokens(usage, 'input_tokens_details')
    if cached_input_tokens == 0:
        cached_input_tokens = _get_cached_tokens(usage, 'prompt_tokens_details')

    cached_input_tokens = min(cached_input_tokens, input_tokens)

    if total_tokens == 0 and (input_tokens or output_tokens):
        total_tokens = input_tokens + output_tokens

    return TokenUsage(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cached_input_tokens=cached_input_tokens,
        total_tokens=total_tokens,
    )


def _pricing_rates(pricing: dict) -> Optional[tuple[float, float, float]]:
    """Return (input, output, cached_input) rates per million tokens, or None."""
    if not pricing:
        return None

    required = ('input_per_million', 'output_per_million', 'cached_input_per_million')
    if not all(key in pricing for key in required):
        return None

    try:
        return (
            float(pricing['input_per_million']),
            float(pricing['output_per_million']),
            float(pricing['cached_input_per_million']),
        )
    except (TypeError, ValueError):
        return None


def calculate_cost(usage: TokenUsage, pricing: Optional[dict]) -> Optional[float]:
    """
    Compute USD cost from token usage and LLM pricing config.

    Returns None when pricing is missing/invalid or no tokens were consumed.
    """
    rates = _pricing_rates(pricing or {})
    if rates is None:
        return None

    if usage.total_tokens == 0 and usage.input_tokens == 0 and usage.output_tokens == 0:
        return None

    input_rate, output_rate, cached_rate = rates
    non_cached = usage.input_tokens - usage.cached_input_tokens

    cost = (
        (non_cached / 1_000_000) * input_rate
        + (usage.cached_input_tokens / 1_000_000) * cached_rate
        + (usage.output_tokens / 1_000_000) * output_rate
    )
    return round(cost, 6)
