"""Tests for Telegram image parsing and multimodal LLM message helpers."""

import asyncio
from unittest.mock import AsyncMock, MagicMock

from bot.recommendation_prompt import append_image_message
from bot.telegram_image import (
    IMAGE_OMITTED,
    IncomingMessage,
    apply_multimodal_to_last_user_message,
    build_chat_completions_user_message,
    build_responses_user_message,
    history_text_for_image,
    parse_incoming_message,
    redact_image_payload,
    session_summary_for_incoming,
)


def test_history_text_for_image_with_caption_and_description():
    text = history_text_for_image("what movie is this?", "A rainy alley scene from a noir film.")
    assert text == "[Image] what movie is this?\nVision: A rainy alley scene from a noir film."


def test_history_text_for_image_without_caption():
    assert history_text_for_image("") == "[Image]"


def test_session_summary_for_incoming_text_only():
    incoming = IncomingMessage(text="Add Inception", image_data_url=None, has_image=False)
    assert session_summary_for_incoming(incoming) == "Add Inception"


def test_build_chat_completions_user_message_with_image():
    message = build_chat_completions_user_message("poster", "data:image/jpeg;base64,abc")
    assert message["role"] == "user"
    assert message["content"][0] == {"type": "text", "text": "poster"}
    assert message["content"][1]["type"] == "image_url"
    assert message["content"][1]["image_url"]["url"] == "data:image/jpeg;base64,abc"


def test_build_responses_user_message_with_image():
    message = build_responses_user_message("", "data:image/jpeg;base64,abc")
    assert message["role"] == "user"
    assert message["content"][0]["type"] == "input_text"
    assert message["content"][1] == {
        "type": "input_image",
        "image_url": "data:image/jpeg;base64,abc",
    }


def test_apply_multimodal_to_last_user_message_replaces_last_user_turn():
    messages = [
        {"role": "system", "content": "system"},
        {"role": "user", "content": "[Image]"},
    ]
    updated = apply_multimodal_to_last_user_message(
        messages,
        "what movie is this?",
        "data:image/jpeg;base64,abc",
        api="responses",
    )
    assert updated[-1]["content"][1]["type"] == "input_image"


def test_redact_image_payload_strips_base64():
    payload = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "poster"},
                    {
                        "type": "image_url",
                        "image_url": {"url": "data:image/jpeg;base64,verylongpayload"},
                    },
                ],
            }
        ]
    }
    redacted = redact_image_payload(payload)
    assert redacted["messages"][0]["content"][1]["image_url"]["url"] == IMAGE_OMITTED


async def _exercise_parse_incoming_message_downloads_largest_photo():
    update = MagicMock()
    update.message = MagicMock()
    update.message.photo = [MagicMock(file_id="small"), MagicMock(file_id="large")]
    update.message.caption = "what is this?"
    update.message.text = None

    telegram_file = MagicMock()
    telegram_file.download_as_bytearray = AsyncMock(return_value=bytearray(b"fake-jpeg"))
    context = MagicMock()
    context.bot.get_file = AsyncMock(return_value=telegram_file)

    incoming = await parse_incoming_message(update, context)

    context.bot.get_file.assert_awaited_once_with("large")
    assert incoming.has_image is True
    assert incoming.text == "what is this?"
    assert incoming.image_data_url.startswith("data:image/jpeg;base64,")


def test_parse_incoming_message_downloads_largest_photo():
    asyncio.run(_exercise_parse_incoming_message_downloads_largest_photo())


async def _exercise_parse_incoming_message_text_only():
    update = MagicMock()
    update.message = MagicMock()
    update.message.photo = None
    update.message.text = "Recommend a comedy"
    update.message.caption = None

    incoming = await parse_incoming_message(update, MagicMock())

    assert incoming == IncomingMessage(text="Recommend a comedy", image_data_url=None, has_image=False)


def test_parse_incoming_message_text_only():
    asyncio.run(_exercise_parse_incoming_message_text_only())


def test_append_image_message_adds_multimodal_user_turn():
    messages = [{"role": "system", "content": "system"}, {"role": "user", "content": "request"}]
    updated = append_image_message(messages, "like this vibe", "data:image/jpeg;base64,abc")
    assert len(updated) == 3
    assert updated[-1]["content"][1]["type"] == "input_image"
