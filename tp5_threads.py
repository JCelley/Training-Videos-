"""True Position, Part 5: position of threaded holes.

Example values (made up): 3/8-16 UNC-2B tapped hole, .750 deep, in a base plate; a .500 thick mating
part with a Ø.406 clearance hole; position Ø.015 to A B C.

Thread sections use the basic UN internal profile (60 deg, thread height 0.5413P) at 3/8-16 proportions.
Rules cited: ASME Y14.5-2009 section 2.9 Screw Threads (pitch cylinder default, MAJOR DIA / MINOR DIA notes),
projected tolerance zone, and the fixed / floating fastener formulas in its Nonmandatory Appendix B.
"""
from tp_common import *

D, P = 0.375, 1 / 16                 # 3/8-16
DEP = 0.5413 * P                     # basic internal thread height (5H/8)
R_MAJ = D / 2
R_MIN = R_MAJ - DEP
R_PD = (D - 0.6495 * P) / 2          # basic pitch diameter / 2

# Drawing only: the thread form is drawn coarser and deeper than true 3/8-16 so the
# three diameters can be told apart on screen. Numbers in the narration stay true.
P_DRAW = 2.0 * P
EXR = 2.4


def rd(r):
    """Drawn radius for a true thread radius (radial distances from the pitch line enlarged)."""
    return R_PD + (r - R_PD) * EXR


def r_int(z, phase=0.0):
    """Radius of the internal thread wall at height z (inches): crest flat at minor, root flat at major."""
    t = ((z + phase * P_DRAW / P) % P_DRAW) / P_DRAW
    fl = 0.3125
    if t < 0.25:
        r = R_MIN
    elif t < 0.25 + fl:
        r = R_MIN + DEP * (t - 0.25) / fl
    elif t < 0.25 + fl + 0.125:
        r = R_MAJ
    else:
        r = R_MAJ - DEP * (t - 0.6875) / fl
    return rd(r)


def thread_section(xc, z0, z1, S, origin_y, outer=1.4, lateral=lambda z: 0.0, stroke=STANDARD, fill=STEEL_DARK):
    """Section through a tapped hole: two walls of material, thread profile on the inside.

    Heights z in inches (0 = top surface). lateral(z) gives the screen x offset of the thread axis at z.
    """
    zs_ = np.linspace(z0, z1, int((z1 - z0) / P_DRAW * 40) + 1)

    def y(z):
        return origin_y + z * S

    left = [[xc + lateral(z) - r_int(z, 0.5 * P) * S, y(z), 0] for z in zs_]
    right = [[xc + lateral(z) + r_int(z) * S, y(z), 0] for z in zs_]
    lp = Polygon([xc - outer * S, y(z0), 0], *left, [xc - outer * S, y(z1), 0]).set_fill(fill, 1).set_stroke(stroke, 2.5)
    rp = Polygon([xc + outer * S, y(z0), 0], *right, [xc + outer * S, y(z1), 0]).set_fill(fill, 1).set_stroke(stroke, 2.5)
    return VGroup(lp, rp)


class TP5Threads(TPScene):
    part_no = 5

    def construct(self):
        self.start("Threaded holes and their complications",
                   "True position, part five. Threaded holes, and the complications they bring.")
        self.tag = Text("Example values for training", font_size=18, color=APW_MUTED).to_corner(UR, buff=0.35)
        self.add(self.tag)

        # --- Which diameter? ----------------------------------------------------------
        self.play(*self.section("Which diameter is located?"), run_time=0.5)
        S = 5.0
        XC, OY = -3.6, 1.6                     # hole axis x, screen y of the top surface
        sec = thread_section(XC, -0.6, 0.0, S, OY, outer=0.45)
        enl = Text("Thread form drawn enlarged", font_size=18, color=APW_MUTED).move_to([XC, OY - 0.6 * S - 0.65, 0])
        ax = DashedLine([XC, OY + 0.4, 0], [XC, OY - 0.6 * S - 0.3, 0], dash_length=0.12, color=APW_MUTED, stroke_width=2)
        callout_txt = VGroup(Text("3/8-16 UNC-2B", font_size=24, color=WHITE),
                             pos_fcf(".015", "A", "B", "C").scale(0.8)).arrange(DOWN, buff=0.15, aligned_edge=LEFT)
        callout_txt.move_to([3.2, 2.4, 0])
        self.say("Here's a section through a tapped hole, three eighths sixteen U N C, with a position callout of fifteen thousandths.",
                 (0.5, FadeIn(sec), Create(ax), FadeIn(enl)), (0.3, FadeIn(callout_txt)))

        y_top, y_bot = OY + 0.2, OY - 0.6 * S - 0.2

        def dia_lines(r, color, dashed=True):
            mk = DashedLine if dashed else Line
            kw = {"dash_length": 0.1} if dashed else {}
            return VGroup(*[mk([XC + s_ * rd(r) * S, y_top, 0], [XC + s_ * rd(r) * S, y_bot, 0], color=color, stroke_width=2.5, **kw)
                            for s_ in (-1, 1)])

        maj = dia_lines(R_MAJ, STANDARD)
        pd = dia_lines(R_PD, IMPROVED)
        mnr = dia_lines(R_MIN, REF_B)
        labels = VGroup(Text("Major Ø", font_size=22, color=STANDARD), Text("Pitch Ø", font_size=22, color=IMPROVED),
                        Text("Minor Ø", font_size=22, color=REF_B))
        labels[0].next_to(maj[1].get_top(), UP, buff=0.12).shift(RIGHT * 0.5)
        labels[1].next_to(pd[0].get_top(), UP, buff=0.12).shift(LEFT * 0.5)
        labels[2].move_to([XC, OY + 0.45, 0])
        self.say("A thread has three diameters. The major diameter at the roots, the minor diameter at the crests, "
                 "and the pitch diameter in between, where the thread and the groove are the same width.",
                 (0.25, Create(maj), FadeIn(labels[0])), (0.25, Create(mnr), FadeIn(labels[2])), (0.35, Create(pd), FadeIn(labels[1])))

        rule = VGroup(Text("Y14.5-2009, section 2.9 Screw Threads:", font_size=22, color=APW_LOGO_BLUE),
                      Text("position applies to the axis of the\npitch cylinder unless noted otherwise", font_size=24, color=IMPROVED,
                           line_spacing=0.8)).arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to([3.2, 0.7, 0])
        self.say("By default, position on a thread applies to the axis of the pitch cylinder. That's in Y fourteen point five, section two point nine.",
                 (0.5, FadeIn(rule)), (0.3, Indicate(pd, color=WHITE)))
        alt = VGroup(pos_fcf(".015", "A", "B", "C").scale(0.75), Text("MINOR DIA", font_size=22, color=REF_B)).arrange(DOWN, buff=0.1)
        alt.move_to([3.2, -1.3, 0])
        alt_note = Text("A MAJOR DIA or MINOR DIA note under the frame\nmoves the control to that diameter.", font_size=20,
                        color=WHITE, line_spacing=0.8).next_to(alt, DOWN, buff=0.25)
        self.say("To control a different diameter, the print adds a note under the frame: major dia, or minor dia. The same goes for a thread used as a datum.",
                 (0.5, FadeIn(alt)), (0.35, FadeIn(alt_note), Indicate(mnr, color=WHITE)))
        self.clear_stage()

        # --- Complication 1: measuring the pitch axis ----------------------------------------
        self.play(*self.section("Measuring a thread's axis"), run_time=0.5)
        sec2 = thread_section(XC, -0.6, 0.0, S, OY - 0.6, outer=0.45)
        ax2 = DashedLine([XC, OY + 1.4, 0], [XC, OY - 0.6 - 0.6 * S - 0.3, 0], dash_length=0.12, color=IMPROVED, stroke_width=2)
        probe = VGroup(Line(UP * 2.2, ORIGIN, color=GAUGE, stroke_width=6), Dot(ORIGIN, radius=0.12, color=GAUGE))
        tip = [XC + rd(R_MIN) * S - 0.12, OY - 0.6 - 0.9, 0]
        probe.move_to(tip, aligned_edge=DOWN).shift(UP * 2.0)
        miss = callout("A probe ball touches crests\nand flanks, not the pitch\ncylinder", tip, [0.4, 0.8, 0], color=PROBLEM)
        self.say("Here's the first problem. A C M M probe can't touch the pitch cylinder. It only lands on the crests and flanks of the thread.",
                 (0.3, FadeIn(sec2), Create(ax2)), (0.3, lambda: probe.animate.shift(DOWN * 2.0)), (0.3, show_callout(miss)))

        # gauge pin: threaded plug with a ground shank
        pin_z = np.linspace(-0.55, 0.0, 200)
        clr = 0.004                          # pin's thread clearance, inches (exaggerated in drawing by the rocking)

        def pin_shape():
            pts_r = [[XC + (r_int(z) - clr) * S, OY - 0.6 + z * S, 0] for z in pin_z]
            pts_l = [[XC - (r_int(z, 0.5 * P) - clr) * S, OY - 0.6 + z * S, 0] for z in pin_z[::-1]]
            sh = 0.12
            top = OY - 0.6 + 0.3 * S
            body = Polygon(*pts_r, [XC + sh * S, OY - 0.6, 0], [XC + sh * S, top, 0], [XC - sh * S, top, 0],
                           [XC - sh * S, OY - 0.6, 0], *pts_l)
            return body.set_fill(GAUGE, 1).set_stroke(REF_A, 2)

        gpin = pin_shape()
        gpin.shift(UP * 4)
        g_lbl = callout("Thread gauge pin:\nthreads in, ground shank\nsticks out", [XC + 0.12 * S, OY - 0.6 + 0.2 * S, 0],
                        [0.4, 1.6, 0], color=REF_A)
        self.say("So inspectors screw in a thread gauge pin. Its precision ground shank sticks out, and the C M M measures the shank instead.",
                 (0.25, FadeOut(miss), FadeOut(probe)), (0.35, lambda: gpin.animate.shift(DOWN * 4)), (0.3, show_callout(g_lbl)))
        pivot = [XC, OY - 0.6, 0]
        rock = callout("The pin's thread has clearance,\nso it can tip and shift.\nThe farther up the shank you\nmeasure, the bigger the error.",
                       [XC + 0.12 * S + 0.05, OY - 0.6 + 0.25 * S, 0], [0.4, -0.9, 0], color=PROBLEM)
        self.say("But the pin's own thread has clearance, so it can tip and shift a little. Any tip gets bigger the farther up the shank you measure.",
                 (0.2, FadeOut(g_lbl)), (0.2, Rotate(gpin, 0.05, about_point=pivot)), (0.2, Rotate(gpin, -0.1, about_point=pivot)),
                 (0.2, Rotate(gpin, 0.05, about_point=pivot), show_callout(rock)))
        fix = Text("Use snug-fitting pins, seat them the same way every time,\nand measure the shank close to the surface.",
                   font_size=22, color=IMPROVED, line_spacing=0.8).to_edge(DOWN, buff=0.4).shift(RIGHT * 1.5)
        self.say("Use snug-fitting pins, seat them the same way every time, and measure the shank close to the part surface.",
                 (0.6, FadeIn(fix)))
        self.clear_stage()

        # drill vs tap axis
        self.play(*self.section("Drill axis vs thread axis"), run_time=0.5)
        off = 0.25                                # screen offset, exaggerated
        sec3 = thread_section(XC, -0.6, 0.0, S, OY - 0.6, outer=0.45, lateral=lambda z: off)
        drill = VGroup(*[DashedLine([XC + s_ * rd(R_MIN) * S, OY - 0.4, 0], [XC + s_ * rd(R_MIN) * S, OY - 0.6 - 0.6 * S - 0.2, 0],
                                    dash_length=0.1, color=STANDARD, stroke_width=3) for s_ in (-1, 1)])
        d_ax = DashedLine([XC, OY + 0.0, 0], [XC, OY - 0.6 - 0.6 * S - 0.4, 0], dash_length=0.12, color=STANDARD, stroke_width=2.5)
        t_ax = DashedLine([XC + off, OY + 0.0, 0], [XC + off, OY - 0.6 - 0.6 * S - 0.4, 0], dash_length=0.12, color=IMPROVED, stroke_width=2.5)
        lbl_d = Text("Drilled hole axis", font_size=22, color=STANDARD).move_to([XC - 1.3, OY + 0.3, 0])
        lbl_t = Text("Thread (pitch) axis", font_size=22, color=IMPROVED).move_to([XC + 1.6, OY + 0.3, 0])
        note = Text("Offset exaggerated", font_size=18, color=APW_MUTED).move_to([XC, OY - 0.6 - 0.6 * S - 0.7, 0])
        self.say("The tap can also run slightly off the drilled hole. Then the drilled minor diameter and the thread itself don't share the same axis.",
                 (0.4, FadeIn(sec3), Create(drill), Create(d_ax), FadeIn(lbl_d), FadeIn(note)), (0.4, Create(t_ax), FadeIn(lbl_t)))
        warn = VGroup(Text("Probing the minor Ø measures the drill,", font_size=24, color=PROBLEM),
                      Text("not the thread. Only use it when the print", font_size=24, color=WHITE),
                      Text("says MINOR DIA.", font_size=24, color=WHITE)).arrange(DOWN, aligned_edge=LEFT, buff=0.1).move_to([3.0, 0.0, 0])
        self.say("So probing the minor diameter measures where the drill went, not where the thread is. "
                 "That's only the right answer when the print says minor dia.",
                 (0.6, FadeIn(warn)))
        self.clear_stage()

        # --- Complication 2: tilt and the projected tolerance zone ----------------------------
        self.play(*self.section("Tilt and the bolt"), run_time=0.5)
        S2 = 2.6                                 # screen units per inch (vertical)
        M = 50.0                                 # screen units per inch for sideways errors (exaggerated)
        X0, Y0 = -3.0, -0.2                      # true position axis x, screen y of the joint (top of base part)
        dx0, dy0, tilt = 0.003, 0.002, 0.012     # axis at the surface, tilt in X per inch of height
        T_DEP, T_MATE = 0.75, 0.50
        TOLZ = 0.015
        RB = R_MAJ * S2 * 1.4                    # drawn bolt radius
        H_CLR = 0.406

        def axis_x(z):
            return X0 + (dx0 + tilt * z) * M

        def y(z):
            return Y0 + z * S2

        base_l = Polygon([X0 - 3.0, y(-T_DEP), 0], [axis_x(-T_DEP) - RB, y(-T_DEP), 0], [axis_x(0) - RB, y(0), 0], [X0 - 3.0, y(0), 0])
        base_r = Polygon([X0 + 3.0, y(-T_DEP), 0], [axis_x(-T_DEP) + RB, y(-T_DEP), 0], [axis_x(0) + RB, y(0), 0], [X0 + 3.0, y(0), 0])
        base = VGroup(base_l, base_r).set_fill(STEEL_DARK, 1).set_stroke(STANDARD, 2.5)
        r_clr = RB + (H_CLR - D) / 2 * M
        mate_shift = ValueTracker(0.0)

        def mating():
            c = X0 + mate_shift.get_value()
            g = VGroup(Polygon([X0 - 3.0, y(0), 0], [c - r_clr, y(0), 0], [c - r_clr, y(T_MATE), 0], [X0 - 3.0, y(T_MATE), 0]),
                       Polygon([X0 + 3.0, y(0), 0], [c + r_clr, y(0), 0], [c + r_clr, y(T_MATE), 0], [X0 + 3.0, y(T_MATE), 0]))
            return g.set_fill("#3A4A68", 1).set_stroke(STANDARD, 2.5)

        mate = always_redraw(mating)
        bolt = Polygon([axis_x(-T_DEP) - RB, y(-T_DEP), 0], [axis_x(-T_DEP) + RB, y(-T_DEP), 0],
                       [axis_x(T_MATE + 0.05) + RB, y(T_MATE + 0.05), 0], [axis_x(T_MATE + 0.05) - RB, y(T_MATE + 0.05), 0])
        bolt.set_fill(STEEL, 1).set_stroke(GAUGE, 2)
        head = Rectangle(width=RB * 3.2, height=0.45).move_to([axis_x(T_MATE + 0.05), y(T_MATE + 0.05) + 0.225, 0])
        head.set_fill(STEEL, 1).set_stroke(GAUGE, 2)
        tp_ax = DashedLine([X0, y(-T_DEP) - 0.3, 0], [X0, y(T_MATE) + 0.8, 0], dash_length=0.12, color=REF_A, stroke_width=2)
        act_ax = Line([axis_x(-T_DEP), y(-T_DEP), 0], [axis_x(T_MATE + 0.05), y(T_MATE + 0.05), 0], color=WHITE, stroke_width=3)
        exag = Text("Sideways errors and clearances exaggerated", font_size=18, color=APW_MUTED).move_to([X0, y(-T_DEP) - 0.55, 0])
        lbls = VGroup(Text("Base part,\ntapped hole", font_size=18, color=WHITE, line_spacing=0.8).move_to([X0 - 2.2, y(-T_DEP / 2), 0]),
                      Text("Mating part,\nØ.406 hole", font_size=18, color=WHITE, line_spacing=0.8)
                      .move_to([X0 - 2.2, y(T_MATE / 2), 0]))
        self.say("The second problem is tilt. A bolt follows the thread's axis, and it sticks up through the mating part.",
                 (0.35, FadeIn(base), FadeIn(mate), FadeIn(lbls), Create(tp_ax), FadeIn(exag)),
                 (0.35, FadeIn(VGroup(bolt, head), shift=DOWN * 0.5), Create(act_ax)))

        zone_in = Rectangle(width=TOLZ * M, height=T_DEP * S2).move_to([X0, y(-T_DEP / 2), 0]).set_fill(IMPROVED, 0.25).set_stroke(IMPROVED, 3)
        f_np = pos_fcf(".015", "A", "B", "C").scale(0.8).move_to([3.4, 2.6, 0])
        calc_np = calc_lines("Zone inside the hole only:", ("Top:      Δx +.003  Δy +.002  →  Ø.0072", WHITE),
                             (f"Bottom: Δx {fmt(dx0 - tilt * T_DEP, 3, True)}  Δy +.002  →  Ø{fmt(zone_dia(dx0 - tilt * T_DEP, dy0), 4)}", WHITE),
                             ("Worst Ø.0126 ≤ Ø.015", IMPROVED), font_size=21).move_to([3.4, 1.0, 0])
        self.say("With a normal position callout, the zone only exists inside the threaded hole. This tilted thread stays inside it, top to bottom, and passes.",
                 (0.3, FadeIn(f_np), DrawBorderThenFill(zone_in)), (0.45, FadeIn(calc_np)))

        tip_r = Dot([axis_x(T_MATE) + RB, y(T_MATE), 0], radius=0.09, color=PROBLEM)
        clash = callout("If the mating hole is also\noff in its own zone,\nthe bolt hits it", [axis_x(T_MATE) + RB, y(T_MATE), 0],
                        [0.9, -1.5, 0], color=PROBLEM)
        self.say("But follow the axis up through the mating part. The tilt keeps growing with height. "
                 "If the mating hole is also near the edge of its own zone, the bolt runs into it.",
                 (0.3, Indicate(act_ax, color=REF_B)), (0.35, mate_shift.animate.set_value(-0.0075 * M)),
                 (0.25, GrowFromCenter(tip_r), show_callout(clash)))

        self.play(*self.section("The projected tolerance zone"), FadeOut(clash), FadeOut(calc_np), run_time=0.5)
        zone_p = Rectangle(width=TOLZ * M, height=T_MATE * S2).move_to([X0, y(T_MATE / 2), 0]).set_fill(REF_A, 0.3).set_stroke(REF_A, 3)
        f_p = pos_fcf(".015", "A", "B", "C", proj=".500").scale(0.8).move_to(f_np)
        self.say("The fix is a projected tolerance zone: a circled P, followed by the projected height, here five hundred thousandths.",
                 (0.3, FadeOut(f_np), FadeIn(f_p)), (0.3, Indicate(f_p[1], color=REF_A)))
        p_note = callout("Zone moved up out of the hole,\nthrough the mating part:\nmin height .500", zone_p.get_right(), [0.9, 1.0, 0], color=REF_A)
        self.say("The zone moves out of the hole, and sits above it, where the bolt actually passes through the mating part.",
                 (0.4, Transform(zone_in, zone_p)), (0.4, show_callout(p_note)))
        calc_p = calc_lines("Projected zone, 0 to .500 above:", ("At the surface:  Δx +.003  Δy +.002  →  Ø.0072", WHITE),
                            (f"At .500 up:  Δx {fmt(dx0 + tilt * T_MATE, 3, True)}  Δy +.002  →  Ø{fmt(zone_dia(dx0 + tilt * T_MATE, dy0), 4)}", WHITE),
                            (f"Ø{fmt(zone_dia(dx0 + tilt * T_MATE, dy0), 4)} > Ø.015", PROBLEM), font_size=21).move_to([3.4, -1.9, 0])
        bad = pass_fail(False).scale(0.8).next_to(calc_p[-1], RIGHT, buff=0.25)
        self.say("Now check the axis at the top of the projected zone. Delta X is nine thousandths there, and position is eighteen point four. "
                 "The same part fails, and that's the right answer, because the bolt wouldn't fit.",
                 (0.3, FadeOut(p_note), FadeIn(calc_p[:2])), (0.3, FadeIn(calc_p[2])), (0.25, FadeIn(calc_p[3]), FadeIn(bad)))
        h_note = VGroup(Text("Projected height: at least the mating part's", font_size=20, color=WHITE),
                        Text("maximum thickness (or the stud's height).", font_size=20, color=WHITE),
                        Text("It can also be shown with a chain line and a", font_size=20, color=APW_MUTED),
                        Text("dimension next to the extended centerline.", font_size=20, color=APW_MUTED)
                        ).arrange(DOWN, aligned_edge=LEFT, buff=0.06).move_to([3.4, 0.55, 0])
        self.say("The projected height should be at least the maximum thickness of the mating part, or the height of a stud. "
                 "Some prints show it instead with a heavy chain line and a dimension beside the centerline.",
                 (0.6, FadeIn(h_note)))
        self.clear_stage()

        # --- Complication 3: MMC on threads ------------------------------------------------------
        self.play(*self.section("MMC on a thread"), run_time=0.5)
        sec4 = thread_section(XC, -0.6, 0.0, S, OY - 0.4, outer=0.45)
        pd2 = VGroup(*[DashedLine([XC + s_ * R_PD * S, OY - 0.2, 0], [XC + s_ * R_PD * S, OY - 0.4 - 0.6 * S - 0.2, 0],
                                  dash_length=0.1, color=IMPROVED, stroke_width=2.5) for s_ in (-1, 1)])
        f_m = pos_fcf(".015", "A", "B", "C", mod="M").scale(0.8).move_to([3.3, 2.5, 0])
        self.say("The third problem: material modifiers on a thread. If the frame says M M C, the bonus comes from the pitch diameter, "
                 "not from a simple hole size.",
                 (0.4, FadeIn(sec4), Create(pd2), FadeIn(f_m)), (0.3, Indicate(pd2, color=WHITE)))
        m_txt = VGroup(Text("Pitch Ø tolerance is small, and the actual", font_size=22, color=WHITE),
                       Text("pitch Ø is hard to measure on a CMM.", font_size=22, color=WHITE),
                       Text("Torqued bolts center in the thread anyway,", font_size=22, color=WHITE),
                       Text("so there's little real bonus to gain.", font_size=22, color=PROBLEM),
                       Text("Treat it as RFS unless you check it with", font_size=22, color=IMPROVED),
                       Text("a threaded functional gauge.", font_size=22, color=IMPROVED)
                       ).arrange(DOWN, aligned_edge=LEFT, buff=0.08).move_to([3.3, 0.2, 0])
        self.say("The pitch diameter tolerance is small, and the actual pitch diameter is hard to measure on a C M M. "
                 "A torqued bolt also pulls itself to the center of the thread. So there's little real bonus to gain.",
                 (0.3, FadeIn(m_txt[:2])), (0.3, FadeIn(m_txt[2:4])))
        self.say("Unless you're checking it with a threaded functional gauge, the safe practice is to treat a tapped hole's position as R F S.",
                 (0.6, FadeIn(m_txt[4:])))
        self.clear_stage()

        # --- Fastener formulas -----------------------------------------------------------------------
        self.play(*self.section("Fastener formulas"), run_time=0.5)

        def joint(xc, fixed):
            k, Ys = 1.1, 0.5
            top = VGroup(Rectangle(width=2.0, height=0.7).move_to([xc - 1.35, Ys + 0.35, 0]),
                         Rectangle(width=2.0, height=0.7).move_to([xc + 1.35, Ys + 0.35, 0])).set_fill("#3A4A68", 1).set_stroke(STANDARD, 2)
            if fixed:
                bot = VGroup(Rectangle(width=2.2, height=1.1).move_to([xc - 1.25, Ys - 0.55, 0]),
                             Rectangle(width=2.2, height=1.1).move_to([xc + 1.25, Ys - 0.55, 0])).set_fill(STEEL_DARK, 1).set_stroke(STANDARD, 2)
                teeth = VGroup(*[Line([xc + s_ * 0.15, Ys - 0.1 - i * 0.18, 0], [xc + s_ * 0.3, Ys - 0.19 - i * 0.18, 0],
                                      color=STANDARD, stroke_width=2) for s_ in (-1, 1) for i in range(5)])
                bot.add(teeth)
            else:
                bot = VGroup(Rectangle(width=2.0, height=0.7).move_to([xc - 1.35, Ys - 0.35, 0]),
                             Rectangle(width=2.0, height=0.7).move_to([xc + 1.35, Ys - 0.35, 0])).set_fill(STEEL_DARK, 1).set_stroke(STANDARD, 2)
            blt = Rectangle(width=0.5, height=2.4 if not fixed else 1.9).set_fill(STEEL, 1).set_stroke(GAUGE, 2)
            blt.move_to([xc, Ys + 0.7 - blt.height / 2 + 0.6, 0])
            hd = Rectangle(width=1.1, height=0.35).set_fill(STEEL, 1).set_stroke(GAUGE, 2).next_to(blt, UP, buff=0)
            g = VGroup(top, bot, blt, hd)
            if not fixed:
                nut = Rectangle(width=1.1, height=0.35).set_fill(STEEL, 1).set_stroke(GAUGE, 2).move_to([xc, Ys - 0.7 - 0.175, 0])
                g.add(nut)
            return g

        fixed_j = joint(-3.4, True)
        float_j = joint(3.4, False)
        t_fixed = VGroup(Text("Fixed fastener", font_size=26, color=WHITE, weight=BOLD),
                         Text("screw threads into one part", font_size=20, color=APW_MUTED)).arrange(DOWN, buff=0.08).move_to([-3.4, 2.6, 0])
        t_float = VGroup(Text("Floating fastener", font_size=26, color=WHITE, weight=BOLD),
                         Text("bolt and nut, clearance in both parts", font_size=20, color=APW_MUTED)).arrange(DOWN, buff=0.08).move_to([3.4, 2.6, 0])
        self.say("Where does a number like fifteen thousandths come from? Y fourteen point five gives two formulas in its appendix, "
                 "one for a screw threaded into a part, and one for a bolt and nut.",
                 (0.4, FadeIn(fixed_j), FadeIn(t_fixed)), (0.4, FadeIn(float_j), FadeIn(t_float)))
        fx_calc = calc_lines(("T = (H − F) / 2  for each part", REF_A), "H = clearance hole at MMC  .406",
                             "F = fastener at MMC  .375", ("T = (.406 − .375) / 2 = .0155", IMPROVED), ("→ about Ø.015 each part", IMPROVED),
                             font_size=20, buff=0.08).move_to([-3.4, -1.85, 0])
        fl_calc = calc_lines(("T = H − F  for each part", REF_A), "T = .406 − .375 = .031", ("→ Ø.031 each part", IMPROVED),
                             font_size=20, buff=0.08).move_to([3.4, -1.55, 0])
        self.say("For a fixed fastener, each part gets half the difference between the clearance hole at M M C and the fastener at M M C. "
                 "Four oh six minus three seventy-five, divided by two, is about fifteen thousandths each.",
                 (0.25, FadeIn(fx_calc[0])), (0.3, FadeIn(fx_calc[1:3])), (0.3, FadeIn(fx_calc[3:])))
        self.say("For a floating fastener, both parts have clearance, so each part gets the whole difference: thirty-one thousandths.",
                 (0.5, FadeIn(fl_calc)))
        perp_req = Text("The fixed-fastener formula assumes the threaded hole is square to the joint.\nThat's the projected tolerance zone's job.",
                        font_size=20, color=REF_A, line_spacing=0.8).move_to([0, -3.4, 0])
        self.say("The fixed fastener formula assumes the threaded hole is square to the joint. That's exactly why tapped holes get a projected zone.",
                 (0.6, FadeIn(perp_req)))
        self.clear_stage()

        # --- Wrap-up on one drawing --------------------------------------------------------------------
        self.play(*self.section("Threaded holes: what to check"), run_time=0.5)
        SX = -3.4
        sec5 = thread_section(SX, -0.6, 0.0, 5.0, -0.2, outer=0.45)
        pz = Rectangle(width=0.5, height=2.2).move_to([SX, -0.2 + 1.1, 0]).set_fill(REF_A, 0.3).set_stroke(REF_A, 3)
        pdl = VGroup(*[DashedLine([SX + s_ * R_PD * 5, -0.2, 0], [SX + s_ * R_PD * 5, -0.2 - 3.0, 0], dash_length=0.1,
                                  color=IMPROVED, stroke_width=2.5) for s_ in (-1, 1)])
        c1 = callout("Pitch Ø axis, unless the\nprint says MAJOR or MINOR DIA", [SX + R_PD * 5, -2.4, 0], [0.3, -2.5, 0], color=IMPROVED)
        c2 = callout("Projected zone: check the axis\nup through the mating part", [SX + 0.25, 1.4, 0], [0.3, 1.8, 0], color=REF_A)
        c3 = callout("Measure with a snug gauge pin,\nclose to the surface", [SX + 0.25, 0.3, 0], [0.3, 0.55, 0], color=WHITE)
        c4 = callout("MMC on threads: little real\nbonus, treat as RFS", [SX + rd(R_MAJ) * 5, -1.2, 0], [0.3, -1.0, 0], color=REF_B)
        self.say("To sum up threaded holes: position is on the pitch diameter axis unless the print says otherwise.",
                 (0.3, FadeIn(sec5), Create(pdl)), (0.4, show_callout(c1)))
        self.say("Projected zones check the axis where the bolt really goes.", (0.3, DrawBorderThenFill(pz)), (0.4, show_callout(c2)))
        self.say("Measure with a snug gauge pin, close to the surface, and don't count on bonus from M M C.",
                 (0.4, show_callout(c3)), (0.4, show_callout(c4)))
        ref = Text("Check figures against the print and the edition of ASME Y14.5 it calls out.", font_size=22,
                   color=APW_MUTED).to_edge(DOWN, buff=0.35)
        self.say("And always check the numbers against the print, and the edition of the standard it calls out. That's the end of the true position series.",
                 (0.6, FadeIn(ref)))
        self.apw_outro()
