#!/usr/bin/env bash
# Recompile dark_mode.svg and light_mode.svg without GitHub API calls.
# Auto-installs dependencies from cache/requirements.txt if needed.
#
# Usage: ./scripts/recompile.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$ROOT_DIR/venv"

cd "$ROOT_DIR"

if [ ! -d "$VENV_DIR" ]; then
    echo "-> Creating venv at $VENV_DIR"
    python3 -m venv "$VENV_DIR"
fi

PYTHON="$VENV_DIR/bin/python3"
PIP="$VENV_DIR/bin/pip3"

echo "-> Installing dependencies from cache/requirements.txt"
"$PIP" install -q -r cache/requirements.txt

echo "-> Recompiling SVGs"
"$PYTHON" today.py
echo "-> Done: dark_mode.svg and light_mode.svg updated"
