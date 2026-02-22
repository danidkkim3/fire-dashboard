"""Pure, stateless FIRE calculation service."""
from __future__ import annotations
from typing import List, Tuple

from app.models.portfolio import Portfolio
from app.models.settings import AppSettings


class FIRECalculator:
    def __init__(self, portfolio: Portfolio, settings: AppSettings) -> None:
        self._portfolio = portfolio
        self._settings = settings

    # ── core numbers ─────────────────────────────────────────────────────

    @property
    def fire_number(self) -> float:
        swr = self._settings.safe_withdrawal_rate
        if swr <= 0:
            return float("inf")
        return (self._settings.fire_monthly_goal * 12) / (swr / 100)

    @property
    def total_after_tax_value(self) -> float:
        return self._portfolio.total_after_tax_value

    @property
    def total_debt(self) -> float:
        return self._portfolio.total_debt

    @property
    def total_net_worth(self) -> float:
        return self.total_after_tax_value - self.total_debt

    @property
    def monthly_passive_income(self) -> float:
        return (max(0.0, self.total_net_worth) * self._settings.safe_withdrawal_rate / 100) / 12

    @property
    def fire_progress_pct(self) -> float:
        fn = self.fire_number
        if fn <= 0 or fn == float("inf"):
            return 0.0
        return min(100.0, max(0.0, self.total_net_worth / fn * 100))

    # ── projection ───────────────────────────────────────────────────────

    def project(self, months: int = 600) -> Tuple[List[float], int]:
        """
        Return (net_worth_curve_by_month, fire_month_index).

        Each asset seeds from its after_tax_value, grows at after_tax_roi_pct,
        and receives its own monthly_contribution each month.
        Debt balances amortize and are subtracted from net worth.
        fire_month_index = -1 if FIRE not reached within `months`.
        """
        assets = self._portfolio.assets
        debts = self._portfolio.debts

        # seed asset values and per-asset parameters
        values = [a.after_tax_value for a in assets]
        monthly_rates = [
            (1 + max(a.after_tax_roi_pct, 0) / 100) ** (1 / 12) - 1
            for a in assets
        ]
        contributions = [a.monthly_contribution for a in assets]

        # seed debt parameters
        debt_balances = [d.balance for d in debts]
        debt_rates = [d.annual_interest_rate / 100 / 12 for d in debts]
        debt_payments = [d.monthly_payment for d in debts]

        portfolio_curve: List[float] = []
        fire_month = -1
        fn = self.fire_number

        for _ in range(months):
            net_worth = sum(values) - sum(debt_balances)
            portfolio_curve.append(net_worth)

            if fire_month == -1 and net_worth >= fn:
                fire_month = len(portfolio_curve) - 1

            # compound each asset + its monthly contribution
            values = [
                v * (1 + r) + c
                for v, r, c in zip(values, monthly_rates, contributions)
            ]

            # amortize each debt
            debt_balances = [
                max(0.0, b * (1 + r) - p)
                for b, r, p in zip(debt_balances, debt_rates, debt_payments)
            ]

        return portfolio_curve, fire_month

    def years_to_fire(self) -> float | None:
        _, fire_month = self.project()
        if fire_month == -1:
            return None
        return fire_month / 12
