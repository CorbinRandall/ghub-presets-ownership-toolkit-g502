"""Convert omm onboard profile JSON to G Hub preset format."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from .devices import DeviceConfig, G502_BUTTONS
from .preset_format import FORMAT_VERSION

PRESET_PREFIX = "0f82f693-5b78-4cf5-867e-"

# HID modifier usage codes used by G Hub (partial).
MODIFIER_HID = {
    "lctrl": 224,
    "lshift": 225,
    "lalt": 226,
    "lgui": 227,
    "rctrl": 228,
    "rshift": 229,
    "ralt": 230,
    "rgui": 231,
}

# omm KeyCode name -> USB HID usage (subset used for single-key macros).
KEY_HID: dict[str, int] = {
    "a": 4,
    "b": 5,
    "c": 6,
    "d": 7,
    "e": 8,
    "f": 9,
    "g": 10,
    "h": 11,
    "i": 12,
    "j": 13,
    "k": 14,
    "l": 15,
    "m": 16,
    "n": 17,
    "o": 18,
    "p": 19,
    "q": 20,
    "r": 21,
    "s": 22,
    "t": 23,
    "u": 24,
    "v": 25,
    "w": 26,
    "x": 27,
    "y": 28,
    "z": 29,
    "f1": 58,
    "f2": 59,
    "f3": 60,
    "f4": 61,
    "f5": 62,
    "f6": 63,
    "f7": 64,
    "f8": 65,
    "f9": 66,
    "f10": 67,
    "f11": 68,
    "f12": 69,
    "enter": 40,
    "escape": 41,
    "backspace": 42,
    "tab": 43,
    "space": 44,
}


def _new_id() -> str:
    return str(uuid.uuid4())


def _preset_card_id(suffix: str) -> str:
    return f"{PRESET_PREFIX}{suffix}"


def _f_key_preset(n: int) -> str:
    return _preset_card_id(f"02{n:02x}00000000")


def _action_to_card(action: dict[str, Any], cards: list[dict[str, Any]], profile_id: str) -> str:
    kind = action.get("action")
    if kind == "button":
        value = action.get("value", "")
        if value in ("no_action", "no_button"):
            return _preset_card_id("090700000000")
        mouse_presets = {
            "left_button": "020100000000",  # fallback; often primary is separate slot
            "middle_button": "020300000000",
            "backward_button": "016800000000",
            "forward_button": "016900000000",
            "next_dpi": "090500000000",
            "cycle_dpi": "090500000000",
            "g_shift": "014000000000",
        }
        suffix = mouse_presets.get(value)
        if suffix:
            return _preset_card_id(suffix)
    elif kind == "key":
        key_name = (action.get("value") or "").lower()
        if key_name.startswith("f") and key_name[1:].isdigit():
            n = int(key_name[1:])
            if 1 <= n <= 24:
                return _f_key_preset(n)
        modifiers = []
        mod_str = action.get("modifier") or ""
        for part in mod_str.replace(",", "+").split("+"):
            part = part.strip().lower()
            if part in MODIFIER_HID:
                modifiers.append(MODIFIER_HID[part])
        code = KEY_HID.get(key_name)
        if code is not None:
            card_id = _new_id()
            label_parts = []
            if "lgui" in mod_str.lower():
                label_parts.append("⌘")
            if "lshift" in mod_str.lower():
                label_parts.append("⇧")
            label_parts.append(key_name.upper())
            cards.append(
                {
                    "id": card_id,
                    "name": "".join(label_parts) or key_name,
                    "attribute": "MACRO_PLAYBACK",
                    "profileId": profile_id,
                    "macro": {
                        "type": "KEYSTROKE",
                        "actionName": "".join(label_parts) or key_name,
                        "keystroke": {"code": code, "modifiers": modifiers},
                    },
                }
            )
            return card_id
    elif kind == "macro":
        card_id = _new_id()
        cards.append(
            {
                "id": card_id,
                "name": "Onboard Macro",
                "attribute": "MACRO_PLAYBACK",
                "profileId": profile_id,
                "macro": {
                    "type": "SEQUENCE",
                    "onboardable": True,
                    "sequence": {
                        "useDefaultDelay": True,
                        "defaultDelay": 50,
                        "useSimpleActions": True,
                        "simpleSequence": {"components": []},
                    },
                },
            }
        )
        return card_id

    return _preset_card_id("090700000000")


def _dpi_levels(raw: list[int]) -> list[int]:
    levels = [d for d in raw if d > 0]
    return levels[:5] if levels else [800, 1600, 3200]


def omm_to_ghub_preset(
    omm_json: dict[str, Any],
    device: DeviceConfig,
    *,
    profile_name: str | None = None,
    slot: int | None = None,
) -> dict[str, Any]:
    profile_id = _new_id()
    prefix = device.slot_prefix
    cards: list[dict[str, Any]] = []

    dpi_levels = _dpi_levels(omm_json.get("dpi_list", []))
    default_dpi = omm_json.get("dpi_default") or (dpi_levels[0] if dpi_levels else 800)
    active_dpi = default_dpi
    for d in dpi_levels:
        if d == default_dpi:
            active_dpi = d
            break

    mouse_settings_id = _new_id()
    report_rate = omm_json.get("extended_report_rate") or omm_json.get("report_rate") or 1000
    cards.append(
        {
            "id": mouse_settings_id,
            "name": "DEFAULT_CARD_NAME_MOUSE_SETTINGS",
            "attribute": "MOUSE_SETTINGS",
            "profileId": profile_id,
            "mouseSettings": {
                "dpiTable": {
                    "activeDpi": active_dpi,
                    "defaultDpi": default_dpi,
                    "levels": dpi_levels,
                    "shiftDpi": omm_json.get("dpi_shift") or default_dpi,
                },
                "reportRate": {"value": report_rate},
            },
        }
    )

    lighting_id = _new_id()
    cards.append(
        {
            "id": lighting_id,
            "name": "DEFAULT_CARD_NAME_FIRMWARE_LIGHTING_SETTINGS",
            "attribute": "FIRMWARE_LIGHTING_SETTINGS",
            "readOnly": True,
            "firmwareLightingSettings": {
                "effects": [
                    {
                        "id": "CYCLE",
                        "zoneType": "ZONE_BRANDING",
                        "cycleParams": {"intensity": 1, "periodInMs": 8000},
                    },
                    {
                        "id": "CYCLE",
                        "zoneType": "ZONE_PRIMARY",
                        "cycleParams": {"intensity": 1, "periodInMs": 8000},
                    },
                ]
            },
        }
    )

    assignments: list[dict[str, Any]] = []
    buttons = omm_json.get("buttons", [])
    buttons_gshift = omm_json.get("buttons_gshift", [])

    for idx, g_slot in enumerate(G502_BUTTONS):
        slot_base = f"{prefix}{g_slot}_m1"
        slot_shift = f"{prefix}{g_slot}_m1_shifted"
        if idx < len(buttons):
            card_id = _action_to_card(buttons[idx], cards, profile_id)
            assignments.append({"slotId": slot_base, "cardId": card_id})
        if idx < len(buttons_gshift):
            card_id = _action_to_card(buttons_gshift[idx], cards, profile_id)
            assignments.append({"slotId": slot_shift, "cardId": card_id})

    assignments.append({"slotId": f"{prefix}mouse_settings", "cardId": mouse_settings_id})
    assignments.append({"slotId": f"{prefix}lighting_setting_firmware", "cardId": lighting_id})

    display_name = profile_name or omm_json.get("profile_name") or f"Onboard Slot {slot or 1}"

    profile = {
        "id": profile_id,
        "name": display_name.strip("\x00").strip() or display_name,
        "applicationId": "",
        "activeForApplication": False,
        "assignments": assignments,
        "lightingCard": lighting_id,
    }

    readable_buttons = []
    for idx, g_slot in enumerate(G502_BUTTONS):
        if idx < len(buttons):
            readable_buttons.append({"slot": g_slot, "action": buttons[idx]})
        if idx < len(buttons_gshift):
            readable_buttons.append({"slot": f"{g_slot}_shifted", "action": buttons_gshift[idx]})

    return {
        "format": FORMAT_VERSION,
        "name": profile["name"],
        "sourceDevice": device.model_id,
        "slotPrefix": prefix,
        "exportedAt": datetime.now(timezone.utc).isoformat(),
        "profile": profile,
        "cards": cards,
        "ommRaw": omm_json,
        "readable": {
            "buttons": readable_buttons,
            "dpi": cards[0]["mouseSettings"],
            "onboardSlot": slot,
        },
    }
