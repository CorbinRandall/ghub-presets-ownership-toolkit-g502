#!/usr/bin/env bash
# Shared launcher for Executables (Mac). Do not run directly — use double-click scripts.
set -euo pipefail

ACTION="${1:?action required}"
shift || true

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOLKIT="$(cd "$SCRIPT_DIR/.." && pwd)"
PRESETS="$TOOLKIT/Presets"

export GHUB_PRESET_TOOLKIT_ROOT="$TOOLKIT"
export GHUB_PRESETS_DIR="$PRESETS"
export PYTHONPATH="$TOOLKIT${PYTHONPATH:+:$PYTHONPATH}"

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: python3 not found. Install Python 3.10+ from https://www.python.org/downloads/"
  exit 1
fi

_banner() {
  echo ""
  echo "=============================================="
  echo "  G Hub Preset Toolkit"
  echo "  Presets folder: $PRESETS"
  echo "=============================================="
  echo ""
  echo "Not affiliated with Logitech. Modifies settings.db — see DISCLAIMER.md"
  echo ""
}

_pause() {
  echo ""
  read -r -p "Press Enter to close this window..."
}

_fail() {
  _pause
  exit 1
}

case "$ACTION" in
  setup)
    _banner
    echo "Installing Python dependencies..."
    python3 -m pip install -e "$TOOLKIT"
    mkdir -p "$PRESETS/onboard" "$PRESETS/_archive"
    echo ""
    echo "Setup done. You can now use the other scripts in Executables/mac/"
    _pause
    ;;
  backup)
    _banner
    python3 -m ghub_presets --folder "$PRESETS" backup || _fail
    _pause
    ;;
  quit-ghub)
    _banner
    echo "Stopping G Hub (including menu-bar background)..."
    python3 -m ghub_presets quit-ghub || _fail
    echo "G Hub is fully stopped."
    _pause
    ;;
  export)
    _banner
    echo "IMPORTANT: G Hub must be quit before export reads settings.db."
    echo "If export fails, run '0b Quit G Hub (menu bar).command' first."
    echo ""
    python3 -m ghub_presets --folder "$PRESETS" backup || _fail
    mkdir -p "$PRESETS"
    if ! python3 -m ghub_presets --folder "$PRESETS" export --all; then
      echo ""
      echo "EXPORT FAILED. Quit Logitech G Hub completely, then run again."
      _fail
    fi
    echo ""
    echo "Opening Presets folder..."
    open "$PRESETS" 2>/dev/null || true
    _pause
    ;;
  pull)
    _banner
    echo "IMPORTANT: Quit G Hub and connect mouse via USB before pull."
    echo ""
    mkdir -p "$PRESETS/onboard"
    echo "Reading onboard slots 1–3 from mouse (G502)..."
    PULL_OK=0
    for s in 1 2 3; do
      if python3 -m ghub_presets --folder "$PRESETS" pull --slot "$s" --device g502 --raw 2>/dev/null; then
        PULL_OK=1
      fi
      if python3 -m ghub_presets --folder "$PRESETS" pull --slot "$s" --device g502 2>/dev/null; then
        PULL_OK=1
      fi
    done
    echo ""
    if [[ "$PULL_OK" == "0" ]]; then
      echo "No onboard profiles read. Check USB, quit G Hub, and G502 device."
    else
      echo "Raw backup: $PRESETS/onboard/"
      echo "G Hub-ready files: $PRESETS/onboard_slot*.lghub-preset.json"
    fi
    open "$PRESETS" 2>/dev/null || true
    _pause
    ;;
  import)
    _banner
    echo "IMPORTANT: Quit G Hub completely before import."
    echo ""
    if ! ls "$PRESETS"/*.lghub-preset.json >/dev/null 2>&1; then
      echo "No preset files in $PRESETS"
      echo "Run 'Export from G Hub' first, or copy .lghub-preset.json files into Presets/"
      _fail
    fi
    python3 -m ghub_presets --folder "$PRESETS" backup || _fail
    if ! python3 -m ghub_presets --folder "$PRESETS" import "$PRESETS" --replace; then
      echo ""
      echo "Import failed. Quit Logitech G Hub completely, then run again."
      _fail
    fi
    echo ""
    echo "Done. Open Logitech G Hub to see your profiles."
    _pause
    ;;
  replace)
    _banner
    echo "Stopping G Hub (including menu-bar background)..."
    if ! python3 -m ghub_presets quit-ghub; then
      echo ""
      echo "Could not stop G Hub. Use the menu bar icon -> Quit, then run again."
      _fail
    fi
    echo ""
    if ! ls "$PRESETS"/*.lghub-preset.json >/dev/null 2>&1; then
      echo "No preset files in $PRESETS"
      echo "Run 'Export from G Hub' first to save your current profiles."
      _fail
    fi
    python3 -m ghub_presets --folder "$PRESETS" backup || _fail
    echo "Presets folder (this is the only folder used):"
    echo "  $PRESETS"
    echo ""
    echo "This makes G Hub match ONLY the .lghub-preset.json files in that folder."
    echo ""
    python3 -m ghub_presets --folder "$PRESETS" replace "$PRESETS" --dry-run
    echo ""
    read -r -p "Press Enter to apply (or Ctrl+C to cancel)... " _
    if ! python3 -m ghub_presets --folder "$PRESETS" replace "$PRESETS"; then
      echo ""
      echo "FAILED. Quit G Hub completely and run again."
      _fail
    fi
    echo ""
    echo "Success. Profiles now in G Hub:"
    python3 -m ghub_presets list 2>&1 | tail -n +1
    echo ""
    echo "You can open Logitech G Hub now."
    _pause
    ;;
  *)
    echo "Unknown action: $ACTION"
    exit 1
    ;;
esac
