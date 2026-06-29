"""
Bot phrase catalog: localized, styled, randomly varied bot copy.
"""

from bot.phrases.keys import *
from bot.phrases.resolver import (
    build_recommend_keyboard,
    get_phrase,
    get_recommend_button_label,
    is_recommend_trigger,
    pick_variant,
)

__all__ = [
    "build_recommend_keyboard",
    "get_phrase",
    "get_recommend_button_label",
    "is_recommend_trigger",
    "pick_variant",
]
