"""App settings model."""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class AppSettings:
    fire_monthly_goal: float = 5_000_000.0
    safe_withdrawal_rate: float = 4.0
    theme: str = "light"
    currency_symbol: str = "₩"
    chart_dpi: int = 144
    birthday: str = ""          # ISO format: YYYY-MM-DD
    net_worth_history: list = field(default_factory=list)
    custom_colors: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "fire_monthly_goal": self.fire_monthly_goal,
            "safe_withdrawal_rate": self.safe_withdrawal_rate,
            "theme": self.theme,
            "currency_symbol": self.currency_symbol,
            "chart_dpi": self.chart_dpi,
            "birthday": self.birthday,
            "net_worth_history": self.net_worth_history,
            "custom_colors": self.custom_colors,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AppSettings":
        return cls(
            fire_monthly_goal=float(data.get("fire_monthly_goal", 5_000_000.0)),
            safe_withdrawal_rate=float(data.get("safe_withdrawal_rate", 4.0)),
            theme=data.get("theme", "light"),
            currency_symbol=data.get("currency_symbol", "₩"),
            chart_dpi=int(data.get("chart_dpi", 144)),
            birthday=data.get("birthday", ""),
            net_worth_history=list(data.get("net_worth_history", [])),
            custom_colors=dict(data.get("custom_colors", {})),
        )
