#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

sudo apt-get clean
sudo rm -rf /var/lib/apt/lists/*
sudo apt-get update
sudo apt-get install -y ffmpeg pkg-config libcairo2-dev libpango1.0-dev

python3 -m venv "$REPO_ROOT/.venv"
"$REPO_ROOT/.venv/bin/pip" install --upgrade pip
"$REPO_ROOT/.venv/bin/pip" install -r "$REPO_ROOT/manim_vid/requirements.txt"

echo
echo "Manim setup complete."
echo "Render with:"
echo "  $REPO_ROOT/manim_vid/render_mp4.sh ServerHardwareSegment"
