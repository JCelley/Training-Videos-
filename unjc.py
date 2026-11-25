"""UNJC vs UNC threads, focused on the internal thread.

Thread drawings use the 60 degree basic profile (ASME B1.1 / B1.15) in true
proportion, at the D = 5P ratio of a 1/4-20, shown as a section through the axis
(so both sides show, offset half a pitch like a real helix). All geometry is in
pitch units: depth is measured inward from the major diameter.
"""
from apw_style import *

# --- Basic thread geometry, in pitches --------------------------------------
H = np.sqrt(3) / 2              # sharp V height
APEX = 7 * H / 8                # depth of the sharp V root below the major diameter
TAN30 = np.tan(PI / 6)
UNC_EXT_ROOT = 17 * H / 24      # flat root of a UN external thread (0.6134P)
UNJ_R = 0.18                    # UNJ external root radius, max of 0.150P to 0.180P
UNC_MINOR = 5 * H / 8           # UNC 3B min minor: D - 1.082532P  (depth 0.5413P)
UNJC_MINOR = 0.974279 / 2       # UNJC 3B min minor: D - 0.974279P (depth 0.4871P)
NUT_ROOT = -0.06                # nut root just past the major diameter
PD_DEPTH = 3 * H / 8            # basic pitch diameter
R = 2.5                         # major radius (D = 5P)
R_OUT = 3.75                    # nut outside radius


def dist_to_root(z):
    """Axial distance from z to the nearest root (roots at whole pitches)."""
    return abs(((z + 0.5) % 1.0) - 0.5)


def v_depth(a):
    return APEX - a / TAN30


def ext_flat(z):
    return min(max(v_depth(dist_to_root(z)), 0.0), UNC_EXT_ROOT)


def ext_round(z, r=UNJ_R):
    a = dist_to_root(z)
    if a <= r * np.cos(PI / 6):
        return APEX - 2 * r + np.sqrt(r * r - a * a)
    return max(v_depth(a), 0.0)


def internal(minor):
    return lambda z: min(max(v_depth(dist_to_root(z)), NUT_ROOT), minor)


# --- Full section view ------------------------------------------------------
CX, CY, PS = -2.0, -0.35, 0.8   # center of the part axis, scene units per pitch
BOLT_Z = (-3.25, 3.25)
NUT_Z = (-2.0, 2.0)
N_PER_P = 80


def fx(depth, side=1):
    return CX + side * (R - depth) * PS


def fy(z):
    return CY + z * PS


def zs(z0, z1):
    return np.linspace(z0, z1, int((z1 - z0) * N_PER_P) + 1)


def poly(pts, fill, stroke, opacity=1.0, width=3):
    m = VMobject().set_points_as_corners([*pts, pts[0]])
    return m.set_fill(fill, opacity).set_stroke(stroke, width)


def bolt(depth_fn, stroke, fill=STEEL, z_range=BOLT_Z):
    z0, z1 = z_range
    right = [[fx(depth_fn(z), 1), fy(z), 0] for z in zs(z0, z1)[::-1]]
    left = [[fx(depth_fn(z + 0.5), -1), fy(z), 0] for z in zs(z0, z1)]
    return poly(right + left, fill, stroke)


def nut(depth_fn, stroke):
    z0, z1 = NUT_Z
    right = [[fx(depth_fn(z), 1), fy(z), 0] for z in zs(z0, z1)]
    right += [[CX + R_OUT * PS, fy(z1), 0], [CX + R_OUT * PS, fy(z0), 0]]
    left = [[fx(depth_fn(z + 0.5), -1), fy(z), 0] for z in zs(z0, z1)]
    left += [[CX - R_OUT * PS, fy(z1), 0], [CX - R_OUT * PS, fy(z0), 0]]
    return VGroup(poly(right, STEEL_DARK, stroke), poly(left, STEEL_DARK, stroke))


def axis_line():
    return DashedLine([CX, fy(BOLT_Z[1]) + 0.3, 0], [CX, fy(BOLT_Z[0]) - 0.3, 0],
                      dash_length=0.25, color=APW_MUTED, stroke_width=2)


# --- Detail view: one root on the right side, magnified ---------------------
DX, DY, DS = -2.2, -0.45, 10.0      # detail center and scene units per pitch
DZ = 0.3                            # half height of the detail, in pitches
D_NEAR, D_FAR = 0.30, 0.85          # depth range shown
D_MID = (D_NEAR + D_FAR) / 2


def dpt(depth, z):
    return [DX + (D_MID - depth) * DS, DY + z * DS, 0]


def clamp_depth(d):
    return min(max(d, D_NEAR), D_FAR)


def detail_bolt(depth_fn, stroke):
    pts = [dpt(clamp_depth(depth_fn(z)), z) for z in np.linspace(-DZ, DZ, 400)]
    pts += [dpt(D_FAR, DZ), dpt(D_FAR, -DZ)]
    return poly(pts, STEEL, stroke)


def detail_nut(depth_fn, stroke):
    pts = [dpt(clamp_depth(depth_fn(z)), z) for z in np.linspace(-DZ, DZ, 400)]
    pts += [dpt(D_NEAR, DZ), dpt(D_NEAR, -DZ)]
    return poly(pts, STEEL_DARK, stroke)


def overlap_slivers(nut_fn):
    """Where the nut crest overlaps the rounded root: bolt surface shallower than nut surface."""
    out = VGroup()
    for sign in (1, -1):
        z = sign * np.linspace(0, UNJ_R, 600)
        hit = [(zz, ext_round(zz), nut_fn(zz)) for zz in z if ext_round(zz) < nut_fn(zz) - 1e-6]
        if not hit:
            continue
        pts = [dpt(n, zz) for zz, _, n in hit] + [dpt(b, zz) for zz, b, _ in hit[::-1]]
        out.add(poly(pts, PROBLEM, PROBLEM, width=2))
    return out


# --- Minor diameter table data (ASME B1.1 UNC series) -----------------------
SIZES = [("#1", .073, 64), ("#2", .086, 56), ("#3", .099, 48), ("#4", .112, 40), ("#5", .125, 40),
         ("#6", .138, 32), ("#8", .164, 32), ("#10", .190, 24), ("#12", .216, 24),
         ("1/4", .25, 20), ("5/16", .3125, 18), ("3/8", .375, 16), ("7/16", .4375, 14),
         ("1/2", .5, 13), ("9/16", .5625, 12), ("5/8", .625, 11), ("3/4", .75, 10),
         ("7/8", .875, 9), ("1", 1, 8), ("1-1/8", 1.125, 7), ("1-1/4", 1.25, 7),
         ("1-3/8", 1.375, 6), ("1-1/2", 1.5, 6), ("1-3/4", 1.75, 5), ("2", 2, 4.5),
         ("2-1/4", 2.25, 4.5), ("2-1/2", 2.5, 4), ("2-3/4", 2.75, 4), ("3", 3, 4),
         ("3-1/4", 3.25, 4), ("3-1/2", 3.5, 4), ("3-3/4", 3.75, 4), ("4", 4, 4)]
COLS = [(-5.4, "Size", TEXT_COLOR), (-3.1, "TPI", TEXT_COLOR), (-0.4, "UNC-3B min minor", STANDARD),
        (2.9, "UNJC-3B min minor", IMPROVED), (5.6, "Difference", TEXT_COLOR)]


def minor_table(rows):
    header = VGroup(*[Text(h, font_size=22, color=c, weight=BOLD).move_to([x, 2.95, 0]) for x, h, c in COLS])
    rule = Line([-6.4, 2.7, 0], [6.6, 2.7, 0], color=APW_LOGO_BLUE, stroke_width=2)
    body = VGroup()
    for i, (size, d, tpi) in enumerate(rows):
        p = 1 / tpi
        unc, unjc = d - 1.082532 * p, d - 0.974279 * p
        y = 2.4 - i * 0.31
        vals = [size, f"{tpi:g}", f"{unc:.4f}", f"{unjc:.4f}", f"+{unjc - unc:.4f}"]
        body.add(VGroup(*[Text(v, font_size=22, color=c).move_to([x, y, 0])
                          for v, (x, _, c) in zip(vals, COLS)]))
    return header, rule, body


class UNJCvsUNC(APWScene):
    def construct(self):
        self.apw_intro("UNJC vs UNC Threads", "What changes on the internal thread",
                       narration="U N J C versus U N C threads, and what changes on the internal thread.")
        self.play(self.set_header("UNJC vs UNC"), *self.section("External thread"))

        # --- External thread -------------------------------------------------
        b = bolt(ext_flat, STANDARD)
        ax = axis_line()
        ext_lbl = callout("External thread\n(bolt), cut in half", [fx(1.5), fy(2.2), 0], [1.0, 2.2, 0])
        with self.voiceover(text="Here's a standard U N C external thread, cut in half so you can see both sides.") as t:
            self.play(Create(ax), DrawBorderThenFill(b), run_time=t.duration * 0.75)
            self.play(show_callout(ext_lbl), run_time=t.duration * 0.25)

        corners = VGroup()
        ac = (APEX - UNC_EXT_ROOT) * TAN30
        for k in range(-3, 4):
            for side, off in ((1, 0.0), (-1, 0.5)):
                for s in (-1, 1):
                    z = k - off + s * ac
                    if BOLT_Z[0] + 0.1 < z < BOLT_Z[1] - 0.1:
                        corners.add(Dot([fx(UNC_EXT_ROOT, side), fy(z), 0], radius=0.06, color=PROBLEM))
        crack = callout("Sharp root corners:\nfatigue cracks start here",
                        [fx(UNC_EXT_ROOT), fy(-1 + ac), 0], [1.0, -1.2, 0], color=PROBLEM)
        with self.voiceover(text="Its root can be flat, with sharp corners. "
                                 "Under load, those corners are where fatigue cracks start.") as t:
            self.play(FadeOut(ext_lbl), LaggedStart(*[GrowFromCenter(d) for d in corners], lag_ratio=0.04),
                      run_time=t.duration * 0.6)
            self.play(show_callout(crack), run_time=t.duration * 0.4)

        b_unj = bolt(ext_round, IMPROVED)
        rad = callout("Controlled root radius\n0.150P to 0.180P", [fx(APEX - UNJ_R), fy(0), 0], [1.0, 0.3, 0],
                      color=IMPROVED)
        with self.voiceover(text="On U N J C, the root must be a controlled radius, "
                                 "fifteen to eighteen hundredths of the pitch.") as t:
            self.play(FadeOut(corners), FadeOut(crack), run_time=0.5)
            self.play(Transform(b, b_unj), run_time=t.duration * 0.5)
            self.play(show_callout(rad), run_time=t.duration * 0.3)

        minor_x = R - (APEX - UNJ_R)
        ext_lines = VGroup(*[DashedLine([CX + s * minor_x * PS, fy(BOLT_Z[1]), 0],
                                        [CX + s * minor_x * PS, fy(BOLT_Z[0]) - 0.45, 0],
                                        dash_length=0.12, color=REF_A, stroke_width=2) for s in (-1, 1)])
        dim_y = fy(BOLT_Z[0]) - 0.35
        ext_dim = DoubleArrow([CX - minor_x * PS, dim_y, 0], [CX + minor_x * PS, dim_y, 0], buff=0,
                              color=REF_A, stroke_width=3, tip_length=0.18)
        ext_dim_lbl = Text("External minor Ø: larger than UNC", font_size=22, color=REF_A).next_to(ext_dim, DOWN, buff=0.1)
        cls = callout("UNJC external:\nclass 3A only", [fx(1.0), fy(-2.4), 0], [1.0, -2.2, 0])
        with self.voiceover(text="The rounded root sits higher, so the external minor diameter is larger. "
                                 "U N J C external threads are class three A only.") as t:
            self.play(FadeOut(rad), Create(ext_lines), GrowFromCenter(ext_dim), FadeIn(ext_dim_lbl),
                      run_time=t.duration * 0.55)
            self.play(show_callout(cls), run_time=t.duration * 0.3)
        self.play(FadeOut(VGroup(ext_lines, ext_dim, ext_dim_lbl, cls)), run_time=0.5)

        # --- Internal thread -------------------------------------------------
        n = nut(internal(UNC_MINOR), STANDARD)
        n_start = n.copy()
        n_start[0].shift(RIGHT * 6)
        n_start[1].shift(LEFT * 6)
        int_lbl = callout("Internal thread (nut)\nstandard UNC minor Ø",
                          [CX + 3.2 * PS, fy(1.3), 0], [1.7, 2.3, 0], color=STANDARD)
        with self.voiceover(text="Now the mating part: a nut with a standard U N C internal thread.") as t:
            self.play(*self.section("Internal thread"), run_time=0.4)
            self.play(Transform(n_start, n), run_time=t.duration * 0.55)
            self.play(show_callout(int_lbl), run_time=t.duration * 0.3)
        self.remove(n_start)
        self.add(n)
        self.bring_to_front(ax)

        # --- Detail: interference --------------------------------------------
        win = Rectangle(width=(D_FAR - D_NEAR) * PS, height=2 * DZ * PS, color=WHITE, stroke_width=3)
        win.move_to([fx(D_MID), fy(0), 0])
        frame = Rectangle(width=(D_FAR - D_NEAR) * DS, height=2 * DZ * DS, color=APW_LOGO_BLUE, stroke_width=4)
        frame.move_to([DX, DY, 0])
        db = detail_bolt(ext_round, IMPROVED)
        dn = detail_nut(internal(UNC_MINOR), STANDARD)
        dn_unj = detail_nut(internal(UNJC_MINOR), IMPROVED)
        full_view = VGroup(b, n, ax)

        with self.voiceover(text="Zoom in on one root, at true proportions.") as t:
            self.play(FadeOut(int_lbl), Create(win), *self.section("Detail: one root"), run_time=t.duration * 0.4)
            self.play(Transform(win, frame), FadeOut(full_view), run_time=t.duration * 0.6)
        self.play(FadeIn(db), FadeIn(dn), run_time=0.6)
        self.bring_to_front(win)

        unc_line = DashedLine(dpt(UNC_MINOR, DZ), dpt(UNC_MINOR, -DZ), dash_length=0.15, color=REF_A, stroke_width=3)
        unjc_line = DashedLine(dpt(UNJC_MINOR, DZ), dpt(UNJC_MINOR, -DZ), dash_length=0.15, color=REF_B, stroke_width=3)
        unc_tag = callout("UNC 3B min minor", dpt(UNC_MINOR, 0.27), [1.0, 2.4, 0], color=REF_A)
        r_tag = callout("Root radius\n0.180P (max)", dpt(APEX - UNJ_R, 0), [1.0, 0.3, 0], color=IMPROVED)
        with self.voiceover(text="Here's the bolt's rounded root, and the nut's crest at the standard U N C minor diameter.") as t:
            self.play(show_callout(r_tag), run_time=t.duration * 0.4)
            self.play(Create(unc_line), show_callout(unc_tag), run_time=t.duration * 0.4)

        slivers = overlap_slivers(internal(UNC_MINOR))
        hit = callout("Interference:\nnut crest corners\ncut into the radius",
                      [s.get_center() for s in slivers], [1.0, -1.0, 0], color=PROBLEM)
        with self.voiceover(text="The corners of the nut's crest run into the root radius. "
                                 "That's metal on metal, right where the bolt is most highly stressed.") as t:
            self.play(FadeIn(slivers), run_time=t.duration * 0.3)
            self.play(show_callout(hit), Indicate(slivers, color=PROBLEM, scale_factor=1.3), run_time=t.duration * 0.5)

        unjc_tag = callout("UNJC 3B min minor\n(larger)", dpt(UNJC_MINOR, -0.27), [1.0, -2.6, 0], color=REF_B)
        clear = callout("Crest clears\nthe radius", dpt(UNJC_MINOR, UNJ_R * np.cos(PI / 6)), [1.0, 1.4, 0],
                        color=IMPROVED)
        with self.voiceover(text="So U N J C internal threads have a larger minimum minor diameter. "
                                 "The crest moves out, and clears the radius.") as t:
            self.play(FadeOut(hit), FadeOut(slivers), run_time=0.4)
            self.play(Transform(dn, dn_unj), Create(unjc_line), show_callout(unjc_tag), run_time=t.duration * 0.5)
            self.play(show_callout(clear), run_time=t.duration * 0.25)
        self.play(FadeOut(VGroup(db, dn, win, unc_line, unjc_line, unc_tag, unjc_tag, clear, r_tag)), run_time=0.6)

        # --- Back to the full thread: what's the same, what changed ----------
        n_unj = nut(internal(UNJC_MINOR), IMPROVED)
        full = VGroup(b, n_unj, ax)
        pd_lines = VGroup(*[DashedLine([CX + s * (R - PD_DEPTH) * PS, fy(NUT_Z[1]) + 0.2, 0],
                                       [CX + s * (R - PD_DEPTH) * PS, fy(NUT_Z[0]) - 0.2, 0],
                                       dash_length=0.1, color=WHITE, stroke_width=2) for s in (-1, 1)])
        pd = callout("Pitch Ø: same as UNC 3B", [fx(PD_DEPTH), fy(1.75), 0], [1.7, 2.5, 0])
        major = callout("Major Ø: same as UNC 3B", [fx(NUT_ROOT), fy(0.5), 0], [1.7, 1.2, 0])
        with self.voiceover(text="Back to the full thread. Pitch diameter and major diameter are the same as U N C class three B.") as t:
            self.play(FadeIn(full), *self.section("UNJC internal thread"), run_time=1)
            self.play(Create(pd_lines), show_callout(pd), run_time=t.duration * 0.35)
            self.play(show_callout(major), run_time=t.duration * 0.3)

        minor = callout("Minor Ø: larger\nbigger tap drill or bore", [fx(UNJC_MINOR), fy(-1), 0], [1.7, -0.6, 0],
                        color=REF_B)
        top = fy(NUT_Z[1])
        eng_ext = VGroup(*[DashedLine([x, top + 0.05, 0], [x, top + 0.55, 0], dash_length=0.06,
                                      color=WHITE, stroke_width=2) for x in (fx(0), fx(UNJC_MINOR))])
        eng_dim = DoubleArrow([fx(UNJC_MINOR), top + 0.45, 0], [fx(0), top + 0.45, 0], buff=0,
                              color=WHITE, stroke_width=3, tip_length=0.12)
        eng = callout("Thread engagement:\nabout 10% less than UNC", eng_dim.get_center(), [1.7, -1.9, 0])
        with self.voiceover(text="Only the minor diameter changes. It's larger, so you drill or bore bigger, "
                                 "and you get about ten percent less thread engagement.") as t:
            self.play(show_callout(minor), run_time=t.duration * 0.4)
            self.play(Create(eng_ext), GrowFromCenter(eng_dim), show_callout(eng), run_time=t.duration * 0.4)
        self.play(FadeOut(VGroup(pd_lines, pd, major, minor, eng_ext, eng_dim, eng)), run_time=0.5)

        # --- Gauging -----------------------------------------------------------
        plug = bolt(ext_flat, STANDARD, fill=GAUGE, z_range=(-3.25, 2.9))
        handle = RoundedRectangle(corner_radius=0.1, width=1.4, height=0.8).set_fill(GAUGE, 1).set_stroke(STANDARD, 3)
        handle.next_to(plug, UP, buff=0)
        thread_plug = VGroup(plug, handle).shift(UP * 8)
        tp = callout("3B GO / NO-GO thread plug\nchecks pitch Ø", [fx(1.2), fy(1.0), 0], [1.7, 1.6, 0],
                     color=STANDARD)
        with self.voiceover(text="To check it, use standard three B GO and NO GO thread plugs for pitch diameter.") as t:
            self.play(b.animate.shift(UP * 8), *self.section("Gauging"), run_time=t.duration * 0.3)
            self.play(thread_plug.animate.shift(DOWN * 8), run_time=t.duration * 0.35)
            self.play(show_callout(tp), run_time=t.duration * 0.25)
        self.remove(b)

        pin_w = 2 * (R - UNJC_MINOR) * PS - 0.03
        pin = Rectangle(width=pin_w, height=(BOLT_Z[1] - BOLT_Z[0]) * PS).set_fill(GAUGE, 1).set_stroke(REF_B, 3)
        pin.move_to([CX, CY, 0])
        pin_handle = RoundedRectangle(corner_radius=0.1, width=1.4, height=0.8).set_fill(GAUGE, 1).set_stroke(REF_B, 3)
        pin_handle.next_to(pin, UP, buff=0)
        plain_plug = VGroup(pin, pin_handle).shift(UP * 8)
        pp = callout("Plain plug gauge\nchecks minor Ø separately", [fx(UNJC_MINOR), fy(-0.5), 0], [1.7, -0.9, 0],
                     color=REF_B)
        with self.voiceover(text="Then check the minor diameter separately, with a plain plug gauge to the U N J C limits.") as t:
            self.play(FadeOut(tp), thread_plug.animate.shift(UP * 8), run_time=t.duration * 0.3)
            self.play(plain_plug.animate.shift(DOWN * 8), run_time=t.duration * 0.35)
            self.play(show_callout(pp), run_time=t.duration * 0.25)
        self.play(FadeOut(VGroup(plain_plug, pp, n_unj, ax)), run_time=0.6)
        self.remove(thread_plug)

        # --- Minor diameter table ----------------------------------------------
        note = Text("Min minor = basic minor.  UNC: D − 1.082532P    UNJC: D − 0.974279P\n"
                    "Max minor and all other limits: ASME B1.1 / B1.15 and the print.",
                    font_size=18, color=APW_MUTED, line_spacing=0.8).to_corner(DL, buff=0.3)
        pages = [SIZES[:17], SIZES[17:]]
        lines = ["Here are the minimum minor diameters for every standard U N C and U N J C internal thread, class three B.",
                 "And the larger sizes. The U N J C minor is always bigger."]
        header = rule = body = None
        for i, (rows, line) in enumerate(zip(pages, lines)):
            new_header, new_rule, new_body = minor_table(rows)
            with self.voiceover(text=line) as t:
                if i == 0:
                    self.play(*self.section("Minimum minor diameters, class 3B"), FadeIn(new_header),
                              Create(new_rule), FadeIn(note), run_time=0.8)
                    header, rule = new_header, new_rule
                else:
                    self.play(FadeOut(body), run_time=0.4)
                self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in new_body], lag_ratio=0.12),
                          run_time=max(t.duration - 1.2, 1.5))
                body = new_body
            self.wait(4)

        with self.voiceover(text="Always confirm the exact limits on the print and in A S M E B 1 point 15.") as t:
            self.play(Indicate(note, color=WHITE, scale_factor=1.05), run_time=t.duration)
        self.play(FadeOut(VGroup(header, rule, body, note)), run_time=0.6)
        self.apw_outro()
