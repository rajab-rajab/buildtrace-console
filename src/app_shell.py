"""The CustomTkinter shell that binds offline generation to visible UI panels."""

from __future__ import annotations

import threading
import queue

import customtkinter as ctk

from src import theme
from src.build_controller import BuildController
from src.generation_service import GenerationService
from src.ui.build_input_panel import BuildInputPanel
from src.ui.file_inspector import FileInspector
from src.ui.header_status import HeaderStatus
from src.ui.progress_tracker import ProgressTracker
from src.ui.terminal_panel import TerminalPanel


class BuildTraceApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.title("BuildTrace")
        self.geometry("1250x780")
        self.minsize(1024, 680)
        self.configure(fg_color=theme.BACKGROUND)
        self.grid_columnconfigure(0, weight=3, uniform="columns")
        self.grid_columnconfigure(1, weight=7, uniform="columns")
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.header = HeaderStatus(self)
        self.header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=16, pady=(16, 10))
        self.progress = ProgressTracker(self)
        self.progress.grid(row=1, column=1, sticky="new", padx=(6, 16), pady=(0, 6))
        self.inspector = FileInspector(self)
        self.inspector.grid(row=2, column=1, sticky="nsew", padx=(6, 16), pady=6)
        self.terminal = TerminalPanel(self, self.run_terminal_command)
        self.terminal.grid(row=3, column=1, sticky="nsew", padx=(6, 16), pady=(6, 16))
        self.input_panel = BuildInputPanel(self, self.start_live_build, self.start_offline_build)
        self.input_panel.grid(row=1, column=0, rowspan=3, sticky="nsew", padx=(16, 6), pady=(0, 16))
        self._ui_events: queue.Queue[tuple[str, object]] = queue.Queue()
        self.controller = BuildController(self._queue_progress, self._queue_files)
        self._build_active = False
        self._terminal_polling = False
        self._refresh_api_readiness()
        self.after(75, self._poll_ui_events)

    def _queue_progress(self, step: str, status: str) -> None:
        self._ui_events.put(("progress", (step, status)))

    def _queue_files(self, files: dict[str, object]) -> None:
        self._ui_events.put(("files", files))

    def _poll_ui_events(self) -> None:
        while True:
            try:
                kind, payload = self._ui_events.get_nowait()
            except queue.Empty:
                break
            if kind == "progress":
                step, status = payload  # type: ignore[misc]
                self.on_progress(step, status)
            elif kind == "files":
                self.inspector.show_files(payload)  # type: ignore[arg-type]
            elif kind == "build_complete":
                self._schedule_terminal_poll()
            elif kind == "build_failed":
                self._handle_build_failure(payload)  # type: ignore[arg-type]
        self.after(75, self._poll_ui_events)

    def on_progress(self, step: str, status: str) -> None:
        if step == "build_log":
            self.terminal.append(status)
            return
        self.progress.set_status(step, status)

    def _refresh_api_readiness(self) -> None:
        if self.controller.generation_service.is_available:
            self.header.set_live_ready()
            self.input_panel.set_live_availability(True)
        else:
            self.header.set_unreachable()
            self.input_panel.set_live_availability(False)

    def start_live_build(self) -> None:
        if self._build_active:
            return
        prompt = self.input_panel.prompt.get("1.0", "end-1c")
        self._begin_build(lambda: self.controller.build_live(prompt), "[live] Starting BuildTrace generation…\n")

    def start_offline_build(self) -> None:
        if self._build_active:
            return
        self._begin_build(self.controller.build_offline, "[offline] Loading the verified local template…\n")

    def _begin_build(self, build_action: callable, start_message: str) -> None:
        self._build_active = True
        self.input_panel.set_building(True)
        self.terminal.set_command_enabled(False)
        self.terminal.append(start_message)

        def worker() -> None:
            try:
                build_action()
                self._ui_events.put(("build_complete", None))
            except Exception as error:  # visible build error instead of a silent GUI failure
                self._ui_events.put(("build_failed", error))

        threading.Thread(target=worker, daemon=True).start()

    def _handle_build_failure(self, error: Exception) -> None:
        self.on_progress("disk_write", "failed")
        self.terminal.append(f"Build failed: {error}\n", is_error=True)
        self.input_panel.set_building(False)
        self.terminal.set_command_enabled(True)
        self._build_active = False

    def run_terminal_command(self, command: str) -> None:
        runner = self.controller.terminal_runner
        if runner is None:
            self.terminal.append("Build the offline project before running commands.\n", is_error=True)
            return
        self.terminal.append(f"> {command}\n")
        if runner.run_demo_command(command):
            self.terminal.set_command_enabled(False)
            self._schedule_terminal_poll()
        else:
            self._display_terminal_events()

    def _schedule_terminal_poll(self) -> None:
        if not self._terminal_polling:
            self._terminal_polling = True
            self.after(100, self.poll_terminal)

    def _display_terminal_events(self) -> bool:
        """Render queued output and return whether the current process exited."""
        runner = self.controller.terminal_runner
        if runner is None:
            return False
        exited = False
        for stream, value in runner.drain_events():
            if stream == "exit":
                exit_code = int(value)
                if exit_code == 0:
                    self.on_progress("auto_execution", "complete")
                    self.terminal.append("[verified] Generated command completed successfully.\n")
                else:
                    self.on_progress("auto_execution", "failed")
                    self.terminal.append(f"[failed] Generated project exited with code {exit_code}.\n", is_error=True)
                exited = True
            else:
                self.terminal.append(str(value), is_error=stream == "stderr")
        return exited

    def poll_terminal(self) -> None:
        if self._display_terminal_events():
            self._terminal_polling = False
            self.terminal.set_command_enabled(True)
            if self._build_active:
                self.input_panel.set_building(False)
                self._build_active = False
        else:
            self.after(100, self.poll_terminal)
