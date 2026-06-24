#!/usr/bin/env bash
# Shared launcher for Executables (Mac). Do not run directly — use double-click scripts.
set -euo pipefail

ACTION="${1:?action required}"
shift || true

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOLKIT="$(cd "$SCRIPT_DIR/.." && pwd)"
PRESETS="$TOOLKIT/Put Presets Here"

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

# Downloaded .command files get com.apple.quarantine; macOS blocks each one until
# approved in Settings. Running Setup once clears quarantine on all Mac shortcuts.
_clear_mac_quarantine() {
  local mac_exe="$TOOLKIT/Executables/mac"
  [[ -d "$mac_exe" ]] || return 0
  local cleared=0
  local f
  for f in "$mac_exe"/*.command; do
    [[ -f "$f" ]] || continue
    if xattr -l "$f" 2>/dev/null | grep -q com.apple.quarantine; then
      xattr -d com.apple.quarantine "$f" 2>/dev/null || true
      cleared=$((cleared + 1))
    fi
    chmod +x "$f" 2>/dev/null || true
  done
  if [[ "$cleared" -gt 0 ]]; then
    echo "Cleared macOS download quarantine on $cleared Mac shortcut(s)."
    echo "You can double-click the other .command files without approving each in Settings."
  fi
}

_run_update_admin() {
  local action="$1"
  local admin="/usr/local/bin/ghub-presets-admin"
  if [[ "$(id -u)" -eq 0 ]]; then
    bash "$SCRIPT_DIR/ghub-admin.sh" "$action"
    return
  fi
  if [[ -x "$admin" ]]; then
    if sudo -n "$admin" "$action" 2>/dev/null; then
      return
    fi
    sudo "$admin" "$action"
    return
  fi
  echo "Tip: run Executables/mac/0 Setup admin sudo (once).command to skip password prompts."
  python3 -m ghub_presets --folder "$PRESETS" "$action"
}

case "$ACTION" in
  setup)
    _banner
    _clear_mac_quarantine
    echo ""
    echo "Installing Python dependencies (hidapi for Pull from Mouse)..."
    if ! python3 -m pip install --user hidapi; then
      echo ""
      echo "WARNING: hidapi install failed. Export/Import/Replace still work."
      echo "Pull from Mouse needs: python3 -m pip install --user hidapi"
    fi
    mkdir -p "$PRESETS/onboard" "$PRESETS/_archive"
    echo ""
    echo "Setup done. Toolkit runs from this folder — no pip install of the repo required."
    echo "You can now use the other scripts in Executables/mac/"
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
  block-updates)
    _banner
    echo "Blocking G Hub automatic updates (sudo required)..."
    echo "Keeps com.logi.ghub.updater loaded; blocks update hosts in /etc/hosts."
    echo ""
    _run_update_admin block-updates || _fail
    _pause
    ;;
  unblock-updates)
    _banner
    echo "Removing G Hub update block (sudo required)..."
    echo ""
    _run_update_admin unblock-updates || _fail
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
    echo "IMPORTANT: Quit G Hub first. Use USB cable or Lightspeed receiver."
    echo ""
    mkdir -p "$PRESETS/onboard"
    python3 -c "from ghub_presets.pull import pull_device_status_lines; print('\n'.join(pull_device_status_lines()))" || true
    echo ""
    echo "Reading onboard slots 1–3 (auto-detect, with fallback)..."
    PULL_OK=0
    for s in 1 2 3; do
      if python3 -m ghub_presets --folder "$PRESETS" pull --slot "$s" --device auto --raw 2>/dev/null; then
        PULL_OK=1
      fi
      if python3 -m ghub_presets --folder "$PRESETS" pull --slot "$s" --device auto 2>/dev/null; then
        PULL_OK=1
      fi
    done
    echo ""
    if [[ "$PULL_OK" == "0" ]]; then
      echo "No onboard profiles read. Quit G Hub, check USB/receiver, and enabled onboard slots."
      echo "Force a path: python3 -m ghub_presets pull --slot 1 --device g502wireless-dongle"
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
      echo "Run 'Export from G Hub' first, or copy .lghub-preset.json files into Put Presets Here/"
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
