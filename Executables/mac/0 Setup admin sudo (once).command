#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")/../../scripts" && pwd)"
TOOLKIT="$(cd "$SCRIPT_DIR/.." && pwd)"
INSTALL_SRC="$SCRIPT_DIR/install-admin-sudo.sh"
INSTALL_TMP="/tmp/ghub-presets-install-admin-sudo.sh"
STAGING="/var/tmp/ghub-presets-toolkit-install"

echo ""
echo "Staging toolkit (root cannot read your Documents folder)..."
rm -rf "$STAGING"
ditto "$TOOLKIT" "$STAGING"

cp "$INSTALL_SRC" "$INSTALL_TMP"
chmod 755 "$INSTALL_TMP"
echo ""
echo "One-time setup: enter your Mac password once."
echo "After this, Block/Unblock G Hub Updates won't ask again."
echo ""
osascript -e "do shell script \"export GHUB_PRESET_TOOLKIT_STAGING='$STAGING'; bash '$INSTALL_TMP'\" with administrator privileges"
rm -f "$INSTALL_TMP"
rm -rf "$STAGING"
echo ""
read -r -p "Press Enter to close..."
