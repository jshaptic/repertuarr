"""
Loads and caches phrase YAML catalogs from bot/phrases/data/.
"""

import os
from functools import lru_cache
from typing import Any, Dict, List, Optional

import yaml

from bot.phrases.keys import SUPPORTED_LANGUAGES, SUPPORTED_STYLES

_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def _normalize_lang(lang_code: Optional[str]) -> str:
    lang = (lang_code or "en").lower()
    if lang in SUPPORTED_LANGUAGES:
        return lang
    short = lang[:2]
    if short in SUPPORTED_LANGUAGES:
        return short
    return "en"


def _normalize_style(style: Optional[str]) -> str:
    if style and style in SUPPORTED_STYLES:
        return style
    return "default"


@lru_cache(maxsize=None)
def load_catalog(lang_code: str) -> Dict[str, Any]:
    """Load a language catalog; missing files fall back to English data only."""
    lang = _normalize_lang(lang_code)
    path = os.path.join(_DATA_DIR, f"{lang}.yaml")
    if not os.path.isfile(path):
        if lang == "en":
            raise FileNotFoundError(f"Missing required phrase catalog: {path}")
        return {}
    with open(path, "r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return data


def _variants_from_section(section: Any, key: str) -> Optional[List[str]]:
    if not isinstance(section, dict):
        return None
    value = section.get(key)
    if isinstance(value, list) and value:
        return value
    if isinstance(value, str) and value:
        return [value]
    return None


def resolve_variants(
    lang_code: str,
    style: str,
    key: str,
) -> List[str]:
    """
    Resolve phrase variants using:
    lang/style -> lang/shared -> en/style -> en/shared.
    """
    lang = _normalize_lang(lang_code)
    style = _normalize_style(style)

    lang_catalog = load_catalog(lang)
    en_catalog = load_catalog("en") if lang != "en" else lang_catalog

    candidates = [
        _variants_from_section((lang_catalog.get("styles") or {}).get(style), key),
        _variants_from_section(lang_catalog.get("shared"), key),
        _variants_from_section((en_catalog.get("styles") or {}).get(style), key),
        _variants_from_section(en_catalog.get("shared"), key),
    ]
    for variants in candidates:
        if variants:
            return variants
    return []


def all_variants_for_key(lang_code: str, key: str) -> List[str]:
    """Collect all variants for a key across styles and shared sections."""
    lang = _normalize_lang(lang_code)
    catalog = load_catalog(lang)
    en_catalog = load_catalog("en") if lang != "en" else catalog

    seen = set()
    ordered: List[str] = []

    def _add(values: Optional[List[str]]) -> None:
        if not values:
            return
        for value in values:
            if value not in seen:
                seen.add(value)
                ordered.append(value)

    for cat in (catalog, en_catalog if lang != "en" else None):
        if not cat:
            continue
        shared = _variants_from_section(cat.get("shared"), key)
        _add(shared)
        styles = cat.get("styles") or {}
        for style_name in SUPPORTED_STYLES:
            _add(_variants_from_section(styles.get(style_name), key))

    return ordered
