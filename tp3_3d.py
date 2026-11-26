"""True Position, Part 3: into 3D. The cylindrical zone, tilt, orientation, zone shapes, coaxial position.

Example values (made up): 4.000 x 3.000 x .750 plate, Ø.500 hole, position Ø.010 to A B C.
Zone sizes and errors are drawn magnified so they can be seen.
"""
from tp_common import *

HX, HY, L, W, T = 1.5, 1.25, 4.0, 3.0, 0.75
BC = np.array([-2.4, -0.6, 0])       # block view screen center
BS = 1.15                            # block view scale (screen units per inch)
ZR = 0.17                            # drawn zone radius on the block (exaggerated)


def bp(p, az, el):
    """Block-view projection, part centered on screen."""
    x, y, z = p
    return project((x - L / 2, y - W / 2, z - T / 2), az, el, BC, BS)


def block_view(az, el, show_zone=False, zone_h=1.0):
    def q(*pts, fill, op=1.0):
        return Polygon(*[bp(p, az, el) for p in pts]).set_fill(fill, op).set_stroke(STANDARD, 2.5)

    g = VGroup(q((0, 0, 0), (0, W, 0), (0, W, T), (0, 0, T), fill="#3A4A68"),
               q((0, 0, 0), (L, 0, 0), (L, 0, T), (0, 0, T), fill=STEEL_DARK),
               q((0, 0, T), (L, 0, T), (L, W, T), (0, W, T), fill=STEEL))
    hole = Polygon(*[bp(p, az, el) for p in circle_pts((HX, HY, T), 0.25)]).set_fill(APW_DARK, 1).set_stroke(STANDARD, 2)
    g.add(hole)
    if show_zone:
        c0 = np.array([HX, HY, T - zone_h * T])
        c1 = np.array([HX, HY, T])
        e0 = [bp(p, az, el) for p in circle_pts(c0, ZR)]
        e1 = [bp(p, az, el) for p in circle_pts(c1, ZR)]
        sil = Polygon(*hull(e0 + e1)).set_fill(IMPROVED, 0.35).set_stroke(IMPROVED, 2.5)
        g.add(sil, Polygon(*e1).set_stroke(IMPROVED, 2.5).set_fill(opacity=0))
    return g


# --- Magnified zone view ---------------------------------------------------------
MC = np.array([2.9, -0.5, 0])
MR = 1.05                    # screen radius of a .005 radial error
MAG = MR / 0.005
MH = 3.6                     # screen height of the .750 deep hole


def mp(dx, dy, frac, az, el):
    """Point in the magnified view: sideways error in inches, frac 0 = bottom of hole, 1 = top."""
    return project((dx * MAG, dy * MAG, (frac - 0.5) * MH), az, el, MC, 1.0)


def mzone(az, el, r=MR, color=IMPROVED, op=0.18, cx=0.0, cy=0.0):
    c0 = np.array([cx, cy, -MH / 2])
    c1 = np.array([cx, cy, MH / 2])
    return cylinder3(c0, c1, r, az, el, MC, 1.0, color, opacity=op)


def axis_segments(bot, top, az, el, limit=0.005):
    """Axis line from bot (dx, dy) to top (dx, dy): green inside the Ø.010 zone, red outside."""
    g = VGroup()
    ts = np.linspace(0, 1, 61)
    pts = [(bot[0] + (top[0] - bot[0]) * t, bot[1] + (top[1] - bot[1]) * t, t) for t in ts]
    for a, b in zip(pts[:-1], pts[1:]):
        inside = np.hypot((a[0] + b[0]) / 2, (a[1] + b[1]) / 2) <= limit + 1e-9
        g.add(Line(mp(a[0], a[1], a[2], az, el), mp(b[0], b[1], b[2], az, el),
                   color=WHITE if inside else PROBLEM, stroke_width=5))
    return g


class TP3ThreeD(TPScene):
    part_no = 3

    def construct(self):
        self.start("Into 3D: the zone is a cylinder",
                   "True position, part three. Into three D, where the tolerance zone becomes a cylinder.")
        self.tag = tag = Text("Example values. Zones magnified.", font_size=18, color=APW_MUTED).to_corner(UR, buff=0.35)
        self.add(tag)

        # --- Circle to cylinder -------------------------------------------------------
        self.play(*self.section("From a circle to a cylinder"), run_time=0.5)
        az, el = ValueTracker(0.0), ValueTracker(PI / 2 - 0.001)
        zh = ValueTracker(0.02)
        view = always_redraw(lambda: block_view(az.get_value(), el.get_value(), True, zh.get_value()))
        f = pos_fcf(".010", "A", "B", "C").scale(0.85).move_to([3.4, 2.5, 0])
        self.say("In part one we drew the zone as a circle, looking straight down on the plate.",
                 (0.6, FadeIn(view), FadeIn(f)))
        self.say("But a hole has depth. Tip the part over, and you'll see the circle is really the end of a cylinder.",
                 (0.75, az.animate.set_value(-0.62), el.animate.set_value(0.5)))
        cyl_lbl = callout("Ø.010 cylinder,\nsquare to datum A,\nthrough the full depth", bp((HX + ZR, HY, T * 0.5), -0.62, 0.5),
                          [0.4, 1.4, 0], color=IMPROVED)
        self.say("The zone extends through the full depth of the hole, and it stands square to datum A.",
                 (0.55, zh.animate.set_value(1.0)), (0.3, show_callout(cyl_lbl)))

        # --- How the axis is measured -----------------------------------------------------
        self.play(*self.section("Finding the hole's axis"), FadeOut(cyl_lbl), run_time=0.5)
        a_, e_ = -0.62, 0.5
        ring_t = VGroup(*[Dot(bp(p, a_, e_), radius=0.045, color=REF_A) for p in circle_pts((HX, HY, T * 0.85), 0.25, n=8)])
        ring_b = VGroup(*[Dot(bp(p, a_, e_), radius=0.045, color=REF_B) for p in circle_pts((HX, HY, T * 0.15), 0.25, n=8)])
        probe = VGroup(Line(UP * 1.4, ORIGIN, color=GAUGE, stroke_width=6), Dot(ORIGIN, radius=0.08, color=GAUGE))
        probe.move_to(ring_t[0].get_center(), aligned_edge=DOWN)
        self.say("To find the axis, the C M M probes the hole wall at several depths, at least near the top and near the bottom.",
                 (0.3, FadeIn(probe, shift=DOWN * 0.4)),
                 (0.3, LaggedStart(*[GrowFromCenter(d) for d in ring_t], lag_ratio=0.15)),
                 (0.3, lambda: probe.animate.move_to(ring_b[0].get_center(), aligned_edge=DOWN),
                  LaggedStart(*[GrowFromCenter(d) for d in ring_b], lag_ratio=0.15)))
        ame = VGroup(Text("Hole axis = axis of the largest perfect pin", font_size=22, color=WHITE),
                     Text("that fits in the hole (actual mating envelope)", font_size=22, color=WHITE)).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
        ame.move_to([2.6, 0.9, 0])
        self.say("The axis that counts is the axis of the largest perfect pin that would fit inside the hole. The standard calls that pin the actual mating envelope.",
                 (0.3, FadeOut(probe)), (0.5, FadeIn(ame)))

        # --- Magnified zone view, a good straight hole ---------------------------------
        self.clear_stage()
        self.play(*self.section("Checking the axis in the zone"), run_time=0.5)
        maz, mel = ValueTracker(-0.5), ValueTracker(0.32)
        ax_bot, ax_top = [0.002, 0.001], [0.002, 0.001]
        bot_v = ValueTracker(0)  # 0 = straight axis, 1 = tilted axis
        tilt_bot = (0.004, 0.005)

        def cur_bot():
            k = bot_v.get_value()
            return (ax_top[0] + (tilt_bot[0] - ax_top[0]) * k, ax_top[1] + (tilt_bot[1] - ax_top[1]) * k)

        zone = always_redraw(lambda: mzone(maz.get_value(), mel.get_value()))
        tp_axis = always_redraw(lambda: DashedLine(mp(0, 0, -0.08, maz.get_value(), mel.get_value()),
                                                   mp(0, 0, 1.08, maz.get_value(), mel.get_value()),
                                                   dash_length=0.1, color=REF_A, stroke_width=2))
        actual = always_redraw(lambda: axis_segments(cur_bot(), ax_top, maz.get_value(), mel.get_value()))
        z_lbl = Text("Ø.010 zone (magnified)", font_size=20, color=IMPROVED).move_to(MC + np.array([0, MH / 2 + 0.75, 0]))
        tp_lbl = Text("True position axis", font_size=20, color=REF_A).move_to(MC + np.array([1.9, -MH / 2 - 0.35, 0]))
        self.say("Here's the zone cylinder, magnified sideways so we can see inside. The yellow line is the true position axis.",
                 (0.4, FadeIn(zone), Create(tp_axis), FadeIn(z_lbl)), (0.3, FadeIn(tp_lbl)))
        top_calc = calc_lines("Straight hole, square to A:", ("Top:     Δx +.002  Δy +.001", REF_A),
                              ("Bottom: Δx +.002  Δy +.001", REF_B), ("Ø = 2 × √(.002² + .001²) = Ø.0045", IMPROVED),
                              font_size=22).move_to([-3.9, 1.2, 0])
        self.say("A straight hole that's square to A, but shifted a little, has the same error at the top and at the bottom. Position is forty-five ten-thousandths. It passes.",
                 (0.35, FadeIn(actual)), (0.4, FadeIn(top_calc)), (0.15, maz.animate.set_value(-0.2)))

        # --- Tilted hole -------------------------------------------------------------------
        tilt_calc = calc_lines("Tilted hole:", ("Top:     Δx +.002  Δy +.001  →  Ø.0045", REF_A),
                               ("Bottom: Δx +.004  Δy +.005  →  Ø.0128", REF_B),
                               ("Worst end: Ø.0128 > Ø.010", PROBLEM), font_size=22).move_to([-3.9, -1.6, 0])
        bad = pass_fail(False).next_to(tilt_calc[-1], RIGHT, buff=0.3)
        self.say("Now the drill wanders. The top of the hole is still in the same place, but the bottom has drifted out.",
                 (0.6, bot_v.animate.set_value(1.0), maz.animate.set_value(-0.75), *self.section("A tilted hole")))
        self.say("Check each end. The top is still forty-five ten-thousandths. At the bottom, delta X is four and delta Y is five thousandths: "
                 "that's twelve point eight thousandths. The axis leaves the cylinder, so the hole fails.",
                 (0.2, FadeIn(tilt_calc[:2])), (0.35, FadeIn(tilt_calc[2])), (0.25, FadeIn(tilt_calc[3]), FadeIn(bad)))
        top_view_note = Text("From the top it looks good.\nOnly the full depth shows the problem.", font_size=22, color=REF_B,
                             line_spacing=0.85).move_to([-3.9, -3.1, 0])
        self.say("Looking only at the top of the hole, this part would have passed. The whole depth has to be in the zone, "
                 "so position reports the worst end. Most C M M software checks the axis at both ends of the hole.",
                 (0.35, FadeIn(top_view_note)), (0.4, lambda: mel.animate.set_value(1.2)), (0.2, lambda: mel.animate.set_value(0.32)))

        # --- Position controls orientation --------------------------------------------------
        self.clear_stage()
        self.play(*self.section("Position also controls tilt"), run_time=0.5)
        zone2 = always_redraw(lambda: mzone(maz.get_value(), mel.get_value()))
        worst = always_redraw(lambda: Line(mp(-0.005, 0, 0, maz.get_value(), mel.get_value()),
                                           mp(0.005, 0, 1, maz.get_value(), mel.get_value()), color=REF_B, stroke_width=5))
        w_calc = calc_lines("Most tilt that can still pass:", ("corner to corner = .010 over the .750 depth", REF_B),
                            "So position also limits perpendicularity", "to A. It can never be worse than .010.",
                            font_size=22).move_to([-3.8, 1.2, 0])
        self.add(zone2)
        self.say("Because the zone is a cylinder square to A, it limits tilt too. The most tilt that can still pass runs corner to corner: "
                 "ten thousandths over the depth of the hole.",
                 (0.4, Create(worst), maz.animate.set_value(-0.35)), (0.4, FadeIn(w_calc)))

        refine = VGroup(pos_fcf(".010", "A", "B", "C"), fcf(perp_symbol(), ["Ø", ".004"], "A")).arrange(DOWN, buff=0, aligned_edge=LEFT)
        refine.scale(0.8).move_to([-3.8, -1.6, 0])
        pz = always_redraw(lambda: mzone(maz.get_value(), mel.get_value(), r=MR * 0.4, color=REF_A, op=0.25,
                                         cx=0.0018 * MAG, cy=0.0006 * MAG))
        p_lbl = Text("Ø.004 perpendicularity zone:\nsame tilt limit, but free to float\ninside the position zone",
                     font_size=20, color=REF_A, line_spacing=0.8).next_to(refine, DOWN, buff=0.3)
        self.say("If the hole needs to be straighter than that, the designer can add a perpendicularity callout under it. "
                 "That zone is smaller, and it can float anywhere inside the position zone.",
                 (0.3, FadeIn(refine), FadeOut(worst)), (0.4, FadeIn(pz), FadeIn(p_lbl)))
        self.say("The tighter perpendicularity controls tilt. Position still controls location.",
                 (0.5, maz.animate.set_value(-0.9)))

        # --- Zone shapes ----------------------------------------------------------------------
        self.clear_stage()
        self.play(*self.section("Zone shapes"), run_time=0.5)
        saz, sel = ValueTracker(-0.6), ValueTracker(0.35)
        cyl = always_redraw(lambda: cylinder3((-3.6, 0, -1.4), (-3.6, 0, 1.4), 0.9, saz.get_value(), sel.get_value(),
                                              np.array([-1.0, -1.2, 0]), 1.0, IMPROVED, opacity=0.25))
        c_lbl = VGroup(pos_fcf(".010", "A", "B", "C").scale(0.8), Text("Ø in the frame: cylinder", font_size=22, color=IMPROVED)
                       ).arrange(DOWN, buff=0.2).move_to([-4.4, 2.1, 0])

        def planes(az_, el_):
            g = VGroup()
            for xo in (-0.45, 0.45):
                pts = [(3.0 + xo, -1.1, -1.4), (3.0 + xo, 1.1, -1.4), (3.0 + xo, 1.1, 1.4), (3.0 + xo, -1.1, 1.4)]
                g.add(Polygon(*[project(p, az_, el_, np.array([-1.0, -1.2, 0]), 1.0) for p in pts])
                      .set_fill(REF_B, 0.25).set_stroke(REF_B, 2.5))
            cp = [(3.0, -1.1, -1.4), (3.0, 1.1, -1.4), (3.0, 1.1, 1.4), (3.0, -1.1, 1.4)]
            g.add(DashedVMobject(Polygon(*[project(p, az_, el_, np.array([-1.0, -1.2, 0]), 1.0) for p in cp])
                                 .set_stroke(WHITE, 2), num_dashes=40))
            return g

        pl = always_redraw(lambda: planes(saz.get_value(), sel.get_value()))
        p_lbl2 = VGroup(pos_fcf(".010", "A", "B", dia=False).scale(0.8),
                        Text("No Ø: two parallel planes .010 apart\n(e.g. a slot's center plane)", font_size=22, color=REF_B,
                             line_spacing=0.8)).arrange(DOWN, buff=0.2).move_to([3.3, 2.0, 0])
        self.say("The diameter symbol decides the shape of the zone. With it, the zone is a cylinder, for a hole or a pin.",
                 (0.6, FadeIn(cyl), FadeIn(c_lbl)))
        self.say("Without it, the zone is two parallel planes. That's used for a slot or a tab, where only one direction matters: "
                 "the center plane of the slot has to lie between them.",
                 (0.5, FadeIn(pl), FadeIn(p_lbl2)), (0.4, saz.animate.set_value(-1.1)))
        self.say("Watch for that symbol when you read the frame. Without the diameter, the ten thousandths is a total width, "
                 "so the center plane can be off at most five thousandths to either side of true position.",
                 (0.6, Indicate(p_lbl2[0], color=REF_A)))

        # --- Coaxial position (2018 removed concentricity) -----------------------------------
        self.clear_stage()
        self.play(*self.section("Coaxial features"), run_time=0.5)
        caz, cel = ValueTracker(-0.35), ValueTracker(0.35)
        SC = np.array([-0.4, -0.9, 0])

        def shaft(az_, el_):
            big = cylinder3((-3.0, 0, 0), (0.2, 0, 0), 1.1, az_, el_, SC, 1.0, STANDARD, opacity=0.35, axis="x")
            small = cylinder3((0.2, 0, 0), (3.4, 0, 0), 0.6, az_, el_, SC, 1.0, STANDARD, opacity=0.35, axis="x")
            dax = DashedLine(project((-3.8, 0, 0), az_, el_, SC, 1.0), project((4.2, 0, 0), az_, el_, SC, 1.0),
                             dash_length=0.12, color=REF_A, stroke_width=2.5)
            zc = cylinder3((0.2, 0, 0), (3.4, 0, 0), 0.22, az_, el_, SC, 1.0, IMPROVED, opacity=0.3, axis="x")
            return VGroup(big, small, dax, zc)

        sh = always_redraw(lambda: shaft(caz.get_value(), cel.get_value()))
        da = always_redraw(lambda: datum_tag("A", project((-1.4, 0, 1.1), caz.get_value(), cel.get_value(), SC, 1.0), UP, length=0.45))
        cf = pos_fcf(".004", "A").scale(0.85).move_to([2.6, 2.4, 0])
        cl = Text("Zone: Ø.004 cylinder around datum axis A (magnified)", font_size=22, color=IMPROVED).move_to([0, -3.1, 0])
        self.say("Position also controls coaxial features, like a turned diameter that has to run true to another one.",
                 (0.6, FadeIn(sh), FadeIn(da)))
        self.say("Datum A is the axis of the large diameter. The small diameter's axis must lie in a cylinder around datum axis A.",
                 (0.35, FadeIn(cf)), (0.35, FadeIn(cl)), (0.2, caz.animate.set_value(-0.6)))
        ed = VGroup(Text("2009", font_size=26, color=STANDARD, weight=BOLD),
                    Text("still has a concentricity symbol", font_size=22, color=WHITE),
                    Text("2018", font_size=26, color=IMPROVED, weight=BOLD),
                    Text("concentricity removed: use position,\nrunout or profile instead", font_size=22, color=WHITE, line_spacing=0.8)
                    ).arrange(DOWN, aligned_edge=LEFT, buff=0.1).move_to([-4.2, 2.0, 0])
        self.say("This matters more under the two thousand eighteen standard. It removed the concentricity symbol completely. "
                 "Position, runout or profile are used instead. You'll still see concentricity on older two thousand nine prints.",
                 (0.35, FadeIn(ed[2:])), (0.3, FadeIn(ed[:2])))

        nxt = Text("Next, Part 4: material modifiers.\nMMC, LMC and bonus tolerance.", font_size=28, color=WHITE, line_spacing=0.9)
        self.clear_stage()
        self.say("Next, in part four: material modifiers. M M C, L M C, and bonus tolerance.", (0.6, FadeIn(nxt, shift=UP * 0.2)))
        self.apw_outro()
