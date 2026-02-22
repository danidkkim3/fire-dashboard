"""Projection view — chart based on asset ROI + per-asset contributions."""
from __future__ import annotations
import customtkinter as ctk
from datetime import date, timedelta
from app.views.base_view import BaseView
from app.components.projection_chart import ProjectionChart
from app.utils.formatting import fmt

PROJECTION_MONTHS = 360   # 30 years


def _age_from_birthday(birthday_str: str) -> int | None:
    """Return exact age in years from an ISO birthday string, or None if invalid."""
    try:
        bday = date.fromisoformat(birthday_str.strip())
        today = date.today()
        age = today.year - bday.year - ((today.month, today.day) < (bday.month, bday.day))
        return age if 0 <= age <= 120 else None
    except ValueError:
        return None


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

        # birthday input (right-aligned in header)
        bday_frame = ctk.CTkFrame(header, fg_color="transparent")
        bday_frame.pack(side="right")
        ctk.CTkLabel(bday_frame, text="Birthday",
                     font=ctk.CTkFont(size=12), text_color=p["subtext"],
                     ).pack(side="left", padx=(0, 6))
        self._bday_entry = ctk.CTkEntry(
            bday_frame, width=110, height=30,
            fg_color=p["card"], border_color=p["border"], text_color=p["text"],
            font=ctk.CTkFont(size=13),
            placeholder_text="YYYY-MM-DD",
            justify="center",
        )
        self._bday_entry.pack(side="left")
        self._bday_entry.bind("<KeyRelease>", lambda _: self._on_bday_key())
        self._bday_entry.bind("<FocusOut>",   lambda _: self._commit_bday())

        # computed age label
        self._age_lbl = ctk.CTkLabel(
            bday_frame, text="", width=60,
            font=ctk.CTkFont(size=12), text_color=p["subtext"],
        )
        self._age_lbl.pack(side="left", padx=(8, 0))

        # chart
        self._chart = ProjectionChart(self, app=self._app)
        self._chart.grid(row=1, column=0, sticky="nsew", padx=24, pady=16)

        # stats row
        self._stats_frame = ctk.CTkFrame(self, fg_color=p["card"], corner_radius=12)
        self._stats_frame.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 24))
        for i in range(4):
            self._stats_frame.grid_columnconfigure(i, weight=1)

        self._stat_labels: list[ctk.CTkLabel] = []
        for i, lbl in enumerate(["Est. Years to FIRE", "FIRE Date", "Age at FIRE", "Monthly Income at FIRE"]):
            frame = ctk.CTkFrame(self._stats_frame, fg_color="transparent")
            frame.grid(row=0, column=i, padx=16, pady=12)
            ctk.CTkLabel(frame, text=lbl, font=ctk.CTkFont(size=11),
                         text_color=p["subtext"]).pack()
            val_lbl = ctk.CTkLabel(frame, text="—",
                                   font=ctk.CTkFont(size=17, weight="bold"),
                                   text_color=p["green"])
            val_lbl.pack()
            self._stat_labels.append(val_lbl)

    # ── birthday handlers ─────────────────────────────────────────────────

    def _on_bday_key(self) -> None:
        """Live-update chart and age label on each keystroke when date is valid."""
        raw = self._bday_entry.get().strip()
        age = _age_from_birthday(raw)
        if age is None:
            self._age_lbl.configure(text="")
            return
        self._age_lbl.configure(text=f"Age {age}")
        self._app.settings.birthday = raw
        self._refresh_chart(age)

    def _commit_bday(self) -> None:
        """On FocusOut, save if valid; reset entry to last good value if not."""
        raw = self._bday_entry.get().strip()
        age = _age_from_birthday(raw)
        if age is not None:
            self._app.settings.birthday = raw
            self._app.save_data()
        else:
            # restore last saved birthday (if any)
            saved = self._app.settings.birthday
            self._bday_entry.delete(0, "end")
            if saved:
                self._bday_entry.insert(0, saved)
            self._age_lbl.configure(text="")

    # ── chart / stats ─────────────────────────────────────────────────────

    def _refresh_chart(self, current_age: int | None) -> None:
        calc = self._app.get_calculator()
        sym = self._app.settings.currency_symbol
        curve, fire_month = calc.project(months=PROJECTION_MONTHS)
        fn = calc.fire_number
        self._chart.refresh(curve, fn, fire_month, sym, current_age=current_age)
        self._update_stats(fire_month, fn, current_age, sym)

    def _update_stats(self, fire_month: int, fn: float,
                      current_age: int | None, sym: str) -> None:
        p = self._app.palette
        if fire_month != -1:
            years = fire_month / 12
            fire_date = date.today() + timedelta(days=int(fire_month * 30.44))
            income_at_fire = (fn * self._app.settings.safe_withdrawal_rate / 100) / 12
            self._stat_labels[0].configure(text=f"{years:.1f} yrs")
            self._stat_labels[1].configure(text=fire_date.strftime("%b %Y"))
            if current_age is not None:
                self._stat_labels[2].configure(text=f"{current_age + years:.0f}")
            else:
                self._stat_labels[2].configure(text="—")
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
        birthday = self._app.settings.birthday

        # sync entry
        self._bday_entry.delete(0, "end")
        if birthday:
            self._bday_entry.insert(0, birthday)

        age = _age_from_birthday(birthday)
        self._age_lbl.configure(text=f"Age {age}" if age is not None else "")
        self._refresh_chart(age)

    def retheme(self) -> None:
        self._chart.retheme()
        self.refresh()
