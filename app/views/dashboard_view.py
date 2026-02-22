"""Dashboard view — KPI cards, pie chart, gauge."""
from __future__ import annotations
import customtkinter as ctk
from app.views.base_view import BaseView
from app.components.summary_card import SummaryCard
from app.components.allocation_chart import AllocationChart
from app.components.gauge_widget import GaugeWidget
from app.utils.formatting import fmt


class DashboardView(BaseView):
    def build(self) -> None:
        p = self._app.palette
        self.configure(fg_color=p["bg"])
        self.grid_columnconfigure(0, weight=1)

        # ── title ──────────────────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 0))
        ctk.CTkLabel(
            header, text="Dashboard",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=p["text"],
        ).pack(side="left")

        # ── row 1: Total Assets / Total Debt / Net Worth ───────────────────
        row1 = ctk.CTkFrame(self, fg_color="transparent")
        row1.grid(row=1, column=0, sticky="ew", padx=24, pady=(16, 8))
        for i in range(3):
            row1.grid_columnconfigure(i, weight=1)

        row1_defs = [
            ("Total Assets",  p["accent"]),
            ("Total Debt",    p["red"]),
            ("Net Worth",     p["green"]),
        ]
        self._row1_cards: list[SummaryCard] = []
        for i, (lbl, clr) in enumerate(row1_defs):
            card = SummaryCard(row1, label=lbl, value="—", color=clr, app=self._app)
            card.grid(row=0, column=i, sticky="ew", padx=(0 if i == 0 else 8, 0))
            self._row1_cards.append(card)

        # ── row 2: Passive Income / Goal / FIRE Number / Yrs to FIRE ──────
        row2 = ctk.CTkFrame(self, fg_color="transparent")
        row2.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 16))
        for i in range(4):
            row2.grid_columnconfigure(i, weight=1)

        row2_defs = [
            ("Monthly Passive Income", p["chart_colors"][2]),
            ("Monthly FIRE Goal",      p["chart_colors"][3]),
            ("FIRE Number",            p["chart_colors"][4]),
            ("Est. Years to FIRE",     p["chart_colors"][0]),
        ]
        self._row2_cards: list[SummaryCard] = []
        for i, (lbl, clr) in enumerate(row2_defs):
            card = SummaryCard(row2, label=lbl, value="—", color=clr, app=self._app)
            card.grid(row=0, column=i, sticky="ew", padx=(0 if i == 0 else 8, 0))
            self._row2_cards.append(card)

        # ── row 3: Allocation chart / FIRE gauge ───────────────────────────
        charts_frame = ctk.CTkFrame(self, fg_color="transparent")
        charts_frame.grid(row=3, column=0, sticky="ew", padx=24, pady=(0, 16))
        charts_frame.grid_columnconfigure(0, weight=3)
        charts_frame.grid_columnconfigure(1, weight=2)

        self._alloc_chart = AllocationChart(charts_frame, app=self._app)
        self._alloc_chart.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self._gauge = GaugeWidget(charts_frame, app=self._app)
        self._gauge.grid(row=0, column=1, sticky="ew")

        # ── asset summary table ───────────────────────────────────────────
        self._table_frame = ctk.CTkScrollableFrame(
            self, fg_color=p["card"], corner_radius=12, height=140,
        )
        self._table_frame.grid(row=4, column=0, sticky="ew", padx=24, pady=(0, 24))
        self._table_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

    def refresh(self) -> None:
        p = self._app.palette
        self.configure(fg_color=p["bg"])
        portfolio = self._app.portfolio
        settings = self._app.settings
        calc = self._app.get_calculator()
        sym = settings.currency_symbol

        total_assets = portfolio.total_value
        total_debt   = calc.total_debt
        net_worth    = calc.total_net_worth
        monthly_pi   = calc.monthly_passive_income
        fire_goal    = settings.fire_monthly_goal
        fire_num     = calc.fire_number
        ytf          = calc.years_to_fire()
        ytf_str      = f"{ytf:.1f} yrs" if ytf is not None else "Never"

        row1_values = [fmt(total_assets, sym), fmt(total_debt, sym), fmt(net_worth, sym)]
        for card, v in zip(self._row1_cards, row1_values):
            card.update_value(v)
            card.retheme()

        row2_values = [
            f"{fmt(monthly_pi, sym)}/mo",
            f"{fmt(fire_goal, sym)}/mo",
            fmt(fire_num, sym),
            ytf_str,
        ]
        for card, v in zip(self._row2_cards, row2_values):
            card.update_value(v)
            card.retheme()

        self._alloc_chart.refresh(portfolio)
        self._gauge.refresh(calc.fire_progress_pct, monthly_pi, sym)

        # Rebuild table
        for widget in list(self._table_frame.winfo_children()):
            widget.destroy()

        headers = ["Name", "Class", "Value", "After-Tax Value"]
        for col, h in enumerate(headers):
            ctk.CTkLabel(
                self._table_frame, text=h,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=p["subtext"],
            ).grid(row=0, column=col, sticky="w", padx=12, pady=(8, 4))

        for row_i, asset in enumerate(portfolio.assets, start=1):
            row_vals = [
                asset.name,
                asset.asset_class,
                fmt(asset.current_value, sym),
                fmt(asset.after_tax_value, sym),
            ]
            for col, v in enumerate(row_vals):
                ctk.CTkLabel(
                    self._table_frame, text=v,
                    font=ctk.CTkFont(size=11),
                    text_color=p["text"] if col == 0 else p["subtext"],
                    anchor="w",
                ).grid(row=row_i, column=col, sticky="w", padx=12, pady=3)

    def retheme(self) -> None:
        self._alloc_chart.retheme()
        self._gauge.retheme()
        self.refresh()
