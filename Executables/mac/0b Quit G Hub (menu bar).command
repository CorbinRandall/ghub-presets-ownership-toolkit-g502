#!/bin/bash
cd "$(dirname "$0")/../../scripts"
export GHUB_PRESET_TOOLKIT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
export PYTHONPATH="$GHUB_PRESET_TOOLKIT_ROOT${PYTHONPATH:+:$PYTHONPATH}"
echo ""
python3 -m ghub_presets quit-ghub
echo ""
read -r -p "Press Enter to close..."
