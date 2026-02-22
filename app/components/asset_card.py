"""Single asset row card widget."""
from __future__ import annotations
from typing import Callable
import customtkinter as ctk
from app.models.asset import Asset, TaxType
from app.utils.formatting import fmt


def _future_value(asset: Asset, months: int) -> float:
    """
    Future after-tax value using the standard compound interest formula
    with regular monthly contributions (복리):
      FV = PV × (1+r)^n  +  PMT × ((1+r)^n − 1) / r
    """
    monthly_rate = (1 + max(asset.after_tax_roi_pct, 0) / 100) ** (1 / 12) - 1
    pv = asset.after_tax_value
    pmt = asset.monthly_contribution
    n = months
    if monthly_rate == 0:
        return pv + pmt * n
    factor = (1 + monthly_rate) ** n
    return pv * factor + pmt * (factor - 1) / monthly_rate


_PROJECTIONS = [
    ("1년", 12),
    ("3년", 36),
    ("5년", 60),
    ("10년", 120),
    ("15년", 180),
]


class AssetCard(ctk.CTkFrame):
    def __init__(
        self,
        master,
        asset: Asset,
        app,
        on_edit: Callable[[Asset], None],
        on_delete: Callable[[str], None],
        **kwargs,
    ):
        p = app.palette
        kwargs.setdefault("fg_color", p["card"])
        kwargs.setdefault("corner_radius", 10)
        super().__init__(master, **kwargs)
        self._app = app

        sym = app.settings.currency_symbol

        # color bar
        color_map = {
            "Cash": p["chart_colors"][0],
            "Stocks": p["chart_colors"][1],
            "Real Estate": p["chart_colors"][2],
            "Crypto": p["chart_colors"][3],
            "Bonds": p["chart_colors"][4],
            "Other": p["chart_colors"][5],
        }
        bar_color = color_map.get(asset.asset_class, p["accent"])
        bar = ctk.CTkFrame(self, fg_color=bar_color, width=4, corner_radius=2)
        bar.pack(side="left", fill="y", padx=(6, 10), pady=8)

        # info block
        info = ctk.CTkFrame(self, fg_color="transparent")
        info.pack(side="left", fill="both", expand=True, pady=8)

        # ── row 1: name + class ────────────────────────────────────────────
        name_row = ctk.CTkFrame(info, fg_color="transparent")
        name_row.pack(fill="x")
        ctk.CTkLabel(
            name_row, text=asset.name,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=p["text"], anchor="w",
        ).pack(side="left")
        ctk.CTkLabel(
            name_row, text=f"  [{asset.asset_class}]",
            font=ctk.CTkFont(size=11), text_color=p["subtext"], anchor="w",
        ).pack(side="left")

        # ── row 2: value · ROI · contribution · tax · after-tax ───────────
        tax_label = {
            TaxType.PCT_TOTAL:        f"Tax {asset.tax_value:.1f}% of total",
            TaxType.PCT_APPRECIATION: f"Tax {asset.tax_value:.1f}% on gain (basis {fmt(asset.cost_basis, sym)})",
            TaxType.FLAT_DOLLAR:      f"Tax {fmt(asset.tax_value, sym)}/yr flat",
        }[asset.tax_type]

        contrib_str = f"  •  +{fmt(asset.monthly_contribution, sym)}/mo" if asset.monthly_contribution > 0 else ""

        detail_row = ctk.CTkFrame(info, fg_color="transparent")
        detail_row.pack(fill="x", pady=(2, 0))
        ctk.CTkLabel(
            detail_row,
            text=(f"{fmt(asset.current_value, sym)}  •  ROI {asset.annual_roi_pct:.1f}%"
                  f"{contrib_str}  •  {tax_label}  •  After-tax {fmt(asset.after_tax_value, sym)}"),
            font=ctk.CTkFont(size=11), text_color=p["subtext"], anchor="w",
        ).pack(side="left")

        # ── row 3: compound projections ────────────────────────────────────
        proj_row = ctk.CTkFrame(info, fg_color="transparent")
        proj_row.pack(fill="x", pady=(3, 0))

        ctk.CTkLabel(
            proj_row,
            text="복리 예측 →",
            font=ctk.CTkFont(size=11),
            text_color=p["subtext"], anchor="w",
        ).pack(side="left", padx=(0, 6))

        for label, months in _PROJECTIONS:
            fv = _future_value(asset, months)
            ctk.CTkLabel(
                proj_row,
                text=f"{label}: ",
                font=ctk.CTkFont(size=11),
                text_color=p["subtext"],
            ).pack(side="left")
            ctk.CTkLabel(
                proj_row,
                text=fmt(fv, sym),
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=p["green"],
            ).pack(side="left", padx=(0, 14))

        # ── buttons ────────────────────────────────────────────────────────
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(side="right", padx=8, pady=8)

        ctk.CTkButton(
            btn_frame, text="Edit", width=56, height=28,
            fg_color=p["accent"], hover_color=p["button_hover"],
            font=ctk.CTkFont(size=11),
            command=lambda: on_edit(asset),
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            btn_frame, text="Delete", width=60, height=28,
            fg_color=p["red"], hover_color="#c0392b",
            font=ctk.CTkFont(size=11),
            command=lambda: on_delete(asset.id),
        ).pack(side="left")
