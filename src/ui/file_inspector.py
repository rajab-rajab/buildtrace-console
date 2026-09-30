from __future__ import annotations

from pathlib import Path

import customtkinter as ctk

from src import theme


class FileInspector(ctk.CTkFrame):
    def __init__(self, master: ctk.CTkBaseClass) -> None:
        super().__init__(master, fg_color=theme.SURFACE, corner_radius=6, border_width=1, border_color=theme.BORDER)
        ctk.CTkLabel(self, text="Generated Files", font=("Segoe UI Semibold", 15), text_color=theme.TEXT).pack(
            anchor="w", padx=14, pady=(12, 8)
        )
        self.tabs = ctk.CTkTabview(self, fg_color=theme.OBSIDIAN, segmented_button_selected_color=theme.INDIGO)
        self.tabs.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.editors: dict[str, ctk.CTkTextbox] = {}

    def show_files(self, files: dict[str, Path]) -> None:
        for filename in ("main.py", "database.py", "README.md"):
            if filename in self.editors:
                self.tabs.delete(filename)
            tab = self.tabs.add(filename)
            editor = ctk.CTkTextbox(tab, fg_color=theme.OBSIDIAN, text_color=theme.TEXT, font=theme.MONO_FONT, wrap="none")
            editor.pack(fill="both", expand=True, padx=4, pady=4)
            editor.insert("1.0", files[filename].read_text(encoding="utf-8"))
            editor.configure(state="disabled")
            self.editors[filename] = editor
        self.tabs.set("main.py")
