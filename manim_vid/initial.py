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
        grid_group = make_world_grid(world_map, cell_size=0.65)
        grid_group.shift(DOWN * 0.25)

        self.play(FadeIn(grid_group, lag_ratio=0.01), run_time=1.4)
        self.wait(0.4)

        wall_swatch  = Square(0.3,  stroke_width=0).set_fill(WALL_COLOR,  opacity=0.92)
        empty_swatch = Square(0.3,  stroke_width=0).set_fill(EMPTY_COLOR, opacity=0.85)
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

        player_world = grid_cell_center(grid_group, 5, 2, map_cols)
        player_dot   = Dot(player_world, radius=0.13, color=PLAYER_A_COLOR, z_index=5)
        player_label = Text("Player", font_size=20, color=PLAYER_A_COLOR)
        player_label.next_to(player_dot, LEFT, buff=0.22)

        self.play(FadeIn(player_dot, scale=0.5), FadeIn(player_label), run_time=0.7)
        self.wait(2.2)
        self.play(FadeOut(VGroup(section, grid_group, legend, bram_text, player_dot, player_label)), run_time=0.8)


class DDAScene(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND

        section = Text("2. Casting Rays — DDA Algorithm", font_size=42, color=PYNQ_RED, weight=BOLD)
        section.to_edge(UP, buff=0.4)
        self.play(Write(section), run_time=0.8)

        world_map = ALGO_WORLD_MAP
        map_rows  = len(world_map)
        map_cols  = len(world_map[0])
        cell_size = 0.55
        grid_group = make_world_grid(world_map, cell_size=cell_size, empty_opacity=0.42)
        grid_group.shift(LEFT * 2.2 + DOWN * 0.3)

        self.play(FadeIn(grid_group, lag_ratio=0.005), run_time=0.8)

        player_world = grid_cell_center(grid_group, 5, 2, map_cols)
        player_dot   = Dot(player_world, radius=0.11, color=PLAYER_A_COLOR, z_index=5)
        self.play(FadeIn(player_dot, scale=0.5), run_time=0.5)

        fov_angle  = 60
        player_dir = 30
        fov_half   = fov_angle / 2
        ray_length = 3.5

        dir_rad       = np.radians(player_dir)
        fov_left_rad  = np.radians(player_dir + fov_half)
        fov_right_rad = np.radians(player_dir - fov_half)

        fov_left_end  = player_world + ray_length * np.array([np.cos(fov_left_rad),  np.sin(fov_left_rad),  0])
        fov_right_end = player_world + ray_length * np.array([np.cos(fov_right_rad), np.sin(fov_right_rad), 0])

        fov_left_line  = DashedLine(player_world, fov_left_end,  color=FOV_COLOR, dash_length=0.1, stroke_width=2)
        fov_right_line = DashedLine(player_world, fov_right_end, color=FOV_COLOR, dash_length=0.1, stroke_width=2)
        fov_label = Text("60° FOV", font_size=22, color=FOV_COLOR)
        fov_label.move_to(player_world + 1.6 * np.array([np.cos(dir_rad), np.sin(dir_rad), 0]) + UP * 0.22)

        self.play(Create(fov_left_line), Create(fov_right_line), FadeIn(fov_label), run_time=1)

        # Right-side explanation panel
        dda_steps = VGroup(
            Text("DDA steps per ray:",   font_size=24, color=TEXT_PRIMARY, weight=BOLD),
            Text("1. For each screen column,",         font_size=21, color=TEXT_MUTED),
            Text("   cast a ray from the player",      font_size=21, color=TEXT_MUTED),
            Text("2. Step through grid cells",         font_size=21, color=TEXT_MUTED),
            Text("   one boundary at a time",          font_size=21, color=TEXT_MUTED),
            Text("3. Stop when a wall is hit",         font_size=21, color=TEXT_MUTED),
            Text("4. Use perpendicular distance",      font_size=21, color=TEXT_MUTED),
            Text("   to prevent fisheye distortion",   font_size=21, color=TEXT_MUTED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        dda_steps.to_edge(RIGHT, buff=0.45).shift(DOWN * 0.2)
        self.play(FadeIn(dda_steps, lag_ratio=0.08), run_time=1.8)

        # Cast rays
        num_rays   = 7
        ray_angles = np.linspace(player_dir + fov_half, player_dir - fov_half, num_rays)
        ray_draws  = VGroup()
        hit_draws  = VGroup()

        for index, angle_deg in enumerate(ray_angles):
            angle_rad = np.radians(angle_deg)
            ray_dir   = np.array([np.cos(angle_rad), np.sin(angle_rad), 0])
            hit_pos   = None

            for step in range(1, 220):
                pos = player_world + ray_dir * 0.05 * step
                row, col = point_to_grid_cell(pos, grid_group, map_rows, map_cols, cell_size)
                if 0 <= row < map_rows and 0 <= col < map_cols:
                    if world_map[row][col] == 1:
                        hit_pos = pos
                        break
                else:
                    hit_pos = pos
                    break

            if hit_pos is None:
                continue

            is_centre = (index == 3)
            ray_line = Line(
                player_world, hit_pos,
                color=PYNQ_RED if is_centre else RAY_COLOR,
                stroke_width=3.0 if is_centre else 1.8,
                stroke_opacity=1.0 if is_centre else 0.55,
            )
            hit_dot = Dot(hit_pos, radius=0.07, color=HIT_COLOR, z_index=5)
            ray_draws.add(ray_line)
            hit_draws.add(hit_dot)

            if is_centre:
                self.play(Create(ray_line), run_time=0.6)
                self.play(FadeIn(hit_dot, scale=0.5), run_time=0.3)
            else:
                self.play(Create(ray_line), FadeIn(hit_dot, scale=0.5), run_time=0.22)

        self.wait(2.2)
        self.play(FadeOut(VGroup(
            section, grid_group, player_dot,
            fov_left_line, fov_right_line, fov_label,
            dda_steps, ray_draws, hit_draws,
        )), run_time=0.8)


class WallRenderScene(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND
 
        section = Text("3. Distance  →  Wall Height", font_size=40,
                       color=PYNQ_RED, weight=BOLD)
        section.to_edge(UP, buff=0.35)
        self.play(Write(section), run_time=0.8)
 
        # ==================================================================
        # LAYOUT
        # ==================================================================
        # Divider and headers — defined now, shown in Phase 2 only
        divider = DashedLine([0.5, -3.8, 0], [0.5, 3.2, 0],
                            stroke_color="#1A3050", stroke_width=1.5,
                            dash_length=0.15)
        lhdr = Text("Top-Down View", font_size=21,
                    color=TEXT_MUTED).move_to([-3.0, 2.85, 0])
        rhdr = Text("Screen Output", font_size=21,
                    color=TEXT_MUTED).move_to([4.2, 2.85, 0])
 
        # ==================================================================
        # PHASE 1 — Lodev perpWallDist diagram  (left half, x ∈ [-7, 0.5])
        # ==================================================================
 
        # ── Grid ──────────────────────────────────────────────────────────
        grid_rows, grid_cols = 8, 9
        cs = 0.62
        grid_ox = -2.8   # centered on screen
        grid_oy = 2.45   # top  edge of grid
 
        def g2s(r, c):
            """Grid cell (row, col) → scene centre."""
            return np.array([grid_ox + (c + 0.5) * cs,
                             grid_oy - (r + 0.5) * cs, 0])
 
        # Wall cells: top row, columns 2-4 and 6-7
        wall_map = [[0]*grid_cols for _ in range(grid_rows)]
        for c in [2, 3, 4, 5, 6, 7]:
            wall_map[0][c] = 1
 
        grid_group = VGroup()
        for r in range(grid_rows):
            for c in range(grid_cols):
                sq = Square(side_length=cs, stroke_width=0.7,
                            stroke_color=LODEV_GRID, stroke_opacity=0.30)
                if wall_map[r][c]:
                    sq.set_fill(LODEV_WALL_BLUE, opacity=0.80)
                else:
                    sq.set_fill(EMPTY_COLOR, opacity=0.10)
                sq.move_to(g2s(r, c))
                grid_group.add(sq)
        self.play(FadeIn(grid_group, lag_ratio=0.002), run_time=0.6)
 
        # ── Geometry ──────────────────────────────────────────────────────
        P = g2s(6, 1) + np.array([0.05, 0.1, 0])
 
        dir_angle = np.radians(68)
        dir_vec = np.array([np.cos(dir_angle), np.sin(dir_angle), 0])
        plane_vec = np.array([dir_vec[1], -dir_vec[0], 0]) * 0.66
 
        cam_x = 0.30
        ray_dir = dir_vec + plane_vec * cam_x
        ray_dir_u = ray_dir / np.linalg.norm(ray_dir)
 
        vs = 1.5   # visual scale for component arrows
 
        D = P + ray_dir * vs
        dir_tip = P + dir_vec * vs
        C = P + np.array([ray_dir[0] * vs, 0, 0])
 
        cpc = P + dir_vec * vs          # camera plane centre
        cp_half = plane_vec * 2.8
        cp_start = cpc - cp_half
        cp_end   = cpc + cp_half
 
        wall_y = grid_oy - cs           # bottom edge of row 0
        t_hit = (wall_y - P[1]) / ray_dir[1]
        H = P + t_hit * ray_dir
 
        B = np.array([H[0], P[1], 0])   # vertical foot
 
        pvu = plane_vec / np.linalg.norm(plane_vec)
        s_proj = np.dot(H - cpc, pvu)
        A = cpc + s_proj * pvu
 
        # ==================================================================
        # Draw with careful label placement (no single-letter point labels)
        # ==================================================================
 
        # ── Camera plane ──────────────────────────────────────────────────
        cam_plane_line = Line(cp_start, cp_end,
                              stroke_color=TEXT_PRIMARY, stroke_width=4,
                              stroke_opacity=0.80)
        cam_lbl = backed_label("camera plane", font_size=15,
                               color=TEXT_MUTED, slant=ITALIC)
        cp_label_pos = cp_start * 0.85 + cp_end * 0.15
        cam_lbl.move_to(cp_label_pos).shift(DOWN * 0.3)
        self.play(Create(cam_plane_line), FadeIn(cam_lbl), run_time=0.6)
 
        # ── Player dot ────────────────────────────────────────────────────
        player_dot = Dot(P, radius=0.15, color=LODEV_RED, z_index=10)
        self.play(FadeIn(player_dot), run_time=0.4)
 
        # ── dir arrow ─────────────────────────────────────────────────────
        dir_arrow = Arrow(P, dir_tip, buff=0, stroke_width=3.5,
                          color=LODEV_GREEN,
                          max_tip_length_to_length_ratio=0.10)
        dir_perp = np.array([-dir_vec[1], dir_vec[0], 0])
        dlbl = backed_label("dir", font_size=17, color=LODEV_GREEN,
                            weight=BOLD, slant=ITALIC)
        dlbl.move_to((P + dir_tip) / 2 + dir_perp * 0.32)
        self.play(GrowArrow(dir_arrow), FadeIn(dlbl), run_time=0.6)
 
        # ── rayDir arrow ──────────────────────────────────────────────────
        ray_arrow = Arrow(P, D, buff=0, stroke_width=3,
                          color=LODEV_RED,
                          max_tip_length_to_length_ratio=0.10)
        ray_perp = np.array([-ray_dir_u[1], ray_dir_u[0], 0])
        rdlbl = backed_label("rayDir", font_size=15, color=LODEV_RED,
                             weight=BOLD, slant=ITALIC)
        rdlbl.move_to((P + D) / 2 - ray_perp * 0.32)
        self.play(GrowArrow(ray_arrow), FadeIn(rdlbl), run_time=0.6)
 
        # ── rayDirX: P → C ───────────────────────────────────────────────
        arr_rdx = Arrow(P, C, buff=0, stroke_width=3, color=LODEV_GREEN,
                        max_tip_length_to_length_ratio=0.14)
        rdx_lbl = backed_label("rayDirX", font_size=15, color=LODEV_GREEN,
                               weight=BOLD)
        rdx_lbl.next_to(arr_rdx, DOWN, buff=0.06)
        self.play(GrowArrow(arr_rdx), FadeIn(rdx_lbl), run_time=0.5)
 
        # ── rayDirY: C → D ───────────────────────────────────────────────
        arr_rdy = Arrow(C, D, buff=0, stroke_width=3, color=LODEV_GREEN,
                        max_tip_length_to_length_ratio=0.14)
        rdy_lbl = backed_label("rayDirY", font_size=15, color=LODEV_GREEN,
                               weight=BOLD)
        rdy_lbl.next_to(arr_rdy, RIGHT, buff=0.06)
        ra_C = right_angle_mark(C, [0, 1, 0], [-1, 0, 0],
                                size=0.10, color=LODEV_RED)
        self.play(GrowArrow(arr_rdy), FadeIn(rdy_lbl), Create(ra_C),
                  run_time=0.5)
        self.wait(0.3)
 
        # ── Full ray P → H ───────────────────────────────────────────────
        ray_full = Line(P, H, stroke_color=LODEV_RED,
                        stroke_width=3.5, z_index=5)
        hit_dot = Dot(H, radius=0.11, color=LODEV_RED, z_index=10)
        self.play(Create(ray_full), FadeIn(hit_dot), run_time=0.7)
        self.wait(0.3)
 
        # ── perpWallDist: A → H ──────────────────────────────────────────
        dot_A = Dot(A, radius=0.05, color=LODEV_BLUE, z_index=8)
        perp_line = Line(A, H, stroke_color=LODEV_GREEN,
                         stroke_width=5.5, z_index=6)
        AH_vec = H - A
        AH_u = AH_vec / (np.linalg.norm(AH_vec) + 1e-12)
        AH_perp = np.array([-AH_u[1], AH_u[0], 0])
        perp_lbl = backed_label("perpWallDist", font_size=17,
                                color=LODEV_GREEN, weight=BOLD)
        perp_lbl.move_to((A + H) / 2 + AH_perp * 0.38)
        self.play(FadeIn(dot_A), Create(perp_line), FadeIn(perp_lbl),
                  run_time=0.7)
        self.wait(0.4)
 
        # ── Euclidean: dotted P → H ──────────────────────────────────────
        euc_line = DashedLine(P, H, stroke_color=TEXT_PRIMARY,
                              stroke_width=2.5, dash_length=0.10,
                              z_index=4, stroke_opacity=0.65)
        euc_lbl = backed_label("Euclidean", font_size=15,
                               color=LODEV_RED, weight=BOLD,
                               slant=ITALIC)
        euc_lbl.move_to((P + H) / 2 + ray_perp * 0.38)
        self.play(Create(euc_line), FadeIn(euc_lbl), run_time=0.6)
 
        # ── yDist: B → H ─────────────────────────────────────────────────
        dot_B = Dot(B, radius=0.05, color=LODEV_BLUE, z_index=8)
        ydist_line = Line(B, H, stroke_color=LODEV_RED,
                          stroke_width=4, z_index=5)
        yd_lbl = backed_label("yDist", font_size=17, color=LODEV_RED,
                              weight=BOLD)
        yd_lbl.next_to(ydist_line, RIGHT, buff=0.12)
        ra_B = right_angle_mark(B, [-1, 0, 0], [0, 1, 0],
                                size=0.10, color=TEXT_PRIMARY)
        self.play(FadeIn(dot_B), Create(ydist_line), FadeIn(yd_lbl),
                  Create(ra_B), run_time=0.6)
 
        # ── Dotted horizontal P → B ──────────────────────────────────────
        horiz_dot = DashedLine(P, B, stroke_color=LODEV_GREEN,
                               stroke_width=1.5, dash_length=0.08,
                               stroke_opacity=0.45)
        self.play(Create(horiz_dot), run_time=0.3)
 
        # ── Orange dotted: dir_tip → D ───────────────────────────────────
        orange_dot = DashedLine(dir_tip, D, stroke_color=LODEV_ORANGE,
                                stroke_width=2, dash_length=0.08,
                                stroke_opacity=0.75)
        self.play(Create(orange_dot), run_time=0.3)
        self.wait(1.0)
 
        # ==================================================================
        # Annotation boxes — side by side at the bottom
        # ==================================================================
 
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
 
        # ── Red box (Euclidean is wrong) — appears first, stays ───────────
        bad_box = make_callout([
            ("Euclidean distance varies with", 16, NORMAL),
            ("ray angle → fisheye effect!", 16, BOLD),
        ], ACCENT_ALERT)
 
        # ── Green box (perpWallDist is correct) — appears second ──────────
        good_box = make_callout([
            ("perpWallDist = dist ⊥ to", 16, NORMAL),
            ("camera plane", 16, NORMAL),
            ("= sideDistY − deltaDistY", 15, NORMAL),
            ("→ no fisheye distortion", 15, BOLD),
        ], HIT_COLOR)
 
        # Arrange side by side at the bottom
        callout_row = VGroup(bad_box, good_box).arrange(RIGHT, buff=0.3)
        callout_row.to_edge(DOWN, buff=0.2)
 
        self.play(FadeIn(bad_box), run_time=0.5)
        self.wait(1.5)
        self.play(FadeIn(good_box), run_time=0.5)
        self.wait(2.5)
 
        # ── Collect diagram elements ──────────────────────────────────────
        diagram_all = VGroup(
            grid_group, cam_plane_line, cam_lbl,
            player_dot,
            dir_arrow, dlbl,
            ray_arrow, rdlbl,
            arr_rdx, rdx_lbl, arr_rdy, rdy_lbl, ra_C,
            ray_full, hit_dot,
            dot_A, perp_line, perp_lbl,
            euc_line, euc_lbl,
            dot_B, ydist_line, yd_lbl, ra_B,
            horiz_dot, orange_dot,
            bad_box, good_box,
        )
 
        # ==================================================================
        # PHASE 2 — Multi-ray + screen columns
        # ==================================================================
        self.play(FadeOut(diagram_all), run_time=0.7)
        self.play(Create(divider), FadeIn(lhdr), FadeIn(rhdr), run_time=0.5)

        # Phase 2 uses left-half positioning (separate from centred Phase 1)
        grid_ox_p2 = -6.6
        grid_oy_p2 = 2.45

        def g2s_p2(r, c):
            return np.array([grid_ox_p2 + (c + 0.5) * cs,
                             grid_oy_p2 - (r + 0.5) * cs, 0])

        P_p2 = g2s_p2(6, 1) + np.array([0.05, 0.1, 0])
        wall_y_p2 = grid_oy_p2 - cs

        # Rebuild grid for left half
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

        # Wall line spanning full grid width
        wl_left  = np.array([grid_ox_p2, wall_y_p2, 0])
        wl_right = np.array([grid_ox_p2 + grid_cols * cs, wall_y_p2, 0])
        simp_wall = Line(wl_left, wl_right,
                         stroke_color=LODEV_WALL_BLUE, stroke_width=5)
        sw_lbl = Text("Wall", font_size=18, color=LODEV_WALL_BLUE)
        sw_lbl.next_to(simp_wall, UP, buff=0.08)

        self.play(FadeIn(simp_grid), FadeIn(simp_wall), FadeIn(sw_lbl),
                  FadeIn(simp_player), FadeIn(sp_lbl), run_time=0.5)

        # ── Cast 5 rays with narrower FOV ─────────────────────────────────
        num_cols = 5
        screen_w = 3.2
        screen_h = 3.2
        screen_cx = 4.2
        screen_cy = -0.1
        col_w = screen_w / num_cols

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
 
        # ── Screen background ─────────────────────────────────────────────
        screen_bg = Rectangle(
            width=screen_w, height=screen_h,
            fill_color="#060D16", fill_opacity=1.0,
            stroke_color="#1A3050", stroke_width=1.5,
        ).move_to([screen_cx, screen_cy, 0])
        self.play(FadeIn(screen_bg), run_time=0.3)
 
        # ── Screen columns ────────────────────────────────────────────────
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
                fill_color=shade, fill_opacity=0.92,
                stroke_width=0,
            ).move_to([col_x, screen_cy, 0])
            ceil_rect = Rectangle(
                width=act_col_w - 0.05, height=ceil_h,
                fill_color="#0C1830", fill_opacity=1.0,
                stroke_width=0,
            ).next_to(wall_rect, UP, buff=0)
            floor_rect = Rectangle(
                width=act_col_w - 0.05, height=ceil_h,
                fill_color="#1A1A1A", fill_opacity=1.0,
                stroke_width=0,
            ).next_to(wall_rect, DOWN, buff=0)
            col_groups.add(VGroup(ceil_rect, wall_rect, floor_rect))
            self.play(FadeIn(col_groups[-1], scale=0.85), run_time=0.22)
 
            ann_y = min(screen_cy + screen_h / 2 - 0.18,
                        screen_cy + line_h / 2 + 0.2)
            ann = Text(f"{line_h:.1f}", font_size=15, color=HIT_COLOR)
            ann.move_to([col_x, ann_y, 0])
            height_annots.add(ann)
        self.play(FadeIn(height_annots, lag_ratio=0.1), run_time=0.4)
 
        # ── Brace on centre column ────────────────────────────────────────
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
 
        # ==================================================================
        # PHASE 3 — Formula panel
        # ==================================================================
        formula_box = RoundedRectangle(
            corner_radius=0.15, width=13.0, height=2.2,
            fill_color=PANEL_FILL, fill_opacity=0.97,
            stroke_color=ACCENT_SERVER, stroke_width=2,
        ).to_edge(DOWN, buff=0.08)
        fl1 = Text("rayDir  =  dir  +  plane × cameraX",
                    font_size=24, color=TEXT_PRIMARY, slant=ITALIC)
        fl2 = Text("perpWallDist  =  sideDistY − deltaDistY     (y-side hit)",
                    font_size=21, color=TEXT_MUTED)
        fl3 = Text(
            "lineHeight  =  screenHeight / perpWallDist"
            "     (⊥ distance — no fisheye)",
            font_size=20, color=ACCENT_STORAGE,
        )
        formula = VGroup(fl1, fl2, fl3).arrange(DOWN, buff=0.16,
                                                aligned_edge=LEFT)
        formula.move_to(formula_box.get_center())
        if formula.get_width() > 12.6:
            formula.scale_to_fit_width(12.6)
 
        self.play(FadeIn(formula_box), run_time=0.3)
        self.play(Write(fl1), run_time=0.8)
        self.play(FadeIn(fl2, shift=UP * 0.1), run_time=0.6)
        self.play(FadeIn(fl3, shift=UP * 0.1), run_time=0.6)
        self.wait(3.8)
 
        # ── Final fade out ────────────────────────────────────────────────
        self.play(FadeOut(VGroup(
            section, divider, lhdr, rhdr,
            simp_grid, simp_wall, sw_lbl, simp_player, sp_lbl,
            ray_lines, hit_dots_r,
            screen_bg, col_groups, height_annots,
            formula_box, formula,
        )), run_time=0.9)


class FPGAParallelScene(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND

        section = Text("4. FPGA Hardware Acceleration", font_size=42, color=PYNQ_RED, weight=BOLD)
        section.to_edge(UP, buff=0.4)
        self.play(Write(section), run_time=0.8)

        cpu_label  = Text("CPU  —  Sequential", font_size=26, weight=BOLD, color="#5599FF")
        fpga_label = Text("FPGA  —  Parallel",  font_size=26, weight=BOLD, color=PYNQ_RED)
        cpu_label.move_to(LEFT * 3.2 + UP * 1.9)
        fpga_label.move_to(RIGHT * 3.2 + UP * 1.9)
        self.play(FadeIn(cpu_label), FadeIn(fpga_label), run_time=0.5)

        num_cols = 16
        col_w    = 0.26
        cpu_cols = VGroup()
        fpga_cols = VGroup()

        for index in range(num_cols):
            def make_col(x_centre):
                return Rectangle(
                    width=col_w, height=2.0,
                    fill_color=GREY_D, fill_opacity=0.3,
                    stroke_color="#2A4060", stroke_width=0.8,
                ).move_to(np.array([x_centre + (index - num_cols / 2 + 0.5) * col_w, -0.3, 0]))
            cpu_cols.add(make_col(-3.2))
            fpga_cols.add(make_col(3.2))

        self.play(FadeIn(cpu_cols), FadeIn(fpga_cols), run_time=0.5)

        # CPU fills one column at a time
        for index in range(num_cols):
            self.play(cpu_cols[index].animate.set_fill(color="#5599FF", opacity=0.85), run_time=0.1)

        # FPGA fills all at once
        self.play(
            *[fpga_cols[i].animate.set_fill(color=PYNQ_RED, opacity=0.85) for i in range(num_cols)],
            run_time=0.45,
        )

        hw_text = VGroup(
            Text("Why DDA maps perfectly to hardware:", font_size=24, color=TEXT_PRIMARY, weight=BOLD),
            Text("Only additions and comparisons — no multiply/divide",  font_size=22, color=TEXT_MUTED),
            Text("Each ray is fully independent — trivially parallelisable", font_size=22, color=TEXT_MUTED),
            Text("Map stored in BRAM — zero off-chip memory latency",    font_size=22, color=TEXT_MUTED),
            Text("Wall-height division done in a single LUT stage",       font_size=22, color=TEXT_MUTED),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        hw_text.to_edge(DOWN, buff=0.45)

        self.play(FadeIn(hw_text, shift=UP * 0.3, lag_ratio=0.1), run_time=1.4)
        self.wait(2.8)
        self.play(FadeOut(VGroup(section, cpu_label, fpga_label, cpu_cols, fpga_cols, hw_text)), run_time=0.8)


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
            font_size=21, color=TEXT_MUTED,
        ).next_to(storage_row, DOWN, buff=0.18)

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