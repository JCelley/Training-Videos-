"""True Position, Part 4: material modifiers. MMC, LMC, RFS, bonus tolerance, virtual condition,
zero at MMC, and datum features at MMB (datum shift).

Example values (made up): hole Ø.500-.505, position Ø.010 to A B C.
Clearances and offsets are drawn magnified.
"""
from tp_common import *

H_MMC, H_LMC, TOL = 0.500, 0.505, 0.010


# --- Allowed-position chart, built from lines (no LaTeX) ------------------------
CH_O = np.array([1.0, -2.9, 0])     # screen origin of the chart (size .490, tol 0)
CH_W, CH_H = 5.2, 3.6
SZ0, SZ1, T1 = 0.490, 0.505, 0.020


def cpt(size, tol):
    return CH_O + np.array([(size - SZ0) / (SZ1 - SZ0) * CH_W, tol / T1 * CH_H, 0])


def chart_frame():
    g = VGroup(Line(cpt(SZ0, 0), cpt(SZ1, 0) + RIGHT * 0.2, color=APW_MUTED, stroke_width=2),
               Line(cpt(SZ0, 0), cpt(SZ0, T1) + UP * 0.1, color=APW_MUTED, stroke_width=2))
    for s in (0.490, 0.495, 0.500, 0.505):
        g.add(Line(cpt(s, 0), cpt(s, 0) + DOWN * 0.08, color=APW_MUTED),
              Text(fmt(s), font_size=18, color=APW_MUTED).next_to(cpt(s, 0), DOWN, buff=0.12))
    for t in (0.005, 0.010, 0.015, 0.020):
        g.add(DashedLine(cpt(SZ0, t), cpt(SZ1, t), dash_length=0.05, color=APW_PANEL, stroke_width=1.5),
              Text(fmt(t), font_size=18, color=APW_MUTED).next_to(cpt(SZ0, t), LEFT, buff=0.1))
    g.add(Text("Actual hole size", font_size=20, color=APW_MUTED).next_to(cpt((SZ0 + SZ1) / 2, 0), DOWN, buff=0.45),
          Text("Allowed\nposition Ø", font_size=20, color=APW_MUTED, line_spacing=0.8).next_to(cpt(SZ0, T1), UP, buff=0.15))
    return g


def chart_line(pts, color, width=5):
    return VMobject().set_points_as_corners([cpt(*p) for p in pts]).set_stroke(color, width)


class TP4Modifiers(TPScene):
    part_no = 4

    def construct(self):
        self.start("Material modifiers and bonus tolerance",
                   "True position, part four. Material modifiers, and bonus tolerance.")
        self.tag = Text("Example values. Clearances magnified.", font_size=18, color=APW_MUTED).to_corner(UR, buff=0.35)
        self.add(self.tag)

        # --- MMC and LMC ------------------------------------------------------------
        self.play(*self.section("Maximum and least material"), run_time=0.5)
        HC = np.array([-3.6, -0.6, 0])
        K = 60.0                     # magnification for size changes

        def hole_r(size):
            return 1.4 + (size - H_MMC) / 2 * K

        size = ValueTracker(H_MMC)
        blockh = Square(4.6).move_to(HC).set_fill(STEEL_DARK, 1).set_stroke(STANDARD, 3)
        hole = always_redraw(lambda: Circle(radius=hole_r(size.get_value())).move_to(HC).set_fill(APW_DARK, 1)
                             .set_stroke(STANDARD, 3))
        size_txt = always_redraw(lambda: Text(f"Hole Ø{fmt(size.get_value(), 4)}", font_size=26, color=WHITE)
                                 .next_to(blockh, UP, buff=0.2))
        callout_sz = Text("Print: Ø.500 – .505", font_size=24, color=WHITE).move_to([2.8, 2.4, 0])
        self.say("This hole can be anywhere from five hundred to five oh five thousandths in diameter.",
                 (0.4, FadeIn(blockh), FadeIn(hole), FadeIn(size_txt)), (0.4, FadeIn(callout_sz)))

        mmc_lbl = VGroup(Text("MMC: maximum material condition", font_size=24, color=REF_A, weight=BOLD),
                         Text("the most metal left on the part.\nFor a hole: the smallest size, Ø.500", font_size=22,
                              color=WHITE, line_spacing=0.8)).arrange(DOWN, aligned_edge=LEFT, buff=0.1).move_to([3.0, 1.0, 0])
        lmc_lbl = VGroup(Text("LMC: least material condition", font_size=24, color=REF_B, weight=BOLD),
                         Text("the least metal left on the part.\nFor a hole: the largest size, Ø.505", font_size=22,
                              color=WHITE, line_spacing=0.8)).arrange(DOWN, aligned_edge=LEFT, buff=0.1).move_to([3.0, -1.0, 0])
        self.say("At its smallest, the most metal is left on the part. That's maximum material condition, or M M C. For a hole, M M C is the smallest size.",
                 (0.6, FadeIn(mmc_lbl)), (0.2, Indicate(hole, color=REF_A)))
        self.say("At its largest, the least metal is left. That's least material condition, L M C. For a hole, that's the biggest size.",
                 (0.4, size.animate.set_value(H_LMC)), (0.4, FadeIn(lmc_lbl)))
        pin_note = Text("For a pin it's reversed:\nMMC = largest pin,  LMC = smallest pin", font_size=22, color=APW_LOGO_BLUE,
                        line_spacing=0.8).move_to([3.0, -2.8, 0])
        self.say("For a pin or a shaft, it's the other way around: M M C is the largest pin, because that leaves the most metal.",
                 (0.6, FadeIn(pin_note)), (0.3, size.animate.set_value(H_MMC)))
        self.clear_stage()

        # --- RFS, then MMC and bonus ----------------------------------------------------
        self.play(*self.section("RFS: the default"), run_time=0.5)
        size2 = ValueTracker(H_MMC)
        mod = ValueTracker(0)   # 0 = RFS, 1 = MMC

        def allowed(s, m):
            return TOL + m * (s - H_MMC)

        ZC = np.array([-3.6, -1.3, 0])
        ZM = 1.0 / 0.005
        hole2 = always_redraw(lambda: Circle(radius=0.55 + (size2.get_value() - H_MMC) * 40).move_to(ZC + LEFT * 2.4 + UP * 3.3)
                              .set_fill(APW_DARK, 1).set_stroke(STANDARD, 3))
        hole2_bg = Square(1.9).move_to(ZC + LEFT * 2.4 + UP * 3.3).set_fill(STEEL_DARK, 1).set_stroke(STANDARD, 2)
        zone = always_redraw(lambda: Circle(radius=allowed(size2.get_value(), mod.get_value()) / 2 * ZM).move_to(ZC)
                             .set_fill(IMPROVED, 0.2).set_stroke(IMPROVED, 3))
        tp = crosshair(ZC, 1.6, color=REF_A, width=1.5)
        read = always_redraw(lambda: calc_lines(f"Hole size:  Ø{fmt(size2.get_value(), 4)}",
                                                (f"Allowed position:  Ø{fmt(allowed(size2.get_value(), mod.get_value()), 4)}", IMPROVED),
                                                font_size=24).move_to([-3.6, -3.25, 0]))
        f_rfs = pos_fcf(".010", "A", "B", "C").scale(0.85).move_to([-3.0, 2.55, 0])
        self.say("With no modifier in the frame, the tolerance applies regardless of feature size, called R F S. "
                 "Under rule number two, that's the default.",
                 (0.3, FadeIn(f_rfs), FadeIn(hole2_bg), FadeIn(hole2), Create(tp), FadeIn(zone), FadeIn(read)))
        self.say("Make the hole bigger or smaller, and the zone doesn't change. It's always ten thousandths.",
                 (0.4, lambda: size2.animate.set_value(H_LMC)), (0.4, lambda: size2.animate.set_value(H_MMC)))

        frame_c = chart_frame()
        rfs_line = chart_line([(H_MMC, TOL), (H_LMC, TOL)], STANDARD)
        rfs_lbl = Text("RFS", font_size=22, color=STANDARD, weight=BOLD).next_to(cpt(H_LMC, TOL), RIGHT, buff=0.1)
        self.say("On a chart of allowed position against hole size, R F S is a flat line.",
                 (0.3, FadeIn(frame_c)), (0.4, Create(rfs_line), FadeIn(rfs_lbl)))

        self.play(*self.section("MMC and bonus tolerance"), run_time=0.5)
        f_mmc = pos_fcf(".010", "A", "B", "C", mod="M").scale(0.85).move_to(f_rfs)
        self.say("Now add the M M C modifier: a circled M after the tolerance.",
                 (0.5, FadeOut(f_rfs), FadeIn(f_mmc), mod.animate.set_value(1)),
                 (0.3, Indicate(f_mmc[1][1][-1], color=REF_A, scale_factor=1.6)))
        self.say("At M M C, five hundred, the zone is ten thousandths. As the hole grows away from M M C, the zone grows by the same amount. "
                 "At five oh five, the zone is fifteen thousandths.",
                 (0.3, Indicate(zone, color=WHITE, scale_factor=1.05)), (0.5, size2.animate.set_value(H_LMC)))
        mmc_line = chart_line([(H_MMC, TOL), (H_LMC, TOL + (H_LMC - H_MMC))], IMPROVED)
        mmc_lbl = Text("MMC", font_size=22, color=IMPROVED, weight=BOLD).next_to(cpt(H_LMC, 0.015), RIGHT, buff=0.1)
        bonus_br = DoubleArrow(cpt(H_LMC, TOL), cpt(H_LMC, 0.015), buff=0, color=REF_B, stroke_width=3, tip_length=0.12)
        bonus_l = Text("bonus", font_size=20, color=REF_B).next_to(bonus_br, LEFT, buff=0.08)
        formula = VGroup(Text("Bonus = actual size − MMC size", font_size=26, color=REF_B),
                         Text("Allowed = stated tolerance + bonus", font_size=26, color=IMPROVED)).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        fbox = VGroup(SurroundingRectangle(formula, color=APW_LOGO_BLUE, buff=0.18, corner_radius=0.1), formula).move_to([3.6, 2.7, 0])
        self.say("The extra is called bonus tolerance. Bonus equals the actual hole size minus the M M C size. Allowed position is the stated tolerance plus the bonus.",
                 (0.3, Create(mmc_line), FadeIn(mmc_lbl)), (0.25, GrowFromCenter(bonus_br), FadeIn(bonus_l)), (0.35, FadeIn(fbox)))

        # --- Worked example ---------------------------------------------------------------
        self.play(*self.section("Worked example"), size2.animate.set_value(0.5035), run_time=0.8)
        dx, dy = 0.005, 0.0035
        pos = zone_dia(dx, dy)
        dot = Dot(ZC + ZM * np.array([dx, dy, 0]), radius=0.08, color=WHITE)
        rfs_ring = DashedVMobject(Circle(radius=TOL / 2 * ZM).move_to(ZC).set_stroke(STANDARD, 3), num_dashes=40)
        ex = calc_lines("Measured: size Ø.5035,  Δx +.005,  Δy +.0035",
                        f"Position = 2 × √(.005² + .0035²) = Ø{fmt(pos, 4)}",
                        ("RFS:  Ø.0122 > Ø.010", PROBLEM),
                        ("MMC:  bonus = .5035 − .500 = .0035", REF_B),
                        ("allowed = .010 + .0035 = Ø.0135 ≥ Ø.0122", IMPROVED),
                        font_size=20, buff=0.1).move_to([-3.4, 1.4, 0])
        ex[0].set_color(WHITE)
        self.say("A real part. The hole measures five oh three five. Delta X is five thousandths, delta Y is thirty-five ten-thousandths. "
                 f"Position comes out to twelve point two thousandths.",
                 (0.25, FadeOut(hole2), FadeOut(hole2_bg), FadeIn(ex[0])), (0.25, GrowFromCenter(dot)), (0.3, FadeIn(ex[1])))
        rfs_fail = pass_fail(False).scale(0.7).next_to(ex[2], RIGHT, buff=0.2)
        mmc_pass = pass_fail(True).move_to(ZC + np.array([2.1, -0.4, 0]))
        self.say("Under R F S, that fails: twelve point two is more than ten. "
                 "But at M M C, the hole is thirty-five ten-thousandths bigger than M M C. That's the bonus. "
                 "The allowed zone is thirteen point five thousandths, so the part passes.",
                 (0.2, FadeIn(ex[2]), FadeIn(rfs_fail), Create(rfs_ring)), (0.3, FadeIn(ex[3])), (0.3, FadeIn(ex[4]), FadeIn(mmc_pass),
                                                                                          lambda: dot.animate.set_color(IMPROVED)))
        self.say("Always measure the actual size of the hole first. Without it, you can't work out the bonus.",
                 (0.5, Indicate(ex[0], color=REF_A)))
        self.clear_stage()

        # --- Why it's fair: virtual condition and gauges -----------------------------------
        self.play(*self.section("Virtual condition"), run_time=0.5)
        GC = np.array([-3.0, -0.5, 0])
        KK = 150.0
        PIN = 0.490

        def r_disp(d):
            return 1.3 + (d - PIN) / 2 * KK

        hs = ValueTracker(H_MMC)
        off = ValueTracker(0.0)
        pin = Circle(radius=r_disp(PIN)).move_to(GC).set_fill(GAUGE, 1).set_stroke(GAUGE, 2)
        pin_l = Text("Gauge pin\nØ.490", font_size=22, color=APW_DARK, line_spacing=0.8).move_to(GC)
        tp2 = crosshair(GC, 2.5, color=REF_A, width=1.5)

        def ring():
            d = hs.get_value()
            c = GC + RIGHT * off.get_value() * KK
            return VGroup(Annulus(inner_radius=r_disp(d), outer_radius=r_disp(d) + 0.4).move_to(c).set_fill(STEEL_DARK, 0.9)
                          .set_stroke(width=0),
                          Circle(radius=r_disp(d)).move_to(c).set_stroke(STANDARD, 3))
        wall = always_redraw(ring)
        vc = calc_lines(("Virtual condition (hole)", REF_A), "= MMC size − position tolerance", "= .500 − .010 = Ø.490",
                        font_size=24).move_to([3.6, 1.6, 0])
        self.say("Why is that bonus safe? Take the smallest hole, five hundred, and the largest position error allowed at that size, "
                 "ten thousandths. The worst-case space left inside is a perfect pin four ninety in diameter.",
                 (0.25, FadeIn(pin), FadeIn(pin_l), Create(tp2), FadeIn(wall)),
                 (0.35, off.animate.set_value(0.005)), (0.3, FadeIn(vc)))
        self.say("That boundary is called the virtual condition. It's the M M C size minus the position tolerance.",
                 (0.5, Indicate(vc[2], color=REF_A)))

        big_note = calc_lines("Hole at Ø.505 (LMC):", "can be off .0075 each way,", ("a Ø.015 zone, and still clears the pin", IMPROVED),
                              font_size=22).move_to([3.6, -0.9, 0])
        self.say("Now make the hole bigger. A five oh five hole can move seven and a half thousandths off center, and it still clears the same pin. "
                 "That extra movement is exactly the bonus.",
                 (0.3, off.animate.set_value(0.0), hs.animate.set_value(H_LMC)), (0.35, lambda: off.animate.set_value(0.0075)),
                 (0.25, FadeIn(big_note)))
        surf = Text("Y14.5 calls this the surface interpretation: the hole's surface\nmust stay outside the Ø.490 boundary at true position.",
                    font_size=18, color=APW_MUTED, line_spacing=0.8).move_to([3.7, -2.6, 0])
        self.say("This is the M M C idea. As long as the hole's surface never crosses the four ninety boundary at true position, a fastener of that size will always fit.",
                 (0.6, FadeIn(surf)))

        # functional gauge, side section
        self.clear_stage()
        self.play(*self.section("A functional gauge"), run_time=0.5)
        base = Rectangle(width=7.0, height=0.5).set_fill(GAUGE, 1).set_stroke(GAUGE, 2).move_to([-1.0, -2.6, 0])
        rail = Rectangle(width=0.4, height=1.6).set_fill(GAUGE, 1).set_stroke(GAUGE, 2).next_to(base, UP, buff=0).align_to(base, LEFT)
        gpin = Rectangle(width=0.98, height=1.6).set_fill(GAUGE, 1).set_stroke(REF_A, 2).next_to(base, UP, buff=0).shift(LEFT * 0.6)
        g_lbl = VGroup(Text("Datum A: gauge base", font_size=20, color=GAUGE), Text("Datum B rail", font_size=20, color=GAUGE),
                       Text("Pin Ø.490 at true position", font_size=20, color=REF_A))
        g_lbl[0].next_to(base, DOWN, buff=0.15)
        g_lbl[1].next_to(rail, LEFT, buff=0.15)
        g_lbl[2].move_to([3.6, -1.2, 0])
        arr = Arrow(g_lbl[2].get_left(), gpin.get_top() + UP * 0.1, buff=0.1, color=REF_A, stroke_width=3)
        left_w = gpin.get_left()[0] - 0.08 - rail.get_right()[0]
        part_l = Rectangle(width=left_w, height=0.9).set_fill(STEEL_DARK, 1).set_stroke(STANDARD, 3)
        part_r = Rectangle(width=2.6, height=0.9).set_fill(STEEL_DARK, 1).set_stroke(STANDARD, 3)
        part_l.move_to([rail.get_right()[0] + left_w / 2, base.get_top()[1] + 0.45 + 3.0, 0])
        part_r.next_to(part_l, RIGHT, buff=0.98 + 0.16)
        part = VGroup(part_l, part_r)
        self.say("That's why a functional gauge works. It has the datum surfaces, and a pin at the virtual condition size, sitting at true position.",
                 (0.4, FadeIn(base), FadeIn(rail), FadeIn(gpin), FadeIn(g_lbl)), (0.3, GrowArrow(arr)))
        ok_g = Text("Part drops on: position is good,\nwith every bit of bonus counted", font_size=24, color=IMPROVED,
                    line_spacing=0.8).move_to([3.4, 1.4, 0])
        self.say("If the part drops onto the gauge, seated on the datums, position is good, with all the bonus counted automatically. "
                 "Gauges like this only work with M M C.",
                 (0.4, part.animate.shift(DOWN * 3.0)), (0.4, FadeIn(ok_g)))
        self.clear_stage()

        # --- LMC -----------------------------------------------------------------------------
        self.play(*self.section("LMC: protecting a wall"), run_time=0.5)
        f_lmc = pos_fcf(".010", "A", "B", "C", mod="L").scale(0.85).move_to([-3.0, 2.55, 0])
        WE = np.array([-6.0, -2.4, 0])
        S = 7.0                       # screen units per inch, close-up of the edge
        edge_d = 0.400
        lsz = ValueTracker(H_LMC)
        lmod = ValueTracker(1)

        def l_allowed(s_):
            return TOL + (H_LMC - s_)

        def wall_view():
            s_ = lsz.get_value()
            zone_r = l_allowed(s_) / 2
            c = WE + RIGHT * S * (edge_d - zone_r)       # hole shifted toward the edge by the full zone radius
            g = VGroup(Rectangle(width=S * 0.9, height=4.6).move_to(WE + RIGHT * S * 0.45 + UP * 1.9)
                       .set_fill(STEEL_DARK, 1).set_stroke(STANDARD, 3))
            g.add(Circle(radius=S * s_ / 2).move_to(c + UP * 1.9).set_fill(APW_DARK, 1).set_stroke(STANDARD, 3))
            wall_t = edge_d - zone_r - s_ / 2
            p0 = WE + UP * 1.9
            p1 = c + UP * 1.9 + LEFT * S * s_ / 2
            g.add(DoubleArrow(p0, p1, buff=0, color=REF_B, stroke_width=3, tip_length=0.12),
                  Text(f"min wall {fmt(wall_t, 4)}", font_size=22, color=REF_B).next_to(p0, DOWN, buff=0.15, aligned_edge=LEFT).shift(RIGHT * 0.1))
            g.add(Text(f"Hole Ø{fmt(s_, 4)}   allowed Ø{fmt(l_allowed(s_), 4)}", font_size=22, color=WHITE)
                  .move_to(WE + RIGHT * 3.2 + DOWN * 0.15))
            return g

        wv = always_redraw(wall_view)
        self.say("The opposite modifier is L M C, a circled L. It's used to protect a minimum wall, like a hole close to an edge.",
                 (0.3, FadeIn(f_lmc)), (0.4, FadeIn(wv)))
        l_txt = calc_lines(("Bonus = LMC size − actual size", REF_B), "At Ø.505 (LMC): zone Ø.010",
                           "At Ø.500 (MMC): zone Ø.015", font_size=22).move_to([3.7, 1.4, 0])
        self.say("Now the bonus goes the other way. The zone is ten thousandths at L M C, the largest hole, and grows as the hole gets smaller.",
                 (0.3, FadeIn(l_txt[0])), (0.25, FadeIn(l_txt[1])), (0.35, lsz.animate.set_value(H_MMC), FadeIn(l_txt[2])))
        const = Text("Worst-case wall stays the same\nat every hole size.", font_size=24, color=IMPROVED, line_spacing=0.8).move_to([3.7, -0.6, 0])
        self.say("Watch the minimum wall while the hole changes size, with the hole pushed to the edge of its zone. "
                 "It never changes. L M C guarantees the wall, at every size.",
                 (0.35, lambda: lsz.animate.set_value(H_LMC)), (0.3, lambda: lsz.animate.set_value(0.502)), (0.2, FadeIn(const)))
        self.clear_stage()

        # --- Zero at MMC -------------------------------------------------------------------------
        self.play(*self.section("Zero tolerance at MMC"), run_time=0.5)
        frame_c2 = chart_frame()
        mmc_line2 = chart_line([(H_MMC, TOL), (H_LMC, 0.015)], IMPROVED, width=12)
        zero_line = chart_line([(0.490, 0.0), (H_LMC, 0.015)], REF_A)
        f_zero = VGroup(Text("Ø.490 – .505", font_size=24, color=WHITE),
                        pos_fcf(".000", "A", "B", "C", mod="M")).arrange(DOWN, buff=0.15).scale(0.85).move_to([-3.6, 2.2, 0])
        f_norm = VGroup(Text("Ø.500 – .505", font_size=24, color=WHITE),
                        pos_fcf(".010", "A", "B", "C", mod="M")).arrange(DOWN, buff=0.15).scale(0.85).move_to([-3.6, 0.3, 0])
        f_norm[1].set_color(IMPROVED)
        f_zero[1].set_color(REF_A)
        self.say("Some prints use zero position tolerance at M M C. Here's our hole the normal way, and the same hole with zero at M M C, "
                 "and the size range opened up to four ninety.",
                 (0.3, FadeIn(frame_c2), FadeIn(f_norm), Create(mmc_line2)), (0.4, FadeIn(f_zero), Create(zero_line)))
        same_vc = calc_lines("Both have the same virtual condition:", ".500 − .010 = .490", ".490 − .000 = .490",
                             ("Same gauge, same fit,", IMPROVED), ("more usable parts for the shop.", IMPROVED),
                             font_size=22).move_to([-3.6, -2.0, 0])
        self.say("Both have the same virtual condition, four ninety, so the same gauge and the same fit. "
                 "On the chart, it's the same line, just extended down to four ninety. Zero at M M C accepts a small hole that's dead on location, and a big hole that's further off. It gives the shop more room.",
                 (0.3, FadeIn(same_vc[:3])), (0.3, FadeIn(same_vc[3:])), (0.3, Indicate(zero_line, color=WHITE)))
        self.clear_stage()

        # --- Datum features at MMB ----------------------------------------------------------------
        self.play(*self.section("Datum shift"), run_time=0.5)
        PC = np.array([-3.0, -0.6, 0])
        disk = Circle(radius=2.4).move_to(PC).set_fill(STEEL_DARK, 1).set_stroke(STANDARD, 3)
        bore = Circle(radius=0.75).move_to(PC).set_fill(APW_DARK, 1).set_stroke(STANDARD, 3)
        holes = VGroup(*[Circle(radius=0.22).move_to(PC + 1.6 * np.array([np.cos(a), np.sin(a), 0])).set_fill(APW_DARK, 1)
                         .set_stroke(STANDARD, 2.5) for a in np.linspace(PI / 4, PI / 4 + TAU, 4, endpoint=False)])
        partd = VGroup(disk, bore, holes)
        gpin2 = Circle(radius=0.6).move_to(PC).set_fill(GAUGE, 1).set_stroke(REF_A, 2.5)
        f_dat = VGroup(Text("4X", font_size=24), fcf(position_symbol(), ["Ø", ".010", circled("M")], "A", ["B", circled("M")])
                       ).arrange(RIGHT, buff=0.15).scale(0.85).move_to([3.4, 2.5, 0])
        self.say("A circled M can also follow a datum letter. Here, four holes are located from datum B, a center bore, at M M B.",
                 (0.4, FadeIn(partd), FadeIn(f_dat)), (0.3, Indicate(f_dat[1][-1], color=REF_A)))
        b_lbl = Text("Gauge pin for datum B\nat the bore's MMB size", font_size=20, color=REF_A, line_spacing=0.8).move_to([3.4, 1.0, 0])
        self.say("The gauge pin for B is made at the bore's maximum material boundary. When the actual bore is bigger, the part can shift on the pin.",
                 (0.3, FadeIn(gpin2), FadeIn(b_lbl)),
                 (0.2, lambda: partd.animate.shift(RIGHT * 0.15)), (0.15, lambda: partd.animate.shift(LEFT * 0.3 + UP * 0.1)),
                 (0.15, lambda: partd.animate.shift(RIGHT * 0.15 + DOWN * 0.1)))
        shift_note = calc_lines("Datum shift moves the whole", "pattern together. It is not", "extra tolerance on each hole.",
                                font_size=22).move_to([3.4, -0.6, 0])
        terms = VGroup(Text("MMB: maximum material boundary", font_size=20, color=REF_A),
                       Text("Term introduced in Y14.5-2009. Older 1994 prints\nshow the same symbol and call it MMC.", font_size=19,
                            color=APW_MUTED, line_spacing=0.8)).arrange(DOWN, aligned_edge=LEFT, buff=0.08).move_to([3.4, -2.3, 0])
        self.say("That's called datum shift. The whole pattern moves together, so it isn't extra tolerance on each hole by itself. "
                 "C M M software has to fit the pattern within the shift that's available.",
                 (0.45, FadeIn(shift_note)), (0.35, Indicate(holes, color=REF_B)))
        self.say("The two thousand nine standard calls it M M B, maximum material boundary. On older nineteen ninety-four prints, the same symbol was called M M C.",
                 (0.6, FadeIn(terms)))

        nxt = Text("Next, Part 5: threaded holes,\nand the complications they bring.", font_size=28, color=WHITE, line_spacing=0.9)
        self.clear_stage()
        self.say("Next, in part five: threaded holes, and the complications they bring to position.",
                 (0.6, FadeIn(nxt, shift=UP * 0.2)))
        self.apw_outro()
