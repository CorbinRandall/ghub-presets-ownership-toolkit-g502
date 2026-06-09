"""Shared update-blocker constants and hosts-file helpers."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .paths import archive_dir, default_presets_dir

STATE_FILENAME = "ghub-update-block.json"
HOSTS_MARKER = "# GHub Preset Toolkit update block"

# From Logitech updater binaries (Windows string scan; same endpoints on macOS).
UPDATE_HOSTS: tuple[str, ...] = (
    "pipeline.logitech.io",
    "updates.ghub.logitechg.com",
    "datapipeline.logitech.io",
    "stg-pipeline.np.logitech.io",
    "stg-datapipeline.np.logitech.io",
    "2pipeline.s3.amazonaws.com",
)


def state_file(library: Path | None = None) -> Path:
    root = library or default_presets_dir()
    path = archive_dir(root) / STATE_FILENAME
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def load_state(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def save_state(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def list_hosts_entries(hosts_file: Path) -> list[str]:
    if not hosts_file.is_file():
        return []
    active: list[str] = []
    for line in hosts_file.read_text(encoding="utf-8", errors="replace").splitlines():
        if HOSTS_MARKER not in line:
            continue
        parts = line.split()
        if len(parts) >= 2 and parts[1] in UPDATE_HOSTS:
            active.append(parts[1])
    return sorted(set(active))


def add_hosts_entries(hosts_file: Path) -> list[str]:
    if not hosts_file.is_file():
        raise RuntimeError(f"Hosts file not found: {hosts_file}")

    lines = hosts_file.read_text(encoding="utf-8", errors="replace").splitlines()
    existing = list_hosts_entries(hosts_file)
    actions: list[str] = []
    for host in UPDATE_HOSTS:
        if host in existing:
            continue
        lines.append(f"127.0.0.1 {host} {HOSTS_MARKER}")
        actions.append(f"hosts block {host}")

    if actions:
        text = "\n".join(lines).rstrip() + "\n"
        hosts_file.write_text(text, encoding="utf-8")
    return actions


def remove_hosts_entries(hosts_file: Path) -> list[str]:
    if not hosts_file.is_file():
        return []

    actions: list[str] = []
    kept: list[str] = []
    for line in hosts_file.read_text(encoding="utf-8", errors="replace").splitlines():
        if HOSTS_MARKER in line:
            parts = line.split()
            if len(parts) >= 2:
                actions.append(f"hosts remove {parts[1]}")
            continue
        kept.append(line)

    if actions:
        text = "\n".join(kept).rstrip()
        if text:
            text += "\n"
        hosts_file.write_text(text, encoding="utf-8")
    return actions


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
