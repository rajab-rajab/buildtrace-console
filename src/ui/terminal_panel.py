from __future__ import annotations

from collections.abc import Callable

import customtkinter as ctk

from src import theme


class TerminalPanel(ctk.CTkFrame):
    def __init__(self, master: ctk.CTkBaseClass, on_command: Callable[[str], None]) -> None:
        super().__init__(master, fg_color=theme.SURFACE, corner_radius=6, border_width=1, border_color=theme.BORDER)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(self, text="Embedded Execution Terminal", font=("Segoe UI Semibold", 15), text_color=theme.TEXT).grid(
            row=0, column=0, sticky="w", padx=14, pady=(12, 8)
        )
        self.output = ctk.CTkTextbox(self, fg_color=theme.OBSIDIAN, text_color=theme.TEXT, font=theme.MONO_FONT, wrap="word")
        self.output.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 8))
        self.output.tag_config("error", foreground=theme.RED)
        command_row = ctk.CTkFrame(self, fg_color="transparent")
        command_row.grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 12))
        command_row.grid_columnconfigure(0, weight=1)
        self.command = ctk.CTkEntry(
            command_row,
            placeholder_text='Try: python main.py add "Submit Devpost Video"',
            fg_color=theme.OBSIDIAN,
            text_color=theme.TEXT,
            font=theme.MONO_FONT,
        )
        self.command.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        def submit() -> None:
            text = self.command.get().strip()
            if text:
                self.command.delete(0, "end")
                on_command(text)

        self.command.bind("<Return>", lambda _event: submit())
        self.run_button = ctk.CTkButton(command_row, text="Run", width=74, command=submit, fg_color=theme.INDIGO)
        self.run_button.grid(row=0, column=1, sticky="e")

    def append(self, text: str, is_error: bool = False) -> None:
        self.output.configure(state="normal")
        self.output.insert("end", text, "error" if is_error else None)
        self.output.see("end")
        self.output.configure(state="disabled")

    def set_command_enabled(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        self.command.configure(state=state)
        self.run_button.configure(state=state)
