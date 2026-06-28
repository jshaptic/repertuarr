"""
Recommendation prompt message helpers.

Builds the multi-message OpenAI input for recommendations so stable system
instructions, user preferences, feedback history, and the current request stay
separated instead of being flattened into one large user prompt.
"""

from typing import Iterable, List


SYSTEM_PROMPT_INTRO = "You are an expert film critic and media curator."
SYSTEM_PROMPT_SCHEMA = "Return the result as a strict JSON object adhering to the provided schema."
SYSTEM_PROMPT = f"{SYSTEM_PROMPT_INTRO}\n\n{SYSTEM_PROMPT_SCHEMA}"


def _clean_lines(values: Iterable[str]) -> List[str]:
    """Normalize optional title lists for prompt display."""
    return [value.strip() for value in values if isinstance(value, str) and value.strip()]


def format_title_list(titles: Iterable[str]) -> str:
    """Render titles as a compact markdown bullet list."""
    return "\n".join(f"- {title}" for title in _clean_lines(titles))


def build_system_message(user_name: str, user_preferences: str, user_guidelines: str) -> str:
    """Build the system message with stable recommendation instructions."""
    sections = [SYSTEM_PROMPT_INTRO]
    if user_name:
        sections.append(f"You are making recommendations for {user_name}.")
    if user_preferences:
        sections.append(f"User preferences: {user_preferences}")
    if user_guidelines:
        sections.append(f"Guidelines:\n{user_guidelines.strip()}")
    sections.append(SYSTEM_PROMPT_SCHEMA)
    return "\n\n".join(sections)


def build_feedback_message(watched_titles: Iterable[str], disliked_titles: Iterable[str]) -> str:
    """Build first-person watched/liked/disliked feedback for taste context."""
    sections = ["I am sharing my watched, liked, and disliked titles for taste context."]

    watched_list = format_title_list(watched_titles)
    if watched_list:
        sections.append(
            "I watched and liked these movies/shows. Do not recommend them again, "
            f"but use them to understand my taste:\n{watched_list}"
        )
    else:
        sections.append("I have not marked any movies/shows as watched and liked yet.")

    disliked_list = format_title_list(disliked_titles)
    if disliked_list:
        sections.append(
            "I watched and disliked these movies/shows. Avoid recommending similar "
            f"content in tone, genre, or style:\n{disliked_list}"
        )
    else:
        sections.append("I have not marked any movies/shows as disliked yet.")

    return "\n\n".join(sections)


def build_recommendation_input_messages(
    system_message: str,
    feedback_message: str,
    recommendation_message: str,
) -> List[dict]:
    """Build OpenAI Responses API input messages for recommendations."""
    messages = [{"role": "system", "content": system_message.strip() or SYSTEM_PROMPT}]
    for message in (feedback_message, recommendation_message):
        content = message.strip()
        if content:
            messages.append({"role": "user", "content": content})
    return messages
