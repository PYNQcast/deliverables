#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VIDEOS_ROOT="$REPO_ROOT/media/videos/initial"
FINAL_ROOT="$REPO_ROOT/media/videos/final"
OUTPUT_NAME="${OUTPUT_NAME:-PYNQCAST_full_video}"

DEFAULT_SCENES=(
  "TitleScene"
  "GridMapScene"
  "DDAScene"
  "WallRenderScene"
  "FPGAParallelScene"
  "MultiNodeScene"
  "PipelineScene"
  "ServerHardwareSegment"
  "ServerHardwareClosingCard"
)

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "Missing ffmpeg"
  echo "Install the Manim dependencies first. See manim_vid/depend.md"
  exit 1
fi

if [ ! -d "$VIDEOS_ROOT" ]; then
  echo "No rendered videos found under $VIDEOS_ROOT"
  echo "Render scenes first with ./manim_vid/render_mp4.sh"
  exit 1
fi

if [ "$#" -eq 0 ]; then
  SCENES=("${DEFAULT_SCENES[@]}")
else
  SCENES=("$@")
fi

FIRST_SCENE="${SCENES[0]}"
mapfile -t CANDIDATE_DIRS < <(
  for SCENE in "${SCENES[@]}"; do
    find "$VIDEOS_ROOT" -type f -name "${SCENE}.mp4" -printf '%h\n'
  done | sort -u
)

if [ "${#CANDIDATE_DIRS[@]}" -eq 0 ]; then
  echo "Could not find rendered MP4s for the requested scene set."
  echo "Render them first with ./manim_vid/render_mp4.sh ${SCENES[*]}"
  exit 1
fi

BEST_DIR=""
BEST_COUNT=0
BEST_MTIME=0

for DIR in "${CANDIDATE_DIRS[@]}"; do
  COUNT=0
  DIR_MTIME=0
  for SCENE in "${SCENES[@]}"; do
    SCENE_PATH="$DIR/${SCENE}.mp4"
    if [ -f "$SCENE_PATH" ]; then
      COUNT=$((COUNT + 1))
      MTIME="$(stat -c %Y "$SCENE_PATH")"
      if [ "$MTIME" -gt "$DIR_MTIME" ]; then
        DIR_MTIME="$MTIME"
      fi
    fi
  done

  if [ "$COUNT" -gt "$BEST_COUNT" ] || { [ "$COUNT" -eq "$BEST_COUNT" ] && [ "$DIR_MTIME" -gt "$BEST_MTIME" ]; }; then
    BEST_DIR="$DIR"
    BEST_COUNT="$COUNT"
    BEST_MTIME="$DIR_MTIME"
  fi
done

SOURCE_DIR="$BEST_DIR"
mkdir -p "$FINAL_ROOT"

LIST_FILE="$(mktemp)"
cleanup() {
  rm -f "$LIST_FILE"
}
trap cleanup EXIT

for SCENE in "${SCENES[@]}"; do
  SCENE_PATH="$SOURCE_DIR/${SCENE}.mp4"
  if [ ! -f "$SCENE_PATH" ]; then
    echo "Missing $SCENE_PATH"
    echo "All combined scenes must exist in the same render-quality folder."
    echo "Render the missing scene with the same QUALITY setting, or combine a smaller set."
    exit 1
  fi
  printf "file '%s'\n" "$SCENE_PATH" >>"$LIST_FILE"
done

OUTPUT_PATH="$FINAL_ROOT/${OUTPUT_NAME}.mp4"
ffmpeg -y -f concat -safe 0 -i "$LIST_FILE" -c copy "$OUTPUT_PATH" >/dev/null 2>&1

printf 'Final video written to: %s\n' "$OUTPUT_PATH"
