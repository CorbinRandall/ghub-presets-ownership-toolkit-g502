"""Cross-platform path detection for G Hub and preset library."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def ghub_settings_dir() -> Path:
    if sys.platform == "win32":
        local = os.environ.get("LOCALAPPDATA")
        if not local:
            raise RuntimeError("LOCALAPPDATA is not set")
        return Path(local) / "LGHUB"
    return Path.home() / "Library" / "Application Support" / "lghub"


def ghub_settings_db() -> Path:
    return ghub_settings_dir() / "settings.db"


def default_presets_dir() -> Path:
    env = os.environ.get("GHUB_PRESETS_DIR")
    if env:
        return Path(env).expanduser()
    return Path.home() / "LogitechPresets"
