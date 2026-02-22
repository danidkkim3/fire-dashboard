"""Left sidebar navigation."""
from __future__ import annotations
from typing import Callable
import customtkinter as ctk


NAV_ITEMS = [
    ("dashboard",  "Dashboard"),
    ("assets",     "Assets"),
    ("debts",      "Debts"),
    ("projection", "Projection"),
    ("history",    "History"),
    ("settings",   "Settings"),
]


class Sidebar(ctk.CTkFrame):
    def __init__(self, master, app, on_navigate: Callable[[str], None], **kwargs):
        p = app.palette
        kwargs.setdefault("fg_color", p["sidebar"])
        kwargs.setdefault("corner_radius", 0)
        super().__init__(master, **kwargs)
        self._app = app
        self._on_navigate = on_navigate
        self._buttons: dict[str, ctk.CTkButton] = {}
        self._active: str = ""
        self._build(p)

    def _build(self, p: dict) -> None:
        self.grid_rowconfigure(len(NAV_ITEMS) + 1, weight=1)

        ctk.CTkLabel(
            self,
            text="FIRE\nDashboard",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=p["accent"],
            justify="center",
        ).grid(row=0, column=0, padx=16, pady=(28, 24))

        for i, (key, label) in enumerate(NAV_ITEMS):
            btn = ctk.CTkButton(
                self,
                text=label,
                anchor="w",
                fg_color="transparent",
                hover_color=p["button_hover"],
                text_color=p["subtext"],
                font=ctk.CTkFont(size=13),
                height=42,
                corner_radius=8,
                command=lambda k=key: self._on_navigate(k),
            )
            btn.grid(row=i + 1, column=0, sticky="ew", padx=10, pady=3)
            self._buttons[key] = btn

        self._theme_btn = ctk.CTkButton(
            self,
            text="Toggle Theme",
            fg_color="transparent",
            hover_color=p["button_hover"],
            text_color=p["subtext"],
            font=ctk.CTkFont(size=12),
            height=36,
            corner_radius=8,
            command=self._toggle_theme,
        )
        self._theme_btn.grid(row=len(NAV_ITEMS) + 2, column=0, sticky="ew", padx=10, pady=(0, 20))

    def set_active(self, key: str) -> None:
        p = self._app.palette
        for k, btn in self._buttons.items():
            if k == key:
                btn.configure(fg_color=p["accent"], text_color="#ffffff")
            else:
                btn.configure(fg_color="transparent", text_color=p["subtext"])
        self._active = key

    def retheme(self, p: dict) -> None:
        self.configure(fg_color=p["sidebar"])
        for k, btn in self._buttons.items():
            if k == self._active:
                btn.configure(fg_color=p["accent"], text_color="#ffffff", hover_color=p["button_hover"])
            else:
                btn.configure(fg_color="transparent", text_color=p["subtext"], hover_color=p["button_hover"])
        self._theme_btn.configure(text_color=p["subtext"], hover_color=p["button_hover"])

    def _toggle_theme(self) -> None:
        new = "light" if self._app.settings.theme == "dark" else "dark"
        self._app.apply_theme(new)
