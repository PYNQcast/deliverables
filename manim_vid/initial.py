from manim import *
import numpy as np


# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
PYNQ_RED       = "#f05252"
PYNQ_RED_DARK  = "#c93c3c"
BACKGROUND     = "#07111C"
PANEL_FILL     = "#10243A"
PANEL_STROKE   = "#58C4DD"
TEXT_PRIMARY   = "#F4F7FB"
TEXT_MUTED     = "#B8CCE0"   # was #9FB3C8 — lifted for readability
TEXT_DIM       = "#7A9AB8"   # for truly secondary info
ACCENT_HARDWARE = "#F7A541"
ACCENT_SERVER   = "#58C4DD"
ACCENT_STORAGE  = "#7BD88F"
ACCENT_ALERT    = "#FF6B6B"
GRID_COLOR      = "#3A5070"  # was GREY_B — warmer on dark bg
WALL_COLOR      = "#4A6FA5"
WALL_COLOR_DARK = "#3A5A8A"
EMPTY_COLOR     = "#1A1A2E"
PLAYER_A_COLOR  = PYNQ_RED
PLAYER_B_COLOR  = "#58C4DD"
RAY_COLOR       = "#FFE066"  # warmer yellow
FOV_COLOR       = "#FFAA33"
HIT_COLOR       = "#6EE7A0"  # brighter green


LODEV_RED       = "#E02020"
LODEV_GREEN     = "#00AA00"
LODEV_BLUE      = "#4477DD"
LODEV_ORANGE    = "#FF8800"
LODEV_WALL_BLUE = "#3366FF"
LODEV_GRID      = "#AABBCC"


ALGO_WORLD_MAP = [
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 0, 0, 1],
    [1, 0, 1, 0, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 1, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1],
]


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def make_world_grid(world_map, cell_size=0.6, empty_opacity=0.6):
    map_rows = len(world_map)
    map_cols = len(world_map[0])
    grid_group = VGroup()
    for row in range(map_rows):
        for col in range(map_cols):
            square = Square(side_length=cell_size, stroke_width=1, stroke_color=GRID_COLOR)
            if world_map[row][col] == 1:
                square.set_fill(WALL_COLOR, opacity=0.92)
            else:
                square.set_fill(EMPTY_COLOR, opacity=empty_opacity)
            square.move_to(np.array([
                (col - map_cols / 2 + 0.5) * cell_size,
                -(row - map_rows / 2 + 0.5) * cell_size,
                0,
            ]))
            grid_group.add(square)
    return grid_group


def grid_cell_center(grid_group, row, col, map_cols):
    return grid_group[row * map_cols + col].get_center()


def point_to_grid_cell(point, grid_group, map_rows, map_cols, cell_size):
    rel = point - grid_group.get_center()
    col = int(np.floor(rel[0] / cell_size + map_cols / 2))
    row = int(np.floor(-rel[1] / cell_size + map_rows / 2))
    return row, col


def make_panel(title: str, subtitle: str, width: float, height: float, accent: str) -> VGroup:
    box = RoundedRectangle(
        corner_radius=0.2, width=width, height=height,
        stroke_color=accent, stroke_width=2,
        fill_color=PANEL_FILL, fill_opacity=0.95,
    )
    title_text    = Text(title,    font_size=26, color=TEXT_PRIMARY, weight=BOLD)
    subtitle_text = Text(subtitle, font_size=17, color=TEXT_MUTED)
    copy = VGroup(title_text, subtitle_text).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
    copy.move_to(box.get_center())
    return VGroup(box, copy)


def make_label(text: str, font_size: int = 22, color: str = TEXT_MUTED) -> Text:
    """Consistent body-copy helper — never go below 22 px."""
    return Text(text, font_size=max(font_size, 22), color=color)


def make_seda_pipeline() -> VGroup:
    labels = [
        ("T1", "UDP Receive"),
        ("T2", "20 Hz Game Tick"),
        ("T3", "Broadcast"),
        ("T4", "Redis Write"),
    ]
    stages = VGroup()
    for code, label in labels:
        stages.add(make_panel(code, label, width=2.3, height=1.15, accent=ACCENT_SERVER))
    stages.arrange(DOWN, buff=0.22)
    connectors = VGroup()
    for idx in range(len(stages) - 1):
        arrow = Arrow(
            stages[idx].get_bottom() + DOWN * 0.04,
            stages[idx + 1].get_top() + UP * 0.04,
            buff=0.05, stroke_width=4,
            max_tip_length_to_length_ratio=0.16,
            color=ACCENT_SERVER,
        )
        connectors.add(arrow)
    return VGroup(stages, connectors)


def make_storage_row() -> VGroup:
    redis_panel  = make_panel("Redis",    "hot state + control",   width=2.8, height=1.2, accent=ACCENT_SERVER)
    dynamo_panel = make_panel("DynamoDB", "warm metadata",         width=2.8, height=1.2, accent=ACCENT_STORAGE)
    s3_panel     = make_panel("S3 / SNS", "cold replay + fan-out", width=3.0, height=1.2, accent=ACCENT_STORAGE)
    row = VGroup(redis_panel, dynamo_panel, s3_panel).arrange(RIGHT, buff=0.35)
    arrows = VGroup(
        Arrow(redis_panel.get_right(),  dynamo_panel.get_left(), buff=0.08, stroke_width=4, color=ACCENT_STORAGE),
        Arrow(dynamo_panel.get_right(), s3_panel.get_left(),     buff=0.08, stroke_width=4, color=ACCENT_STORAGE),
    )
    return VGroup(row, arrows)


def make_hardware_lane() -> VGroup:
    board_a    = make_panel("PYNQ Board A", "HDMI + FPGA raycaster",     width=3.2, height=1.35, accent=ACCENT_HARDWARE)
    board_b    = make_panel("PYNQ Board B", "manual or auto role",        width=3.2, height=1.35, accent=ACCENT_HARDWARE)
    controller = make_panel("Controls",    "buttons / joystick / AI",     width=3.2, height=1.1,  accent=ACCENT_HARDWARE)
    return VGroup(board_a, board_b, controller).arrange(DOWN, buff=0.28)


def make_service_branch() -> VGroup:
    sidecar = make_panel("Python Sidecar", "AWS writes off the hot path",  width=3.4, height=1.25, accent=ACCENT_STORAGE)
    monitor = make_panel("Live Monitor",   "WebSocket + replay + control", width=3.4, height=1.25, accent=ACCENT_SERVER)
    return VGroup(sidecar, monitor).arrange(DOWN, buff=0.3)

# ---------------------------------------------------------------------------
# Helper: right-angle marker
# ---------------------------------------------------------------------------
def right_angle_mark(vertex, v1_dir, v2_dir, size=0.15, color=WHITE, stroke_width=1.8):
    v1 = np.array(v1_dir[:3] if len(v1_dir) >= 3 else list(v1_dir) + [0])
    v2 = np.array(v2_dir[:3] if len(v2_dir) >= 3 else list(v2_dir) + [0])
    v1 = v1 / (np.linalg.norm(v1) + 1e-12) * size
    v2 = v2 / (np.linalg.norm(v2) + 1e-12) * size
    p1 = vertex + v1
    p2 = vertex + v1 + v2
    p3 = vertex + v2
    return VGroup(
        Line(p1, p2, stroke_color=color, stroke_width=stroke_width),
        Line(p3, p2, stroke_color=color, stroke_width=stroke_width),
    )
 
 
# ---------------------------------------------------------------------------
# Helper: label with dark background pad so it reads over lines
# ---------------------------------------------------------------------------
def backed_label(text_str, font_size=17, color=WHITE, weight=NORMAL,
                 slant=NORMAL, bg_opacity=0.85, buff=0.06):
    txt = Text(text_str, font_size=font_size, color=color,
               weight=weight, slant=slant)
    bg = Rectangle(
        width=txt.width + buff * 2,
        height=txt.height + buff * 2,
        fill_color=BACKGROUND, fill_opacity=bg_opacity,
        stroke_width=0,
    ).move_to(txt.get_center())
    return VGroup(bg, txt)


# ---------------------------------------------------------------------------
# Scenes
# ---------------------------------------------------------------------------

class TitleScene(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND

        # Subtle grid backdrop
        grid_lines = VGroup()
        for x in np.arange(-7, 7.5, 1.4):
            grid_lines.add(Line([x, -4, 0], [x, 4, 0], stroke_color="#0D2035", stroke_width=1))
        for y in np.arange(-4, 4.5, 1.4):
            grid_lines.add(Line([-7, y, 0], [7, y, 0], stroke_color="#0D2035", stroke_width=1))
        self.add(grid_lines)

        title    = Text("PYNQ CAST", font_size=80, weight=BOLD, color=PYNQ_RED)
        subtitle = Text("Distributed FPGA Raycasting", font_size=38, color=TEXT_PRIMARY)
        subtitle.next_to(title, DOWN, buff=0.45)
        tagline  = Text("Two players. One map. Hardware-accelerated.", font_size=26, color=TEXT_MUTED)
        tagline.next_to(subtitle, DOWN, buff=0.55)

        underline = Line(
            title.get_left() + DOWN * 0.15,
            title.get_right() + DOWN * 0.15,
            stroke_color=PYNQ_RED_DARK, stroke_width=3,
        ).next_to(title, DOWN, buff=0.1)

        self.play(Write(title), run_time=1.5)
        self.play(Create(underline), run_time=0.4)
        self.play(FadeIn(subtitle, shift=UP * 0.3), run_time=0.9)
        self.wait(0.3)
        self.play(FadeIn(tagline, shift=UP * 0.2), run_time=0.8)
        self.wait(2.2)
        self.play(FadeOut(VGroup(grid_lines, title, underline, subtitle, tagline)), run_time=0.9)


class GridMapScene(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND

        section = Text("1. The 2D Grid Map", font_size=42, color=PYNQ_RED, weight=BOLD)
        section.to_edge(UP, buff=0.4)
        self.play(Write(section), run_time=0.8)

        world_map = ALGO_WORLD_MAP
        map_rows  = len(world_map)
        map_cols  = len(world_map[0])
        cell_size = 0.65
        grid_group = make_world_grid(world_map, cell_size=cell_size)
        grid_group.shift(DOWN * 0.25)

        self.play(FadeIn(grid_group, lag_ratio=0.01), run_time=1.4)
        self.wait(0.4)

        # ── Legend ────────────────────────────────────────────────────────
        wall_swatch  = Square(0.3, stroke_width=0).set_fill(WALL_COLOR, opacity=0.92)
        empty_swatch = Square(0.3, stroke_width=0).set_fill(EMPTY_COLOR, opacity=0.85)
        wall_label   = Text("Wall (1)",  font_size=22, color=TEXT_PRIMARY)
        empty_label  = Text("Empty (0)", font_size=22, color=TEXT_MUTED)
        legend = VGroup(
            VGroup(wall_swatch,  wall_label ).arrange(RIGHT, buff=0.18),
            VGroup(empty_swatch, empty_label).arrange(RIGHT, buff=0.18),
        ).arrange(RIGHT, buff=1.2)
        legend.next_to(grid_group, DOWN, buff=0.55)
        self.play(FadeIn(legend), run_time=0.6)

        bram_text = Text(
            "Stored in FPGA Block RAM — each cell is a single bit",
            font_size=24, color=TEXT_MUTED,
        )
        bram_text.next_to(legend, DOWN, buff=0.38)
        self.play(FadeIn(bram_text, shift=UP * 0.2), run_time=0.8)
        self.wait(0.8)

        # ── Players ───────────────────────────────────────────────────────
        # Player A (red) and Player B (blue) at different positions
        pos_a = grid_cell_center(grid_group, 5, 2, map_cols)
        pos_b = grid_cell_center(grid_group, 1, 5, map_cols)

        player_a = Dot(pos_a, radius=0.14, color=PLAYER_A_COLOR, z_index=5)
        player_b = Dot(pos_b, radius=0.14, color=PLAYER_B_COLOR, z_index=5)
        lbl_a = Text("Player A", font_size=18, color=PLAYER_A_COLOR)
        lbl_a.next_to(player_a, LEFT, buff=0.18)
        lbl_b = Text("Player B", font_size=18, color=PLAYER_B_COLOR)
        lbl_b.next_to(player_b, RIGHT, buff=0.18)

        self.play(FadeIn(player_a, scale=0.5), FadeIn(lbl_a), run_time=0.5)
        self.play(FadeIn(player_b, scale=0.5), FadeIn(lbl_b), run_time=0.5)
        self.wait(0.5)

        # ── Ghosts (AI-controlled, like pac-man) ─────────────────────────
        GHOST_COLOR = "#BB66FF"
        ghost_positions = [
            grid_cell_center(grid_group, 1, 1, map_cols),
            grid_cell_center(grid_group, 5, 5, map_cols),
        ]
        ghosts = VGroup()
        ghost_lbls = VGroup()
        for i, gp in enumerate(ghost_positions):
            # Simple ghost shape: circle + three bumps at the bottom
            body = Circle(radius=0.18, fill_color=GHOST_COLOR,
                          fill_opacity=0.85, stroke_width=0, z_index=5)
            body.move_to(gp + UP * 0.04)
            # Eyes
            eye_l = Dot(gp + np.array([-0.07, 0.08, 0]), radius=0.04,
                        color=WHITE, z_index=6)
            eye_r = Dot(gp + np.array([0.07, 0.08, 0]), radius=0.04,
                        color=WHITE, z_index=6)
            pupil_l = Dot(gp + np.array([-0.05, 0.08, 0]), radius=0.02,
                          color="#222244", z_index=7)
            pupil_r = Dot(gp + np.array([0.09, 0.08, 0]), radius=0.02,
                          color="#222244", z_index=7)
            ghost = VGroup(body, eye_l, eye_r, pupil_l, pupil_r)
            ghosts.add(ghost)

        ghost_lbl = Text("Ghosts (AI)", font_size=18, color=GHOST_COLOR)
        ghost_lbl.next_to(ghosts[0], UP, buff=0.20)

        self.play(
            *[FadeIn(g, scale=0.5) for g in ghosts],
            FadeIn(ghost_lbl),
            run_time=0.6,
        )
        self.wait(0.6)

        # ── Animate movement: players walk, ghosts chase ──────────────────
        # Player A moves right then up
        pa_wp1 = grid_cell_center(grid_group, 5, 4, map_cols)
        pa_wp2 = grid_cell_center(grid_group, 4, 4, map_cols)
        pa_wp3 = grid_cell_center(grid_group, 3, 4, map_cols)

        # Player B moves left
        pb_wp1 = grid_cell_center(grid_group, 1, 3, map_cols)
        pb_wp2 = grid_cell_center(grid_group, 1, 2, map_cols)

        # Ghost 0 chases Player B (moves right)
        g0_wp1 = grid_cell_center(grid_group, 1, 2, map_cols)

        # Ghost 1 chases Player A (moves left then up)
        g1_wp1 = grid_cell_center(grid_group, 5, 4, map_cols)
        g1_wp2 = grid_cell_center(grid_group, 4, 4, map_cols)

        # Step 1: everyone moves
        self.play(
            player_a.animate.move_to(pa_wp1),
            lbl_a.animate.move_to(pa_wp1 + LEFT * 0.7),
            player_b.animate.move_to(pb_wp1),
            lbl_b.animate.move_to(pb_wp1 + RIGHT * 0.7),
            ghosts[1].animate.move_to(g1_wp1),
            run_time=0.6,
        )
        # Step 2
        self.play(
            player_a.animate.move_to(pa_wp2),
            lbl_a.animate.move_to(pa_wp2 + LEFT * 0.7),
            player_b.animate.move_to(pb_wp2),
            lbl_b.animate.move_to(pb_wp2 + RIGHT * 0.7),
            ghosts[0].animate.move_to(g0_wp1),
            ghost_lbl.animate.move_to(g0_wp1 + UP * 0.35),
            run_time=0.6,
        )
        # Step 3: Player A keeps going, ghost catches up
        self.play(
            player_a.animate.move_to(pa_wp3),
            lbl_a.animate.move_to(pa_wp3 + LEFT * 0.7),
            ghosts[1].animate.move_to(g1_wp2),
            run_time=0.6,
        )
        self.wait(0.5)

        # ── Entity legend at the bottom ───────────────────────────────────
        # Fade out the wall/empty legend and replace with entity legend
        self.play(FadeOut(legend), FadeOut(bram_text), run_time=0.3)

        ent_legend = VGroup(
            VGroup(
                Dot(radius=0.09, color=PLAYER_A_COLOR),
                Text("Player A", font_size=18, color=PLAYER_A_COLOR),
            ).arrange(RIGHT, buff=0.10),
            VGroup(
                Dot(radius=0.09, color=PLAYER_B_COLOR),
                Text("Player B", font_size=18, color=PLAYER_B_COLOR),
            ).arrange(RIGHT, buff=0.10),
            VGroup(
                Circle(radius=0.09, fill_color=GHOST_COLOR,
                       fill_opacity=0.85, stroke_width=0),
                Text("Ghost (AI)", font_size=18, color=GHOST_COLOR),
            ).arrange(RIGHT, buff=0.10),
        ).arrange(RIGHT, buff=0.7)
        ent_legend.next_to(grid_group, DOWN, buff=0.35)

        caption = Text(
            "Players navigate the map — ghosts hunt using A* pathfinding",
            font_size=20, color=TEXT_MUTED,
        )
        caption.next_to(ent_legend, DOWN, buff=0.18)

        # Clamp to screen bottom if needed
        if caption.get_bottom()[1] < -3.8:
            VGroup(ent_legend, caption).to_edge(DOWN, buff=0.12)

        self.play(FadeIn(ent_legend), FadeIn(caption, shift=UP * 0.15),
                  run_time=0.6)
        self.wait(2.5)

        self.play(FadeOut(VGroup(
            section, grid_group,
            player_a, player_b, lbl_a, lbl_b,
            ghosts, ghost_lbl,
            ent_legend, caption,
        )), run_time=0.8)


class DDAScene(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND

        section = Text("2. Casting Rays — DDA Algorithm", font_size=42,
                       color=PYNQ_RED, weight=BOLD)
        section.to_edge(UP, buff=0.35)
        self.play(Write(section), run_time=0.8)

        # ── Shared grid setup ─────────────────────────────────────────────
        world_map = ALGO_WORLD_MAP
        map_rows  = len(world_map)
        map_cols  = len(world_map[0])
        cell_size = 0.55

        # ══════════════════════════════════════════════════════════════════
        # PART A — The problem: fixed-step ray marching can miss walls
        # ══════════════════════════════════════════════════════════════════
        part_a_lbl = Text("Problem: fixed-step ray marching", font_size=28,
                          color=TEXT_PRIMARY, weight=BOLD)
        part_a_lbl.next_to(section, DOWN, buff=0.30)
        self.play(FadeIn(part_a_lbl, shift=UP * 0.15), run_time=0.5)

        grid_a = make_world_grid(world_map, cell_size=cell_size,
                                 empty_opacity=0.42)
        grid_a.move_to(ORIGIN + DOWN * 0.5)
        self.play(FadeIn(grid_a, lag_ratio=0.005), run_time=0.6)

        player_pos = grid_cell_center(grid_a, 5, 2, map_cols)
        player_dot = Dot(player_pos, radius=0.11, color=PLAYER_A_COLOR,
                         z_index=5)
        self.play(FadeIn(player_dot, scale=0.5), run_time=0.4)

        # Pick a ray angle that threads through a narrow gap between two
        # wall cells — aiming between (2,2)/(2,3) wall block and (3,5) wall
        # so that with large step size the samples skip right over the wall.
        ray_angle_deg = 38
        ray_angle_rad = np.radians(ray_angle_deg)
        ray_dir = np.array([np.cos(ray_angle_rad),
                            np.sin(ray_angle_rad), 0])

        # Compute the actual hit point (fine stepping)
        true_hit = None
        for s in range(1, 400):
            pos = player_pos + ray_dir * 0.02 * s
            r, c = point_to_grid_cell(pos, grid_a, map_rows, map_cols,
                                      cell_size)
            if 0 <= r < map_rows and 0 <= c < map_cols:
                if world_map[r][c] == 1:
                    true_hit = pos
                    break
            else:
                break

        # Draw the full ray line (faint) to show where it goes
        ray_end = player_pos + ray_dir * 4.5
        ray_line_faint = Line(player_pos, ray_end, stroke_color=RAY_COLOR,
                              stroke_width=1.5, stroke_opacity=0.3)
        self.play(Create(ray_line_faint), run_time=0.4)

        # ── Fixed-step samples with LARGE step — some miss the wall ───────
        large_step = 0.38
        sample_dots = VGroup()
        missed_wall = False
        wall_passed = False
        for i in range(1, 14):
            pos = player_pos + ray_dir * large_step * i
            r, c = point_to_grid_cell(pos, grid_a, map_rows, map_cols,
                                      cell_size)
            in_wall = (0 <= r < map_rows and 0 <= c < map_cols
                       and world_map[r][c] == 1)
            # Check if any fine-step between previous and this would be wall
            if not in_wall and not wall_passed:
                for sub in range(1, 20):
                    subpos = player_pos + ray_dir * (large_step * (i - 1)
                             + large_step * sub / 20)
                    sr, sc = point_to_grid_cell(subpos, grid_a, map_rows,
                                                map_cols, cell_size)
                    if (0 <= sr < map_rows and 0 <= sc < map_cols
                            and world_map[sr][sc] == 1):
                        wall_passed = True
                        missed_wall = True
                        break

            dot = Dot(pos, radius=0.07,
                      color=ACCENT_ALERT if in_wall else RAY_COLOR,
                      z_index=6)
            sample_dots.add(dot)

        self.play(LaggedStart(
            *[FadeIn(d, scale=0.5) for d in sample_dots],
            lag_ratio=0.08,
        ), run_time=1.2)

        # "MISSED" label
        miss_lbl = Text("MISSED!", font_size=32, color=ACCENT_ALERT,
                         weight=BOLD)
        miss_lbl.next_to(grid_a, RIGHT, buff=0.5).shift(UP * 0.3)
        miss_desc = Text("Step size too large — ray\npassed through the wall",
                         font_size=18, color=TEXT_MUTED, line_spacing=0.9)
        miss_desc.next_to(miss_lbl, DOWN, buff=0.15)

        self.play(FadeIn(miss_lbl, scale=1.3), FadeIn(miss_desc),
                  run_time=0.6)
        self.wait(1.8)

        # Clean up Part A
        part_a_all = VGroup(part_a_lbl, grid_a, player_dot,
                            ray_line_faint, sample_dots,
                            miss_lbl, miss_desc)
        self.play(FadeOut(part_a_all), run_time=0.6)

        # ══════════════════════════════════════════════════════════════════
        # PART B — The solution: DDA steps at grid boundaries
        # ══════════════════════════════════════════════════════════════════
        part_b_lbl = Text("Solution: DDA — step at every grid boundary",
                          font_size=28, color=TEXT_PRIMARY, weight=BOLD)
        part_b_lbl.next_to(section, DOWN, buff=0.30)
        self.play(FadeIn(part_b_lbl, shift=UP * 0.15), run_time=0.5)

        grid_b = make_world_grid(world_map, cell_size=cell_size,
                                 empty_opacity=0.42)
        grid_b.move_to(LEFT * 2.2 + DOWN * 0.5)
        self.play(FadeIn(grid_b, lag_ratio=0.005), run_time=0.6)

        player_pos_b = grid_cell_center(grid_b, 5, 2, map_cols)
        player_dot_b = Dot(player_pos_b, radius=0.11,
                           color=PLAYER_A_COLOR, z_index=5)
        self.play(FadeIn(player_dot_b, scale=0.5), run_time=0.4)

        # ── DDA stepping: find each grid boundary crossing ────────────────
        # We simulate DDA: from the player cell, step through x-side and
        # y-side crossings until we hit a wall.
        px, py = player_pos_b[0], player_pos_b[1]
        grid_center = grid_b.get_center()
        # Convert scene coords to grid float coords
        gx = (px - grid_center[0]) / cell_size + map_cols / 2
        gy = -(py - grid_center[1]) / cell_size + map_rows / 2

        dx = ray_dir[0]
        dy = -ray_dir[1]  # flip because grid y is inverted

        map_x, map_y = int(gx), int(gy)
        delta_dist_x = abs(1 / dx) if dx != 0 else 1e10
        delta_dist_y = abs(1 / dy) if dy != 0 else 1e10

        if dx < 0:
            step_x = -1
            side_dist_x = (gx - map_x) * delta_dist_x
        else:
            step_x = 1
            side_dist_x = (map_x + 1.0 - gx) * delta_dist_x
        if dy < 0:
            step_y = -1
            side_dist_y = (gy - map_y) * delta_dist_y
        else:
            step_y = 1
            side_dist_y = (map_y + 1.0 - gy) * delta_dist_y

        # Collect DDA step positions (scene coords of each boundary hit)
        dda_points = [player_pos_b.copy()]
        dda_hit = None
        for _ in range(60):
            if side_dist_x < side_dist_y:
                t = side_dist_x
                side_dist_x += delta_dist_x
                map_x += step_x
            else:
                t = side_dist_y
                side_dist_y += delta_dist_y
                map_y += step_y

            # Convert back to scene coords
            scene_x = grid_center[0] + (gx + dx * t - map_cols / 2) * cell_size
            scene_y = grid_center[1] - (gy + dy * t - map_rows / 2) * cell_size
            pt = np.array([scene_x, scene_y, 0])
            dda_points.append(pt)

            if 0 <= map_y < map_rows and 0 <= map_x < map_cols:
                if world_map[map_y][map_x] == 1:
                    dda_hit = pt
                    break
            else:
                break

        # ── Draw DDA steps one at a time ──────────────────────────────────
        dda_lines = VGroup()
        dda_dots = VGroup()
        for i in range(1, len(dda_points)):
            seg = Line(dda_points[i - 1], dda_points[i],
                       stroke_color=RAY_COLOR, stroke_width=2.5,
                       z_index=4)
            dot = Dot(dda_points[i], radius=0.06, color=HIT_COLOR,
                      z_index=6)
            dda_lines.add(seg)
            dda_dots.add(dot)
            self.play(Create(seg), FadeIn(dot, scale=0.5),
                      run_time=0.12)

        # Highlight final hit
        if dda_hit is not None:
            hit_flash = Dot(dda_hit, radius=0.12, color=HIT_COLOR,
                            z_index=8)
            hit_lbl = Text("HIT", font_size=28, color=HIT_COLOR,
                           weight=BOLD)
            hit_lbl.next_to(hit_flash, UP + RIGHT, buff=0.12)
            self.play(FadeIn(hit_flash, scale=1.5), FadeIn(hit_lbl),
                      run_time=0.4)
        self.wait(0.8)

        # ── Right-side explanation ────────────────────────────────────────
        dda_explain = VGroup(
            Text("DDA steps per ray:", font_size=24,
                 color=TEXT_PRIMARY, weight=BOLD),
            Text("1. Compute distance to next", font_size=20,
                 color=TEXT_MUTED),
            Text("   x-side and y-side", font_size=20, color=TEXT_MUTED),
            Text("2. Advance to the closer one", font_size=20,
                 color=TEXT_MUTED),
            Text("3. Check: is this cell a wall?", font_size=20,
                 color=TEXT_MUTED),
            Text("4. If not, repeat from step 1", font_size=20,
                 color=TEXT_MUTED),
            Text("5. If yes, record the hit", font_size=20,
                 color=HIT_COLOR),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        dda_explain.to_edge(RIGHT, buff=0.4).shift(DOWN * 0.3)
        self.play(FadeIn(dda_explain, lag_ratio=0.06), run_time=1.2)
        self.wait(1.5)

        # ── FPGA callout — why DDA is perfect for hardware ────────────────
        fpga_box_bg = RoundedRectangle(
            corner_radius=0.12, width=12.0, height=1.6,
            fill_color=PANEL_FILL, fill_opacity=0.96,
            stroke_color=ACCENT_HARDWARE, stroke_width=1.8,
        ).to_edge(DOWN, buff=0.10)
        fpga_txt = VGroup(
            Text("Why DDA maps perfectly to FPGA:", font_size=20,
                 color=ACCENT_HARDWARE, weight=BOLD),
            Text("Custom fixed-point precision minimises utilisation and latency.",
                 font_size=16, color=TEXT_MUTED),
            Text("Each ray is independent — trivially parallelisable.",
                 font_size=16, color=TEXT_MUTED),
        ).arrange(DOWN, buff=0.08, aligned_edge=LEFT)
        fpga_txt.move_to(fpga_box_bg)
        self.play(FadeIn(VGroup(fpga_box_bg, fpga_txt)), run_time=0.5)
        self.wait(2.5)

        # ── Fade out ──────────────────────────────────────────────────────
        fade_grp = VGroup(
            section, part_b_lbl,
            grid_b, player_dot_b,
            dda_lines, dda_dots,
            dda_explain, fpga_box_bg, fpga_txt,
        )
        if dda_hit is not None:
            fade_grp.add(hit_flash, hit_lbl)
        self.play(FadeOut(fade_grp), run_time=0.8)


class WallRenderScene(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND

        section = Text("3. Distance  →  Wall Height", font_size=40,
                       color=PYNQ_RED, weight=BOLD)
        section.to_edge(UP, buff=0.35)
        self.play(Write(section), run_time=0.8)

        # Shared callout helper
        def make_callout(lines, accent):
            txt_group = VGroup(*[
                Text(t, font_size=fs, color=accent, weight=w)
                for t, fs, w in lines
            ]).arrange(DOWN, buff=0.08, aligned_edge=LEFT)
            bg = RoundedRectangle(
                corner_radius=0.12,
                width=txt_group.width + 0.4,
                height=txt_group.height + 0.3,
                fill_color=PANEL_FILL, fill_opacity=0.96,
                stroke_color=accent, stroke_width=1.8,
            )
            txt_group.move_to(bg.get_center())
            return VGroup(bg, txt_group)

        # ==================================================================
        # SCENE 1 — Fisheye problem: Euclidean distances differ
        # Left: top-down view   Right: distorted screen output
        # ==================================================================

        intro = Text("DDA found the wall. Now: how tall should it appear?",
                     font_size=28, color=TEXT_MUTED)
        intro.move_to(ORIGIN)
        self.play(FadeIn(intro, shift=UP * 0.15), run_time=0.6)
        self.wait(1.2)
        self.play(FadeOut(intro), run_time=0.4)

        # ── Split layout ──────────────────────────────────────────────────
        div1 = DashedLine([0.3, -3.5, 0], [0.3, 2.3, 0],
                          stroke_color="#1A3050", stroke_width=1.5,
                          dash_length=0.15)
        lhdr1 = Text("Top-Down View", font_size=19,
                      color=TEXT_MUTED).move_to([-3.2, 2.5, 0])
        rhdr1 = Text("Screen Output (Euclidean)", font_size=19,
                      color=ACCENT_ALERT).move_to([4.0, 2.5, 0])
        self.play(Create(div1), FadeIn(lhdr1), FadeIn(rhdr1), run_time=0.4)

        # ── Left side: player looking straight at a wall ──────────────────
        wall_y1 = 1.8
        wall_line1 = Line([-6.5, wall_y1, 0], [0.0, wall_y1, 0],
                          stroke_color=TEXT_PRIMARY, stroke_width=5)
        wall_fill1 = Rectangle(width=6.5, height=0.5,
                               fill_color=WALL_COLOR, fill_opacity=0.6,
                               stroke_width=0)
        wall_fill1.next_to(wall_line1, UP, buff=0)
        wall_fill1.align_to(wall_line1, LEFT)

        P1 = np.array([-3.2, -2.2, 0])
        player1 = Dot(P1, radius=0.14, color=PLAYER_A_COLOR, z_index=10)

        self.play(FadeIn(wall_line1), FadeIn(wall_fill1),
                  FadeIn(player1), run_time=0.5)

        # ── Cast 5 green rays fanning out to the wall ─────────────────────
        num_rays = 5
        ray_spread = np.linspace(-2.5, 1.5, num_rays)
        ray_hits = []
        ray_lines1 = VGroup()
        hit_dots1 = VGroup()
        euc_labels = VGroup()

        for i, x_off in enumerate(ray_spread):
            hit = np.array([P1[0] + x_off, wall_y1, 0])
            ray_hits.append(hit)
            euc_dist = np.linalg.norm(hit - P1)

            rl = Arrow(P1, hit, buff=0, stroke_width=2.5,
                       color=LODEV_GREEN,
                       max_tip_length_to_length_ratio=0.08)
            hd = Dot(hit, radius=0.06, color=HIT_COLOR, z_index=6)
            ray_lines1.add(rl)
            hit_dots1.add(hd)

            # Distance label at midpoint
            mid = (P1 + hit) / 2
            ray_vec = hit - P1
            ray_u = ray_vec / (np.linalg.norm(ray_vec) + 1e-12)
            perp = np.array([-ray_u[1], ray_u[0], 0])
            dlbl = Text(f"{euc_dist:.1f}", font_size=14, color=LODEV_GREEN)
            side = 1 if i < num_rays // 2 else -1
            dlbl.move_to(mid + perp * 0.25 * side)
            euc_labels.add(dlbl)

        for rl, hd in zip(ray_lines1, hit_dots1):
            self.play(GrowArrow(rl), FadeIn(hd, scale=0.5), run_time=0.18)
        self.play(FadeIn(euc_labels, lag_ratio=0.1), run_time=0.5)
        self.wait(0.5)

        # ── Right side: screen columns using Euclidean (fisheye) ──────────
        scr_w1, scr_h1 = 3.8, 3.5
        scr_cx1, scr_cy1 = 4.0, -0.5
        screen_bg1 = Rectangle(width=scr_w1, height=scr_h1,
                               fill_color="#060D16", fill_opacity=1.0,
                               stroke_color="#1A3050", stroke_width=1.5,
                               ).move_to([scr_cx1, scr_cy1, 0])
        self.play(FadeIn(screen_bg1), run_time=0.3)

        col_w1 = scr_w1 / num_rays
        euc_cols = VGroup()
        perp_dist_1 = abs(wall_y1 - P1[1])
        for i, hit in enumerate(ray_hits):
            euc_d = np.linalg.norm(hit - P1)
            line_h = min(scr_h1 - 0.05, scr_h1 * perp_dist_1 / euc_d)
            ceil_h = max(0.0, (scr_h1 - line_h) / 2)
            col_x = scr_cx1 - scr_w1 / 2 + (i + 0.5) * col_w1
            shade = interpolate_color(ManimColor(WALL_COLOR_DARK), ManimColor(WALL_COLOR), 0.5)
            wrect = Rectangle(width=col_w1 - 0.04, height=line_h,
                              fill_color=shade, fill_opacity=0.92,
                              stroke_width=0).move_to([col_x, scr_cy1, 0])
            crect = Rectangle(width=col_w1 - 0.04, height=ceil_h,
                              fill_color="#0C1830", fill_opacity=1.0,
                              stroke_width=0).next_to(wrect, UP, buff=0)
            frect = Rectangle(width=col_w1 - 0.04, height=ceil_h,
                              fill_color="#1A1A1A", fill_opacity=1.0,
                              stroke_width=0).next_to(wrect, DOWN, buff=0)
            euc_cols.add(VGroup(crect, wrect, frect))
        self.play(FadeIn(euc_cols, lag_ratio=0.08), run_time=0.6)

        fisheye_lbl = Text("Walls appear curved!", font_size=20,
                           color=ACCENT_ALERT, weight=BOLD)
        fisheye_lbl.next_to(screen_bg1, DOWN, buff=0.20)
        self.play(FadeIn(fisheye_lbl), run_time=0.4)
        self.wait(2.0)

        scene1_all = VGroup(
            div1, lhdr1, rhdr1,
            wall_line1, wall_fill1, player1,
            ray_lines1, hit_dots1, euc_labels,
            screen_bg1, euc_cols, fisheye_lbl,
        )
        self.play(FadeOut(scene1_all), run_time=0.6)

        # ==================================================================
        # SCENE 2 — perpWallDist solution
        # Left: single ray with camera plane   Right: corrected output
        # ==================================================================

        scene2_hdr = Text("Solution: use perpendicular distance",
                          font_size=28, color=TEXT_PRIMARY, weight=BOLD)
        scene2_hdr.move_to(ORIGIN)
        self.play(FadeIn(scene2_hdr, shift=UP * 0.15), run_time=0.6)
        self.wait(1.2)
        self.play(FadeOut(scene2_hdr), run_time=0.4)

        div2 = DashedLine([0.3, -3.5, 0], [0.3, 2.3, 0],
                          stroke_color="#1A3050", stroke_width=1.5,
                          dash_length=0.15)
        lhdr2 = Text("Top-Down View", font_size=19,
                      color=TEXT_MUTED).move_to([-3.2, 2.5, 0])
        rhdr2 = Text("Screen Output (perpWallDist)", font_size=19,
                      color=HIT_COLOR).move_to([4.0, 2.5, 0])
        self.play(Create(div2), FadeIn(lhdr2), FadeIn(rhdr2), run_time=0.4)

        # ── Left: simplified diagram ──────────────────────────────────────
        wall_y2 = 1.8
        wall_line2 = Line([-6.5, wall_y2, 0], [0.0, wall_y2, 0],
                          stroke_color=TEXT_PRIMARY, stroke_width=5)
        wall_fill2 = Rectangle(width=6.5, height=0.5,
                               fill_color=WALL_COLOR, fill_opacity=0.6,
                               stroke_width=0)
        wall_fill2.next_to(wall_line2, UP, buff=0)
        wall_fill2.align_to(wall_line2, LEFT)

        P2 = np.array([-3.2, -2.2, 0])
        player2 = Dot(P2, radius=0.14, color=PLAYER_A_COLOR, z_index=10)

        # Camera plane — horizontal through player
        cam_plane2 = Line([P2[0] - 2.8, P2[1], 0],
                          [P2[0] + 2.8, P2[1], 0],
                          stroke_color=ACCENT_HARDWARE, stroke_width=3,
                          stroke_opacity=0.7)
        cam_lbl2 = backed_label("camera plane", font_size=14,
                                color=ACCENT_HARDWARE, slant=ITALIC)
        cam_lbl2.next_to(cam_plane2, DOWN + RIGHT, buff=0.08)

        self.play(FadeIn(wall_line2), FadeIn(wall_fill2),
                  FadeIn(player2), Create(cam_plane2), FadeIn(cam_lbl2),
                  run_time=0.5)

        # Single angled ray
        hit2 = np.array([-1.5, wall_y2, 0])
        ray2 = Arrow(P2, hit2, buff=0, stroke_width=3,
                     color=LODEV_GREEN,
                     max_tip_length_to_length_ratio=0.08)
        hit_dot2 = Dot(hit2, radius=0.08, color=HIT_COLOR, z_index=8)
        self.play(GrowArrow(ray2), FadeIn(hit_dot2), run_time=0.5)

        # Euclidean (dotted red)
        euc_line2 = DashedLine(P2, hit2, stroke_color=ACCENT_ALERT,
                               stroke_width=2, dash_length=0.10,
                               stroke_opacity=0.6, z_index=3)
        euc_d2 = np.linalg.norm(hit2 - P2)
        euc_lbl2 = backed_label(f"Euclidean = {euc_d2:.1f}", font_size=14,
                                color=ACCENT_ALERT, slant=ITALIC)
        ray_u2 = (hit2 - P2) / euc_d2
        perp_u2 = np.array([-ray_u2[1], ray_u2[0], 0])
        euc_lbl2.move_to((P2 + hit2) / 2 + perp_u2 * 0.35)
        self.play(Create(euc_line2), FadeIn(euc_lbl2), run_time=0.5)

        # perpWallDist — vertical from hit down to camera plane
        perp_foot = np.array([hit2[0], P2[1], 0])
        perp_line2 = Line(hit2, perp_foot, stroke_color=HIT_COLOR,
                          stroke_width=4.5, z_index=6)
        perp_d2 = abs(wall_y2 - P2[1])
        perp_lbl2 = backed_label(f"perpWallDist = {perp_d2:.1f}",
                                 font_size=14, color=HIT_COLOR, weight=BOLD)
        perp_lbl2.next_to(perp_line2, RIGHT, buff=0.12)

        ra2 = right_angle_mark(perp_foot, [-1, 0, 0], [0, 1, 0],
                               size=0.12, color=HIT_COLOR)
        self.play(Create(perp_line2), FadeIn(perp_lbl2), Create(ra2),
                  run_time=0.6)
        self.wait(0.5)

        # Show perpWallDist is the same for ALL rays
        other_hits = [np.array([P2[0] - 2.0, wall_y2, 0]),
                      np.array([P2[0] + 0.5, wall_y2, 0])]
        other_perps = VGroup()
        for oh in other_hits:
            foot = np.array([oh[0], P2[1], 0])
            pl = Line(oh, foot, stroke_color=HIT_COLOR, stroke_width=2,
                      stroke_opacity=0.5, z_index=4)
            other_perps.add(pl)

        same_lbl = backed_label("same distance for every ray!",
                                font_size=15, color=HIT_COLOR, weight=BOLD)
        same_lbl.move_to([-3.2, 0.0, 0])
        self.play(FadeIn(other_perps, lag_ratio=0.15), FadeIn(same_lbl),
                  run_time=0.6)
        self.wait(0.8)

        # ── Right: corrected screen (flat wall) ───────────────────────────
        scr_w2, scr_h2 = 3.8, 3.5
        scr_cx2, scr_cy2 = 4.0, -0.5
        screen_bg2 = Rectangle(width=scr_w2, height=scr_h2,
                               fill_color="#060D16", fill_opacity=1.0,
                               stroke_color="#1A3050", stroke_width=1.5,
                               ).move_to([scr_cx2, scr_cy2, 0])
        self.play(FadeIn(screen_bg2), run_time=0.3)

        col_w2 = scr_w2 / num_rays
        perp_cols = VGroup()
        for i in range(num_rays):
            line_h = scr_h2 * 0.75
            ceil_h = max(0.0, (scr_h2 - line_h) / 2)
            col_x = scr_cx2 - scr_w2 / 2 + (i + 0.5) * col_w2
            shade = interpolate_color(ManimColor(WALL_COLOR_DARK), ManimColor(WALL_COLOR), 0.5)
            wrect = Rectangle(width=col_w2 - 0.04, height=line_h,
                              fill_color=shade, fill_opacity=0.92,
                              stroke_width=0).move_to([col_x, scr_cy2, 0])
            crect = Rectangle(width=col_w2 - 0.04, height=ceil_h,
                              fill_color="#0C1830", fill_opacity=1.0,
                              stroke_width=0).next_to(wrect, UP, buff=0)
            frect = Rectangle(width=col_w2 - 0.04, height=ceil_h,
                              fill_color="#1A1A1A", fill_opacity=1.0,
                              stroke_width=0).next_to(wrect, DOWN, buff=0)
            perp_cols.add(VGroup(crect, wrect, frect))
        self.play(FadeIn(perp_cols, lag_ratio=0.08), run_time=0.6)

        flat_lbl = Text("Walls render flat — correct!", font_size=20,
                        color=HIT_COLOR, weight=BOLD)
        flat_lbl.next_to(screen_bg2, DOWN, buff=0.20)
        self.play(FadeIn(flat_lbl), run_time=0.4)

        # ── Formula callout ───────────────────────────────────────────────
        formula_txt = VGroup(
            Text("perpWallDist = sideDistX − deltaDistX",
                 font_size=18, color=TEXT_PRIMARY),
            Text("Reuses DDA values — zero extra cost",
                 font_size=16, color=TEXT_MUTED),
            Text("lineHeight = screenHeight / perpWallDist",
                 font_size=18, color=HIT_COLOR),
        ).arrange(DOWN, buff=0.06, aligned_edge=LEFT)
        formula_bg = RoundedRectangle(
            corner_radius=0.10,
            width=formula_txt.width + 0.4,
            height=formula_txt.height + 0.25,
            fill_color=PANEL_FILL, fill_opacity=0.96,
            stroke_color=ACCENT_SERVER, stroke_width=1.5,
        )
        formula_bg.to_edge(DOWN, buff=0.08)
        formula_txt.move_to(formula_bg)
        self.play(FadeIn(VGroup(formula_bg, formula_txt)), run_time=0.5)
        self.wait(3.0)

        scene2_all = VGroup(
            div2, lhdr2, rhdr2,
            wall_line2, wall_fill2, player2, cam_plane2, cam_lbl2,
            ray2, hit_dot2,
            euc_line2, euc_lbl2,
            perp_line2, perp_lbl2, ra2,
            other_perps, same_lbl,
            screen_bg2, perp_cols, flat_lbl,
            formula_bg, formula_txt,
        )
        self.play(FadeOut(scene2_all), run_time=0.6)

        # ==================================================================
        # SCENE 2.5 — How perpWallDist is computed from DDA values
        # Shows sideDistX, sideDistY, deltaDistX, deltaDistY on a grid
        # ==================================================================

        s25_hdr = Text("Computing perpWallDist from DDA",
                       font_size=28, color=TEXT_PRIMARY, weight=BOLD)
        s25_hdr.move_to(ORIGIN)
        self.play(FadeIn(s25_hdr, shift=UP * 0.15), run_time=0.6)
        self.wait(1.2)
        self.play(FadeOut(s25_hdr), run_time=0.4)

        # ── Grid background (few large cells for clarity) ─────────────────
        s25_rows, s25_cols = 5, 5
        s25_cs = 1.15
        s25_ox = -s25_cols * s25_cs / 2
        s25_oy = 2.4

        def s25_g2s(r, c):
            return np.array([s25_ox + (c + 0.5) * s25_cs,
                             s25_oy - (r + 0.5) * s25_cs, 0])

        # Wall in top-right corner (2x2 block)
        s25_wall = [[0]*s25_cols for _ in range(s25_rows)]
        for r in range(2):
            for c in range(3, s25_cols):
                s25_wall[r][c] = 1

        s25_grid = VGroup()
        for r in range(s25_rows):
            for c in range(s25_cols):
                sq = Square(side_length=s25_cs, stroke_width=1.0,
                            stroke_color=LODEV_GRID, stroke_opacity=0.40)
                if s25_wall[r][c]:
                    sq.set_fill(WALL_COLOR, opacity=0.85)
                else:
                    sq.set_fill(EMPTY_COLOR, opacity=0.08)
                sq.move_to(s25_g2s(r, c))
                s25_grid.add(sq)
        self.play(FadeIn(s25_grid, lag_ratio=0.003), run_time=0.5)

        # ── Player and ray ────────────────────────────────────────────────
        s25_P = s25_g2s(4, 0) + np.array([0.25, 0.25, 0])
        s25_player = Dot(s25_P, radius=0.13, color=PLAYER_A_COLOR, z_index=10)
        self.play(FadeIn(s25_player), run_time=0.3)

        # Ray direction: up and to the right, hitting the wall
        s25_ray_angle = np.radians(58)
        s25_ray_dir = np.array([np.cos(s25_ray_angle),
                                np.sin(s25_ray_angle), 0])

        # Find wall hit
        s25_hit = None
        for s in range(1, 500):
            pos = s25_P + s25_ray_dir * 0.015 * s
            rel = pos - s25_grid.get_center()
            gc = int(np.floor(rel[0] / s25_cs + s25_cols / 2))
            gr = int(np.floor(-rel[1] / s25_cs + s25_rows / 2))
            if 0 <= gr < s25_rows and 0 <= gc < s25_cols:
                if s25_wall[gr][gc] == 1:
                    s25_hit = pos
                    break

        if s25_hit is None:
            s25_hit = s25_P + s25_ray_dir * 4.0

        # Draw ray
        s25_ray = Line(s25_P, s25_hit, stroke_color=LODEV_RED,
                       stroke_width=3, z_index=5)
        s25_hit_dot = Dot(s25_hit, radius=0.08, color=LODEV_RED, z_index=10)
        self.play(Create(s25_ray), FadeIn(s25_hit_dot), run_time=0.5)

        # ── Camera plane (green diagonal through P) ───────────────────────
        s25_plane_dir = np.array([s25_ray_dir[1], -s25_ray_dir[0], 0])
        s25_cp_start = s25_P - s25_plane_dir * 2.5
        s25_cp_end   = s25_P + s25_plane_dir * 2.5
        s25_cam = Line(s25_cp_start, s25_cp_end,
                       stroke_color=LODEV_GREEN, stroke_width=3,
                       stroke_opacity=0.7)
        s25_cam_lbl = backed_label("camera plane", font_size=13,
                                   color=LODEV_GREEN, slant=ITALIC)
        s25_cam_lbl.next_to(s25_cp_end, DOWN, buff=0.08)
        self.play(Create(s25_cam), FadeIn(s25_cam_lbl), run_time=0.4)

        # ── Compute the first grid crossings for sideDistX/Y ─────────────
        # Get grid-relative float position
        grid_cx = s25_grid.get_center()[0]
        grid_cy = s25_grid.get_center()[1]
        gx_f = (s25_P[0] - grid_cx) / s25_cs + s25_cols / 2
        gy_f = -(s25_P[1] - grid_cy) / s25_cs + s25_rows / 2

        rdx = s25_ray_dir[0]
        rdy = -s25_ray_dir[1]  # grid y is flipped

        # First x-boundary crossing (sideDistX direction)
        if rdx > 0:
            x_bound = (int(gx_f) + 1 - gx_f) * s25_cs
        else:
            x_bound = (gx_f - int(gx_f)) * s25_cs
        t_first_x = x_bound / (abs(rdx) * s25_cs + 1e-12)
        sdx_end = s25_P + s25_ray_dir * t_first_x * s25_cs

        # First y-boundary crossing (sideDistY direction)
        if rdy > 0:
            y_bound = (int(gy_f) + 1 - gy_f) * s25_cs
        else:
            y_bound = (gy_f - int(gy_f)) * s25_cs
        t_first_y = y_bound / (abs(rdy) * s25_cs + 1e-12)
        sdy_end = s25_P + s25_ray_dir * t_first_y * s25_cs

        # deltaDistX: distance along ray to cross one full x-cell
        ddx_len = s25_cs / (abs(rdx) + 1e-12)
        ddx_start = sdx_end
        ddx_end = sdx_end + s25_ray_dir * (ddx_len / np.linalg.norm(s25_ray_dir))

        # deltaDistY: distance along ray to cross one full y-cell
        ddy_len = s25_cs / (abs(rdy) + 1e-12)
        ddy_start = sdy_end
        ddy_end = sdy_end + s25_ray_dir * (ddy_len / np.linalg.norm(s25_ray_dir))

        # ── Draw sideDistY (green, from P along ray) ─────────────────────
        sdy_line = Line(s25_P, sdy_end, stroke_color=LODEV_GREEN,
                        stroke_width=4, z_index=7)
        sdy_lbl = backed_label("sideDistY", font_size=16,
                               color=LODEV_GREEN, weight=BOLD)
        sdy_perp = np.array([-s25_ray_dir[1], s25_ray_dir[0], 0])
        sdy_lbl.move_to((s25_P + sdy_end) / 2 + sdy_perp * 0.35)
        sdy_dot = Dot(sdy_end, radius=0.06, color=LODEV_GREEN, z_index=8)
        self.play(Create(sdy_line), FadeIn(sdy_lbl), FadeIn(sdy_dot),
                  run_time=0.5)

        # ── Draw sideDistX (blue, from P along ray) ──────────────────────
        sdx_line = Line(s25_P, sdx_end, stroke_color=LODEV_BLUE,
                        stroke_width=4, z_index=7)
        sdx_lbl = backed_label("sideDistX", font_size=16,
                               color=LODEV_BLUE, weight=BOLD)
        sdx_lbl.move_to((s25_P + sdx_end) / 2 - sdy_perp * 0.35)
        sdx_dot = Dot(sdx_end, radius=0.06, color=LODEV_BLUE, z_index=8)
        self.play(Create(sdx_line), FadeIn(sdx_lbl), FadeIn(sdx_dot),
                  run_time=0.5)
        self.wait(0.5)

        # ── Draw deltaDistY (green, continuing from sideDistY end) ────────
        ddy_line = Line(ddy_start, ddy_end, stroke_color=LODEV_GREEN,
                        stroke_width=3, stroke_opacity=0.7, z_index=7)
        ddy_lbl = backed_label("deltaDistY", font_size=14,
                               color=LODEV_GREEN, weight=BOLD)
        ddy_lbl.move_to((ddy_start + ddy_end) / 2 + sdy_perp * 0.32)
        self.play(Create(ddy_line), FadeIn(ddy_lbl), run_time=0.4)

        # ── Draw deltaDistX (blue, continuing from sideDistX end) ─────────
        ddx_line = Line(ddx_start, ddx_end, stroke_color=LODEV_BLUE,
                        stroke_width=3, stroke_opacity=0.7, z_index=7)
        ddx_lbl = backed_label("deltaDistX", font_size=14,
                               color=LODEV_BLUE, weight=BOLD)
        ddx_lbl.move_to((ddx_start + ddx_end) / 2 - sdy_perp * 0.32)
        self.play(Create(ddx_line), FadeIn(ddx_lbl), run_time=0.4)
        self.wait(0.8)

        # ── perpWallDist line (magenta, from cam plane to hit) ────────────
        # Project hit onto the dir vector from P
        perp_d_val = np.dot(s25_hit - s25_P, s25_ray_dir / np.linalg.norm(s25_ray_dir))
        # Visually: line from the camera plane at the hit's projection back to hit
        proj_on_cam = s25_P + np.dot(s25_hit - s25_P, s25_plane_dir) * s25_plane_dir / (np.linalg.norm(s25_plane_dir)**2 + 1e-12)
        # Actually perpWallDist is parallel to dir, so draw from A (on cam plane) to H
        A_pt = s25_hit - s25_ray_dir * (np.dot(s25_hit - s25_P, s25_plane_dir)**2)**0  # simplify: A is projection of H onto cam plane
        # Better: A = P + component of (H-P) along plane_dir * plane_dir_unit
        s25_pvu = s25_plane_dir / (np.linalg.norm(s25_plane_dir) + 1e-12)
        s25_A = s25_P + np.dot(s25_hit - s25_P, s25_pvu) * s25_pvu
        perp_vis = Line(s25_A, s25_hit, stroke_color="#CC44FF",
                        stroke_width=5, z_index=8)
        perp_vis_lbl = backed_label("perpWallDist", font_size=17,
                                    color="#CC44FF", weight=BOLD)
        AH_d = s25_hit - s25_A
        AH_u_v = AH_d / (np.linalg.norm(AH_d) + 1e-12)
        AH_p = np.array([-AH_u_v[1], AH_u_v[0], 0])
        perp_vis_lbl.move_to((s25_A + s25_hit) / 2 + AH_p * 0.40)
        self.play(Create(perp_vis), FadeIn(perp_vis_lbl), run_time=0.6)
        self.wait(0.5)

        # ── Formula callout at bottom ─────────────────────────────────────
        s25_formula = VGroup(
            Text("For an x-side hit:", font_size=18,
                 color=TEXT_PRIMARY, weight=BOLD),
            Text("perpWallDist = sideDistX − deltaDistX",
                 font_size=20, color=LODEV_BLUE),
            Text("For a y-side hit:", font_size=18,
                 color=TEXT_PRIMARY, weight=BOLD),
            Text("perpWallDist = sideDistY − deltaDistY",
                 font_size=20, color=LODEV_GREEN),
            Text("These values are already computed during DDA stepping",
                 font_size=16, color=TEXT_MUTED),
        ).arrange(DOWN, buff=0.10, aligned_edge=LEFT)
        s25_formula_bg = RoundedRectangle(
            corner_radius=0.10,
            width=s25_formula.width + 0.5,
            height=s25_formula.height + 0.3,
            fill_color=PANEL_FILL, fill_opacity=0.96,
            stroke_color=ACCENT_SERVER, stroke_width=1.5,
        )
        s25_formula_bg.to_edge(DOWN, buff=0.08)
        s25_formula.move_to(s25_formula_bg)
        self.play(FadeIn(VGroup(s25_formula_bg, s25_formula)), run_time=0.5)
        self.wait(3.5)

        # ── Clean up ──────────────────────────────────────────────────────
        s25_all = VGroup(
            s25_grid, s25_player, s25_ray, s25_hit_dot,
            s25_cam, s25_cam_lbl,
            sdy_line, sdy_lbl, sdy_dot,
            sdx_line, sdx_lbl, sdx_dot,
            ddy_line, ddy_lbl, ddx_line, ddx_lbl,
            perp_vis, perp_vis_lbl,
            s25_formula_bg, s25_formula,
        )
        self.play(FadeOut(s25_all), run_time=0.6)

        # ==================================================================
        # SCENE 3 — Multi-ray + screen columns (existing Phase 2)
        # ==================================================================
        grid_rows, grid_cols = 8, 9
        cs = 0.62
        dir_angle = np.radians(68)
        dir_vec = np.array([np.cos(dir_angle), np.sin(dir_angle), 0])
        plane_vec = np.array([dir_vec[1], -dir_vec[0], 0]) * 0.66

        divider = DashedLine([0.5, -3.8, 0], [0.5, 3.2, 0],
                             stroke_color="#1A3050", stroke_width=1.5,
                             dash_length=0.15)
        lhdr = Text("Top-Down View", font_size=21,
                     color=TEXT_MUTED).move_to([-3.0, 2.85, 0])
        rhdr = Text("Screen Output", font_size=21,
                     color=TEXT_MUTED).move_to([4.2, 2.85, 0])
        self.play(Create(divider), FadeIn(lhdr), FadeIn(rhdr), run_time=0.5)

        grid_ox_p2 = -6.6
        grid_oy_p2 = 2.45

        def g2s_p2(r, c):
            return np.array([grid_ox_p2 + (c + 0.5) * cs,
                             grid_oy_p2 - (r + 0.5) * cs, 0])

        P_p2 = g2s_p2(6, 1) + np.array([0.05, 0.1, 0])
        wall_y_p2 = grid_oy_p2 - cs

        wall_map_p2 = [[0]*grid_cols for _ in range(grid_rows)]
        for c in [2, 3, 4, 5, 6, 7]:
            wall_map_p2[0][c] = 1

        simp_grid = VGroup()
        for r in range(grid_rows):
            for c in range(grid_cols):
                sq = Square(side_length=cs, stroke_width=0.7,
                            stroke_color=LODEV_GRID, stroke_opacity=0.12)
                if wall_map_p2[r][c]:
                    sq.set_fill(LODEV_WALL_BLUE, opacity=0.35)
                else:
                    sq.set_fill(EMPTY_COLOR, opacity=0.05)
                sq.move_to(g2s_p2(r, c))
                simp_grid.add(sq)

        simp_player = Dot(P_p2, radius=0.12, color=PLAYER_A_COLOR, z_index=6)
        sp_lbl = Text("P", font_size=20, color=PLAYER_A_COLOR, weight=BOLD)
        sp_lbl.next_to(simp_player, DOWN + LEFT, buff=0.06)

        wl_left  = np.array([grid_ox_p2, wall_y_p2, 0])
        wl_right = np.array([grid_ox_p2 + grid_cols * cs, wall_y_p2, 0])
        simp_wall = Line(wl_left, wl_right,
                         stroke_color=LODEV_WALL_BLUE, stroke_width=5)
        sw_lbl = Text("Wall", font_size=18, color=LODEV_WALL_BLUE)
        sw_lbl.next_to(simp_wall, UP, buff=0.08)

        self.play(FadeIn(simp_grid), FadeIn(simp_wall), FadeIn(sw_lbl),
                  FadeIn(simp_player), FadeIn(sp_lbl), run_time=0.5)

        num_cols = 5
        screen_w, screen_h = 3.2, 3.2
        screen_cx, screen_cy = 4.2, -0.1
        narrow_plane = plane_vec * 0.65

        ray_data = []
        grid_left_x  = grid_ox_p2
        grid_right_x = grid_ox_p2 + grid_cols * cs
        for i in range(num_cols):
            cx = 2 * i / (num_cols - 1) - 1
            rd = dir_vec + narrow_plane * cx
            rd3 = np.array([rd[0], rd[1], 0.0])
            t = (wall_y_p2 - P_p2[1]) / rd[1]
            hit = P_p2 + t * rd3
            if hit[0] < grid_left_x or hit[0] > grid_right_x:
                continue
            perp_d = np.dot(hit - P_p2, dir_vec)
            ray_data.append((cx, rd3, hit, perp_d))

        actual_cols = len(ray_data)
        act_col_w = screen_w / actual_cols

        ray_lines = VGroup()
        hit_dots_r = VGroup()
        for i, (cx, rd, hit, perp_d) in enumerate(ray_data):
            is_c = (i == actual_cols // 2)
            rl = Line(P_p2, hit,
                      color=PYNQ_RED if is_c else RAY_COLOR,
                      stroke_width=3.0 if is_c else 1.8,
                      stroke_opacity=1.0 if is_c else 0.55, z_index=4)
            hd = Dot(hit, radius=0.07, color=HIT_COLOR, z_index=5)
            ray_lines.add(rl)
            hit_dots_r.add(hd)
            self.play(Create(rl), FadeIn(hd, scale=0.5), run_time=0.22)

        screen_bg = Rectangle(
            width=screen_w, height=screen_h,
            fill_color="#060D16", fill_opacity=1.0,
            stroke_color="#1A3050", stroke_width=1.5,
        ).move_to([screen_cx, screen_cy, 0])
        self.play(FadeIn(screen_bg), run_time=0.3)

        col_groups = VGroup()
        height_annots = VGroup()
        for i, (cx, _, hit, perp_d) in enumerate(ray_data):
            line_h = min(screen_h - 0.05, screen_h / perp_d)
            ceil_h = max(0.0, (screen_h - line_h) / 2)
            col_x = screen_cx - screen_w / 2 + (i + 0.5) * act_col_w
            shade = interpolate_color(ManimColor(WALL_COLOR_DARK),
                                      ManimColor(WALL_COLOR),
                                      i / max(actual_cols - 1, 1))
            wall_rect = Rectangle(
                width=act_col_w - 0.05, height=line_h,
                fill_color=shade, fill_opacity=0.92, stroke_width=0,
            ).move_to([col_x, screen_cy, 0])
            ceil_rect = Rectangle(
                width=act_col_w - 0.05, height=ceil_h,
                fill_color="#0C1830", fill_opacity=1.0, stroke_width=0,
            ).next_to(wall_rect, UP, buff=0)
            floor_rect = Rectangle(
                width=act_col_w - 0.05, height=ceil_h,
                fill_color="#1A1A1A", fill_opacity=1.0, stroke_width=0,
            ).next_to(wall_rect, DOWN, buff=0)
            col_groups.add(VGroup(ceil_rect, wall_rect, floor_rect))
            self.play(FadeIn(col_groups[-1], scale=0.85), run_time=0.22)

            ann_y = min(screen_cy + screen_h / 2 - 0.18,
                        screen_cy + line_h / 2 + 0.2)
            ann = Text(f"{line_h:.1f}", font_size=15, color=HIT_COLOR)
            ann.move_to([col_x, ann_y, 0])
            height_annots.add(ann)
        self.play(FadeIn(height_annots, lag_ratio=0.1), run_time=0.4)

        mid_i = actual_cols // 2
        c_perp = ray_data[mid_i][3]
        c_lineh = min(screen_h - 0.05, screen_h / c_perp)
        cbot = np.array([screen_cx, screen_cy - c_lineh / 2, 0])
        ctop = np.array([screen_cx, screen_cy + c_lineh / 2, 0])
        brace = BraceBetweenPoints(cbot, ctop, direction=LEFT,
                                   color=HIT_COLOR)
        b_lbl = VGroup(
            Text("lineHeight =", font_size=17, color=HIT_COLOR),
            Text("H / perpDist", font_size=17, color=HIT_COLOR),
            Text(f"= {c_lineh:.2f}", font_size=17, color=HIT_COLOR),
        ).arrange(DOWN, buff=0.06, aligned_edge=LEFT)
        b_lbl.next_to(brace, LEFT, buff=0.1)
        self.play(Create(brace), FadeIn(b_lbl), run_time=0.6)
        self.wait(1.0)
        self.play(FadeOut(brace), FadeOut(b_lbl), run_time=0.4)
        self.wait(1.5)

        self.play(FadeOut(VGroup(
            section, divider, lhdr, rhdr,
            simp_grid, simp_wall, sw_lbl, simp_player, sp_lbl,
            ray_lines, hit_dots_r,
            screen_bg, col_groups, height_annots,
        )), run_time=0.9)


class FPGAParallelScene(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND

        section = Text("4. FPGA Hardware Acceleration", font_size=42,
                       color=PYNQ_RED, weight=BOLD)
        section.to_edge(UP, buff=0.4)
        self.play(Write(section), run_time=0.8)

        # ==================================================================
        # PART 1 — CPU sequential vs FPGA parallel column rendering
        # ==================================================================
        cpu_label  = Text("CPU  —  Sequential", font_size=26, weight=BOLD,
                          color="#5599FF")
        fpga_label = Text("FPGA  —  Parallel",  font_size=26, weight=BOLD,
                          color=PYNQ_RED)
        cpu_label.move_to(LEFT * 3.2 + UP * 1.9)
        fpga_label.move_to(RIGHT * 3.2 + UP * 1.9)
        self.play(FadeIn(cpu_label), FadeIn(fpga_label), run_time=0.5)

        num_cols = 16
        col_w    = 0.26
        cpu_cols = VGroup()
        fpga_cols = VGroup()

        for index in range(num_cols):
            def make_col(x_centre, idx=index):
                return Rectangle(
                    width=col_w, height=2.0,
                    fill_color=GREY_D, fill_opacity=0.3,
                    stroke_color="#2A4060", stroke_width=0.8,
                ).move_to(np.array([
                    x_centre + (idx - num_cols / 2 + 0.5) * col_w,
                    -0.3, 0
                ]))
            cpu_cols.add(make_col(-3.2))
            fpga_cols.add(make_col(3.2))

        self.play(FadeIn(cpu_cols), FadeIn(fpga_cols), run_time=0.5)

        # CPU fills one column at a time
        for index in range(num_cols):
            self.play(cpu_cols[index].animate.set_fill(
                color="#5599FF", opacity=0.85), run_time=0.1)

        # FPGA fills all at once
        self.play(
            *[fpga_cols[i].animate.set_fill(
                color=PYNQ_RED, opacity=0.85) for i in range(num_cols)],
            run_time=0.45,
        )

        # Brief note
        par_note = Text("Each ray is independent — all 720 columns "
                        "can be computed in parallel",
                        font_size=20, color=TEXT_MUTED)
        par_note.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(par_note, shift=UP * 0.15), run_time=0.5)
        self.wait(2.0)

        # Fade part 1
        self.play(FadeOut(VGroup(
            cpu_label, fpga_label, cpu_cols, fpga_cols, par_note,
        )), run_time=0.6)

        # ==================================================================
        # PART 2 — PYNQ-Z1 SoC Architecture block diagram
        # ==================================================================
        soc_hdr = Text("PYNQ-Z1 SoC Architecture", font_size=30,
                       color=TEXT_PRIMARY, weight=BOLD)
        soc_hdr.next_to(section, DOWN, buff=0.30)
        self.play(FadeIn(soc_hdr, shift=UP * 0.15), run_time=0.5)

        # ── Helper for SoC blocks ─────────────────────────────────────────
        def soc_block(label, sub, w, h, accent):
            box = RoundedRectangle(
                corner_radius=0.12, width=w, height=h,
                stroke_color=accent, stroke_width=2,
                fill_color=PANEL_FILL, fill_opacity=0.95,
            )
            t = Text(label, font_size=18, color=TEXT_PRIMARY, weight=BOLD)
            s = Text(sub, font_size=13, color=TEXT_MUTED)
            VGroup(t, s).arrange(DOWN, buff=0.06).move_to(box)
            return VGroup(box, t, s)

        # ── PL side (left) ────────────────────────────────────────────────
        pl_region = RoundedRectangle(
            corner_radius=0.18, width=5.5, height=4.0,
            stroke_color=PYNQ_RED, stroke_width=1.5,
            fill_color="#0A1520", fill_opacity=0.5,
        ).move_to(LEFT * 3.2 + DOWN * 0.6)
        pl_title = Text("PL (FPGA Fabric)", font_size=20,
                        color=PYNQ_RED, weight=BOLD)
        pl_title.next_to(pl_region, UP, buff=0.08)

        raycaster = soc_block("Raycaster IP", "DDA Engine",
                              2.2, 0.9, PYNQ_RED)
        raycaster.move_to(LEFT * 4.2 + UP * 0.2)

        bram = soc_block("BRAM", "Map + State",
                         1.6, 0.9, ACCENT_HARDWARE)
        bram.move_to(LEFT * 1.8 + UP * 0.2)

        hdmi = soc_block("HDMI Controller", "Pixel Output",
                         2.2, 0.8, PYNQ_RED)
        hdmi.move_to(LEFT * 4.2 + DOWN * 1.4)

        # ── PS side (right) ───────────────────────────────────────────────
        ps_region = RoundedRectangle(
            corner_radius=0.18, width=4.5, height=4.0,
            stroke_color=ACCENT_SERVER, stroke_width=1.5,
            fill_color="#0A1520", fill_opacity=0.5,
        ).move_to(RIGHT * 3.5 + DOWN * 0.6)
        ps_title = Text("PS (ARM Cortex-A9)", font_size=20,
                        color=ACCENT_SERVER, weight=BOLD)
        ps_title.next_to(ps_region, UP, buff=0.08)

        gameloop = soc_block("Game Loop", "Python",
                             2.0, 0.9, ACCENT_SERVER)
        gameloop.move_to(RIGHT * 3.5 + UP * 0.2)

        gpio = soc_block("AXI GPIO", "Buttons",
                         2.0, 0.8, ACCENT_SERVER)
        gpio.move_to(RIGHT * 3.5 + DOWN * 1.4)

        # ── Connections ───────────────────────────────────────────────────
        arr_kw = dict(buff=0.08, stroke_width=3,
                      max_tip_length_to_length_ratio=0.12)

        # Raycaster reads from BRAM
        a_rc_bram = Arrow(bram.get_left(), raycaster.get_right(),
                          color=ACCENT_HARDWARE, **arr_kw)
        a_rc_bram_lbl = Text("Read", font_size=13,
                             color=ACCENT_HARDWARE)
        a_rc_bram_lbl.next_to(a_rc_bram, UP, buff=0.04)

        # Raycaster outputs pixels to HDMI
        a_rc_hdmi = Arrow(raycaster.get_bottom(), hdmi.get_top(),
                          color=PYNQ_RED, **arr_kw)
        a_rc_hdmi_lbl = Text("Pixels", font_size=13, color=PYNQ_RED)
        a_rc_hdmi_lbl.next_to(a_rc_hdmi, LEFT, buff=0.04)

        # PS writes to BRAM via AXI
        a_ps_bram = Arrow(gameloop.get_left(), bram.get_right(),
                          color=ACCENT_SERVER, **arr_kw)
        a_ps_bram_lbl = Text("AXI", font_size=14,
                             color=ACCENT_SERVER, weight=BOLD)
        a_ps_bram_lbl.next_to(a_ps_bram, UP, buff=0.04)

        # GPIO to game loop
        a_gpio = Arrow(gpio.get_top(), gameloop.get_bottom(),
                       color=ACCENT_SERVER, **arr_kw)
        a_gpio_lbl = Text("BTN0-3", font_size=13, color=ACCENT_SERVER)
        a_gpio_lbl.next_to(a_gpio, RIGHT, buff=0.04)

        # ── Animate build ─────────────────────────────────────────────────
        self.play(
            FadeIn(pl_region), FadeIn(pl_title),
            FadeIn(ps_region), FadeIn(ps_title),
            run_time=0.5,
        )
        self.play(
            FadeIn(raycaster, shift=RIGHT * 0.15),
            FadeIn(bram, shift=LEFT * 0.15),
            FadeIn(hdmi, shift=UP * 0.15),
            run_time=0.5,
        )
        self.play(
            FadeIn(gameloop, shift=LEFT * 0.15),
            FadeIn(gpio, shift=UP * 0.15),
            run_time=0.5,
        )
        self.play(
            GrowArrow(a_rc_bram), FadeIn(a_rc_bram_lbl),
            GrowArrow(a_rc_hdmi), FadeIn(a_rc_hdmi_lbl),
            GrowArrow(a_ps_bram), FadeIn(a_ps_bram_lbl),
            GrowArrow(a_gpio),    FadeIn(a_gpio_lbl),
            run_time=0.6,
        )
        self.wait(0.5)

        # ── Animate data flow: PS writes → BRAM → Raycaster → HDMI ───────
        flow_dot = Dot(radius=0.10, color=ACCENT_HARDWARE, z_index=15)
        flow_lbl = Text("pos, angle, map", font_size=12,
                        color=ACCENT_HARDWARE)
        flow_grp = VGroup(flow_dot, flow_lbl).arrange(DOWN, buff=0.04)
        flow_grp.move_to(gameloop)

        self.play(FadeIn(flow_grp, scale=0.5), run_time=0.3)
        self.play(flow_grp.animate.move_to(bram), run_time=0.4)
        self.play(flow_grp.animate.move_to(raycaster), run_time=0.4)
        flow_lbl2 = Text("pixels", font_size=12, color=PYNQ_RED)
        flow_lbl2.next_to(flow_dot, DOWN, buff=0.04)
        self.play(
            Transform(flow_lbl, flow_lbl2),
            flow_grp.animate.move_to(hdmi),
            run_time=0.4,
        )
        self.play(FadeOut(flow_grp), run_time=0.3)
        self.wait(0.5)

        # ── Caption ───────────────────────────────────────────────────────
        soc_caption = Text(
            "PS writes game state to BRAM each tick — "
            "PL renders the next frame independently",
            font_size=18, color=TEXT_MUTED,
        )
        soc_caption.to_edge(DOWN, buff=0.15)
        self.play(FadeIn(soc_caption, shift=UP * 0.1), run_time=0.4)
        self.wait(2.0)

        # Fade part 2
        soc_all = VGroup(
            soc_hdr,
            pl_region, pl_title, ps_region, ps_title,
            raycaster, bram, hdmi, gameloop, gpio,
            a_rc_bram, a_rc_bram_lbl, a_rc_hdmi, a_rc_hdmi_lbl,
            a_ps_bram, a_ps_bram_lbl, a_gpio, a_gpio_lbl,
            soc_caption,
        )
        self.play(FadeOut(soc_all), run_time=0.6)

        # ==================================================================
        # PART 3 — Pipeline timing calculation
        # ==================================================================
        timing_hdr = Text("Raycaster Pipeline Timing", font_size=30,
                          color=TEXT_PRIMARY, weight=BOLD)
        timing_hdr.next_to(section, DOWN, buff=0.30)
        self.play(FadeIn(timing_hdr, shift=UP * 0.15), run_time=0.5)

        # ── Pipeline stages diagram ───────────────────────────────────────
        pipe_stages = ["DDA\nStepping", "Wall\nHeight", "Texture\nLookup",
                       "Pixel\nOutput"]
        pipe_colors = [PYNQ_RED, ACCENT_HARDWARE, ACCENT_STORAGE,
                       ACCENT_SERVER]
        pipe_boxes = VGroup()
        for label, color in zip(pipe_stages, pipe_colors):
            box = RoundedRectangle(
                corner_radius=0.10, width=2.2, height=1.1,
                stroke_color=color, stroke_width=2,
                fill_color=PANEL_FILL, fill_opacity=0.95,
            )
            txt = Text(label, font_size=16, color=color, weight=BOLD)
            txt.move_to(box)
            pipe_boxes.add(VGroup(box, txt))
        pipe_boxes.arrange(RIGHT, buff=0.35).move_to(UP * 0.3)

        pipe_arrows = VGroup()
        for i in range(len(pipe_boxes) - 1):
            pipe_arrows.add(Arrow(
                pipe_boxes[i].get_right(), pipe_boxes[i + 1].get_left(),
                buff=0.06, stroke_width=3, color=TEXT_MUTED,
                max_tip_length_to_length_ratio=0.14,
            ))

        self.play(
            LaggedStart(
                *[FadeIn(b, shift=RIGHT * 0.15) for b in pipe_boxes],
                lag_ratio=0.12,
            ),
            run_time=0.8,
        )
        self.play(FadeIn(pipe_arrows, lag_ratio=0.15), run_time=0.5)

        pipe_note = Text("Free-running pipeline: one column per clock "
                         "cycle after initial fill",
                         font_size=18, color=TEXT_MUTED)
        pipe_note.next_to(pipe_boxes, DOWN, buff=0.30)
        self.play(FadeIn(pipe_note, shift=UP * 0.1), run_time=0.4)
        self.wait(1.5)

        # ── Timing numbers ────────────────────────────────────────────────
        timing_lines = VGroup(
            Text("t_col  = ray_steps_max / f_clk  "
                 "= 64 / 100 MHz  = 0.64 μs",
                 font_size=20, color=TEXT_PRIMARY),
            Text("t_frame = 720 × 0.64 μs  ≈  461 μs",
                 font_size=20, color=TEXT_PRIMARY),
            Text("Budget for 60 fps  =  16.7 ms  "
                 "→  36× headroom",
                 font_size=20, color=HIT_COLOR, weight=BOLD),
        ).arrange(DOWN, buff=0.14, aligned_edge=LEFT)

        timing_bg = RoundedRectangle(
            corner_radius=0.10,
            width=timing_lines.width + 0.5,
            height=timing_lines.height + 0.3,
            fill_color=PANEL_FILL, fill_opacity=0.96,
            stroke_color=ACCENT_SERVER, stroke_width=1.5,
        )
        timing_bg.to_edge(DOWN, buff=0.12)
        timing_lines.move_to(timing_bg)

        self.play(FadeIn(VGroup(timing_bg, timing_lines)), run_time=0.6)
        self.wait(3.5)

        # ── Final fade ────────────────────────────────────────────────────
        self.play(FadeOut(VGroup(
            section, timing_hdr,
            pipe_boxes, pipe_arrows, pipe_note,
            timing_bg, timing_lines,
        )), run_time=0.8)


class MultiplayerScene(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND

        section = Text("5. Multiplayer — Seeing Each Other", font_size=42, color=PYNQ_RED, weight=BOLD)
        section.to_edge(UP, buff=0.4)
        self.play(Write(section), run_time=0.8)

        # ── 2-D map (left half) ─────────────────────────────────────────────
        world_map = ALGO_WORLD_MAP
        map_rows  = len(world_map)
        map_cols  = len(world_map[0])
        cell_size = 0.52
        grid_group = make_world_grid(world_map, cell_size=cell_size, empty_opacity=0.4)
        grid_group.shift(LEFT * 3.0 + DOWN * 0.2)
        self.play(FadeIn(grid_group, lag_ratio=0.005), run_time=0.7)

        # Player A and B positions in the map
        pos_a = grid_cell_center(grid_group, 5, 2, map_cols)
        pos_b = grid_cell_center(grid_group, 2, 5, map_cols)

        dot_a = Dot(pos_a, radius=0.13, color=PLAYER_A_COLOR, z_index=6)
        dot_b = Dot(pos_b, radius=0.13, color=PLAYER_B_COLOR, z_index=6)
        lbl_a = Text("A", font_size=18, color=PLAYER_A_COLOR, weight=BOLD).next_to(dot_a, LEFT,  buff=0.15)
        lbl_b = Text("B", font_size=18, color=PLAYER_B_COLOR, weight=BOLD).next_to(dot_b, RIGHT, buff=0.15)

        self.play(FadeIn(dot_a, scale=0.5), FadeIn(lbl_a), run_time=0.5)
        self.play(FadeIn(dot_b, scale=0.5), FadeIn(lbl_b), run_time=0.5)

        # ── Step 1: UDP packet from A to server ─────────────────────────────
        server_box = RoundedRectangle(
            corner_radius=0.15, width=2.2, height=0.7,
            stroke_color=ACCENT_SERVER, stroke_width=2,
            fill_color=PANEL_FILL, fill_opacity=0.95,
        ).move_to(UP * 2.8)
        server_txt = Text("AWS EC2", font_size=22, color=ACCENT_SERVER, weight=BOLD).move_to(server_box)
        server_grp = VGroup(server_box, server_txt)
        self.play(FadeIn(server_grp, shift=DOWN * 0.2), run_time=0.5)

        udp_up = Arrow(dot_a.get_top(), server_box.get_bottom(), buff=0.1,
                       stroke_width=3, color=PLAYER_A_COLOR,
                       max_tip_length_to_length_ratio=0.18)
        udp_lbl_up = Text("UDP  pos + angle", font_size=20, color=PLAYER_A_COLOR)
        udp_lbl_up.next_to(udp_up, LEFT, buff=0.12)
        self.play(GrowArrow(udp_up), FadeIn(udp_lbl_up), run_time=0.7)
        self.wait(0.5)

        # ── Step 2: server broadcasts B's position back to A ────────────────
        udp_down = Arrow(server_box.get_bottom() + RIGHT * 0.3, dot_a.get_top() + RIGHT * 0.2,
                         buff=0.1, stroke_width=3, color=ACCENT_SERVER,
                         max_tip_length_to_length_ratio=0.18)
        udp_lbl_down = Text("B's pos + angle", font_size=20, color=ACCENT_SERVER)
        udp_lbl_down.next_to(udp_down, RIGHT, buff=0.12)
        self.play(GrowArrow(udp_down), FadeIn(udp_lbl_down), run_time=0.7)
        self.wait(0.6)

        # ── Step 3: sprite projection on the right ──────────────────────────
        # Fade out the map-side labels and arrows, keep dots for reference
        self.play(
            FadeOut(VGroup(udp_up, udp_lbl_up, udp_down, udp_lbl_down, server_grp)),
            run_time=0.5,
        )

        proj_title = Text("A's rendered view", font_size=24, color=TEXT_MUTED)
        proj_title.move_to(RIGHT * 3.0 + UP * 2.5)
        self.play(FadeIn(proj_title), run_time=0.4)

        # Simple pseudo-screen
        screen = Rectangle(
            width=3.8, height=2.8,
            stroke_color="#2A4060", stroke_width=2,
            fill_color="#08101A", fill_opacity=1.0,
        ).move_to(RIGHT * 3.0 + DOWN * 0.1)
        self.play(FadeIn(screen), run_time=0.4)

        # Floor / ceiling
        ceiling = Rectangle(width=3.8, height=1.4, fill_color="#0D1A2E", fill_opacity=1.0, stroke_width=0)
        ceiling.align_to(screen, UP).align_to(screen, LEFT)
        floor_r = Rectangle(width=3.8, height=1.4, fill_color="#1A1A1A", fill_opacity=1.0, stroke_width=0)
        floor_r.align_to(screen, DOWN).align_to(screen, LEFT)
        self.add(ceiling, floor_r)

        # Wall columns (simple 3-D feel)
        wall_cols = VGroup()
        col_count = 12
        col_w     = 3.8 / col_count
        for i in range(col_count):
            h = 1.1 + 0.35 * np.sin(i * 0.55)   # vary heights slightly
            shade = interpolate_color(ManimColor(WALL_COLOR_DARK), ManimColor(WALL_COLOR), i / col_count)
            col = Rectangle(
                width=col_w - 0.02, height=h,
                fill_color=shade, fill_opacity=0.9, stroke_width=0,
            ).move_to(screen.get_left() + RIGHT * (i + 0.5) * col_w + RIGHT * 0 + UP * 0)
            wall_cols.add(col)
        self.play(FadeIn(wall_cols), run_time=0.6)

        # Player B sprite — a bright column in the middle of the screen
        sprite_x = screen.get_center()[0] + 0.3
        sprite_h = 1.6
        sprite_col = Rectangle(
            width=0.28, height=sprite_h,
            fill_color=PLAYER_B_COLOR, fill_opacity=0.85, stroke_width=0,
        ).move_to([sprite_x, screen.get_center()[1], 0])

        sprite_label = Text("Player B", font_size=20, color=PLAYER_B_COLOR)
        sprite_label.next_to(sprite_col, UP, buff=0.18)

        self.play(FadeIn(sprite_col, scale=0.3), run_time=0.6)
        self.play(FadeIn(sprite_label), run_time=0.4)
        self.wait(0.4)

        # Annotation: sprite height computed the same way as walls
        annot = VGroup(
            Text("Sprite column computed identically to walls:", font_size=22, color=TEXT_PRIMARY, weight=BOLD),
            Text("spriteHeight  =  k / distance_to_B",          font_size=22, color=TEXT_MUTED, slant=ITALIC),
            Text("Drawn only if B is in A's field of view",      font_size=22, color=TEXT_MUTED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        annot.next_to(screen, DOWN, buff=0.38)
        self.play(FadeIn(annot, shift=UP * 0.2, lag_ratio=0.1), run_time=1.2)
        self.wait(2.8)

        self.play(FadeOut(VGroup(
            section, grid_group, dot_a, dot_b, lbl_a, lbl_b,
            proj_title, screen, ceiling, floor_r,
            wall_cols, sprite_col, sprite_label, annot,
        )), run_time=0.9)


# ═══════════════════════════════════════════════════════════════════════════
# Sprite & Texture Rendering Pipeline
# ═══════════════════════════════════════════════════════════════════════════

class SpriteTexturingScene(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND

        title = Text("Sprite & Texture Rendering", font_size=40,
                     color=PYNQ_RED, weight=BOLD)
        title.to_edge(UP, buff=0.35)
        self.play(Write(title), run_time=0.8)

        # ==================================================================
        # PART 1 — Sprite rendering pipeline (5 stages)
        # ==================================================================
        part1_hdr = Text("Sprite Rendering Pipeline", font_size=28,
                         color=TEXT_PRIMARY, weight=BOLD)
        part1_hdr.move_to(ORIGIN)
        self.play(FadeIn(part1_hdr, shift=UP * 0.15), run_time=0.5)
        self.wait(1.0)
        self.play(FadeOut(part1_hdr), run_time=0.4)

        # ── 5-stage pipeline boxes ────────────────────────────────────────
        stages = [
            ("1. Z-Buffer\nRecord",
             "Store perpendicular wall\ndist per column during\nwall pass"),
            ("2. Camera\nProjection",
             "Subtract player pos,\nmultiply by inverse\ncamera matrix"),
            ("3. Screen\nDimensions",
             "spriteHeight =\nk / perpDist\n(same as walls)"),
            ("4. Column\nRendering",
             "Render column by column,\nskip if occluded\nby Z-buffer"),
            ("5. Transparency\nMask",
             "Colour-key check\nper pixel — avoids\nsolid rectangles"),
        ]

        stage_colors = [PYNQ_RED, ACCENT_SERVER, ACCENT_HARDWARE,
                        HIT_COLOR, "#BB66FF"]

        stage_boxes = VGroup()
        for (label, desc), color in zip(stages, stage_colors):
            box = RoundedRectangle(
                corner_radius=0.10, width=2.3, height=2.0,
                stroke_color=color, stroke_width=2,
                fill_color=PANEL_FILL, fill_opacity=0.95,
            )
            t = Text(label, font_size=14, color=color, weight=BOLD)
            d = Text(desc, font_size=11, color=TEXT_MUTED)
            VGroup(t, d).arrange(DOWN, buff=0.12).move_to(box)
            stage_boxes.add(VGroup(box, t, d))

        stage_boxes.arrange(RIGHT, buff=0.25).move_to(UP * 0.5)
        if stage_boxes.get_width() > 13.0:
            stage_boxes.scale_to_fit_width(13.0)

        stage_arrows = VGroup()
        for i in range(len(stage_boxes) - 1):
            stage_arrows.add(Arrow(
                stage_boxes[i].get_right(), stage_boxes[i + 1].get_left(),
                buff=0.04, stroke_width=2.5, color=TEXT_MUTED,
                max_tip_length_to_length_ratio=0.18,
            ))

        self.play(
            LaggedStart(
                *[FadeIn(b, shift=RIGHT * 0.12) for b in stage_boxes],
                lag_ratio=0.10,
            ),
            run_time=1.0,
        )
        self.play(FadeIn(stage_arrows, lag_ratio=0.12), run_time=0.5)
        self.wait(1.0)

        # ── Key detail: runs in parallel with wall raycasting ─────────────
        sprite_note = VGroup(
            Text("Sprite casting runs in parallel with wall raycasting",
                 font_size=18, color=TEXT_PRIMARY, weight=BOLD),
            Text("Uses a longer window — multi-cycle dividers allowed "
                 "without impacting throughput",
                 font_size=16, color=TEXT_MUTED),
        ).arrange(DOWN, buff=0.06, aligned_edge=LEFT)
        sn_bg = RoundedRectangle(
            corner_radius=0.10,
            width=sprite_note.width + 0.5,
            height=sprite_note.height + 0.3,
            fill_color=PANEL_FILL, fill_opacity=0.96,
            stroke_color=ACCENT_HARDWARE, stroke_width=1.5,
        )
        sn_bg.to_edge(DOWN, buff=0.12)
        sprite_note.move_to(sn_bg)
        self.play(FadeIn(VGroup(sn_bg, sprite_note)), run_time=0.5)
        self.wait(2.5)

        self.play(FadeOut(VGroup(
            stage_boxes, stage_arrows, sn_bg, sprite_note,
        )), run_time=0.6)

        # ==================================================================
        # PART 2 — Texture rendering: how wall textures are looked up
        # ==================================================================
        part2_hdr = Text("Wall Texture Mapping", font_size=28,
                         color=TEXT_PRIMARY, weight=BOLD)
        part2_hdr.move_to(ORIGIN)
        self.play(FadeIn(part2_hdr, shift=UP * 0.15), run_time=0.5)
        self.wait(1.0)
        self.play(FadeOut(part2_hdr), run_time=0.4)

        # ── Left side: how X and Y texture coords are derived ─────────────
        tex_steps = VGroup(
            Text("Texture coordinate lookup:", font_size=22,
                 color=TEXT_PRIMARY, weight=BOLD),
            Text("X position: recorded at end of DDA stepping",
                 font_size=18, color=ACCENT_SERVER),
            Text("    → which column within the wall tile",
                 font_size=16, color=TEXT_MUTED),
            Text("Y position: reciprocal LUT on perpWallDist",
                 font_size=18, color=ACCENT_HARDWARE),
            Text("    → fractional depth within the wall column",
                 font_size=16, color=TEXT_MUTED),
            Text("Together they index a 32×32 12-bit RGB bitmap",
                 font_size=18, color=HIT_COLOR),
            Text("    stored at reduced bit-width, zero-extended to 24-bit",
                 font_size=16, color=TEXT_MUTED),
        ).arrange(DOWN, buff=0.14, aligned_edge=LEFT)
        tex_steps.move_to(LEFT * 2.5 + UP * 0.0)
        if tex_steps.get_height() > 4.5:
            tex_steps.scale_to_fit_height(4.5)

        self.play(FadeIn(tex_steps, lag_ratio=0.06), run_time=1.2)
        self.wait(1.0)

        # ── Right side: simplified texture grid ───────────────────────────
        tex_size = 8  # visual 8x8 grid representing 32x32 texture
        tex_cs = 0.28
        tex_cx = 4.0
        tex_cy = 0.3

        tex_grid = VGroup()
        for r in range(tex_size):
            for c in range(tex_size):
                # Create a colourful pattern to look like a texture
                hue = (r * tex_size + c) / (tex_size * tex_size)
                # Use warm browns/reds for a brick-like feel
                r_val = 0.4 + 0.4 * np.sin(hue * 6.28 + 0.0)
                g_val = 0.2 + 0.2 * np.sin(hue * 6.28 + 2.1)
                b_val = 0.1 + 0.1 * np.sin(hue * 6.28 + 4.2)
                color_hex = f"#{int(r_val*255):02x}{int(g_val*255):02x}{int(b_val*255):02x}"

                sq = Square(side_length=tex_cs, stroke_width=0.3,
                            stroke_color="#333333")
                sq.set_fill(color_hex, opacity=0.9)
                sq.move_to([
                    tex_cx + (c - tex_size / 2 + 0.5) * tex_cs,
                    tex_cy + (tex_size / 2 - r - 0.5) * tex_cs,
                    0,
                ])
                tex_grid.add(sq)

        tex_label = Text("32×32 texture bitmap", font_size=16,
                         color=TEXT_MUTED)
        tex_label.next_to(tex_grid, DOWN, buff=0.15)
        tex_format = Text("12-bit RGB per texel", font_size=14,
                          color=TEXT_DIM)
        tex_format.next_to(tex_label, DOWN, buff=0.06)

        self.play(FadeIn(tex_grid, lag_ratio=0.005), run_time=0.6)
        self.play(FadeIn(tex_label), FadeIn(tex_format), run_time=0.4)

        # Highlight a single texel
        highlight_r, highlight_c = 3, 5
        highlight_idx = highlight_r * tex_size + highlight_c
        highlight_sq = SurroundingRectangle(
            tex_grid[highlight_idx], color=HIT_COLOR, buff=0.02,
            stroke_width=2.5,
        )
        coord_lbl = Text(f"(X={highlight_c}, Y={highlight_r})",
                         font_size=14, color=HIT_COLOR)
        coord_lbl.next_to(highlight_sq, UP + RIGHT, buff=0.08)
        self.play(Create(highlight_sq), FadeIn(coord_lbl), run_time=0.5)
        self.wait(1.5)

        # ── LUT callout at the bottom ─────────────────────────────────────
        lut_callout = VGroup(
            Text("LUT Design Tradeoffs:", font_size=18,
                 color=ACCENT_HARDWARE, weight=BOLD),
            Text("Single-cycle access (vs multi-cycle DSP dividers) · "
                 "Preserves DSP slices for future compute",
                 font_size=15, color=TEXT_MUTED),
            Text("LUT addressing allows independent tuning of "
                 "input/output precision per table",
                 font_size=15, color=TEXT_MUTED),
        ).arrange(DOWN, buff=0.06, aligned_edge=LEFT)
        lut_bg = RoundedRectangle(
            corner_radius=0.10,
            width=lut_callout.width + 0.5,
            height=lut_callout.height + 0.3,
            fill_color=PANEL_FILL, fill_opacity=0.96,
            stroke_color=ACCENT_HARDWARE, stroke_width=1.5,
        )
        lut_bg.to_edge(DOWN, buff=0.08)
        lut_callout.move_to(lut_bg)
        self.play(FadeIn(VGroup(lut_bg, lut_callout)), run_time=0.5)
        self.wait(3.0)

        # ── Sprite format note ────────────────────────────────────────────
        self.play(FadeOut(VGroup(lut_bg, lut_callout)), run_time=0.3)

        sprite_fmt = VGroup(
            Text("Sprites: 16×16 12-bit RGB bitmaps", font_size=20,
                 color="#BB66FF", weight=BOLD),
            Text("Transparency mask enables non-rectangular shapes "
                 "(e.g. Pac-Man ghosts)",
                 font_size=17, color=TEXT_MUTED),
            Text("Fully customisable — swap .mem files for any texture",
                 font_size=17, color=TEXT_MUTED),
        ).arrange(DOWN, buff=0.08, aligned_edge=LEFT)
        sf_bg = RoundedRectangle(
            corner_radius=0.10,
            width=sprite_fmt.width + 0.5,
            height=sprite_fmt.height + 0.3,
            fill_color=PANEL_FILL, fill_opacity=0.96,
            stroke_color="#BB66FF", stroke_width=1.5,
        )
        sf_bg.to_edge(DOWN, buff=0.08)
        sprite_fmt.move_to(sf_bg)
        self.play(FadeIn(VGroup(sf_bg, sprite_fmt)), run_time=0.5)
        self.wait(2.5)

        self.play(FadeOut(VGroup(
            title, tex_steps,
            tex_grid, tex_label, tex_format,
            highlight_sq, coord_lbl,
            sf_bg, sprite_fmt,
        )), run_time=0.8)


class MultiNodeScene(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND

        section = Text("6. Multi-Node Tile Distribution", font_size=42, color=PYNQ_RED, weight=BOLD)
        section.to_edge(UP, buff=0.4)
        self.play(Write(section), run_time=0.8)

        screen_w = 5.0
        screen_h = 3.0
        tiles_x  = 4
        tiles_y  = 2
        tile_w   = screen_w / tiles_x
        tile_h   = screen_h / tiles_y
        node_colors = ["#F05252", "#4A9EFF", "#4ADB7A", "#FFAA33"]
        node_names  = ["Node 0", "Node 1", "Node 2", "Node 3"]

        screen_rect = Rectangle(width=screen_w, height=screen_h,
                                stroke_color=TEXT_MUTED, stroke_width=2).shift(DOWN * 0.3)
        self.play(Create(screen_rect), run_time=0.5)

        tiles = VGroup()
        for row in range(tiles_y):
            for col in range(tiles_x):
                node_idx = (row * tiles_x + col) % len(node_colors)
                tile = Rectangle(
                    width=tile_w - 0.04, height=tile_h - 0.04,
                    fill_color=node_colors[node_idx], fill_opacity=0.5,
                    stroke_color=node_colors[node_idx], stroke_width=1.5,
                )
                tile.move_to(
                    screen_rect.get_corner(UL)
                    + np.array([(col + 0.5) * tile_w, -(row + 0.5) * tile_h, 0])
                )
                tiles.add(tile)
        self.play(FadeIn(tiles, lag_ratio=0.1), run_time=1.5)

        legend = VGroup()
        for name, color in zip(node_names, node_colors):
            dot   = Dot(radius=0.09, color=color)
            label = Text(name, font_size=20, color=color)
            legend.add(VGroup(dot, label).arrange(RIGHT, buff=0.16))
        legend.arrange(RIGHT, buff=0.65)
        legend.next_to(screen_rect, DOWN, buff=0.48)
        self.play(FadeIn(legend), run_time=0.5)

        arch_text = VGroup(
            Text("Each PYNQ node renders its tile independently", font_size=22, color=TEXT_MUTED),
            Text("Server orchestrates and aggregates via Redis / DynamoDB", font_size=22, color=TEXT_MUTED),
        ).arrange(DOWN, buff=0.18)
        arch_text.next_to(legend, DOWN, buff=0.38)
        self.play(FadeIn(arch_text, shift=UP * 0.2), run_time=0.8)
        self.wait(2.8)
        self.play(FadeOut(VGroup(section, screen_rect, tiles, legend, arch_text)), run_time=0.8)


class ServerHardwareSegment(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND

        title    = Text("PYNQCAST Runtime", font_size=42, color=TEXT_PRIMARY, weight=BOLD)
        subtitle = Text(
            "Hardware rendering on the edge.  Authoritative game logic in the cloud.",
            font_size=22, color=TEXT_MUTED,
        )
        title_group = VGroup(title, subtitle).arrange(DOWN, buff=0.18).to_edge(UP, buff=0.45)

        hardware_lane   = make_hardware_lane().scale(0.88).to_edge(LEFT, buff=0.5).shift(DOWN * 0.25)
        server_pipeline = make_seda_pipeline().scale(0.86).move_to(ORIGIN + RIGHT * 0.2 + DOWN * 0.1)
        service_branch  = make_service_branch().scale(0.85).to_edge(RIGHT, buff=0.42).shift(DOWN * 0.2)
        storage_row     = make_storage_row().scale(0.8).next_to(server_pipeline, DOWN, buff=0.55)

        top_divider = Line(LEFT * 7.2, RIGHT * 7.2, stroke_color="#16324D", stroke_width=2).next_to(title_group, DOWN, buff=0.28)

        flow_a = Arrow(hardware_lane[0].get_right(), server_pipeline[0][0].get_left(),
                       buff=0.12, stroke_width=5, color=ACCENT_HARDWARE)
        flow_b = Arrow(hardware_lane[1].get_right(), server_pipeline[0][0].get_left() + DOWN * 1.2,
                       buff=0.12, stroke_width=5, color=ACCENT_HARDWARE)
        control_arrow = Arrow(server_pipeline[0][2].get_right(), service_branch[1].get_left(),
                              buff=0.12, stroke_width=4, color=ACCENT_SERVER)
        sidecar_arrow = Arrow(server_pipeline[0][3].get_right(), service_branch[0].get_left(),
                              buff=0.12, stroke_width=4, color=ACCENT_STORAGE)
        storage_down  = Arrow(service_branch[0].get_bottom(), storage_row[0][1].get_top(),
                              buff=0.12, stroke_width=4, color=ACCENT_STORAGE)

        udp_label     = Text("UDP 9000",         font_size=20, color=TEXT_MUTED).next_to(flow_a, UP, buff=0.1)
        monitor_label = Text("monitor + control", font_size=20, color=TEXT_MUTED).next_to(control_arrow, UP, buff=0.08)
        sidecar_label = Text("async persistence", font_size=20, color=TEXT_MUTED).next_to(sidecar_arrow, UP, buff=0.08)

        edge_note  = Text("Edge: real FPGA rendering",           font_size=20, color=ACCENT_HARDWARE, weight=BOLD)
        cloud_note = Text("Cloud: authoritative state + storage", font_size=20, color=ACCENT_SERVER,  weight=BOLD)
        edge_note.next_to(hardware_lane, UP, buff=0.18)
        cloud_note.next_to(server_pipeline, UP, buff=0.18)

        demo_modes = VGroup(
            Text("Manual:", font_size=21, color=TEXT_PRIMARY, weight=BOLD),
            Text("player controls board locally",          font_size=21, color=TEXT_MUTED),
            Text("Auto:",   font_size=21, color=TEXT_PRIMARY, weight=BOLD),
            Text("AI drives the runner / tagger on-board", font_size=21, color=TEXT_MUTED),
        ).arrange_in_grid(rows=2, cols=2, col_alignments="lr", buff=(0.18, 0.2))
        demo_modes.scale(0.85).to_edge(DOWN, buff=0.35)

        storage_caption = Text(
            "Replay, metadata, and post-match processing stay off the hot path.",
            font_size=19, color=TEXT_MUTED,
        ).next_to(storage_row, DOWN, buff=0.12)
        if storage_caption.get_bottom()[1] < -3.8:
            storage_caption.to_edge(DOWN, buff=0.12)

        self.play(FadeIn(title_group, shift=DOWN * 0.2), Create(top_divider))
        self.play(
            LaggedStart(
                FadeIn(hardware_lane,   shift=RIGHT * 0.2),
                FadeIn(server_pipeline, shift=UP * 0.2),
                FadeIn(service_branch,  shift=LEFT * 0.2),
                lag_ratio=0.2,
            ),
            FadeIn(edge_note,  shift=UP * 0.1),
            FadeIn(cloud_note, shift=UP * 0.1),
        )
        self.play(LaggedStart(GrowArrow(flow_a), GrowArrow(flow_b), FadeIn(udp_label, shift=UP * 0.1), lag_ratio=0.12))
        self.play(LaggedStart(
            GrowArrow(control_arrow), GrowArrow(sidecar_arrow),
            FadeIn(monitor_label, shift=UP * 0.1), FadeIn(sidecar_label, shift=UP * 0.1),
            lag_ratio=0.12,
        ))
        self.play(FadeIn(storage_row, shift=UP * 0.2), GrowArrow(storage_down), FadeIn(storage_caption, shift=UP * 0.1))

        highlight_box  = SurroundingRectangle(server_pipeline[0][1], color=ACCENT_ALERT, buff=0.12, corner_radius=0.12)
        hot_path_copy  = Text("T2 stays non-blocking and authoritative.", font_size=24, color=ACCENT_ALERT, weight=BOLD)
        hot_path_copy.next_to(server_pipeline, RIGHT, buff=0.65).shift(UP * 0.5)
        self.play(Create(highlight_box), FadeIn(hot_path_copy, shift=RIGHT * 0.15))
        self.wait(0.5)
        self.play(FadeOut(highlight_box), FadeOut(hot_path_copy))

        self.play(FadeIn(demo_modes, shift=UP * 0.15))
        self.wait(1.8)


class ServerHardwareClosingCard(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND

        card = RoundedRectangle(
            corner_radius=0.25, width=9.5, height=3.6,
            stroke_color=ACCENT_SERVER, stroke_width=2.5,
            fill_color=PANEL_FILL, fill_opacity=0.96,
        )
        headline = Text("One System, Two Strengths", font_size=42, color=TEXT_PRIMARY, weight=BOLD)
        line1    = Text("FPGA boards handle the edge rendering.",                     font_size=26, color=ACCENT_HARDWARE)
        line2    = Text("The EC2 stack owns game state, storage, replay, and control.", font_size=26, color=ACCENT_SERVER)
        copy = VGroup(headline, line1, line2).arrange(DOWN, buff=0.26)
        copy.move_to(card.get_center())
        group = VGroup(card, copy)

        self.play(FadeIn(group, scale=0.96))
        self.wait(2.2)
        self.play(FadeOut(group, scale=1.02))


# ═══════════════════════════════════════════════════════════════════════════
# SEDA Deep-Dive — animated packet flow with queue isolation
# ═══════════════════════════════════════════════════════════════════════════

class SEDADeepDiveScene(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND

        # ── Title ─────────────────────────────────────────────────────────
        title = Text("SEDA Pipeline — Queue Isolation", font_size=40,
                     color=PYNQ_RED, weight=BOLD)
        title.to_edge(UP, buff=0.35)
        self.play(Write(title), run_time=0.8)

        # ── Stage boxes — horizontal layout ───────────────────────────────
        stage_data = [
            ("T1: Ingest",    "UDP Receiver",         ACCENT_SERVER),
            ("T2: Brain",     "20 Hz Game Tick",       ACCENT_SERVER),
            ("T3: Broadcast", "Egress to clients",     ACCENT_SERVER),
            ("T4: Archivist", "Redis Writer (thread)",  ACCENT_ALERT),
        ]

        stages = VGroup()
        for name, sub, accent in stage_data:
            box = RoundedRectangle(
                corner_radius=0.15, width=2.6, height=1.3,
                stroke_color=accent, stroke_width=2,
                fill_color=PANEL_FILL, fill_opacity=0.95,
            )
            t = Text(name, font_size=20, color=TEXT_PRIMARY, weight=BOLD)
            s = Text(sub, font_size=14, color=TEXT_MUTED)
            VGroup(t, s).arrange(DOWN, buff=0.10).move_to(box)
            stages.add(VGroup(box, t, s))

        # T1 → PQ → T2 horizontal, then T2 fans to BQ → T3 (upper right)
        #                                  and WQ → T4 (lower right)
        t1, t2, t3, t4 = stages
        t1.move_to(LEFT * 5.5 + UP * 0.5)
        t2.move_to(LEFT * 0.8 + UP * 0.5)
        t3.move_to(RIGHT * 4.5 + UP * 2.0)
        t4.move_to(RIGHT * 4.5 + DOWN * 1.0)

        # ── Queue boxes (dashed border) ───────────────────────────────────
        def make_queue(label_str, width=1.8):
            qbox = RoundedRectangle(
                corner_radius=0.10, width=width, height=0.65,
                stroke_color=TEXT_MUTED, stroke_width=1.5,
                fill_color="#0C1A2C", fill_opacity=0.90,
            )
            qbox.set_stroke(opacity=0.7)
            qlbl = Text(label_str, font_size=13, color=TEXT_MUTED)
            qlbl.move_to(qbox)
            return VGroup(qbox, qlbl)

        pq = make_queue("PacketQueue")
        pq.move_to((t1.get_right() + t2.get_left()) / 2)
        bq = make_queue("BroadcastQueue")
        bq.move_to(RIGHT * 2.0 + UP * 2.0)
        wq = make_queue("WriteQueue")
        wq.move_to(RIGHT * 2.0 + DOWN * 1.0)

        # ── Arrows ────────────────────────────────────────────────────────
        arr_kw = dict(buff=0.08, stroke_width=3,
                      max_tip_length_to_length_ratio=0.14)
        a1 = Arrow(t1.get_right(), pq.get_left(), color=ACCENT_SERVER, **arr_kw)
        a2 = Arrow(pq.get_right(), t2.get_left(), color=ACCENT_SERVER, **arr_kw)
        a3 = Arrow(t2.get_right() + UP * 0.3, bq.get_left(),
                   color=ACCENT_SERVER, **arr_kw)
        a4 = Arrow(bq.get_right(), t3.get_left(), color=ACCENT_SERVER, **arr_kw)
        a5 = Arrow(t2.get_right() + DOWN * 0.3, wq.get_left(),
                   color=ACCENT_ALERT, **arr_kw)
        a6 = Arrow(wq.get_right(), t4.get_left(), color=ACCENT_ALERT, **arr_kw)

        # ── Animate build ─────────────────────────────────────────────────
        self.play(FadeIn(t1, shift=RIGHT * 0.2), run_time=0.4)
        self.play(GrowArrow(a1), FadeIn(pq), run_time=0.4)
        self.play(GrowArrow(a2), FadeIn(t2, shift=RIGHT * 0.2), run_time=0.4)
        self.play(
            GrowArrow(a3), FadeIn(bq), GrowArrow(a4),
            FadeIn(t3, shift=LEFT * 0.2),
            run_time=0.5,
        )
        self.play(
            GrowArrow(a5), FadeIn(wq), GrowArrow(a6),
            FadeIn(t4, shift=LEFT * 0.2),
            run_time=0.5,
        )
        self.wait(0.8)

        # ── Asyncio vs Thread swim-lane labels ────────────────────────────
        async_lbl = Text("asyncio event loop (single thread, no locks)",
                         font_size=16, color=ACCENT_SERVER, slant=ITALIC)
        async_lbl.next_to(t1, UP, buff=0.25).shift(RIGHT * 2.0)
        thread_lbl = Text("OS thread (absorbs Redis latency)",
                          font_size=16, color=ACCENT_ALERT, slant=ITALIC)
        thread_lbl.next_to(t4, DOWN, buff=0.25)
        self.play(FadeIn(async_lbl), FadeIn(thread_lbl), run_time=0.5)
        self.wait(0.6)

        # ── Animate a packet flowing through ──────────────────────────────
        packet = Dot(radius=0.10, color=ACCENT_HARDWARE, z_index=15)
        pkt_lbl = Text("UDP pkt", font_size=12, color=ACCENT_HARDWARE)
        pkt_grp = VGroup(packet, pkt_lbl).arrange(DOWN, buff=0.04)
        pkt_grp.move_to(t1.get_left() + LEFT * 0.8)

        self.play(FadeIn(pkt_grp, shift=RIGHT * 0.3), run_time=0.3)
        self.play(pkt_grp.animate.move_to(t1), run_time=0.3)
        self.play(pkt_grp.animate.move_to(pq), run_time=0.25)
        self.play(pkt_grp.animate.move_to(t2), run_time=0.3)

        # Fan out: clone to T3 path and T4 path
        pkt_t3 = pkt_grp.copy().set_color(ACCENT_SERVER)
        pkt_t4 = pkt_grp.copy().set_color(ACCENT_ALERT)
        self.add(pkt_t3, pkt_t4)
        self.play(
            pkt_t3.animate.move_to(bq),
            pkt_t4.animate.move_to(wq),
            FadeOut(pkt_grp),
            run_time=0.35,
        )
        self.play(
            pkt_t3.animate.move_to(t3),
            pkt_t4.animate.move_to(t4),
            run_time=0.35,
        )
        self.play(FadeOut(pkt_t3), FadeOut(pkt_t4), run_time=0.3)
        self.wait(0.5)

        # ── Key insight: queue isolation ──────────────────────────────────
        # Flash T4 red to simulate Redis latency
        t4_flash = SurroundingRectangle(t4, color=ACCENT_ALERT, buff=0.08,
                                        corner_radius=0.12, stroke_width=3)
        latency_lbl = Text("Redis slow: 5 ms", font_size=18,
                           color=ACCENT_ALERT, weight=BOLD)
        latency_lbl.next_to(t4, UP, buff=0.15)

        t2_ok = SurroundingRectangle(t2, color=HIT_COLOR, buff=0.08,
                                     corner_radius=0.12, stroke_width=3)
        ok_lbl = Text("T2 keeps ticking at 20 Hz", font_size=18,
                       color=HIT_COLOR, weight=BOLD)
        ok_lbl.next_to(t2, DOWN, buff=0.55)

        self.play(Create(t4_flash), FadeIn(latency_lbl), run_time=0.5)
        self.play(Create(t2_ok), FadeIn(ok_lbl), run_time=0.5)
        self.wait(1.5)

        # ── Takeaway callout ──────────────────────────────────────────────
        takeaway = VGroup(
            Text("Queues decouple every stage:", font_size=22,
                 color=TEXT_PRIMARY, weight=BOLD),
            Text("slow storage never blocks gameplay",
                 font_size=20, color=HIT_COLOR),
        ).arrange(DOWN, buff=0.10)
        tk_bg = RoundedRectangle(
            corner_radius=0.12,
            width=takeaway.width + 0.5, height=takeaway.height + 0.35,
            fill_color=PANEL_FILL, fill_opacity=0.96,
            stroke_color=HIT_COLOR, stroke_width=1.8,
        )
        tk_bg.to_edge(DOWN, buff=0.2)
        takeaway.move_to(tk_bg)
        self.play(FadeIn(VGroup(tk_bg, takeaway)), run_time=0.5)
        self.wait(2.5)

        self.play(FadeOut(VGroup(
            title, t1, t2, t3, t4, pq, bq, wq,
            a1, a2, a3, a4, a5, a6,
            async_lbl, thread_lbl,
            t4_flash, latency_lbl, t2_ok, ok_lbl,
            tk_bg, takeaway,
        )), run_time=0.8)


# ═══════════════════════════════════════════════════════════════════════════
# Storage Tiering — Hot / Warm / Cold with data flow
# ═══════════════════════════════════════════════════════════════════════════

class StorageTieringScene(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND

        title = Text("Storage Tiers — Hot / Warm / Cold", font_size=40,
                     color=PYNQ_RED, weight=BOLD)
        title.to_edge(UP, buff=0.35)
        self.play(Write(title), run_time=0.8)

        # ── Three tier panels ─────────────────────────────────────────────
        tier_w, tier_h = 10.5, 1.6

        # --- Redis (Hot) ---
        redis_box = RoundedRectangle(
            corner_radius=0.15, width=tier_w, height=tier_h,
            stroke_color=ACCENT_ALERT, stroke_width=2,
            fill_color=PANEL_FILL, fill_opacity=0.95,
        )
        redis_title = Text("Redis — Hot Tier", font_size=24,
                           color=ACCENT_ALERT, weight=BOLD)
        redis_detail = VGroup(
            Text("In-memory, local to EC2  ·  reads/writes ~0.1 ms",
                 font_size=16, color=TEXT_MUTED),
            Text("player:1  player:2  (HSET per tick)  ·  game:seda-events  game:seda-replay",
                 font_size=14, color=TEXT_DIM),
        ).arrange(DOWN, buff=0.06, aligned_edge=LEFT)
        redis_content = VGroup(redis_title, redis_detail).arrange(
            DOWN, buff=0.12, aligned_edge=LEFT)
        redis_content.move_to(redis_box).shift(LEFT * 0.3)
        redis_lbl = Text("~0.1 ms", font_size=18, color=ACCENT_ALERT,
                         weight=BOLD)
        redis_lbl.next_to(redis_box, RIGHT, buff=0.2)
        redis_tier = VGroup(redis_box, redis_content, redis_lbl)

        # --- DynamoDB (Warm) ---
        ddb_box = RoundedRectangle(
            corner_radius=0.15, width=tier_w, height=tier_h,
            stroke_color=ACCENT_HARDWARE, stroke_width=2,
            fill_color=PANEL_FILL, fill_opacity=0.95,
        )
        ddb_title = Text("DynamoDB — Warm Tier", font_size=24,
                         color=ACCENT_HARDWARE, weight=BOLD)
        ddb_detail = VGroup(
            Text("Persistent NoSQL  ·  survives restarts  ·  queryable",
                 font_size=16, color=TEXT_MUTED),
            Text("match_id + record_type (META / TAG#1 / TAG#2 ...)"
                 "  ·  25 recent matches retained",
                 font_size=14, color=TEXT_DIM),
        ).arrange(DOWN, buff=0.06, aligned_edge=LEFT)
        ddb_content = VGroup(ddb_title, ddb_detail).arrange(
            DOWN, buff=0.12, aligned_edge=LEFT)
        ddb_content.move_to(ddb_box).shift(LEFT * 0.3)
        ddb_lbl = Text("10–50 ms", font_size=18, color=ACCENT_HARDWARE,
                        weight=BOLD)
        ddb_lbl.next_to(ddb_box, RIGHT, buff=0.2)
        ddb_tier = VGroup(ddb_box, ddb_content, ddb_lbl)

        # --- S3 (Cold) ---
        s3_box = RoundedRectangle(
            corner_radius=0.15, width=tier_w, height=tier_h,
            stroke_color=ACCENT_STORAGE, stroke_width=2,
            fill_color=PANEL_FILL, fill_opacity=0.95,
        )
        s3_title = Text("S3 — Cold Tier", font_size=24,
                        color=ACCENT_STORAGE, weight=BOLD)
        s3_detail = VGroup(
            Text("Object storage  ·  cheap  ·  indefinite retention",
                 font_size=16, color=TEXT_MUTED),
            Text("replays/YYYY/MM/{match_id}.ndjson.gz"
                 "  ·  ddb-archive/{match_id}.json.gz",
                 font_size=14, color=TEXT_DIM),
        ).arrange(DOWN, buff=0.06, aligned_edge=LEFT)
        s3_content = VGroup(s3_title, s3_detail).arrange(
            DOWN, buff=0.12, aligned_edge=LEFT)
        s3_content.move_to(s3_box).shift(LEFT * 0.3)
        s3_lbl = Text("50–200 ms", font_size=18, color=ACCENT_STORAGE,
                       weight=BOLD)
        s3_lbl.next_to(s3_box, RIGHT, buff=0.2)
        s3_tier = VGroup(s3_box, s3_content, s3_lbl)

        # Stack vertically
        tiers = VGroup(redis_tier, ddb_tier, s3_tier).arrange(
            DOWN, buff=0.30)
        tiers.next_to(title, DOWN, buff=0.40)
        if tiers.get_bottom()[1] < -3.7:
            tiers.scale_to_fit_height(6.2).next_to(title, DOWN, buff=0.35)

        # ── Animate tiers appearing ───────────────────────────────────────
        self.play(FadeIn(redis_tier, shift=RIGHT * 0.2), run_time=0.6)
        self.wait(0.3)
        self.play(FadeIn(ddb_tier, shift=RIGHT * 0.2), run_time=0.6)
        self.wait(0.3)
        self.play(FadeIn(s3_tier, shift=RIGHT * 0.2), run_time=0.6)
        self.wait(0.5)

        # ── Down arrows between tiers + sidecar label ─────────────────────
        arr_kw = dict(buff=0.06, stroke_width=4,
                      max_tip_length_to_length_ratio=0.12)
        a_r2d = Arrow(redis_box.get_bottom(), ddb_box.get_top(),
                      color=ACCENT_HARDWARE, **arr_kw)
        a_d2s = Arrow(ddb_box.get_bottom(), s3_box.get_top(),
                      color=ACCENT_STORAGE, **arr_kw)

        sidecar_lbl = Text("sidecar.py (BRPOP)", font_size=15,
                           color=TEXT_MUTED, slant=ITALIC)
        sidecar_lbl.next_to(a_r2d, LEFT, buff=0.12)

        evict_lbl = Text("eviction after 25 matches", font_size=15,
                         color=TEXT_MUTED, slant=ITALIC)
        evict_lbl.next_to(a_d2s, LEFT, buff=0.12)

        self.play(GrowArrow(a_r2d), FadeIn(sidecar_lbl), run_time=0.5)
        self.play(GrowArrow(a_d2s), FadeIn(evict_lbl), run_time=0.5)
        self.wait(2.5)

        self.play(FadeOut(VGroup(
            title, redis_tier, ddb_tier, s3_tier,
            a_r2d, a_d2s, sidecar_lbl, evict_lbl,
        )), run_time=0.8)


# ═══════════════════════════════════════════════════════════════════════════
# T4 Pipeline Batching — before/after with concrete numbers
# ═══════════════════════════════════════════════════════════════════════════

class T4BatchingScene(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND

        title = Text("T4 Optimisation — Pipeline Batching", font_size=40,
                     color=PYNQ_RED, weight=BOLD)
        title.to_edge(UP, buff=0.35)
        self.play(Write(title), run_time=0.8)

        # ── Layout: Before on the left, After on the right ────────────────
        divider = DashedLine([0, -3.5, 0], [0, 2.5, 0],
                             stroke_color="#1A3050", stroke_width=1.5,
                             dash_length=0.15)

        before_hdr = Text("Before: N round-trips", font_size=22,
                          color=ACCENT_ALERT, weight=BOLD)
        before_hdr.move_to(LEFT * 3.5 + UP * 2.1)
        after_hdr = Text("After: 1 pipeline call", font_size=22,
                         color=HIT_COLOR, weight=BOLD)
        after_hdr.move_to(RIGHT * 3.5 + UP * 2.1)

        self.play(Create(divider), FadeIn(before_hdr), FadeIn(after_hdr),
                  run_time=0.5)

        # ── Before side: N separate HSET calls ────────────────────────────
        redis_icon_l = RoundedRectangle(
            corner_radius=0.12, width=1.6, height=0.7,
            stroke_color=ACCENT_ALERT, stroke_width=2,
            fill_color=PANEL_FILL, fill_opacity=0.95,
        ).move_to(LEFT * 2.0 + DOWN * 0.2)
        redis_txt_l = Text("Redis", font_size=18, color=ACCENT_ALERT,
                           weight=BOLD).move_to(redis_icon_l)
        self.play(FadeIn(VGroup(redis_icon_l, redis_txt_l)), run_time=0.3)

        # Animate N separate calls
        hset_arrows = VGroup()
        hset_labels = VGroup()
        t4_pos_l = LEFT * 5.5 + DOWN * 0.2
        t4_dot_l = Dot(t4_pos_l, radius=0.12, color=ACCENT_ALERT)
        t4_lbl_l = Text("T4", font_size=16, color=ACCENT_ALERT,
                         weight=BOLD).next_to(t4_dot_l, DOWN, buff=0.06)
        self.play(FadeIn(t4_dot_l), FadeIn(t4_lbl_l), run_time=0.2)

        for i in range(4):
            y_off = UP * (0.8 - i * 0.5)
            start = t4_pos_l + y_off + RIGHT * 0.2
            end = redis_icon_l.get_left() + y_off
            arr = Arrow(start, end, buff=0.06, stroke_width=2,
                        color=ACCENT_ALERT,
                        max_tip_length_to_length_ratio=0.15)
            lbl = Text(f"HSET player:{i+1}", font_size=12,
                       color=TEXT_DIM)
            lbl.next_to(arr, UP, buff=0.02)
            hset_arrows.add(arr)
            hset_labels.add(lbl)
            self.play(GrowArrow(arr), FadeIn(lbl), run_time=0.18)

        # "..." to indicate more
        dots_l = Text("... N calls", font_size=14,
                      color=TEXT_DIM).next_to(hset_arrows, DOWN, buff=0.15)
        self.play(FadeIn(dots_l), run_time=0.2)

        # Latency label
        lat_before = Text("O(N) round-trips per tick", font_size=16,
                          color=ACCENT_ALERT)
        lat_before.next_to(redis_icon_l, DOWN, buff=0.6)
        self.play(FadeIn(lat_before), run_time=0.3)
        self.wait(0.8)

        # ── After side: drain queue then 1 pipeline ───────────────────────
        redis_icon_r = RoundedRectangle(
            corner_radius=0.12, width=1.6, height=0.7,
            stroke_color=HIT_COLOR, stroke_width=2,
            fill_color=PANEL_FILL, fill_opacity=0.95,
        ).move_to(RIGHT * 5.0 + DOWN * 0.2)
        redis_txt_r = Text("Redis", font_size=18, color=HIT_COLOR,
                           weight=BOLD).move_to(redis_icon_r)

        # Queue box
        q_box = RoundedRectangle(
            corner_radius=0.10, width=1.8, height=0.65,
            stroke_color=TEXT_MUTED, stroke_width=1.5,
            fill_color="#0C1A2C", fill_opacity=0.90,
        ).move_to(RIGHT * 2.0 + DOWN * 0.2)
        q_lbl = Text("WriteQueue", font_size=13,
                      color=TEXT_MUTED).move_to(q_box)

        t4_pos_r = RIGHT * 1.0 + DOWN * 0.2
        t4_dot_r = Dot(t4_pos_r, radius=0.12, color=HIT_COLOR)
        t4_lbl_r = Text("T4", font_size=16, color=HIT_COLOR,
                         weight=BOLD).next_to(t4_dot_r, DOWN, buff=0.06)

        self.play(FadeIn(t4_dot_r), FadeIn(t4_lbl_r),
                  FadeIn(VGroup(q_box, q_lbl)),
                  FadeIn(VGroup(redis_icon_r, redis_txt_r)),
                  run_time=0.4)

        # Step 1: drain queue
        drain_arr = Arrow(q_box.get_left(), t4_dot_r.get_right(),
                          buff=0.08, stroke_width=3, color=HIT_COLOR,
                          max_tip_length_to_length_ratio=0.14)
        drain_lbl = Text("drain all", font_size=13,
                         color=TEXT_MUTED).next_to(drain_arr, UP, buff=0.04)
        self.play(GrowArrow(drain_arr), FadeIn(drain_lbl), run_time=0.3)

        # Step 2: one fat pipeline call
        pipe_arr = Arrow(q_box.get_right(), redis_icon_r.get_left(),
                         buff=0.08, stroke_width=5, color=HIT_COLOR,
                         max_tip_length_to_length_ratio=0.12)
        pipe_lbl = Text("1 pipeline()", font_size=14, color=HIT_COLOR,
                         weight=BOLD)
        pipe_lbl.next_to(pipe_arr, UP, buff=0.06)
        self.play(GrowArrow(pipe_arr), FadeIn(pipe_lbl), run_time=0.4)

        lat_after = Text("O(1) round-trip per tick", font_size=16,
                         color=HIT_COLOR)
        lat_after.next_to(redis_icon_r, DOWN, buff=0.6)
        self.play(FadeIn(lat_after), run_time=0.3)
        self.wait(1.0)

        # ── Concrete numbers table ────────────────────────────────────────
        table_data = [
            ("",                "2 players\nlocalhost", "2 players\nElastiCache", "10 players\nElastiCache"),
            ("Old (N trips)",   "~0.1 ms",              "~1 ms",                   "~5 ms"),
            ("New (1 pipe)",    "~0.05 ms",             "~0.5 ms",                 "~0.5 ms"),
        ]

        cells = VGroup()
        cell_w, cell_h = 2.2, 0.7
        for ri, row in enumerate(table_data):
            for ci, val in enumerate(row):
                bg_color = PANEL_FILL
                if ri == 0:
                    txt_color = TEXT_PRIMARY
                    fw = BOLD
                elif ri == 1:
                    txt_color = ACCENT_ALERT
                    fw = NORMAL
                else:
                    txt_color = HIT_COLOR
                    fw = BOLD
                rect = Rectangle(
                    width=cell_w, height=cell_h,
                    stroke_color="#2A4060", stroke_width=1,
                    fill_color=bg_color, fill_opacity=0.90,
                )
                txt = Text(val, font_size=14, color=txt_color, weight=fw)
                txt.move_to(rect)
                cell = VGroup(rect, txt)
                cell.move_to([
                    (ci - 1.5) * cell_w,
                    -(ri - 1) * cell_h,
                    0,
                ])
                cells.add(cell)

        cells.move_to(DOWN * 2.6)
        if cells.get_width() > 12.5:
            cells.scale_to_fit_width(12.5)

        self.play(FadeIn(cells, lag_ratio=0.02), run_time=0.8)
        self.wait(3.0)

        self.play(FadeOut(VGroup(
            title, divider, before_hdr, after_hdr,
            redis_icon_l, redis_txt_l, t4_dot_l, t4_lbl_l,
            hset_arrows, hset_labels, dots_l, lat_before,
            redis_icon_r, redis_txt_r, t4_dot_r, t4_lbl_r,
            q_box, q_lbl, drain_arr, drain_lbl,
            pipe_arr, pipe_lbl, lat_after,
            cells,
        )), run_time=0.8)


# ═══════════════════════════════════════════════════════════════════════════
# Packet Protocol — 24-byte fixed binary frame
# ═══════════════════════════════════════════════════════════════════════════

class PacketProtocolScene(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND

        title = Text("UDP Packet Protocol — 24-Byte Fixed Frame",
                     font_size=38, color=PYNQ_RED, weight=BOLD)
        title.to_edge(UP, buff=0.35)
        self.play(Write(title), run_time=0.8)

        # ── Packet field definitions ──────────────────────────────────────
        # (name, type, bytes, colour)
        fields = [
            ("node_id", "u16",  2, "#FF6B6B"),   # red - identity
            ("seq",     "u16",  2, "#FF6B6B"),
            ("tick",    "u32",  4, "#F7A541"),   # orange - timing
            ("x",       "f32",  4, "#58C4DD"),   # cyan - position
            ("y",       "f32",  4, "#58C4DD"),
            ("angle",   "f32",  4, "#58C4DD"),
            ("flags",   "u8",   1, "#7BD88F"),   # green - state
            ("pad",     "3B",   3, "#5A6A7A"),   # grey - alignment
        ]

        total_bytes = sum(f[2] for f in fields)

        # ── Build the byte-strip diagram ──────────────────────────────────
        strip_w = 11.0
        strip_h = 0.9
        strip_y = 1.3
        px_per_byte = strip_w / total_bytes

        field_rects = VGroup()
        field_labels = VGroup()
        type_labels = VGroup()
        byte_offsets = VGroup()

        x_cursor = -strip_w / 2
        byte_cursor = 0

        for name, dtype, nbytes, color in fields:
            w = px_per_byte * nbytes
            rect = Rectangle(
                width=w, height=strip_h,
                fill_color=color, fill_opacity=0.25,
                stroke_color=color, stroke_width=2,
            )
            rect.move_to([x_cursor + w / 2, strip_y, 0])

            nlbl = Text(name, font_size=15, color=WHITE, weight=BOLD)
            nlbl.move_to(rect.get_center() + UP * 0.12)
            tlbl = Text(dtype, font_size=12, color=color)
            tlbl.move_to(rect.get_center() + DOWN * 0.18)

            # Byte offset marker at the left edge
            off = Text(str(byte_cursor), font_size=11, color=TEXT_DIM)
            off.move_to([x_cursor, strip_y + strip_h / 2 + 0.18, 0])

            field_rects.add(rect)
            field_labels.add(nlbl)
            type_labels.add(tlbl)
            byte_offsets.add(off)

            x_cursor += w
            byte_cursor += nbytes

        # Final byte offset (24)
        off_end = Text(str(total_bytes), font_size=11, color=TEXT_DIM)
        off_end.move_to([x_cursor, strip_y + strip_h / 2 + 0.18, 0])
        byte_offsets.add(off_end)

        # Group labels for the field categories
        cat_id = Text("Identity", font_size=14, color="#FF6B6B")
        cat_id.move_to([-strip_w / 2 + px_per_byte * 2, strip_y - 0.7, 0])
        cat_time = Text("Timing", font_size=14, color="#F7A541")
        cat_time.move_to([-strip_w / 2 + px_per_byte * 6, strip_y - 0.7, 0])
        cat_pos = Text("Position + Rotation", font_size=14, color="#58C4DD")
        cat_pos.move_to([px_per_byte * 2, strip_y - 0.7, 0])
        cat_state = Text("State", font_size=14, color="#7BD88F")
        cat_state.move_to([strip_w / 2 - px_per_byte * 3, strip_y - 0.7, 0])

        # ── Animate packet building field by field ────────────────────────
        self.play(FadeIn(byte_offsets, lag_ratio=0.05), run_time=0.4)
        for i in range(len(fields)):
            self.play(
                FadeIn(field_rects[i], scale=0.9),
                FadeIn(field_labels[i]),
                FadeIn(type_labels[i]),
                run_time=0.18,
            )
        self.play(
            FadeIn(cat_id), FadeIn(cat_time),
            FadeIn(cat_pos), FadeIn(cat_state),
            run_time=0.5,
        )
        self.wait(0.8)

        # ── struct.pack line ──────────────────────────────────────────────
        code_bg = RoundedRectangle(
            corner_radius=0.10, width=11.5, height=0.65,
            fill_color="#0D1B2A", fill_opacity=0.95,
            stroke_color="#2A4060", stroke_width=1.5,
        ).move_to([0, -0.2, 0])
        code_txt = Text(
            "struct.pack('<HHIfffB3x', node_id, seq, tick, x, y, angle, flags)",
            font_size=16, color=TEXT_PRIMARY,
        )
        code_txt.move_to(code_bg)
        self.play(FadeIn(code_bg), FadeIn(code_txt), run_time=0.5)
        self.wait(0.8)

        # ── Animate packet flying: PYNQ → EC2 → all PYNQs ───────────────
        pynq_box = RoundedRectangle(
            corner_radius=0.10, width=1.8, height=0.7,
            stroke_color=ACCENT_HARDWARE, stroke_width=2,
            fill_color=PANEL_FILL, fill_opacity=0.95,
        ).move_to(LEFT * 4.5 + DOWN * 2.2)
        pynq_txt = Text("PYNQ", font_size=16, color=ACCENT_HARDWARE,
                        weight=BOLD).move_to(pynq_box)

        ec2_box = RoundedRectangle(
            corner_radius=0.10, width=1.8, height=0.7,
            stroke_color=ACCENT_SERVER, stroke_width=2,
            fill_color=PANEL_FILL, fill_opacity=0.95,
        ).move_to(DOWN * 2.2)
        ec2_txt = Text("EC2 Server", font_size=14, color=ACCENT_SERVER,
                       weight=BOLD).move_to(ec2_box)

        pynqs_box = RoundedRectangle(
            corner_radius=0.10, width=2.2, height=0.7,
            stroke_color=ACCENT_HARDWARE, stroke_width=2,
            fill_color=PANEL_FILL, fill_opacity=0.95,
        ).move_to(RIGHT * 4.5 + DOWN * 2.2)
        pynqs_txt = Text("All PYNQs", font_size=14,
                         color=ACCENT_HARDWARE,
                         weight=BOLD).move_to(pynqs_box)

        self.play(
            FadeIn(pynq_box), FadeIn(pynq_txt),
            FadeIn(ec2_box), FadeIn(ec2_txt),
            FadeIn(pynqs_box), FadeIn(pynqs_txt),
            run_time=0.4,
        )

        # Packet dot flies
        pkt = Dot(radius=0.10, color=ACCENT_HARDWARE, z_index=15)
        pkt_lbl = Text("24B", font_size=12, color=ACCENT_HARDWARE)
        pkt_grp = VGroup(pkt, pkt_lbl).arrange(DOWN, buff=0.03)
        pkt_grp.move_to(pynq_box.get_right() + RIGHT * 0.2)

        arr1 = Arrow(pynq_box.get_right(), ec2_box.get_left(),
                     buff=0.08, stroke_width=3, color=ACCENT_HARDWARE,
                     max_tip_length_to_length_ratio=0.14)
        arr2 = Arrow(ec2_box.get_right(), pynqs_box.get_left(),
                     buff=0.08, stroke_width=3, color=ACCENT_SERVER,
                     max_tip_length_to_length_ratio=0.14)

        udp_lbl1 = Text("UDP", font_size=13, color=TEXT_MUTED)
        udp_lbl1.next_to(arr1, UP, buff=0.04)
        udp_lbl2 = Text("UDP broadcast", font_size=13, color=TEXT_MUTED)
        udp_lbl2.next_to(arr2, UP, buff=0.04)

        self.play(GrowArrow(arr1), FadeIn(udp_lbl1), run_time=0.3)
        self.play(FadeIn(pkt_grp), run_time=0.2)
        self.play(pkt_grp.animate.move_to(ec2_box), run_time=0.35)
        self.play(GrowArrow(arr2), FadeIn(udp_lbl2), run_time=0.3)
        self.play(pkt_grp.animate.move_to(pynqs_box), run_time=0.35)
        self.play(FadeOut(pkt_grp), run_time=0.2)
        self.wait(0.5)

        # ── Why UDP callout ───────────────────────────────────────────────
        why_box = RoundedRectangle(
            corner_radius=0.10, width=10.0, height=1.1,
            fill_color=PANEL_FILL, fill_opacity=0.96,
            stroke_color=ACCENT_SERVER, stroke_width=1.5,
        ).to_edge(DOWN, buff=0.08)
        why_txt = VGroup(
            Text("Why UDP?  At 30 Hz, a stale packet is useless — "
                 "the next one has fresher data.",
                 font_size=16, color=TEXT_PRIMARY),
            Text("Fixed 24B frame: O(1) decode, zero parsing overhead. "
                 "Seq number detects out-of-order / duplicates.",
                 font_size=15, color=TEXT_MUTED),
        ).arrange(DOWN, buff=0.06, aligned_edge=LEFT)
        why_txt.move_to(why_box)
        self.play(FadeIn(VGroup(why_box, why_txt)), run_time=0.5)
        self.wait(3.0)

        self.play(FadeOut(VGroup(
            title, field_rects, field_labels, type_labels, byte_offsets,
            cat_id, cat_time, cat_pos, cat_state,
            code_bg, code_txt,
            pynq_box, pynq_txt, ec2_box, ec2_txt, pynqs_box, pynqs_txt,
            arr1, arr2, udp_lbl1, udp_lbl2,
            why_box, why_txt,
        )), run_time=0.8)


# ═══════════════════════════════════════════════════════════════════════════
# Map Hot-Swap — live map change mid-session
# ═══════════════════════════════════════════════════════════════════════════

class MapHotSwapScene(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND

        title = Text("Live Map Hot-Swap", font_size=40,
                     color=PYNQ_RED, weight=BOLD)
        title.to_edge(UP, buff=0.35)
        self.play(Write(title), run_time=0.8)

        subtitle = Text(
            "Change the map mid-session — no reboot, no overlay reload",
            font_size=22, color=TEXT_MUTED,
        )
        subtitle.next_to(title, DOWN, buff=0.20)
        self.play(FadeIn(subtitle, shift=UP * 0.1), run_time=0.4)

        # ── Flow diagram: Monitor → Redis → Server → PKT_MAP → Boards → BRAM → HDMI
        flow_data = [
            ("Monitor\nEditor",      "#FF6B6B"),
            ("Redis\nPub/Sub",       "#E02020"),
            ("t2_game\n_tick.py",    ACCENT_SERVER),
            ("PKT_MAP\n→ UDP",       ACCENT_HARDWARE),
            ("pynq_\nclient.py",     ACCENT_HARDWARE),
            ("MMIO →\nBRAM",         "#F7A541"),
            ("PL\nRaycaster",        PYNQ_RED),
            ("HDMI",                 PYNQ_RED),
        ]

        flow_boxes = VGroup()
        for label, color in flow_data:
            box = RoundedRectangle(
                corner_radius=0.08, width=1.35, height=0.85,
                stroke_color=color, stroke_width=1.8,
                fill_color=PANEL_FILL, fill_opacity=0.95,
            )
            txt = Text(label, font_size=12, color=color, weight=BOLD)
            txt.move_to(box)
            flow_boxes.add(VGroup(box, txt))
        flow_boxes.arrange(RIGHT, buff=0.20).move_to(UP * 0.6)
        if flow_boxes.get_width() > 13.0:
            flow_boxes.scale_to_fit_width(13.0)

        flow_arrows = VGroup()
        for i in range(len(flow_boxes) - 1):
            flow_arrows.add(Arrow(
                flow_boxes[i].get_right(), flow_boxes[i + 1].get_left(),
                buff=0.04, stroke_width=2.5, color=TEXT_MUTED,
                max_tip_length_to_length_ratio=0.18,
            ))

        self.play(
            LaggedStart(
                *[FadeIn(b, shift=RIGHT * 0.1) for b in flow_boxes],
                lag_ratio=0.08,
            ),
            run_time=1.0,
        )
        self.play(FadeIn(flow_arrows, lag_ratio=0.1), run_time=0.6)
        self.wait(0.8)

        # ── Animate map morphing: old grid → new grid ─────────────────────
        cell_s = 0.28
        grid_n = 8  # 8x8 for visual simplicity

        map_old = [
            [1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,1],
            [1,0,1,1,0,0,0,1],
            [1,0,1,0,0,1,0,1],
            [1,0,0,0,0,1,0,1],
            [1,0,0,0,0,0,0,1],
            [1,0,0,1,0,0,0,1],
            [1,1,1,1,1,1,1,1],
        ]

        map_new = [
            [1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,1],
            [1,0,0,0,0,1,0,1],
            [1,0,0,1,0,1,0,1],
            [1,0,0,1,0,0,0,1],
            [1,0,0,0,0,0,1,1],
            [1,0,0,0,0,0,0,1],
            [1,1,1,1,1,1,1,1],
        ]

        grid_cx = -3.0
        grid_cy = -1.8

        def build_grid(world_map, cx, cy, opacity=0.9):
            g = VGroup()
            for r in range(grid_n):
                for c in range(grid_n):
                    sq = Square(side_length=cell_s, stroke_width=0.6,
                                stroke_color=GRID_COLOR)
                    if world_map[r][c]:
                        sq.set_fill(WALL_COLOR, opacity=opacity)
                    else:
                        sq.set_fill(EMPTY_COLOR, opacity=0.3)
                    sq.move_to([
                        cx + (c - grid_n / 2 + 0.5) * cell_s,
                        cy + (grid_n / 2 - r - 0.5) * cell_s,
                        0,
                    ])
                    g.add(sq)
            return g

        old_grid = build_grid(map_old, grid_cx, grid_cy)
        old_lbl = Text("Current Map", font_size=18, color=TEXT_MUTED)
        old_lbl.next_to(old_grid, UP, buff=0.15)

        self.play(FadeIn(old_grid, lag_ratio=0.005), FadeIn(old_lbl),
                  run_time=0.6)
        self.wait(0.5)

        # PKT_MAP packet flying from flow to grid
        pkt_dot = Dot(radius=0.08, color=ACCENT_HARDWARE, z_index=15)
        pkt_label = Text("PKT_MAP", font_size=11, color=ACCENT_HARDWARE)
        pkt_g = VGroup(pkt_dot, pkt_label).arrange(DOWN, buff=0.03)
        pkt_g.move_to(flow_boxes[3])

        self.play(FadeIn(pkt_g, scale=0.5), run_time=0.2)
        self.play(pkt_g.animate.move_to(old_grid.get_center() + UP * 0.5),
                  run_time=0.5)
        self.play(FadeOut(pkt_g), run_time=0.2)

        # Morph old grid to new grid
        new_grid = build_grid(map_new, grid_cx, grid_cy)
        new_lbl = Text("New Map — live!", font_size=18,
                        color=HIT_COLOR, weight=BOLD)
        new_lbl.next_to(new_grid, UP, buff=0.15)

        self.play(
            *[Transform(old_grid[i], new_grid[i])
              for i in range(len(old_grid))],
            Transform(old_lbl, new_lbl),
            run_time=1.0,
        )
        self.wait(0.5)

        # Show the same thing on a second "board" to show broadcast
        grid2_cx = 3.0
        new_grid2 = build_grid(map_new, grid2_cx, grid_cy)
        board2_lbl = Text("Board B — same map", font_size=18,
                          color=HIT_COLOR)
        board2_lbl.next_to(new_grid2, UP, buff=0.15)

        self.play(FadeIn(new_grid2, lag_ratio=0.005),
                  FadeIn(board2_lbl), run_time=0.6)
        self.wait(0.5)

        # ── Packet details callout ────────────────────────────────────────
        detail_box = RoundedRectangle(
            corner_radius=0.10, width=12.5, height=1.2,
            fill_color=PANEL_FILL, fill_opacity=0.96,
            stroke_color=ACCENT_SERVER, stroke_width=1.5,
        ).to_edge(DOWN, buff=0.08)
        detail_txt = VGroup(
            Text("PKT_MAP: 8B header + 128B payload "
                 "(32×32 grid, 1 bit per cell, row-major)",
                 font_size=16, color=TEXT_PRIMARY),
            Text("BRAM write is immediate — PL raycaster sees "
                 "the new map on the very next frame",
                 font_size=15, color=TEXT_MUTED),
            Text("Broadcast to ALL boards simultaneously — "
                 "everyone sees the same walls at the same time",
                 font_size=15, color=HIT_COLOR),
        ).arrange(DOWN, buff=0.06, aligned_edge=LEFT)
        detail_txt.move_to(detail_box)
        self.play(FadeIn(VGroup(detail_box, detail_txt)), run_time=0.5)
        self.wait(3.0)

        self.play(FadeOut(VGroup(
            title, subtitle,
            flow_boxes, flow_arrows,
            old_grid, old_lbl, new_grid2, board2_lbl,
            detail_box, detail_txt,
        )), run_time=0.8)


class PipelineScene(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND

        section = Text("7. The Full Pipeline", font_size=42, color=PYNQ_RED, weight=BOLD)
        section.to_edge(UP, buff=0.4)
        self.play(Write(section), run_time=0.8)

        box_style = {"fill_opacity": 0.18, "stroke_width": 2, "corner_radius": 0.15}
        labels_text = [
            ("Scene Data\n(S3 / DynamoDB)", GREY_A),
            ("Server\nOrchestrator",        "#4A9EFF"),
            ("FPGA Node\n(DDA Raycaster)",  PYNQ_RED),
            ("Tile\nAggregator",            "#FFAA33"),
            ("Web\nDashboard",              "#4ADB7A"),
        ]

        boxes = []
        for text_value, color in labels_text:
            box   = RoundedRectangle(width=2.3, height=1.4, stroke_color=color, fill_color=color, **box_style)
            label = Text(text_value, font_size=19, color=WHITE)
            label.move_to(box.get_center())
            boxes.append(VGroup(box, label))

        flow = VGroup(*boxes).arrange(RIGHT, buff=0.38).shift(DOWN * 0.2)
        if flow.get_width() > 12.5:
            flow.scale_to_fit_width(12.5)

        for box in boxes:
            self.play(FadeIn(box, scale=0.9), run_time=0.38)

        arrows = VGroup()
        for index in range(len(boxes) - 1):
            arrows.add(Arrow(
                boxes[index].get_right(), boxes[index + 1].get_left(),
                buff=0.1, color=TEXT_MUTED, stroke_width=2.5,
                max_tip_length_to_length_ratio=0.15,
            ))
        self.play(FadeIn(arrows, lag_ratio=0.2), run_time=1)
        self.wait(2.8)
        self.play(FadeOut(VGroup(section, flow, arrows)), run_time=0.8)

        # Outro card
        final   = Text("PYNQ CAST", font_size=64, weight=BOLD, color=PYNQ_RED)
        tagline = Text("Distributed FPGA Raycasting — embarrassingly parallel", font_size=28, color=TEXT_MUTED)
        tagline.next_to(final, DOWN, buff=0.45)
        self.play(Write(final), run_time=1.1)
        self.play(FadeIn(tagline, shift=UP * 0.2), run_time=0.9)
        self.wait(3.0)
        self.play(FadeOut(VGroup(final, tagline)), run_time=0.8)