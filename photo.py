from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.gtts import GTTSService


class Photolithography(VoiceoverScene):
    def construct(self):
        self.set_speech_service(GTTSService())

        title = Text("Photolithography", font_size=48).to_edge(UP)

        def label(t):
            return Text(t, font_size=30).next_to(title, DOWN)

        def layer(color, below):
            parts = VGroup(
                Rectangle(width=3, height=0.3),
                Rectangle(width=2, height=0.3),
                Rectangle(width=3, height=0.3),
            ).arrange(RIGHT, buff=0)
            parts.set_fill(color, 1).set_stroke(width=0)
            return parts.next_to(below, UP, buff=0)

        with self.voiceover(text="Photolithography is how patterns are printed onto silicon chips.") as t:
            self.play(Write(title), run_time=t.duration)

        step = label("1. Silicon wafer")
        wafer = Rectangle(width=8, height=1).set_fill(GREY_D, 1).set_stroke(width=0).shift(DOWN * 2)
        with self.voiceover(text="We start with a clean silicon wafer.") as t:
            self.play(FadeIn(step), FadeIn(wafer, shift=UP), run_time=t.duration)

        oxide = layer(BLUE_D, wafer)
        with self.voiceover(text="A thin layer of oxide is grown on top.") as t:
            self.play(Transform(step, label("2. Grow oxide layer")),
                      GrowFromEdge(oxide, DOWN), run_time=t.duration)

        resist = layer(RED_C, oxide)
        with self.voiceover(text="Then a light sensitive coating, called photoresist, is spun on.") as t:
            self.play(Transform(step, label("3. Spin on photoresist")),
                      GrowFromEdge(resist, DOWN), run_time=t.duration)

        mask = VGroup(
            Rectangle(width=3, height=0.2).move_to(LEFT * 2.5),
            Rectangle(width=3, height=0.2).move_to(RIGHT * 2.5),
        ).set_fill(GREY_B, 1).set_stroke(width=0).next_to(resist, UP, buff=1.5)
        with self.voiceover(text="A mask with the pattern is lined up above the wafer.") as t:
            self.play(Transform(step, label("4. Align the mask")),
                      FadeIn(mask, shift=DOWN), run_time=t.duration)

        rays = VGroup()
        for x in np.linspace(-3.5, 3.5, 15):
            end_y = resist.get_top()[1] if abs(x) < 1 else mask.get_top()[1]
            rays.add(Arrow([x, 2.2, 0], [x, end_y, 0], buff=0, color=PURPLE_A,
                           stroke_width=3, max_tip_length_to_length_ratio=0.15))
        with self.voiceover(text="Ultraviolet light shines through the gap, exposing only part of the resist.") as t:
            self.play(Transform(step, label("5. Expose to UV light")),
                      LaggedStart(*[GrowArrow(r) for r in rays], lag_ratio=0.05),
                      run_time=t.duration * 0.7)
            self.play(resist[1].animate.set_fill(YELLOW_C), run_time=t.duration * 0.3)
        self.play(FadeOut(rays), FadeOut(mask))

        with self.voiceover(text="The developer washes away the exposed resist.") as t:
            self.play(Transform(step, label("6. Develop")),
                      FadeOut(resist[1], shift=UP * 0.3), run_time=t.duration)

        with self.voiceover(text="Etching removes the oxide that is no longer protected.") as t:
            self.play(Transform(step, label("7. Etch the oxide")),
                      oxide[1].animate.stretch_to_fit_height(0.01, about_edge=DOWN),
                      run_time=t.duration)
        self.remove(oxide[1])

        with self.voiceover(text="Finally, the leftover resist is stripped, and the pattern is transferred.") as t:
            self.play(Transform(step, label("8. Strip resist")),
                      FadeOut(resist[0], resist[2], shift=UP), run_time=t.duration)
        self.wait(1)
