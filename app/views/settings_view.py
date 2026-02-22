"""Settings view — FIRE goal, SWR, theme, chart DPI, export/import, CSV, custom colors."""
from __future__ import annotations
import csv
import json
import customtkinter as ctk
from tkinter import filedialog, messagebox
from app.views.base_view import BaseView
from app.services.persistence import DATA_PATH
from app.models.portfolio import Portfolio
from app.models.settings import AppSettings
from app.utils.formatting import CommaEntry

def _contrast_text(hex_color: str) -> str:
    """Return '#ffffff' or '#000000' depending on luminance of hex_color."""
    try:
        h = hex_color.lstrip("#")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
        return "#000000" if luminance > 140 else "#ffffff"
    except Exception:
        return "#ffffff"


# Keys shown in the color customizer (chart_colors excluded — list type)
COLOR_KEYS = [
    "bg", "card", "sidebar", "accent", "green", "red",
    "text", "subtext", "border", "button_hover",
]

DPI_OPTIONS = {
    "96 — Standard":    96,
    "120 — Medium":    120,
    "144 — Retina 1×": 144,
    "192 — Retina 2×": 192,
}
DPI_LABELS = list(DPI_OPTIONS.keys())


class SettingsView(BaseView):
    def build(self) -> None:
        p = self._app.palette
        self.configure(fg_color=p["bg"])
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            self, text="Settings",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=p["text"],
        ).grid(row=0, column=0, sticky="w", padx=24, pady=(24, 8))

        # scrollable container for all cards
        scroll = ctk.CTkScrollableFrame(self, fg_color=p["bg"], corner_radius=0)
        scroll.grid(row=1, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)
        self._scroll = scroll

        card = ctk.CTkFrame(scroll, fg_color=p["card"], corner_radius=12)
        card.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 16))
        card.grid_columnconfigure(1, weight=1)

        def row(r, label, widget_factory):
            ctk.CTkLabel(
                card, text=label, font=ctk.CTkFont(size=12),
                text_color=p["subtext"], anchor="w",
            ).grid(row=r, column=0, sticky="w", padx=16, pady=10)
            w = widget_factory(card)
            w.grid(row=r, column=1, sticky="ew", padx=16, pady=10)
            return w

        self._goal_entry = row(0, "Monthly FIRE Goal (₩)", lambda m: CommaEntry(
            m, fg_color=p["bg"], border_color=p["border"], text_color=p["text"],
        ))
        self._swr_entry = row(1, "Safe Withdrawal Rate (%)", lambda m: ctk.CTkEntry(
            m, fg_color=p["bg"], border_color=p["border"], text_color=p["text"],
        ))
        self._sym_entry = row(2, "Currency Symbol", lambda m: ctk.CTkEntry(
            m, fg_color=p["bg"], border_color=p["border"], text_color=p["text"], width=80,
        ))

        def make_theme_toggle(m):
            self._theme_var = ctk.StringVar(value=self._app.settings.theme)
            frame = ctk.CTkFrame(m, fg_color="transparent")
            ctk.CTkRadioButton(
                frame, text="Dark", variable=self._theme_var, value="dark",
                fg_color=p["accent"], text_color=p["text"],
            ).pack(side="left", padx=(0, 16))
            ctk.CTkRadioButton(
                frame, text="Light", variable=self._theme_var, value="light",
                fg_color=p["accent"], text_color=p["text"],
            ).pack(side="left")
            return frame

        row(3, "Theme", make_theme_toggle)

        def make_dpi_menu(m):
            current_label = next(
                (lbl for lbl, v in DPI_OPTIONS.items() if v == self._app.settings.chart_dpi),
                DPI_LABELS[2],  # default to 144
            )
            self._dpi_var = ctk.StringVar(value=current_label)
            return ctk.CTkOptionMenu(
                m, values=DPI_LABELS, variable=self._dpi_var,
                fg_color=p["bg"], button_color=p["accent"], text_color=p["text"],
            )

        row(4, "Chart Resolution (DPI)", make_dpi_menu)

        ctk.CTkButton(
            card, text="Save Settings", fg_color=p["accent"],
            hover_color=p["button_hover"], text_color="#ffffff",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._save_settings,
        ).grid(row=5, column=0, columnspan=2, sticky="e", padx=16, pady=16)

        # data file path
        path_card = ctk.CTkFrame(scroll, fg_color=p["card"], corner_radius=12)
        path_card.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 16))
        ctk.CTkLabel(path_card, text="Data File",
                     font=ctk.CTkFont(size=13, weight="bold"), text_color=p["text"],
                     ).pack(anchor="w", padx=16, pady=(12, 4))
        ctk.CTkLabel(path_card, text=str(DATA_PATH),
                     font=ctk.CTkFont(size=11), text_color=p["subtext"],
                     ).pack(anchor="w", padx=16, pady=(0, 12))

        # export / import
        io_card = ctk.CTkFrame(scroll, fg_color=p["card"], corner_radius=12)
        io_card.grid(row=3, column=0, sticky="ew", padx=24, pady=(0, 16))
        btn_row = ctk.CTkFrame(io_card, fg_color="transparent")
        btn_row.pack(padx=16, pady=12, anchor="w")
        ctk.CTkButton(btn_row, text="Export JSON", fg_color=p["accent"],
                      hover_color=p["button_hover"], text_color="#ffffff",
                      command=self._export).pack(side="left", padx=(0, 12))
        ctk.CTkButton(btn_row, text="Import JSON", fg_color=p["card"],
                      hover_color=p["button_hover"], text_color=p["text"],
                      border_width=1, border_color=p["border"],
                      command=self._import).pack(side="left", padx=(0, 12))
        ctk.CTkButton(btn_row, text="Export CSV", fg_color=p["card"],
                      hover_color=p["button_hover"], text_color=p["text"],
                      border_width=1, border_color=p["border"],
                      command=self._export_csv).pack(side="left")

        # ── custom colors ──────────────────────────────────────────────────
        color_card = ctk.CTkFrame(scroll, fg_color=p["card"], corner_radius=12)
        color_card.grid(row=4, column=0, sticky="ew", padx=24, pady=(0, 24))
        color_card.grid_columnconfigure(2, weight=1)

        ctk.CTkLabel(color_card, text="Customize Colors",
                     font=ctk.CTkFont(size=13, weight="bold"), text_color=p["text"],
                     ).grid(row=0, column=0, columnspan=3, sticky="w", padx=16, pady=(12, 4))
        ctk.CTkLabel(color_card, text="Click a swatch to open the color picker",
                     font=ctk.CTkFont(size=11), text_color=p["subtext"],
                     ).grid(row=1, column=0, columnspan=3, sticky="w", padx=16, pady=(0, 8))

        # picked_colors mirrors what will be applied; initialised from current palette
        self._picked_colors: dict[str, str] = {k: p.get(k, "#888888") for k in COLOR_KEYS}
        self._color_swatches: dict[str, ctk.CTkButton] = {}

        # 2-column grid of swatches so the card isn't too tall
        COLS = 2
        for i, key in enumerate(COLOR_KEYS):
            grid_row = i // COLS + 2          # +2 for the two header rows
            grid_col = (i % COLS) * 2         # 0 or 2 (label + swatch pairs)

            ctk.CTkLabel(color_card, text=key, font=ctk.CTkFont(size=12),
                         text_color=p["subtext"], anchor="w", width=100,
                         ).grid(row=grid_row, column=grid_col, sticky="w",
                                padx=(16, 4), pady=6)

            color = self._picked_colors[key]
            btn = ctk.CTkButton(
                color_card,
                text=color,
                width=110, height=30,
                fg_color=color,
                hover_color=color,
                text_color=_contrast_text(color),
                font=ctk.CTkFont(size=11),
                corner_radius=6,
                command=lambda k=key: self._pick_color(k),
            )
            btn.grid(row=grid_row, column=grid_col + 1, sticky="w",
                     padx=(0, 16), pady=6)
            self._color_swatches[key] = btn

        btn_row2 = ctk.CTkFrame(color_card, fg_color="transparent")
        btn_row2.grid(row=len(COLOR_KEYS) // COLS + 3, column=0, columnspan=4,
                      sticky="e", padx=16, pady=(8, 16))
        ctk.CTkButton(btn_row2, text="Apply Colors", fg_color=p["accent"],
                      hover_color=p["button_hover"], text_color="#ffffff",
                      font=ctk.CTkFont(size=13, weight="bold"),
                      command=self._apply_colors).pack(side="left", padx=(0, 10))
        ctk.CTkButton(btn_row2, text="Reset to Default", fg_color=p["card"],
                      hover_color=p["button_hover"], text_color=p["text"],
                      border_width=1, border_color=p["border"],
                      command=self._reset_colors).pack(side="left")

    def refresh(self) -> None:
        s = self._app.settings
        self._goal_entry.delete(0, "end")
        self._goal_entry.set_number(s.fire_monthly_goal)
        self._swr_entry.delete(0, "end")
        self._swr_entry.insert(0, str(s.safe_withdrawal_rate))
        self._sym_entry.delete(0, "end")
        self._sym_entry.insert(0, s.currency_symbol)
        self._theme_var.set(s.theme)
        current_label = next(
            (lbl for lbl, v in DPI_OPTIONS.items() if v == s.chart_dpi),
            DPI_LABELS[2],
        )
        self._dpi_var.set(current_label)

        # sync swatch buttons to current palette
        p = self._app.palette
        for key in COLOR_KEYS:
            color = p.get(key, "#888888")
            self._picked_colors[key] = color
            self._color_swatches[key].configure(
                fg_color=color, hover_color=color,
                text=color, text_color=_contrast_text(color),
            )

    def _save_settings(self) -> None:
        try:
            goal = self._goal_entry.get_number()
            swr = float(self._swr_entry.get())
            sym = self._sym_entry.get().strip() or "₩"
            theme = self._theme_var.get()
            dpi = DPI_OPTIONS[self._dpi_var.get()]
        except (ValueError, KeyError):
            messagebox.showerror("Invalid Input", "Please enter valid values.")
            return

        self._app.settings.fire_monthly_goal = goal
        self._app.settings.safe_withdrawal_rate = swr
        self._app.settings.currency_symbol = sym

        dpi_changed = dpi != self._app.settings.chart_dpi
        theme_changed = theme != self._app.settings.theme

        self._app.settings.chart_dpi = dpi
        self._app.settings.theme = theme

        if theme_changed:
            self._app.apply_theme(theme)
        elif dpi_changed:
            self._app.apply_chart_dpi(dpi)
        else:
            self._app.save_data()
            self._app.refresh_active_view()

    def _export(self) -> None:
        path = filedialog.asksaveasfilename(
            defaultextension=".json", filetypes=[("JSON", "*.json")],
        )
        if path:
            from app.services.persistence import save
            import shutil
            save(self._app.portfolio, self._app.settings)
            shutil.copy(DATA_PATH, path)
            messagebox.showinfo("Export", f"Data exported to:\n{path}")

    def _import(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            portfolio = Portfolio.from_dict(raw.get("portfolio", {}))
            settings = AppSettings.from_dict(raw.get("settings", {}))
            self._app.portfolio = portfolio
            self._app.settings = settings
            self._app.save_data()
            self._app.apply_theme(settings.theme)
            messagebox.showinfo("Import", "Data imported successfully.")
        except Exception as e:
            messagebox.showerror("Import Error", str(e))

    def _export_csv(self) -> None:
        directory = filedialog.askdirectory(title="Choose export folder")
        if not directory:
            return
        try:
            assets = self._app.portfolio.assets
            debts = self._app.portfolio.debts

            assets_path = f"{directory}/assets.csv"
            with open(assets_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Name", "Class", "Value", "Annual ROI%", "Tax Type",
                    "Tax Value", "Cost Basis", "Monthly Contribution", "After-Tax Value",
                ])
                for a in assets:
                    writer.writerow([
                        a.name,
                        a.asset_class,
                        a.current_value,
                        a.annual_roi_pct,
                        a.tax_type.name,
                        a.tax_value,
                        a.cost_basis,
                        a.monthly_contribution,
                        round(a.after_tax_value, 2),
                    ])

            debts_path = f"{directory}/debts.csv"
            with open(debts_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Name", "Class", "Balance", "Annual Interest Rate%", "Monthly Payment",
                ])
                for d in debts:
                    writer.writerow([
                        d.name,
                        d.debt_class,
                        d.balance,
                        d.annual_interest_rate,
                        d.monthly_payment,
                    ])

            messagebox.showinfo("Export CSV",
                                f"Exported:\n  {assets_path}\n  {debts_path}")
        except Exception as e:
            messagebox.showerror("Export CSV Error", str(e))

    # ── color helpers ──────────────────────────────────────────────────────

    def _pick_color(self, key: str) -> None:
        from tkinter import colorchooser
        current = self._picked_colors.get(key, "#888888")
        result = colorchooser.askcolor(color=current, title=f"Choose color — {key}")
        if result and result[1]:
            hex_color = result[1].lower()
            self._picked_colors[key] = hex_color
            self._color_swatches[key].configure(
                fg_color=hex_color, hover_color=hex_color,
                text=hex_color, text_color=_contrast_text(hex_color),
            )

    def _apply_colors(self) -> None:
        self._app.apply_custom_colors(dict(self._picked_colors))

    def _reset_colors(self) -> None:
        self._app.apply_custom_colors({})
