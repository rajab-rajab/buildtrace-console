"""Writes validated generated files into the isolated BuildTrace output folder."""

from __future__ import annotations

from pathlib import Path


class ProjectWriter:
    def __init__(self, output_dir: Path | None = None) -> None:
        root = Path(__file__).resolve().parent.parent
        self.output_dir = output_dir or root / "output" / "buildtrace_app"

    def write(self, payload: dict[str, str]) -> dict[str, Path]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        written: dict[str, Path] = {}
        for filename, content in payload.items():
            target = self.output_dir / filename
            target.write_text(content, encoding="utf-8", newline="\n")
            written[filename] = target
        return written
