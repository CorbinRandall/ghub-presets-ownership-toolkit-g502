#!/usr/bin/env bash
# Maintainer: create public GitHub repo and push (run once).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

REPO_NAME="${GHUB_PRESETS_REPO_NAME:-ghub-presets}"
GITHUB_USER="${GHUB_PRESETS_GITHUB_USER:-CorbinRandall}"

echo ""
echo "=============================================="
echo "  Publish G Hub Preset Toolkit to GitHub"
echo "  Repo: $GITHUB_USER/$REPO_NAME"
echo "=============================================="
echo ""

if ! command -v gh >/dev/null 2>&1; then
  echo "Install GitHub CLI: https://cli.github.com/"
  echo "Then: gh auth login"
  exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "Run: gh auth login"
  exit 1
fi

# Show what will be committed (personal Presets/ are gitignored)
echo "Files to publish (personal presets are excluded):"
git status --short
echo ""

if ! git diff --quiet || ! git diff --cached --quiet || [ -n "$(git status --porcelain)" ]; then
  read -r -p "Create commit for current changes? [Y/n] " ans
  if [ "${ans:-Y}" = "Y" ] || [ "${ans:-Y}" = "y" ]; then
    git add -A
    git status --short
    git commit -m "$(cat <<'EOF'
Release public G Hub Preset Toolkit.

Double-click Executables, Presets folder workflow, replace/sync,
background G Hub quit, and hidden DONT_TOUCH_SYSTEM profile.
EOF
)"
  fi
fi

if git remote get-url origin >/dev/null 2>&1; then
  echo "Pushing to origin..."
  git push origin HEAD
  URL="$(gh repo view --json url -q .url 2>/dev/null || git remote get-url origin)"
  echo ""
  echo "Done: $URL"
  echo ""
  read -r -p "Press Enter to close..."
  exit 0
else
  echo "Creating public repo and pushing..."
  gh repo create "$REPO_NAME" \
    --public \
    --source=. \
    --remote=origin \
    --description "Export, import, and pull Logitech G Hub mouse profiles — full preset control without cloud sync." \
    --push
fi

URL="$(gh repo view --json url -q .url 2>/dev/null || echo "https://github.com/$GITHUB_USER/$REPO_NAME")"
echo ""
echo "Done: $URL"
echo ""
read -r -p "Press Enter to close..."
