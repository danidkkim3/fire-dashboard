"""Projection view — chart based on asset ROI + per-asset contributions."""
from __future__ import annotations
import customtkinter as ctk
from datetime import date, timedelta
from app.views.base_view import BaseView
from app.components.projection_chart import ProjectionChart
from app.utils.formatting import fmt

PROJECTION_MONTHS = 360   # 30 years


class ProjectionView(BaseView):
    def build(self) -> None:
        p = self._app.palette
        self.configure(fg_color=p["bg"])
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 0))
        ctk.CTkLabel(
            header, text="Projection",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=p["text"],
        ).pack(side="left")
        ctk.CTkLabel(
            header,
            text="30-year outlook based on current assets, ROI rates, and contributions",
            font=ctk.CTkFont(size=11), text_color=p["subtext"],
        ).pack(side="left", padx=(16, 0))

        # age input (right-aligned in header)
        age_frame = ctk.CTkFrame(header, fg_color="transparent")
        age_frame.pack(side="right")
        ctk.CTkLabel(age_frame, text="Your age",
                     font=ctk.CTkFont(size=12), text_color=p["subtext"],
                     ).pack(side="left", padx=(0, 6))
        self._age_entry = ctk.CTkEntry(
            age_frame, width=56, height=30,
            fg_color=p["card"], border_color=p["border"], text_color=p["text"],
            font=ctk.CTkFont(size=13),
            justify="center",
        )
        self._age_entry.insert(0, str(self._app.settings.current_age))
        self._age_entry.pack(side="left")
        self._age_entry.bind("<KeyRelease>", lambda _: self._on_age_key())
        self._age_entry.bind("<FocusOut>",   lambda _: self._commit_age())

        # chart
        self._chart = ProjectionChart(self, app=self._app)
        self._chart.grid(row=1, column=0, sticky="nsew", padx=24, pady=16)

        # stats row — 4 columns now (added Age at FIRE)
        self._stats_frame = ctk.CTkFrame(self, fg_color=p["card"], corner_radius=12)
        self._stats_frame.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 24))
        for i in range(4):
            self._stats_frame.grid_columnconfigure(i, weight=1)

        self._stat_labels: list[ctk.CTkLabel] = []
        stat_titles = ["Est. Years to FIRE", "FIRE Date", "Age at FIRE", "Monthly Income at FIRE"]
        for i, lbl in enumerate(stat_titles):
            frame = ctk.CTkFrame(self._stats_frame, fg_color="transparent")
            frame.grid(row=0, column=i, padx=16, pady=12)
            ctk.CTkLabel(frame, text=lbl, font=ctk.CTkFont(size=11),
                         text_color=p["subtext"]).pack()
            val_lbl = ctk.CTkLabel(frame, text="—",
                                   font=ctk.CTkFont(size=17, weight="bold"),
                                   text_color=p["green"])
            val_lbl.pack()
            self._stat_labels.append(val_lbl)

    def _on_age_key(self) -> None:
        """Live-update the chart on every keystroke when the entry holds a valid age."""
        try:
            age = int(self._age_entry.get().strip())
            if not (0 <= age <= 120):
                return
        except ValueError:
            return
        self._app.settings.current_age = age
        self._refresh_chart()

    def _commit_age(self) -> None:
        """On FocusOut, validate and reset to last good value if entry is invalid."""
        try:
            age = int(self._age_entry.get().strip())
            if not (0 <= age <= 120):
                raise ValueError
            self._app.settings.current_age = age
            self._app.save_data()
        except ValueError:
            self._age_entry.delete(0, "end")
            self._age_entry.insert(0, str(self._app.settings.current_age))

    def _refresh_chart(self) -> None:
        """Recalculate and redraw the chart using the current settings."""
        calc = self._app.get_calculator()
        sym = self._app.settings.currency_symbol
        current_age = self._app.settings.current_age
        curve, fire_month = calc.project(months=PROJECTION_MONTHS)
        fn = calc.fire_number
        self._chart.refresh(curve, fn, fire_month, sym, current_age=current_age)
        self._update_stats(fire_month, fn, current_age, sym)

    def _update_stats(self, fire_month: int, fn: float, current_age: int, sym: str) -> None:
        p = self._app.palette
        if fire_month != -1:
            years = fire_month / 12
            fire_date = date.today() + timedelta(days=int(fire_month * 30.44))
            age_at_fire = current_age + years
            income_at_fire = (fn * self._app.settings.safe_withdrawal_rate / 100) / 12
            self._stat_labels[0].configure(text=f"{years:.1f} yrs")
            self._stat_labels[1].configure(text=fire_date.strftime("%b %Y"))
            self._stat_labels[2].configure(text=f"{age_at_fire:.0f}")
            self._stat_labels[3].configure(text=f"{fmt(income_at_fire, sym)}/mo")
        else:
            self._stat_labels[0].configure(text="> 30 yrs")
            for lbl in self._stat_labels[1:]:
                lbl.configure(text="—")
        for lbl in self._stat_labels:
            lbl.configure(text_color=p["green"])

    def refresh(self) -> None:
        p = self._app.palette
        self.configure(fg_color=p["bg"])
        current_age = self._app.settings.current_age

        # keep entry in sync (e.g. after settings import)
        self._age_entry.delete(0, "end")
        self._age_entry.insert(0, str(current_age))

        self._refresh_chart()

    def retheme(self) -> None:
        self._chart.retheme()
        self.refresh()
