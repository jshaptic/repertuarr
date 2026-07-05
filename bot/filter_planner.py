"""
Filter planner LLM step for custom recommendations.

Runs a small structured-output call that extracts concrete media constraints
(genres, people, years, rating, language) from a RECOMMEND query into a
RecommendationPlan. Executed only when the intent classifier produced a query,
so the shortcut recommend button never pays for it. The caller supplies the
rendered system prompt and the LLM client/config plumbing from telegram_bot.
"""

import logging
import time
from typing import Callable, List, Optional

from bot.llm_logging import log_llm_call
from bot.models import RecommendationPlan

logger = logging.getLogger(__name__)


def run_filter_planner(
    *,
    client,
    llm_cfg: dict,
    build_llm_kwargs: Callable,
    system_prompt: str,
    query: str,
    history: List[dict],
    db,
    session_id: str,
    user_id: int,
) -> Optional[RecommendationPlan]:
    """Extract a RecommendationPlan from the user's query via structured output.

    History (most recent transcript messages) lets follow-ups like "same but
    from the 90s" resolve against prior context.
    """
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": query})

    start_time = time.time()
    kwargs = build_llm_kwargs(
        llm_cfg,
        model=llm_cfg.get('model', 'gpt-4.1-nano'),
        messages=messages,
        response_format=RecommendationPlan,
    )
    response = client.beta.chat.completions.parse(**kwargs)
    duration_ms = int((time.time() - start_time) * 1000)
    parsed = response.choices[0].message.parsed
    logger.info("Filter planner result: %s", parsed)

    log_llm_call(
        db,
        session_id=session_id,
        user_id=user_id,
        user_message=query,
        prompt_name='filter_planner',
        kwargs=kwargs,
        response=response,
        parsed=parsed,
        duration_ms=duration_ms,
        llm_name=llm_cfg.get('name'),
        pricing=llm_cfg.get('pricing'),
    )
    return parsed
