import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from src.fallback_provider import FallbackProvider
from src.project_writer import ProjectWriter


class GeneratedTaskManagerTests(unittest.TestCase):
    def test_init_add_list_and_complete_persist_to_sqlite(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory) / "buildtrace_app"
            ProjectWriter(output).write(FallbackProvider().load())

            def run(*arguments: str) -> str:
                result = subprocess.run(
                    [sys.executable, "main.py", *arguments],
                    cwd=output,
                    capture_output=True,
                    text=True,
                    check=True,
                )
                return result.stdout

            self.assertIn("initialized", run("init"))
            self.assertIn("ID: 1 created", run("add", "Submit Devpost Video"))
            self.assertIn("Submit Devpost Video", run("list"))
            self.assertIn("ID: 1 completed", run("complete", "1"))
            self.assertIn("done", run("list"))


if __name__ == "__main__":
    unittest.main()
