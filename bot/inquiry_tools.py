"""
Inquiry function tools: definitions and dispatch.

Defines the TMDB fact-lookup tools exposed to the inquiry LLM call (title
search and person filmography) in OpenAI Responses API function-tool format,
and executes them against the TmdbClient. Tool results are compact JSON
strings; failures are returned as {"error": ...} payloads so the tool loop in
bot/inquiry_agent.py can recover instead of crashing mid-conversation.
"""

import json
import logging
from typing import Literal

from pydantic import BaseModel, Field

from bot.recommendation_filters import resolve_person_ids

logger = logging.getLogger(__name__)

MAX_SEARCH_RESULTS = 5
MAX_CREDITS_RESULTS = 20
OVERVIEW_CHARS = 120


class TmdbSearchArgs(BaseModel):
    query: str = Field(description="Title or partial title to search for")
    media_type: Literal['movie', 'tv'] = Field(description="Whether to search movies or TV shows")


class TmdbPersonCreditsArgs(BaseModel):
    person_name: str = Field(description="Full name of the actor or director")
    media_type: Literal['movie', 'tv'] = Field(description="Return movie credits or TV credits")


def _strict_schema(model: type[BaseModel]) -> dict:
    """Render a flat Pydantic model as an OpenAI strict-mode parameter schema."""
    schema = model.model_json_schema()
    schema['additionalProperties'] = False
    return schema


def build_inquiry_tools() -> list:
    """Build Responses API function-tool definitions for TMDB fact lookups."""
    return [
        {
            "type": "function",
            "name": "tmdb_search",
            "description": (
                "Search TMDB for a movie or TV show by title. Returns tmdb_id, title, "
                "year, rating and a short overview for the top matches."
            ),
            "parameters": _strict_schema(TmdbSearchArgs),
            "strict": True,
        },
        {
            "type": "function",
            "name": "tmdb_person_credits",
            "description": (
                "Look up a person's filmography on TMDB by name. Returns their most "
                "popular movie or TV credits."
            ),
            "parameters": _strict_schema(TmdbPersonCreditsArgs),
            "strict": True,
        },
    ]


def _compact_items(items: list) -> str:
    """Serialize TMDB items to the compact JSON shape returned to the model."""
    return json.dumps(
        [
            {
                'tmdb_id': item.get('id'),
                'title': item.get('title'),
                'original_title': item.get('original_title'),
                'year': item.get('year'),
                'vote_average': item.get('vote_average'),
                'media_type': item.get('media_type'),
                'overview': (item.get('overview') or '')[:OVERVIEW_CHARS],
            }
            for item in items
        ],
        ensure_ascii=False,
    )


def dispatch_inquiry_tool(tmdb_client, name: str, arguments: dict, language: str) -> str:
    """Execute one inquiry function tool and return its JSON string result."""
    try:
        if name == 'tmdb_search':
            items = tmdb_client.search_media(arguments['query'], arguments['media_type'], language)
            return _compact_items(items[:MAX_SEARCH_RESULTS])
        if name == 'tmdb_person_credits':
            person_ids, _ = resolve_person_ids(tmdb_client, [arguments['person_name']])
            if not person_ids:
                return json.dumps({'error': f"No TMDB person found for {arguments['person_name']!r}"})
            items = tmdb_client.get_person_credits(person_ids[0], arguments['media_type'], language)
            return _compact_items(items[:MAX_CREDITS_RESULTS])
        return json.dumps({'error': f"Unknown tool {name!r}"})
    except Exception as e:
        logger.error(f"Inquiry tool {name} failed: {e}")
        return json.dumps({'error': str(e)})
