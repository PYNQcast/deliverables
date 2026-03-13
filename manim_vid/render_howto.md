# Manim Render How-To

This file is only about rendering scenes. Dependency and install setup lives in:

- `manim_vid/depend.md`

## Run from the repo root

```bash
cd /home/akendall/Documents/ServerSide_PYNQ_Raycaster
```

## Render one scene

```bash
./manim_vid/render_mp4.sh GridMapScene
```

## Render multiple scenes

```bash
./manim_vid/render_mp4.sh TitleScene GridMapScene DDAScene
```

## Render all scenes in `initial.py`

```bash
./manim_vid/render_mp4.sh all
```

## Render at higher quality

```bash
QUALITY=qh ./manim_vid/render_mp4.sh all
```

Or:

```bash
QUALITY=qk ./manim_vid/render_mp4.sh all
```

## Auto-open after render

By default the helper only renders and prints the MP4 path.

If you want it to try opening the result too:

```bash
OPEN_AFTER_RENDER=1 ./manim_vid/render_mp4.sh GridMapScene
```

## Output location

Rendered files are written under:

```text
media/videos/initial/
```

Common examples:

```text
media/videos/initial/480p15/GridMapScene.mp4
media/videos/initial/1080p60/ServerHardwareSegment.mp4
```

## Current scene names

- `TitleScene`
- `GridMapScene`
- `DDAScene`
- `WallRenderScene`
- `FPGAParallelScene`
- `MultiNodeScene`
- `PipelineScene`
- `ServerHardwareSegment`
- `ServerHardwareClosingCard`

## Quick examples

Algorithm-only sequence:

```bash
./manim_vid/render_mp4.sh TitleScene GridMapScene DDAScene WallRenderScene FPGAParallelScene MultiNodeScene PipelineScene
```

Runtime/server-only sequence:

```bash
./manim_vid/render_mp4.sh ServerHardwareSegment ServerHardwareClosingCard
```

## Clean render artifacts

Standard clean workflow:

- keep source scenes in git
- treat rendered `media/` output as build artifacts
- remove partial Manim chunks after a successful render if you do not need them

Keep final MP4s, delete partial chunk files:

```bash
./manim_vid/clean_render_artifacts.sh
```

Delete all rendered scene outputs and start fresh:

```bash
./manim_vid/clean_render_artifacts.sh all
```

## Combine rendered scenes into one final video

Use the helper:

```bash
./manim_vid/combine_mp4.sh
```

That defaults to this order:

- `TitleScene`
- `GridMapScene`
- `DDAScene`
- `WallRenderScene`
- `FPGAParallelScene`
- `MultiNodeScene`
- `PipelineScene`
- `ServerHardwareSegment`
- `ServerHardwareClosingCard`

It writes the final stitched MP4 to:

```text
media/videos/final/PYNQCAST_full_video.mp4
```

To combine only a subset:

```bash
./manim_vid/combine_mp4.sh TitleScene GridMapScene DDAScene
```

To change the output name:

```bash
OUTPUT_NAME=algo_cut ./manim_vid/combine_mp4.sh TitleScene GridMapScene DDAScene
```

Important:

- every scene you combine must already be rendered
- they must exist in the same quality folder, for example all in `480p15` or all in `1080p60`
