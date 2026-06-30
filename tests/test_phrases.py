"""Tests for the bot phrase catalog and resolver."""

from __future__ import annotations

import random
from unittest.mock import patch

import pytest
import yaml

from bot.phrases import keys as phrase_keys
from bot.phrases.catalog import load_catalog, resolve_variants
from bot.phrases.keys import SUPPORTED_LANGUAGES, SUPPORTED_STYLES
from bot.phrases.resolver import get_jellyfin_play_label, get_phrase, is_recommend_trigger


def _en_catalog():
    load_catalog.cache_clear()
    return load_catalog("en")


def _shared_keys(catalog: dict) -> list[str]:
    return list((catalog.get("shared") or {}).keys())


def _style_keys(catalog: dict, style: str) -> list[str]:
    return list(((catalog.get("styles") or {}).get(style) or {}).keys())


@pytest.fixture(autouse=True)
def clear_catalog_cache():
    load_catalog.cache_clear()
    yield
    load_catalog.cache_clear()


def test_english_shared_keys_have_one_variant():
    catalog = _en_catalog()
    for key in _shared_keys(catalog):
        variants = catalog["shared"][key]
        assert isinstance(variants, list), key
        assert len(variants) == 1, key


def test_english_thinking_styles_have_three_variants():
    catalog = _en_catalog()
    for style in SUPPORTED_STYLES:
        variants = catalog["styles"][style]["thinking"]
        assert len(variants) >= 3, style


def test_thinking_resolves_for_all_languages_and_styles():
    for lang in SUPPORTED_LANGUAGES:
        for style in SUPPORTED_STYLES:
            prefs = {"language": lang, "bot_style": style}
            text = get_phrase(prefs, phrase_keys.THINKING)
            assert text
            variants = resolve_variants(lang, style, phrase_keys.THINKING)
            assert len(variants) >= 3, f"{lang}/{style}"
            if lang != "en":
                assert text in variants, f"{lang}/{style} fell back to English"


def test_recommend_button_resolves_for_all_languages():
    for lang in SUPPORTED_LANGUAGES:
        prefs = {"language": lang, "bot_style": "default"}
        text = get_phrase(prefs, phrase_keys.RECOMMEND_BUTTON)
        assert text
        variants = resolve_variants(lang, "default", phrase_keys.RECOMMEND_BUTTON)
        assert len(variants) >= 1, lang
        assert text in variants


def test_is_recommend_trigger_matches_all_language_variants():
    for lang in SUPPORTED_LANGUAGES:
        prefs = {"language": lang, "bot_style": "default"}
        variants = resolve_variants(lang, "default", phrase_keys.RECOMMEND_BUTTON)
        for variant in variants:
            assert is_recommend_trigger(variant, prefs), f"{lang}: {variant!r}"
        assert not is_recommend_trigger("totally unrelated text", prefs)


def test_unknown_style_falls_back_to_default():
    prefs = {"language": "en", "bot_style": "nonexistent"}
    default_variants = set(resolve_variants("en", "default", phrase_keys.THINKING))
    with patch("bot.phrases.resolver.random.choice", side_effect=lambda xs: xs[0]):
        text = get_phrase(prefs, phrase_keys.THINKING)
    assert text in default_variants


def test_missing_lang_key_falls_back_to_english_for_non_thinking():
    prefs = {"language": "xx", "bot_style": "default"}
    text = get_phrase(prefs, phrase_keys.WELCOME)
    en_variants = resolve_variants("en", "default", phrase_keys.WELCOME)
    assert text in en_variants


def test_random_variant_selection():
    prefs = {"language": "en", "bot_style": "default"}
    seen = {get_phrase(prefs, phrase_keys.THINKING) for _ in range(30)}
    assert len(seen) >= 2


def test_format_placeholders():
    prefs = {"language": "en", "bot_style": "default"}
    text = get_phrase(prefs, phrase_keys.CLEAR_CHAT, removed=5)
    assert "5" in text


def test_request_lifecycle_placeholders():
    prefs = {"language": "en", "bot_style": "default"}
    queued = get_phrase(
        prefs, phrase_keys.REQUEST_QUEUED, title="Example Movie", type="Movie",
    )
    started = get_phrase(
        prefs, phrase_keys.DOWNLOAD_STARTED, title="Example Movie", type="Movie",
    )

    assert "Example Movie" in queued
    assert "(Movie)" in queued
    assert "Example Movie" in started
    assert "(Movie)" in started
    assert "✅" not in queued
    assert "⬇️" not in started


def test_download_failure_phrases_hide_arr_details():
    prefs = {"language": "en", "bot_style": "default"}
    failed = get_phrase(
        prefs, phrase_keys.DOWNLOAD_FAILED, title="Example Movie", type="Movie",
    )
    unavailable = get_phrase(
        prefs, phrase_keys.DOWNLOAD_UNAVAILABLE, title="Example Show", type="Show",
    )

    assert "(Movie)" in failed
    assert "(Show)" in unavailable
    assert "Radarr" not in failed
    assert "Sonarr" not in failed
    assert "Wanted" not in unavailable
    assert "server owner" in failed.lower()
    assert "server owner" in unavailable.lower()


def test_jellyfin_play_label_comes_from_download_ready():
    prefs = {"language": "en", "bot_style": "default"}
    assert get_jellyfin_play_label(prefs) == "Play on Jellyfin"
    ready = get_phrase(
        prefs,
        phrase_keys.DOWNLOAD_READY,
        title="Example Movie",
        type="Movie",
        url="https://jellyfin.example/movie",
    )
    assert "[Play on Jellyfin](https://jellyfin.example/movie)" in ready
