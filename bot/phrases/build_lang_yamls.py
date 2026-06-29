"""
One-off builder for per-language phrase YAML overlays.

Run: poetry run python bot/phrases/build_lang_yamls.py
"""

from __future__ import annotations

import importlib.util
import os
import sys

import yaml

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

_spec = importlib.util.spec_from_file_location(
    "lang_overlay_data",
    os.path.join(os.path.dirname(__file__), "lang_overlay_data.py"),
)
_module = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_module)
LANG_OVERLAYS = _module.LANG_OVERLAYS

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def main() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    for lang, payload in sorted(LANG_OVERLAYS.items()):
        path = os.path.join(DATA_DIR, f"{lang}.yaml")
        with open(path, "w", encoding="utf-8") as handle:
            yaml.dump(
                payload,
                handle,
                allow_unicode=True,
                default_flow_style=False,
                sort_keys=False,
                width=120,
            )
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
