"""Debts view — CRUD list of debts."""
from __future__ import annotations
import customtkinter as ctk
from app.views.base_view import BaseView
from app.components.debt_card import DebtCard
from app.components.debt_form import DebtFormModal
from app.models.debt import Debt
from app.utils.formatting import fmt


class DebtsView(BaseView):
    def build(self) -> None:
        p = self._app.palette
        self.configure(fg_color=p["bg"])
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 0))
        ctk.CTkLabel(
            header, text="Debts",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=p["text"],
        ).pack(side="left")
        self._add_btn = ctk.CTkButton(
            header, text="+ Add Debt",
            fg_color=p["red"], hover_color="#c0392b", text_color="#ffffff",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._open_add_modal,
        )
        self._add_btn.pack(side="right")

        self._scroll = ctk.CTkScrollableFrame(self, fg_color=p["bg"], corner_radius=0)
        self._scroll.grid(row=1, column=0, sticky="nsew", padx=24, pady=16)
        self._scroll.grid_columnconfigure(0, weight=1)

        self._footer = ctk.CTkFrame(self, fg_color=p["card"], corner_radius=12)
        self._footer.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 24))
        self._footer_label = ctk.CTkLabel(
            self._footer, text="", font=ctk.CTkFont(size=12), text_color=p["subtext"],
        )
        self._footer_label.pack(padx=16, pady=10)

    def refresh(self) -> None:
        p = self._app.palette
        self.configure(fg_color=p["bg"])
        self._scroll.configure(fg_color=p["bg"])
        self._footer.configure(fg_color=p["card"])

        for w in list(self._scroll.winfo_children()):
            w.destroy()

        sym = self._app.settings.currency_symbol
        debts = self._app.portfolio.debts

        if not debts:
            ctk.CTkLabel(
                self._scroll,
                text="No debts recorded. Click '+ Add Debt' to add one.",
                font=ctk.CTkFont(size=13), text_color=p["subtext"],
            ).grid(row=0, column=0, pady=40)
        else:
            for i, debt in enumerate(debts):
                card = DebtCard(
                    self._scroll, debt=debt, app=self._app,
                    on_edit=self._open_edit_modal,
                    on_delete=self._delete_debt,
                )
                card.grid(row=i, column=0, sticky="ew", pady=(0, 8))

        total_debt = self._app.portfolio.total_debt
        total_monthly = sum(d.monthly_payment for d in debts)
        self._footer_label.configure(
            text=f"Total Debt: {fmt(total_debt, sym)}    •    Total Monthly Payments: {fmt(total_monthly, sym)}/mo",
            text_color=p["subtext"],
        )

    def _open_add_modal(self) -> None:
        DebtFormModal(self, app=self._app, on_save=self._save_new_debt)

    def _open_edit_modal(self, debt: Debt) -> None:
        DebtFormModal(self, app=self._app, on_save=self._save_edited_debt, debt=debt)

    def _save_new_debt(self, debt: Debt) -> None:
        self._app.portfolio.add_debt(debt)
        self._app.save_data()
        self._app.refresh_active_view()

    def _save_edited_debt(self, debt: Debt) -> None:
        self._app.portfolio.update_debt(debt)
        self._app.save_data()
        self._app.refresh_active_view()

    def _delete_debt(self, debt_id: str) -> None:
        self._app.portfolio.delete_debt(debt_id)
        self._app.save_data()
        self._app.refresh_active_view()
