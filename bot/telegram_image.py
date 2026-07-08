"""
Telegram inbound photo handling for vision-enabled LLM flows.

Downloads the largest photo from a Telegram message, builds multimodal
OpenAI message payloads for Chat Completions and Responses API, formats
chat-history placeholders, and redacts image blobs from LLM log payloads.
"""

from __future__ import annotations

import base64
import copy
import logging
from dataclasses import dataclass
from typing import Any, List, Optional

from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

IMAGE_OMITTED = "[image omitted]"
DEFAULT_IMAGE_PROMPT = "The user sent an image."


class TelegramImageDownloadError(Exception):
    """Raised when a Telegram photo cannot be downloaded."""


@dataclass(frozen=True)
class IncomingMessage:
    text: str
    image_data_url: Optional[str]
    has_image: bool


def history_text_for_image(caption: str, image_description: Optional[str] = None) -> str:
    """Build a text-only transcript line for an image message."""
    base = f"[Image] {caption}".strip() if caption else "[Image]"
    if image_description:
        return f"{base}\nVision: {image_description}"
    return base


def session_summary_for_incoming(incoming: IncomingMessage) -> str:
    """Short summary for session logging."""
    if incoming.has_image:
        return history_text_for_image(incoming.text)
    return incoming.text


async def parse_incoming_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> IncomingMessage:
    """Extract caption/text and optional base64 JPEG data URL from an update."""
    message = update.message
    if not message:
        return IncomingMessage(text="", image_data_url=None, has_image=False)

    if message.photo:
        photo = message.photo[-1]
        try:
            telegram_file = await context.bot.get_file(photo.file_id)
            image_bytes = await telegram_file.download_as_bytearray()
        except Exception as exc:
            logger.error("Failed to download Telegram photo: %s", exc)
            raise TelegramImageDownloadError(str(exc)) from exc

        encoded = base64.b64encode(bytes(image_bytes)).decode("ascii")
        data_url = f"data:image/jpeg;base64,{encoded}"
        return IncomingMessage(
            text=message.caption or "",
            image_data_url=data_url,
            has_image=True,
        )

    return IncomingMessage(
        text=message.text or "",
        image_data_url=None,
        has_image=False,
    )


def build_text_content(text: str) -> str:
    """Return plain text content for an LLM user turn."""
    return text


def build_chat_completions_user_message(text: str, image_data_url: Optional[str]) -> dict:
    """Build a Chat Completions API user message, optionally with an image."""
    if not image_data_url:
        return {"role": "user", "content": text}
    parts: List[dict] = [
        {"type": "text", "text": text or DEFAULT_IMAGE_PROMPT},
        {"type": "image_url", "image_url": {"url": image_data_url}},
    ]
    return {"role": "user", "content": parts}


def build_responses_user_message(text: str, image_data_url: Optional[str]) -> dict:
    """Build a Responses API user message, optionally with an image."""
    if not image_data_url:
        return {"role": "user", "content": text}
    parts: List[dict] = [
        {"type": "input_text", "text": text or DEFAULT_IMAGE_PROMPT},
        {"type": "input_image", "image_url": image_data_url},
    ]
    return {"role": "user", "content": parts}


def apply_multimodal_to_last_user_message(
    messages: List[dict],
    text: str,
    image_data_url: str,
    *,
    api: str = "chat",
) -> List[dict]:
    """Replace the last user turn with a multimodal payload containing the image."""
    updated = list(messages)
    builder = build_chat_completions_user_message if api == "chat" else build_responses_user_message
    for index in range(len(updated) - 1, -1, -1):
        if updated[index].get("role") == "user":
            updated[index] = builder(text, image_data_url)
            return updated
    updated.append(builder(text, image_data_url))
    return updated


def _redact_value(value: Any) -> Any:
    if isinstance(value, str):
        if value.startswith("data:image/"):
            return IMAGE_OMITTED
        if "base64," in value and len(value) > 200:
            return IMAGE_OMITTED
        return value
    if isinstance(value, list):
        return [_redact_value(item) for item in value]
    if isinstance(value, dict):
        redacted = {key: _redact_value(val) for key, val in value.items()}
        if redacted.get("type") in {"image_url", "input_image"}:
            if "image_url" in redacted:
                url_value = redacted["image_url"]
                if isinstance(url_value, dict) and "url" in url_value:
                    redacted["image_url"] = {"url": IMAGE_OMITTED}
                else:
                    redacted["image_url"] = IMAGE_OMITTED
        return redacted
    return value


def redact_image_payload(kwargs: dict) -> dict:
    """Return a copy of LLM kwargs with embedded image data replaced by a placeholder."""
    return _redact_value(copy.deepcopy(kwargs))
