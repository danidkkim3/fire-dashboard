"""Asset data model."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import uuid


class TaxType(str, Enum):
    FLAT_DOLLAR = "flat_dollar"
    PCT_TOTAL = "pct_total"          # % of total current value
    PCT_APPRECIATION = "pct_appreciation"  # % of appreciated (gain) value only


BUILT_IN_CLASSES = ["Cash", "Stocks", "Real Estate", "Crypto", "Bonds", "Other"]


@dataclass
class Asset:
    name: str
    asset_class: str
    current_value: float
    annual_roi_pct: float
    tax_type: TaxType
    tax_value: float
    notes: str = ""
    cost_basis: float = 0.0
    monthly_contribution: float = 0.0
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # ── derived properties ────────────────────────────────────────────────

    @property
    def gain(self) -> float:
        return max(0.0, self.current_value - self.cost_basis)

    @property
    def annual_tax_cost(self) -> float:
        if self.tax_type == TaxType.FLAT_DOLLAR:
            return self.tax_value
        if self.tax_type == TaxType.PCT_APPRECIATION:
            return self.gain * (self.tax_value / 100)
        return self.current_value * (self.tax_value / 100)

    @property
    def after_tax_value(self) -> float:
        if self.tax_type == TaxType.FLAT_DOLLAR:
            return max(0.0, self.current_value - self.tax_value)
        if self.tax_type == TaxType.PCT_APPRECIATION:
            return self.current_value - self.gain * (self.tax_value / 100)
        return self.current_value * (1 - self.tax_value / 100)

    @property
    def after_tax_roi_pct(self) -> float:
        """
        Effective annual growth rate used in projections.
        - FLAT_DOLLAR: recurring annual cost → reduces ROI proportionally.
        - PCT_TOTAL / PCT_APPRECIATION: one-time liquidation taxes, not annual drag.
          The tax is already captured by seeding projections from after_tax_value;
          the growth rate itself is the gross ROI.
        """
        if self.tax_type == TaxType.FLAT_DOLLAR:
            if self.current_value <= 0:
                return self.annual_roi_pct
            tax_drag = (self.tax_value / self.current_value) * 100
            return self.annual_roi_pct - tax_drag
        return self.annual_roi_pct

    # ── serialisation ─────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "asset_class": self.asset_class,
            "current_value": self.current_value,
            "annual_roi_pct": self.annual_roi_pct,
            "tax_type": self.tax_type.value,
            "tax_value": self.tax_value,
            "cost_basis": self.cost_basis,
            "monthly_contribution": self.monthly_contribution,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Asset":
        raw_type = data.get("tax_type", TaxType.PCT_TOTAL.value)
        if raw_type == "percentage":
            raw_type = TaxType.PCT_TOTAL.value
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data["name"],
            asset_class=data["asset_class"],
            current_value=float(data["current_value"]),
            annual_roi_pct=float(data["annual_roi_pct"]),
            tax_type=TaxType(raw_type),
            tax_value=float(data.get("tax_value", 0)),
            cost_basis=float(data.get("cost_basis", 0)),
            monthly_contribution=float(data.get("monthly_contribution", 0)),
            notes=data.get("notes", ""),
        )
