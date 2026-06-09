#!/usr/bin/env bash
# Run block-updates / unblock-updates as root (via sudo). See install-admin-sudo.sh.
set -euo pipefail

ACTION="${1:?usage: ghub-admin.sh block-updates|unblock-updates}"
case "$ACTION" in
  block-updates | unblock-updates) ;;
  *)
    echo "Only block-updates and unblock-updates are allowed." >&2
    exit 2
    ;;
esac

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOLKIT="$(cd "$SCRIPT_DIR/.." && pwd)"
PRESETS="$TOOLKIT/Presets"

export GHUB_PRESET_TOOLKIT_ROOT="$TOOLKIT"
export GHUB_PRESETS_DIR="$PRESETS"

if command -v ghub-presets >/dev/null 2>&1; then
  exec ghub-presets --folder "$PRESETS" "$ACTION"
fi

export PYTHONPATH="$TOOLKIT${PYTHONPATH:+:$PYTHONPATH}"
exec python3 -m ghub_presets --folder "$PRESETS" "$ACTION"
