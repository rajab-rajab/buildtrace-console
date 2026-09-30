"""Validates project payloads before anything touches the output directory."""

from __future__ import annotations


EXPECTED_FILENAMES = {"main.py", "database.py", "README.md"}


class PayloadValidationError(ValueError):
    """Raised when a project response is incomplete or unsafe."""


def validate_payload(payload: object) -> dict[str, str]:
    if not isinstance(payload, dict):
        raise PayloadValidationError("Generation result must be a JSON object.")

    filenames = set(payload)
    if filenames != EXPECTED_FILENAMES:
        raise PayloadValidationError(
            "Generation result must contain exactly: " + ", ".join(sorted(EXPECTED_FILENAMES)) + "."
        )

    validated: dict[str, str] = {}
    for filename in EXPECTED_FILENAMES:
        content = payload[filename]
        if not isinstance(content, str) or not content.strip():
            raise PayloadValidationError(f"{filename} must contain non-empty text.")
        validated[filename] = content
    return validated
