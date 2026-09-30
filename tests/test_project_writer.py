import tempfile
import unittest
from pathlib import Path

from src.project_writer import ProjectWriter


class ProjectWriterTests(unittest.TestCase):
    def test_writes_only_expected_payload_into_output_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory) / "buildtrace_app"
            written = ProjectWriter(output).write(
                {"main.py": "main", "database.py": "database", "README.md": "readme"}
            )
            self.assertEqual(set(written), {"main.py", "database.py", "README.md"})
            self.assertEqual((output / "main.py").read_text(encoding="utf-8"), "main")


if __name__ == "__main__":
    unittest.main()
