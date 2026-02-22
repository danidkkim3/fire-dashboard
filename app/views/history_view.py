"""Net Worth History view — line chart + scrollable entry table."""
from __future__ import annotations
import customtkinter as ctk
from app.views.base_view import BaseView


class HistoryView(BaseView):
    def build(self) -> None:
        p = self._app.palette
        self.configure(fg_color=p["bg"])
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            self, text="Net Worth History",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=p["text"],
        ).grid(row=0, column=0, sticky="w", padx=24, pady=(24, 16))

        # chart card
        self._chart_card = ctk.CTkFrame(self, fg_color=p["card"], corner_radius=12)
        self._chart_card.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 12))
        self._chart_card.grid_columnconfigure(0, weight=1)
        self._chart_card.grid_rowconfigure(0, weight=1)

        # table card
        self._table_card = ctk.CTkFrame(self, fg_color=p["card"], corner_radius=12)
        self._table_card.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 24))
        self.grid_rowconfigure(2, weight=0)

        self._fig = None
        self._mpl_canvas = None
        self._build_chart()
        self._build_table_header()

    # ── chart ─────────────────────────────────────────────────────────────

    def _build_chart(self) -> None:
        import matplotlib
        matplotlib.use("TkAgg")
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

        self._plt = plt
        if self._mpl_canvas:
            self._mpl_canvas.get_tk_widget().destroy()
        if self._fig is not None:
            plt.close(self._fig)

        p = self._app.palette
        self._fig, self._ax = plt.subplots(figsize=(9, 3.5))
        self._fig.patch.set_facecolor(p["chart_bg"])
        self._ax.set_facecolor(p["chart_bg"])

        self._mpl_canvas = FigureCanvasTkAgg(self._fig, master=self._chart_card)
        self._mpl_canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

    def _refresh_chart(self, history: list) -> None:
        import matplotlib.ticker as mticker
        import matplotlib.dates as mdates
        from datetime import datetime

        p = self._app.palette
        self._ax.clear()
        self._fig.patch.set_facecolor(p["chart_bg"])
        self._ax.set_facecolor(p["chart_bg"])
        sym = self._app.settings.currency_symbol

        if len(history) >= 2:
            dates = [datetime.strptime(e["date"], "%Y-%m-%d") for e in history]
            values = [e["value"] for e in history]

            self._ax.plot(dates, values, color=p["accent"], linewidth=2.5, marker="o",
                          markersize=3, label="Net Worth")
            self._ax.fill_between(dates, values, alpha=0.12, color=p["accent"])

            self._ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
            self._ax.xaxis.set_major_locator(mdates.AutoDateLocator())

            def _fmt_y(x, _):
                if x >= 1e8:
                    return f"{sym}{x/1e8:.1f}억"
                if x >= 1e4:
                    return f"{sym}{x/1e4:.0f}만"
                return f"{sym}{x:,.0f}"

            self._ax.yaxis.set_major_formatter(mticker.FuncFormatter(_fmt_y))
            self._fig.autofmt_xdate(rotation=30, ha="right")
        elif len(history) == 1:
            # single point — show as scatter
            from datetime import datetime
            d = datetime.strptime(history[0]["date"], "%Y-%m-%d")
            self._ax.scatter([d], [history[0]["value"]], color=p["accent"], s=60, zorder=5)
            self._ax.set_xlim(
                d.replace(day=max(1, d.day - 1)),
                d.replace(day=min(28, d.day + 1)),
            )
        else:
            self._ax.text(
                0.5, 0.5, "No history yet.\nLaunch the app daily to build your history.",
                ha="center", va="center", transform=self._ax.transAxes,
                color=p["subtext"], fontsize=12,
            )

        self._ax.tick_params(colors=p["subtext"], labelsize=9)
        for spine in self._ax.spines.values():
            spine.set_edgecolor(p["border"])
        self._ax.set_title("Net Worth Over Time", color=p["text"], fontsize=13, pad=10)
        self._ax.set_ylabel("Net Worth", color=p["subtext"], fontsize=10)

        self._fig.tight_layout()
        self._mpl_canvas.draw()

    # ── table ─────────────────────────────────────────────────────────────

    def _build_table_header(self) -> None:
        p = self._app.palette
        hdr = ctk.CTkFrame(self._table_card, fg_color="transparent")
        hdr.pack(fill="x", padx=16, pady=(12, 4))
        for text, w in [("Date", 160), ("Net Worth", 200)]:
            ctk.CTkLabel(hdr, text=text, font=ctk.CTkFont(size=11, weight="bold"),
                         text_color=p["subtext"], width=w, anchor="w").pack(side="left")

        self._scroll = ctk.CTkScrollableFrame(
            self._table_card, fg_color="transparent", height=180,
        )
        self._scroll.pack(fill="x", padx=16, pady=(0, 12))

    def _refresh_table(self, history: list) -> None:
        p = self._app.palette
        sym = self._app.settings.currency_symbol
        for widget in self._scroll.winfo_children():
            widget.destroy()

        for entry in reversed(history):
            row_frame = ctk.CTkFrame(self._scroll, fg_color="transparent")
            row_frame.pack(fill="x", pady=2)

            def _fmt(v):
                if v >= 1e8:
                    return f"{sym}{v/1e8:.2f}억"
                if v >= 1e4:
                    return f"{sym}{v/1e4:.0f}만"
                return f"{sym}{v:,.0f}"

            ctk.CTkLabel(row_frame, text=entry["date"],
                         font=ctk.CTkFont(size=12), text_color=p["text"],
                         width=160, anchor="w").pack(side="left")
            ctk.CTkLabel(row_frame, text=_fmt(entry["value"]),
                         font=ctk.CTkFont(size=12), text_color=p["accent"],
                         width=200, anchor="w").pack(side="left")

    # ── refresh ───────────────────────────────────────────────────────────

    def refresh(self) -> None:
        history = self._app.settings.net_worth_history
        self._refresh_chart(history)
        self._refresh_table(history)

    def retheme(self) -> None:
        p = self._app.palette
        self.configure(fg_color=p["bg"])
        self._chart_card.configure(fg_color=p["card"])
        self._table_card.configure(fg_color=p["card"])
        self._build_chart()
        self.refresh()
