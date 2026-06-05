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
  echo "IMPORTANT: Quit Logitech G Hub completely first!"
  echo "(Menu bar icon -> Quit, or Force Quit in Activity Monitor)"
  echo ""
}

_pause() {
  echo ""
  read -r -p "Press Enter to close this window..."
}

case "$ACTION" in
  setup)
    _banner
    echo "Installing Python dependencies..."
    python3 -m pip install -e "$TOOLKIT"
    mkdir -p "$PRESETS/onboard"
    echo ""
    echo "Setup done. You can now use the other scripts in Executables/mac/"
    _pause
    ;;
  export)
    _banner
    mkdir -p "$PRESETS"
    python3 -m ghub_presets --folder "$PRESETS" export --all
    echo ""
    echo "Saved to: $PRESETS"
    open "$PRESETS" 2>/dev/null || true
    _pause
    ;;
  pull)
    _banner
    mkdir -p "$PRESETS/onboard"
    echo "Reading onboard slots 1–3 from mouse (G502)..."
    for s in 1 2 3; do
      python3 -m ghub_presets --folder "$PRESETS" pull --slot "$s" --device g502 --raw 2>/dev/null || \
        echo "  (slot $s raw skipped — empty or disabled)"
      python3 -m ghub_presets --folder "$PRESETS" pull --slot "$s" --device g502 2>/dev/null || \
        echo "  (slot $s skipped — empty or disabled)"
    done
    echo ""
    echo "Raw backup: $PRESETS/onboard/"
    echo "G Hub-ready files: $PRESETS/onboard_slot*.lghub-preset.json"
    open "$PRESETS" 2>/dev/null || true
    _pause
    ;;
  import)
    _banner
    if ! ls "$PRESETS"/*.lghub-preset.json >/dev/null 2>&1; then
      echo "No preset files in $PRESETS"
      echo "Run 'Export from G Hub' first, or copy .lghub-preset.json files into Presets/"
      _pause
      exit 1
    fi
    python3 -m ghub_presets --folder "$PRESETS" import "$PRESETS" --replace
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
      _pause
      exit 1
    fi
    echo ""
    if ! ls "$PRESETS"/*.lghub-preset.json >/dev/null 2>&1; then
      echo "No preset files in $PRESETS"
      _pause
      exit 1
    fi
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
      echo "FAILED. Common fixes:"
      echo "  1. Quit G Hub (Activity Monitor → search lghub → Quit)"
      echo "  2. Run this script again"
      _pause
      exit 1
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
