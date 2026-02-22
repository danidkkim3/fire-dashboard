"""Assets view — CRUD list of assets."""
from __future__ import annotations
import customtkinter as ctk
from app.views.base_view import BaseView
from app.components.asset_card import AssetCard
from app.components.asset_form import AssetFormModal
from app.models.asset import Asset
from app.utils.formatting import fmt


class AssetsView(BaseView):
    def build(self) -> None:
        p = self._app.palette
        self.configure(fg_color=p["bg"])
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 0))
        ctk.CTkLabel(
            header, text="Assets",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=p["text"],
        ).pack(side="left")
        self._add_btn = ctk.CTkButton(
            header, text="+ Add Asset", fg_color=p["accent"],
            hover_color=p["button_hover"], text_color="#ffffff",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._open_add_modal,
        )
        self._add_btn.pack(side="right")

        # scrollable list
        self._scroll = ctk.CTkScrollableFrame(
            self, fg_color=p["bg"], corner_radius=0,
        )
        self._scroll.grid(row=1, column=0, sticky="nsew", padx=24, pady=16)
        self._scroll.grid_columnconfigure(0, weight=1)

        # footer totals
        self._footer = ctk.CTkFrame(self, fg_color=p["card"], corner_radius=12)
        self._footer.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 24))
        self._footer_label = ctk.CTkLabel(
            self._footer, text="", font=ctk.CTkFont(size=12),
            text_color=p["subtext"],
        )
        self._footer_label.pack(padx=16, pady=10)

    def refresh(self) -> None:
        p = self._app.palette
        self.configure(fg_color=p["bg"])
        self._scroll.configure(fg_color=p["bg"])
        self._footer.configure(fg_color=p["card"])

        for widget in list(self._scroll.winfo_children()):
            widget.destroy()

        portfolio = self._app.portfolio
        sym = self._app.settings.currency_symbol

        if not portfolio.assets:
            ctk.CTkLabel(
                self._scroll,
                text="No assets yet. Click '+ Add Asset' to get started.",
                font=ctk.CTkFont(size=13), text_color=p["subtext"],
            ).grid(row=0, column=0, pady=40)
        else:
            for i, asset in enumerate(portfolio.assets):
                card = AssetCard(
                    self._scroll, asset=asset, app=self._app,
                    on_edit=self._open_edit_modal,
                    on_delete=self._delete_asset,
                )
                card.grid(row=i, column=0, sticky="ew", pady=(0, 8))

        total = portfolio.total_value
        total_at = portfolio.total_after_tax_value
        total_contrib = sum(a.monthly_contribution for a in portfolio.assets)
        self._footer_label.configure(
            text=(f"Total Value: {fmt(total, sym)}    •    Total After-Tax: {fmt(total_at, sym)}"
                  f"    •    Monthly Contributions: {fmt(total_contrib, sym)}/mo"),
            text_color=p["subtext"],
        )

    def _open_add_modal(self) -> None:
        AssetFormModal(self, app=self._app, on_save=self._save_new_asset)

    def _open_edit_modal(self, asset: Asset) -> None:
        AssetFormModal(self, app=self._app, on_save=self._save_edited_asset, asset=asset)

    def _save_new_asset(self, asset: Asset) -> None:
        self._app.portfolio.add_asset(asset)
        self._app.save_data()
        self._app.refresh_active_view()

    def _save_edited_asset(self, asset: Asset) -> None:
        self._app.portfolio.update_asset(asset)
        self._app.save_data()
        self._app.refresh_active_view()

    def _delete_asset(self, asset_id: str) -> None:
        self._app.portfolio.delete_asset(asset_id)
        self._app.save_data()
        self._app.refresh_active_view()
