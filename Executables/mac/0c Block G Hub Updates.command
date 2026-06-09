#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")/../../scripts" && pwd)"
TOOLKIT_SH="$SCRIPT_DIR/toolkit.sh"
osascript -e "do shell script \"bash '$TOOLKIT_SH' block-updates\" with administrator privileges"
