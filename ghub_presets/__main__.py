"""G Hub Personal Preset Control — CLI entry point."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .db import ghub_settings_db, list_profiles, read_settings
from .devices import DEVICES
from .export import export_all_profiles, export_profile_by_name, load_preset_file
from .ghub_running import is_ghub_running, require_ghub_stopped
from .import_ import collect_preset_paths, import_presets
from .manifest import list_manifest_presets, upsert_manifest_entry
from .paths import default_presets_dir


def _print_import_result(result) -> None:
    if result.imported:
        print("Imported:", ", ".join(result.imported))
    if result.replaced:
        print("Replaced:", ", ".join(result.replaced))
    if result.skipped:
        print("Skipped:", ", ".join(result.skipped))


def cmd_list(args: argparse.Namespace) -> int:
    if args.source == "folder":
        folder = Path(args.folder)
        if not folder.exists():
            print(f"Folder not found: {folder}")
            return 1
        paths = collect_preset_paths(folder)
        if not paths:
            print(f"No presets in {folder}")
            return 0
        for path in paths:
            try:
                preset = load_preset_file(path)
                print(f"{path.name}\t{preset.get('name')}\t{preset.get('sourceDevice', '?')}")
            except Exception as exc:
                print(f"{path.name}\t(error: {exc})")
        manifest = list_manifest_presets(folder)
        if manifest:
            print(f"\nManifest: {len(manifest)} entries")
        return 0

    try:
        settings = read_settings(args.db_path)
    except FileNotFoundError as exc:
        print(exc)
        return 1
    for profile in list_profiles(settings):
        print(profile.get("name", "?"), profile.get("id", ""))
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    require_ghub_stopped()
    folder = Path(args.folder)
    folder.mkdir(parents=True, exist_ok=True)

    if args.all:
        paths = export_all_profiles(folder, db_path=args.db_path)
        for path in paths:
            preset = load_preset_file(path)
            upsert_manifest_entry(folder, path.name, preset.get("name", "?"), "ghub-export")
            print(f"Exported: {path}")
        print(f"Done. {len(paths)} profile(s) -> {folder}")
        return 0

    if not args.name:
        print("Provide --name or use --all")
        return 1

    path = export_profile_by_name(args.name, folder, db_path=args.db_path)
    preset = load_preset_file(path)
    upsert_manifest_entry(folder, path.name, preset.get("name", "?"), "ghub-export")
    print(f"Exported: {path}")
    return 0


def cmd_import(args: argparse.Namespace) -> int:
    target = Path(args.target)
    paths = collect_preset_paths(target)
    if not paths:
        print(f"No preset files found at {target}")
        return 1

    conflict = "replace" if args.replace else ("rename" if args.rename else "skip")
    result = import_presets(
        paths,
        conflict_mode=conflict,
        rename_to=args.rename,
        target_device=args.target_device,
        target_platform="mac" if args.for_mac else None,
        db_path=args.db_path,
        dry_run=args.dry_run,
    )
    _print_import_result(result)
    if args.dry_run:
        print("(dry run — settings.db not modified)")
    else:
        folder = target if target.is_dir() else target.parent
        for path in paths:
            try:
                preset = load_preset_file(path)
                upsert_manifest_entry(folder, path.name, preset.get("name", "?"), "ghub-import")
            except Exception:
                pass
        print("Reopen Logitech G Hub to see imported profiles.")
    return 0


def cmd_pull(args: argparse.Namespace) -> int:
    from .pull import pull_to_file

    output = Path(args.output) if args.output else Path(args.folder) / f"onboard_slot{args.slot}.lghub-preset.json"
    try:
        path = pull_to_file(
            args.device,
            args.slot,
            output,
            profile_name=args.name,
            target_platform="mac" if args.for_mac else None,
        )
    except (RuntimeError, OSError, AssertionError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    preset = load_preset_file(path)
    upsert_manifest_entry(path.parent, path.name, preset.get("name", "?"), "mouse-pull")
    print(f"Pulled onboard slot {args.slot} -> {path}")
    return 0


def cmd_compare(args: argparse.Namespace) -> int:
    from .compare import compare_onboard_to_ghub, print_compare_report

    report = compare_onboard_to_ghub(args.onboard, args.ghub)
    print_compare_report(report)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"\nWrote {args.output}")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    db = ghub_settings_db()
    print(f"G Hub running: {is_ghub_running()}")
    print(f"settings.db: {db} ({'exists' if db.exists() else 'missing'})")
    print(f"Preset folder: {Path(args.folder)}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ghub-presets",
        description="Export, import, and pull Logitech G Hub mouse profiles.",
    )
    parser.add_argument(
        "--folder",
        default=str(default_presets_dir()),
        help="Preset library folder (default: ~/LogitechPresets)",
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        default=None,
        help="Override path to settings.db",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="List profiles in G Hub or preset folder")
    p_list.add_argument(
        "--source",
        choices=("ghub", "folder"),
        default="ghub",
        help="List from G Hub database or preset folder",
    )

    p_export = sub.add_parser("export", help="Export profile(s) from G Hub to preset files")
    p_export.add_argument("--name", help="Profile name to export")
    p_export.add_argument("--all", action="store_true", help="Export all profiles")

    p_import = sub.add_parser("import", help="Import preset file(s) into G Hub")
    p_import.add_argument("target", help="Preset file or folder")
    p_import.add_argument("--replace", action="store_true", help="Replace existing profile with same name")
    p_import.add_argument("--rename", help="Import under a new profile name (single file)")
    p_import.add_argument(
        "--target-device",
        choices=("g502_spectrum", "g502wireless"),
        help="Remap slot IDs for target mouse model",
    )
    p_import.add_argument("--dry-run", action="store_true", help="Preview without writing settings.db")
    p_import.add_argument(
        "--for-mac",
        action="store_true",
        help="Re-convert onboard presets for macOS (Ctrl→Cmd editing shortcuts)",
    )

    p_pull = sub.add_parser("pull", help="Pull onboard profile from mouse via HID++")
    p_pull.add_argument("--slot", type=int, default=1, help="Onboard profile slot (1-5)")
    p_pull.add_argument(
        "--device",
        choices=tuple(DEVICES.keys()),
        default="g502",
        help="Device type (g502, g502wireless, g502wireless-dongle)",
    )
    p_pull.add_argument("--output", help="Output preset file path")
    p_pull.add_argument("--name", help="Override imported profile name")
    p_pull.add_argument(
        "--for-mac",
        action="store_true",
        help="Map Windows Ctrl editing shortcuts to Mac Cmd when converting",
    )

    sub.add_parser("status", help="Show G Hub and preset paths")

    p_compare = sub.add_parser(
        "compare",
        help="Compare onboard pull JSON to G Hub export (Rosetta stone)",
    )
    p_compare.add_argument(
        "--onboard",
        type=Path,
        required=True,
        help="Onboard pull file (onboard_raw_slotN.json or preset with ommRaw)",
    )
    p_compare.add_argument(
        "--ghub",
        type=Path,
        required=True,
        help="G Hub export .lghub-preset.json (e.g. from upload-from-device)",
    )
    p_compare.add_argument(
        "--output",
        type=Path,
        help="Write rosetta report JSON to this path",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    handlers = {
        "list": cmd_list,
        "export": cmd_export,
        "import": cmd_import,
        "pull": cmd_pull,
        "compare": cmd_compare,
        "status": cmd_status,
    }
    return handlers[args.command](args)


def main_entry() -> None:
    raise SystemExit(main())


if __name__ == "__main__":
    main_entry()
