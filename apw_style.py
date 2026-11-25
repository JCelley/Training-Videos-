"""APW house style for Manim training videos.

Usage in a video file:

    from apw_style import *

    class Collets(APWScene):
        def construct(self):
            self.apw_intro("Collets", "Types, sizes and care")
            ...
            self.apw_outro()

APWScene sets up the gTTS voice, keeps a small logo in the bottom-right corner,
and provides a standard intro and outro. Build titles, step labels and bullets
with the helpers below so every video looks the same.
"""
from pathlib import Path

from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.gtts import GTTSService

ASSETS = Path(__file__).parent / "assets"
LOGO_PATH = ASSETS / "apw_logo.png"

# --- Company colors (from the Tool Tag Generator's CSS variables) -----------
APW_LOGO_BLUE = "#689DCC"  # sampled from apw-logo-stacked-blue.png
APW_BLUE = "#0057A8"
APW_ACCENT = "#00AAFF"
APW_GREEN = "#00E676"
APW_WARN = "#FFAA00"
APW_DARK = "#0A0F1A"
APW_PANEL = "#1A2234"
APW_TEXT = "#E8EDF5"
APW_MUTED = "#6B7A99"

# --- Meaning colors (keep these consistent across every video) -------------
STANDARD = BLUE_C   # standard / baseline, e.g. UNC
IMPROVED = GREEN_C  # improved / correct, e.g. UNJC
PROBLEM = RED       # problem spots, failure points
REF_A = YELLOW      # reference lines that need telling apart...
REF_B = ORANGE      # ...from each other

TEXT_COLOR = WHITE
TITLE_SIZE = 48
LABEL_SIZE = 30
BULLET_SIZE = 28


# --- Text helpers -----------------------------------------------------------
def apw_title(text):
    """Scene title, pinned to the top edge."""
    return Text(text, font_size=TITLE_SIZE, color=TEXT_COLOR).to_edge(UP)


def step_label(text, title):
    """Step caption that sits under the title, e.g. '3. Spin on photoresist'."""
    return Text(text, font_size=LABEL_SIZE, color=TEXT_COLOR).next_to(title, DOWN)


def bullets(*lines, font_size=BULLET_SIZE):
    """Left-aligned bullet list. Reveal with reveal_bullets() so viewers can't read ahead."""
    return VGroup(*[Text("• " + l, font_size=font_size, color=TEXT_COLOR) for l in lines]).arrange(
        DOWN, aligned_edge=LEFT, buff=0.3)


def reveal_bullets(group, lag_ratio=0.4):
    """Animation that fades bullets in one at a time."""
    return LaggedStart(*[FadeIn(b, shift=RIGHT) for b in group], lag_ratio=lag_ratio)


def apw_logo(height=2.5):
    return ImageMobject(str(LOGO_PATH)).set_height(height)


# --- Base scene -------------------------------------------------------------
class APWScene(VoiceoverScene):
    """VoiceoverScene with APW voice, corner logo, intro and outro."""

    corner_logo_height = 0.45
    corner_logo_opacity = 0.6

    def setup(self):
        super().setup()
        self.set_speech_service(GTTSService())
        self.corner_logo = None

    def _corner_position(self, mob):
        return mob.to_corner(DR, buff=0.25)

    def add_corner_logo(self):
        """Show the small logo in the bottom-right corner, drawn above everything else."""
        if self.corner_logo is None:
            self.corner_logo = self._corner_position(
                apw_logo(self.corner_logo_height).set_opacity(self.corner_logo_opacity))
            self.add_foreground_mobject(self.corner_logo)

    def apw_intro(self, title, subtitle=None, narration=None):
        """Logo, then title, then the logo shrinks into the corner.

        narration defaults to just reading the title. Leaves nothing on screen
        except the corner logo, so the video starts on a clean frame.
        """
        logo = apw_logo(2.5).shift(UP * 1.2)
        heading = Text(title, font_size=56, color=TEXT_COLOR).next_to(logo, DOWN, buff=0.6)
        group = [heading]
        if subtitle:
            sub = Text(subtitle, font_size=30, color=APW_LOGO_BLUE).next_to(heading, DOWN, buff=0.3)
            group.append(sub)
        rule = Line(LEFT * 3, RIGHT * 3, color=APW_LOGO_BLUE, stroke_width=3).next_to(group[-1], DOWN, buff=0.3)

        self.play(FadeIn(logo, scale=0.9), run_time=1)
        with self.voiceover(text=narration or title) as t:
            self.play(Write(heading), *[FadeIn(m, shift=UP * 0.2) for m in group[1:]],
                      Create(rule), run_time=max(t.duration, 1))
        self.wait(0.5)

        target = self._corner_position(
            apw_logo(self.corner_logo_height).set_opacity(self.corner_logo_opacity))
        self.play(FadeOut(VGroup(*group, rule)),
                  logo.animate.set_height(self.corner_logo_height)
                      .move_to(target).set_opacity(self.corner_logo_opacity),
                  run_time=1)
        self.remove(logo)
        self.add_corner_logo()

    def apw_outro(self, narration=None):
        """Clear the screen and end on the full logo."""
        others = [m for m in self.mobjects if m is not self.corner_logo]
        if others:
            self.play(FadeOut(Group(*others)), run_time=0.8)
        logo = apw_logo(3)
        if self.corner_logo is not None:
            self.remove_foreground_mobject(self.corner_logo)
            self.remove(self.corner_logo)
            self.corner_logo = None
        if narration:
            with self.voiceover(text=narration) as t:
                self.play(FadeIn(logo, scale=0.9), run_time=max(t.duration, 1))
        else:
            self.play(FadeIn(logo, scale=0.9), run_time=1)
        self.wait(1.5)
        self.play(FadeOut(logo), run_time=0.8)
