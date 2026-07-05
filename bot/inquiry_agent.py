"""
Inquiry agent loop: one LLM conversation with fact-lookup tools.

Runs the inquiry call with native web_search plus custom TMDB function tools
(bot/inquiry_tools.py) and loops while the model requests tool executions.
The model decides per question: general knowledge needs no tools, catalog
facts use TMDB tools, current events use web search. Each iteration is logged
separately to the LLM interaction log, and a hard iteration cap forces a
final tool-free answer so the loop always terminates.
"""

import json
import logging
import time
from typing import Callable, List, Optional

from bot.inquiry_tools import build_inquiry_tools, dispatch_inquiry_tool
from bot.llm_logging import log_llm_call
from bot.models import InquiryResponse

logger = logging.getLogger(__name__)


def run_inquiry(
    *,
    client,
    llm_cfg: dict,
    build_llm_kwargs: Callable,
    db,
    tmdb_client,
    messages: List[dict],
    session_id: str,
    user_id: int,
    user_text: str,
    language: str,
    max_iterations: int = 4,
) -> Optional[InquiryResponse]:
    """Answer an inquiry, executing model-requested TMDB tools in a loop.

    The full conversation is threaded via explicit input concatenation (not
    previous_response_id) so every request is reproducible in the LLM logs.
    """
    tools = [{"type": "web_search"}]
    if tmdb_client:
        tools.extend(build_inquiry_tools())

    input_list = list(messages)

    def call_llm(prompt_name: str, **extra_kwargs):
        start_time = time.time()
        kwargs = build_llm_kwargs(
            llm_cfg,
            model=llm_cfg.get('model', 'gpt-4.1-mini'),
            input=input_list,
            text_format=InquiryResponse,
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
        response = call_llm('inquiry' if iteration == 0 else f'inquiry_tool_{iteration}')
        calls = [item for item in response.output if getattr(item, 'type', '') == 'function_call']
        if not calls:
            return response.output_parsed
        # Feed the full model output back (function calls plus any reasoning
        # items), then answer each requested tool call.
        input_list.extend(response.output)
        for call in calls:
            output = dispatch_inquiry_tool(tmdb_client, call.name, json.loads(call.arguments), language)
            logger.info("Inquiry tool %s(%s) -> %d chars", call.name, call.arguments, len(output))
            input_list.append({
                "type": "function_call_output",
                "call_id": call.call_id,
                "output": output,
            })

    logger.warning("Inquiry tool loop hit max_iterations=%d; forcing final answer", max_iterations)
    response = call_llm('inquiry_final', tool_choice="none")
    return response.output_parsed
