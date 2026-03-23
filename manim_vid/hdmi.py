"""
HDMI Output Protocol Scene — PYNQ CAST
Run with: manim -pqh hdmi_scene.py HDMIScene

Target runtime: ~20 seconds at 1x  (~13 s at 1.5x)

═══════════════════════════════════════════════════════
VOICE SCRIPT
═══════════════════════════════════════════════════════
BEAT 1 — title  (2 s)
"The default PYNQ video pipeline routes every pixel
 through DDR3 — a full framebuffer round trip."

BEAT 2 — standard pipeline  (4 s)
"The PS writes a complete 480p frame into SDRAM.
 The VDMA reads it back over AXI, and the VTC clocks
 it through to the display. At 60 frames per second
 that's 900 kilobytes per frame — 55 megabytes per
 second of AXI bandwidth just to keep the screen fed.
 Frame rate couples to PS scheduling, and tearing
 is possible whenever the display scans out while the
 PS is still writing the next frame."

BEAT 3 — removal + new pipeline  (5 s)
"We removed the VDMA entirely. The raycaster
 AXI-Stream connects straight into the video output IP,
 with the VTC and RGB-to-DVI retained. Pixels flow
 raycaster to display with no memory transaction."

BEAT 4 — gains  (5 s)
"The VTC is a hardware counter on a fixed pixel clock —
 frame rate is now physically decoupled from the PS.
 No shared framebuffer means no tearing surface.
 Latency drops from 16.7 milliseconds to under 1
 microsecond, and the full 55 megabytes per second
 is recovered for the network stack."

BEAT 5 — stat cards  (4 s)
"Zero BRAM tiles added. 55 megabytes per second freed.
 And the ARM core is reduced to writing a 34-byte
 game-state packet to BRAM each tick."
═══════════════════════════════════════════════════════
"""

from manim import *
import numpy as np

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
PYNQ_RED        = "#F05252"
BACKGROUND      = "#07111C"
PANEL_FILL      = "#10243A"
TEXT_PRIMARY    = "#F4F7FB"
TEXT_MUTED      = "#B8CCE0"
TEXT_DIM        = "#7A9AB8"
ACCENT_HARDWARE = "#F7A541"
ACCENT_SERVER   = "#58C4DD"
ACCENT_GREEN    = "#7BD88F"
ACCENT_RED      = "#F05252"
GRID_COLOR      = "#3A5070"

DDR_COLOR       = "#D97706"
DDR_FILL        = "#1A1200"
VDMA_COLOR      = "#F05252"
VDMA_FILL       = "#1A0505"
KEEP_COLOR      = "#58C4DD"
KEEP_FILL       = "#051020"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def pipe_block(label, sub, stroke, fill, w=2.2, h=1.0):
    box = RoundedRectangle(corner_radius=0.15, width=w, height=h,
                           stroke_color=stroke, stroke_width=2.5,
                           fill_color=fill, fill_opacity=0.97)
    t = Text(label, font_size=18, color=stroke, weight=BOLD)
    s = Text(sub,   font_size=12, color=TEXT_MUTED)
    VGroup(t, s).arrange(DOWN, buff=0.07).move_to(box)
    return VGroup(box, t, s)

def flow_arrow(start, end, color=TEXT_MUTED):
    return Arrow(start, end, buff=0.07, stroke_width=3, color=color,
                 max_tip_length_to_length_ratio=0.18)

def stat_card(val, desc, col, w=3.2, h=1.3):
    box = RoundedRectangle(corner_radius=0.15, width=w, height=h,
                           stroke_color=col, stroke_width=2,
                           fill_color=PANEL_FILL, fill_opacity=0.95)
    v = Text(val,  font_size=24, color=col,        weight=BOLD)
    d = Text(desc, font_size=14, color=TEXT_MUTED)
    VGroup(v, d).arrange(DOWN, buff=0.1).move_to(box)
    return VGroup(box, v, d)

def cross(mob, color=ACCENT_RED, width=4):
    tl = mob.get_corner(UL)
    br = mob.get_corner(DR)
    tr = mob.get_corner(UR)
    bl = mob.get_corner(DL)
    return VGroup(
        Line(tl, br, stroke_color=color, stroke_width=width),
        Line(tr, bl, stroke_color=color, stroke_width=width),
    )

# ---------------------------------------------------------------------------
# Scene
# ---------------------------------------------------------------------------

class HDMIScene(Scene):

    def construct(self):
        self.camera.background_color = BACKGROUND

        # ── BEAT 1: Title (2 s) ──────────────────────────────────────────
        title = Text("HDMI Output Protocol", font_size=52,
                     weight=BOLD, color=PYNQ_RED)
        sub   = Text("Removing the DDR framebuffer",
                     font_size=24, color=TEXT_MUTED)
        sub.next_to(title, DOWN, buff=0.3)
        VGroup(title, sub).move_to(ORIGIN)

        self.play(Write(title), run_time=0.6)
        self.play(FadeIn(sub, shift=UP*0.15), run_time=0.4)
        self.wait(0.7)
        self.play(FadeOut(VGroup(title, sub)), run_time=0.4)

        # ── BEAT 2: Standard PYNQ pipeline (4 s) ─────────────────────────
        ps_block   = pipe_block("PS — ARM",    "renders frame",   ACCENT_HARDWARE, "#0D1A08")
        ddr_block  = pipe_block("DDR3",        "900 kB framebuf", DDR_COLOR,       DDR_FILL, w=2.2)
        vdma_block = pipe_block("VDMA",        "DMA read-back",   VDMA_COLOR,      VDMA_FILL)
        vtc_block  = pipe_block("VTC",         "pixel clock",     KEEP_COLOR,      KEEP_FILL)
        hdmi_block = pipe_block("HDMI out",    "RGB2DVI",         KEEP_COLOR,      KEEP_FILL)

        std_pipeline = VGroup(ps_block, ddr_block, vdma_block,
                              vtc_block, hdmi_block)
        std_pipeline.arrange(RIGHT, buff=0.32).move_to(UP*0.3)
        if std_pipeline.get_width() > 13.0:
            std_pipeline.scale_to_fit_width(13.0)

        std_arrows = VGroup(*[
            flow_arrow(std_pipeline[i].get_right(),
                       std_pipeline[i+1].get_left(),
                       color=TEXT_DIM)
            for i in range(4)
        ])

        # cost label under DDR + VDMA
        cost_pill = RoundedRectangle(
            corner_radius=0.09, width=5.2, height=0.38,
            stroke_color=DDR_COLOR, stroke_width=1.5,
            fill_color=PANEL_FILL, fill_opacity=0.92)
        cost_txt = Text("900 kB/frame  ·  55 MB/s AXI  ·  tearing risk",
                        font_size=14, color=DDR_COLOR)
        cost_txt.move_to(cost_pill)
        cost_grp = VGroup(cost_pill, cost_txt)
        cost_grp.next_to(VGroup(ddr_block, vdma_block), DOWN, buff=0.22)

        latency_lbl = Text("~16.7 ms latency", font_size=16,
                           color=ACCENT_RED, weight=BOLD)
        latency_lbl.next_to(std_pipeline, DOWN, buff=0.62)

        self.play(
            LaggedStart(*[FadeIn(b, shift=RIGHT*0.1) for b in std_pipeline],
                        lag_ratio=0.12),
            run_time=0.8,
        )
        self.play(FadeIn(std_arrows, lag_ratio=0.1), run_time=0.4)
        self.play(FadeIn(cost_grp, shift=UP*0.1), run_time=0.35)
        self.play(FadeIn(latency_lbl, shift=UP*0.1), run_time=0.3)
        self.wait(1.0)

        # ── BEAT 3: Cross out VDMA + DDR, redraw pipeline (5 s) ──────────
        ddr_x  = cross(ddr_block)
        vdma_x = cross(vdma_block)

        self.play(
            FadeOut(cost_grp),
            FadeOut(latency_lbl),
            run_time=0.25,
        )
        self.play(
            Create(ddr_x), Create(vdma_x),
            ddr_block.animate.set_opacity(0.25),
            vdma_block.animate.set_opacity(0.25),
            std_arrows[0].animate.set_opacity(0.15),
            std_arrows[1].animate.set_opacity(0.15),
            std_arrows[2].animate.set_opacity(0.15),
            run_time=0.55,
        )
        self.wait(0.3)

        # Slide surviving blocks left and draw direct green arrow
        raycaster_block = pipe_block("Raycaster", "AXI-Stream",
                                     PYNQ_RED, "#1A0505", w=2.2)

        new_pipeline = VGroup(raycaster_block,
                              vtc_block.copy(),
                              hdmi_block.copy())
        new_pipeline.arrange(RIGHT, buff=0.55).move_to(DOWN*1.5)
        if new_pipeline.get_width() > 9.0:
            new_pipeline.scale_to_fit_width(9.0)

        new_arrows = VGroup(
            flow_arrow(new_pipeline[0].get_right(),
                       new_pipeline[1].get_left(), color=ACCENT_GREEN),
            flow_arrow(new_pipeline[1].get_right(),
                       new_pipeline[2].get_left(), color=ACCENT_GREEN),
        )

        direct_lbl = Text("direct AXI-Stream — no memory transaction",
                          font_size=16, color=ACCENT_GREEN, weight=BOLD)
        direct_lbl.next_to(new_pipeline, DOWN, buff=0.22)

        self.play(
            LaggedStart(*[FadeIn(b, shift=UP*0.15) for b in new_pipeline],
                        lag_ratio=0.15),
            run_time=0.6,
        )
        self.play(FadeIn(new_arrows, lag_ratio=0.2), run_time=0.35)
        self.play(FadeIn(direct_lbl, shift=UP*0.1), run_time=0.3)
        self.wait(0.8)

        # ── BEAT 4: Gains (5 s) ───────────────────────────────────────────
        self.play(FadeOut(VGroup(
            std_pipeline, std_arrows, ddr_x, vdma_x,
            new_pipeline, new_arrows, direct_lbl,
        )), run_time=0.4)

        gain_data = [
            ("16.7 ms  →  <1 µs",  "end-to-end pixel latency",  ACCENT_GREEN),
            ("35 words/tick",       "PS BRAM write per frame",   ACCENT_SERVER),
            ("no tearing",          "no shared framebuffer",     ACCENT_HARDWARE),
        ]
        gain_cards = VGroup(*[
            stat_card(v, d, c) for v, d, c in gain_data
        ]).arrange(RIGHT, buff=0.5).move_to(UP*0.5)

        vtc_line1 = Text("VTC driven by fixed pixel clock — frame rate physically decoupled from PS scheduling.",
                         font_size=17, color=TEXT_MUTED)
        vtc_line1.next_to(gain_cards, DOWN, buff=0.8)

        self.play(
            LaggedStart(*[FadeIn(c, shift=UP*0.15) for c in gain_cards],
                        lag_ratio=0.18),
            run_time=0.8,
        )
        self.play(FadeIn(vtc_line1, shift=UP*0.1), run_time=0.4)
        self.wait(2.2)
        self.play(FadeOut(VGroup(gain_cards, vtc_line1)), run_time=0.5)