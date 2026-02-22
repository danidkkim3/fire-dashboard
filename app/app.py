"""Root CTk window — controller / mediator."""
from __future__ import annotations
import customtkinter as ctk
from app.models.portfolio import Portfolio
from app.models.settings import AppSettings
from app.services import persistence
from app.services.theme_manager import get_palette
from app.services.fire_calculator import FIRECalculator
from app.navigation import Sidebar
from app.views.dashboard_view import DashboardView
from app.views.assets_view import AssetsView
from app.views.debts_view import DebtsView
from app.views.projection_view import ProjectionView
from app.views.history_view import HistoryView
from app.views.settings_view import SettingsView


class FIREApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        self.title("FIRE Dashboard")
        self.geometry("1200x760")
        self.minsize(960, 640)

        self.portfolio, self.settings = persistence.load()
        self._record_net_worth_snapshot()
        self._apply_ctk_theme(self.settings.theme)
        self._apply_mpl_dpi(self.settings.chart_dpi)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._sidebar = Sidebar(self, app=self, on_navigate=self.show_view)
        self._sidebar.grid(row=0, column=0, sticky="ns")

        content = ctk.CTkFrame(self, fg_color=self.palette["bg"], corner_radius=0)
        content.grid(row=0, column=1, sticky="nsew")
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(0, weight=1)

        self._views: dict[str, any] = {}
        for key, ViewClass in [
            ("dashboard",  DashboardView),
            ("assets",     AssetsView),
            ("debts",      DebtsView),
            ("projection", ProjectionView),
            ("history",    HistoryView),
            ("settings",   SettingsView),
        ]:
            view = ViewClass(content, app=self, fg_color=self.palette["bg"], corner_radius=0)
            view.grid(row=0, column=0, sticky="nsew")
            self._views[key] = view

        self._active_key = "dashboard"
        self.show_view("dashboard")

    # ── snapshot ──────────────────────────────────────────────────────────

    def _record_net_worth_snapshot(self) -> None:
        from datetime import date
        today = date.today().isoformat()
        history = self.settings.net_worth_history
        if history and history[-1]["date"] == today:
            return
        calc = FIRECalculator(self.portfolio, self.settings)
        value = calc.total_net_worth
        history.append({"date": today, "value": value})
        # keep at most 730 entries
        if len(history) > 730:
            self.settings.net_worth_history = history[-730:]
        persistence.save(self.portfolio, self.settings)

    # ── theme ─────────────────────────────────────────────────────────────

    @property
    def palette(self) -> dict:
        return get_palette(self.settings.theme, self.settings.custom_colors)

    def _apply_ctk_theme(self, theme: str) -> None:
        ctk.set_appearance_mode("dark" if theme == "dark" else "light")
        ctk.set_default_color_theme("blue")

    def _apply_mpl_dpi(self, dpi: int) -> None:
        import matplotlib
        matplotlib.rcParams["figure.dpi"] = dpi

    def apply_chart_dpi(self, dpi: int) -> None:
        self.settings.chart_dpi = dpi
        self._apply_mpl_dpi(dpi)
        # retheme all views to rebuild charts at new DPI
        for view in self._views.values():
            if hasattr(view, "retheme"):
                view.retheme()
            else:
                view.refresh()
        self.save_data()

    def apply_custom_colors(self, colors: dict) -> None:
        self.settings.custom_colors = colors
        p = self.palette
        self.configure(fg_color=p["bg"])
        self._sidebar.retheme(p)
        for view in self._views.values():
            view.configure(fg_color=p["bg"])
            if hasattr(view, "retheme"):
                view.retheme()
            else:
                view.refresh()
        self.save_data()

    def apply_theme(self, theme: str) -> None:
        self.settings.theme = theme
        self._apply_ctk_theme(theme)
        p = self.palette
        self.configure(fg_color=p["bg"])
        self._sidebar.retheme(p)
        for view in self._views.values():
            view.configure(fg_color=p["bg"])
            if hasattr(view, "retheme"):
                view.retheme()
            else:
                view.refresh()
        self.save_data()

    # ── navigation ────────────────────────────────────────────────────────

    def show_view(self, key: str) -> None:
        self._active_key = key
        self._sidebar.set_active(key)
        view = self._views[key]
        view.on_show()
        view.tkraise()

    def refresh_active_view(self) -> None:
        self._views[self._active_key].refresh()

    # ── data ──────────────────────────────────────────────────────────────

    def save_data(self) -> None:
        persistence.save(self.portfolio, self.settings)

    def get_calculator(self) -> FIRECalculator:
        return FIRECalculator(self.portfolio, self.settings)
