import tempfile
import time
import unittest
from pathlib import Path

from src.build_controller import BuildController
from src.fallback_provider import FallbackProvider
from src.project_writer import ProjectWriter


class OfflineEndToEndTests(unittest.TestCase):
    def test_controller_writes_and_initializes_the_full_offline_project(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            events: list[tuple[str, str]] = []
            files: dict[str, Path] = {}
            controller = BuildController(
                lambda step, status: events.append((step, status)),
                lambda written: files.update(written),
                fallback_provider=FallbackProvider(),
                project_writer=ProjectWriter(Path(temporary_directory) / "buildtrace_app"),
            )
            runner = controller.build_offline()
            deadline = time.monotonic() + 5
            terminal_events: list[tuple[str, str | int]] = []
            while time.monotonic() < deadline:
                terminal_events.extend(runner.drain_events())
                if any(stream == "exit" for stream, _value in terminal_events):
                    break
                time.sleep(0.02)

            self.assertEqual(set(files), {"main.py", "database.py", "README.md"})
            self.assertIn(("disk_write", "complete"), events)
            self.assertIn(("auto_execution", "active"), events)
            self.assertIn(("exit", 0), terminal_events)
            self.assertIn("initialized", "".join(str(value) for stream, value in terminal_events if stream == "stdout"))


if __name__ == "__main__":
    unittest.main()
