"""
Telegram reply helpers that attach the persistent recommend keyboard.
"""

from typing import Any, Callable, Optional

from telegram import Update
from telegram.ext import ContextTypes

from bot.phrases.resolver import build_recommend_keyboard, get_phrase


async def reply_bot_text(
    update: Update,
    prefs: dict,
    key: str,
    *,
    add_to_history: Optional[Callable] = None,
    context: Optional[ContextTypes.DEFAULT_TYPE] = None,
    history_role: str = "assistant",
    parse_mode: Optional[str] = None,
    **fmt: Any,
):
    """Send a phrase-backed text reply with the recommend keyboard attached."""
    text = get_phrase(prefs, key, **fmt)
    keyboard = build_recommend_keyboard(prefs)
    sent = await update.message.reply_text(
        text,
        reply_markup=keyboard,
        parse_mode=parse_mode,
    )
    if add_to_history and context is not None:
        add_to_history(update, context, history_role, text, sent)
    return sent


async def send_thinking_message(update: Update, prefs: dict) -> None:
    """Send a transient thinking phrase (not stored in chat history)."""
    from bot.phrases import keys

    text = get_phrase(prefs, keys.THINKING)
    keyboard = build_recommend_keyboard(prefs)
    await update.message.reply_text(text, reply_markup=keyboard)
