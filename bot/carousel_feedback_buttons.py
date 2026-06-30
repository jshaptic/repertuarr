"""
Carousel feedback inline buttons for the Telegram recommendation UI.

Builds InlineKeyboardButton instances for ignore/watched/disliked/liked toggles.
Selected state is shown with Telegram's native button styles instead of extra label icons.
"""

from __future__ import annotations

from telegram import InlineKeyboardButton

STYLE_PRIMARY = "primary"
STYLE_SUCCESS = "success"
STYLE_DANGER = "danger"


def feedback_button(
    text: str,
    callback_data: str,
    *,
    selected: bool,
    selected_style: str,
) -> InlineKeyboardButton:
    """Return a feedback toggle button; apply Telegram style when selected."""
    if selected:
        return InlineKeyboardButton(
            text,
            callback_data=callback_data,
            api_kwargs={"style": selected_style},
        )
    return InlineKeyboardButton(text, callback_data=callback_data)
