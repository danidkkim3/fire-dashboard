"""Abstract base view."""
from __future__ import annotations
import customtkinter as ctk


class BaseView(ctk.CTkFrame):
    """All views inherit from this. Provides refresh() and on_show() hooks."""

    def __init__(self, master, app, **kwargs):
        super().__init__(master, **kwargs)
        self._app = app
        self.build()

    def build(self) -> None:
        """Build child widgets. Called once during __init__."""

    def refresh(self) -> None:
        """Re-render data. Called whenever the view becomes active or data changes."""

    def on_show(self) -> None:
        """Called just before the view is raised to the top."""
        self.refresh()
