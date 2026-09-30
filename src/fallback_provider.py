"""Loads the deterministic, locally stored project payload."""

from __future__ import annotations

import json
from pathlib import Path


class FallbackProvider:
    def __init__(self, template_path: Path | None = None) -> None:
        root = Path(__file__).resolve().parent.parent
        self.template_path = template_path or root / "templates" / "task_manager_fallback.json"

    def load(self) -> dict[str, str]:
        with self.template_path.open("r", encoding="utf-8") as template_file:
            payload = json.load(template_file)
        return payload
