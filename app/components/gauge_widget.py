"""Arc gauge widget showing FIRE % progress."""
from __future__ import annotations
import customtkinter as ctk


class GaugeWidget(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        p = app.palette
        kwargs.setdefault("fg_color", p["card"])
        kwargs.setdefault("corner_radius", 12)
        super().__init__(master, **kwargs)
        self._app = app
        self._fig = None
        self._mpl_canvas = None
        self._plt = None
        self._np = None
        self._build()

    def _build(self):
        import matplotlib
        matplotlib.use("TkAgg")
        import matplotlib.pyplot as plt
        import numpy as np
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        self._plt = plt
        self._np = np
        if self._mpl_canvas:
            self._mpl_canvas.get_tk_widget().destroy()
        if self._fig is not None:
            plt.close(self._fig)
        p = self._app.palette
        self._fig, self._ax = plt.subplots(figsize=(3.0, 2.4), dpi=96, subplot_kw={"aspect": "equal"})
        self._fig.patch.set_facecolor(p["chart_bg"])
        self._ax.set_facecolor(p["chart_bg"])
        self._ax.axis("off")
        self._mpl_canvas = FigureCanvasTkAgg(self._fig, master=self)
        self._mpl_canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)

    def refresh(self, pct: float, monthly_income: float, symbol: str) -> None:
        np = self._np
        p = self._app.palette
        self._ax.clear()
        self._ax.set_facecolor(p["chart_bg"])
        self._fig.patch.set_facecolor(p["chart_bg"])
        self._ax.axis("off")

        pct = max(0.0, min(100.0, pct))
        theta_start = 180
        theta_end = 0
        total_arc = 180

        # background arc
        theta_bg = np.linspace(np.radians(theta_start), np.radians(theta_end), 200)
        self._ax.plot(
            np.cos(theta_bg), np.sin(theta_bg),
            color=p["border"], linewidth=18, solid_capstyle="round",
        )

        # filled arc
        if pct > 0:
            fill_angle = theta_end + (1 - pct / 100) * total_arc
            theta_fill = np.linspace(np.radians(theta_start), np.radians(fill_angle), 200)
            self._ax.plot(
                np.cos(theta_fill), np.sin(theta_fill),
                color=p["green"], linewidth=18, solid_capstyle="round",
            )

        # centre text
        self._ax.text(
            0, 0.15, f"{pct:.1f}%",
            ha="center", va="center", fontsize=26, fontweight="bold",
            color=p["green"], transform=self._ax.transData,
        )
        self._ax.text(
            0, -0.22, "FIRE Progress",
            ha="center", va="center", fontsize=10,
            color=p["subtext"], transform=self._ax.transData,
        )
        self._ax.text(
            0, -0.5, f"{symbol}{monthly_income:,.0f}/mo",
            ha="center", va="center", fontsize=11, fontweight="bold",
            color=p["text"], transform=self._ax.transData,
        )
        self._ax.set_xlim(-1.3, 1.3)
        self._ax.set_ylim(-0.7, 1.2)
        self._ax.set_title("FIRE Progress", color=p["text"], fontsize=13, pad=2)
        self._mpl_canvas.draw()

    def retheme(self) -> None:
        self._build()
