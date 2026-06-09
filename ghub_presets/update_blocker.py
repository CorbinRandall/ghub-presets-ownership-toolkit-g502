"""Optional G Hub update blocker (Windows). See SECURITY.md."""

from __future__ import annotations

import ctypes
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .paths import archive_dir, default_presets_dir

UPDATER_SERVICE = "LGHUBUpdaterService"
UPDATER_EXE = "lghub_updater.exe"
SOFTWARE_MANAGER_EXE = "lghub_software_manager.exe"
STATE_FILENAME = "ghub-update-block.json"
FIREWALL_RULE_PREFIX = "GHub Preset Toolkit - Block"

# Referenced by lghub_updater.exe / lghub_software_manager.exe (string scan).
def _registry_locations() -> tuple[tuple[int, str], ...]:
    import winreg

    return (
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Logitech\GHUB"),
        (winreg.HKEY_CURRENT_USER, r"Software\Logitech\GHUB"),
    )

REGISTRY_DISABLE_VALUES: dict[str, int] = {
    "AutoUpdateCheckEnabled": 0,
    "AutoUpdateDownloadEnabled": 0,
    "updateEnabled": 0,
}

SERVICE_START_TYPES = {
    2: "automatic",
    3: "manual",
    4: "disabled",
}

SERVICE_START_KEYWORDS = {
    2: "auto",
    3: "demand",
    4: "disabled",
}


@dataclass(frozen=True)
class UpdateBlockStatus:
    platform_supported: bool
    is_admin: bool
    install_dir: Path | None
    updater_service_exists: bool
    updater_service_running: bool
    updater_service_start: int | None
    updater_process_running: bool
    firewall_rules: list[str]
    registry_values: dict[str, dict[str, int | None]]
    state_file: Path | None
    block_active: bool
    block_applied_at: str | None

    def summary_lines(self) -> list[str]:
        lines: list[str] = []
        if not self.platform_supported:
            lines.append("Update blocking is only implemented on Windows.")
            return lines

        lines.append(f"Administrator: {'yes' if self.is_admin else 'no (required to apply/remove block)'}")
        if self.install_dir:
            lines.append(f"G Hub install: {self.install_dir}")
        else:
            lines.append("G Hub install: not found under Program Files\\LGHUB")

        if self.updater_service_exists:
            start = SERVICE_START_TYPES.get(self.updater_service_start or 0, "unknown")
            run = "running" if self.updater_service_running else "stopped"
            lines.append(f"LGHUBUpdaterService: {run}, startup={start}")
        else:
            lines.append("LGHUBUpdaterService: not installed")

        lines.append(
            "lghub_updater.exe process: "
            + ("running" if self.updater_process_running else "not running")
        )

        if self.firewall_rules:
            lines.append(f"Toolkit firewall rules: {len(self.firewall_rules)} active")
            for rule in self.firewall_rules:
                lines.append(f"  - {rule}")
        else:
            lines.append("Toolkit firewall rules: none")

        if self.block_active:
            lines.append(f"Toolkit update block: ACTIVE (since {self.block_applied_at or 'unknown'})")
        else:
            lines.append("Toolkit update block: not active")

        for hive_name, values in self.registry_values.items():
            rendered = ", ".join(f"{k}={v}" for k, v in sorted(values.items()))
            lines.append(f"Registry {hive_name}: {rendered or '(no update keys set)'}")

        if self.state_file:
            lines.append(f"State file: {self.state_file}")
        return lines


def _is_windows_admin() -> bool:
    if sys.platform != "win32":
        return False
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except (AttributeError, OSError):
        return False


def _state_file(library: Path | None = None) -> Path:
    root = library or default_presets_dir()
    path = archive_dir(root) / STATE_FILENAME
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def ghub_install_dir() -> Path | None:
    if sys.platform != "win32":
        return None
    for base in (Path(r"C:\Program Files"), Path(r"C:\Program Files (x86)")):
        candidate = base / "LGHUB"
        if (candidate / UPDATER_EXE).is_file():
            return candidate
    return None


def _run_command(args: list[str], *, check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        capture_output=True,
        text=True,
        errors="replace",
        check=check,
    )


def _query_service() -> tuple[bool, bool, int | None]:
    if sys.platform != "win32":
        return False, False, None

    import winreg

    proc = _run_command(["sc.exe", "query", UPDATER_SERVICE])
    if proc.returncode != 0:
        return False, False, None
    running = "RUNNING" in (proc.stdout or "").upper()

    try:
        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            rf"SYSTEM\CurrentControlSet\Services\{UPDATER_SERVICE}",
        ) as key:
            start, _ = winreg.QueryValueEx(key, "Start")
            return True, running, int(start)
    except OSError:
        return True, running, None


def _set_service_start(start_type: int) -> None:
    keyword = SERVICE_START_KEYWORDS.get(start_type)
    if keyword is None:
        raise RuntimeError(f"Unsupported service start type: {start_type}")
    proc = _run_command(["sc.exe", "config", UPDATER_SERVICE, "start=", keyword])
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip()
        raise RuntimeError(f"Could not configure {UPDATER_SERVICE}: {detail}")


def _stop_service() -> None:
    _run_command(["sc.exe", "stop", UPDATER_SERVICE])


def _kill_updater_process() -> bool:
    proc = _run_command(["taskkill", "/IM", UPDATER_EXE, "/F"])
    return proc.returncode == 0


def _read_registry_values() -> dict[str, dict[str, int | None]]:
    import winreg

    result: dict[str, dict[str, int | None]] = {}
    for hive, subkey in _registry_locations():
        hive_name = "HKLM" if hive == winreg.HKEY_LOCAL_MACHINE else "HKCU"
        values: dict[str, int | None] = {}
        try:
            with winreg.OpenKey(hive, subkey) as key:
                for name in REGISTRY_DISABLE_VALUES:
                    try:
                        raw, reg_type = winreg.QueryValueEx(key, name)
                        if reg_type == winreg.REG_DWORD:
                            values[name] = int(raw)
                        else:
                            values[name] = None
                    except OSError:
                        values[name] = None
        except OSError:
            for name in REGISTRY_DISABLE_VALUES:
                values[name] = None
        result[hive_name] = values
    return result


def _write_registry_values(values: dict[str, int]) -> list[str]:
    import winreg

    actions: list[str] = []
    for hive, subkey in _registry_locations():
        hive_name = "HKLM" if hive == winreg.HKEY_LOCAL_MACHINE else "HKCU"
        try:
            with winreg.CreateKey(hive, subkey) as key:
                for name, value in values.items():
                    winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, int(value))
                    actions.append(f"registry {hive_name}\\{subkey} {name}={value}")
        except OSError as exc:
            raise RuntimeError(f"Could not write {hive_name}\\{subkey}: {exc}") from exc
    return actions


def _restore_registry_values(saved: dict[str, dict[str, int | None]]) -> list[str]:
    import winreg

    actions: list[str] = []
    hive_map = {
        "HKLM": winreg.HKEY_LOCAL_MACHINE,
        "HKCU": winreg.HKEY_CURRENT_USER,
    }
    subkey_map = {
        "HKLM": r"SOFTWARE\Logitech\GHUB",
        "HKCU": r"Software\Logitech\GHUB",
    }
    for hive_name, values in saved.items():
        hive = hive_map.get(hive_name)
        subkey = subkey_map.get(hive_name)
        if hive is None or subkey is None:
            continue
        try:
            with winreg.OpenKey(hive, subkey, 0, winreg.KEY_SET_VALUE) as key:
                for name, value in values.items():
                    if value is None:
                        try:
                            winreg.DeleteValue(key, name)
                            actions.append(f"registry delete {hive_name}\\{subkey} {name}")
                        except OSError:
                            pass
                    else:
                        winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, int(value))
                        actions.append(f"registry restore {hive_name}\\{subkey} {name}={value}")
        except OSError:
            if any(v is not None for v in values.values()):
                actions.append(f"registry skip {hive_name}\\{subkey} (key missing)")
    return actions


def _firewall_rule_names() -> list[str]:
    return [
        f"{FIREWALL_RULE_PREFIX} lghub_updater",
        f"{FIREWALL_RULE_PREFIX} lghub_software_manager",
    ]


def _list_firewall_rules() -> list[str]:
    if sys.platform != "win32":
        return []
    proc = _run_command(
        ["netsh", "advfirewall", "firewall", "show", "rule", "name=all"],
    )
    if proc.returncode != 0:
        return []
    active = [name for name in _firewall_rule_names() if name in (proc.stdout or "")]
    return active


def _add_firewall_rules(install_dir: Path) -> list[str]:
    actions: list[str] = []
    targets = (
        install_dir / UPDATER_EXE,
        install_dir / SOFTWARE_MANAGER_EXE,
    )
    for exe, rule_name in zip(targets, _firewall_rule_names(), strict=True):
        if not exe.is_file():
            continue
        proc = _run_command(
            [
                "netsh",
                "advfirewall",
                "firewall",
                "add",
                "rule",
                f"name={rule_name}",
                "dir=out",
                "action=block",
                f"program={exe}",
                "enable=yes",
            ],
        )
        if proc.returncode != 0:
            detail = (proc.stderr or proc.stdout or "").strip()
            raise RuntimeError(f"Could not add firewall rule '{rule_name}': {detail}")
        actions.append(f"firewall block outbound {exe.name}")
    return actions


def _remove_firewall_rules() -> list[str]:
    actions: list[str] = []
    for rule_name in _firewall_rule_names():
        proc = _run_command(
            ["netsh", "advfirewall", "firewall", "delete", "rule", f"name={rule_name}"],
        )
        if proc.returncode == 0:
            actions.append(f"firewall remove {rule_name}")
    return actions


def _updater_process_running() -> bool:
    proc = _run_command(["tasklist", "/FI", f"IMAGENAME eq {UPDATER_EXE}", "/NH"])
    text = (proc.stdout or "").lower()
    return UPDATER_EXE.lower() in text and "no tasks" not in text


def _load_state(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def get_update_block_status(*, library: Path | None = None) -> UpdateBlockStatus:
    state_path = _state_file(library)
    state = _load_state(state_path)
    exists, running, start = _query_service()
    firewall = _list_firewall_rules()
    block_active = bool(state and state.get("active")) or bool(firewall)
    return UpdateBlockStatus(
        platform_supported=sys.platform == "win32",
        is_admin=_is_windows_admin(),
        install_dir=ghub_install_dir(),
        updater_service_exists=exists,
        updater_service_running=running,
        updater_service_start=start,
        updater_process_running=_updater_process_running(),
        firewall_rules=firewall,
        registry_values=_read_registry_values(),
        state_file=state_path if state_path.is_file() else None,
        block_active=block_active,
        block_applied_at=state.get("appliedAt") if state else None,
    )


def apply_update_block(*, library: Path | None = None) -> list[str]:
    if sys.platform != "win32":
        raise RuntimeError("G Hub update blocking is only supported on Windows.")

    if not _is_windows_admin():
        raise RuntimeError(
            "Administrator privileges are required to block G Hub updates.\n"
            "Re-run from an elevated Command Prompt or use "
            "Executables\\windows\\0c Block G Hub Updates.bat"
        )

    install_dir = ghub_install_dir()
    if install_dir is None:
        raise RuntimeError(
            "Could not find G Hub under Program Files\\LGHUB. Is Logitech G Hub installed?"
        )

    state_path = _state_file(library)
    if _load_state(state_path):
        raise RuntimeError(
            f"Update block already active. State file: {state_path}\n"
            "Run 'ghub-presets unblock-updates' first if you want to re-apply."
        )

    exists, _, original_start = _query_service()
    if not exists:
        raise RuntimeError(
            f"{UPDATER_SERVICE} is not installed. G Hub may use a different update mechanism."
        )

    saved_registry = _read_registry_values()
    actions: list[str] = []
    registry_written = False
    firewall_added = False

    # Do NOT stop or disable LGHUBUpdaterService — G Hub fails to load without it.
    try:
        actions.extend(_add_firewall_rules(install_dir))
        firewall_added = True

        actions.extend(_write_registry_values(REGISTRY_DISABLE_VALUES))
        registry_written = True

        state = {
            "active": True,
            "appliedAt": datetime.now(timezone.utc).isoformat(),
            "installDir": str(install_dir),
            "serviceStartType": original_start,
            "registry": saved_registry,
            "firewallRules": _firewall_rule_names(),
            "toolkitVersion": "1.0.0",
        }
        state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
        actions.append(f"state saved: {state_path}")
        actions.append(
            f"note: {UPDATER_SERVICE} left running (required for G Hub to start)"
        )
        return actions
    except Exception:
        if registry_written:
            _restore_registry_values(saved_registry)
        if firewall_added:
            _remove_firewall_rules()
        raise


def remove_update_block(*, library: Path | None = None) -> list[str]:
    if sys.platform != "win32":
        raise RuntimeError("G Hub update blocking is only supported on Windows.")

    if not _is_windows_admin():
        raise RuntimeError(
            "Administrator privileges are required to unblock G Hub updates.\n"
            "Re-run from an elevated Command Prompt or use "
            "Executables\\windows\\0d Unblock G Hub Updates.bat"
        )

    state_path = _state_file(library)
    state = _load_state(state_path)
    actions: list[str] = []

    exists, _, _ = _query_service()
    if exists:
        start_type = 2
        if state and state.get("serviceStartType") is not None:
            start_type = int(state["serviceStartType"])
        _set_service_start(start_type)
        actions.append(f"restore {UPDATER_SERVICE} startup={SERVICE_START_TYPES.get(start_type, start_type)}")

    actions.extend(_remove_firewall_rules())

    if state and state.get("registry"):
        actions.extend(_restore_registry_values(state["registry"]))

    if state_path.is_file():
        state_path.unlink()
        actions.append(f"state removed: {state_path}")

    if not actions:
        actions.append("No toolkit update block state found (nothing to undo).")
    return actions
