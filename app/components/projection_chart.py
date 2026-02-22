"""Projection line chart component with hover tooltip."""
from __future__ import annotations
import customtkinter as ctk


class ProjectionChart(ctk.CTkFrame):
    def __init__(self, master, app, **kwargs):
        p = app.palette
        kwargs.setdefault("fg_color", p["card"])
        kwargs.setdefault("corner_radius", 12)
        super().__init__(master, **kwargs)
        self._app = app
        self._fig = None
        self._mpl_canvas = None
        self._hover_cid = None
        self._build()

    def _build(self):
        import matplotlib
        matplotlib.use("TkAgg")
        import matplotlib.pyplot as plt
        import matplotlib.ticker as mticker
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        self._plt = plt
        self._mticker = mticker
        if self._mpl_canvas:
            self._mpl_canvas.get_tk_widget().destroy()
        if self._fig is not None:
            plt.close(self._fig)
        p = self._app.palette
        self._fig, self._ax = plt.subplots(figsize=(7, 4))
        self._fig.patch.set_facecolor(p["chart_bg"])
        self._ax.set_facecolor(p["chart_bg"])
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        self._mpl_canvas = FigureCanvasTkAgg(self._fig, master=self)
        self._mpl_canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)
        self._hover_cid = None

    def refresh(
        self,
        curve: list[float],
        fire_number: float,
        fire_month: int,
        symbol: str,
        current_age: int | None = None,
    ) -> None:
        p = self._app.palette

        # disconnect old hover handler before clearing
        if self._hover_cid is not None:
            try:
                self._mpl_canvas.mpl_disconnect(self._hover_cid)
            except Exception:
                pass
            self._hover_cid = None

        self._ax.clear()
        self._fig.patch.set_facecolor(p["chart_bg"])
        self._ax.set_facecolor(p["chart_bg"])

        if current_age is not None:
            years = [current_age + m / 12 for m in range(len(curve))]
            x_label = "Age"
        else:
            years = [m / 12 for m in range(len(curve))]
            x_label = "Time"

        (line,) = self._ax.plot(
            years, curve, color=p["accent"], linewidth=2.5, label="Net Worth",
        )

        # FIRE goal line
        self._ax.axhline(
            fire_number, color=p["green"], linewidth=1.5,
            linestyle="--", label=f"FIRE Goal ({symbol}{fire_number/1e8:.1f}억)" if fire_number >= 1e8 else f"FIRE Goal ({symbol}{fire_number:,.0f})",
        )

        # shaded region after crossing
        age_offset = current_age if current_age is not None else 0
        if fire_month != -1:
            cross_x = age_offset + fire_month / 12
            self._ax.axvspan(cross_x, years[-1], alpha=0.10, color=p["green"], label="FIRE Zone")
            self._ax.axvline(cross_x, color=p["green"], linewidth=1, linestyle=":")

        def _fmt_y(x):
            if x >= 1e8:
                return f"{symbol}{x/1e8:.1f}억"
            if x >= 1e4:
                return f"{symbol}{x/1e4:.0f}만"
            return f"{symbol}{x:,.0f}"

        mticker = self._mticker
        self._ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: _fmt_y(x)))
        if current_age is not None:
            self._ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"Age {x:.0f}"))
        else:
            self._ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"Yr {x:.0f}"))
        self._ax.tick_params(colors=p["subtext"], labelsize=9)
        for spine in self._ax.spines.values():
            spine.set_edgecolor(p["border"])
        self._ax.set_title("30-Year Portfolio Projection", color=p["text"], fontsize=13, pad=10)
        self._ax.set_xlabel(x_label, color=p["subtext"], fontsize=10)
        self._ax.set_ylabel("Net Worth", color=p["subtext"], fontsize=10)
        self._ax.legend(fontsize=9, frameon=False, labelcolor=p["subtext"], loc="upper left")

        self._fig.tight_layout()

        # ── hover tooltip ─────────────────────────────────────────────────
        annot = self._ax.annotate(
            "", xy=(0, 0), xytext=(14, 14), textcoords="offset points",
            bbox=dict(boxstyle="round,pad=0.5", fc=p["card"], ec=p["accent"],
                      alpha=0.95, linewidth=1.5),
            arrowprops=dict(arrowstyle="->", color=p["accent"], lw=1.2),
            color=p["text"], fontsize=10, zorder=20,
        )
        annot.set_visible(False)

        # vertical cursor line — start at left edge so it doesn't distort xlim
        vline = self._ax.axvline(x=years[0], color=p["accent"], linewidth=1,
                                  linestyle=":", alpha=0, zorder=5)

        x_data = line.get_xdata()
        y_data = line.get_ydata()

        def on_hover(event):
            if event.inaxes != self._ax or len(x_data) == 0:
                annot.set_visible(False)
                vline.set_alpha(0)
                self._mpl_canvas.draw_idle()
                return

            # find nearest month index
            idx = min(range(len(x_data)), key=lambda i: abs(x_data[i] - event.xdata))
            x, y = x_data[idx], y_data[idx]

            year_int = int(x)
            month_int = round((x - year_int) * 12)
            if current_age is not None:
                label = f"Age {year_int}"
            else:
                label = f"Year {year_int}"
            if month_int:
                label += f"  Month {month_int}"

            value_str = _fmt_y(y)
            annot.xy = (x, y)
            annot.set_text(f"{label}\n{value_str}")
            annot.set_visible(True)
            vline.set_xdata([x, x])
            vline.set_alpha(0.4)
            self._mpl_canvas.draw_idle()

        self._hover_cid = self._mpl_canvas.mpl_connect("motion_notify_event", on_hover)
        self._mpl_canvas.draw()

    def retheme(self) -> None:
        self._build()
