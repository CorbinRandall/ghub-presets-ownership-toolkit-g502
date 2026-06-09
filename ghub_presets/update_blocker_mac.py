"""macOS G Hub update blocker."""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .update_blocker_common import (
    UPDATE_HOSTS,
    add_hosts_entries,
    list_hosts_entries,
    load_state,
    remove_hosts_entries,
    save_state,
    state_file,
    utc_now_iso,
)

HOSTS_FILE = Path("/etc/hosts")
GHUB_APP = Path("/Applications/lghub.app")
UPDATER_PLIST = Path("/Library/LaunchDaemons/com.logi.ghub.updater.plist")
UPDATER_LABEL = "com.logi.ghub.updater"
UPDATER_PROCESS = "lghub_updater"


@dataclass(frozen=True)
class UpdateBlockStatus:
    platform: str
    is_admin: bool
    install_dir: Path | None
    updater_daemon_installed: bool
    updater_daemon_running: bool
    updater_process_running: bool
    hosts_entries: list[str]
    state_file: Path | None
    block_active: bool
    block_applied_at: str | None

    def summary_lines(self) -> list[str]:
        lines = [
            "Platform: macOS",
            f"Administrator: {'yes' if self.is_admin else 'no (sudo required to apply/remove block)'}",
        ]
        if self.install_dir:
            lines.append(f"G Hub install: {self.install_dir}")
        else:
            lines.append("G Hub install: not found at /Applications/lghub.app")

        if self.updater_daemon_installed:
            run = "running" if self.updater_daemon_running else "not running"
            lines.append(f"{UPDATER_LABEL} launchd daemon: installed, {run}")
        else:
            lines.append(f"{UPDATER_LABEL} launchd daemon: not installed")

        lines.append(
            f"lghub_updater process: "
            + ("running" if self.updater_process_running else "not running")
        )

        if self.hosts_entries:
            lines.append(f"Toolkit hosts blocks: {len(self.hosts_entries)}")
            for host in self.hosts_entries:
                lines.append(f"  - {host}")
        else:
            lines.append("Toolkit hosts blocks: none")

        if self.block_active:
            lines.append(f"Toolkit update block: ACTIVE (since {self.block_applied_at or 'unknown'})")
        else:
            lines.append("Toolkit update block: not active")

        if self.state_file:
            lines.append(f"State file: {self.state_file}")
        return lines


def _is_admin() -> bool:
    try:
        return os.geteuid() == 0
    except AttributeError:
        return False


def ghub_install_dir() -> Path | None:
    return GHUB_APP if GHUB_APP.is_dir() else None


def _run_command(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, capture_output=True, text=True, errors="replace")


def _query_updater_daemon() -> tuple[bool, bool]:
    installed = UPDATER_PLIST.is_file()
    if not installed:
        return False, False

    proc = _run_command(["launchctl", "print", f"system/{UPDATER_LABEL}"])
    if proc.returncode != 0:
        return True, False
    text = (proc.stdout or "").lower()
    running = "state = running" in text or "\tstate = running" in text
    return True, running


def _updater_process_running() -> bool:
    proc = _run_command(["pgrep", "-x", UPDATER_PROCESS])
    return proc.returncode == 0


def _ensure_updater_daemon_ready() -> list[str]:
    """Keep updater daemon loaded — do not bootout/disable (G Hub may fail to start)."""
    actions: list[str] = []
    installed, running = _query_updater_daemon()
    if not installed:
        return actions
    if not running:
        proc = _run_command(["launchctl", "kickstart", "-k", f"system/{UPDATER_LABEL}"])
        if proc.returncode == 0:
            actions.append(f"kickstart system/{UPDATER_LABEL}")
    return actions


def get_update_block_status(*, library: Path | None = None) -> UpdateBlockStatus:
    path = state_file(library)
    state = load_state(path)
    installed, running = _query_updater_daemon()
    hosts = list_hosts_entries(HOSTS_FILE)
    block_active = bool(state and state.get("active")) or bool(hosts)
    return UpdateBlockStatus(
        platform="macos",
        is_admin=_is_admin(),
        install_dir=ghub_install_dir(),
        updater_daemon_installed=installed,
        updater_daemon_running=running,
        updater_process_running=_updater_process_running(),
        hosts_entries=hosts,
        state_file=path if path.is_file() else None,
        block_active=block_active,
        block_applied_at=state.get("appliedAt") if state else None,
    )


def apply_update_block(*, library: Path | None = None) -> list[str]:
    if not _is_admin():
        raise RuntimeError(
            "Administrator privileges are required to block G Hub updates.\n"
            "Re-run with sudo or use Executables/mac/0c Block G Hub Updates.command"
        )

    if ghub_install_dir() is None:
        raise RuntimeError("Could not find G Hub at /Applications/lghub.app.")

    path = state_file(library)
    if load_state(path):
        raise RuntimeError(
            f"Update block already active. State file: {path}\n"
            "Run 'ghub-presets unblock-updates' first if you want to re-apply."
        )

    actions: list[str] = []
    hosts_added = False
    try:
        actions.extend(_ensure_updater_daemon_ready())
        actions.extend(add_hosts_entries(HOSTS_FILE))
        hosts_added = True
        save_state(
            path,
            {
                "active": True,
                "platform": "macos",
                "appliedAt": utc_now_iso(),
                "installDir": str(GHUB_APP),
                "hosts": list(UPDATE_HOSTS),
                "updaterPlist": str(UPDATER_PLIST),
                "toolkitVersion": "1.0.0",
            },
        )
        actions.append(f"state saved: {path}")
        actions.append(
            f"note: {UPDATER_LABEL} stays loaded; updates blocked via /etc/hosts"
        )
        return actions
    except Exception:
        if hosts_added:
            remove_hosts_entries(HOSTS_FILE)
        raise


def remove_update_block(*, library: Path | None = None) -> list[str]:
    if not _is_admin():
        raise RuntimeError(
            "Administrator privileges are required to unblock G Hub updates.\n"
            "Re-run with sudo or use Executables/mac/0d Unblock G Hub Updates.command"
        )

    path = state_file(library)
    state = load_state(path)
    actions = remove_hosts_entries(HOSTS_FILE)
    if path.is_file():
        path.unlink()
        actions.append(f"state removed: {path}")
    if state:
        actions.extend(_ensure_updater_daemon_ready())
    if not actions:
        actions.append("No toolkit update block state found (nothing to undo).")
    return actions
