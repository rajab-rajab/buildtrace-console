"""Coordinates the offline BuildTrace project generation flow."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from src.fallback_provider import FallbackProvider
from src.generation_service import GenerationError, GenerationService
from src.payload_validator import validate_payload
from src.project_writer import ProjectWriter
from src.terminal_runner import TerminalRunner

ProgressCallback = Callable[[str, str], None]
FilesCallback = Callable[[dict[str, Path]], None]


class BuildController:
    def __init__(
        self,
        progress_callback: ProgressCallback,
        files_callback: FilesCallback,
        fallback_provider: FallbackProvider | None = None,
        project_writer: ProjectWriter | None = None,
        generation_service: GenerationService | None = None,
    ) -> None:
        self.progress_callback = progress_callback
        self.files_callback = files_callback
        self.fallback_provider = fallback_provider or FallbackProvider()
        self.project_writer = project_writer or ProjectWriter()
        self.generation_service = generation_service or GenerationService()
        self.terminal_runner: TerminalRunner | None = None

    def build_offline(self) -> TerminalRunner:
        self.progress_callback("database.py", "active")
        self.progress_callback("build_log", "[offline] Loading the verified local template…\n")
        return self._build_payload(self.fallback_provider.load())

    def build_live(self, prompt: str) -> TerminalRunner:
        self.progress_callback("database.py", "active")
        try:
            payload = self.generation_service.generate(prompt, lambda message: self.progress_callback("build_log", message))
        except GenerationError as error:
            self.progress_callback("build_log", f"[fallback] {error} Using the offline template instead.\n")
            payload = self.fallback_provider.load()
        return self._build_payload(payload)

    def _build_payload(self, payload: object) -> TerminalRunner:
        payload = validate_payload(payload)
        self.progress_callback("database.py", "complete")
        self.progress_callback("main.py", "active")
        self.progress_callback("main.py", "complete")
        self.progress_callback("README.md", "active")
        self.progress_callback("README.md", "complete")
        self.progress_callback("disk_write", "active")
        files = self.project_writer.write(payload)
        self.files_callback(files)
        self.progress_callback("disk_write", "complete")
        self.progress_callback("auto_execution", "active")
        self.terminal_runner = TerminalRunner(self.project_writer.output_dir)
        self.terminal_runner.initialize()
        return self.terminal_runner
