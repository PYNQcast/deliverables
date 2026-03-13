#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VIDEOS_ROOT="$REPO_ROOT/media/videos"
MODE="${1:-partials}"

if [ ! -d "$VIDEOS_ROOT" ]; then
  echo "No media/videos directory to clean."
  exit 0
fi

case "$MODE" in
  partials)
    find "$VIDEOS_ROOT" -type d -name partial_movie_files -prune -exec rm -rf {} +
    find "$VIDEOS_ROOT" -type f -name 'partial_movie_file_list.txt' -delete
    echo "Removed Manim partial render artifacts under $VIDEOS_ROOT"
    ;;
  all)
    rm -rf "$VIDEOS_ROOT/initial"
    echo "Removed all rendered scene outputs under $VIDEOS_ROOT/initial"
    ;;
  *)
    echo "Usage: ./manim_vid/clean_render_artifacts.sh [partials|all]"
    echo "  partials: remove partial_movie_files and concat txt artifacts, keep final MP4s"
    echo "  all: remove all rendered scene outputs under media/videos/initial"
    exit 1
    ;;
esac
