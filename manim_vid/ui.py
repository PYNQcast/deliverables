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
GRID_COLOR      = "#3A5070"
GLYPH_ON        = "#C8D8E8"
GLYPH_OFF       = "#1E2D3D"
GLYPH_ACTIVE    = "#F05252"
GLYPH_SELECT    = "#7BD88F"

# ---------------------------------------------------------------------------
# 8x16 'A' — wide strokes, flat crossbar at rows 5-6
# ---------------------------------------------------------------------------
CHAR_A = [
    0b00011000,
    0b00111100,
    0b01100110,
    0b11000011,
    0b11000011,
    0b11111111,  # crossbar row 5 — active in demo
    0b11111111,
    0b11000011,
    0b11000011,
    0b11000011,
    0b00000000, 0b00000000, 0b00000000,
    0b00000000, 0b00000000, 0b00000000,
]

CHAR_H = [
    0b11000011,
    0b11000011,
    0b11000011,
    0b11000011,
    0b11111111,
    0b11111111,
    0b11000011,
    0b11000011,
    0b11000011,
    0b11000011,
    0b00000000, 0b00000000, 0b00000000,
    0b00000000, 0b00000000, 0b00000000,
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def glyph_grid(pattern, cell=0.22, active_row=-1, select_col=-1):
    rows, cols = len(pattern), 8
    g = VGroup()
    for r in range(rows):
        for c in range(cols):
            bit   = (pattern[r] >> (7 - c)) & 1
            fill  = GLYPH_ON if bit else GLYPH_OFF
            sw, sc = 0.5, GRID_COLOR
            if r == active_row:
                fill, sw, sc = GLYPH_ACTIVE, 1.2, GLYPH_ACTIVE
            sq = Square(side_length=cell, stroke_width=sw, stroke_color=sc)
            sq.set_fill(fill, opacity=0.95)
            if r == active_row and c == select_col:
                sq.set_stroke(color=GLYPH_SELECT, width=2.8)
            sq.move_to(np.array([
                (c - cols/2 + 0.5)*cell,
                -(r - rows/2 + 0.5)*cell,
                0,
            ]))
            g.add(sq)
    return g


def pipe_box(title_str, sub_str, col, w=2.0, h=1.0):
    box = RoundedRectangle(corner_radius=0.15, width=w, height=h,
                           stroke_color=col, stroke_width=2,
                           fill_color=PANEL_FILL, fill_opacity=0.95)
    t = Text(title_str, font_size=17, color=col,        weight=BOLD)
    s = Text(sub_str,   font_size=12, color=TEXT_MUTED)
    VGroup(t, s).arrange(DOWN, buff=0.06).move_to(box)
    return VGroup(box, t, s)


def ip_tag(label, color):
    bg = RoundedRectangle(corner_radius=0.07, width=2.2, height=0.32,
                          stroke_color=color, stroke_width=1.5,
                          fill_color=PANEL_FILL, fill_opacity=0.92)
    tx = Text(label, font_size=13, color=color, weight=BOLD)
    tx.move_to(bg)
    return VGroup(bg, tx)


def stat_card(val, desc, col, w=3.2, h=1.3):
    box = RoundedRectangle(corner_radius=0.15, width=w, height=h,
                           stroke_color=col, stroke_width=2,
                           fill_color=PANEL_FILL, fill_opacity=0.95)
    v = Text(val,  font_size=26, color=col,        weight=BOLD)
    d = Text(desc, font_size=15, color=TEXT_MUTED)
    VGroup(v, d).arrange(DOWN, buff=0.1).move_to(box)
    return VGroup(box, v, d)


# ---------------------------------------------------------------------------
# Scene
# ---------------------------------------------------------------------------

class UIOverlayScene(Scene):

    def construct(self):
        self.camera.background_color = BACKGROUND

        # ── BEAT 1: Title (2 s) ──────────────────────────────────────────
        title = Text("Extension: UI Overlay", font_size=52,
                     weight=BOLD, color=PYNQ_RED)
        sub   = Text("Hardware compositing at pixel-clock rate",
                     font_size=24, color=TEXT_MUTED)
        sub.next_to(title, DOWN, buff=0.3)
        VGroup(title, sub).move_to(ORIGIN)

        self.play(Write(title), run_time=0.6)
        self.play(FadeIn(sub, shift=UP*0.15), run_time=0.4)
        self.wait(0.7)
        self.play(FadeOut(VGroup(title, sub)), run_time=0.35)

        # ── BEAT 2: Pipeline strip (4 s) ─────────────────────────────────
        stage_data = [
            ("Raycaster",    "pixel stream",    PYNQ_RED),
            ("Textbox IP",   "8 slots · comb.", ACCENT_HARDWARE),
            ("Text overlay", "glyph BRAM",      ACCENT_SERVER),
            ("Fill bars",    "reg. multiply",   ACCENT_GREEN),
            ("HDMI out",     "VTC · RGB2DVI",   TEXT_DIM),
        ]
        boxes = VGroup(*[pipe_box(t, s, c) for t, s, c in stage_data])
        boxes.arrange(RIGHT, buff=0.28).to_edge(UP, buff=0.32)
        if boxes.get_width() > 13.0:
            boxes.scale_to_fit_width(13.0)

        pipe_arrows = VGroup(*[
            Arrow(boxes[i].get_right(), boxes[i+1].get_left(),
                  buff=0.05, stroke_width=2.5, color=TEXT_DIM,
                  max_tip_length_to_length_ratio=0.18)
            for i in range(len(boxes)-1)
        ])

        latency_pill = RoundedRectangle(
            corner_radius=0.1, width=6.0, height=0.4,
            stroke_color=ACCENT_HARDWARE, stroke_width=1.5,
            fill_color=PANEL_FILL, fill_opacity=0.9)
        latency_txt = Text("combinatorial logic · 1 cycle pipeline latency",
                           font_size=14, color=ACCENT_HARDWARE)
        latency_txt.move_to(latency_pill)
        latency_grp = VGroup(latency_pill, latency_txt)
        latency_grp.next_to(VGroup(boxes[1], boxes[2], boxes[3]),
                            DOWN, buff=0.16)

        self.play(LaggedStart(*[FadeIn(b, shift=RIGHT*0.1) for b in boxes],
                              lag_ratio=0.1), run_time=0.8)
        self.play(FadeIn(pipe_arrows, lag_ratio=0.08), run_time=0.35)
        self.play(FadeIn(latency_grp, shift=UP*0.1), run_time=0.3)
        self.wait(1.2)
        self.play(FadeOut(latency_grp), run_time=0.25)

        # ── BEAT 3: Countdown timer UI build (8 s) ───────────────────────
        # Panel background — textbox IP
        panel_w, panel_h = 5.6, 2.8
        panel = RoundedRectangle(
            corner_radius=0.18, width=panel_w, height=panel_h,
            stroke_color=ACCENT_HARDWARE, stroke_width=3,
            fill_color="#0B1E30", fill_opacity=1.0)
        panel.move_to(DOWN*0.9)

        tag_tb = ip_tag("Textbox IP", ACCENT_HARDWARE)
        tag_tb.next_to(panel, DOWN, buff=0.14)

        self.play(FadeIn(panel), FadeIn(tag_tb), run_time=0.45)
        self.wait(0.3)

        # Fill bar — fill bars IP
        bar_bg = Rectangle(width=4.4, height=0.52,
                           stroke_width=0,
                           fill_color="#0D2535", fill_opacity=1.0)
        bar_bg.move_to(panel.get_center() + DOWN*0.72)

        bar_fill = Rectangle(width=4.4, height=0.52,
                             stroke_width=0,
                             fill_color=ACCENT_GREEN, fill_opacity=0.9)
        bar_fill.move_to(bar_bg.get_left() + RIGHT*2.2)

        bar_border = Rectangle(width=4.4, height=0.52,
                               stroke_color=ACCENT_GREEN, stroke_width=1.8,
                               fill_opacity=0)
        bar_border.move_to(bar_bg.get_center())

        tag_bar = ip_tag("Fill bar IP", ACCENT_GREEN)
        tag_bar.next_to(panel, DOWN, buff=0.14)

        self.play(FadeOut(tag_tb), run_time=0.15)
        self.play(FadeIn(bar_bg), FadeIn(bar_fill), FadeIn(bar_border),
                  FadeIn(tag_bar), run_time=0.4)

        # Animate bar draining (countdown)
        self.play(
            bar_fill.animate.stretch_to_fit_width(0.05)
                             .move_to(bar_bg.get_left() + RIGHT*0.025),
            run_time=0.6,
            rate_func=linear,
        )
        self.wait(0.2)

        # Text label — text overlay IP — pixel-rendered clock 00:03 -> 00:02 -> 00:01 -> 00:00
        # All digits and colon as bitmap pixel grids, same style as glyph_grid

        DIGIT = {
            0: [
                0b01111110, 0b11000011, 0b11000011, 0b11000011,
                0b11000011, 0b11000011, 0b11000011, 0b11000011,
                0b11000011, 0b01111110,
                0b00000000, 0b00000000, 0b00000000,
                0b00000000, 0b00000000, 0b00000000,
            ],
            1: [
                0b00011000, 0b00111000, 0b01111000, 0b00011000,
                0b00011000, 0b00011000, 0b00011000, 0b00011000,
                0b11111111, 0b11111111,
                0b00000000, 0b00000000, 0b00000000,
                0b00000000, 0b00000000, 0b00000000,
            ],
            2: [
                0b01111110, 0b11111111, 0b00000011, 0b00000011,
                0b01111110, 0b11111100, 0b11000000, 0b11000000,
                0b11111111, 0b11111111,
                0b00000000, 0b00000000, 0b00000000,
                0b00000000, 0b00000000, 0b00000000,
            ],
            3: [
                0b01111110, 0b11111111, 0b00000011, 0b00000011,
                0b00111110, 0b00111110, 0b00000011, 0b00000011,
                0b11111111, 0b01111110,
                0b00000000, 0b00000000, 0b00000000,
                0b00000000, 0b00000000, 0b00000000,
            ],
        }
        # colon: two small dots in an 8-wide pattern
        COLON = [
            0b00000000, 0b00011000, 0b00011000, 0b00000000,
            0b00000000, 0b00000000, 0b00011000, 0b00011000,
            0b00000000, 0b00000000,
            0b00000000, 0b00000000, 0b00000000,
            0b00000000, 0b00000000, 0b00000000,
        ]

        def pix_char(pattern, ox, oy, cell=0.09, rows=10, on_col=GLYPH_ON):
            g = VGroup()
            for r in range(rows):
                for c in range(8):
                    bit = (pattern[r] >> (7-c)) & 1
                    sq = Square(side_length=cell, stroke_width=0)
                    sq.set_fill(on_col if bit else "#0B1E30", opacity=0.95)
                    sq.move_to(np.array([ox + c*cell, oy - r*cell, 0]))
                    g.add(sq)
            return g

        cell  = 0.09
        gap   = 0.04          # gap between characters
        cw    = 8 * cell + gap  # character slot width

        def build_clock(mm1, mm2, ss1, ss2):
            ox = panel.get_center()[0] - 2.5*cw
            oy = panel.get_center()[1] + 0.52
            return VGroup(
                pix_char(DIGIT[mm1], ox + 0*cw, oy),
                pix_char(DIGIT[mm2], ox + 1*cw, oy),
                pix_char(COLON,      ox + 2*cw, oy, on_col=GLYPH_ON),
                pix_char(DIGIT[ss1], ox + 3*cw, oy),
                pix_char(DIGIT[ss2], ox + 4*cw, oy),
            )

        clk3 = build_clock(0, 0, 0, 3)
        clk2 = build_clock(0, 0, 0, 2)
        clk1 = build_clock(0, 0, 0, 1)
        clk0 = build_clock(0, 0, 0, 0)

        tag_txt = ip_tag("Text overlay IP", ACCENT_SERVER)
        tag_txt.next_to(panel, DOWN, buff=0.14)

        self.play(FadeOut(tag_bar), run_time=0.15)
        self.play(FadeIn(clk3), FadeIn(tag_txt), run_time=0.25)
        self.wait(0.18)
        self.play(FadeOut(clk3), run_time=0.08)
        self.play(FadeIn(clk2), run_time=0.08)
        self.wait(0.18)
        self.play(FadeOut(clk2), run_time=0.08)
        self.play(FadeIn(clk1), run_time=0.08)
        self.wait(0.18)
        self.play(FadeOut(clk1), run_time=0.08)
        self.play(FadeIn(clk0), run_time=0.08)
        self.wait(0.15)

        text_chars = clk0  # keep reference for FadeOut below

        # ── BEAT 4: Glyph lookup (7 s) ───────────────────────────────────
        self.play(
            FadeOut(VGroup(panel, bar_bg, bar_fill, bar_border,
                           text_chars, tag_txt)),
            run_time=0.4,
        )

        # Shrink pipeline strip, make room
        self.play(
            boxes.animate.scale(0.7).to_edge(UP, buff=0.22),
            pipe_arrows.animate.scale(0.7).to_edge(UP, buff=0.22),
            run_time=0.4,
        )

        # Glyph grid — left
        g = glyph_grid(CHAR_A, cell=0.26, active_row=5, select_col=2)
        g.move_to(LEFT*4.0 + DOWN*0.55)
        g_lbl = Text("'A'  (8×16)", font_size=17, color=TEXT_MUTED)
        g_lbl.next_to(g, DOWN, buff=0.16)

        row_y = g[5*8].get_center()[1]
        row_arr = Arrow(
            np.array([g.get_right()[0]+0.04, row_y, 0]),
            np.array([g.get_right()[0]+0.72, row_y, 0]),
            buff=0, stroke_width=2.5, color=GLYPH_ACTIVE,
            max_tip_length_to_length_ratio=0.22)
        row_lbl = Text("row 5", font_size=14, color=GLYPH_ACTIVE)
        row_lbl.next_to(row_arr, UP, buff=0.06)

        # BRAM box — centre
        bram = RoundedRectangle(corner_radius=0.14, width=3.4, height=1.55,
                                stroke_color=ACCENT_SERVER, stroke_width=2,
                                fill_color=PANEL_FILL, fill_opacity=0.95)
        bram.move_to(ORIGIN + DOWN*0.5)
        bram_lines = VGroup(
            Text("BRAM lookup",              font_size=17,
                 color=ACCENT_SERVER, weight=BOLD),
            Text("addr = (65−32)×16+5 = 533", font_size=14,
                 color=TEXT_PRIMARY),
            Text("→  0xFF  (all bits set)",   font_size=14,
                 color=GLYPH_ACTIVE),
        ).arrange(DOWN, buff=0.11, aligned_edge=LEFT).move_to(bram)

        arr_to_bram = Arrow(row_arr.get_right(), bram.get_left(),
                            buff=0.08, stroke_width=2.5,
                            color=GLYPH_ACTIVE,
                            max_tip_length_to_length_ratio=0.18)

        # Bit cells — right
        bit_cells = VGroup()
        for i in range(7, -1, -1):
            cell = Square(side_length=0.34, stroke_width=1,
                          stroke_color=GRID_COLOR)
            cell.set_fill(GLYPH_ACTIVE, opacity=0.95)
            bl = Text("1", font_size=12, color=TEXT_PRIMARY)
            bl.move_to(cell)
            il = Text(str(i), font_size=10, color=TEXT_DIM)
            il.next_to(cell, DOWN, buff=0.04)
            bit_cells.add(VGroup(cell, bl, il))
        bit_cells.arrange(RIGHT, buff=0.04).move_to(RIGHT*4.2 + DOWN*0.55)
        bit_cells[5][0].set_stroke(color=GLYPH_SELECT, width=3)

        bit_hdr = Text("0xFF", font_size=18, color=TEXT_MUTED, weight=BOLD)
        bit_hdr.next_to(bit_cells, UP, buff=0.16)

        sel_arr = Arrow(
            bit_cells[5].get_bottom(),
            bit_cells[5].get_bottom() + DOWN*0.45,
            buff=0, stroke_width=2.5, color=GLYPH_SELECT,
            max_tip_length_to_length_ratio=0.28)
        sel_lbl = Text("bit 2 → pixel ON", font_size=15,
                       color=GLYPH_SELECT, weight=BOLD)
        sel_lbl.next_to(sel_arr, DOWN, buff=0.08)

        arr_to_bits = Arrow(bram.get_right(), bit_cells.get_left(),
                            buff=0.08, stroke_width=2.5,
                            color=ACCENT_SERVER,
                            max_tip_length_to_length_ratio=0.18)

        cycle_pill = RoundedRectangle(
            corner_radius=0.09, width=9.5, height=0.4,
            stroke_color=ACCENT_GREEN, stroke_width=1.5,
            fill_color=PANEL_FILL, fill_opacity=0.92)
        cycle_txt = Text(
            "addr computed  →  byte fetched  →  bit selected  →  pixel out.  "
            "1 clock cycle.",
            font_size=14, color=ACCENT_GREEN)
        cycle_txt.move_to(cycle_pill)
        cycle_grp = VGroup(cycle_pill, cycle_txt)
        cycle_grp.to_edge(DOWN, buff=0.22)

        self.play(FadeIn(g, lag_ratio=0.003), FadeIn(g_lbl), run_time=0.55)
        self.play(GrowArrow(row_arr), FadeIn(row_lbl), run_time=0.35)
        self.play(GrowArrow(arr_to_bram), run_time=0.3)
        self.play(FadeIn(bram), Write(bram_lines[0]), run_time=0.3)
        self.play(FadeIn(bram_lines[1]), run_time=0.25)
        self.play(FadeIn(bram_lines[2]), run_time=0.25)
        self.play(GrowArrow(arr_to_bits), run_time=0.3)
        self.play(FadeIn(bit_hdr),
                  LaggedStart(*[FadeIn(bc) for bc in bit_cells],
                              lag_ratio=0.05), run_time=0.5)
        self.play(GrowArrow(sel_arr), FadeIn(sel_lbl), run_time=0.4)
        self.play(FadeIn(cycle_grp), run_time=0.35)
        self.wait(1.2)

        # ── BEAT 5: Stat cards (4 s) ─────────────────────────────────────
        self.play(FadeOut(VGroup(
            g, g_lbl, row_arr, row_lbl, arr_to_bram,
            bram, bram_lines,
            arr_to_bits, bit_hdr, bit_cells, sel_arr, sel_lbl,
            cycle_grp, boxes, pipe_arrows,
        )), run_time=0.4)

        stats = VGroup(
            stat_card("~180 LUTs",    "combinatorial logic",   ACCENT_HARDWARE),
            stat_card("1 BRAM tile",  "glyph + sprite store",  ACCENT_SERVER),
            stat_card("55 MB/s saved","vs software at 480p",   ACCENT_GREEN),
        ).arrange(RIGHT, buff=0.5).move_to(DOWN*0.2)

        self.play(LaggedStart(*[FadeIn(s, shift=UP*0.15) for s in stats],
                              lag_ratio=0.18), run_time=0.8)
        self.wait(1.6)
        self.play(FadeOut(stats), run_time=0.5)

        # ── BEAT 6: Live demo section (5 s) ──────────────────────────────
        # Replace this ImageMobject path with your actual recording frame
        # or swap the whole block for a video in Canva post-export.
        demo_border = RoundedRectangle(
            corner_radius=0.22, width=11.5, height=6.2,
            stroke_color=ACCENT_SERVER, stroke_width=3,
            fill_color="#050D18", fill_opacity=1.0,
        ).move_to(ORIGIN)

        # Placeholder — swap with:
        #   img = ImageMobject("path/to/your/frame.png")
        #   img.set(width=11.5).move_to(ORIGIN)
        #   self.play(FadeIn(img), ...)
        placeholder_txt = Text(
            "[ insert UI recording here ]",
            font_size=32, color=TEXT_DIM,
        ).move_to(ORIGIN)

        demo_label = Text(
            "UI overlay — live on PYNQ",
            font_size=22, color=ACCENT_SERVER, weight=BOLD,
        )
        demo_label.next_to(demo_border, DOWN, buff=0.18)

        self.play(FadeIn(demo_border), FadeIn(placeholder_txt),
                  FadeIn(demo_label), run_time=0.5)
        self.wait(4.2)
        self.play(FadeOut(VGroup(demo_border, placeholder_txt, demo_label)),
                  run_time=0.4)