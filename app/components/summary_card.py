"""KPI summary card widget."""
from __future__ import annotations
import customtkinter as ctk


class SummaryCard(ctk.CTkFrame):
    def __init__(self, master, label: str, value: str, color: str, app, **kwargs):
        p = app.palette
        kwargs.setdefault("fg_color", p["card"])
        kwargs.setdefault("corner_radius", 12)
        super().__init__(master, **kwargs)
        self._app = app

        self._accent_bar = ctk.CTkFrame(self, fg_color=color, width=4, corner_radius=2)
        self._accent_bar.pack(side="left", fill="y", padx=(0, 12), pady=12)

        text_frame = ctk.CTkFrame(self, fg_color="transparent")
        text_frame.pack(side="left", fill="both", expand=True, pady=12)

        self._label_widget = ctk.CTkLabel(
            text_frame, text=label, font=ctk.CTkFont(size=11),
            text_color=p["subtext"], anchor="w",
        )
        self._label_widget.pack(anchor="w")

        self._value_widget = ctk.CTkLabel(
            text_frame, text=value, font=ctk.CTkFont(size=18, weight="bold"),
            text_color=p["text"], anchor="w",
        )
        self._value_widget.pack(anchor="w")

    def update_value(self, value: str) -> None:
        self._value_widget.configure(text=value)

    def update_label(self, label: str) -> None:
        self._label_widget.configure(text=label)

    def retheme(self) -> None:
        p = self._app.palette
        self.configure(fg_color=p["card"])
        self._label_widget.configure(text_color=p["subtext"])
        self._value_widget.configure(text_color=p["text"])
