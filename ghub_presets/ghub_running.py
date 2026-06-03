"""Detect whether Logitech G Hub is running."""

from __future__ import annotations

import subprocess
import sys


GHUB_PROCESS_NAMES = (
    "lghub",
    "lghub_agent",
    "lghub_ui",
    "lghub_updater",
    "LGHUB",
    "lghub.exe",
    "lghub_agent.exe",
    "lghub_ui.exe",
)


def is_ghub_running() -> bool:
    if sys.platform == "win32":
        try:
            out = subprocess.check_output(
                ["tasklist"],
                stderr=subprocess.DEVNULL,
                text=True,
                errors="replace",
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
        lower = out.lower()
        return any(name.lower() in lower for name in GHUB_PROCESS_NAMES)

    try:
        out = subprocess.check_output(["ps", "-axo", "comm="], text=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

    running = {line.strip().lower() for line in out.splitlines() if line.strip()}
    for name in GHUB_PROCESS_NAMES:
        base = name.lower().removesuffix(".exe")
        if base in running:
            return True
    return False


def require_ghub_stopped() -> None:
    if is_ghub_running():
        raise RuntimeError(
            "Logitech G Hub is running. Quit G Hub completely before export/import/pull."
        )
