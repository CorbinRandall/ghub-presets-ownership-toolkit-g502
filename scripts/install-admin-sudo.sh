#!/usr/bin/env bash
# One-time setup: install toolkit for root + passwordless sudo for update block/unblock only.
# Must be run as root. The Mac .command stages the repo to /var/tmp first (root cannot read Documents).
set -euo pipefail

if [[ "$(id -u)" -ne 0 ]]; then
  echo "Run as root: sudo bash scripts/install-admin-sudo.sh" >&2
  exit 1
fi

STAGING="${GHUB_PRESET_TOOLKIT_STAGING:-}"
USER_NAME="${SUDO_USER:-${USER}}"
ADMIN_BIN="/usr/local/bin/ghub-presets-admin"
INSTALL_LIB="/usr/local/lib/ghub-presets-toolkit"
SUDOERS_FILE="/etc/sudoers.d/ghub-presets-toolkit"

if [[ -z "$STAGING" || ! -d "$STAGING/ghub_presets" ]]; then
  echo "Set GHUB_PRESET_TOOLKIT_STAGING to a /var/tmp copy of the repo." >&2
  exit 1
fi

_pick_python() {
  local py
  for py in python3.12 python3.11 python3.10 python3; do
    if command -v "$py" >/dev/null 2>&1; then
      command -v "$py"
      return 0
    fi
  done
  return 1
}

PYTHON="$(_pick_python || true)"
if [[ -z "$PYTHON" ]]; then
  echo "python3 not found." >&2
  exit 1
fi

echo "Installing ghub-presets into $INSTALL_LIB (python: $PYTHON)..."
rm -rf "$INSTALL_LIB"
mkdir -p "$INSTALL_LIB"
ditto "$STAGING/ghub_presets" "$INSTALL_LIB/ghub_presets"

mkdir -p "/Library/Application Support/ghub-presets-toolkit"
chmod 755 "/Library/Application Support/ghub-presets-toolkit"

mkdir -p /usr/local/bin
cat >"$ADMIN_BIN" <<EOF
#!/usr/bin/env bash
case "\${1:-}" in
  block-updates | unblock-updates) ;;
  *)
    echo "Only block-updates and unblock-updates are allowed." >&2
    exit 2
    ;;
esac
export PYTHONPATH="$INSTALL_LIB\${PYTHONPATH:+:\$PYTHONPATH}"
exec "$PYTHON" -m ghub_presets "\$@"
EOF
chmod 755 "$ADMIN_BIN"

cat >"$SUDOERS_FILE" <<EOF
# G Hub Preset Toolkit — passwordless sudo for update block/unblock only.
# Installed $(date -u +%Y-%m-%d) for user ${USER_NAME}.
Defaults:${USER_NAME} !requiretty
${USER_NAME} ALL=(ALL) NOPASSWD: ${ADMIN_BIN} block-updates
${USER_NAME} ALL=(ALL) NOPASSWD: ${ADMIN_BIN} unblock-updates
EOF
chmod 440 "$SUDOERS_FILE"

if ! visudo -c -f "$SUDOERS_FILE" >/dev/null; then
  echo "sudoers validation failed; removing $SUDOERS_FILE" >&2
  rm -f "$SUDOERS_FILE"
  exit 1
fi

echo ""
echo "Done. ${USER_NAME} can run without a password:"
echo "  sudo ghub-presets-admin block-updates"
echo "  sudo ghub-presets-admin unblock-updates"
echo ""
echo "Or double-click:"
echo "  Executables/mac/0c Block G Hub Updates.command"
echo ""
echo "To remove: sudo rm -rf $SUDOERS_FILE $ADMIN_BIN $INSTALL_LIB"
