import tempfile
import time
import unittest
from pathlib import Path

from src.fallback_provider import FallbackProvider
from src.project_writer import ProjectWriter
from src.terminal_runner import TerminalRunner


class TerminalRunnerTests(unittest.TestCase):
    def _wait_for_exit(self, runner: TerminalRunner) -> list[tuple[str, str | int]]:
        events: list[tuple[str, str | int]] = []
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            events.extend(runner.drain_events())
            if any(stream == "exit" for stream, _value in events):
                return events
            time.sleep(0.02)
        self.fail("Timed out waiting for generated command")

    def test_allows_add_and_list_commands(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory) / "buildtrace_app"
            ProjectWriter(output).write(FallbackProvider().load())
            runner = TerminalRunner(output)
            self.assertTrue(runner.run_demo_command('python main.py add "Submit Devpost Video"'))
            self.assertIn("ID: 1 created", "".join(str(value) for stream, value in self._wait_for_exit(runner) if stream == "stdout"))
            self.assertTrue(runner.run_demo_command("python main.py list"))
            self.assertIn("Submit Devpost Video", "".join(str(value) for stream, value in self._wait_for_exit(runner) if stream == "stdout"))

    def test_rejects_shell_like_commands(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            runner = TerminalRunner(Path(temporary_directory))
            self.assertFalse(runner.run_demo_command("python main.py list & whoami"))
            events = runner.drain_events()
            self.assertTrue(any(stream == "stderr" for stream, _value in events))


if __name__ == "__main__":
    unittest.main()
