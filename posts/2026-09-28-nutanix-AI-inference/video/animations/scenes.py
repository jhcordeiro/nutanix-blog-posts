"""Manim scenes for the video explainer, one Slide class per narration file.

Each ``self.beat()`` starts a new click-to-advance step and attaches the next
narration paragraph as speaker notes (press S in the HTML deck to see them).
"""

from manim import *

from theme import (
    AMBER,
    AMBER_SOFT,
    BG,
    GREEN,
    INDIGO,
    INDIGO_SOFT,
    INK,
    LINE,
    MUTED,
    PAPER,
    RED,
    SOFT,
    TEXT,
    MemoryBar,
    NarratedSlide,
    Server,
    card,
    chip,
    counter,
    header,
    labeled_box,
    mono,
    panel,
    pull_quote,
    txt,
)


def token(size=0.42, color=LINE, fill=BG, opacity=1.0):
    return Square(side_length=size, stroke_color=color, stroke_width=2, fill_color=fill, fill_opacity=opacity)


def rack(slots=8, width=1.1, height=3.0):
    body = panel(width, height, stroke=MUTED, fill=PAPER)
    lines = VGroup(*[
        Line(LEFT * (width / 2 - 0.15), RIGHT * (width / 2 - 0.15), color=INDIGO, stroke_width=3)
        for _ in range(slots)
    ]).arrange(DOWN, buff=(height - 0.6) / slots).move_to(body)
    return VGroup(body, lines)


def clear(scene, *keep, run_time=0.6):
    gone = [m for m in scene.mobjects if m not in keep]
    if gone:
        scene.play(*[FadeOut(m) for m in gone], run_time=run_time)


class S01Hook(NarratedSlide):
    narration = "01"

    def construct(self):
        self.beat()
        prompt = mono("user: Explain the KV cache in one sentence.", 22, AMBER)
        answer = txt(
            "It stores each layer's attention keys and values,\nso every new token can reuse them.",
            28, INK, line_spacing=0.9,
        )
        content = VGroup(prompt, answer).arrange(DOWN, aligned_edge=LEFT, buff=0.35)
        bubble = panel(content.width + 0.9, content.height + 0.8)
        content.move_to(bubble)
        chat = VGroup(bubble, prompt, answer)
        self.play(FadeIn(bubble, shift=UP * 0.2), FadeIn(prompt))
        self.play(AddTextLetterByLetter(answer, time_per_char=0.03))
        self.wait(0.3)

        server = Server("GPU SERVER · 8 GPUS").move_to(DOWN * 1.6)
        self.play(chat.animate.scale(0.6).to_edge(UP, buff=0.5), FadeIn(server, shift=UP * 0.3))
        arrow = Arrow(server.get_top(), chat.get_bottom(), buff=0.15, color=INDIGO)
        self.play(GrowArrow(arrow), LaggedStart(*[
            s.animate.set_fill(INDIGO, 0.8) for s in server.slots
        ], lag_ratio=0.08))

        racks = VGroup(*[rack() for _ in range(9)]).arrange(RIGHT, buff=0.3).move_to(DOWN * 1.5)
        self.play(FadeOut(arrow), ReplacementTransform(server, racks[4]))
        self.play(LaggedStart(*[FadeIn(r, shift=UP * 0.2) for i, r in enumerate(racks) if i != 4], lag_ratio=0.08))
        arrow = Arrow(racks.get_top(), chat.get_bottom(), buff=0.15, color=INDIGO)
        self.play(GrowArrow(arrow))
        name = chip("INFERENCE: A REQUEST IN, AN ANSWER OUT", AMBER, 18).next_to(arrow, RIGHT, buff=0.3)
        self.play(FadeIn(name, shift=LEFT * 0.2))
        self.wait(0.2)

        self.beat()
        clear(self)
        head = header("01 · The basics", "What inference is")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        panels = VGroup(panel(6.3, 4.6), panel(6.3, 4.6)).arrange(RIGHT, buff=0.4).move_to(DOWN * 0.8)
        titles = VGroup(
            VGroup(mono("TRAINING", 30, INDIGO, BOLD), txt("the model learns", 22, MUTED)).arrange(DOWN, buff=0.12),
            VGroup(mono("INFERENCE", 30, AMBER, BOLD), txt("the model answers", 22, MUTED)).arrange(DOWN, buff=0.12),
        )
        for t, p in zip(titles, panels):
            t.move_to(p.get_top() + DOWN * 0.65)
        weights = VGroup(*[
            Square(0.28, stroke_color=BG, stroke_width=2, fill_color=INDIGO, fill_opacity=0.3) for _ in range(32)
        ]).arrange_in_grid(rows=4, cols=8, buff=0.08).move_to(panels[0]).shift(UP * 0.05)
        self.play(FadeIn(panels), LaggedStart(*[FadeIn(t, shift=DOWN * 0.2) for t in titles], lag_ratio=0.4))
        self.play(FadeIn(weights))
        rng = np.random.default_rng(7)
        for _ in range(5):
            self.play(*[w.animate.set_fill(INDIGO, rng.uniform(0.15, 1.0)) for w in weights], run_time=0.35)
        notes = []
        for grid_x, label, body, color in [
            (panels[0].get_x(), "WEIGHTS CHANGE ON EVERY STEP", "one long job · days to weeks", INDIGO),
            (panels[1].get_x(), "WEIGHTS STAY FIXED", "always-on service · every request, all day", AMBER),
        ]:
            note = VGroup(chip(label, color, 16), txt(body, 20, MUTED)).arrange(DOWN, buff=0.2)
            note.next_to(weights, DOWN, buff=0.3).set_x(grid_x)
            notes.append(note)
        self.play(FadeIn(notes[0], shift=UP * 0.1))
        frozen = weights.copy().set_x(panels[1].get_x())
        self.play(TransformFromCopy(weights, frozen), run_time=1.2)
        self.play(FadeIn(notes[1], shift=UP * 0.1))
        y = frozen.get_y()
        for _ in range(3):
            req = Square(0.2, stroke_width=0, fill_color=AMBER, fill_opacity=1).move_to([panels[1].get_left()[0] + 0.3, y, 0])
            ans = Square(0.2, stroke_width=0, fill_color=GREEN, fill_opacity=1).move_to([frozen.get_right()[0] + 0.2, y, 0])
            self.play(req.animate.move_to([frozen.get_left()[0] - 0.2, y, 0]), run_time=0.4)
            self.remove(req)
            self.play(Indicate(frozen, color=AMBER, scale_factor=1.03), run_time=0.35)
            self.add(ans)
            self.play(ans.animate.move_to([panels[1].get_right()[0] - 0.3, y, 0]), run_time=0.4)
            self.play(FadeOut(ans), run_time=0.15)
        self.wait(0.2)

        self.beat()
        clear(self, head)
        layers = [
            ("Application", "chat · IDE agent · RAG", MUTED),
            ("API\ngateway", "auth · quotas · routing", MUTED),
            ("Serving\nframework", "vLLM · SGLang", INDIGO),
            ("Model\nruntime", "PyTorch · GPU kernels", MUTED),
            ("GPU", "memory · bandwidth", MUTED),
        ]
        boxes = VGroup(*[labeled_box(n, 2.3, 1.2, color=c, size=24) for n, _, c in layers]).arrange(RIGHT, buff=0.4).move_to(UP * 0.2)
        subs = VGroup(*[mono(s, 14, MUTED).next_to(b, DOWN, buff=0.2) for (_, s, _), b in zip(layers, boxes)])
        links = VGroup(*[
            Arrow(a.get_right(), b.get_left(), buff=0.05, color=LINE, stroke_width=3, max_tip_length_to_length_ratio=0.35)
            for a, b in zip(boxes, boxes[1:])
        ])
        self.play(LaggedStart(*[
            AnimationGroup(FadeIn(b, shift=RIGHT * 0.2), FadeIn(s), *([GrowArrow(links[i - 1])] if i else []))
            for i, (b, s) in enumerate(zip(boxes, subs))
        ], lag_ratio=0.4, run_time=3))
        top_y = boxes.get_top()[1] + 0.35
        dot = Square(0.22, stroke_width=0, fill_color=AMBER, fill_opacity=1).move_to([boxes[0].get_x(), top_y, 0])
        request = VGroup(dot, mono("request", 16, AMBER).next_to(dot, UP, buff=0.08))
        self.play(FadeIn(request))
        self.play(
            request.animate.shift(RIGHT * (boxes[-1].get_x() - boxes[0].get_x())),
            LaggedStart(*[Indicate(b, color=AMBER, scale_factor=1.04) for b in boxes], lag_ratio=0.3),
            run_time=2.2,
        )
        self.play(FadeOut(request))
        answer_label = mono("answer, token by token", 16, GREEN).move_to([0, top_y + 0.3, 0])
        answers = [
            Square(0.16, stroke_width=0, fill_color=GREEN, fill_opacity=1).move_to([boxes[-1].get_x(), top_y, 0])
            for _ in range(6)
        ]
        self.play(FadeIn(answer_label), LaggedStart(*[
            a.animate.move_to([boxes[0].get_x(), top_y, 0]) for a in answers
        ], lag_ratio=0.2, run_time=2.2))
        self.play(FadeOut(answer_label), *[FadeOut(a) for a in answers])
        self.wait(0.2)

        self.beat()
        ours = chip("OUR TEAM OPERATES THIS LAYER", AMBER, 16).next_to(subs[2], DOWN, buff=0.3)
        outline = panel(2.3, 1.2, stroke=AMBER, fill_opacity=0, stroke_width=5).move_to(boxes[2])
        self.play(Create(outline), FadeIn(ours, shift=UP * 0.1))
        self.play(LaggedStart(*[Indicate(boxes[i], color=RED, scale_factor=1.05) for i in (1, 2, 3, 4)], lag_ratio=0.35))
        limit = txt("Any layer in the path can set the speed limit.", 32, INK, BOLD).move_to(DOWN * 2.35)
        seen = mono("to the user, every bottleneck looks like a slow answer", 18, MUTED).next_to(limit, DOWN, buff=0.25)
        self.play(FadeIn(limit, shift=UP * 0.2))
        self.play(FadeIn(seen))

        self.beat()
        clear(self)
        question = txt("“Which model is best?”", 56, INK, BOLD)
        self.play(Write(question))
        strike = Line(question.get_left() + LEFT * 0.2, question.get_right() + RIGHT * 0.2, color=AMBER, stroke_width=8)
        self.play(Create(strike))
        self.play(VGroup(question, strike).animate.scale(0.6).set_opacity(0.45).to_edge(UP, buff=1.0))
        rows = VGroup(*[
            VGroup(chip(n, AMBER), txt(q, 34, INK)).arrange(RIGHT, buff=0.4)
            for n, q in [
                ("01", "How many GPUs does this model need?"),
                ("02", "How many servers does that span?"),
                ("03", "What fails first when 1,000 coding agents hit it?"),
            ]
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.55).move_to(DOWN * 0.6)
        self.play(LaggedStart(*[FadeIn(r, shift=UP * 0.3) for r in rows], lag_ratio=0.5))

        self.beat()
        clear(self)
        kicker = mono("INFERENCE ENGINEERING AT NUTANIX · PART 1", 22, INDIGO, BOLD)
        title = txt("Inference is an\ninfrastructure problem", 80, INK, BOLD, line_spacing=0.85)
        VGroup(kicker, title).arrange(DOWN, aligned_edge=LEFT, buff=0.4).move_to(UP * 1.1)
        self.play(FadeIn(kicker, shift=UP * 0.2), Write(title), run_time=2)
        quote = pull_quote("Choosing a model is choosing\nthe physical shape of the service.", 38)
        quote.next_to(title, DOWN, buff=0.9).align_to(title, LEFT).shift(RIGHT * 0.4)
        self.play(FadeIn(quote, shift=UP * 0.2))


class S02Gpt2(NarratedSlide):
    narration = "02"

    def construct(self):
        self.beat()
        head = header("02 · Start small", "GPT-2 on a laptop")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        screen = panel(4.6, 2.9, stroke=MUTED, fill=PAPER)
        screen_label = txt("GPT-2", 56, INK, BOLD).move_to(screen)
        base = Polygon(
            screen.get_corner(DL) + DOWN * 0.1 + LEFT * 0.3,
            screen.get_corner(DR) + DOWN * 0.1 + RIGHT * 0.3,
            screen.get_corner(DR) + DOWN * 0.4 + RIGHT * 0.6,
            screen.get_corner(DL) + DOWN * 0.4 + LEFT * 0.6,
            stroke_color=MUTED, stroke_width=2, fill_color=SOFT, fill_opacity=1,
        )
        laptop = VGroup(screen, screen_label, base).move_to(LEFT * 3.2 + DOWN * 0.6)
        facts = VGroup(
            chip("124M PARAMETERS"),
            chip("≈500 MB OF FP32 WEIGHTS"),
            chip("FITS IN LAPTOP RAM", GREEN),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.35).move_to(RIGHT * 3.4 + DOWN * 0.6)
        self.play(FadeIn(laptop, shift=UP * 0.3))
        self.play(LaggedStart(*[FadeIn(f, shift=LEFT * 0.3) for f in facts], lag_ratio=0.3))

        self.beat()
        self.play(FadeOut(facts), laptop.animate.scale(0.55).move_to(LEFT * 5.2 + DOWN * 0.4))
        term = panel(9.0, 4.2, fill="#060b16").move_to(RIGHT * 1.6 + DOWN * 0.6)
        lines = VGroup(
            mono("$ python code/gpt2-inference.py", 22, MUTED),
            mono("prompt: The GPU is", 22, INK),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        lines.move_to(term).align_to(term, UP + LEFT).shift(RIGHT * 0.35 + DOWN * 0.35)
        echo = mono("The GPU is", 22, INK).next_to(lines, DOWN, aligned_edge=LEFT, buff=0.3)
        stream = mono(" a powerful piece of hardware, and", 22, INDIGO)
        stream.next_to(echo, RIGHT, buff=0.2).align_to(echo, DOWN)
        timing = mono("[TTFT … ms · decode … tokens/s]", 24, AMBER, BOLD)
        timing.next_to(echo, DOWN, aligned_edge=LEFT, buff=0.55)
        tag = chip("≈140 LINES OF PYTHON · NO SERVING FRAMEWORK", MUTED, 16).next_to(term, UP, buff=0.2).align_to(term, LEFT)
        self.play(FadeIn(term), FadeIn(tag))
        self.play(AddTextLetterByLetter(lines[0], time_per_char=0.02))
        self.play(AddTextLetterByLetter(lines[1], time_per_char=0.03))
        self.play(FadeIn(echo, run_time=0.2))
        self.play(AddTextLetterByLetter(stream, time_per_char=0.06))
        self.play(FadeIn(timing, shift=UP * 0.1))
        self.play(Create(SurroundingRectangle(timing, color=AMBER, buff=0.12, corner_radius=0.06)))

        self.beat()
        clear(self, head)
        col_a = mono("IN THE SCRIPT", 18, MUTED, BOLD)
        col_b = mono("AT PRODUCTION SCALE", 18, MUTED, BOLD)
        mapping = [
            ("download()", "Model import: hundreds of GB to ≈1 TB"),
            ("Tokenizer.encode", "Request ingress, locked to the weights"),
            ("first forward(ids)", "Prefill: compute-bound, sets TTFT"),
            ("generate() loop", "Decode: bandwidth-bound, sets tokens/s"),
            ("print(..., flush=True)", "Streaming through the NAI Agent Gateway"),
        ]
        left_x, arrow_x, right_x = -6.4, (-1.75, -0.75), -0.5
        rows = VGroup(*[
            VGroup(mono(left, 20, INDIGO, BOLD), txt(right, 24, INK)) for left, right in mapping
        ])
        for i, row in enumerate(rows):
            y = 1.1 - i * 0.85
            row[0].move_to([left_x + row[0].width / 2, y, 0])
            row[1].move_to([right_x + row[1].width / 2, y, 0])
        arrows = VGroup(*[
            Arrow([arrow_x[0], r.get_y(), 0], [arrow_x[1], r.get_y(), 0], buff=0, color=LINE,
                  stroke_width=3, max_tip_length_to_length_ratio=0.3)
            for r in rows
        ])
        col_a.move_to([left_x + col_a.width / 2, 1.85, 0])
        col_b.move_to([right_x + col_b.width / 2, 1.85, 0])
        self.play(FadeIn(col_a), FadeIn(col_b))
        self.play(LaggedStart(*[
            AnimationGroup(FadeIn(r[0], shift=RIGHT * 0.2), GrowArrow(a), FadeIn(r[1], shift=RIGHT * 0.2))
            for r, a in zip(rows, arrows)
        ], lag_ratio=0.4, run_time=4))

        self.beat()
        clear(self, head)
        panels = VGroup(panel(6.3, 4.4), panel(6.3, 4.4)).arrange(RIGHT, buff=0.4).move_to(DOWN * 0.75)
        titles = VGroup(
            txt("No KV cache (the demo script)", 26, AMBER, BOLD),
            txt("With a KV cache (vLLM)", 26, INDIGO, BOLD),
        )
        for t, p in zip(titles, panels):
            t.move_to(p.get_top() + DOWN * 0.45)
        rows_tokens = []
        for p in panels:
            row = VGroup(*[token() for _ in range(4)]).arrange(RIGHT, buff=0.08)
            row.move_to(p.get_left() + RIGHT * 0.4 + UP * 0.55, aligned_edge=LEFT)
            rows_tokens.append(row)
        work_labels = VGroup(
            mono("compute per step", 16, MUTED), mono("compute per step", 16, MUTED)
        )
        bars = []
        for lbl, p, color in zip(work_labels, panels, [AMBER, INDIGO]):
            lbl.move_to(p.get_left() + RIGHT * 0.4 + DOWN * 0.55, aligned_edge=LEFT)
            bar = Rectangle(width=0.5 * 4, height=0.35, stroke_width=0, fill_color=color, fill_opacity=0.85)
            bar.next_to(lbl, DOWN, buff=0.18, aligned_edge=LEFT)
            bars.append(bar)
        bars[1].stretch_to_fit_width(0.5).align_to(work_labels[1], LEFT)
        notes = VGroup(
            mono("re-runs attention over every token", 16, AMBER),
            mono("reuses cached keys and values", 16, INDIGO),
        )
        for n, p in zip(notes, panels):
            n.move_to(p.get_bottom() + UP * 0.45)
        self.play(FadeIn(panels), FadeIn(titles))
        self.play(*[FadeIn(r) for r in rows_tokens], *[FadeIn(l) for l in work_labels],
                  *[GrowFromEdge(b, LEFT) for b in bars])
        self.play(*[r.animate.set_fill(INDIGO_SOFT, 1) for r in rows_tokens[1:]], FadeIn(notes))
        for step in range(4):
            new_tokens = []
            for row in rows_tokens:
                t = token().next_to(row[-1], RIGHT, buff=0.08)
                new_tokens.append(t)
                row.add(t)
            n = len(rows_tokens[0])
            self.play(*[FadeIn(t, scale=0.6) for t in new_tokens], run_time=0.3)
            self.play(
                *[sq.animate.set_fill(AMBER, 0.9) for sq in rows_tokens[0]],
                new_tokens[1].animate.set_fill(INDIGO, 0.9),
                bars[0].animate.stretch_to_fit_width(0.5 * n).align_to(work_labels[0], LEFT),
                run_time=0.45,
            )
            self.play(
                *[sq.animate.set_fill(BG, 1) for sq in rows_tokens[0]],
                new_tokens[1].animate.set_fill(INDIGO_SOFT, 1),
                run_time=0.3,
            )
        spend = chip("SAVES RECOMPUTATION · SPENDS GPU MEMORY", GREEN, 16).next_to(panels, DOWN, buff=0.25)
        self.play(FadeIn(spend, shift=UP * 0.1))

        self.beat()
        clear(self, head)
        gpt2 = card("GPT-2 · 124M parameters", width=5.4, height=3.0)
        gpt2_value = VGroup(mono("≈72 KB", 72, INDIGO, BOLD), txt("of KV cache per token", 24, MUTED)).arrange(DOWN, buff=0.15)
        gpt2_value.move_to(gpt2[0]).shift(DOWN * 0.25)
        gpt2[2].move_to(gpt2[0].get_top() + DOWN * 0.55)
        kimi = card("Kimi K2 · ≈1T parameters", width=5.4, height=3.0, accent=AMBER)
        kimi_value = VGroup(mono("≈70 KB", 72, AMBER, BOLD), txt("per token (compressed attention)", 22, MUTED)).arrange(DOWN, buff=0.15)
        kimi_value.move_to(kimi[0]).shift(DOWN * 0.25)
        kimi[2].move_to(kimi[0].get_top() + DOWN * 0.55)
        g_left = VGroup(gpt2, gpt2_value).move_to(LEFT * 3.3 + DOWN * 0.5)
        g_right = VGroup(kimi, kimi_value).move_to(RIGHT * 3.3 + DOWN * 0.5)
        math = mono("2 × 12 layers × 12 heads × 64 dims × 4 bytes", 16, MUTED).next_to(g_left, DOWN, buff=0.3)
        approx = txt("≈", 80, INK, BOLD).move_to(DOWN * 0.5)
        self.play(FadeIn(g_left, shift=UP * 0.2))
        self.play(Write(math))
        self.play(FadeIn(g_right, shift=UP * 0.2), FadeIn(approx))

        self.beat()
        self.play(FadeOut(g_right), FadeOut(approx), FadeOut(math), g_left.animate.scale(0.8).move_to(LEFT * 4.3 + DOWN * 0.6))
        label = mono("THE THREE MULTIPLIERS", 18, AMBER, BOLD).move_to(RIGHT * 2.9 + UP * 1.75)
        mults = VGroup(
            card("Context", "1K → 128K tokens", width=5.6, accent=AMBER),
            card("Concurrency", "1 session → thousands", width=5.6, accent=AMBER),
            card("Weights", "no longer fit on one device", width=5.6, accent=AMBER),
        ).arrange(DOWN, buff=0.3).move_to(RIGHT * 3.4 + DOWN * 0.8)
        label.next_to(mults, UP, buff=0.25).align_to(mults, LEFT)
        arrows = VGroup(*[
            Arrow(g_left.get_right(), m.get_left(), buff=0.2, color=AMBER, stroke_width=5)
            for m in mults
        ])
        self.play(FadeIn(label))
        self.play(LaggedStart(*[
            AnimationGroup(GrowArrow(a), FadeIn(m, shift=RIGHT * 0.3)) for a, m in zip(arrows, mults)
        ], lag_ratio=0.6, run_time=3))


class S03Phases(NarratedSlide):
    narration = "03"

    def construct(self):
        self.beat()
        head = header("03 · Two phases", "Two phases, two bottlenecks")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        panels = VGroup(panel(6.3, 4.6), panel(6.3, 4.6)).arrange(RIGHT, buff=0.4).move_to(DOWN * 0.8)
        titles = VGroup(
            VGroup(mono("PREFILL", 30, INDIGO, BOLD), txt("reads the whole prompt", 22, MUTED)).arrange(DOWN, buff=0.12),
            VGroup(mono("DECODE", 30, AMBER, BOLD), txt("writes the answer", 22, MUTED)).arrange(DOWN, buff=0.12),
        )
        for t, p in zip(titles, panels):
            t.move_to(p.get_top() + DOWN * 0.65)
        self.play(FadeIn(panels), LaggedStart(*[FadeIn(t, shift=DOWN * 0.2) for t in titles], lag_ratio=0.4))

        self.beat()
        prompt = VGroup(*[token(0.4) for _ in range(12)]).arrange(RIGHT, buff=0.07).move_to(panels[0]).shift(UP * 0.1)
        prompt_label = mono("prompt tokens, all at once", 16, MUTED).next_to(prompt, UP, buff=0.2)
        self.play(FadeIn(prompt), FadeIn(prompt_label))
        self.play(prompt.animate.set_fill(INDIGO, 0.9), run_time=0.6)
        self.play(Flash(prompt.get_center(), color=INDIGO, line_length=0.5, flash_radius=prompt.width / 2 + 0.2, num_lines=16))
        pre_chip = chip("COMPUTE-BOUND", INDIGO).move_to(panels[0]).shift(DOWN * 1.0)
        pre_out = txt("→ sets time to first token (TTFT)", 24, INK).next_to(pre_chip, DOWN, buff=0.25)
        self.play(FadeIn(pre_chip, shift=UP * 0.1), FadeIn(pre_out, shift=UP * 0.1))

        self.beat()
        weights = labeled_box("weights", 1.3, 0.6, color=MUTED, size=20)
        weights.move_to(panels[1].get_left() + RIGHT * 1.0).set_y(prompt.get_y())
        out_row = VGroup()
        anchor = weights.get_right() + RIGHT * 0.6
        dec_label = mono("one token per step, rereads the weights", 16, MUTED)
        dec_label.move_to([panels[1].get_x(), prompt_label.get_y(), 0])
        self.play(FadeIn(weights), FadeIn(dec_label))
        for i in range(7):
            t = token(0.4, color=AMBER, fill=AMBER, opacity=0.9)
            t.move_to(anchor + RIGHT * (0.2 + i * 0.47))
            dot = Dot(weights.get_right(), color=AMBER, radius=0.09)
            path = Line(weights.get_right(), t.get_center())
            self.play(
                Indicate(weights[0], color=AMBER, scale_factor=1.04),
                MoveAlongPath(dot, path),
                run_time=0.45,
            )
            self.remove(dot)
            self.play(FadeIn(t, scale=0.5), run_time=0.15)
            out_row.add(t)
        dec_chip = chip("MEMORY-BANDWIDTH-BOUND", AMBER).move_to(panels[1]).shift(DOWN * 1.0)
        dec_out = txt("→ sets tokens per second", 24, INK).next_to(dec_chip, DOWN, buff=0.25)
        self.play(FadeIn(dec_chip, shift=UP * 0.1), FadeIn(dec_out, shift=UP * 0.1))

        self.beat()
        clear(self, head)
        example = txt("Example request: ≈2,000-token prompt, ≈500-token answer", 26, MUTED).move_to(UP * 1.9)
        stages = [("ingress", 40, MUTED), ("queue", 110, LINE), ("prefill", 300, INDIGO), ("decode", 10000, AMBER), ("egress", 50, MUTED)]
        total_ms = sum(ms for _, ms, _ in stages)
        width = 12.6
        x = -width / 2
        segs = VGroup()
        for _, ms, color in stages:
            w = max(width * ms / total_ms, 0.03)
            r = Rectangle(width=w, height=0.8, stroke_width=0, fill_color=color, fill_opacity=0.95)
            r.move_to([x + w / 2, -0.1, 0])
            segs.add(r)
            x += w
        self.play(FadeIn(example))
        self.play(LaggedStart(*[GrowFromEdge(s, LEFT) for s in segs], lag_ratio=0.9, run_time=3.5))
        first = VGroup(*segs[:3])
        first_brace = Brace(first, UP, buff=0.1, color=INDIGO)
        first_label = mono("first token ≈500 ms", 20, INDIGO, BOLD).next_to(first_brace, UP, buff=0.1).align_to(first, LEFT)
        dec_brace = Brace(segs[3], DOWN, buff=0.12, color=AMBER)
        dec_label = txt("decode ≈10,000 ms · ≈97% of model time", 28, AMBER, BOLD).next_to(dec_brace, DOWN, buff=0.15)
        total = mono("total ≈10.5 s", 22, INK, BOLD).next_to(segs, UP, buff=0.3).align_to(segs, RIGHT)
        self.play(GrowFromCenter(first_brace), FadeIn(first_label))
        self.play(GrowFromCenter(dec_brace), FadeIn(dec_label), FadeIn(total))
        legend = mono("ingress ≈40 ms · queue ≈110 ms · prefill ≈300 ms · decode ≈10,000 ms · egress ≈50 ms", 16, MUTED)
        legend.to_edge(DOWN, buff=0.7)
        self.play(FadeIn(legend))

        self.beat()
        clear(self, head)
        budgets = VGroup(
            card("First-token budget", "queue + prefill → TTFT", width=5.2, accent=INDIGO),
            card("Completion budget", "decode → when the answer ends", width=5.2, accent=AMBER),
        ).arrange(RIGHT, buff=0.5).move_to(UP * 1.25)
        heights = [0.25, 0.8, 1.6, 2.1, 2.2, 1.9, 1.45, 1.05, 0.75, 0.55, 0.4, 0.3, 0.22, 0.17, 0.13, 0.1, 0.08]
        bars = VGroup(*[
            Rectangle(width=0.5, height=h, stroke_color=BG, stroke_width=2, fill_color=INDIGO, fill_opacity=0.8)
            for h in heights
        ]).arrange(RIGHT, buff=0.04, aligned_edge=DOWN)
        bars.move_to(DOWN * 1.7, aligned_edge=DOWN).shift(DOWN * 0.9)
        axis = Line(bars.get_corner(DL) + LEFT * 0.2, bars.get_corner(DR) + RIGHT * 0.2, color=MUTED, stroke_width=2)
        axis_label = mono("request latency (illustrative)", 16, MUTED).next_to(axis, DOWN, buff=0.12)
        self.play(LaggedStart(*[FadeIn(b, shift=UP * 0.2) for b in budgets], lag_ratio=0.4))
        self.play(Create(axis), FadeIn(axis_label), LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.06))
        p50 = DashedLine(bars[4].get_bottom(), bars[4].get_bottom() + UP * 2.5, color=INK, stroke_width=3)
        p99 = DashedLine(bars[14].get_bottom(), bars[14].get_bottom() + UP * 2.5, color=AMBER, stroke_width=3)
        p50_label = mono("p50", 20, INK, BOLD).next_to(p50, UP, buff=0.08)
        p99_label = mono("p99", 20, AMBER, BOLD).next_to(p99, UP, buff=0.08)
        self.play(Create(p50), FadeIn(p50_label))
        self.play(Create(p99), FadeIn(p99_label))

        self.beat()
        self.play(FadeOut(budgets), *[b.animate.set_fill(AMBER, 0.95) for b in bars[12:]])
        quote = pull_quote("The average tells you the machine is healthy.\nThe tail tells you whether users agree.", 34)
        quote.move_to(UP * 1.2)
        self.play(FadeIn(quote, shift=UP * 0.2))


class S04GpuNumbers(NarratedSlide):
    narration = "04"

    def construct(self):
        self.beat()
        head = header("04 · The GPU", "The two numbers that describe a GPU")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        tank = Rectangle(width=2.3, height=3.2, stroke_color=MUTED, stroke_width=3).move_to(LEFT * 5.4 + DOWN * 0.7)
        tank_title = mono("GPU MEMORY", 16, MUTED).next_to(tank, UP, buff=0.15)
        tank_label = VGroup(mono("CAPACITY", 20, INDIGO, BOLD), txt("how many bytes it holds", 20, MUTED)).arrange(DOWN, buff=0.08)
        tank_label.next_to(tank, DOWN, buff=0.2)
        pipe_y = tank.get_bottom()[1] + 0.45
        die = labeled_box("cores", 1.2, 1.2, color=MUTED, size=22).move_to([-0.2, pipe_y + 0.2, 0])
        pipe = Rectangle(
            width=die.get_left()[0] - tank.get_right()[0], height=0.4,
            stroke_color=MUTED, stroke_width=3, fill_color=SOFT, fill_opacity=1,
        ).move_to([(die.get_left()[0] + tank.get_right()[0]) / 2, pipe_y, 0])
        pipe_label = VGroup(mono("BANDWIDTH", 20, AMBER, BOLD), txt("how fast it reads them", 18, MUTED)).arrange(DOWN, buff=0.08)
        pipe_label.next_to(pipe, UP, buff=0.3)
        col_x, col_w = 3.9, 6.0
        self.play(Create(tank), FadeIn(tank_title), FadeIn(tank_label))
        self.play(FadeIn(pipe), FadeIn(die), FadeIn(pipe_label))

        def pulse(color, n=5, run_time=1.6, size=0.18):
            dots = [Square(size, stroke_width=0, fill_color=color, fill_opacity=1).move_to(pipe.get_left()) for _ in range(n)]
            path = Line(pipe.get_left(), pipe.get_right())
            self.play(LaggedStart(*[MoveAlongPath(d, path) for d in dots], lag_ratio=0.25, run_time=run_time))
            self.remove(*dots)

        self.beat()
        fill = Rectangle(width=2.3, height=2.6, stroke_width=0, fill_color=INDIGO, fill_opacity=0.45)
        fill.move_to(tank.get_bottom() + UP * 1.35)
        fill_label = txt("weights", 26, INK, BOLD).move_to(fill)
        fits = chip("✓ FITS", GREEN).next_to(tank, RIGHT, buff=0.25).align_to(tank, UP)
        self.play(GrowFromEdge(fill, DOWN), FadeIn(fill_label))
        self.play(FadeIn(fits, shift=LEFT * 0.2))
        speed = mono("decode speed", 18, AMBER).next_to(die, DOWN, buff=0.2)
        self.play(FadeIn(speed))
        pulse(AMBER)

        self.beat()
        f1 = txt("decode ceiling per stream (tokens/s)", 24, INK, BOLD)
        f2 = VGroup(txt("≤", 32, INK, BOLD), txt("memory bandwidth", 28, AMBER, BOLD)).arrange(RIGHT, buff=0.25)
        f3 = VGroup(txt("÷", 32, INK, BOLD), txt("active-weight bytes per token", 28, INDIGO, BOLD)).arrange(RIGHT, buff=0.25)
        formula = VGroup(f1, f2, f3).arrange(DOWN, aligned_edge=LEFT, buff=0.28)
        if formula.width > col_w - 0.6:
            formula.scale_to_fit_width(col_w - 0.6)
        formula_box = panel(col_w, formula.height + 0.5, stroke=INDIGO, fill=PAPER).move_to([col_x, 1.15, 0])
        formula.move_to(formula_box)
        self.play(FadeIn(formula_box), Write(f1))
        self.play(FadeIn(f2, shift=RIGHT * 0.2))
        self.play(FadeIn(f3, shift=RIGHT * 0.2))

        self.beat()
        example = card("Llama 3.1 405B · dense · FP8 · 8×H100", "≈26.8 TB/s ÷ ≈405 GB of weights per token", width=col_w)
        example.next_to(formula_box, DOWN, buff=0.35).align_to(formula_box, LEFT)
        readout_anchor = example.get_corner(DL) + DOWN * 0.7

        def readout(tracker, color):
            value = counter(tracker, lambda v: f"≈{v:.0f}", 60, color, anchor=readout_anchor, align=LEFT)
            unit = txt("tokens/s, at best", 26, MUTED)
            unit.add_updater(lambda m: m.next_to(value, RIGHT, buff=0.25).align_to(value, DOWN))
            return value, unit

        tps = ValueTracker(0)
        value, unit = readout(tps, INDIGO)
        self.play(FadeIn(example, shift=UP * 0.2))
        self.add(value, unit)
        self.play(Indicate(fill, color=INDIGO, scale_factor=1.03), run_time=0.6)
        self.play(tps.animate.set_value(66), run_time=2.2)
        pulse(INDIGO, n=3, run_time=1.8, size=0.3)

        self.beat()
        experts = VGroup(*[
            Square(0.3, stroke_color=BG, stroke_width=2, fill_color=INDIGO_SOFT, fill_opacity=1) for _ in range(24)
        ]).arrange_in_grid(rows=6, cols=4, buff=0.1).move_to(fill)
        moe = card("gpt-oss-120b · MoE · MXFP4 · 1× RTX PRO 6000", "≈1.6 TB/s ÷ ≈3 GB of active weights per token", width=col_w, accent=AMBER)
        moe.move_to(example)
        router = chip("ROUTER", AMBER, 16).next_to(tank, RIGHT, buff=0.25).align_to(tank, UP)
        self.play(
            FadeOut(fill_label), FadeOut(fits), ReplacementTransform(fill, experts),
            ReplacementTransform(example, moe), FadeIn(router), FadeOut(value), FadeOut(unit),
            Transform(tank_title, mono("GPU MEMORY · EXPERTS", 16, MUTED).move_to(tank_title)),
        )
        active = [experts[5], experts[18]]
        self.play(*[e.animate.set_fill(AMBER, 1) for e in active], Indicate(router))
        tps = ValueTracker(0)
        value, unit = readout(tps, AMBER)
        self.add(value, unit)
        self.play(tps.animate.set_value(530), run_time=2.2)
        pulse(AMBER, n=8, run_time=1.2, size=0.14)

        self.beat()
        self.play(*[e.animate.set_fill(INDIGO, 0.85) for e in experts], FadeOut(router))
        resident = mono("EVERY EXPERT STAYS RESIDENT", 16, INDIGO, BOLD).move_to(tank_title).align_to(tank, LEFT)
        shift = VGroup(
            txt("pressure moves from", 26, INK),
            txt("bandwidth", 26, AMBER, BOLD),
            txt("→", 26, INK),
            txt("capacity", 26, INDIGO, BOLD),
        ).arrange(RIGHT, buff=0.2)
        if shift.width > col_w:
            shift.scale_to_fit_width(col_w)
        shift.next_to(moe, DOWN, buff=0.45).align_to(moe, LEFT)
        self.play(ReplacementTransform(tank_title, resident), FadeOut(value), FadeOut(unit))
        self.play(FadeIn(shift, shift=UP * 0.2))
        self.play(Indicate(tank, color=INDIGO, scale_factor=1.03))


class S05Math(NarratedSlide):
    narration = "05"

    def construct(self):
        self.beat()
        head = header("05 · Do the math", "Model selection is capacity planning")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        lines = VGroup(
            mono("weight memory = parameters × bytes per parameter", 22, INK),
            mono("KV per token  ≈ 2 × layers × kv_heads × head_dim × bytes", 22, INK),
            mono("GPU count     = ceil[(weights + live KV) ÷ usable memory per GPU]", 22, INK),
            mono("node count    = ceil(GPUs ÷ 8 per node)", 22, INK),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.35)
        code = panel(lines.width + 0.8, lines.height + 0.7, fill="#060b16").move_to(UP * 0.2)
        lines.move_to(code)
        precision = mono("BF16 = 2 bytes · FP8 = 1 · INT4 ≈ 0.5", 18, MUTED).next_to(code, DOWN, buff=0.25).align_to(code, LEFT)
        self.play(FadeIn(code))
        self.play(LaggedStart(*[AddTextLetterByLetter(l, time_per_char=0.015) for l in lines], lag_ratio=0.9))
        self.play(FadeIn(precision))

        self.beat()
        highlights = VGroup(*[
            SurroundingRectangle(lines[i], color=AMBER, buff=0.1, corner_radius=0.05) for i in (0, 2)
        ])
        self.play(Create(highlights[0]))
        self.play(Create(highlights[1]))
        worked = VGroup(
            mono("Llama 3.1 405B:  (405 GB + ≈64 GB KV) ÷ 72 GB usable = 6.5", 22, AMBER),
            mono("→ 7 GPUs by capacity → 8 in practice (one full node)", 22, AMBER),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.2).next_to(precision, DOWN, buff=0.35).align_to(code, LEFT)
        self.play(FadeIn(worked[0], shift=UP * 0.1))
        self.play(FadeIn(worked[1], shift=UP * 0.1))

        self.beat()
        clear(self, head)
        nodes = VGroup(Server("NODE 1 · 8×H100"), Server("NODE 2 · 8×H100")).arrange(DOWN, buff=0.9, aligned_edge=LEFT)
        nodes.move_to([3.6, -0.55, 0])
        slots = [*nodes[0].slots, *nodes[1].slots]
        cols = [-6.5, -3.35, -1.5, -0.5]
        head_row = VGroup(*[
            mono(t, 15, MUTED, BOLD).move_to([x, 1.6, 0], aligned_edge=LEFT)
            for t, x in zip(["MODEL", "FP8 WEIGHTS", "H100s", "NODES"], cols)
        ])
        models = [
            ("gpt-oss-120b", "≈117 GB", 2, 1),
            ("Qwen3-235B-A22B", "≈235 GB", 4, 1),
            ("Llama 3.1 405B", "≈405 GB", 8, 1),
            ("DeepSeek V3.1", "≈685 GB", 16, 2),
            ("Kimi K2", "≈1 TB", 16, 2),
        ]
        assumptions = mono("FP8 weights · 72 GB usable per 80 GB H100 · one 128K-token session of KV cache", 15, MUTED)
        assumptions.to_edge(DOWN, buff=0.45)
        self.play(FadeIn(nodes), FadeIn(head_row), FadeIn(assumptions))
        table = VGroup()
        marker = None
        for i, (name, weights, gpus, node_count) in enumerate(models):
            y = 1.0 - i * 0.62
            row = VGroup(
                txt(name, 22, INK, BOLD).move_to([cols[0], y, 0], aligned_edge=LEFT),
                mono(weights, 20, TEXT).move_to([cols[1], y, 0], aligned_edge=LEFT),
                mono(str(gpus), 20, AMBER if node_count > 1 else INDIGO, BOLD).move_to([cols[2], y, 0], aligned_edge=LEFT),
                mono(str(node_count), 20, AMBER if node_count > 1 else INDIGO, BOLD).move_to([cols[3], y, 0], aligned_edge=LEFT),
            )
            table.add(row)
            new_marker = SurroundingRectangle(row, color=LINE, buff=0.12, corner_radius=0.05)
            color = AMBER if node_count > 1 else INDIGO
            self.play(
                FadeIn(row, shift=RIGHT * 0.2),
                ReplacementTransform(marker, new_marker) if marker else Create(new_marker),
                *[s.animate.set_fill(color if j < gpus else BG, 0.85 if j < gpus else 1) for j, s in enumerate(slots)],
                run_time=0.9,
            )
            marker = new_marker
            self.wait(0.3)

        self.beat()
        link_top = nodes[0].outline.get_bottom()
        link = Line(link_top, [link_top[0], nodes[1].outline.get_top()[1], 0], color=AMBER, stroke_width=8)
        link_label = mono("leaves NVLink", 18, AMBER, BOLD).next_to(link, RIGHT, buff=0.2)
        self.play(FadeOut(table), FadeOut(marker), FadeOut(head_row), Create(link), FadeIn(link_label))
        self.play(ShowPassingFlash(link.copy().set_color(RED).set_stroke(width=14), time_width=0.5), run_time=1.0)
        costs = VGroup(
            card("Collectives leave NVLink", "tensor and expert traffic crosses the network", width=5.6, accent=AMBER),
            card("Rack-level power", "≈10.2 kW max per DGX H100", width=5.6, accent=AMBER),
            card("Bigger blast radius", "a failure or drain moves ≈1 TB", width=5.6, accent=AMBER),
        ).arrange(DOWN, buff=0.25).move_to([-3.8, -0.45, 0])
        self.play(LaggedStart(*[FadeIn(c, shift=RIGHT * 0.3) for c in costs], lag_ratio=0.4))
        self.play(ShowPassingFlash(link.copy().set_color(RED).set_stroke(width=14), time_width=0.5), run_time=1.0)

        self.beat()
        b300 = card("Kimi K2 on B300", "≈259 GB usable per GPU\nceil(1,009 ÷ 259) = 4 GPUs\none NVLink domain", width=5.6, accent=GREEN)
        b300.move_to([-3.8, -0.45, 0])
        new_label = mono("NODE 1 · 8×B300", 18, MUTED).move_to(nodes[0].label, aligned_edge=LEFT)
        self.play(
            FadeOut(costs), FadeOut(link), FadeOut(link_label), FadeOut(nodes[1]), FadeOut(assumptions),
            Transform(nodes[0].label, new_label),
            *[s.animate.set_fill(BG, 1) for s in nodes[0].slots],
        )
        self.play(nodes[0].animate.move_to([3.6, 0.2, 0]))
        self.play(
            FadeIn(b300, shift=RIGHT * 0.3),
            LaggedStart(*[s.animate.set_fill(GREEN, 0.85) for s in nodes[0].slots[:4]], lag_ratio=0.2),
        )

        self.beat()
        clear(self, head)
        quote = pull_quote("Choosing a GPU SKU really means choosing\nhow many failure domains a replica spans.", 40)
        quote.move_to(DOWN * 0.3)
        self.play(FadeIn(quote, shift=UP * 0.2))


class S06KvCache(NarratedSlide):
    narration = "06"

    def construct(self):
        self.beat()
        head = header("06 · KV cache", "The concurrency multiplier")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        bar = MemoryBar(640, width=12.6, height=1.0).move_to(DOWN * 0.2)
        title = mono("ONE REPLICA · 8×H100 · 640 GB NOMINAL", 18, MUTED, BOLD).next_to(bar, UP, buff=0.9).align_to(bar, LEFT)
        usable = DashedLine(bar.x_at(576) + UP * 0.75, bar.x_at(576) + DOWN * 0.75, color=INK, stroke_width=3)
        usable.set_y(bar.get_y())
        usable_label = mono("90% usable · 576 GB", 16, INK).next_to(usable, UP, buff=0.1).align_to(usable, RIGHT)
        weights = bar.block(0, 405, INDIGO)
        weights_label = txt("weights ≈405 GB", 28, INK, BOLD).move_to(weights)
        fits = chip("✓ THE MODEL FITS", GREEN).next_to(bar, DOWN, buff=0.4).align_to(bar, LEFT)
        self.play(FadeIn(title), Create(bar))
        self.play(Create(usable), FadeIn(usable_label))
        self.play(GrowFromEdge(weights, LEFT), FadeIn(weights_label), run_time=1.5)
        self.play(FadeIn(fits, shift=UP * 0.1))

        self.beat()
        per_session = mono("≈500 KB/token × 128K tokens ≈ 64 GB per session", 20, AMBER)
        per_session.next_to(fits, RIGHT, buff=0.5)
        self.play(FadeIn(per_session))
        sessions = []
        for i in range(2):
            s = bar.block(405 + i * 64, 64, AMBER)
            self.play(FadeIn(s, shift=DOWN * 0.8), run_time=0.7)
            sessions.append(s)
        third = bar.block(405 + 2 * 64, 64, AMBER)
        self.play(FadeIn(third, shift=DOWN * 0.8), run_time=0.7)
        self.play(third.animate.set_fill(RED, 0.9), Wiggle(third), run_time=0.8)
        self.play(third.animate.shift(UP * 1.6).set_opacity(0), run_time=0.7)
        room = txt("room for just 2 full-length sessions", 26, AMBER, BOLD).next_to(fits, DOWN, buff=0.35).align_to(bar, LEFT)
        verdict = txt("The model fits. The workload doesn't.", 34, INK, BOLD).next_to(room, DOWN, buff=0.35).align_to(bar, LEFT)
        self.play(FadeIn(room, shift=UP * 0.1))
        self.play(FadeIn(verdict, shift=UP * 0.1))

        self.beat()
        clear(self, head)
        label = mono("KV CACHE FOR 8 CONCURRENT 128K-TOKEN SESSIONS", 18, MUTED, BOLD).move_to([-6.4, 1.6, 0], aligned_edge=LEFT)
        scale = 6.6 / 512
        bars_x = -1.6
        rows = VGroup()
        for i, (name, sub, per_gb, color, total) in enumerate([
            ("Llama 3.1 405B", "≈500 KB per token", 64, AMBER, "≈512 GB"),
            ("MLA models", "DeepSeek V3.1, Kimi K2 · ≈70 KB per token", 9, INDIGO, "≈72 GB"),
        ]):
            y = 0.6 - i * 1.5
            names = VGroup(txt(name, 26, INK, BOLD), txt(sub, 17, MUTED)).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
            if names.width > 4.4:
                names.scale_to_fit_width(4.4)
            names.move_to([-6.4, y, 0], aligned_edge=LEFT)
            blocks = VGroup(*[
                Rectangle(width=per_gb * scale, height=0.7, stroke_color=BG, stroke_width=2, fill_color=color, fill_opacity=0.9)
                for _ in range(8)
            ]).arrange(RIGHT, buff=0).move_to([bars_x, y, 0], aligned_edge=LEFT)
            value = mono(total, 24, color, BOLD).next_to(blocks, RIGHT, buff=0.25)
            rows.add(VGroup(names, blocks, value))
        self.play(FadeIn(label))
        for names, blocks, value in rows:
            self.play(FadeIn(names), LaggedStart(*[GrowFromEdge(b, LEFT) for b in blocks], lag_ratio=0.5, run_time=1.6))
            self.play(FadeIn(value))
        more = mono("more than the ≈405 GB of weights", 16, AMBER).next_to(rows[0][1], UP, buff=0.12).align_to(rows[0][1], RIGHT)
        takeaway = pull_quote("Attention design is an infrastructure input.", 32).move_to([0, -2.6, 0])
        self.play(FadeIn(more))
        self.play(FadeIn(takeaway, shift=UP * 0.2))

        self.beat()
        self.play(FadeOut(takeaway), FadeOut(more), VGroup(label, rows).animate.scale(0.8).move_to(UP * 0.95))
        previews = VGroup(
            card("KV-cache-aware routing", "the llm-d scheduler sends repeated prompts\nto the replica that already holds them", width=6.2),
            card("KV-cache offload to host RAM", "evictable blocks spill to host memory\ninstead of being discarded", width=6.2),
        ).arrange(RIGHT, buff=0.4).move_to(DOWN * 2.35)
        badges = VGroup(*[
            chip("TECH PREVIEW · NAI 2.8", AMBER, 14).next_to(c, UP, buff=0.12).align_to(c, RIGHT)
            for c in previews
        ])
        self.play(LaggedStart(*[FadeIn(VGroup(c, b), shift=UP * 0.3) for c, b in zip(previews, badges)], lag_ratio=0.4))


class S07Nutanix(NarratedSlide):
    narration = "07"

    def construct(self):
        self.beat()
        head = header("07 · Nutanix", "Where Nutanix fits")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        server = labeled_box("model server (vLLM)", 4.2, 1.0, color=INDIGO, size=28).move_to(DOWN * 0.7)
        self.play(FadeIn(server, scale=0.9))
        around = ["GPU servers", "bare-metal lifecycle", "clusters", "GPU VMs", "tenancy", "Kubernetes", "endpoints", "model storage"]
        ring = VGroup()
        for i, name in enumerate(around):
            angle = PI / 2 - i * TAU / len(around)
            c = chip(name.upper(), MUTED, 15).move_to(server.get_center() + np.array([4.6 * np.cos(angle), 1.9 * np.sin(angle), 0]))
            ring.add(c)
        self.play(LaggedStart(*[FadeIn(c, scale=0.8) for c in ring], lag_ratio=0.15, run_time=2.4))

        self.beat()
        self.play(FadeOut(ring), FadeOut(server))
        layers = [
            ("GPU servers", "", MUTED),
            ("Foundation Central + NICo", "discover, health-check, image", INDIGO),
            ("NIM (Nutanix Infra Manager)", "claim nodes, build clusters", INDIGO),
            ("AHV + COCI", "GPU VMs on compute-only nodes", INDIGO),
            ("Prism Central projects", "tenancy for GPUs and networks", INDIGO),
            ("NKP", "Kubernetes workload clusters", INDIGO),
            ("NAI", "governed model endpoints", AMBER),
        ]
        stack_w, stack_x = 9.0, -1.75
        stack = VGroup()
        for i, (name, desc, color) in enumerate(layers):
            box = panel(stack_w, 0.6, stroke=color, fill=PAPER)
            label = txt(name, 20, INK, BOLD).move_to(box).align_to(box, LEFT).shift(RIGHT * 0.25)
            parts = [box, label]
            if desc:
                parts.append(mono(desc, 13, MUTED).move_to(box).align_to(box, RIGHT).shift(LEFT * 0.25))
            stack.add(VGroup(*parts).move_to([stack_x, -3.3 + i * 0.7, 0]))
        banner = VGroup(
            mono("PROJECT ASTRA", 20, AMBER, BOLD),
            txt("user intent → ready-to-use GPU or inference service", 22, INK),
        ).arrange(RIGHT, buff=0.4)
        banner_box = panel(stack_w, 0.7, stroke=AMBER, fill=AMBER_SOFT).move_to([stack_x, stack[-1].get_y() + 0.85, 0])
        if banner.width > stack_w - 0.4:
            banner.scale_to_fit_width(stack_w - 0.4)
        banner.move_to(banner_box)

        def side_note(s, layer):
            return VGroup(
                Arrow(RIGHT * 0.6, ORIGIN, buff=0, color=AMBER, stroke_width=3, max_tip_length_to_length_ratio=0.4),
                mono(s, 14, AMBER, BOLD),
            ).arrange(RIGHT, buff=0.12).next_to(layer, RIGHT, buff=0.12)

        notes = {1: side_note("NVIDIA Infra Controller", stack[1]), 2: side_note("not NVIDIA NIM", stack[2])}
        self.play(FadeIn(banner_box), FadeIn(banner))
        for i, layer in enumerate(stack):
            self.play(FadeIn(layer, shift=UP * 0.25), run_time=0.55)
            if i in notes:
                self.play(FadeIn(notes[i], shift=LEFT * 0.2), run_time=0.4)
        self.play(Indicate(stack[-1], color=AMBER, scale_factor=1.03))

        self.beat()
        clear(self, head)

        def store(title, sub, x, color):
            box = panel(3.2, 1.4, stroke=color, fill=PAPER)
            content = VGroup(txt(title, 26, INK, BOLD), mono(sub, 15, MUTED)).arrange(DOWN, buff=0.15).move_to(box)
            return VGroup(box, content).move_to([x, 1.1, 0])

        objects = store("Nutanix Objects", "durable S3 source", -5.2, MUTED)
        files = store("Nutanix Files", "/mnt/models · RWX", -0.5, INDIGO)
        gpu = store("GPU memory", "every new replica", 5.2, AMBER)
        a1 = Arrow(objects.get_right(), files.get_left(), buff=0.1, color=MUTED)
        a2 = Arrow(files.get_right(), gpu.get_left(), buff=0.1, color=AMBER)
        once = mono("import once", 14, MUTED).next_to(a1, UP, buff=0.08)
        every = mono("read on every start", 14, AMBER).next_to(a2, UP, buff=0.08)
        self.play(LaggedStart(FadeIn(objects), GrowArrow(a1), FadeIn(once), FadeIn(files), GrowArrow(a2), FadeIn(every), FadeIn(gpu), lag_ratio=0.3))
        for arrow, color, n in [(a1, MUTED, 3), (a2, AMBER, 6)]:
            dots = [Square(0.14, stroke_width=0, fill_color=color, fill_opacity=1).move_to(arrow.get_start()) for _ in range(n)]
            self.play(LaggedStart(*[MoveAlongPath(d, Line(arrow.get_start(), arrow.get_end())) for d in dots], lag_ratio=0.2, run_time=1.2))
            self.remove(*dots)

        scale = 7.4 / 140
        bar_x = -2.3
        rows = [
            ("floor", "≈400 GB ÷ ≈10 GB/s", 40, INDIGO),
            ("typical path", "≈400 GB ÷ ≈5 GB/s", 80, AMBER),
            ("observed", "≈40 GB, 4-bit 70B on L40S", 140, RED),
        ]
        for i, (name, math, seconds, color) in enumerate(rows):
            y = -0.75 - i * 0.95
            label = VGroup(txt(name, 22, INK, BOLD), mono(math, 14, MUTED)).arrange(DOWN, aligned_edge=LEFT, buff=0.06)
            label.move_to([-6.5, y, 0], aligned_edge=LEFT)
            t = ValueTracker(0)
            bar = always_redraw(lambda t=t, y=y, color=color: Rectangle(
                width=max(t.get_value() * scale, 0.01), height=0.5, stroke_width=0, fill_color=color, fill_opacity=0.9,
            ).move_to([bar_x, y, 0], aligned_edge=LEFT))
            clock = always_redraw(lambda t=t, y=y, color=color: mono(
                f"≈{t.get_value():.0f} s", 22, color, BOLD,
            ).move_to([bar_x + max(t.get_value() * scale, 0.01) + 0.2, y, 0], aligned_edge=LEFT))
            self.play(FadeIn(label))
            self.add(bar, clock)
            self.play(t.animate.set_value(seconds), run_time=0.6 + seconds / 50, rate_func=linear)
            if i == 0:
                setup = mono("+ deserialization, KV allocation, collective setup, health checks", 14, MUTED)
                setup.next_to(label, DOWN, buff=0.05).align_to(label, LEFT).shift(RIGHT * (bar_x + 6.5))
                self.play(FadeIn(setup))
        dominated = mono("deserialization, not storage, dominated", 15, RED).move_to([bar_x, -3.55, 0], aligned_edge=LEFT)
        self.play(FadeIn(dominated))

        self.beat()
        clear(self, head)
        quote = pull_quote("Measure the load.\nDon't derive it from a spec sheet.", 48)
        quote.move_to(DOWN * 0.3)
        self.play(FadeIn(quote, shift=UP * 0.2))


class S08GpuFarm(NarratedSlide):
    narration = "08"

    def construct(self):
        self.beat()
        head = header("08 · Field notes", "Our own GPU Farm")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        steps = VGroup(
            labeled_box("Nutanix developer", 2.7, 1.0, MUTED, 20),
            labeled_box("Internal portal", 2.7, 1.0, MUTED, 20),
            labeled_box("NAI Agent Gateway", 2.7, 1.0, INDIGO, 20),
            labeled_box("GPU Farm", 2.7, 1.0, AMBER, 20),
        ).arrange(RIGHT, buff=0.85).move_to(UP * 0.8)
        arrows = VGroup(*[Arrow(a.get_right(), b.get_left(), buff=0.08, color=LINE) for a, b in zip(steps, steps[1:])])
        key = mono("API key", 14, MUTED).next_to(arrows[0], UP, buff=0.08)
        duties = mono("auth · quotas · rate limits · routing · token accounting", 16, INDIGO)
        duties.next_to(steps[2], DOWN, buff=0.3)
        workload_label = mono("TOKEN-AS-A-SERVICE WORKLOADS", 16, MUTED, BOLD)
        workloads = VGroup(
            chip("CODING AGENTS", AMBER),
            chip("CHAT", MUTED),
            chip("RAG", MUTED),
            chip("EMBEDDINGS", MUTED),
            chip("RERANKING", MUTED),
        ).arrange(RIGHT, buff=0.3)
        VGroup(workload_label, workloads).arrange(DOWN, buff=0.25).move_to(DOWN * 2.2)
        self.play(LaggedStart(*[
            AnimationGroup(FadeIn(s, shift=RIGHT * 0.2), *([GrowArrow(arrows[i - 1])] if i else []))
            for i, s in enumerate(steps)
        ], lag_ratio=0.5), FadeIn(key))
        self.play(FadeIn(duties, shift=UP * 0.1))
        self.play(FadeIn(workload_label), LaggedStart(*[FadeIn(w, shift=UP * 0.2) for w in workloads], lag_ratio=0.2))

        self.beat()
        clear(self, head)
        stats = [
            (96, lambda v: f"{v:.0f}", "RTX PRO 6000 GPUs", "12 nodes × 8 · 96 GB GDDR7 each\nPCIe Gen5, no NVLink"),
            (42, lambda v: f"≈{v:.0f}B", "tokens per week", "TaaS report\nSeptember 25, 2026"),
            (619, lambda v: f"{v:.0f}", "onboarded users", "up 62%, planning for\n≈1,500 and then ≈3,000"),
        ]
        boxes = VGroup(*[panel(4.1, 3.0) for _ in stats]).arrange(RIGHT, buff=0.35).move_to(DOWN * 0.4)
        trackers = [ValueTracker(0) for _ in stats]
        texts = VGroup()
        counters = []
        for box, tracker, (target, fmt, title, body) in zip(boxes, trackers, stats):
            counters.append(counter(tracker, fmt, 64, INDIGO, anchor=box.get_top() + DOWN * 0.8))
            texts.add(VGroup(
                txt(title, 24, INK, BOLD),
                txt(body, 17, MUTED, line_spacing=0.9),
            ).arrange(DOWN, buff=0.15).move_to(box).shift(DOWN * 0.6))
        confirm = mono("Confirm 90 vs 96 GPUs before external use", 14, AMBER).next_to(boxes, DOWN, buff=0.3).align_to(boxes, LEFT)
        self.play(LaggedStart(*[FadeIn(b, shift=UP * 0.2) for b in boxes], lag_ratio=0.2))
        self.add(*counters)
        self.play(*[t.animate.set_value(s[0]) for t, s in zip(trackers, stats)], FadeIn(texts), run_time=2.2)
        self.play(FadeIn(confirm))

        self.beat()
        lessons = VGroup(
            card("Capacity is cheap;\ninterconnect is not", "without NVLink, tensor parallelism\npushes every all-reduce over PCIe", width=6.0, height=3.0, accent=AMBER, title_size=28, body_size=18),
            card("PCIe favors models\nthat fit on one card", "Qwen3.6-35B-A3B on one RTX PRO 6000:\nfast to serve, not frontier-class", width=6.0, height=3.0, accent=INDIGO, title_size=28, body_size=18),
        ).arrange(RIGHT, buff=0.4).move_to(boxes)
        self.play(FadeOut(boxes), FadeOut(texts), FadeOut(confirm), *[FadeOut(c) for c in counters])
        self.play(LaggedStart(*[FadeIn(l, shift=UP * 0.3) for l in lessons], lag_ratio=0.5, run_time=2.0))

        self.beat()
        clear(self, head)
        title = mono("FP8 WEIGHTS VS. WHAT ONE RTX PRO 6000 HOLDS", 18, MUTED, BOLD).move_to([-6.5, 1.55, 0], aligned_edge=LEFT)
        scale, x0 = 7.4 / 1029, -2.4
        rows = VGroup()
        for i, (name, sub, gb, value, color) in enumerate([
            ("Qwen3.6-35B-A3B", "the farm's single-GPU agent model", 35, "≈35 GB", GREEN),
            ("DeepSeek V3.1", "frontier open model", 685, "≈685 GB", AMBER),
            ("Kimi K2", "frontier open model", 1029, "≈1 TB", AMBER),
        ]):
            y = 0.6 - i * 1.1
            names = VGroup(txt(name, 24, INK, BOLD), txt(sub, 16, MUTED)).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
            names.move_to([-6.5, y, 0], aligned_edge=LEFT)
            bar = Rectangle(width=gb * scale, height=0.55, stroke_width=0, fill_color=color, fill_opacity=0.9)
            bar.move_to([x0, y, 0], aligned_edge=LEFT)
            label = mono(value, 20, color, BOLD).next_to(bar, RIGHT, buff=0.2)
            label.set_x(max(label.get_x(), x0 + 86 * scale + 0.2 + label.width / 2))
            rows.add(VGroup(names, bar, label))
        gpu_x = x0 + 86 * scale
        gpu_line = DashedLine([gpu_x, 1.1, 0], [gpu_x, -1.95, 0], color=INK, stroke_width=3)
        gpu_label = mono("one GPU · ≈86 GB usable", 16, INK).next_to(gpu_line, DOWN, buff=0.12).align_to(gpu_line, LEFT).shift(LEFT * 0.2)
        self.play(FadeIn(title), Create(gpu_line), FadeIn(gpu_label))
        for names, bar, value in rows:
            self.play(FadeIn(names), GrowFromEdge(bar, LEFT), run_time=0.9)
            self.play(FadeIn(value), run_time=0.3)
        gap = txt("Frontier open models need 8–12× what one GPU holds.", 30, INK, BOLD).move_to(DOWN * 3.05)
        self.play(FadeIn(gap, shift=UP * 0.2))

        self.beat()
        clear(self, head)
        bar = MemoryBar(96, width=10.0, height=1.0).move_to(UP * 0.4)
        bar_title = mono("ONE RTX PRO 6000 · 96 GB", 18, MUTED, BOLD).next_to(bar, UP, buff=0.55).align_to(bar, LEFT)
        usable = DashedLine(bar.x_at(86) + UP * 0.6, bar.x_at(86) + DOWN * 0.6, color=INK, stroke_width=3).set_y(bar.get_y())
        usable_label = mono("90% usable", 16, INK).next_to(usable, UP, buff=0.1)
        session = bar.block(0, 64, AMBER)
        session_label = txt("one 128K-token agent session ≈64 GB", 24, INK, BOLD).move_to(session)
        basis = mono("KV cache at Llama 3.1 405B's ≈500 KB per token, before any weights", 16, MUTED)
        basis.next_to(bar, DOWN, buff=0.3).align_to(bar, LEFT)
        self.play(FadeIn(bar_title), Create(bar), Create(usable), FadeIn(usable_label))
        self.play(GrowFromEdge(session, LEFT), FadeIn(session_label), run_time=1.4)
        self.play(FadeIn(basis))
        quote = pull_quote("Usable LLMs for agentic work\nneed a GPU farm.", 38).move_to(DOWN * 2.3)
        self.play(FadeIn(quote, shift=UP * 0.2))


class S09Takeaways(NarratedSlide):
    narration = "09"

    def construct(self):
        self.beat()
        head = header("09 · Takeaways", "What to remember")
        self.play(FadeIn(head, shift=DOWN * 0.2))
        items = VGroup(*[
            VGroup(txt("✓", 34, GREEN, BOLD), txt(s, 28, INK)).arrange(RIGHT, buff=0.35)
            for s in [
                "Prefill sets the first token; decode sets completion. Measure both at p99.",
                "Check capacity and bandwidth for every model–GPU pair.",
                "KV cache, not weights, usually limits concurrency.",
                "The GPU SKU decides how many failure domains a replica spans.",
            ]
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.55).move_to(DOWN * 0.6)
        if items.width > 12.8:
            items.scale_to_fit_width(12.8)
        for item in items:
            self.play(FadeIn(item[1], shift=RIGHT * 0.2), run_time=0.6)
            self.play(Write(item[0]), run_time=0.4)
            self.wait(0.8)

        self.beat()
        clear(self, head)
        kicker = mono("COMING NEXT · PART 2", 20, AMBER, BOLD)
        title = txt("Parallelism and the fabric", 60, INK, BOLD)
        sub = txt(
            "Tensor, pipeline, expert, and data parallelism, the three networks\n"
            "in the Nutanix AI Factory, and why the interconnect becomes part of the accelerator.",
            22, MUTED, line_spacing=0.95,
        )
        teaser = VGroup(kicker, title, sub).arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to(UP * 0.4)
        gpus = VGroup(*[
            Square(0.5, stroke_color=INDIGO, stroke_width=2, fill_color=INDIGO_SOFT, fill_opacity=1) for _ in range(8)
        ]).arrange(RIGHT, buff=0.9).move_to(DOWN * 2.3)
        links = VGroup(*[
            ArcBetweenPoints(a.get_top(), b.get_top(), angle=-PI / 2, color=LINE, stroke_width=3)
            for i, a in enumerate(gpus) for b in gpus[i + 1:i + 3]
        ])
        self.play(FadeIn(kicker, shift=UP * 0.2), Write(title), run_time=1.6)
        self.play(FadeIn(sub))
        self.play(LaggedStart(*[FadeIn(g, scale=0.7) for g in gpus], lag_ratio=0.1), Create(links, lag_ratio=0.05, run_time=1.8))
        self.play(LaggedStart(*[
            ShowPassingFlash(l.copy().set_color(AMBER).set_stroke(width=6), time_width=0.6) for l in links
        ], lag_ratio=0.08, run_time=2.4))

        self.beat()
        clear(self)
        kicker = mono("INFERENCE ENGINEERING AT NUTANIX · PART 1", 22, INDIGO, BOLD)
        title = txt("Inference is an\ninfrastructure problem", 72, INK, BOLD, line_spacing=0.85)
        cta = VGroup(chip("READ THE FULL POST", INDIGO, 20), mono("Internal audiences only", 18, MUTED)).arrange(RIGHT, buff=0.5)
        end = VGroup(kicker, title, cta).arrange(DOWN, aligned_edge=LEFT, buff=0.5).move_to(ORIGIN)
        self.play(FadeIn(kicker, shift=UP * 0.2), Write(title), run_time=2)
        self.play(FadeIn(cta, shift=UP * 0.2))
