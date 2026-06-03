"""G502 wired and Lightspeed device metadata."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DeviceConfig:
    key: str
    model_id: str
    slot_prefix: str
    pid: int
    hid_index: int
    label: str


DEVICES: dict[str, DeviceConfig] = {
    "g502": DeviceConfig(
        key="g502",
        model_id="g502_spectrum",
        slot_prefix="g502spectrum_",
        pid=0xC332,
        hid_index=0xFF,
        label="G502 Proteus Spectrum / Gaming Mouse G502 (wired)",
    ),
    "g502-hero": DeviceConfig(
        key="g502-hero",
        model_id="g502_spectrum",
        slot_prefix="g502spectrum_",
        pid=0xC08B,
        hid_index=0xFF,
        label="G502 Hero (wired, alternate PID)",
    ),
    "g502wireless": DeviceConfig(
        key="g502wireless",
        model_id="g502wireless",
        slot_prefix="g502wireless_",
        pid=0xC08D,
        hid_index=0xFF,
        label="G502 Lightspeed (USB cable)",
    ),
    "g502wireless-dongle": DeviceConfig(
        key="g502wireless-dongle",
        model_id="g502wireless",
        slot_prefix="g502wireless_",
        pid=0xC539,
        hid_index=0x01,
        label="G502 Lightspeed (wireless receiver)",
    ),
}

SLOT_PREFIX_BY_MODEL = {
    cfg.model_id: cfg.slot_prefix for cfg in DEVICES.values()
}

# G502 button slots in G Hub assignment naming (g1..g11 + shifted layers).
G502_BUTTONS = [f"g{i}" for i in range(1, 12)]


def get_device(key: str) -> DeviceConfig:
    if key not in DEVICES:
        known = ", ".join(sorted(DEVICES))
        raise ValueError(f"Unknown device {key!r}. Known: {known}")
    return DEVICES[key]


def slot_prefix_for_model(model_id: str) -> str | None:
    return SLOT_PREFIX_BY_MODEL.get(model_id)


def remap_slot_id(slot_id: str, from_prefix: str, to_prefix: str) -> str:
    if slot_id.startswith(from_prefix):
        return to_prefix + slot_id[len(from_prefix) :]
    return slot_id
