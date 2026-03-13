from manim import *
import numpy as np


PYNQ_RED = "#f05252"
PYNQ_RED_DARK = "#c93c3c"
BACKGROUND = "#07111C"
PANEL_FILL = "#10243A"
PANEL_STROKE = "#58C4DD"
TEXT_PRIMARY = "#F4F7FB"
TEXT_MUTED = "#9FB3C8"
ACCENT_HARDWARE = "#F7A541"
ACCENT_SERVER = "#58C4DD"
ACCENT_STORAGE = "#7BD88F"
ACCENT_ALERT = "#FF6B6B"
GRID_COLOR = GREY_B
WALL_COLOR = "#4A6FA5"
WALL_COLOR_DARK = "#3A5A8A"
EMPTY_COLOR = "#1A1A2E"
PLAYER_COLOR = PYNQ_RED
RAY_COLOR = YELLOW
FOV_COLOR = "#FFAA33"
HIT_COLOR = GREEN_A

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


# Build the small 2D tile map used in the algorithm scenes.
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
            square.move_to(
                np.array(
                    [
                        (col - map_cols / 2 + 0.5) * cell_size,
                        -(row - map_rows / 2 + 0.5) * cell_size,
                        0,
                    ]
                )
            )
            grid_group.add(square)

    return grid_group


# Convert a row and column into a square center inside a rendered grid group.
def grid_cell_center(grid_group, row, col, map_cols):
    return grid_group[row * map_cols + col].get_center()


# Map a world-space point back into the current grid cell coordinates.
def point_to_grid_cell(point, grid_group, map_rows, map_cols, cell_size):
    rel = point - grid_group.get_center()
    col = int(np.floor(rel[0] / cell_size + map_cols / 2))
    row = int(np.floor(-rel[1] / cell_size + map_rows / 2))
    return row, col


# Build a rounded labelled box used across the architecture segment.
def make_panel(title: str, subtitle: str, width: float, height: float, accent: str) -> VGroup:
    box = RoundedRectangle(
        corner_radius=0.2,
        width=width,
        height=height,
        stroke_color=accent,
        stroke_width=2,
        fill_color=PANEL_FILL,
        fill_opacity=0.95,
    )
    title_text = Text(title, font_size=28, color=TEXT_PRIMARY, weight=BOLD)
    subtitle_text = Text(subtitle, font_size=18, color=TEXT_MUTED)
    copy = VGroup(title_text, subtitle_text).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
    copy.move_to(box.get_center())
    return VGroup(box, copy)


# Build a vertical SEDA stage strip for the EC2 game loop.
def make_seda_pipeline() -> VGroup:
    labels = [
        ("T1", "UDP Receive"),
        ("T2", "20 Hz Game Tick"),
        ("T3", "Broadcast"),
        ("T4", "Redis Write"),
    ]
    stages = VGroup()
    for code, label in labels:
        stage = make_panel(code, label, width=2.3, height=1.15, accent=ACCENT_SERVER)
        stages.add(stage)
    stages.arrange(DOWN, buff=0.22)

    connectors = VGroup()
    for idx in range(len(stages) - 1):
        start = stages[idx].get_bottom() + DOWN * 0.04
        end = stages[idx + 1].get_top() + UP * 0.04
        arrow = Arrow(start, end, buff=0.05, stroke_width=4, max_tip_length_to_length_ratio=0.16, color=ACCENT_SERVER)
        connectors.add(arrow)

    return VGroup(stages, connectors)


# Build the storage tier callout row shown under the server pipeline.
def make_storage_row() -> VGroup:
    redis_panel = make_panel("Redis", "hot state + control", width=2.8, height=1.2, accent=ACCENT_SERVER)
    dynamo_panel = make_panel("DynamoDB", "warm metadata", width=2.8, height=1.2, accent=ACCENT_STORAGE)
    s3_panel = make_panel("S3 / SNS", "cold replay + fan-out", width=3.0, height=1.2, accent=ACCENT_STORAGE)
    row = VGroup(redis_panel, dynamo_panel, s3_panel).arrange(RIGHT, buff=0.35)

    arrows = VGroup(
        Arrow(redis_panel.get_right(), dynamo_panel.get_left(), buff=0.08, stroke_width=4, color=ACCENT_STORAGE),
        Arrow(dynamo_panel.get_right(), s3_panel.get_left(), buff=0.08, stroke_width=4, color=ACCENT_STORAGE),
    )
    return VGroup(row, arrows)


# Build the left-side hardware lane for the real PYNQ boards.
def make_hardware_lane() -> VGroup:
    board_a = make_panel("PYNQ Board A", "HDMI + FPGA raycaster", width=3.2, height=1.35, accent=ACCENT_HARDWARE)
    board_b = make_panel("PYNQ Board B", "manual or auto role", width=3.2, height=1.35, accent=ACCENT_HARDWARE)
    controller = make_panel("Controls", "buttons / joystick / demo AI", width=3.2, height=1.1, accent=ACCENT_HARDWARE)
    return VGroup(board_a, board_b, controller).arrange(DOWN, buff=0.28)


# Build the sidecar and monitor branch shown to the right of the server.
def make_service_branch() -> VGroup:
    sidecar = make_panel("Python Sidecar", "AWS writes off the hot path", width=3.4, height=1.25, accent=ACCENT_STORAGE)
    monitor = make_panel("Live Monitor", "WebSocket + replay + control", width=3.4, height=1.25, accent=ACCENT_SERVER)
    return VGroup(sidecar, monitor).arrange(DOWN, buff=0.3)


class TitleScene(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND

        title = Text("PYNQ CAST", font_size=72, weight=BOLD, color=PYNQ_RED)
        subtitle = Text("Distributed FPGA Raycasting", font_size=36, color=WHITE)
        subtitle.next_to(title, DOWN, buff=0.4)
        algo_text = Text("From grid map to hardware pipeline", font_size=28, color=GREY_A)
        algo_text.next_to(subtitle, DOWN, buff=0.6)

        self.play(Write(title), run_time=1.5)
        self.play(FadeIn(subtitle, shift=UP * 0.3), run_time=1)
        self.wait(0.3)
        self.play(FadeIn(algo_text, shift=UP * 0.2), run_time=0.8)
        self.wait(1.6)
        self.play(FadeOut(Group(title, subtitle, algo_text)), run_time=0.8)


class GridMapScene(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND

        section = Text("1. The 2D Grid Map", font_size=40, color=PYNQ_RED)
        section.to_edge(UP, buff=0.4)
        self.play(Write(section), run_time=0.8)

        world_map = ALGO_WORLD_MAP
        map_rows = len(world_map)
        map_cols = len(world_map[0])
        grid_group = make_world_grid(world_map, cell_size=0.6)
        grid_group.shift(DOWN * 0.3)

        self.play(FadeIn(grid_group, lag_ratio=0.01), run_time=1.5)
        self.wait(0.3)

        wall_swatch = Square(0.28, stroke_width=0).set_fill(WALL_COLOR, opacity=0.92)
        wall_label = Text("Wall (1)", font_size=20, color=WALL_COLOR)
        empty_swatch = Square(0.28, stroke_width=0).set_fill(EMPTY_COLOR, opacity=0.75)
        empty_label = Text("Empty (0)", font_size=20, color=GREY_A)
        legend = VGroup(
            VGroup(wall_swatch, wall_label).arrange(RIGHT, buff=0.15),
            VGroup(empty_swatch, empty_label).arrange(RIGHT, buff=0.15),
        ).arrange(RIGHT, buff=1.0)
        legend.next_to(grid_group, DOWN, buff=0.5)
        self.play(FadeIn(legend), run_time=0.5)

        bram_text = Text(
            "Stored in FPGA Block RAM — each cell is just a few bits",
            font_size=22,
            color=GREY_A,
        )
        bram_text.next_to(legend, DOWN, buff=0.4)
        self.play(FadeIn(bram_text, shift=UP * 0.2), run_time=0.8)

        player_world = grid_cell_center(grid_group, 5, 2, map_cols)
        player_dot = Dot(player_world, radius=0.12, color=PLAYER_COLOR, z_index=5)
        player_label = Text("Player", font_size=18, color=PLAYER_COLOR)
        player_label.next_to(player_dot, LEFT, buff=0.2)

        self.play(FadeIn(player_dot, scale=0.5), FadeIn(player_label), run_time=0.8)
        self.wait(1.8)
        self.play(FadeOut(Group(section, grid_group, legend, bram_text, player_dot, player_label)), run_time=0.8)


class DDAScene(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND

        section = Text("2. Casting Rays — The DDA Algorithm", font_size=40, color=PYNQ_RED)
        section.to_edge(UP, buff=0.4)
        self.play(Write(section), run_time=0.8)

        world_map = ALGO_WORLD_MAP
        map_rows = len(world_map)
        map_cols = len(world_map[0])
        cell_size = 0.55
        grid_group = make_world_grid(world_map, cell_size=cell_size, empty_opacity=0.42)
        grid_group.shift(LEFT * 2.0 + DOWN * 0.3)

        self.play(FadeIn(grid_group, lag_ratio=0.005), run_time=0.8)

        player_world = grid_cell_center(grid_group, 5, 2, map_cols)
        player_dot = Dot(player_world, radius=0.1, color=PLAYER_COLOR, z_index=5)
        self.play(FadeIn(player_dot, scale=0.5), run_time=0.5)

        fov_angle = 60
        player_dir = 30
        fov_half = fov_angle / 2
        ray_length = 3.5

        dir_rad = np.radians(player_dir)
        fov_left_rad = np.radians(player_dir + fov_half)
        fov_right_rad = np.radians(player_dir - fov_half)

        fov_left_end = player_world + ray_length * np.array([np.cos(fov_left_rad), np.sin(fov_left_rad), 0])
        fov_right_end = player_world + ray_length * np.array([np.cos(fov_right_rad), np.sin(fov_right_rad), 0])

        fov_left_line = DashedLine(player_world, fov_left_end, color=FOV_COLOR, dash_length=0.1, stroke_width=2)
        fov_right_line = DashedLine(player_world, fov_right_end, color=FOV_COLOR, dash_length=0.1, stroke_width=2)
        fov_label = Text("60° FOV", font_size=20, color=FOV_COLOR)
        fov_label.move_to(player_world + 1.55 * np.array([np.cos(dir_rad), np.sin(dir_rad), 0]) + UP * 0.2)

        self.play(Create(fov_left_line), Create(fov_right_line), FadeIn(fov_label), run_time=1)

        dda_steps = VGroup(
            Text("DDA Steps:", font_size=24, weight=BOLD, color=WHITE),
            Text("1. For each screen column,", font_size=19, color=GREY_A),
            Text("   cast a ray from the player", font_size=19, color=GREY_A),
            Text("2. Step through grid cells", font_size=19, color=GREY_A),
            Text("   one boundary at a time", font_size=19, color=GREY_A),
            Text("3. Stop when a wall is hit", font_size=19, color=GREY_A),
            Text("4. Use perpendicular distance", font_size=19, color=GREY_A),
            Text("   to avoid fisheye distortion", font_size=19, color=GREY_A),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        dda_steps.to_edge(RIGHT, buff=0.5).shift(DOWN * 0.2)
        self.play(FadeIn(dda_steps, lag_ratio=0.1), run_time=2)

        num_rays = 7
        ray_angles = np.linspace(player_dir + fov_half, player_dir - fov_half, num_rays)
        ray_draws = VGroup()
        hit_draws = VGroup()

        for index, angle_deg in enumerate(ray_angles):
            angle_rad = np.radians(angle_deg)
            ray_dir = np.array([np.cos(angle_rad), np.sin(angle_rad), 0])
            hit_pos = None

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

            ray_line = Line(
                player_world,
                hit_pos,
                color=RAY_COLOR if index != 3 else PYNQ_RED,
                stroke_width=2.5 if index == 3 else 1.5,
                stroke_opacity=1.0 if index == 3 else 0.5,
            )
            hit_dot = Dot(hit_pos, radius=0.06, color=HIT_COLOR, z_index=5)
            ray_draws.add(ray_line)
            hit_draws.add(hit_dot)

            if index == 3:
                self.play(Create(ray_line), run_time=0.6)
                self.play(FadeIn(hit_dot, scale=0.5), run_time=0.3)
            else:
                self.play(Create(ray_line), FadeIn(hit_dot, scale=0.5), run_time=0.25 if index > 0 else 0.4)

        self.wait(1.8)
        self.play(FadeOut(Group(section, grid_group, player_dot, fov_left_line, fov_right_line, fov_label, dda_steps, ray_draws, hit_draws)), run_time=0.8)


class WallRenderScene(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND

        section = Text("3. Distance → Wall Height", font_size=40, color=PYNQ_RED)
        section.to_edge(UP, buff=0.4)
        self.play(Write(section), run_time=0.8)

        top_label = Text("Top-Down View", font_size=22, color=GREY_A)
        top_label.move_to(LEFT * 3.5 + UP * 2.2)
        screen_label = Text("Screen Output", font_size=22, color=GREY_A)
        screen_label.move_to(RIGHT * 2.5 + UP * 2.2)
        self.play(FadeIn(top_label), FadeIn(screen_label), run_time=0.5)

        player_pos = LEFT * 3.5 + DOWN * 1.5
        player_dot = Dot(player_pos, radius=0.1, color=PLAYER_COLOR, z_index=5)
        self.play(FadeIn(player_dot), run_time=0.3)

        distances = [1.2, 2.0, 3.5, 2.5, 1.5]
        angles = [70, 55, 40, 25, 10]
        screen_columns = VGroup()
        rays = VGroup()
        max_wall_h = 3.0
        col_width = 0.6
        screen_left = RIGHT * 0.5

        for index, (dist, angle_deg) in enumerate(zip(distances, angles)):
            angle_rad = np.radians(angle_deg)
            end = player_pos + dist * np.array([np.cos(angle_rad), np.sin(angle_rad), 0])
            ray = Line(player_pos, end, color=RAY_COLOR, stroke_width=2)
            hit = Dot(end, radius=0.06, color=HIT_COLOR)
            rays.add(ray, hit)

            wall_h = min(max_wall_h, 1.8 / dist * 2.5)
            col_x = screen_left[0] + index * col_width + col_width / 2
            col_center = np.array([col_x, 0, 0])

            wall_rect = Rectangle(
                width=col_width - 0.05,
                height=wall_h,
                fill_color=WALL_COLOR,
                fill_opacity=0.9,
                stroke_color=WALL_COLOR_DARK,
                stroke_width=1,
            ).move_to(col_center)

            ceil_h = (max_wall_h - wall_h) / 2
            ceil_rect = Rectangle(
                width=col_width - 0.05,
                height=ceil_h,
                fill_color="#1A1A3E",
                fill_opacity=0.8,
                stroke_width=0,
            ).next_to(wall_rect, UP, buff=0)
            floor_rect = Rectangle(
                width=col_width - 0.05,
                height=ceil_h,
                fill_color="#3A3A3A",
                fill_opacity=0.6,
                stroke_width=0,
            ).next_to(wall_rect, DOWN, buff=0)

            screen_columns.add(VGroup(floor_rect, wall_rect, ceil_rect))

        for index in range(len(distances)):
            self.play(Create(rays[index * 2]), FadeIn(rays[index * 2 + 1]), FadeIn(screen_columns[index]), run_time=0.5)

        formula = Text("wallHeight = k / perpDistance", font_size=30, color=WHITE, slant=ITALIC)
        formula.to_edge(DOWN, buff=0.6)
        note = Text("Perpendicular distance avoids fisheye distortion", font_size=20, color=GREY_A)
        note.next_to(formula, DOWN, buff=0.3)

        self.play(Write(formula), run_time=1)
        self.play(FadeIn(note), run_time=0.5)
        self.wait(1.8)
        self.play(FadeOut(Group(section, top_label, screen_label, player_dot, rays, screen_columns, formula, note)), run_time=0.8)


class FPGAParallelScene(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND

        section = Text("4. FPGA Parallelism", font_size=40, color=PYNQ_RED)
        section.to_edge(UP, buff=0.4)
        self.play(Write(section), run_time=0.8)

        cpu_label = Text("CPU (Sequential)", font_size=24, weight=BOLD, color="#5599FF")
        cpu_label.move_to(LEFT * 3.2 + UP * 1.8)
        fpga_label = Text("FPGA (Parallel)", font_size=24, weight=BOLD, color=PYNQ_RED)
        fpga_label.move_to(RIGHT * 3.2 + UP * 1.8)
        self.play(FadeIn(cpu_label), FadeIn(fpga_label), run_time=0.5)

        num_cols = 16
        col_w = 0.25
        cpu_cols = VGroup()
        fpga_cols = VGroup()

        for index in range(num_cols):
            cpu_col = Rectangle(
                width=col_w,
                height=2.0,
                fill_color=GREY_D,
                fill_opacity=0.3,
                stroke_color=GREY_B,
                stroke_width=0.5,
            ).move_to(LEFT * 3.2 + RIGHT * (index - num_cols / 2 + 0.5) * col_w + DOWN * 0.3)
            fpga_col = Rectangle(
                width=col_w,
                height=2.0,
                fill_color=GREY_D,
                fill_opacity=0.3,
                stroke_color=GREY_B,
                stroke_width=0.5,
            ).move_to(RIGHT * 3.2 + RIGHT * (index - num_cols / 2 + 0.5) * col_w + DOWN * 0.3)
            cpu_cols.add(cpu_col)
            fpga_cols.add(fpga_col)

        self.play(FadeIn(cpu_cols), FadeIn(fpga_cols), run_time=0.5)

        for index in range(num_cols):
            self.play(cpu_cols[index].animate.set_fill(color="#5599FF", opacity=0.8), run_time=0.12)

        self.play(*[fpga_cols[index].animate.set_fill(color=PYNQ_RED, opacity=0.8) for index in range(num_cols)], run_time=0.4)

        hw_text = VGroup(
            Text("DDA on hardware:", font_size=22, weight=BOLD, color=WHITE),
            Text("• additions + comparisons only", font_size=19, color=GREY_A),
            Text("• no full matrix math", font_size=19, color=GREY_A),
            Text("• each ray is fully independent", font_size=19, color=GREY_A),
            Text("• map stored in BRAM", font_size=19, color=GREY_A),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        hw_text.to_edge(DOWN, buff=0.5)

        self.play(FadeIn(hw_text, shift=UP * 0.3), run_time=1)
        self.wait(2.5)
        self.play(FadeOut(Group(section, cpu_label, fpga_label, cpu_cols, fpga_cols, hw_text)), run_time=0.8)


class MultiNodeScene(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND

        section = Text("5. Multi-Node Tile Distribution", font_size=40, color=PYNQ_RED)
        section.to_edge(UP, buff=0.4)
        self.play(Write(section), run_time=0.8)

        screen_w = 5.0
        screen_h = 3.0
        tiles_x = 4
        tiles_y = 2
        tile_w = screen_w / tiles_x
        tile_h = screen_h / tiles_y
        node_colors = ["#F05252", "#4A9EFF", "#4ADB7A", "#FFAA33"]
        node_names = ["Node 0", "Node 1", "Node 2", "Node 3"]

        screen_rect = Rectangle(width=screen_w, height=screen_h, stroke_color=WHITE, stroke_width=2).shift(DOWN * 0.3)
        self.play(Create(screen_rect), run_time=0.5)

        tiles = VGroup()
        for row in range(tiles_y):
            for col in range(tiles_x):
                node_idx = (row * tiles_x + col) % len(node_colors)
                tile = Rectangle(
                    width=tile_w - 0.04,
                    height=tile_h - 0.04,
                    fill_color=node_colors[node_idx],
                    fill_opacity=0.5,
                    stroke_color=node_colors[node_idx],
                    stroke_width=1.5,
                )
                tile.move_to(
                    screen_rect.get_corner(UL)
                    + np.array([(col + 0.5) * tile_w, -(row + 0.5) * tile_h, 0])
                )
                tiles.add(tile)

        self.play(FadeIn(tiles, lag_ratio=0.1), run_time=1.5)

        legend = VGroup()
        for name, color in zip(node_names, node_colors):
            dot = Dot(radius=0.08, color=color)
            label = Text(name, font_size=18, color=color)
            legend.add(VGroup(dot, label).arrange(RIGHT, buff=0.15))
        legend.arrange(RIGHT, buff=0.6)
        legend.next_to(screen_rect, DOWN, buff=0.5)
        self.play(FadeIn(legend), run_time=0.5)

        arch_text = VGroup(
            Text("Each PYNQ node renders its tile independently", font_size=20, color=GREY_A),
            Text("Server orchestrates + aggregates via Redis/DynamoDB", font_size=20, color=GREY_A),
        ).arrange(DOWN, buff=0.15)
        arch_text.next_to(legend, DOWN, buff=0.4)
        self.play(FadeIn(arch_text, shift=UP * 0.2), run_time=0.8)
        self.wait(2.5)
        self.play(FadeOut(Group(section, screen_rect, tiles, legend, arch_text)), run_time=0.8)


class PipelineScene(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND

        section = Text("6. The Full Pipeline", font_size=40, color=PYNQ_RED)
        section.to_edge(UP, buff=0.4)
        self.play(Write(section), run_time=0.8)

        box_style = {"fill_opacity": 0.15, "stroke_width": 2, "corner_radius": 0.15}
        labels_text = [
            ("Scene Data\n(S3/DynamoDB)", GREY_A),
            ("Server\nOrchestrator", "#4A9EFF"),
            ("FPGA Node\n(DDA Raycaster)", PYNQ_RED),
            ("Tile\nAggregator", "#FFAA33"),
            ("Web\nDashboard", "#4ADB7A"),
        ]

        boxes = []
        for text_value, color in labels_text:
            box = RoundedRectangle(width=2.2, height=1.3, stroke_color=color, fill_color=color, **box_style)
            label = Text(text_value, font_size=16, color=WHITE)
            label.move_to(box.get_center())
            boxes.append(VGroup(box, label))

        flow = VGroup(*boxes).arrange(RIGHT, buff=0.4).shift(DOWN * 0.2)
        if flow.get_width() > 12:
            flow.scale_to_fit_width(12)

        for box in boxes:
            self.play(FadeIn(box, scale=0.9), run_time=0.4)

        arrows = VGroup()
        for index in range(len(boxes) - 1):
            arrows.add(
                Arrow(
                    boxes[index].get_right(),
                    boxes[index + 1].get_left(),
                    buff=0.1,
                    color=GREY_A,
                    stroke_width=2,
                    max_tip_length_to_length_ratio=0.15,
                )
            )

        self.play(FadeIn(arrows, lag_ratio=0.2), run_time=1)
        self.wait(2.2)
        self.play(FadeOut(Group(section, flow, arrows)), run_time=0.8)

        final = Text("PYNQ CAST", font_size=60, weight=BOLD, color=PYNQ_RED)
        tagline = Text("Distributed FPGA Raycasting — embarrassingly parallel", font_size=26, color=GREY_A)
        tagline.next_to(final, DOWN, buff=0.4)
        self.play(Write(final), run_time=1)
        self.play(FadeIn(tagline, shift=UP * 0.2), run_time=0.8)
        self.wait(2.4)
        self.play(FadeOut(Group(final, tagline)), run_time=0.6)


class ServerHardwareSegment(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND

        title = Text("PYNQCAST Runtime", font_size=42, color=TEXT_PRIMARY, weight=BOLD)
        subtitle = Text(
            "Hardware rendering on the edge. Authoritative game logic in the EC2 server.",
            font_size=22,
            color=TEXT_MUTED,
        )
        title_group = VGroup(title, subtitle).arrange(DOWN, buff=0.18).to_edge(UP, buff=0.45)

        hardware_lane = make_hardware_lane().scale(0.88).to_edge(LEFT, buff=0.5).shift(DOWN * 0.25)
        server_pipeline = make_seda_pipeline().scale(0.86).move_to(ORIGIN + RIGHT * 0.2 + DOWN * 0.1)
        service_branch = make_service_branch().scale(0.85).to_edge(RIGHT, buff=0.42).shift(DOWN * 0.2)
        storage_row = make_storage_row().scale(0.8).next_to(server_pipeline, DOWN, buff=0.55)

        top_divider = Line(LEFT * 7.2, RIGHT * 7.2, stroke_color="#16324D", stroke_width=2).next_to(title_group, DOWN, buff=0.28)
        flow_a = Arrow(hardware_lane[0].get_right(), server_pipeline[0][0].get_left(), buff=0.12, stroke_width=5, color=ACCENT_HARDWARE)
        flow_b = Arrow(
            hardware_lane[1].get_right(),
            server_pipeline[0][0].get_left() + DOWN * 1.2,
            buff=0.12,
            stroke_width=5,
            color=ACCENT_HARDWARE,
        )
        control_arrow = Arrow(server_pipeline[0][2].get_right(), service_branch[1].get_left(), buff=0.12, stroke_width=4, color=ACCENT_SERVER)
        sidecar_arrow = Arrow(server_pipeline[0][3].get_right(), service_branch[0].get_left(), buff=0.12, stroke_width=4, color=ACCENT_STORAGE)
        storage_down = Arrow(service_branch[0].get_bottom(), storage_row[0][1].get_top(), buff=0.12, stroke_width=4, color=ACCENT_STORAGE)

        udp_label = Text("UDP 9000", font_size=18, color=TEXT_MUTED).next_to(flow_a, UP, buff=0.1)
        monitor_label = Text("monitor + control", font_size=18, color=TEXT_MUTED).next_to(control_arrow, UP, buff=0.08)
        sidecar_label = Text("async persistence", font_size=18, color=TEXT_MUTED).next_to(sidecar_arrow, UP, buff=0.08)

        edge_note = Text("Edge: real FPGA rendering", font_size=18, color=ACCENT_HARDWARE, weight=BOLD)
        edge_note.next_to(hardware_lane, UP, buff=0.18)
        cloud_note = Text("Cloud: authoritative state + storage", font_size=18, color=ACCENT_SERVER, weight=BOLD)
        cloud_note.next_to(server_pipeline, UP, buff=0.18)

        demo_modes = VGroup(
            Text("Manual:", font_size=20, color=TEXT_PRIMARY, weight=BOLD),
            Text("player controls board locally", font_size=20, color=TEXT_MUTED),
            Text("Auto:", font_size=20, color=TEXT_PRIMARY, weight=BOLD),
            Text("same board client can drive runner/tagger AI", font_size=20, color=TEXT_MUTED),
        ).arrange_in_grid(rows=2, cols=2, col_alignments="lr", buff=(0.18, 0.2))
        demo_modes.scale(0.82).to_edge(DOWN, buff=0.35)

        storage_caption = Text(
            "Replay, metadata, and post-match processing stay off the hot path.",
            font_size=20,
            color=TEXT_MUTED,
        ).next_to(storage_row, DOWN, buff=0.18)

        self.play(FadeIn(title_group, shift=DOWN * 0.2), Create(top_divider))
        self.play(
            LaggedStart(
                FadeIn(hardware_lane, shift=RIGHT * 0.2),
                FadeIn(server_pipeline, shift=UP * 0.2),
                FadeIn(service_branch, shift=LEFT * 0.2),
                lag_ratio=0.2,
            ),
            FadeIn(edge_note, shift=UP * 0.1),
            FadeIn(cloud_note, shift=UP * 0.1),
        )
        self.play(LaggedStart(GrowArrow(flow_a), GrowArrow(flow_b), FadeIn(udp_label, shift=UP * 0.1), lag_ratio=0.12))
        self.play(
            LaggedStart(
                GrowArrow(control_arrow),
                GrowArrow(sidecar_arrow),
                FadeIn(monitor_label, shift=UP * 0.1),
                FadeIn(sidecar_label, shift=UP * 0.1),
                lag_ratio=0.12,
            )
        )
        self.play(FadeIn(storage_row, shift=UP * 0.2), GrowArrow(storage_down), FadeIn(storage_caption, shift=UP * 0.1))

        highlight_box = SurroundingRectangle(server_pipeline[0][1], color=ACCENT_ALERT, buff=0.12, corner_radius=0.12)
        hot_path_copy = Text("T2 stays non-blocking and authoritative.", font_size=24, color=ACCENT_ALERT, weight=BOLD)
        hot_path_copy.next_to(server_pipeline, RIGHT, buff=0.65).shift(UP * 0.5)
        self.play(Create(highlight_box), FadeIn(hot_path_copy, shift=RIGHT * 0.15))
        self.wait(0.35)
        self.play(FadeOut(highlight_box), FadeOut(hot_path_copy))

        self.play(FadeIn(demo_modes, shift=UP * 0.15))
        self.wait(1.2)


class ServerHardwareClosingCard(Scene):
    def construct(self):
        self.camera.background_color = BACKGROUND

        card = RoundedRectangle(
            corner_radius=0.25,
            width=9.0,
            height=3.4,
            stroke_color=ACCENT_SERVER,
            stroke_width=2.5,
            fill_color=PANEL_FILL,
            fill_opacity=0.96,
        )
        headline = Text("One System, Two Strengths", font_size=40, color=TEXT_PRIMARY, weight=BOLD)
        line1 = Text("FPGA boards handle the edge rendering.", font_size=24, color=ACCENT_HARDWARE)
        line2 = Text("The EC2 stack owns game state, storage, replay, and control.", font_size=24, color=ACCENT_SERVER)
        copy = VGroup(headline, line1, line2).arrange(DOWN, buff=0.22)
        copy.move_to(card.get_center())
        group = VGroup(card, copy)

        self.play(FadeIn(group, scale=0.96))
        self.wait(1.6)
        self.play(FadeOut(group, scale=1.02))
