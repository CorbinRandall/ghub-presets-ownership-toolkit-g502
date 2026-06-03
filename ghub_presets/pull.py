"""Pull onboard profiles from Logitech mice via HID++."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .convert import omm_to_ghub_preset
from .devices import get_device
from .ghub_running import require_ghub_stopped


def _import_omm():
    try:
        from .omm.FeatureOnboardProfile import FeatureOnboardProfile
        from .omm.LogiHPP20 import LogiHPP20
    except ImportError as exc:
        raise RuntimeError(
            "Mouse pull requires hidapi. Install with: pip install hidapi"
        ) from exc
    return LogiHPP20, FeatureOnboardProfile


def pull_onboard_profile(
    device_key: str,
    slot: int,
    *,
    output: Path | None = None,
    profile_name: str | None = None,
) -> dict[str, Any]:
    require_ghub_stopped()
    device = get_device(device_key)
    LogiHPP20, FeatureOnboardProfile = _import_omm()

    dev = LogiHPP20(device.pid, "", "", [device.hid_index])
    omm = None
    try:
        omm = FeatureOnboardProfile(dev)
        if not omm.onboard_mode:
            omm.onboard_mode = True
        omm.dest_profile = slot
        if not omm.profile_enabled:
            raise RuntimeError(
                f"Onboard profile slot {slot} is disabled on the mouse. "
                f"Enable it in G Hub or with omm --enable."
            )
        data = omm.onboard_profile_to_bin()
        omm_json = omm.profile_bin_to_json(data)
    finally:
        if omm is not None:
            omm.close()
        else:
            dev.close()

    return omm_to_ghub_preset(
        omm_json,
        device,
        profile_name=profile_name or omm_json.get("profile_name"),
        slot=slot,
    )


def pull_to_file(
    device_key: str,
    slot: int,
    output: Path,
    *,
    profile_name: str | None = None,
) -> Path:
    preset = pull_onboard_profile(device_key, slot, profile_name=profile_name)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(preset, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return output


def list_connected_logitech_devices() -> list[dict[str, Any]]:
    LogiHPP20, _ = _import_omm()
    LogiHPP20.list_devices()
    return []


def _safe_name(name: str) -> str:
    import re

    safe = re.sub(r"[^\w\- ]+", "", name).strip().replace(" ", "_")
    return safe or "onboard_preset"
