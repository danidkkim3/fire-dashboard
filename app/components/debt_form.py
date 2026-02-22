"""Debt add/edit modal."""
from __future__ import annotations
from typing import Callable, Optional
import customtkinter as ctk
from app.models.debt import Debt, DEBT_CLASSES
from app.utils.formatting import CommaEntry


class DebtFormModal(ctk.CTkToplevel):
    def __init__(
        self,
        master,
        app,
        on_save: Callable[[Debt], None],
        debt: Optional[Debt] = None,
    ):
        super().__init__(master)
        self._app = app
        self._on_save = on_save
        self._debt = debt
        p = app.palette

        self.title("Edit Debt" if debt else "Add Debt")
        self.geometry("480x600")
        self.resizable(False, False)
        self.configure(fg_color=p["bg"])
        self.grab_set()
        self.focus_force()

        self._build(p)
        if debt:
            self._populate(debt)

    def _build(self, p: dict) -> None:
        pad = {"padx": 20, "pady": 6}

        ctk.CTkLabel(self, text="Debt Name", font=ctk.CTkFont(size=12),
                     text_color=p["subtext"], anchor="w").pack(fill="x", padx=20, pady=(20, 0))
        self._name = ctk.CTkEntry(self, placeholder_text="e.g. Apartment Mortgage",
                                  fg_color=p["card"], border_color=p["border"], text_color=p["text"])
        self._name.pack(fill="x", **pad)

        ctk.CTkLabel(self, text="Debt Class", font=ctk.CTkFont(size=12),
                     text_color=p["subtext"], anchor="w").pack(fill="x", padx=20, pady=(8, 0))
        self._class_var = ctk.StringVar(value=DEBT_CLASSES[0])
        ctk.CTkOptionMenu(self, values=DEBT_CLASSES, variable=self._class_var,
                          fg_color=p["card"], button_color=p["accent"],
                          text_color=p["text"]).pack(fill="x", **pad)

        ctk.CTkLabel(self, text="Current Balance (₩)", font=ctk.CTkFont(size=12),
                     text_color=p["subtext"], anchor="w").pack(fill="x", padx=20, pady=(8, 0))
        self._balance = CommaEntry(self, placeholder_text="0",
                                   fg_color=p["card"], border_color=p["border"], text_color=p["text"])
        self._balance.pack(fill="x", **pad)

        ctk.CTkLabel(self, text="Annual Interest Rate (%)", font=ctk.CTkFont(size=12),
                     text_color=p["subtext"], anchor="w").pack(fill="x", padx=20, pady=(8, 0))
        self._rate = ctk.CTkEntry(self, placeholder_text="3.5",
                                  fg_color=p["card"], border_color=p["border"], text_color=p["text"])
        self._rate.pack(fill="x", **pad)

        ctk.CTkLabel(self, text="Monthly Payment (₩)", font=ctk.CTkFont(size=12),
                     text_color=p["subtext"], anchor="w").pack(fill="x", padx=20, pady=(8, 0))
        self._payment = CommaEntry(self, placeholder_text="0",
                                   fg_color=p["card"], border_color=p["border"], text_color=p["text"])
        self._payment.pack(fill="x", **pad)

        ctk.CTkLabel(self, text="Notes (optional)", font=ctk.CTkFont(size=12),
                     text_color=p["subtext"], anchor="w").pack(fill="x", padx=20, pady=(8, 0))
        self._notes = ctk.CTkEntry(self, fg_color=p["card"], border_color=p["border"],
                                   text_color=p["text"])
        self._notes.pack(fill="x", **pad)

        self._error_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=11),
                                         text_color=p["red"])
        self._error_label.pack()

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=12)
        ctk.CTkButton(btn_row, text="Cancel", fg_color=p["card"],
                      text_color=p["subtext"], hover_color=p["button_hover"],
                      command=self.destroy).pack(side="left", expand=True, padx=(0, 8))
        ctk.CTkButton(btn_row, text="Save Debt", fg_color=p["red"],
                      hover_color="#c0392b", text_color="#ffffff",
                      command=self._save).pack(side="left", expand=True)

    def _populate(self, debt: Debt) -> None:
        self._name.insert(0, debt.name)
        self._class_var.set(debt.debt_class)
        self._balance.set_number(debt.balance)
        self._rate.insert(0, str(debt.annual_interest_rate))
        self._payment.set_number(debt.monthly_payment)
        self._notes.insert(0, debt.notes)

    def _save(self) -> None:
        try:
            name = self._name.get().strip()
            if not name:
                raise ValueError("Name is required.")
            balance = self._balance.get_number()
            rate = float(self._rate.get() or "0")
            payment = self._payment.get_number()
            if balance < 0:
                raise ValueError("Balance cannot be negative.")
            if rate < 0:
                raise ValueError("Interest rate cannot be negative.")
            if payment < 0:
                raise ValueError("Payment cannot be negative.")

            debt = Debt(
                id=self._debt.id if self._debt else str(__import__("uuid").uuid4()),
                name=name,
                debt_class=self._class_var.get(),
                balance=balance,
                annual_interest_rate=rate,
                monthly_payment=payment,
                notes=self._notes.get().strip(),
            )
            self._on_save(debt)
            self.destroy()
        except ValueError as e:
            self._error_label.configure(text=str(e))
