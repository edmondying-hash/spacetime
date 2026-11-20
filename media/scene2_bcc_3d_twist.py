from manim import *
import numpy as np

class BCC3DChiralAndConfinement(ThreeDScene):
    def construct(self):
        self.camera.background_color = "#0d1117"
        self.set_camera_orientation(phi=68 * DEGREES, theta=-42 * DEGREES)

        title = Text("3D BCC 8-Diagonal Lattice: Zero-Knob Derivations", font_size=30, color=WHITE, weight=BOLD).to_edge(UP, buff=0.3)
        sub = Text("Target A: 192/512 (3/8) Chiral Twists  |  Target B: 4-Link SU(2) Glueball Gap", font_size=17, color="#8b949e").next_to(title, DOWN, buff=0.12)
        self.add_fixed_in_frame_mobjects(title, sub)
        self.play(Write(title), FadeIn(sub), run_time=0.9)

        scale = 1.65
        corners = [
            np.array([x, y, z]) * scale
            for x in (-1, 1)
            for y in (-1, 1)
            for z in (-1, 1)
        ]
        center = np.array([0.0, 0.0, 0.0])

        cube_frame = Cube(side_length=2 * scale, fill_opacity=0.0, stroke_color="#30363d", stroke_width=1.5)
        center_dot = Sphere(center=center, radius=0.13, resolution=(14, 14)).set_color("#58a6ff")
        corner_dots = VGroup(*[
            Sphere(center=c, radius=0.09, resolution=(12, 12)).set_color("#8b949e")
            for c in corners
        ])
        diag_links = VGroup(*[
            Line3D(start=center, end=c, color="#30363d", thickness=0.015)
            for c in corners
        ])

        bcc_group = VGroup(cube_frame, diag_links, corner_dots, center_dot)
        self.play(FadeIn(bcc_group), run_time=1.0)
        self.begin_ambient_camera_rotation(rate=0.22)

        # Target A: Non-Planar 3-Step Chiral Twist (192/512 = 3/8 -> eta = 5.90e-10)
        p0 = np.array([-1.0, -1.0, -1.0]) * scale
        p1 = np.array([0.0, 0.0, 0.0])
        p2 = np.array([1.0, -1.0, 1.0]) * scale
        p3 = np.array([0.0, 0.0, 2.0]) * scale

        twist_path = VGroup(
            Line3D(p0, p1, color="#f0883e", thickness=0.045),
            Line3D(p1, p2, color="#f0883e", thickness=0.045),
            Line3D(p2, p3, color="#f0883e", thickness=0.045),
        )
        badge_a = RoundedRectangle(corner_radius=0.12, width=5.6, height=1.15, color="#f0883e", fill_color="#161b22", fill_opacity=0.95).to_corner(DL, buff=0.35)
        txt_a = Text("Target A: 3-Hop Chiral Twist (192/512 = 3/8)\nPredicts eta = 5.90e-10 (3.3% from Planck)", font_size=17, color="#ffa657", weight=BOLD).move_to(badge_a)
        self.add_fixed_in_frame_mobjects(badge_a, txt_a)

        self.play(Create(twist_path), FadeIn(badge_a), Write(txt_a), run_time=1.4)
        self.wait(1.6)
        self.play(FadeOut(twist_path), run_time=0.6)

        # Target B: Closed 4-Link BCC Rhombus Glueball Plaquette (1306.1 MeV)
        r0 = np.array([0.0, 0.0, 0.0])
        r1 = np.array([1.0, 1.0, 1.0]) * scale
        r2 = np.array([2.0, 0.0, 0.0]) * scale
        r3 = np.array([1.0, -1.0, -1.0]) * scale

        rhombus = VGroup(
            Line3D(r0, r1, color="#3fb950", thickness=0.05),
            Line3D(r1, r2, color="#3fb950", thickness=0.05),
            Line3D(r2, r3, color="#3fb950", thickness=0.05),
            Line3D(r3, r0, color="#3fb950", thickness=0.05),
        )
        badge_b = RoundedRectangle(corner_radius=0.12, width=5.6, height=1.15, color="#3fb950", fill_color="#161b22", fill_opacity=0.95).to_corner(DR, buff=0.35)
        txt_b = Text("Target B: 4-Link SU(2) Rhombus Plaquette\nEmergent 0++ Glueball Gap = 1306.1 MeV", font_size=17, color="#56d364", weight=BOLD).move_to(badge_b)
        self.add_fixed_in_frame_mobjects(badge_b, txt_b)

        self.play(Create(rhombus), FadeIn(badge_b), Write(txt_b), run_time=1.4)
        self.wait(2.2)
        self.stop_ambient_camera_rotation()
