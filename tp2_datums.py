"""True Position, Part 2: datums. Position to one, two and three datums, and datum order.

Example parts (made up):
- 4.000 x 3.000 x .750 plate, Ø.500 hole at 1.500 / 1.250 basic, position Ø.010 to A B C.
- Same hole, position Ø.010 to A only (A perpendicular to the hole).
- 3.000 x 2.000 block with a Ø.375 cross hole 1.000 basic above A (A parallel to the hole).
- Datum order: datum C edge out of square to B by .010 over 4.000.
"""
from tp_common import *

HX, HY = 1.500, 1.250


# --- 3D setup view for 3-2-1 --------------------------------------------------
AZ, EL = 2.3, 0.52                    # looking from the +X +Y side, from above
C3 = np.array([-2.6, -1.2, 0])
S3 = 0.95
L, W, T = 4.0, 3.0, 0.75


def p3(x, y, z):
    return project((x, y, z), AZ, EL, C3, S3)


def quad(a, b, c, d, fill, stroke, opacity=1.0, width=2):
    return Polygon(p3(*a), p3(*b), p3(*c), p3(*d)).set_fill(fill, opacity).set_stroke(stroke, width)


def block3(ox, oy, oz):
    x0, x1, y0, y1, z0, z1 = ox, ox + L, oy, oy + W, oz, oz + T
    top = quad((x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1), STEEL, STANDARD)
    fx = quad((x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1), STEEL_DARK, STANDARD)
    fy = quad((x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1), "#3A4A68", STANDARD)
    hole = Polygon(*[project(p, AZ, EL, C3, S3) for p in circle_pts((ox + HX, oy + HY, z1), 0.25)])
    hole.set_fill(APW_DARK, 1).set_stroke(STANDARD, 2)
    return VGroup(fx, fy, top, hole)


def simulators():
    floor = quad((-0.6, -0.6, 0), (5.2, -0.6, 0), (5.2, 4.2, 0), (-0.6, 4.2, 0), GAUGE, GAUGE, 0.18)
    wall_b = quad((0, -0.6, 0), (0, 4.2, 0), (0, 4.2, 1.5), (0, -0.6, 1.5), REF_A, REF_A, 0.18)
    wall_c = quad((-0.6, 0, 0), (5.2, 0, 0), (5.2, 0, 1.5), (-0.6, 0, 1.5), REF_B, REF_B, 0.18)
    return floor, wall_b, wall_c


def dof_chips():
    names = ["Slide Z", "Tilt about X", "Tilt about Y", "Slide X", "Spin about Z", "Slide Y"]
    chips = VGroup()
    for n in names:
        box = RoundedRectangle(corner_radius=0.1, width=2.7, height=0.5).set_fill(APW_PANEL, 1).set_stroke(APW_MUTED, 2)
        chips.add(VGroup(box, Text(n, font_size=22, color=TEXT_COLOR).move_to(box)))
    chips.arrange(DOWN, buff=0.14).move_to([3.7, -0.5, 0])
    title = Text("Ways the part can move", font_size=22, color=APW_LOGO_BLUE).next_to(chips, UP, buff=0.2)
    return chips, title


def lock(chip, by, color):
    lbl = Text(f"locked by {by}", font_size=16, color=color).next_to(chip, RIGHT, buff=0.1)
    return [chip[0].animate.set_fill(color, 0.35).set_stroke(color, 2.5), FadeIn(lbl)], lbl


class TP2Datums(TPScene):
    part_no = 2

    def construct(self):
        self.start("Datums: position to one, two and three datums",
                   "True position, part two. Datums, and what position controls with one, two or three of them.")
        self.tag = tag = Text("Example values for training", font_size=18, color=APW_MUTED).to_corner(UR, buff=0.35)
        self.add(tag)

        # --- What a datum is ------------------------------------------------------
        self.play(*self.section("What a datum is"), run_time=0.5)
        s = 1.4
        x0, y0 = -2.8, 0.2
        xs = np.linspace(0, 4, 160)
        wav = 0.05 * np.sin(xs * 3.1) + 0.035 * np.sin(xs * 7.3 + 1) + 0.04
        bottom = [[x0 + x * s, y0 + w, 0] for x, w in zip(xs, wav)]
        side = Polygon(*bottom, [x0 + 4 * s, y0 + 0.75 * s, 0], [x0, y0 + 0.75 * s, 0])
        side.set_fill(STEEL_DARK, 1).set_stroke(STANDARD, 3)
        side_lbl = Text("Side view, surface waviness exaggerated", font_size=20, color=APW_MUTED).next_to(side, UP, buff=0.3)
        self.say("Every basic dimension starts from a datum. But a real surface is never perfectly flat.",
                 (0.5, DrawBorderThenFill(side)), (0.3, FadeIn(side_lbl)))

        plate = Rectangle(width=7.2, height=0.6).set_fill(GAUGE, 0.9).set_stroke(GAUGE, 2)
        plate.move_to([x0 + 2 * s, y0 - 2.0, 0])
        plate_lbl = Text("Surface plate", font_size=20, color=APW_DARK).move_to(plate)
        low = min(wav)
        drop = (y0 + low) - plate.get_top()[1]
        highs = [i for i in range(1, len(wav) - 1) if wav[i] <= wav[i - 1] and wav[i] <= wav[i + 1]]
        contacts = sorted(highs, key=lambda i: wav[i])[:2]
        dots = VGroup(*[Dot([x0 + xs[i] * s, plate.get_top()[1], 0], radius=0.07, color=REF_A) for i in contacts])
        dplane = DashedLine([x0 - 0.6, plate.get_top()[1], 0], [x0 + 4 * s + 0.6, plate.get_top()[1], 0],
                            dash_length=0.12, color=REF_A, stroke_width=3)
        dplane_lbl = Text("Datum plane A", font_size=22, color=REF_A).next_to(dplane, LEFT, buff=0.15).shift(UP * 0.35 + RIGHT * 1.6)
        self.say("So the datum isn't the surface itself. It's the perfect plane of the inspection equipment the part rests on, like a surface plate. "
                 "The part sits on its high points.",
                 (0.25, FadeIn(plate, shift=UP * 0.3), FadeIn(plate_lbl)),
                 (0.3, lambda: side.animate.shift(DOWN * drop)),
                 (0.3, LaggedStart(*[GrowFromCenter(d) for d in dots], lag_ratio=0.4), Create(dplane), FadeIn(dplane_lbl)))

        tag_a = datum_tag("A", [x0 + 3.2 * s, side.get_top()[1] - 0.02, 0], UP, length=0.45)
        sym_note = callout("Datum feature symbol:\nmarks the surface the\ndatum comes from", tag_a[2].get_right(), [3.2, 1.6, 0])
        self.say("On the print, a triangle and a lettered box mark the surface the datum comes from, called the datum feature.",
                 (0.4, FadeIn(tag_a)), (0.4, show_callout(sym_note)))
        self.clear_stage()

        # --- One datum, perpendicular to the hole -----------------------------
        self.play(*self.section("One datum, square to the hole"), run_time=0.5)
        sx, sy0, ts = 1.3, -1.6, 1.6
        sec_l = Rectangle(width=(HX - 0.25) * sx, height=0.75 * ts).set_fill(STEEL_DARK, 1).set_stroke(STANDARD, 3)
        sec_l.move_to([-6.2 + (HX - 0.25) * sx / 2, sy0 + 0.375 * ts, 0])
        sec_r = Rectangle(width=(4 - HX - 0.25) * sx, height=0.75 * ts).set_fill(STEEL_DARK, 1).set_stroke(STANDARD, 3)
        sec_r.next_to(sec_l, RIGHT, buff=0.5 * sx)
        axis_x = sec_l.get_right()[0] + 0.25 * sx
        axis = DashedLine([axis_x, sec_l.get_bottom()[1] - 0.4, 0], [axis_x, sec_l.get_top()[1] + 0.4, 0],
                          dash_length=0.12, color=APW_MUTED, stroke_width=2)
        floor_line = Line([-6.6, sec_l.get_bottom()[1], 0], [0.2, sec_l.get_bottom()[1], 0], color=REF_A, stroke_width=3)
        ta = datum_tag("A", [-5.3, sec_l.get_bottom()[1], 0], DOWN, length=0.35)
        f1 = pos_fcf(".010", "A").move_to([-3.4, 1.4, 0])
        sec_lbl = Text("Section through the hole", font_size=20, color=APW_MUTED).next_to(f1, UP, buff=0.35)
        lead1 = Line(f1.get_bottom(), [axis_x + 0.25 * sx, sec_l.get_top()[1], 0], color=WHITE, stroke_width=2).add_tip(tip_length=0.14)
        self.say("Start with position to just one datum. This hole goes straight through face A, so datum A is square to the hole.",
                 (0.45, FadeIn(sec_l), FadeIn(sec_r), Create(axis), Create(floor_line), FadeIn(ta), FadeIn(sec_lbl)),
                 (0.35, FadeIn(f1), Create(lead1)))

        # magnified view of the axis: depth to scale, sideways magnified
        MZ = np.array([3.6, -0.4, 0])
        MX = 1.0 / 0.005          # .005 sideways = 1 unit
        DEP = 3.6                 # screen height of the .750 deep hole
        mag_bg = panel(6.0, 5.4, MZ + np.array([0, 0.1, 0]), title="Hole axis, sideways error magnified")
        z_bot, z_top = MZ[1] - DEP / 2, MZ[1] + DEP / 2

        def mpt(dx, frac):
            return np.array([MZ[0] + dx * MX, z_bot + frac * DEP, 0])

        a_line = Line([MZ[0] - 2.7, z_bot, 0], [MZ[0] + 2.7, z_bot, 0], color=REF_A, stroke_width=3)
        a_lbl = Text("Datum A", font_size=20, color=REF_A).next_to(a_line, DOWN, buff=0.08).align_to(a_line, LEFT)
        ax_actual = Line(mpt(-0.0045, 0), mpt(0.0015, 1), color=WHITE, stroke_width=4)
        ax_lbl = Text("Actual hole axis", font_size=20, color=WHITE).next_to(ax_actual.get_center(), RIGHT, buff=0.9)

        def zone_rect(cx, w=0.010, color=IMPROVED):
            return Rectangle(width=w * MX, height=DEP).move_to([MZ[0] + cx * MX, MZ[1], 0]).set_stroke(color, 3).set_fill(color, 0.15)

        zr = zone_rect(0.0)
        zr_lbl = Text("Green: Ø.010 zone, square to A", font_size=20, color=IMPROVED).move_to([MZ[0] + 1.2, z_bot + 0.3, 0])
        self.say("With only A in the frame, nothing ties the zone to the edges of the part. The zone has to stand square to A, "
                 "but it's free to slide wherever the hole is.",
                 (0.25, FadeIn(mag_bg), Create(a_line), FadeIn(a_lbl), Create(ax_actual), FadeIn(ax_lbl)),
                 (0.25, DrawBorderThenFill(zr), FadeIn(zr_lbl)),
                 (0.15, lambda: zr.animate.shift(RIGHT * 1.2)), (0.15, lambda: zr.animate.shift(LEFT * 2.0)),
                 (0.1, lambda: zr.animate.move_to([MZ[0] - 0.0015 * MX, MZ[1], 0])))

        top_m = Dot(mpt(0.0015, 1), color=REF_B, radius=0.08)
        bot_m = Dot(mpt(-0.0045, 0), color=REF_B, radius=0.08)
        lean = dim(mpt(-0.0045, 1), mpt(0.0015, 1), ".006", (0, 0.15, 0), color=REF_B, basic=False, font_size=20)
        lean_ext = DashedLine(mpt(-0.0045, 0), mpt(-0.0045, 1), dash_length=0.08, color=REF_B, stroke_width=1.5)
        calc = calc_lines("Measure the axis at top and bottom:", ("Top is .006 over from bottom", REF_B),
                          "Smallest zone square to A that holds", "the axis is Ø.006.  Ø.006 ≤ Ø.010",
                          font_size=22).to_edge(LEFT, buff=0.5)
        calc.shift(UP * (2.75 - calc.get_top()[1]))
        tight = zone_rect(-0.0015, 0.006, REF_B)
        ok1 = pass_fail(True).next_to(calc, RIGHT, buff=0.3).align_to(calc[-1], DOWN)
        self.say("To calculate it, measure the hole's axis at the top and at the bottom. Here the top sits six thousandths over from the bottom. "
                 "The smallest zone that stays square to A and still holds the axis is six thousandths across. Position is diameter six thousandths, a pass.",
                 (0.2, FadeOut(f1), FadeOut(lead1), FadeOut(sec_lbl), GrowFromCenter(top_m), GrowFromCenter(bot_m)),
                 (0.25, Create(lean_ext), FadeIn(lean), FadeIn(calc[:2])),
                 (0.35, DrawBorderThenFill(tight), FadeIn(calc[2:]), FadeIn(ok1)))

        perp_note = VGroup(Text("Position to A only, one hole", font_size=22, color=WHITE),
                           Text("= the same as perpendicularity to A", font_size=22, color=REF_A)).arrange(DOWN, buff=0.1)
        perp_fcf = fcf(perp_symbol(), ["Ø", ".010"], "A").scale(0.8)
        pg = VGroup(perp_note, perp_fcf).arrange(DOWN, buff=0.2).to_edge(LEFT, buff=0.6).shift(DOWN * 0.1 + RIGHT * 0.4)
        self.say("With a single hole, position to A alone only controls tilt. It works exactly like a perpendicularity callout.",
                 (0.6, FadeOut(VGroup(sec_l, sec_r, axis, floor_line, ta)), FadeIn(pg)))
        self.clear_stage()

        # --- Pattern to A only --------------------------------------------------------
        self.play(*self.section("A hole pattern to datum A only"), run_time=0.5)
        V = PartView(origin=(-6.0, -2.7), s=1.15)
        plate2 = V.rect(0, 0, 4, 3)
        nom = [(1.0, 0.75), (3.0, 0.75), (1.0, 2.25), (3.0, 2.25)]
        shift_v, rot = np.array([0.22, 0.14]), 0.035  # exaggerated pattern shift and twist, in inches / radians
        cen = np.array([2.0, 1.5])

        def moved(p):
            q = np.array(p) - cen
            c, s_ = np.cos(rot), np.sin(rot)
            return cen + shift_v + np.array([c * q[0] - s_ * q[1], s_ * q[0] + c * q[1]])

        holes = VGroup(*[V.hole(*moved(p), 0.4) for p in nom])
        sp_x = dim(V(*nom[2]) + np.array([0, 0, 0]), V(*nom[3]), "2.000", (0, 0.6, 0), color=REF_A)
        sp_y = dim(V(*nom[1]), V(*nom[3]), "1.500", (0.7, 0, 0), color=REF_A)
        f4 = VGroup(Text("4X", font_size=24), pos_fcf(".010", "A")).arrange(RIGHT, buff=0.15).move_to([3.4, 2.0, 0])
        self.say("Position to A alone still matters for a pattern. Here are four holes, with basic dimensions between the holes, and the frame says four X, "
                 "position ten thousandths to A.",
                 (0.35, DrawBorderThenFill(plate2), FadeIn(holes)), (0.35, FadeIn(sp_x), FadeIn(sp_y), FadeIn(f4)))

        frame_z = VGroup(*[Circle(radius=0.16).move_to(V(*p)).set_stroke(IMPROVED, 3).set_fill(IMPROVED, 0.2) for p in nom])
        links = VGroup(*[DashedLine(frame_z[i].get_center(), frame_z[j].get_center(), dash_length=0.1, color=IMPROVED, stroke_width=2)
                         for i, j in [(0, 1), (1, 3), (3, 2), (2, 0)]])
        zframe = VGroup(links, frame_z)
        z_note = Text("Zones locked to each other\nat basic spacing\n(sizes exaggerated)", font_size=20, color=IMPROVED,
                      line_spacing=0.8).move_to([3.4, 0.4, 0])
        self.say("The four zones are locked to each other at the basic spacing, like a rigid gauge. But as a group, they can slide and turn to fit the holes.",
                 (0.3, FadeIn(zframe), FadeIn(z_note)),
                 (0.4, lambda: zframe.animate.rotate(rot, about_point=V(*cen)).shift(V(*shift_v) - V(0, 0)) ))

        float_note = calc_lines(("Controls:", IMPROVED), "  hole-to-hole spacing", "  each hole square to A",
                                ("Does not control:", PROBLEM), "  where the pattern sits on the plate",
                                font_size=22).move_to([3.4, -1.6, 0])
        self.say("So the callout controls the spacing between the holes and keeps each one square to A. "
                 "Where the whole pattern sits on the plate isn't controlled at all.",
                 (0.45, FadeIn(float_note[:3])), (0.35, FadeIn(float_note[3:]), Indicate(holes, color=REF_B)))
        self.clear_stage()

        # --- One datum, parallel to the hole -------------------------------------
        self.play(*self.section("One datum, parallel to the hole"), run_time=0.5)
        E = PartView(origin=(-6.0, -2.4), s=1.3)
        blk = E.rect(0, 0, 3.0, 2.0)
        cross = E.hole(1.4, 1.0, 0.375)
        e_lbl = Text("End view, looking down the hole", font_size=20, color=APW_MUTED).next_to(blk, UP, buff=0.75)
        h_dim = dim(E(3.0, 0), E(3.0, 1.0), "1.000", (0.55, 0, 0))
        h_ext = DashedLine(E(1.4, 1.0), E(3.0, 1.0), dash_length=0.08, color=REF_A, stroke_width=1.5)
        a_line2 = Line(E(-0.3, 0), E(3.3, 0), color=REF_A, stroke_width=3)
        ta2 = datum_tag("A", E(0.5, 0), DOWN, length=0.3)
        f_par = pos_fcf(".010", "A").scale(0.9).next_to(blk, UP, buff=0.12).align_to(blk, LEFT)
        self.say("Now a different part: a hole drilled sideways, parallel to the bottom face A, one inch up.",
                 (0.4, DrawBorderThenFill(blk), GrowFromCenter(cross), FadeIn(e_lbl)),
                 (0.4, Create(a_line2), FadeIn(ta2), Create(h_ext), FadeIn(h_dim), FadeIn(f_par)))

        band = Rectangle(width=3.6 * 1.3, height=0.3).move_to(E(1.5, 1.0)).set_fill(IMPROVED, 0.15).set_stroke(IMPROVED, 2)
        zcirc = Circle(radius=0.15).move_to(E(1.4, 1.0)).set_stroke(IMPROVED, 3).set_fill(IMPROVED, 0.35)
        band_lbl = Text("Zone held at 1.000 above A,\nfree to slide sideways\n(zone size exaggerated)", font_size=20, color=IMPROVED,
                        line_spacing=0.8).move_to([3.3, 1.6, 0])
        self.say("Position to A locks the zone at exactly one inch above A, and parallel to it. Side to side, nothing holds it.",
                 (0.35, FadeIn(band), GrowFromCenter(zcirc), FadeIn(band_lbl)),
                 (0.2, lambda: [zcirc.animate.shift(RIGHT * 1.2), cross.animate.shift(RIGHT * 1.2)]),
                 (0.2, lambda: [zcirc.animate.shift(LEFT * 2.0), cross.animate.shift(LEFT * 2.0)]))

        # side view of the axis: length to scale, height magnified
        SZ = np.array([3.3, -0.1, 0])
        HM = 0.9 / 0.005
        LEN = 4.6
        sv_bg = panel(5.8, 3.2, SZ + np.array([0, 0.05, 0]), title="Side view, height error magnified")
        nomline = DashedLine(SZ + LEFT * LEN / 2, SZ + RIGHT * LEN / 2, dash_length=0.1, color=REF_A, stroke_width=2)
        bands = VGroup(*[Line(SZ + LEFT * LEN / 2 + UP * k * HM, SZ + RIGHT * LEN / 2 + UP * k * HM, color=IMPROVED, stroke_width=3)
                         for k in (0.005, -0.005)])
        f_end, b_end = SZ + LEFT * LEN / 2 + UP * 0.003 * HM, SZ + RIGHT * LEN / 2 + DOWN * 0.002 * HM
        ax2 = Line(f_end, b_end, color=WHITE, stroke_width=4)
        lbls = VGroup(Text("+.003", font_size=20, color=REF_B).next_to(f_end, UP, buff=0.08),
                      Text("−.002", font_size=20, color=REF_B).next_to(b_end, DOWN, buff=0.08),
                      Text("1.000 from A", font_size=18, color=REF_A).next_to(nomline.get_end(), UP, buff=0.08).shift(LEFT * 0.5))
        calc2 = calc_lines("Height above A at each end:", ("front +.003   back −.002", REF_B),
                           "Position = 2 × worst end = Ø.006", font_size=22).next_to(sv_bg, DOWN, buff=0.15)
        self.say("To calculate it, measure the axis height above A at both ends of the hole. Plus three thousandths at the front, minus two at the back. "
                 "Position is twice the worst end: diameter six thousandths. It passes, and the hole is parallel to A within that zone.",
                 (0.25, FadeOut(band_lbl), FadeIn(sv_bg), Create(nomline), Create(bands)),
                 (0.3, Create(ax2), FadeIn(lbls)), (0.3, FadeIn(calc2)))

        miss = Text("Off .250 sideways?\nThis callout still passes it.", font_size=22, color=PROBLEM, line_spacing=0.8)
        miss.move_to([-3.0, -3.05, 0])
        self.say("Even if the hole were a quarter inch off sideways, this callout would still pass it. To control that direction, you need another datum.",
                 (0.3, lambda: [cross.animate.move_to(E(2.1, 1.0)), zcirc.animate.move_to(E(2.1, 1.0))]),
                 (0.3, FadeIn(miss)))
        self.clear_stage()

        # --- Three datums: 3-2-1 -----------------------------------------------------
        self.play(*self.section("Three datums: 3-2-1"), run_time=0.5)
        floor, wall_b, wall_c = simulators()
        ox, oy, oz = ValueTracker(0.8), ValueTracker(0.7), ValueTracker(1.6)
        blk3 = always_redraw(lambda: block3(ox.get_value(), oy.get_value(), oz.get_value()))
        chips, chips_t = dof_chips()
        wall_b.set_fill(opacity=0).set_stroke(opacity=0)
        wall_c.set_fill(opacity=0).set_stroke(opacity=0)
        self.add(wall_b, wall_c)            # behind the block from the start
        self.say("To fix a hole's location completely, the part has to be locked down in all six ways it can move: three slides, and three rotations.",
                 (0.3, FadeIn(floor), FadeIn(blk3)), (0.5, FadeIn(chips_t), LaggedStart(*[FadeIn(c, shift=LEFT * 0.2) for c in chips], lag_ratio=0.2)))

        fa = pos_fcf(".010", "A", "B", "C").scale(0.8).move_to([-2.6, 2.6, 0])
        fl_lbl = Text("A: surface plate", font_size=20, color=GAUGE).move_to(p3(4.6, 4.0, 0) + DOWN * 0.1)
        a_dots = VGroup(*[Dot(p3(x, y, 0), radius=0.07, color=GAUGE) for x, y in [(0.6, 0.5), (3.5, 0.9), (2.0, 2.6)]])
        an = [lock(chips[i], "A", GAUGE) for i in range(3)]
        self.say("Datum A is primary. The part sits down on the surface plate and touches at least three high points. "
                 "That stops it sliding down, and tilting either way.",
                 (0.1, FadeIn(fa)), (0.1, Indicate(fa[2], color=REF_A)),
                 (0.3, oz.animate.set_value(0)),
                 (0.3, LaggedStart(*[GrowFromCenter(d) for d in a_dots], lag_ratio=0.3), FadeIn(fl_lbl), *an[0][0], *an[1][0], *an[2][0]))

        b_dots = VGroup(*[Dot(p3(0, y, 0.4), radius=0.07, color=REF_A) for y in (0.5, 2.5)])
        bn = [lock(chips[i], "B", REF_A) for i in (3, 4)]
        self.say("Datum B is secondary. The part slides against the B wall and touches at least two points. That stops one slide, and the spin.",
                 (0.15, wall_b.animate.set_fill(opacity=0.18).set_stroke(opacity=1), Indicate(fa[3], color=REF_A)),
                 (0.3, ox.animate.set_value(0)),
                 (0.3, LaggedStart(*[GrowFromCenter(d) for d in b_dots], lag_ratio=0.4), *bn[0][0], *bn[1][0]))

        c_dot = Dot(p3(2.5, 0, 0.4), radius=0.07, color=REF_B)
        cn = lock(chips[5], "C", REF_B)
        self.say("Datum C is tertiary. The part slides over until it touches the C wall at one point. That stops the last slide. Now nothing can move.",
                 (0.15, wall_c.animate.set_fill(opacity=0.18).set_stroke(opacity=1), Indicate(fa[4], color=REF_B)),
                 (0.3, oy.animate.set_value(0)),
                 (0.3, GrowFromCenter(c_dot), *cn[0]))

        rule = Text("3 - 2 - 1", font_size=40, color=WHITE, weight=BOLD).move_to([-5.6, 1.4, 0])
        self.say("Three points, then two, then one. That's why it's called three, two, one. The datum reference frame is now fixed, "
                 "and true position has an exact home in it.",
                 (0.5, FadeIn(rule, shift=UP * 0.2)))
        self.clear_stage()

        # --- Measuring from each datum ---------------------------------------------
        self.play(*self.section("Error from each datum"), run_time=0.5)
        T = PartView(origin=(-5.6, -2.5), s=1.25)
        plate3 = T.rect(0, 0, 4, 3)
        h3 = T.hole(HX + 0.002, HY + 0.001, 0.5)
        rail_b = Rectangle(width=0.18, height=3.6 * 1.25).next_to(T(0, -0.3), LEFT, buff=0, aligned_edge=DOWN)
        rail_b.set_fill(REF_A, 0.6).set_stroke(REF_A, 2)
        rail_c = Rectangle(width=4.6 * 1.25, height=0.18).next_to(T(-0.3, 0), DOWN, buff=0, aligned_edge=LEFT)
        rail_c.set_fill(REF_B, 0.6).set_stroke(REF_B, 2)
        rb_l = Text("B", font_size=26, color=REF_A, weight=BOLD).next_to(rail_b, LEFT, buff=0.1)
        rc_l = Text("C", font_size=26, color=REF_B, weight=BOLD).next_to(rail_c, DOWN, buff=0.1).align_to(rail_c, RIGHT)
        mx_arrow = DoubleArrow(T(0, HY + 0.001), T(HX + 0.002, HY + 0.001), buff=0, color=REF_A, stroke_width=3, tip_length=0.15)
        my_arrow = DoubleArrow(T(HX + 0.002, 0), T(HX + 0.002, HY + 0.001), buff=0, color=REF_B, stroke_width=3, tip_length=0.15)
        mx_l = Text("1.502", font_size=22, color=REF_A).next_to(mx_arrow, UP, buff=0.08).shift(LEFT * 0.4)
        my_l = Text("1.251", font_size=22, color=REF_B).next_to(my_arrow, RIGHT, buff=0.08).shift(DOWN * 0.4)
        top_view_lbl = Text("Top view, part locked against B and C", font_size=20, color=APW_MUTED).next_to(plate3, UP, buff=0.2)
        self.say("Back to the top view, with the part locked against B and C. Each coordinate is measured straight out from its own datum.",
                 (0.3, DrawBorderThenFill(plate3), GrowFromCenter(h3), FadeIn(rail_b), FadeIn(rail_c), FadeIn(rb_l), FadeIn(rc_l),
                  FadeIn(top_view_lbl)),
                 (0.4, GrowFromCenter(mx_arrow), FadeIn(mx_l), GrowFromCenter(my_arrow), FadeIn(my_l)))

        err = calc_lines(("Error from datum B (X):  1.502 − 1.500 = +.002", REF_A),
                         ("Error from datum C (Y):  1.251 − 1.250 = +.001", REF_B),
                         "Combine:  Ø = 2 × √(.002² + .001²)", ("Position = Ø.0045", IMPROVED),
                         font_size=22).move_to([3.4, 0.6, 0])
        ok3 = pass_fail(True).next_to(err[-1], RIGHT, buff=0.3)
        note_a = Text("Datum A sets the zone square to the face.\nB and C each give one direction of error.",
                      font_size=20, color=APW_MUTED, line_spacing=0.8).next_to(err, DOWN, buff=0.4)
        self.say("The error from datum B is plus two thousandths in X. The error from datum C is plus one thousandth in Y. "
                 "Combine them with the formula, and position is forty-five ten-thousandths. A pass.",
                 (0.25, FadeIn(err[0])), (0.25, FadeIn(err[1])), (0.35, FadeIn(err[2:]), FadeIn(ok3)))
        self.say("Datum A keeps the zone square to the face. Datums B and C each give one direction of the error.",
                 (0.5, FadeIn(note_a)))
        self.clear_stage()

        # --- Datum order matters -------------------------------------------------------
        self.play(*self.section("Why datum order matters"), run_time=0.5)
        skew = 0.010 / 4.0                # true out-of-square of edge C
        vis = 0.06                        # drawn tilt, exaggerated
        hole_true = np.array([1.502, 1.251])
        D = PartView(origin=(-6.0, -2.1), s=1.05)

        def skew_plate():
            pts = [D(0, 0), D(4, 4 * vis), D(4, 3), D(0, 3)]
            return Polygon(*pts).set_fill(STEEL_DARK, 1).set_stroke(STANDARD, 3)

        def frames(order):
            if order == "BC":
                return VGroup(Line(D(0, -0.3), D(0, 3.3), color=REF_A, stroke_width=6),
                              Line(D(-0.3, 0), D(4.3, 0), color=REF_B, stroke_width=6))
            ang = np.arctan(vis)
            c_line = Line(D(-0.3, -0.3 * vis), D(4.3, 4.3 * vis), color=REF_B, stroke_width=6)
            b_line = Line(D(0, 0) + rotate_vector(LEFT * 0.0, ang), D(0, 0) + rotate_vector(UP * 3.6 * 1.05, ang),
                          color=REF_A, stroke_width=6)
            return VGroup(b_line, c_line)

        sp = skew_plate()
        sh = Circle(radius=0.25 * 1.05).move_to(D(*hole_true)).set_fill(APW_DARK, 1).set_stroke(STANDARD, 2.5)
        exag = Text("Edge C is .010 out of square over 4 in.\n(tilt exaggerated)", font_size=20, color=PROBLEM, line_spacing=0.8)
        exag.next_to(D(2, 0), DOWN, buff=0.5)
        self.say("Datum order matters whenever the datum features aren't perfectly square to each other. On this part, edge C is ten thousandths out of square to edge B.",
                 (0.4, DrawBorderThenFill(sp), GrowFromCenter(sh)), (0.4, FadeIn(exag)))

        fbc = pos_fcf(".010", "A", "B", "C").scale(0.75)
        fcb = pos_fcf(".010", "A", "C", "B").scale(0.75)
        fbc.move_to([3.5, 2.6, 0])
        fr1 = frames("BC")
        contacts1 = VGroup(*[Dot(D(0, y), radius=0.07, color=REF_A) for y in (0.4, 2.6)], Dot(D(0, 0), radius=0.07, color=REF_B))
        r1 = calc_lines("B second: part squared to edge B,", "C touches only its low corner.",
                        ("Δx = +.002   Δy = +.001", WHITE), ("Position Ø.0045", IMPROVED), font_size=22).next_to(fbc, DOWN, buff=0.3)
        ok_bc = pass_fail(True).next_to(r1[-1], RIGHT, buff=0.3)
        self.say("With B before C, the part is squared up to edge B with two points, and C only touches at its low corner. "
                 "Measured that way, position is forty-five ten-thousandths. It passes.",
                 (0.25, FadeIn(fbc), Create(fr1)), (0.3, FadeIn(contacts1), FadeIn(r1[:2])), (0.3, FadeIn(r1[2:]), FadeIn(ok_bc)))

        c, s_ = np.cos(skew), np.sin(skew)
        xp = hole_true[0] * c + hole_true[1] * s_
        yp = -hole_true[0] * s_ + hole_true[1] * c
        dxp, dyp = xp - HX, yp - HY
        pos_cb = zone_dia(dxp, dyp)
        fcb.next_to(r1, DOWN, buff=0.5).align_to(fbc, LEFT)
        fr2 = frames("CB")
        contacts2 = VGroup(*[Dot(D(x, x * vis), radius=0.07, color=REF_B) for x in (0.5, 3.5)], Dot(D(0, 0), radius=0.07, color=REF_A))
        r2 = calc_lines("C second: part squared to edge C,", "B touches only one point.",
                        (f"Δx = {fmt(dxp, 4, True)}   Δy = {fmt(dyp, 4, True)}", WHITE),
                        (f"Position Ø{fmt(pos_cb, 4)}", PROBLEM), font_size=22).next_to(fcb, DOWN, buff=0.3)
        bad_cb = pass_fail(pos_cb <= 0.010).next_to(r2[-1], RIGHT, buff=0.3)
        self.say("Now swap them: C before B. The part is squared up to the crooked edge C instead, and the whole measuring frame turns with it. "
                 f"Same hole, but now delta X is about fifty-one ten-thousandths, and position comes out at about {pos_cb * 1000:.1f} thousandths. It fails.",
                 (0.25, FadeIn(fcb), FadeOut(contacts1), Transform(fr1, fr2)),
                 (0.3, FadeIn(contacts2), FadeIn(r2[:2])), (0.3, FadeIn(r2[2:]), FadeIn(bad_cb)))

        lesson = Text("Same part, same hole. Set up in the order the frame lists.", font_size=26, color=REF_A)
        lesson.to_edge(DOWN, buff=0.35).shift(RIGHT * 1.0)
        self.say("Same part, same hole, two different answers. Always set the part up in the exact order the frame lists the datums.",
                 (0.5, FadeOut(exag), FadeIn(lesson, shift=UP * 0.2)))
        self.clear_stage()

        # --- 2009 vs 2018 ----------------------------------------------------------------
        self.play(*self.section("2009 and 2018"), run_time=0.5)
        rx0, ry0 = -6.4, -0.6
        xs2 = np.linspace(0, 4, 120)
        bump = 0.09 * np.exp(-((xs2 - 2.0) ** 2) / 0.35)
        rpts = [[rx0 + x * 1.3, ry0 - b, 0] for x, b in zip(xs2, bump)]
        rock = Polygon(*rpts, [rx0 + 5.2, ry0 + 0.9, 0], [rx0, ry0 + 0.9, 0]).set_fill(STEEL_DARK, 1).set_stroke(STANDARD, 3)
        splate = Rectangle(width=6.4, height=0.5).set_fill(GAUGE, 0.9).set_stroke(GAUGE, 2)
        splate.next_to(rock, DOWN, buff=0)
        pivot = np.array([rx0 + 2.6, splate.get_top()[1], 0])
        rock.shift(UP * (splate.get_top()[1] - (ry0 - 0.09)))
        rock_lbl = Text("A face with a high spot rocks on the plate\n(exaggerated)", font_size=20, color=APW_MUTED,
                        line_spacing=0.8).next_to(splate, DOWN, buff=0.3)
        self.say("Both editions of A S M E Y fourteen point five use these same datum ideas. Most of our prints call out the two thousand nine edition. "
                 "One difference shows up when a datum face rocks.",
                 (0.3, FadeIn(splate), FadeIn(rock), FadeIn(rock_lbl)),
                 (0.2, Rotate(rock, 0.05, about_point=pivot)), (0.25, Rotate(rock, -0.1, about_point=pivot)),
                 (0.2, Rotate(rock, 0.05, about_point=pivot)))

        y09 = VGroup(Text("2009", font_size=30, color=STANDARD, weight=BOLD),
                     Text("Calls the gauge surfaces datum feature simulators.\nA rocking datum face leaves a choice\nof candidate datums.",
                          font_size=21, color=WHITE, line_spacing=0.85)).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        y18 = VGroup(Text("2018", font_size=30, color=IMPROVED, weight=BOLD),
                     Text("Calls the perfect theoretical gauge the\n\"true geometric counterpart.\" By default, a rocking\nface is settled to one solution that minimizes\nthe separation.",
                          font_size=21, color=WHITE, line_spacing=0.85)).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        cmp_ = VGroup(y09, y18).arrange(DOWN, aligned_edge=LEFT, buff=0.45).move_to([3.6, 0.4, 0])
        self.say("Under two thousand nine, a rocking face can leave a choice of candidate datums. "
                 "The two thousand eighteen edition settles it by default: the part is adjusted to a single solution that minimizes the gap. "
                 "It also renames the perfect theoretical gauge the true geometric counterpart.",
                 (0.35, FadeIn(y09)), (0.4, FadeIn(y18)))
        chk = Text("Check the print's title block for which edition applies.", font_size=24, color=REF_A).to_edge(DOWN, buff=0.4)
        self.say("Always check the title block or notes to see which edition the print calls out.", (0.5, FadeIn(chk)))

        nxt = Text("Next, Part 3: into 3D. The zone is a cylinder,\nand the hole's tilt counts.", font_size=28, color=WHITE,
                   line_spacing=0.9)
        self.clear_stage()
        self.say("Next, in part three, we go into three D. The tolerance zone is really a cylinder, and the hole's tilt counts.",
                 (0.6, FadeIn(nxt, shift=UP * 0.2)))
        self.apw_outro()
