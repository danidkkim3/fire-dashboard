"""Single debt row card widget."""
from __future__ import annotations
from typing import Callable
import customtkinter as ctk
from app.models.debt import Debt
from app.utils.formatting import fmt


class DebtCard(ctk.CTkFrame):
    def __init__(
        self,
        master,
        debt: Debt,
        app,
        on_edit: Callable[[Debt], None],
        on_delete: Callable[[str], None],
        **kwargs,
    ):
        p = app.palette
        kwargs.setdefault("fg_color", p["card"])
        kwargs.setdefault("corner_radius", 10)
        super().__init__(master, **kwargs)
        self._app = app

        sym = app.settings.currency_symbol

        # red accent bar
        bar = ctk.CTkFrame(self, fg_color=p["red"], width=4, corner_radius=2)
        bar.pack(side="left", fill="y", padx=(6, 10), pady=8)

        info = ctk.CTkFrame(self, fg_color="transparent")
        info.pack(side="left", fill="both", expand=True, pady=8)

        name_row = ctk.CTkFrame(info, fg_color="transparent")
        name_row.pack(fill="x")
        ctk.CTkLabel(
            name_row, text=debt.name,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=p["text"], anchor="w",
        ).pack(side="left")
        ctk.CTkLabel(
            name_row, text=f"  [{debt.debt_class}]",
            font=ctk.CTkFont(size=11), text_color=p["subtext"], anchor="w",
        ).pack(side="left")

        # months remaining display
        mr = debt.months_remaining
        if mr == float("inf"):
            mr_str = "Never paid off"
        elif mr <= 0:
            mr_str = "Paid off"
        else:
            years, months = divmod(int(mr), 12)
            mr_str = f"{years}y {months}m remaining" if years else f"{months}m remaining"

        detail_row = ctk.CTkFrame(info, fg_color="transparent")
        detail_row.pack(fill="x", pady=(2, 0))
        ctk.CTkLabel(
            detail_row,
            text=(
                f"Balance {fmt(debt.balance, sym)}  •  "
                f"Rate {debt.annual_interest_rate:.2f}%/yr  •  "
                f"Payment {fmt(debt.monthly_payment, sym)}/mo  •  "
                f"{mr_str}"
            ),
            font=ctk.CTkFont(size=11), text_color=p["subtext"], anchor="w",
        ).pack(side="left")

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(side="right", padx=8, pady=8)
        ctk.CTkButton(
            btn_frame, text="Edit", width=56, height=28,
            fg_color=p["accent"], hover_color=p["button_hover"],
            font=ctk.CTkFont(size=11),
            command=lambda: on_edit(debt),
        ).pack(side="left", padx=4)
        ctk.CTkButton(
            btn_frame, text="Delete", width=60, height=28,
            fg_color=p["red"], hover_color="#c0392b",
            font=ctk.CTkFont(size=11),
            command=lambda: on_delete(debt.id),
        ).pack(side="left")
