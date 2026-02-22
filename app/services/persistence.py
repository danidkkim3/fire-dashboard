"""JSON persistence — cross-platform data storage."""
from __future__ import annotations
import json
import os
import sys
from pathlib import Path

from app.models.portfolio import Portfolio
from app.models.settings import AppSettings

SCHEMA_VERSION = 1


def _data_path() -> Path:
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home()))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    folder = base / "FIREDashboard"
    folder.mkdir(parents=True, exist_ok=True)
    return folder / "data.json"


DATA_PATH: Path = _data_path()


def load() -> tuple[Portfolio, AppSettings]:
    """Load from disk. Returns defaults on any error."""
    try:
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            raw = json.load(f)
        portfolio = Portfolio.from_dict(raw.get("portfolio", {}))
        settings = AppSettings.from_dict(raw.get("settings", {}))
        return portfolio, settings
    except Exception:
        return Portfolio(), AppSettings()


def save(portfolio: Portfolio, settings: AppSettings) -> None:
    payload = {
        "version": SCHEMA_VERSION,
        "portfolio": portfolio.to_dict(),
        "settings": settings.to_dict(),
    }
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
