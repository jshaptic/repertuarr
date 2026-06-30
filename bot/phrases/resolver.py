"""
Phrase resolution: random variant selection, user preference lookup, keyboard helpers.
"""

import re
import random
from typing import Any, Dict, Optional

from telegram import ReplyKeyboardMarkup

from bot.phrases import keys
from bot.phrases.catalog import all_variants_for_key, resolve_variants
from bot.phrases.keys import DOWNLOAD_READY, RECOMMEND_BUTTON, STYLE_SPECIFIC_KEYS, SUPPORTED_STYLES

_DOWNLOAD_READY_LINK_RE = re.compile(r"\[([^\]]+)\]\(\{url\}\)")


def _user_lang(prefs: Optional[Dict[str, Any]]) -> str:
    if not prefs:
        return "en"
    return prefs.get("language", "en")


def _user_style(prefs: Optional[Dict[str, Any]]) -> str:
    if not prefs:
        return "default"
    style = prefs.get("bot_style", "default")
    if style in SUPPORTED_STYLES:
        return style
    return "default"


def pick_variant(variants: list[str]) -> str:
    if not variants:
        raise ValueError("No phrase variants available")
    return random.choice(variants)


def get_media_type_label(prefs: Optional[Dict[str, Any]], media_type: str) -> str:
    """Return a localized display label for movie or series media types."""
    if media_type == "movie":
        return get_phrase(prefs, keys.MEDIA_TYPE_MOVIE)
    if media_type == "series":
        return get_phrase(prefs, keys.MEDIA_TYPE_SHOW)
    raise ValueError(f"Unknown media_type: {media_type!r}")


def get_phrase(
    prefs: Optional[Dict[str, Any]],
    key: str,
    *,
    style: Optional[str] = None,
    lang: Optional[str] = None,
    **fmt: Any,
) -> str:
    """
    Return a random variant for the given phrase key, formatted with kwargs.
    Style-specific keys (e.g. thinking) use bot_style; others use shared phrases.
    """
    resolved_lang = lang or _user_lang(prefs)
    resolved_style = style or _user_style(prefs)
    lookup_style = resolved_style if key in STYLE_SPECIFIC_KEYS else "default"

    variants = resolve_variants(resolved_lang, lookup_style, key)
    if not variants:
        raise ValueError(f"No phrase variants found for key={key!r} lang={resolved_lang!r}")

    text = pick_variant(variants)
    if fmt:
        text = text.format(**fmt)
    return text


def get_jellyfin_play_label(prefs: Optional[Dict[str, Any]]) -> str:
    """Return the Jellyfin link label embedded in the localized download_ready phrase."""
    resolved_lang = _user_lang(prefs)
    variants = resolve_variants(resolved_lang, "default", DOWNLOAD_READY)
    if not variants:
        raise ValueError(
            f"No download_ready phrase variants found for lang={resolved_lang!r}"
        )
    match = _DOWNLOAD_READY_LINK_RE.search(variants[0])
    if not match:
        raise ValueError(
            f"download_ready phrase missing [label]({{url}}) link: {variants[0]!r}"
        )
    return match.group(1)


def get_recommend_button_label(prefs: Optional[Dict[str, Any]]) -> str:
    return get_phrase(prefs, RECOMMEND_BUTTON)


def build_recommend_keyboard(prefs: Optional[Dict[str, Any]]) -> ReplyKeyboardMarkup:
    label = get_recommend_button_label(prefs)
    return ReplyKeyboardMarkup([[label]], resize_keyboard=True, one_time_keyboard=False)


def is_recommend_trigger(text: Optional[str], prefs: Optional[Dict[str, Any]]) -> bool:
    """True when text matches any recommend_button variant for the user's language."""
    if not text:
        return False
    normalized = text.strip()
    if not normalized:
        return False
    lang = _user_lang(prefs)
    return normalized in set(all_variants_for_key(lang, RECOMMEND_BUTTON))
