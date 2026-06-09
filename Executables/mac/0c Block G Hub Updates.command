#!/bin/bash
set -euo pipefail
ADMIN="/usr/local/bin/ghub-presets-admin"
if [[ -x "$ADMIN" ]]; then
  sudo "$ADMIN" block-updates
else
  echo "First run: double-click '0 Setup admin sudo (once).command'"
  exit 1
fi
echo ""
read -r -p "Press Enter to close..."
