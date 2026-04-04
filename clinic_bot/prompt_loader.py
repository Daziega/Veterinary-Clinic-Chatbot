from __future__ import annotations

from pathlib import Path

_PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompt.md"

SYSTEM_PROMPT: str = _PROMPT_PATH.read_text(encoding="utf-8")
