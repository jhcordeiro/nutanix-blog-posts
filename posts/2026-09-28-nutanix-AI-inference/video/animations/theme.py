from pathlib import Path

from manim import (
    BOLD,
    DOWN,
    LEFT,
    NORMAL,
    ORIGIN,
    RIGHT,
    UL,
    UP,
    Line,
    Rectangle,
    RoundedRectangle,
    Text,
    VGroup,
    always_redraw,
    config,
)
from manim_slides import Slide

BG = "#0b1020"
PAPER = "#121a2b"
SOFT = "#1e293b"
INK = "#f8fafc"
TEXT = "#dbe3ef"
MUTED = "#a8b5c8"
LINE = "#334155"
INDIGO = "#818cf8"
INDIGO_SOFT = "#25294a"
AMBER = "#fbbf24"
AMBER_SOFT = "#3a2b12"
GREEN = "#6ee7a1"
RED = "#fca5a5"

SANS = "Helvetica Neue"
MONO = "Menlo"

config.background_color = BG

NARRATION_DIR = Path(__file__).resolve().parent.parent / "narration"


def paragraphs(prefix):
    path = next(NARRATION_DIR.glob(f"{prefix}-*.txt"))
    return [p.strip() for p in path.read_text().split("\n\n") if p.strip()]


class NarratedSlide(Slide):
    """A slide whose steps are the paragraphs of one narration file.

    Call ``beat()`` before the animations for each paragraph; the paragraph
    becomes the step's speaker notes. Rendering fails if the number of beats
    doesn't match the number of paragraphs.
    """

    narration = ""

    def setup(self):
        super().setup()
        self._paragraphs = paragraphs(self.narration)
        self._beats = 0

    def beat(self):
        self.next_slide(notes=self._paragraphs[self._beats])
        self._beats += 1

    def tear_down(self):
        if self._beats != len(self._paragraphs):
            raise ValueError(
                f"{type(self).__name__}: {self._beats} beats for "
                f"{len(self._paragraphs)} narration paragraphs"
            )
        super().tear_down()


def txt(s, size=28, color=TEXT, weight=NORMAL, font=SANS, **kwargs):
    return Text(s, font=font, font_size=size, color=color, weight=weight, **kwargs)


def mono(s, size=22, color=TEXT, weight=NORMAL, **kwargs):
    return txt(s, size, color, weight, font=MONO, **kwargs)


def header(kicker, heading):
    k = mono(kicker.upper(), 18, INDIGO, BOLD)
    h = txt(heading, 44, INK, BOLD)
    return VGroup(k, h).arrange(DOWN, aligned_edge=LEFT, buff=0.18).to_corner(UL, buff=0.55)


def panel(width, height, stroke=LINE, fill=PAPER, fill_opacity=1.0, radius=0.08, stroke_width=2):
    return RoundedRectangle(
        corner_radius=radius,
        width=width,
        height=height,
        stroke_color=stroke,
        stroke_width=stroke_width,
        fill_color=fill,
        fill_opacity=fill_opacity,
    )


def card(title, body=None, width=4.0, height=None, accent=INDIGO, title_size=26, body_size=19):
    """A panel with an accent bar on top, a title, and optional muted body text."""
    parts = [txt(title, title_size, INK, BOLD)]
    if body:
        parts.append(txt(body, body_size, MUTED, line_spacing=0.9))
    content = VGroup(*parts).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
    if content.width > width - 0.5:
        content.scale_to_fit_width(width - 0.5)
    h = height or content.height + 0.7
    box = panel(width, h)
    bar = Line(box.get_corner(UL) + RIGHT * 0.08, box.get_corner(UP + RIGHT) + LEFT * 0.08,
               color=accent, stroke_width=6)
    content.move_to(box).align_to(box, LEFT).shift(RIGHT * 0.25)
    return VGroup(box, bar, content)


def chip(s, color=INDIGO, size=18, fill=None):
    label = mono(s, size, color, BOLD)
    box = RoundedRectangle(
        corner_radius=0.17,
        width=label.width + 0.4,
        height=label.height + 0.24,
        stroke_color=color,
        stroke_width=2,
        fill_color=fill or BG,
        fill_opacity=1,
    )
    return VGroup(box, label.move_to(box))


def labeled_box(s, width, height, color=INDIGO, size=22, fill=PAPER, text_color=INK):
    box = panel(width, height, stroke=color, fill=fill)
    label = txt(s, size, text_color, BOLD)
    if label.width > width - 0.3:
        label.scale_to_fit_width(width - 0.3)
    return VGroup(box, label.move_to(box))


def gpu_slot(width=0.5, height=0.8):
    return RoundedRectangle(
        corner_radius=0.05, width=width, height=height,
        stroke_color=LINE, stroke_width=2, fill_color=BG, fill_opacity=1,
    )


class Server(VGroup):
    """An outlined server with a row of GPU slots and a label above it."""

    def __init__(self, label, slots=8, slot_width=0.5, slot_height=0.8, **kwargs):
        super().__init__(**kwargs)
        self.slots = VGroup(*[gpu_slot(slot_width, slot_height) for _ in range(slots)]).arrange(RIGHT, buff=0.12)
        self.outline = panel(self.slots.width + 0.4, self.slots.height + 0.4, fill=PAPER).move_to(self.slots)
        self.label = mono(label, 18, MUTED).next_to(self.outline, UP, buff=0.12).align_to(self.outline, LEFT)
        self.add(self.outline, self.slots, self.label)


class MemoryBar(VGroup):
    """A horizontal bar where x-position is proportional to gigabytes."""

    def __init__(self, capacity_gb, width=12.0, height=0.9, **kwargs):
        super().__init__(**kwargs)
        self.capacity = capacity_gb
        self.bar_width = width
        self.bar_height = height
        self.outline = Rectangle(width=width, height=height, stroke_color=MUTED, stroke_width=2)
        self.add(self.outline)

    def x_at(self, gb):
        return self.outline.get_left() + RIGHT * (gb / self.capacity) * self.bar_width

    def block(self, start_gb, size_gb, color, opacity=0.85):
        w = (size_gb / self.capacity) * self.bar_width
        r = Rectangle(
            width=w, height=self.bar_height - 0.08,
            stroke_color=BG, stroke_width=2, fill_color=color, fill_opacity=opacity,
        )
        r.move_to(self.x_at(start_gb) + RIGHT * w / 2)
        r.set_y(self.outline.get_y())
        return r


def counter(tracker, fmt, size=64, color=INDIGO, anchor=ORIGIN, align=None):
    """Text that redraws from a ValueTracker. Avoids DecimalNumber, which needs LaTeX."""

    def build():
        t = mono(fmt(tracker.get_value()), size, color, BOLD)
        t.move_to(anchor)
        if align is not None:
            t.align_to(anchor, align)
        return t

    return always_redraw(build)


def pull_quote(s, size=36, width=None):
    quote = txt(s, size, INK, BOLD, line_spacing=0.95)
    if width and quote.width > width:
        quote.scale_to_fit_width(width)
    bar = Line(UP, DOWN, color=INDIGO, stroke_width=8)
    bar.set_height(quote.height + 0.3).next_to(quote, LEFT, buff=0.35)
    return VGroup(bar, quote)
