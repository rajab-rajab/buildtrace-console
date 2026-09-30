"""Runs generated project commands and streams their output without blocking the UI."""

from __future__ import annotations

import queue
import shlex
import subprocess
import sys
import threading
from pathlib import Path


class TerminalRunner:
    def __init__(self, working_directory: Path) -> None:
        self.working_directory = working_directory
        self.events: queue.Queue[tuple[str, str | int]] = queue.Queue()

    def initialize(self) -> None:
        self._run([sys.executable, "main.py", "init"])

    def run_demo_command(self, command_text: str) -> bool:
        """Run one supported task-manager command without exposing a shell."""
        try:
            parts = shlex.split(command_text, posix=False)
        except ValueError as error:
            self.events.put(("stderr", f"Could not read command: {error}\n"))
            return False

        if len(parts) < 3 or Path(parts[0]).name.lower() not in {"python", "python.exe"} or parts[1] != "main.py":
            self.events.put(("stderr", "Use a task-manager command beginning with: python main.py\n"))
            return False

        action, arguments = parts[2], parts[3:]
        if action in {"init", "list"} and not arguments:
            self._run([sys.executable, "main.py", action])
            return True
        if action == "add" and len(arguments) == 1 and arguments[0].strip():
            self._run([sys.executable, "main.py", "add", arguments[0]])
            return True
        if action == "complete" and len(arguments) == 1 and arguments[0].isdigit():
            self._run([sys.executable, "main.py", "complete", arguments[0]])
            return True

        self.events.put(("stderr", "Allowed commands: init, add \"title\", list, and complete <id>.\n"))
        return False

    def _run(self, command: list[str]) -> None:
        def worker() -> None:
            try:
                process = subprocess.Popen(
                    command,
                    cwd=self.working_directory,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding="utf-8",
                )
                assert process.stdout is not None
                assert process.stderr is not None
                try:
                    for line in process.stdout:
                        self.events.put(("stdout", line))
                    for line in process.stderr:
                        self.events.put(("stderr", line))
                    self.events.put(("exit", process.wait()))
                finally:
                    process.stdout.close()
                    process.stderr.close()
            except OSError as error:
                self.events.put(("stderr", f"Unable to run generated app: {error}\n"))
                self.events.put(("exit", 1))

        threading.Thread(target=worker, daemon=True).start()

    def drain_events(self) -> list[tuple[str, str | int]]:
        drained: list[tuple[str, str | int]] = []
        while True:
            try:
                drained.append(self.events.get_nowait())
            except queue.Empty:
                return drained
