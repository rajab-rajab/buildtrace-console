from __future__ import annotations

import customtkinter as ctk

from src import theme


class HeaderStatus(ctk.CTkFrame):
    def __init__(self, master: ctk.CTkBaseClass) -> None:
        super().__init__(master, fg_color=theme.SURFACE, corner_radius=6, border_width=1, border_color=theme.BORDER)
        self.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self, text="BuildTrace", font=theme.TITLE_FONT, text_color=theme.TEXT).grid(
            row=0, column=0, padx=18, pady=12, sticky="w"
        )
        self.badge = ctk.CTkLabel(
            self,
            text="Offline Template Ready",
            font=("Segoe UI Semibold", 12),
            text_color=theme.OBSIDIAN,
            fg_color=theme.AMBER,
            corner_radius=12,
            padx=12,
            pady=5,
        )
        self.badge.grid(row=0, column=1, padx=18, pady=12, sticky="e")

    def set_live_ready(self) -> None:
        self.badge.configure(text="LLM Ready", fg_color=theme.EMERALD)

    def set_unreachable(self) -> None:
        self.badge.configure(text="LLM Unreachable", fg_color=theme.RED)
