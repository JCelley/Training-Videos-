"""Shared drawing helpers for the True Position series (tp1_*.py ... tp5_*.py).

Drawing conventions
- Part coordinates are in inches; pt() maps them onto the screen.
- Basic dimensions get a box around the value, like on a print.
- All figures are made-up example values for training, not from a real print.
  Sources and what still needs checking: notes/true_position_sources.md.
"""
import types

from apw_style import *

SERIES = "True Position"


# --- Number formatting -------------------------------------------------------
def fmt(v, places=3, sign=False):
    """1.5 -> '1.500', 0.01 -> '.010', -0.004 -> '-.004' (shop style, no leading zero)."""
    s = f"{abs(v):.{places}f}"
    if s.startswith("0."):
        s = s[1:]
    if v < 0 and float(s) != 0:
        s = "-" + s
    elif sign:
        s = "+" + s
    return s


def zone_dia(dx, dy):
    """Diametral position deviation: 2 * sqrt(dx^2 + dy^2)."""
    return 2 * float(np.hypot(dx, dy))


# --- GD&T symbols, drawn from primitives (no font fallbacks) -----------------
def position_symbol(size=0.34, color=TEXT_COLOR, width=2.5):
    r = size * 0.32
    return VGroup(Circle(radius=r, color=color, stroke_width=width),
                  Line(LEFT * size / 2, RIGHT * size / 2, color=color, stroke_width=width),
                  Line(DOWN * size / 2, UP * size / 2, color=color, stroke_width=width))


def perp_symbol(size=0.3, color=TEXT_COLOR, width=2.5):
    return VGroup(Line(LEFT * size / 2 + DOWN * size / 2, RIGHT * size / 2 + DOWN * size / 2, color=color,
                       stroke_width=width),
                  Line(DOWN * size / 2, UP * size / 2, color=color, stroke_width=width))


def circled(letter, size=0.32, color=TEXT_COLOR):
    c = Circle(radius=size / 2, color=color, stroke_width=2.2)
    t = Text(letter, color=color, weight=BOLD).scale_to_fit_height(size * 0.5)
    return VGroup(c, t.move_to(c))


def fcf(*cells, h=0.52, font_size=26, color=TEXT_COLOR):
    """Feature control frame. Each cell is a str, a Mobject, or a list of those placed side by side.

    Returns a VGroup of cells; cell[i] = VGroup(box, content), so single cells can be highlighted.
    """
    contents = []
    for c in cells:
        parts = c if isinstance(c, (list, tuple)) else [c]
        mobs = [p if isinstance(p, Mobject) else Text(p, font_size=font_size, color=color) for p in parts]
        contents.append(VGroup(*mobs).arrange(RIGHT, buff=0.08))
    frame, x = VGroup(), 0.0
    for g in contents:
        w = max(g.width + 0.32, h)
        box = Rectangle(width=w, height=h, stroke_color=color, stroke_width=2.5)
        box.move_to([x + w / 2, 0, 0])
        g.move_to(box)
        frame.add(VGroup(box, g))
        x += w
    return frame.center()


def pos_fcf(tol, *datums, mod=None, proj=None, dia=True, **kw):
    """Position FCF: [pos][Ø tol (M)][A][B][C]. mod = 'M' / 'L'; proj = projected height text."""
    tcell = (["Ø"] if dia else []) + [tol]
    if mod:
        tcell.append(circled(mod))
    if proj:
        tcell += [circled("P"), proj]
    return fcf(position_symbol(), tcell, *datums, **kw)


def basic_box(text, color=TEXT_COLOR, font_size=22):
    t = Text(text, font_size=font_size, color=color)
    return VGroup(SurroundingRectangle(t, buff=0.07, color=color, stroke_width=2, corner_radius=0), t)


def dim(p1, p2, text, offset, color=REF_A, basic=True, font_size=22, ext=True):
    """Linear dimension between p1 and p2, drawn `offset` away (a vector perpendicular to p1->p2)."""
    p1, p2, off = np.array(p1, float), np.array(p2, float), np.array(offset, float)
    n = off / np.linalg.norm(off)
    a, b = p1 + off, p2 + off
    parts = VGroup()
    if ext:
        parts.add(Line(p1 + n * 0.06, a + n * 0.1, color=color, stroke_width=1.6),
                  Line(p2 + n * 0.06, b + n * 0.1, color=color, stroke_width=1.6))
    parts.add(DoubleArrow(a, b, buff=0, color=color, stroke_width=2.5, tip_length=0.14,
                          max_tip_length_to_length_ratio=0.4))
    label = basic_box(text, color, font_size) if basic else Text(text, font_size=font_size, color=color)
    half = abs(n[0]) * label.width / 2 + abs(n[1]) * label.height / 2
    label.move_to((a + b) / 2 + n * (half + 0.08))
    parts.add(label)
    return parts


def datum_tag(letter, at, direction, length=0.55, color=TEXT_COLOR, size=0.42):
    """ASME datum feature symbol: filled triangle on the feature, leader, boxed letter."""
    at = np.array(at, float)
    d = np.array(direction, float)
    d = d / np.linalg.norm(d)
    perp = np.array([-d[1], d[0], 0])
    tri = Polygon(at + perp * 0.13, at - perp * 0.13, at + d * 0.2, color=color, stroke_width=1.5)
    tri.set_fill(color, 1)
    leader = Line(at + d * 0.2, at + d * length, color=color, stroke_width=2)
    box = Square(size, color=color, stroke_width=2.5).move_to(at + d * (length + size / 2))
    t = Text(letter, font_size=26, color=color, weight=BOLD).move_to(box)
    return VGroup(tri, leader, box, t)


def crosshair(at, size=0.25, color=TEXT_COLOR, width=2):
    at = np.array(at, float)
    return VGroup(Line(at + LEFT * size, at + RIGHT * size, color=color, stroke_width=width),
                  Line(at + DOWN * size, at + UP * size, color=color, stroke_width=width))


def center_mark(at, size=0.3, color=APW_MUTED):
    at = np.array(at, float)
    return VGroup(DashedLine(at + LEFT * size, at + RIGHT * size, dash_length=0.06, color=color, stroke_width=1.6),
                  DashedLine(at + DOWN * size, at + UP * size, dash_length=0.06, color=color, stroke_width=1.6))


def pass_fail(ok, at=None):
    t = Text("PASS" if ok else "FAIL", font_size=30, weight=BOLD, color=IMPROVED if ok else PROBLEM)
    if at is not None:
        t.move_to(at)
    return t


def calc_lines(*lines, font_size=24, color=TEXT_COLOR, buff=0.18):
    """Calculation steps, left aligned. Each line is a str or (str, color)."""
    out = VGroup()
    for l in lines:
        text, c = (l, color) if isinstance(l, str) else l
        out.add(Text(text, font_size=font_size, color=c))
    return out.arrange(DOWN, aligned_edge=LEFT, buff=buff)


def panel(width, height, at, title=None):
    box = RoundedRectangle(corner_radius=0.12, width=width, height=height)
    box.set_fill(APW_PANEL, 0.85).set_stroke(APW_LOGO_BLUE, 2).move_to(at)
    g = VGroup(box)
    if title:
        g.add(Text(title, font_size=20, color=APW_LOGO_BLUE).next_to(box.get_top(), DOWN, buff=0.12))
    return g


# --- Part drawing --------------------------------------------------------------
class PartView:
    """Maps part inches to screen. origin = screen point of part (0, 0); s = screen units per inch."""

    def __init__(self, origin, s):
        self.o = np.array([*origin, 0.0][:3], float)
        self.s = s

    def __call__(self, x, y):
        return self.o + np.array([x * self.s, y * self.s, 0])

    def rect(self, x0, y0, x1, y1, fill=STEEL_DARK, stroke=STANDARD, opacity=1.0, width=3):
        r = Polygon(self(x0, y0), self(x1, y0), self(x1, y1), self(x0, y1))
        return r.set_fill(fill, opacity).set_stroke(stroke, width)

    def hole(self, x, y, d, stroke=STANDARD, fill=APW_DARK):
        return Circle(radius=d / 2 * self.s).move_to(self(x, y)).set_fill(fill, 1).set_stroke(stroke, 2.5)


# --- Simple orthographic 3D projection (keeps the scene 2D so text stays flat) ---
def project(p, az, el, center=ORIGIN, scale=1.0):
    """World point (x, y, z), z up -> screen. el=90 deg looks straight down; el=0 is a front view."""
    x, y, z = p
    ca, sa = np.cos(az), np.sin(az)
    x1 = x * ca + y * sa
    y1 = -x * sa + y * ca
    sy = y1 * np.sin(el) + z * np.cos(el)
    return np.array(center, float) + scale * np.array([x1, sy, 0.0])


def hull(points):
    """2D convex hull (monotone chain) of screen points; returns points in order."""
    pts = sorted({(round(p[0], 6), round(p[1], 6)) for p in points})
    if len(pts) < 3:
        return [np.array([*p, 0]) for p in pts]

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return [np.array([*p, 0]) for p in lower[:-1] + upper[:-1]]


def circle_pts(c, r, n=72, axis="z"):
    """Points of a circle of radius r around center c, in the plane normal to `axis`."""
    t = np.linspace(0, TAU, n, endpoint=False)
    c = np.array(c, float)
    if axis == "z":
        return [c + np.array([r * np.cos(a), r * np.sin(a), 0]) for a in t]
    if axis == "y":
        return [c + np.array([r * np.cos(a), 0, r * np.sin(a)]) for a in t]
    return [c + np.array([0, r * np.cos(a), r * np.sin(a)]) for a in t]


def poly3(pts3, az, el, center, scale, close=True):
    m = VMobject()
    pts = [project(p, az, el, center, scale) for p in pts3]
    m.set_points_as_corners(pts + [pts[0]] if close else pts)
    return m


def cylinder3(c0, c1, r, az, el, center, scale, color, opacity=0.25, axis="z", width=2.5):
    """Cylinder between end centers c0 and c1: filled silhouette plus both end circles."""
    e0 = circle_pts(c0, r, axis=axis)
    e1 = circle_pts(c1, r, axis=axis)
    sil = Polygon(*hull([project(p, az, el, center, scale) for p in e0 + e1]))
    sil.set_fill(color, opacity).set_stroke(color, width)
    ends = VGroup(poly3(e0, az, el, center, scale).set_stroke(color, width * 0.7),
                  poly3(e1, az, el, center, scale).set_stroke(color, width * 0.7))
    return VGroup(sil, ends)


# --- Base scene for the series -------------------------------------------------
class TPScene(APWScene):
    part_no = 1
    part_title = ""

    def say(self, text, *steps):
        """One spoken line. Each step is (fraction_of_line, anim, anim, ...).

        A plain function (lambda) in a step is called when the step starts, so it can
        build animations from the scene state at that moment.
        """
        with self.voiceover(text=text) as t:
            for step in steps:
                frac, *anims = step
                built = []
                for a in anims:
                    if isinstance(a, types.FunctionType):
                        a = a()
                    built.extend(a if isinstance(a, (list, tuple)) else [a])
                if built:
                    self.play(*built, run_time=max(t.duration * frac, 0.4))

    def start(self, subtitle, narration):
        self.apw_intro(f"True Position, Part {self.part_no}", subtitle, narration=narration)
        self.play(self.set_header(f"True Position {self.part_no}/5"), run_time=0.6)

    def clear_stage(self, run_time=0.6):
        keep = {self.corner_logo, self.header, self.section_label, getattr(self, "tag", None)}
        others = [m for m in self.mobjects if m not in keep]
        if others:
            self.play(FadeOut(Group(*others)), run_time=run_time)

    def example_tag(self):
        """Small reminder that the numbers are made up."""
        tag = Text("Example values for training", font_size=18, color=APW_MUTED).to_corner(DL, buff=0.3)
        self.add(tag)
        return tag
