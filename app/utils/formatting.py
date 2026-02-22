"""Number formatting utilities and comma-aware CTkEntry widget."""
from __future__ import annotations
import platform
import customtkinter as ctk


def setup_matplotlib_fonts() -> None:
    """Point matplotlib at a system font that supports Korean (CJK) glyphs."""
    import matplotlib
    import matplotlib.font_manager as fm
    if platform.system() == "Darwin":
        candidates = ["Apple SD Gothic Neo", "AppleGothic", "Nanum Gothic"]
    elif platform.system() == "Windows":
        candidates = ["Malgun Gothic", "Gulim", "Batang"]
    else:
        candidates = ["Noto Sans CJK KR", "NanumGothic", "UnDotum"]

    available = {f.name for f in fm.fontManager.ttflist}
    for font in candidates:
        if font in available:
            matplotlib.rcParams["font.family"] = font
            break
    matplotlib.rcParams["axes.unicode_minus"] = False


def fmt(value: float, symbol: str) -> str:
    """Format a value as currency with no decimal places (KRW style)."""
    return f"{symbol}{value:,.0f}"


def parse_number(text: str) -> float:
    """Strip commas and parse to float."""
    cleaned = text.replace(",", "").strip()
    return float(cleaned) if cleaned else 0.0


class CommaEntry(ctk.CTkEntry):
    """CTkEntry that auto-formats integers with thousands commas as the user types."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.bind("<KeyRelease>", self._reformat)

    def _reformat(self, event=None) -> None:
        if event and event.keysym in ("Left", "Right", "Home", "End", "Tab", "Return", "Escape"):
            return

        # Try to preserve cursor position via internal tk.Entry
        try:
            internal = self._entry
            cursor = internal.index("insert")
            before = internal.get()[:cursor]
            digits_before = sum(1 for c in before if c.isdigit())
        except Exception:
            internal = None
            digits_before = None

        raw = self.get().replace(",", "")
        all_digits = "".join(c for c in raw if c.isdigit())
        if not all_digits:
            return

        try:
            formatted = f"{int(all_digits):,}"
        except ValueError:
            return

        self.delete(0, "end")
        self.insert(0, formatted)

        if internal is not None and digits_before is not None:
            # find position of digits_before-th digit in formatted string
            count = 0
            new_pos = len(formatted)
            for i, ch in enumerate(formatted):
                if ch.isdigit():
                    count += 1
                    if count == digits_before:
                        new_pos = i + 1
                        break
            try:
                internal.icursor(new_pos)
            except Exception:
                pass

    def get_number(self) -> float:
        return parse_number(self.get())

    def set_number(self, value: float) -> None:
        self.delete(0, "end")
        if value:
            self.insert(0, f"{int(round(value)):,}")
