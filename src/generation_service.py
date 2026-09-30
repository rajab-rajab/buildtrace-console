"""OpenAI JSON-mode generation with a small, auditable response contract."""

from __future__ import annotations

import json
import os
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


class GenerationError(RuntimeError):
    """A live-generation failure that should route to the local fallback."""


ProgressLog = Callable[[str], None]


class GenerationService:
    MODEL = "gpt-4o-mini"

    def __init__(self, api_key: str | None = None, client: Any | None = None) -> None:
        root = Path(__file__).resolve().parent.parent
        load_dotenv(root / ".env", override=False)
        self.api_key = api_key if api_key is not None else os.getenv("OPENAI_API_KEY")
        self.client = client

    @property
    def is_available(self) -> bool:
        return bool(self.api_key and self.api_key.strip())

    def generate(self, user_prompt: str, on_progress: ProgressLog) -> dict[str, str]:
        if not self.is_available:
            raise GenerationError("No OpenAI API key is available.")
        on_progress("[live] Requesting a JSON project payload from gpt-4o-mini…\n")
        try:
            client = self.client or self._create_client()
            stream: Iterable[Any] = client.chat.completions.create(
                model=self.MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Return only a JSON object with exactly these string keys: "
                            "database.py, main.py, README.md. Generate a local SQLite Python CLI task manager "
                            "with init, add, list, and complete commands."
                        ),
                    },
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                stream=True,
                timeout=10.0,
            )
            parts: list[str] = []
            for chunk in stream:
                choices = getattr(chunk, "choices", [])
                if not choices:
                    continue
                content = getattr(choices[0].delta, "content", None)
                if content:
                    parts.append(content)
                    on_progress("[live] Receiving generated file content…\n")
            if not parts:
                raise GenerationError("The live response did not contain project content.")
            on_progress("[live] Parsing the generated JSON payload…\n")
            parsed = json.loads("".join(parts))
            if not isinstance(parsed, dict):
                raise GenerationError("The live response was not a JSON object.")
            return parsed
        except GenerationError:
            raise
        except Exception as error:
            raise GenerationError(f"Live generation failed ({type(error).__name__}).") from error

    def _create_client(self) -> Any:
        from openai import OpenAI

        return OpenAI(api_key=self.api_key, timeout=10.0)
