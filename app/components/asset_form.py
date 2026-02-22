"""Asset add/edit modal (CTkToplevel)."""
from __future__ import annotations
from typing import Callable, Optional
import customtkinter as ctk
from app.models.asset import Asset, TaxType, BUILT_IN_CLASSES
from app.utils.formatting import CommaEntry


class AssetFormModal(ctk.CTkToplevel):
    def __init__(
        self,
        master,
        app,
        on_save: Callable[[Asset], None],
        asset: Optional[Asset] = None,
    ):
        super().__init__(master)
        self._app = app
        self._on_save = on_save
        self._asset = asset
        p = app.palette

        self.title("Edit Asset" if asset else "Add Asset")
        self.geometry("480x700")
        self.resizable(False, False)
        self.configure(fg_color=p["bg"])
        self.grab_set()
        self.focus_force()

        self._build(p)
        if asset:
            self._populate(asset)

    def _build(self, p: dict) -> None:
        pad = {"padx": 20, "pady": 6}

        ctk.CTkLabel(self, text="Asset Name", font=ctk.CTkFont(size=12),
                     text_color=p["subtext"], anchor="w").pack(fill="x", padx=20, pady=(20, 0))
        self._name = ctk.CTkEntry(self, placeholder_text="e.g. 삼성전자",
                                  fg_color=p["card"], border_color=p["border"],
                                  text_color=p["text"])
        self._name.pack(fill="x", **pad)

        ctk.CTkLabel(self, text="Asset Class", font=ctk.CTkFont(size=12),
                     text_color=p["subtext"], anchor="w").pack(fill="x", padx=20, pady=(8, 0))
        all_classes = self._app.portfolio.all_classes
        self._class_var = ctk.StringVar(value=all_classes[0])
        self._class_menu = ctk.CTkOptionMenu(
            self, values=all_classes + ["+ Custom"],
            variable=self._class_var,
            fg_color=p["card"], button_color=p["accent"],
            text_color=p["text"],
            command=self._on_class_change,
        )
        self._class_menu.pack(fill="x", **pad)

        self._custom_frame = ctk.CTkFrame(self, fg_color="transparent")
        ctk.CTkLabel(self._custom_frame, text="Custom Class Name",
                     font=ctk.CTkFont(size=12), text_color=p["subtext"], anchor="w").pack(fill="x")
        self._custom_entry = ctk.CTkEntry(self._custom_frame, placeholder_text="e.g. 리츠",
                                          fg_color=p["card"], border_color=p["border"],
                                          text_color=p["text"])
        self._custom_entry.pack(fill="x")

        ctk.CTkLabel(self, text="Current Value (₩)", font=ctk.CTkFont(size=12),
                     text_color=p["subtext"], anchor="w").pack(fill="x", padx=20, pady=(8, 0))
        self._value = CommaEntry(self, placeholder_text="0",
                                 fg_color=p["card"], border_color=p["border"],
                                 text_color=p["text"])
        self._value.pack(fill="x", **pad)

        ctk.CTkLabel(self, text="Annual ROI (%)", font=ctk.CTkFont(size=12),
                     text_color=p["subtext"], anchor="w").pack(fill="x", padx=20, pady=(8, 0))
        self._roi = ctk.CTkEntry(self, placeholder_text="7.0",
                                 fg_color=p["card"], border_color=p["border"],
                                 text_color=p["text"])
        self._roi.pack(fill="x", **pad)

        ctk.CTkLabel(self, text="Monthly Contribution (₩)", font=ctk.CTkFont(size=12),
                     text_color=p["subtext"], anchor="w").pack(fill="x", padx=20, pady=(8, 0))
        self._monthly_contrib = CommaEntry(self, placeholder_text="0",
                                           fg_color=p["card"], border_color=p["border"],
                                           text_color=p["text"])
        self._monthly_contrib.pack(fill="x", **pad)

        # ── Tax Type ──────────────────────────────────────────────────────
        ctk.CTkLabel(self, text="Tax Type", font=ctk.CTkFont(size=12),
                     text_color=p["subtext"], anchor="w").pack(fill="x", padx=20, pady=(8, 0))
        self._tax_type_var = ctk.StringVar(value=TaxType.PCT_TOTAL.value)
        tax_frame = ctk.CTkFrame(self, fg_color="transparent")
        tax_frame.pack(fill="x", padx=20)
        for value, label in [
            (TaxType.PCT_TOTAL.value,        "% of Total Value"),
            (TaxType.PCT_APPRECIATION.value, "% of Gain Only"),
            (TaxType.FLAT_DOLLAR.value,      "Flat ₩/yr"),
        ]:
            ctk.CTkRadioButton(
                tax_frame, text=label, variable=self._tax_type_var,
                value=value, text_color=p["text"], fg_color=p["accent"],
                command=self._on_tax_type_change,
            ).pack(side="left", padx=(0, 14))

        # ── Tax Rate / Amount ─────────────────────────────────────────────
        ctk.CTkLabel(self, text="Tax Rate / Amount", font=ctk.CTkFont(size=12),
                     text_color=p["subtext"], anchor="w").pack(fill="x", padx=20, pady=(8, 0))
        self._tax_val = ctk.CTkEntry(self, placeholder_text="0",
                                     fg_color=p["card"], border_color=p["border"],
                                     text_color=p["text"])
        self._tax_val.pack(fill="x", **pad)

        # ── Cost Basis (shown only for PCT_APPRECIATION) ──────────────────
        self._basis_frame = ctk.CTkFrame(self, fg_color="transparent")
        ctk.CTkLabel(self._basis_frame,
                     text="Cost Basis (₩)  — original purchase price",
                     font=ctk.CTkFont(size=12), text_color=p["subtext"], anchor="w").pack(fill="x")
        self._basis_entry = CommaEntry(self._basis_frame, placeholder_text="0",
                                       fg_color=p["card"], border_color=p["border"],
                                       text_color=p["text"])
        self._basis_entry.pack(fill="x")

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
        ctk.CTkButton(btn_row, text="Save Asset", fg_color=p["accent"],
                      hover_color=p["button_hover"], text_color="#ffffff",
                      command=self._save).pack(side="left", expand=True)

    def _on_class_change(self, value: str) -> None:
        if value == "+ Custom":
            self._custom_frame.pack(fill="x", padx=20, pady=(0, 4))
        else:
            self._custom_frame.pack_forget()

    def _on_tax_type_change(self) -> None:
        if self._tax_type_var.get() == TaxType.PCT_APPRECIATION.value:
            self._basis_frame.pack(fill="x", padx=20, pady=(0, 4))
        else:
            self._basis_frame.pack_forget()

    def _populate(self, asset: Asset) -> None:
        self._name.insert(0, asset.name)
        all_classes = self._app.portfolio.all_classes
        if asset.asset_class in all_classes:
            self._class_var.set(asset.asset_class)
        else:
            self._class_var.set("+ Custom")
            self._custom_frame.pack(fill="x", padx=20, pady=(0, 4))
            self._custom_entry.insert(0, asset.asset_class)
        self._value.set_number(asset.current_value)
        self._roi.insert(0, str(asset.annual_roi_pct))
        self._monthly_contrib.set_number(asset.monthly_contribution)
        self._tax_type_var.set(asset.tax_type.value)
        self._tax_val.insert(0, str(asset.tax_value))
        self._basis_entry.set_number(asset.cost_basis)
        self._notes.insert(0, asset.notes)
        self._on_tax_type_change()

    def _save(self) -> None:
        try:
            name = self._name.get().strip()
            if not name:
                raise ValueError("Name is required.")

            asset_class = self._class_var.get()
            if asset_class == "+ Custom":
                asset_class = self._custom_entry.get().strip()
                if not asset_class:
                    raise ValueError("Custom class name is required.")
                self._app.portfolio.add_custom_class(asset_class)

            value = self._value.get_number()
            roi = float(self._roi.get() or "0")
            monthly_contribution = self._monthly_contrib.get_number()
            tax_val = float(self._tax_val.get() or "0")
            tax_type = TaxType(self._tax_type_var.get())
            cost_basis = self._basis_entry.get_number() if tax_type == TaxType.PCT_APPRECIATION else 0.0
            notes = self._notes.get().strip()

            if value < 0:
                raise ValueError("Value cannot be negative.")
            if tax_val < 0:
                raise ValueError("Tax rate/amount cannot be negative.")
            if cost_basis < 0:
                raise ValueError("Cost basis cannot be negative.")

            asset = Asset(
                id=self._asset.id if self._asset else str(__import__("uuid").uuid4()),
                name=name, asset_class=asset_class,
                current_value=value, annual_roi_pct=roi,
                monthly_contribution=monthly_contribution,
                tax_type=tax_type, tax_value=tax_val,
                cost_basis=cost_basis, notes=notes,
            )
            self._on_save(asset)
            self.destroy()
        except ValueError as e:
            self._error_label.configure(text=str(e))
