from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.gtts import GTTSService

P, H = 1.5, 0.8  # schematic pitch and thread height


def un_profile():
    pts = []
    for i in range(-3, 3):
        x = i * P
        pts += [[x, H, 0], [x + 0.2, H, 0], [x + 0.6, 0, 0], [x + 0.9, 0, 0], [x + 1.3, H, 0]]
    return VMobject().set_points_as_corners(pts).set_stroke(BLUE_C, 4)


def unj_profile():
    g = VGroup()
    for i in range(-3, 3):
        x = i * P
        g.add(
            Line([x, H, 0], [x + 0.2, H, 0]),
            Line([x + 0.2, H, 0], [x + 0.55, 0.12, 0]),
            ArcBetweenPoints([x + 0.55, 0.12, 0], [x + 0.95, 0.12, 0], angle=PI * 0.7),
            Line([x + 0.95, 0.12, 0], [x + 1.3, H, 0]),
            Line([x + 1.3, H, 0], [x + 1.5, H, 0]),
        )
    return g.set_stroke(GREEN_C, 4)


def bullets(*lines):
    return VGroup(*[Text("• " + l, font_size=28) for l in lines]).arrange(
        DOWN, aligned_edge=LEFT, buff=0.3)


class UNJCvsUNC(VoiceoverScene):
    def construct(self):
        self.set_speech_service(GTTSService())

        title = Text("UNJC vs UNC Threads", font_size=48).to_edge(UP)
        with self.voiceover(text="Let's look at U N J C threads, and how they differ from standard U N C.") as t:
            self.play(Write(title), run_time=t.duration)

        why = bullets("J = controlled root radius on the external thread",
                      "Rounded root = lower stress concentration",
                      "Much better fatigue life: aerospace standard",
                      "Defined by ASME B1.15").next_to(title, DOWN, buff=0.6)
        with self.voiceover(text="The J means the external thread must have a controlled, rounded root. "
                                 "A rounded root spreads out stress, so the bolt resists fatigue cracking much better. "
                                 "That's why it's common in aerospace.") as t:
            self.play(LaggedStart(*[FadeIn(b, shift=RIGHT) for b in why], lag_ratio=0.4), run_time=t.duration)
        self.play(FadeOut(why))

        # External thread profile comparison
        un = un_profile().shift(DOWN * 1.2)
        tag = Text("UNC external: flat or uncontrolled root", font_size=28).next_to(title, DOWN, buff=0.5)
        dots = VGroup(*[Dot([i * P + 0.75, -1.2, 0], color=RED) for i in range(-3, 3)])
        with self.voiceover(text="Here's a standard U N C external thread. Its root can be flat or sharp, "
                                 "and those corners are where cracks start.") as t:
            self.play(Create(un), FadeIn(tag), run_time=t.duration * 0.6)
            self.play(LaggedStart(*[Indicate(d, scale_factor=1.8) for d in dots]), run_time=t.duration * 0.4)

        unj = unj_profile().shift(DOWN * 1.2)
        tag2 = Text("UNJC external: required root radius", font_size=28).next_to(title, DOWN, buff=0.5)
        with self.voiceover(text="On a U N J C thread, the root is a required radius, "
                                 "roughly fifteen to eighteen percent of the pitch.") as t:
            self.play(FadeOut(dots), ReplacementTransform(un, unj), Transform(tag, tag2), run_time=t.duration)

        ext = bullets("Root radius required, and inspected",
                      "Larger minimum minor diameter",
                      "Class 3A only").to_edge(DOWN).shift(UP * 0.1)
        with self.voiceover(text="For the external thread, that means a larger minimum minor diameter, "
                                 "and it's held to class three A.") as t:
            self.play(FadeIn(ext), run_time=t.duration)
        self.play(FadeOut(ext))

        # Internal thread effect
        tag3 = Text("Internal thread: clear the root radius", font_size=28).next_to(title, DOWN, buff=0.5)
        un_line = DashedLine([-4.6, -1.05, 0], [4.6, -1.05, 0], color=YELLOW)
        un_lbl = Text("UNC 3B min minor", font_size=22, color=YELLOW).next_to(un_line, RIGHT, buff=0.1).shift(LEFT * 2.6 + DOWN * 0.3)
        with self.voiceover(text="Now the internal thread. A standard U N C minor diameter would let the nut's crests "
                                 "run down into that rounded root.") as t:
            self.play(Transform(tag, tag3), Create(un_line), FadeIn(un_lbl), run_time=t.duration)

        unj_line = DashedLine([-4.6, -0.8, 0], [4.6, -0.8, 0], color=ORANGE)
        unj_lbl = Text("UNJC 3B min minor (larger)", font_size=22, color=ORANGE).next_to(unj_line, UP, buff=0.1)
        with self.voiceover(text="So U N J C internal threads have a larger minor diameter, to clear the radius.") as t:
            self.play(TransformFromCopy(un_line, unj_line), FadeIn(unj_lbl), run_time=t.duration)
        self.play(FadeOut(VGroup(unj, un_line, un_lbl, unj_line, unj_lbl)))

        internal = bullets("Pitch diameter: same as UNC class 3B",
                           "Major diameter: same as UNC 3B",
                           "Minor diameter: larger, so a bigger tap drill or bore",
                           "Slightly less thread engagement",
                           "Gauge PD with 3B GO / NO-GO plugs",
                           "Check the minor diameter separately").next_to(title, DOWN, buff=0.6)
        with self.voiceover(text="For the internal thread, pitch and major diameter match U N C class three B. "
                                 "The difference is the minor diameter. It's larger, so you drill or bore bigger, "
                                 "and the thread has a bit less engagement. Check pitch diameter with standard three B "
                                 "gauges, but check the minor diameter separately.") as t:
            self.play(FadeOut(tag),
                      LaggedStart(*[FadeIn(b, shift=RIGHT) for b in internal], lag_ratio=0.3), run_time=t.duration)

        with self.voiceover(text="Always confirm the exact limits on the print and in A S M E B 1 point 15.") as t:
            self.play(Indicate(internal[2]), run_time=t.duration)
        self.wait(1)
