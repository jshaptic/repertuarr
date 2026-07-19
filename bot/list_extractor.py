"""
List extractor agent: pull movie/TV titles from a user-pasted URL.

Uses the OpenAI Responses API with native web_search (same threading pattern
as bot/inquiry_agent.py). The model opens the URL, extracts titles, and
returns a structured ListExtractResponse. A hard iteration cap forces a
final tool-free answer so the loop always terminates.
"""

import logging
import time
from typing import Callable, List, Optional

from bot.llm_logging import log_llm_call
from bot.models import ListExtractResponse

logger = logging.getLogger(__name__)


def run_list_extract(
    *,
    client,
    llm_cfg: dict,
    build_llm_kwargs: Callable,
    db,
    messages: List[dict],
    session_id: str,
    user_id: int,
    user_text: str,
    max_iterations: int = 4,
) -> Optional[ListExtractResponse]:
    """Extract titles from a URL using web_search, logging every LLM round-trip."""
    tools = [{"type": "web_search"}]
    input_list = list(messages)

    def call_llm(prompt_name: str, **extra_kwargs):
        start_time = time.time()
        kwargs = build_llm_kwargs(
            llm_cfg,
            model=llm_cfg.get('model', 'gpt-4.1-mini'),
            input=input_list,
            text_format=ListExtractResponse,
            tools=tools,
            **extra_kwargs,
        )
        response = client.responses.parse(**kwargs)
        duration_ms = int((time.time() - start_time) * 1000)
        log_llm_call(
            db,
            session_id=session_id,
            user_id=user_id,
            user_message=user_text,
            prompt_name=prompt_name,
            kwargs=kwargs,
            response=response,
            parsed=response.output_parsed,
            duration_ms=duration_ms,
            llm_name=llm_cfg.get('name'),
            pricing=llm_cfg.get('pricing'),
        )
        return response

    for iteration in range(max_iterations):
        response = call_llm(
            'list_extract' if iteration == 0 else f'list_extract_tool_{iteration}'
        )
        # Native web_search is executed server-side; only custom function_call
        # items need a local round-trip. If the model still emits none, we are done.
        calls = [item for item in response.output if getattr(item, 'type', '') == 'function_call']
        if not calls:
            return response.output_parsed
        input_list.extend(response.output)
        for call in calls:
            logger.warning(
                "List extract received unexpected function_call %s; returning empty output",
                call.name,
            )
            input_list.append({
                "type": "function_call_output",
                "call_id": call.call_id,
                "output": '{"error": "unsupported_tool"}',
            })

    logger.warning(
        "List extract tool loop hit max_iterations=%d; forcing final answer",
        max_iterations,
    )
    response = call_llm('list_extract_final', tool_choice="none")
    return response.output_parsed
