"""Color palettes for dark / light themes."""
from __future__ import annotations
from typing import Dict

PALETTES: Dict[str, Dict[str, str | list]] = {
    "dark": {
        "bg": "#0f0f23",
        "card": "#16213e",
        "sidebar": "#0d1b3e",
        "accent": "#4f8ef7",
        "green": "#00d4aa",
        "red": "#ff6b6b",
        "text": "#e8eaf6",
        "subtext": "#8892b0",
        "border": "#1e2d5a",
        "button_hover": "#2a3f7a",
        "chart_bg": "#16213e",
        "chart_colors": [
            "#4f8ef7", "#00d4aa", "#f7b84f", "#ff6b6b",
            "#a78bfa", "#fb923c", "#34d399", "#f472b6",
        ],
    },
    "light": {
        "bg":           "#f5f5f7",   # Apple systemGroupedBackground
        "card":         "#ffffff",   # pure white card surface
        "sidebar":      "#fafafa",   # ultra-light sidebar
        "accent":       "#007aff",   # Apple system blue
        "green":        "#34c759",   # Apple system green
        "red":          "#ff3b30",   # Apple system red
        "text":         "#1d1d1f",   # Apple primary label
        "subtext":      "#6e6e73",   # Apple secondary label
        "border":       "#d1d1d6",   # Apple separator
        "button_hover": "#e5e5ea",   # Apple tertiarySystemFill
        "chart_bg":     "#ffffff",
        "chart_colors": [
            "#007aff", "#34c759", "#ff9500", "#ff3b30",
            "#af52de", "#ff2d55", "#5ac8fa", "#ffcc00",
        ],
    },
}


def get_palette(theme: str = "dark", custom_colors: dict | None = None) -> Dict[str, str | list]:
    p = dict(PALETTES.get(theme, PALETTES["dark"]))
    if custom_colors:
        p.update(custom_colors)
    return p
