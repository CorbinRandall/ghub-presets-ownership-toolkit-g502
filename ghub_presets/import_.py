"""Import portable preset files into G Hub settings.db."""

from __future__ import annotations

import copy
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from .db import (
    backup_settings_db,
    detect_slot_prefix,
    get_desktop_application_id,
    read_settings,
    write_settings,
)
from .devices import remap_slot_id, slot_prefix_for_model
from .export import load_preset_file
from .ghub_running import require_ghub_stopped


ConflictMode = Literal["skip", "replace", "rename"]


@dataclass
class ImportResult:
    imported: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    replaced: list[str] = field(default_factory=list)


def _new_id() -> str:
    return str(uuid.uuid4())


def _cards_list(settings: dict[str, Any]) -> list[dict[str, Any]]:
    return settings.setdefault("cards", {}).setdefault("cards", [])


def _profiles_list(settings: dict[str, Any]) -> list[dict[str, Any]]:
    return settings.setdefault("profiles", {}).setdefault("profiles", [])


def _find_profile_by_name(profiles: list[dict[str, Any]], name: str) -> dict[str, Any] | None:
    for profile in profiles:
        if profile.get("name") == name:
            return profile
    return None


def _remove_profile(profiles: list[dict[str, Any]], profile_id: str) -> None:
    profiles[:] = [p for p in profiles if p.get("id") != profile_id]


def _upsert_card(cards: list[dict[str, Any]], card: dict[str, Any]) -> None:
    card_id = card.get("id")
    for idx, existing in enumerate(cards):
        if existing.get("id") == card_id:
            cards[idx] = card
            return
    cards.append(card)


def _resolve_target_slot_prefix(
    settings: dict[str, Any],
    preset: dict[str, Any],
    target_device: str | None,
) -> str | None:
    if target_device:
        prefix = slot_prefix_for_model(target_device)
        if prefix:
            return prefix
    return detect_slot_prefix(settings) or preset.get("slotPrefix")


def _apply_slot_remap(profile: dict[str, Any], from_prefix: str | None, to_prefix: str | None) -> None:
    if not from_prefix or not to_prefix or from_prefix == to_prefix:
        return
    for assignment in profile.get("assignments", []):
        slot_id = assignment.get("slotId")
        if slot_id:
            assignment["slotId"] = remap_slot_id(slot_id, from_prefix, to_prefix)


def _regenerate_ids(
    profile: dict[str, Any],
    cards: list[dict[str, Any]],
) -> None:
    old_profile_id = profile.get("id", _new_id())
    new_profile_id = _new_id()
    id_map: dict[str, str] = {old_profile_id: new_profile_id}
    profile["id"] = new_profile_id

    for card in cards:
        old_card_id = card.get("id")
        if not old_card_id:
            continue
        new_card_id = _new_id()
        id_map[old_card_id] = new_card_id
        card["id"] = new_card_id
        if card.get("profileId") == old_profile_id:
            card["profileId"] = new_profile_id

    lighting = profile.get("lightingCard")
    if lighting in id_map:
        profile["lightingCard"] = id_map[lighting]

    for assignment in profile.get("assignments", []):
        cid = assignment.get("cardId")
        if cid in id_map:
            assignment["cardId"] = id_map[cid]


def merge_preset_into_settings(
    settings: dict[str, Any],
    preset: dict[str, Any],
    *,
    conflict_mode: ConflictMode = "skip",
    rename_to: str | None = None,
    target_device: str | None = None,
) -> str | None:
    profile = copy.deepcopy(preset["profile"])
    cards = copy.deepcopy(preset.get("cards", []))
    profile_name = rename_to or preset.get("name") or profile.get("name", "Imported")

    profiles = _profiles_list(settings)
    existing = _find_profile_by_name(profiles, profile_name)

    if existing and conflict_mode == "skip":
        return None

    if existing and conflict_mode == "replace":
        _remove_profile(profiles, existing["id"])

    _regenerate_ids(profile, cards)

    profile["name"] = profile_name

    desktop_id = get_desktop_application_id(settings)
    if desktop_id:
        profile["applicationId"] = desktop_id
        for card in cards:
            app_id = card.get("applicationId")
            prof_id = card.get("profileId")
            if app_id or prof_id == preset["profile"].get("id"):
                if app_id:
                    card["applicationId"] = desktop_id

    from_prefix = preset.get("slotPrefix")
    to_prefix = _resolve_target_slot_prefix(settings, preset, target_device)
    _apply_slot_remap(profile, from_prefix, to_prefix)

    card_store = _cards_list(settings)
    for card in cards:
        if card.get("profileId") == preset["profile"].get("id"):
            card["profileId"] = profile["id"]
        _upsert_card(card_store, card)

    profiles.append(profile)
    return profile_name


def import_presets(
    paths: list[Path],
    *,
    conflict_mode: ConflictMode = "skip",
    rename_to: str | None = None,
    target_device: str | None = None,
    db_path: Path | None = None,
    dry_run: bool = False,
) -> ImportResult:
    require_ghub_stopped()
    if not dry_run:
        backup_settings_db(db_path)

    settings = read_settings(db_path)
    result = ImportResult()

    for path in paths:
        preset = load_preset_file(path)
        name = rename_to or preset.get("name", path.stem)

        existing = _find_profile_by_name(_profiles_list(settings), name)
        if existing and conflict_mode == "skip":
            result.skipped.append(name)
            continue

        if dry_run:
            if existing and conflict_mode == "replace":
                result.replaced.append(name)
            else:
                result.imported.append(name)
            continue

        merged = merge_preset_into_settings(
            settings,
            preset,
            conflict_mode=conflict_mode,
            rename_to=rename_to if len(paths) == 1 else None,
            target_device=target_device,
        )
        if merged is None:
            result.skipped.append(name)
        elif existing and conflict_mode == "replace":
            result.replaced.append(merged)
        else:
            result.imported.append(merged)

    if not dry_run and (result.imported or result.replaced):
        write_settings(settings, db_path)

    return result


def collect_preset_paths(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    if not target.is_dir():
        raise FileNotFoundError(f"Not found: {target}")
    return sorted(target.glob("*.lghub-preset.json"))
