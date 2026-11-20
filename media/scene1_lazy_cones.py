from manim import *

class LazyTwoConeHandshake(Scene):
    def construct(self):
        self.camera.background_color = "#0d1117"

        title = Text("Client-Server Spacetime: Lazy Two-Cone Handshake", font_size=34, color=WHITE, weight=BOLD).to_edge(UP, buff=0.35)
        subtitle = Text("Superposition saves vacuum bandwidth until outer fringes touch", font_size=20, color="#8b949e").next_to(title, DOWN, buff=0.15)
        self.play(Write(title), FadeIn(subtitle), run_time=1.0)

        emit_dot = Dot(LEFT * 4.8 + DOWN * 0.3, color="#58a6ff", radius=0.11)
        emit_lbl = Text("Emitter (t0)", font_size=18, color="#58a6ff").next_to(emit_dot, LEFT, buff=0.15)

        det_line = Line(RIGHT * 4.2 + DOWN * 2.5, RIGHT * 4.2 + UP * 1.9, color="#30363d", stroke_width=5)
        det_lbl = Text("Detector Screen", font_size=18, color="#c9d1d9").next_to(det_line, UP, buff=0.15)

        hud_box = RoundedRectangle(corner_radius=0.12, width=4.6, height=1.15, color="#30363d", fill_color="#161b22", fill_opacity=0.95).to_corner(DL, buff=0.4)
        hud_text = Text("Client Grid Updates: 0\nServer State: Unrendered Ticket", font_size=18, color="#3fb950").move_to(hud_box)

        self.play(FadeIn(emit_dot), Write(emit_lbl), Create(det_line), Write(det_lbl), FadeIn(hud_box), Write(hud_text), run_time=1.0)

        fwd_cone = Polygon(
            LEFT * 4.8 + DOWN * 0.3,
            RIGHT * 4.2 + UP * 1.8,
            RIGHT * 4.2 + DOWN * 2.4,
            color="#58a6ff",
            fill_color="#58a6ff",
            fill_opacity=0.14,
            stroke_width=2.5,
        )
        fwd_tag = Text("Forward Pascal Cone (Lazy / 0 Ticks)", font_size=17, color="#58a6ff").move_to(LEFT * 1.1 + UP * 1.35)
        self.play(Create(fwd_cone), FadeIn(fwd_tag), run_time=1.6)
        self.wait(0.6)

        air_dot = Dot(UP * 1.35 + LEFT * 0.4, color="#f0883e", radius=0.09)
        air_ring = Circle(radius=0.65, color="#f0883e", stroke_width=2).move_to(air_dot)
        air_lbl = Text("Fringe Contact -> decohere()", font_size=18, color="#f0883e", weight=BOLD).next_to(air_ring, LEFT, buff=0.2)

        self.play(FadeIn(air_dot), Create(air_ring), Write(air_lbl), run_time=0.9)
        self.play(Indicate(fwd_cone, color="#f0883e"), run_time=0.6)

        hit_pt = RIGHT * 4.2 + UP * 0.35
        hit_dot = Dot(hit_pt, color="#ff7b72", radius=0.13)
        bwd_cone = Polygon(
            hit_pt,
            LEFT * 4.8 + UP * 1.6,
            LEFT * 4.8 + DOWN * 2.2,
            color="#bc8cff",
            fill_color="#bc8cff",
            fill_opacity=0.18,
            stroke_width=2.5,
        )
        bwd_tag = Text("Inverted Backward Cone (Just-In-Time Handshake)", font_size=17, color="#bc8cff").move_to(RIGHT * 0.6 + DOWN * 1.85)
        new_hud = Text("Client Grid Updates: 1 Click\nBandwidth Saved: 99.75%", font_size=18, color="#79c0ff", weight=BOLD).move_to(hud_box)

        self.play(FadeIn(hit_dot), Create(bwd_cone), FadeIn(bwd_tag), Transform(hud_text, new_hud), run_time=1.4)

        zigzag = VMobject(color="#3fb950", stroke_width=4)
        zigzag.set_points_as_corners([
            LEFT * 4.8 + DOWN * 0.3,
            LEFT * 2.5 + UP * 0.45,
            LEFT * 0.3 + DOWN * 0.25,
            RIGHT * 2.0 + UP * 0.65,
            hit_pt,
        ])
        self.play(Create(zigzag), Flash(hit_dot, color="#ff7b72", line_length=0.35), run_time=1.2)
        self.wait(1.8)
