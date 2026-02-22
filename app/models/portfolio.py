"""Portfolio aggregate model."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
from .asset import Asset, BUILT_IN_CLASSES
from .debt import Debt


@dataclass
class Portfolio:
    assets: List[Asset] = field(default_factory=list)
    debts: List[Debt] = field(default_factory=list)
    custom_classes: List[str] = field(default_factory=list)

    # ── asset helpers ─────────────────────────────────────────────────────

    @property
    def all_classes(self) -> List[str]:
        return BUILT_IN_CLASSES + [c for c in self.custom_classes if c not in BUILT_IN_CLASSES]

    @property
    def total_value(self) -> float:
        return sum(a.current_value for a in self.assets)

    @property
    def total_after_tax_value(self) -> float:
        return sum(a.after_tax_value for a in self.assets)

    def get_asset(self, asset_id: str) -> Asset | None:
        return next((a for a in self.assets if a.id == asset_id), None)

    def add_asset(self, asset: Asset) -> None:
        self.assets.append(asset)

    def update_asset(self, asset: Asset) -> None:
        for i, a in enumerate(self.assets):
            if a.id == asset.id:
                self.assets[i] = asset
                return

    def delete_asset(self, asset_id: str) -> None:
        self.assets = [a for a in self.assets if a.id != asset_id]

    def add_custom_class(self, name: str) -> None:
        if name and name not in self.all_classes:
            self.custom_classes.append(name)

    # ── debt helpers ──────────────────────────────────────────────────────

    @property
    def total_debt(self) -> float:
        return sum(d.balance for d in self.debts)

    def add_debt(self, debt: Debt) -> None:
        self.debts.append(debt)

    def update_debt(self, debt: Debt) -> None:
        for i, d in enumerate(self.debts):
            if d.id == debt.id:
                self.debts[i] = debt
                return

    def delete_debt(self, debt_id: str) -> None:
        self.debts = [d for d in self.debts if d.id != debt_id]

    # ── serialisation ─────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "assets": [a.to_dict() for a in self.assets],
            "debts": [d.to_dict() for d in self.debts],
            "custom_classes": self.custom_classes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Portfolio":
        assets = [Asset.from_dict(a) for a in data.get("assets", [])]
        debts = [Debt.from_dict(d) for d in data.get("debts", [])]
        return cls(
            assets=assets,
            debts=debts,
            custom_classes=data.get("custom_classes", []),
        )
