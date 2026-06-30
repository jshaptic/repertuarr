"""Tests for carousel feedback inline button styling."""

from bot.carousel_feedback_buttons import (
    STYLE_DANGER,
    STYLE_PRIMARY,
    STYLE_SUCCESS,
    feedback_button,
)


def test_feedback_button_unselected_has_no_style():
    button = feedback_button("👁️", "WATCHED|movie|1|Title", selected=False, selected_style=STYLE_PRIMARY)
    assert button.to_dict() == {"text": "👁️", "callback_data": "WATCHED|movie|1|Title"}


def test_feedback_button_selected_applies_telegram_style():
    button = feedback_button("👁️👍", "LIKED|movie|1|Title", selected=True, selected_style=STYLE_SUCCESS)
    assert button.to_dict() == {
        "text": "👁️👍",
        "callback_data": "LIKED|movie|1|Title",
        "style": "success",
    }


def test_feedback_button_disliked_uses_danger_style():
    button = feedback_button("👁️👎", "DISLIKED|movie|1|Title", selected=True, selected_style=STYLE_DANGER)
    assert button.to_dict()["style"] == "danger"
