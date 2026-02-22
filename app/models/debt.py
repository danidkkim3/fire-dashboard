"""Debt data model."""
from __future__ import annotations
import math
from dataclasses import dataclass, field
import uuid


DEBT_CLASSES = ["Mortgage", "Student Loan", "Auto Loan", "Credit Card", "Personal Loan", "Other"]


@dataclass
class Debt:
    name: str
    debt_class: str
    balance: float
    annual_interest_rate: float
    monthly_payment: float
    notes: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    @property
    def monthly_interest_cost(self) -> float:
        return self.balance * (self.annual_interest_rate / 100 / 12)

    @property
    def months_remaining(self) -> float:
        if self.balance <= 0 or self.monthly_payment <= 0:
            return 0.0
        rate = self.annual_interest_rate / 100 / 12
        if rate == 0:
            return self.balance / self.monthly_payment
        monthly_interest = self.balance * rate
        if self.monthly_payment <= monthly_interest:
            return float("inf")
        return -math.log(1 - self.balance * rate / self.monthly_payment) / math.log(1 + rate)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "debt_class": self.debt_class,
            "balance": self.balance,
            "annual_interest_rate": self.annual_interest_rate,
            "monthly_payment": self.monthly_payment,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Debt":
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data["name"],
            debt_class=data.get("debt_class", "Other"),
            balance=float(data["balance"]),
            annual_interest_rate=float(data["annual_interest_rate"]),
            monthly_payment=float(data["monthly_payment"]),
            notes=data.get("notes", ""),
        )
