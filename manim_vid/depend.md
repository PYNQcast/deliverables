# Manim Segment Setup

This folder contains the Manim segment for the PYNQCAST architecture video.

For a short render-only shell guide, see:

- `manim_vid/render_howto.md`

## Scene file

- `manim_vid/initial.py`

Main scenes:

- `TitleScene`
- `GridMapScene`
- `DDAScene`
- `WallRenderScene`
- `FPGAParallelScene`
- `MultiNodeScene`
- `PipelineScene`
- `ServerHardwareSegment`
- `ServerHardwareClosingCard`

## Linux dependencies

Manim Community needs:

- `ffmpeg`
- `pkg-config`
- `libcairo2-dev`
- `libpango1.0-dev`
- a Python environment with `manim`

Without the Linux packages above, `pip install manim` fails during the Cairo/Pango build path. On this machine the concrete failure was:

- `Did not find pkg-config`
- `Dependency lookup for cairo with method 'pkgconfig' failed`

## Local install flow

```bash
sudo apt-get clean
sudo rm -rf /var/lib/apt/lists/*
sudo apt-get update
sudo apt-get install -y ffmpeg pkg-config libcairo2-dev libpango1.0-dev

python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r manim_vid/requirements.txt
```

Or use the helper script:

```bash
./manim_vid/install_manim.sh
```

## VS Code / Manim Sideview

This repo now ships a tracked workspace setting in `.vscode/settings.json` that points:

- Python to `${workspaceFolder}/.venv/bin/python`
- Manim Sideview to `${workspaceFolder}/manim_vid/manim`

So if the repo is opened in VS Code after the local install above, the extension should find Manim without extra manual path setup.

The wrapper at `manim_vid/manim` also injects a local `xdg-open` fallback, so preview rendering still works on minimal systems that do not have the `xdg-utils` package installed.

## If apt throws 400 Bad Request

That usually means the local apt package lists are stale while the mirror has moved on.

Run:

```bash
sudo apt-get clean
sudo rm -rf /var/lib/apt/lists/*
sudo apt-get update
sudo apt-get install -y ffmpeg pkg-config libcairo2-dev libpango1.0-dev
```

Then retry:

```bash
.venv/bin/pip install -r manim_vid/requirements.txt
```

## Render preview

```bash
./manim_vid/render_mp4.sh ServerHardwareSegment
```

This renders the MP4 only. It does not try to auto-open the file, which avoids
`FileNotFoundError: xdg-open` on minimal Linux setups.

You can also render multiple scenes in one call:

```bash
./manim_vid/render_mp4.sh TitleScene GridMapScene DDAScene
```

Or render every scene in `manim_vid/initial.py`:

```bash
./manim_vid/render_mp4.sh all
```

## Render final MP4

```bash
QUALITY=qh ./manim_vid/render_mp4.sh ServerHardwareSegment
```

Higher quality:

```bash
QUALITY=qk ./manim_vid/render_mp4.sh ServerHardwareSegment
```

If you do want the rendered video to open automatically and your machine has
`xdg-open` or `open`, use:

```bash
OPEN_AFTER_RENDER=1 ./manim_vid/render_mp4.sh ServerHardwareSegment
```

## Output location

Manim writes videos under:

```text
media/videos/initial/<quality>/
```

Typical final output:

```text
media/videos/initial/1080p60/ServerHardwareSegment.mp4
```
