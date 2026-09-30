import tempfile
import unittest
from pathlib import Path

from src.build_controller import BuildController
from src.fallback_provider import FallbackProvider
from src.generation_service import GenerationError
from src.project_writer import ProjectWriter


class FailingGenerationService:
    def generate(self, _prompt: str, _progress: object) -> dict[str, str]:
        raise GenerationError("Live generation failed (APITimeoutError).")


class BuildControllerLiveTests(unittest.TestCase):
    def test_uses_fallback_when_live_generation_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            events: list[tuple[str, str]] = []
            files: dict[str, Path] = {}
            controller = BuildController(
                lambda step, status: events.append((step, status)),
                lambda written: files.update(written),
                fallback_provider=FallbackProvider(),
                project_writer=ProjectWriter(Path(temporary_directory) / "buildtrace_app"),
                generation_service=FailingGenerationService(),  # type: ignore[arg-type]
            )
            controller.build_live("Build it")
            self.assertEqual(set(files), {"main.py", "database.py", "README.md"})
            self.assertTrue(any("fallback" in text for step, text in events if step == "build_log"))


if __name__ == "__main__":
    unittest.main()
