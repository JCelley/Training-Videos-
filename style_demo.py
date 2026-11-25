from apw_style import *


class StyleDemo(APWScene):
    """Short check that the house style renders: intro, colors, bullets, outro."""

    def construct(self):
        self.apw_intro("APW Training", "House style demo",
                       narration="Welcome to American Precision Works training.")

        title = apw_title("Color meanings")
        swatches = VGroup(*[
            VGroup(Square(0.5).set_fill(c, 1).set_stroke(width=0),
                   Text(name, font_size=26)).arrange(RIGHT, buff=0.3)
            for c, name in [(STANDARD, "Standard / baseline"), (IMPROVED, "Improved / correct"),
                            (PROBLEM, "Problem spot"), (REF_A, "Reference line A"),
                            (REF_B, "Reference line B")]
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.3).next_to(title, DOWN, buff=0.6)

        with self.voiceover(text="Colors mean the same thing in every video.") as t:
            self.play(Write(title), reveal_bullets(swatches, lag_ratio=0.3), run_time=t.duration)
        self.play(FadeOut(swatches))

        points = bullets("One spoken line per step",
                         "Bullets appear one at a time",
                         "Check figures against the print").next_to(title, DOWN, buff=0.6)
        with self.voiceover(text="Each step gets one spoken line, and bullets appear one at a time.") as t:
            self.play(Transform(title, apw_title("House rules")), reveal_bullets(points), run_time=t.duration)

        self.apw_outro()
