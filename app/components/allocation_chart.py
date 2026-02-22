"""Asset allocation pie chart component."""
from __future__ import annotations
import customtkinter as ctk
from app.models.portfolio import Portfolio


class AllocationChart(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        p = app.palette
        kwargs.setdefault("fg_color", p["card"])
        kwargs.setdefault("corner_radius", 12)
        super().__init__(master, **kwargs)
        self._app = app
        self._fig = None
        self._mpl_canvas = None
        self._build_chart()

    def _build_chart(self):
        import matplotlib
        matplotlib.use("TkAgg")
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        if self._mpl_canvas:
            self._mpl_canvas.get_tk_widget().destroy()
        p = self._app.palette
        self._fig, self._ax = plt.subplots(figsize=(3.2, 2.6), dpi=96)
        self._fig.patch.set_facecolor(p["chart_bg"])
        self._ax.set_facecolor(p["chart_bg"])
        self._ax.text(
            0.5, 0.5, "No assets yet", ha="center", va="center",
            color=p["subtext"], fontsize=11, transform=self._ax.transAxes,
        )
        self._ax.axis("off")
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        self._mpl_canvas = FigureCanvasTkAgg(self._fig, master=self)
        self._mpl_canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)

    def refresh(self, portfolio: Portfolio) -> None:
        p = self._app.palette
        self._ax.clear()
        self._fig.patch.set_facecolor(p["chart_bg"])
        self._ax.set_facecolor(p["chart_bg"])

        assets = portfolio.assets
        if not assets:
            self._ax.text(
                0.5, 0.5, "No assets yet", ha="center", va="center",
                color=p["subtext"], fontsize=11, transform=self._ax.transAxes,
            )
            self._ax.axis("off")
            self._mpl_canvas.draw()
            return

        # group by class
        class_totals: dict[str, float] = {}
        for a in assets:
            class_totals[a.asset_class] = class_totals.get(a.asset_class, 0) + a.current_value

        labels = list(class_totals.keys())
        sizes = list(class_totals.values())
        colors = p["chart_colors"][: len(labels)]

        wedges, texts, autotexts = self._ax.pie(
            sizes,
            labels=None,
            colors=colors,
            autopct="%1.1f%%",
            startangle=90,
            wedgeprops={"edgecolor": p["chart_bg"], "linewidth": 2},
            pctdistance=0.82,
        )
        for t in autotexts:
            t.set_color(p["text"])
            t.set_fontsize(9)

        self._ax.legend(
            wedges, labels,
            loc="lower center",
            ncol=min(len(labels), 3),
            fontsize=8,
            frameon=False,
            labelcolor=p["subtext"],
            bbox_to_anchor=(0.5, -0.12),
        )
        self._ax.set_title("Allocation", color=p["text"], fontsize=13, pad=8)
        self._mpl_canvas.draw()

    def retheme(self) -> None:
        self._build_chart()
