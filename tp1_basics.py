"""True Position, Part 1: what position means and how to calculate it (2D).

Example part (made up): 4.000 x 3.000 plate, one Ø.500 hole at 1.500 / 1.250 basic
from datums B and C, position Ø.010 to A B C.
"""
from tp_common import *

V = PartView(origin=(-5.6, -2.6), s=1.25)      # plate drawing, screen units per inch
HX, HY, HD = 1.500, 1.250, 0.500                 # basic hole location and size
ZC = np.array([3.7, -0.35, 0])                   # zoom view center (true position)
MAG = 1.25 / 0.005                               # zoom: Ø.010 zone drawn at radius 1.25


def zp(dx, dy):
    return ZC + MAG * np.array([dx, dy, 0])


class TP1Basics(TPScene):
    part_no = 1

    def construct(self):
        self.start("What position means, and how to calculate it",
                   "True position, part one. What position means, and how to calculate it.")

        # --- The part and its basic dimensions --------------------------------
        self.play(*self.section("The part"), run_time=0.5)
        self.tag = tag = Text("Example values for training", font_size=18, color=APW_MUTED).to_corner(UR, buff=0.35)
        plate = V.rect(0, 0, 4, 3)
        hole = V.hole(HX, HY, HD)
        cm = center_mark(V(HX, HY), 0.45)
        self.say("Here's a simple plate with one drilled hole. The print has to say where the center of that hole belongs.",
                 (0.5, DrawBorderThenFill(plate), FadeIn(tag)), (0.3, GrowFromCenter(hole), Create(cm)))

        dx_dim = dim(V(0, 0), V(HX, 0), "1.500", (0, -0.5, 0))
        dy_dim = dim(V(0, 0), V(0, HY), "1.250", (-0.5, 0, 0))
        hx_ext = DashedLine(V(HX, 0), V(HX, HY), dash_length=0.08, color=REF_A, stroke_width=1.5)
        hy_ext = DashedLine(V(0, HY), V(HX, HY), dash_length=0.08, color=REF_A, stroke_width=1.5)
        self.say("These dimensions are basic. The box around the number means it's exact, with no plus or minus tolerance on it.",
                 (0.45, Create(hx_ext), Create(hy_ext), FadeIn(dx_dim), FadeIn(dy_dim)),
                 (0.35, Indicate(dx_dim[-1], color=WHITE), Indicate(dy_dim[-1], color=WHITE)))

        tp_mark = crosshair(V(HX, HY), 0.32, color=REF_A, width=3)
        tp_lbl = callout("True position:\nthe exact, theoretical\ncenter", V(HX, HY) + np.array([0.05, 0.05, 0]),
                         [-3.1, 1.75, 0], color=REF_A)
        self.say("Together they define a point called true position: the exact spot where the hole is supposed to be.",
                 (0.4, GrowFromCenter(tp_mark)), (0.4, show_callout(tp_lbl)))

        self.say("On the print, this control is just called position. True position is the perfect location it's measured from.",
                 (0.6, Indicate(tp_mark, color=WHITE, scale_factor=1.6)))

        self.say("No real hole lands exactly on that point. The question is how far off it's allowed to be, and in which directions.",
                 (0.4, lambda: hole.animate.shift(RIGHT * 0.06 + UP * 0.04)), (0.3, lambda: hole.animate.shift(LEFT * 0.1 + DOWN * 0.07)),
                 (0.2, lambda: hole.animate.move_to(V(HX, HY))))

        # --- Zoom in: plus/minus square vs round zone ---------------------------
        win = Square(0.36, color=WHITE, stroke_width=2.5).move_to(V(HX, HY))
        zoom_bg = panel(6.0, 5.6, ZC + np.array([0, 0.05, 0]))
        zoom_lbl = Text("Zoomed in about 200x", font_size=20, color=APW_LOGO_BLUE).next_to(zoom_bg, UP, buff=0.08)
        rays = VGroup(Line(win.get_corner(UR), zoom_bg[0].get_corner(UL), color=APW_MUTED, stroke_width=1.5),
                      Line(win.get_corner(DR), zoom_bg[0].get_corner(DL), color=APW_MUTED, stroke_width=1.5))
        z_tp = crosshair(ZC, 2.8, color=REF_A, width=1.5)
        scale_bar = VGroup(Line(zp(-0.011, -0.0102), zp(-0.010, -0.0102), color=APW_MUTED, stroke_width=4),
                           Text(".001 in", font_size=18, color=APW_MUTED)).arrange(RIGHT, buff=0.12)
        scale_bar.move_to(zoom_bg[0].get_corner(DR) + np.array([-0.75, 0.3, 0]))
        self.say("Let's zoom way in on true position.",
                 (0.3, FadeOut(tp_lbl), Create(win), *self.section("Square zone vs round zone")),
                 (0.6, FadeIn(zoom_bg), FadeIn(zoom_lbl), Create(rays), Create(z_tp), FadeIn(scale_bar)))

        sq = Square(MAG * 0.010).move_to(ZC).set_stroke(STANDARD, 3).set_fill(STANDARD, 0.15)
        sq_lbl = Text("±.005 in X and Y:\na square zone", font_size=20, color=STANDARD, line_spacing=0.8)
        sq_lbl.next_to(sq, UP, buff=0.12).shift(LEFT * 1.5)
        self.say("With old-style plus or minus dimensions, say plus or minus five thousandths in X and in Y, the hole center has to land in a square.",
                 (0.5, DrawBorderThenFill(sq)), (0.3, FadeIn(sq_lbl)))

        corner = Dot(zp(0.005, 0.005), radius=0.09, color=IMPROVED)
        diag = Line(ZC, zp(0.005, 0.005), color=WHITE, stroke_width=2.5)
        diag_lbl = Text(".0071 from\ntrue position", font_size=20, color=IMPROVED, line_spacing=0.8).move_to(ZC + np.array([2.1, 1.75, 0]))
        self.say("A hole five thousandths off in X and five in Y sits in the corner and passes. "
                 "But that corner is about seventy-one ten-thousandths away from true position.",
                 (0.35, GrowFromCenter(corner)), (0.45, Create(diag), FadeIn(diag_lbl)))

        side = Dot(zp(0.006, 0), radius=0.09, color=PROBLEM)
        side_line = Line(ZC, zp(0.006, 0), color=PROBLEM, stroke_width=2.5)
        side_lbl = Text(".006 off in X only: rejected", font_size=20, color=PROBLEM).next_to(side, DOWN, buff=0.15).shift(LEFT * 0.4)
        self.say("A hole only six thousandths off, straight sideways, falls outside the square and gets rejected, "
                 "even though it's closer to where it belongs.",
                 (0.35, GrowFromCenter(side), Create(side_line)), (0.4, FadeIn(side_lbl)))

        big = Circle(radius=MAG * 0.0070711).move_to(ZC).set_stroke(IMPROVED, 3).set_fill(IMPROVED, 0.08)
        big = DashedVMobject(big, num_dashes=60)
        big_lbl = Text("Round zone through the corners:\nØ.0141, about 57% more area", font_size=20, color=IMPROVED,
                       line_spacing=0.8).move_to(zoom_bg[0].get_bottom() + UP * 0.45)
        self.say("A round zone treats every direction the same. A circle through the square's corners is fourteen thousandths across, "
                 "and gives about fifty-seven percent more area to work with.",
                 (0.4, Create(big)), (0.4, FadeIn(big_lbl), lambda: side.animate.set_color(IMPROVED)))

        zone = Circle(radius=MAG * 0.005).move_to(ZC).set_stroke(IMPROVED, 3.5).set_fill(IMPROVED, 0.18)
        zone_lbl = Text("This print: Ø.010 zone", font_size=22, color=IMPROVED).next_to(zone, UP, buff=0.12)
        self.say("That's position: a round tolerance zone centered on true position. On this print, the designer chose a zone ten thousandths in diameter.",
                 (0.35, FadeOut(VGroup(sq, sq_lbl, corner, diag, diag_lbl, side, side_line, side_lbl, big_lbl)), Transform(big, zone)),
                 (0.3, FadeIn(zone_lbl)))
        self.remove(big)
        self.add(zone)

        # --- Feature control frame --------------------------------------------
        frame = pos_fcf(".010", "A", "B", "C").move_to([-3.1, 1.75, 0])
        leader = Line(frame.get_bottom() + DOWN * 0.02 + LEFT * 0.6, V(HX, HY) + np.array([0.18, 0.18, 0]) ,
                      color=WHITE, stroke_width=2)
        leader.add_tip(tip_length=0.15)
        self.say("On the print, position is called out in a feature control frame, read left to right.",
                 (0.2, FadeOut(win), FadeOut(rays), *self.section("The feature control frame")),
                 (0.5, LaggedStart(*[FadeIn(c, shift=RIGHT * 0.2) for c in frame], lag_ratio=0.3), Create(leader)))

        def hl(i, color=REF_A):
            return frame[i][0].animate.set_stroke(color, 5)

        def unhl(i):
            return frame[i][0].animate.set_stroke(TEXT_COLOR, 2.5)

        self.say("The first box holds the position symbol: a circle with a cross through it.",
                 (0.3, hl(0)), (0.3, Indicate(frame[0][1], color=REF_A, scale_factor=1.4)))
        self.say("Next is the tolerance. The diameter symbol in front of it means the zone is round, ten thousandths across.",
                 (0.25, unhl(0), hl(1)), (0.4, Indicate(zone, color=REF_A, scale_factor=1.05)))

        tag_a = datum_tag("A", V(3.6, 2.6), (1, 1, 0), length=0.35)
        a_note = Text("A = this face", font_size=20, color=TEXT_COLOR).next_to(tag_a, RIGHT, buff=0.1)
        tag_b = datum_tag("B", V(0, 2.3), LEFT, length=0.3)
        tag_c = datum_tag("C", V(3.2, 0), DOWN, length=0.3)
        self.say("Then the datums, in order: A, B and C. They're the surfaces the basic dimensions start from. Part two covers them in detail.",
                 (0.25, unhl(1), hl(2), hl(3), hl(4)),
                 (0.45, LaggedStart(FadeIn(tag_a), FadeIn(a_note), FadeIn(tag_b), FadeIn(tag_c), lag_ratio=0.4)))

        read = Text("The hole's axis must lie inside a Ø.010 zone\ncentered on true position, located from A, B, C",
                    font_size=22, color=WHITE, line_spacing=0.8).move_to([-3.0, 2.75, 0])
        self.say("So the whole frame reads: the axis of this hole must lie inside a ten-thousandths diameter zone, "
                 "centered on true position, located from datums A, B and C.",
                 (0.25, unhl(2), unhl(3), unhl(4)), (0.15, lambda: frame.animate.shift(DOWN * 0.15)), (0.4, FadeIn(read)))

        # --- Calculation -------------------------------------------------------
        part_view = VGroup(plate, hole, cm, dx_dim, dy_dim, hx_ext, hy_ext, tp_mark, tag_a, a_note, tag_b, tag_c, leader)
        self.say("Now let's check a real part.",
                 (0.5, FadeOut(part_view), FadeOut(read), frame.animate.scale(0.85).move_to([-4.2, 2.6, 0]),
                  *self.section("Calculating position")))

        meas = calc_lines("Measured center (CMM):",
                          ("X = 1.503 from datum B", REF_A), ("Y = 1.248 from datum C", REF_B),
                          font_size=22, buff=0.12).move_to([-4.4, 2.05, 0], aligned_edge=UP).align_to(frame, LEFT)
        self.say("The C M M measures the hole's center: X is one point five oh three from datum B, and Y is one point two four eight from datum C.",
                 (0.2, FadeIn(meas[0])), (0.3, FadeIn(meas[1])), (0.3, FadeIn(meas[2])))

        d1 = (0.003, -0.002)
        p1 = Dot(zp(*d1), radius=0.09, color=WHITE)
        dxd = dim(ZC, ZC + np.array([MAG * d1[0], 0, 0]), ".003", (0, 0.35, 0), color=REF_A, basic=False, font_size=20)
        dyd = dim(zp(d1[0], 0), zp(*d1), ".002", (0.4, 0, 0), color=REF_B, basic=False, font_size=20)
        deltas = calc_lines(("Δx = 1.503 − 1.500 = +.003", REF_A), ("Δy = 1.248 − 1.250 = −.002", REF_B),
                            font_size=22, buff=0.12).next_to(meas, DOWN, buff=0.25, aligned_edge=LEFT)
        self.say("Subtract the basic values. Delta X is plus three thousandths. Delta Y is minus two thousandths.",
                 (0.2, GrowFromCenter(p1)), (0.35, FadeIn(deltas[0]), FadeIn(dxd)), (0.35, FadeIn(deltas[1]), FadeIn(dyd)))

        radial = Line(ZC, zp(*d1), color=WHITE, stroke_width=3)
        r_txt = calc_lines("Distance from true position:", "r = √(.003² + .002²) = .0036",
                           font_size=22, buff=0.12).next_to(deltas, DOWN, buff=0.25, aligned_edge=LEFT)
        self.say("The straight-line distance from true position is the square root of delta X squared plus delta Y squared. "
                 "That's thirty-six ten-thousandths.",
                 (0.3, Create(radial)), (0.5, FadeIn(r_txt)))

        dia_txt = calc_lines(("Position = 2 × r = Ø.0072", WHITE), ("Ø.0072 ≤ Ø.010", IMPROVED),
                             font_size=24, buff=0.12).next_to(r_txt, DOWN, buff=0.25, aligned_edge=LEFT)
        ok = pass_fail(True).next_to(dia_txt[1], RIGHT, buff=0.3)
        circ1 = Circle(radius=MAG * 0.0036).move_to(ZC).set_stroke(WHITE, 2)
        self.say("The zone is a diameter, so double it. Position is seventy-two ten-thousandths, inside the ten thousandths allowed. This hole passes.",
                 (0.3, FadeIn(dia_txt[0]), Create(circ1)), (0.3, FadeIn(dia_txt[1]), FadeIn(ok), lambda: p1.animate.set_color(IMPROVED)))

        formula = Text("Position  Ø = 2 × √( Δx² + Δy² )", font_size=34, color=WHITE)
        formula_box = SurroundingRectangle(formula, color=APW_LOGO_BLUE, buff=0.2, corner_radius=0.1)
        fgroup = VGroup(formula_box, formula).move_to([-3.6, -3.3, 0])
        self.say("That's the formula to remember: two times the square root of delta X squared plus delta Y squared.",
                 (0.6, FadeIn(fgroup, shift=UP * 0.2)), (0.3, Indicate(formula, color=REF_A, scale_factor=1.05)))

        # --- Second part: passes each direction, fails position -----------------
        calc1 = VGroup(meas, deltas, r_txt, dia_txt, ok)
        d2 = (0.004, 0.004)
        p2 = Dot(zp(*d2), radius=0.09, color=WHITE)
        dxd2 = dim(ZC, ZC + np.array([MAG * d2[0], 0, 0]), ".004", (0, -0.35, 0), color=REF_A, basic=False, font_size=20)
        dyd2 = dim(zp(d2[0], 0), zp(*d2), ".004", (0.4, 0, 0), color=REF_B, basic=False, font_size=20)
        calc2 = calc_lines("Second part:", ("Δx = +.004", REF_A), ("Δy = +.004", REF_B),
                           "r = √(.004² + .004²) = .0057", ("Position = 2 × .0057 = Ø.0113", PROBLEM),
                           font_size=22, buff=0.14).move_to(calc1, aligned_edge=UL)
        bad = pass_fail(False).next_to(calc2[-1], RIGHT, buff=0.25)
        self.say("A second part. Delta X is four thousandths, and delta Y is four thousandths.",
                 (0.3, FadeOut(calc1), FadeOut(VGroup(p1, dxd, dyd, radial, circ1))),
                 (0.4, FadeIn(calc2[:3]), GrowFromCenter(p2), FadeIn(dxd2), FadeIn(dyd2)))
        self.say("Each one alone would pass a plus or minus five thousandths check. But together, the center is fifty-seven ten-thousandths away, "
                 "so position is eleven point three thousandths. That's outside the zone. This hole fails.",
                 (0.3, FadeIn(calc2[3]), Create(Line(ZC, zp(*d2), color=WHITE, stroke_width=3))),
                 (0.4, FadeIn(calc2[4]), FadeIn(bad), lambda: p2.animate.set_color(PROBLEM)),
                 (0.2, Indicate(zone, color=PROBLEM, scale_factor=1.04)))

        warn = VGroup(Text("Common mistake:", font_size=24, color=PROBLEM, weight=BOLD),
                      Text("reporting r = .0057 as the position.\nAlways double it to compare with the Ø zone.",
                           font_size=22, color=WHITE, line_spacing=0.8)).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        warn.next_to(calc2, DOWN, buff=0.4, aligned_edge=LEFT)
        self.say("A common mistake is reporting the radial distance, fifty-seven ten-thousandths, as the position. "
                 "The zone is a diameter, so always double it before you compare.",
                 (0.5, FadeOut(fgroup), FadeIn(warn, shift=UP * 0.2)), (0.3, Indicate(calc2[4], color=REF_A)))

        # --- A batch of parts ----------------------------------------------------
        self.clear_stage()
        self.play(*self.section("Reading a batch of parts"), run_time=0.5)
        zoom_bg2 = panel(6.0, 5.6, ZC + np.array([0, 0.05, 0]), title="Hole centers, 12 parts (zoomed)")
        z_tp2 = crosshair(ZC, 2.8, color=REF_A, width=1.5)
        zone2 = zone.copy()
        pts = [(0.0021, 0.0012), (0.0030, 0.0004), (0.0016, 0.0025), (0.0042, 0.0018), (0.0027, -0.0006),
               (0.0011, 0.0009), (0.0035, 0.0031), (0.0050, 0.0009), (0.0024, 0.0019), (0.0019, -0.0002),
               (0.0046, 0.0026), (0.0033, 0.0014)]
        dots = VGroup(*[Dot(zp(*p), radius=0.08, color=IMPROVED if zone_dia(*p) <= 0.010 else PROBLEM) for p in pts])
        n_bad = sum(zone_dia(*p) > 0.010 for p in pts)
        tally = calc_lines(("Inside the zone: pass", IMPROVED), (f"Outside: fail ({n_bad})", PROBLEM),
                           font_size=24).move_to([-3.6, 1.4, 0], aligned_edge=UL)
        self.say("Plot the hole centers from a batch of parts, and the zone shows you the story at a glance. Green dots are inside, red are outside.",
                 (0.25, FadeIn(zoom_bg2), Create(z_tp2), FadeIn(zone2)),
                 (0.5, LaggedStart(*[GrowFromCenter(d) for d in dots], lag_ratio=0.15), FadeIn(tally)))

        mx = np.mean([p[0] for p in pts])
        my = np.mean([p[1] for p in pts])
        avg = Dot(zp(mx, my), radius=0.11, color=REF_B)
        shift_arrow = Arrow(ZC, zp(mx, my), buff=0, color=REF_B, stroke_width=5, max_tip_length_to_length_ratio=0.3)
        shift_txt = calc_lines(("Average center:", REF_B), (f"Δx {fmt(mx, 4, True)}   Δy {fmt(my, 4, True)}", REF_B),
                               "The whole batch sits off to one side.", "That points to a setup or offset,",
                               "not random scatter.", font_size=22).next_to(tally, DOWN, buff=0.5, aligned_edge=LEFT)
        self.say("Notice the whole group sits off to one side. When the scatter is shifted like this, look for a work offset or setup problem, "
                 "not a bad spindle. Shift the group back to center and every part passes.",
                 (0.3, GrowFromCenter(avg), GrowArrow(shift_arrow)), (0.3, FadeIn(shift_txt)),
                 (0.3, lambda: [dots.animate.shift(ZC - zp(mx, my)).set_color(IMPROVED), avg.animate.move_to(ZC),
                                FadeOut(shift_arrow)]))

        nxt = Text("Next, Part 2: datums. Position to one, two and three datums,\nand why datum order changes the answer.",
                   font_size=28, color=WHITE, line_spacing=0.9)
        self.clear_stage()
        self.say("Next, in part two: datums. What position controls when you reference one, two or three datums, and why their order changes the answer.",
                 (0.6, FadeIn(nxt, shift=UP * 0.2)))
        self.apw_outro()
