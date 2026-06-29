"""Tests for recommendation prompt rendering and OpenAI message assembly."""

from pathlib import Path

import chevron

from bot.recommendation_prompt import (
    build_feedback_message,
    build_recommendation_input_messages,
    build_system_message,
)


PROMPT_PATH = Path(__file__).resolve().parents[1] / "bot" / "prompts" / "recommendation.mustache"


def test_recommendation_input_messages_are_split_by_role():
    system_message = build_system_message(
        "Lena",
        "Likes warm comedies.",
        "- Prefer happy endings",
    )
    feedback_message = build_feedback_message(["Paddington"], ["Grimdark Show"])
    recommendation_message = "Recommend something cozy."

    messages = build_recommendation_input_messages(
        system_message,
        feedback_message,
        recommendation_message,
    )

    assert [message["role"] for message in messages] == ["system", "user", "user"]
    assert "You are an expert film critic" in messages[0]["content"]
    assert "You are making recommendations for Lena." in messages[0]["content"]
    assert "User preferences: Likes warm comedies." in messages[0]["content"]
    assert "Guidelines:\n- Prefer happy endings" in messages[0]["content"]
    assert "Return the result as a strict JSON object" in messages[0]["content"]
    assert "I watched and liked" in messages[1]["content"]
    assert "- Paddington" in messages[1]["content"]
    assert "- Grimdark Show" in messages[1]["content"]
    assert messages[2]["content"] == recommendation_message


def test_recommendation_template_renders_group_headers_and_tmdb_overview():
    template = PROMPT_PATH.read_text()
    rendered = chevron.render(
        template,
        {
            "query": "something light",
            "language": "ru",
            "has_tmdb_candidates": True,
            "tmdb_candidate_groups": [
                {
                    "name": "Cozy family picks",
                    "items": [
                        {
                            "title": "Paddington",
                            "original_title": "Paddington",
                            "media_type": "movie",
                            "year": "2014",
                            "id": 116149,
                            "vote_average": 7.1,
                            "genres": "Comedy, Family",
                            "overview": "A young bear finds a new home in London.",
                        }
                    ],
                }
            ],
        },
    )

    assert "You are an expert film critic" not in rendered
    assert "Return the result as a strict JSON object" not in rendered
    assert 'request: "something light"' in rendered
    assert "### Cozy family picks" in rendered
    assert "Overview: A young bear finds a new home in London." in rendered
    assert "Generate `title` and `overview` in ru language" in rendered


def test_recommendation_template_uses_configured_count():
    template = PROMPT_PATH.read_text()
    rendered = chevron.render(template, {"query": "sci-fi", "recommendation_count": 7})

    assert "generate 7 deeply curated recommendations" in rendered
