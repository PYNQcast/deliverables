#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV_PY="$REPO_ROOT/.venv/bin/python"
VENV_MANIM="$REPO_ROOT/.venv/bin/manim"
QUALITY="${QUALITY:-qh}"
OPEN_AFTER_RENDER="${OPEN_AFTER_RENDER:-0}"

if [ ! -x "$VENV_MANIM" ]; then
  echo "Missing .venv/bin/manim"
  echo "Install the Manim dependencies first. See manim_vid/depend.md"
  exit 1
fi

cd "$REPO_ROOT"
ARGS=("-${QUALITY}")

if [ "$OPEN_AFTER_RENDER" = "1" ]; then
  if command -v xdg-open >/dev/null 2>&1 || command -v open >/dev/null 2>&1; then
    ARGS+=(-p)
  else
    echo "OPEN_AFTER_RENDER=1 requested, but no xdg-open/open binary is available."
    echo "Rendering the MP4 without auto-opening it."
  fi
fi

if [ "$#" -eq 0 ]; then
  SCENES=("ServerHardwareSegment")
elif [ "$1" = "all" ] || [ "$1" = "--all" ]; then
  SCENES=()
else
  SCENES=("$@")
fi

"$VENV_MANIM" "${ARGS[@]}" manim_vid/initial.py "${SCENES[@]}"

if [ "${#SCENES[@]}" -eq 0 ]; then
  printf '\nMP4s written under: %s\n' "$REPO_ROOT/media/videos/initial"
else
  for SCENE in "${SCENES[@]}"; do
    OUTPUT_PATH="$(find "$REPO_ROOT/media/videos/initial" -type f -name "${SCENE}.mp4" | sort | tail -n 1)"
    if [ -n "$OUTPUT_PATH" ]; then
      printf '\nMP4 written to: %s\n' "$OUTPUT_PATH"
    fi
  done
fi
