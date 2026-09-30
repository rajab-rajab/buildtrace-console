from __future__ import annotations

from collections.abc import Callable

import customtkinter as ctk

from src import theme


DEMO_PROMPT = "Build a Python CLI Task Manager app with SQLite support that can add, list, and complete tasks."


class BuildInputPanel(ctk.CTkFrame):
    def __init__(self, master: ctk.CTkBaseClass, on_live_build: Callable[[], None], on_offline_build: Callable[[], None]) -> None:
        super().__init__(master, fg_color=theme.SURFACE, corner_radius=6, border_width=1, border_color=theme.BORDER)
        ctk.CTkLabel(self, text="Project Input", font=("Segoe UI Semibold", 15), text_color=theme.TEXT).pack(
            anchor="w", padx=14, pady=(14, 8)
        )
        ctk.CTkLabel(self, text="Preset", font=theme.UI_FONT, text_color=theme.MUTED).pack(anchor="w", padx=14)
        preset = ctk.CTkOptionMenu(self, values=["Demo: SQLite Python Task Manager"], fg_color=theme.INDIGO)
        preset.pack(fill="x", padx=14, pady=(4, 14))
        ctk.CTkLabel(self, text="Build request", font=theme.UI_FONT, text_color=theme.MUTED).pack(anchor="w", padx=14)
        self.prompt = ctk.CTkTextbox(self, height=156, fg_color=theme.OBSIDIAN, text_color=theme.TEXT, font=theme.UI_FONT)
        self.prompt.pack(fill="x", padx=14, pady=(4, 14))
        self.prompt.insert("1.0", DEMO_PROMPT)
        ctk.CTkLabel(
            self,
            text="Live API is optional for this first slice. The offline template creates and runs a real local project.",
            font=("Segoe UI", 12),
            text_color=theme.MUTED,
            wraplength=270,
            justify="left",
        ).pack(anchor="w", padx=14, pady=(0, 12))
        self.build_button = ctk.CTkButton(
            self, text="Build & Verify Project", command=on_live_build, fg_color=theme.INDIGO, hover_color="#4F46E5", height=40
        )
        self.build_button.pack(fill="x", padx=14, pady=(0, 8))
        self.offline_button = ctk.CTkButton(
            self,
            text="Use Offline Template",
            command=on_offline_build,
            fg_color="transparent",
            border_width=1,
            border_color=theme.BORDER,
            text_color=theme.TEXT,
            height=36,
        )
        self.offline_button.pack(fill="x", padx=14, pady=(0, 14))

    def set_building(self, building: bool) -> None:
        state = "disabled" if building else "normal"
        self.build_button.configure(state=state, text="Building…" if building else "Build & Verify Project")
        self.offline_button.configure(state=state)

    def set_live_availability(self, available: bool) -> None:
        if available:
            self.build_button.configure(state="normal", text="Build & Verify Project")
        else:
            self.build_button.configure(state="disabled", text="Fix Settings to Build")
