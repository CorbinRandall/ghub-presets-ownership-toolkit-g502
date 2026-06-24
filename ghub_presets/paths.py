"""Cross-platform path detection for G Hub and preset toolkit."""

from __future__ import annotations

import os
import sys
from pathlib import Path

# User-facing preset library folder at toolkit root (empty in git; fill via Export).
PRESETS_DIR_NAME = "Put Presets Here"
LEGACY_PRESETS_DIR_NAME = "Presets"


def toolkit_root() -> Path | None:
    """Repo / toolkit root when launched from Executables (set by wrapper scripts)."""
    env = os.environ.get("GHUB_PRESET_TOOLKIT_ROOT")
    if env:
        return Path(env).expanduser().resolve()
    # Running from repo: parent of ghub_presets package
    here = Path(__file__).resolve().parent.parent
    if (
        (here / PRESETS_DIR_NAME).is_dir()
        or (here / LEGACY_PRESETS_DIR_NAME).is_dir()
        or (here / "Executables").is_dir()
    ):
        return here
    return None


def presets_folder_in_root(root: Path) -> Path:
    """Resolve preset library folder; prefer new name, fall back to legacy Presets/."""
    for name in (PRESETS_DIR_NAME, LEGACY_PRESETS_DIR_NAME):
        path = root / name
        if path.is_dir():
            return path
    return root / PRESETS_DIR_NAME


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
    """Folder of .lghub-preset.json files to import (toolkit: ./Put Presets Here)."""
    env = os.environ.get("GHUB_PRESETS_DIR")
    if env:
        return Path(env).expanduser().resolve()
    root = toolkit_root()
    if root:
        return presets_folder_in_root(root)
    return Path.home() / "LogitechPresets"


def presets_dir(library: Path | None = None) -> Path:
    """Same as default_presets_dir — flat import/export folder."""
    return library or default_presets_dir()


def onboard_dir(library: Path | None = None) -> Path:
    """Raw mouse pulls live under Put Presets Here/onboard/ (not imported)."""
    return presets_dir(library) / "onboard"


# Legacy names used elsewhere in the codebase
def profiles_dir(library: Path | None = None) -> Path:
    return presets_dir(library)


def reference_dir(library: Path | None = None) -> Path:
    return presets_dir(library) / "reference"


def archive_dir(library: Path | None = None) -> Path:
    return presets_dir(library) / "_archive"
