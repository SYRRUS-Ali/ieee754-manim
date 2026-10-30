# Russian on-screen edition, synchronized with the updated English scenes.
from fractions import Fraction

from manim import *

# Pango handles Cyrillic; LaTeX formulas stay symbolic.
Text.set_default(font="Arial")

from ieee754_utils import (
    BIAS,
    MANT_BITS,
    binary_expansion,
    bits_to_double,
    decode_fields,
    double_bits,
    exact_decimal,
    exact_frac_length,
    normalize,
    round_mantissa,
    sci_tex,
    split_fields,
    times_two_steps,
)

# input numbers, everything else is computed from them
SCENE1_NUMBER = "19.59375"
SCENE2_NUMBER = "0.3"
SCENE2_FRAC_BITS = 90

SIGN_COLOR = GREEN
EXP_COLOR = RED
MANT_COLOR = "#4FC3F7"
TAIL_COLOR = YELLOW
CELL_H = 0.42
MONO = "Consolas"


def ru_text(*args, **kwargs):
    text = Text(*args, **kwargs)
    if text.width > 12.8:
        text.scale_to_fit_width(12.8)
    return text


def field_color(i):
    # i counts cells from the left, so the bit number is 63 - i
    if i == 0:
        return SIGN_COLOR
    if i <= 11:
        return EXP_COLOR
    return MANT_COLOR


def make_bar(cell_w, left_x, y, with_dimension=True):
    cells = VGroup()
    for i in range(64):
        cell = Rectangle(width=cell_w, height=CELL_H)
        cell.set_stroke(field_color(i), 1).set_fill(field_color(i), 0.2)
        cell.move_to([left_x + cell_w * (i + 0.5), y, 0])
        cells.add(cell)

    fields = [cells[0:1], cells[1:12], cells[12:]]
    outlines = VGroup(
        *[
            SurroundingRectangle(f, buff=0, color=field_color(i), stroke_width=3)
            for f, i in zip(fields, [0, 1, 12])
        ]
    )

    idx = VGroup(
        ru_text("63", font_size=16).next_to(cells[0], UP, buff=0.1).align_to(cells[0], RIGHT).shift(LEFT * 0.03),
        ru_text("62", font_size=16).next_to(cells[1], UP, buff=0.1).align_to(cells[1], LEFT).shift(RIGHT * 0.03),
        ru_text("51", font_size=16).next_to(cells[12], UP, buff=0.1).align_to(cells[12], LEFT),
        ru_text("0", font_size=16).next_to(cells[63], UP, buff=0.1).align_to(cells[63], RIGHT),
    )

    names = VGroup(
        ru_text("Знак", font_size=22, color=SIGN_COLOR).align_to(cells[0], LEFT),
        ru_text("Порядок", font_size=22, color=EXP_COLOR),
        ru_text("Мантисса", font_size=22, color=MANT_COLOR).set_x(fields[2].get_x()),
    )
    names[1].next_to(names[0], RIGHT, buff=0.3)
    for name in names:
        name.set_y(y + CELL_H / 2 + 0.55)

    deco = VGroup(outlines, idx, names)
    if with_dimension:
        left = cells[0].get_left()[0]
        right = cells[-1].get_right()[0]
        dim_y = y - CELL_H / 2 - 0.3
        arrow = DoubleArrow(
            [left, dim_y, 0], [right, dim_y, 0], buff=0, stroke_width=2,
            tip_length=0.15, max_tip_length_to_length_ratio=0.05,
        )
        ticks = VGroup(
            Line([left, y - CELL_H / 2, 0], [left, dim_y - 0.1, 0], stroke_width=1.5),
            Line([right, y - CELL_H / 2, 0], [right, dim_y - 0.1, 0], stroke_width=1.5),
        )
        label = ru_text("64", font_size=20).move_to(arrow)
        label.add_background_rectangle(opacity=1, buff=0.08)
        deco.add(VGroup(ticks, arrow, label))
    return cells, deco


def cell_digits(bits, cells, font_size):
    return VGroup(*[ru_text(b, font=MONO, font_size=font_size).move_to(c) for b, c in zip(bits, cells)])


def caption(text, y=0.55):
    return ru_text(text, font_size=28).to_edge(LEFT, buff=0.6).set_y(y)


def row_labels(table, texts=("Вес", "Бит"), font_size=22):
    # names of the two table rows, placed left of the table
    boxes = table[0]
    labels = VGroup()
    for text, box in zip(texts, boxes[:2]):
        label = ru_text(text, font_size=font_size, color=GREY_B).set_y(box.get_y())
        labels.add(label.align_to(boxes.get_left() + LEFT * 0.25, RIGHT))
    return labels


def terms_row(cols, digits, terms, y, font_size=32, color=WHITE, max_w=None):
    # the place values of the 1 bits, each one under its own column, joined by "+"
    picked = [i for i, d in enumerate(digits) if d == "1"]
    term_mobs = VGroup(*[MathTex(terms[i], font_size=font_size, color=color).move_to([cols[i].get_x(), y, 0]) for i in picked])
    for term in term_mobs:
        if max_w is not None and term.width > max_w:
            term.scale_to_fit_width(max_w)
    pluses = VGroup(*[
        MathTex("+", font_size=font_size).move_to([(a.get_right()[0] + b.get_left()[0]) / 2, y, 0])
        for a, b in zip(term_mobs[:-1], term_mobs[1:])
    ])
    return picked, term_mobs, pluses


def place_value_table(headers, digits, point_after=None, col_w=1.0, digit_color=WHITE):
    # one column per digit: weight on top, digit below; optional binary point
    boxes = VGroup()
    digit_mobs = VGroup()
    x = 0
    point = None
    for i, (head, d) in enumerate(zip(headers, digits)):
        if point_after is not None and i == point_after:
            point = Dot(radius=0.07).move_to([x + 0.05, -0.62, 0])
            x += 0.4
        top = Rectangle(width=col_w, height=0.6).move_to([x + col_w / 2, 0.3, 0])
        bottom = Rectangle(width=col_w, height=0.75).move_to([x + col_w / 2, -0.375, 0])
        boxes.add(top, bottom)
        head.move_to(top)
        if head.width > col_w * 0.88:
            head.scale_to_fit_width(col_w * 0.88)
        digit_mobs.add(ru_text(d, font=MONO, font_size=36, color=digit_color).move_to(bottom))
        x += col_w
    boxes.set_stroke(GREY_B, 1.5)
    heads = VGroup(*headers)
    table = VGroup(boxes, heads, digit_mobs)
    if point is not None:
        table.add(point)
    return table, heads, digit_mobs, point


class BuildDoubleRU(Scene):
    def construct(self):
        value = Fraction(SCENE1_NUMBER)
        x = float(SCENE1_NUMBER)
        bits = double_bits(x)
        s_bit, e_bits, m_bits = split_fields(bits)
        E = int(e_bits, 2)
        x_str = exact_decimal(abs(value))

        # --- intro and the empty 64-bit layout ---
        title = ru_text("IEEE 754: двойная точность (64 бита)", font_size=44)
        authors = ru_text("Махмуд А.А., Мехрез М.  |  группа 231-352", font_size=24, color=GREY_B)
        authors.next_to(title, DOWN, buff=0.4)
        self.play(Write(title), run_time=1.5)
        self.play(FadeIn(authors))
        self.wait(1)
        self.play(FadeOut(title), FadeOut(authors))

        cells, deco = make_bar(0.2, -6.4, 2.75)
        bit_mobs = cell_digits(bits, cells, 15)
        self.play(LaggedStart(*[FadeIn(c) for c in cells], lag_ratio=0.03), run_time=2)
        self.play(Create(deco[0]), FadeIn(deco[1]), FadeIn(deco[2]))
        self.play(FadeIn(deco[3]))

        formula = MathTex(
            "F =", "(-1)^{S}", r"\cdot", "2^{E-1023}", r"\cdot", r"\left(1+\frac{M}{2^{52}}\right)",
            font_size=44,
        ).set_y(1.5)
        formula[1].set_color(SIGN_COLOR)
        formula[3].set_color(EXP_COLOR)
        formula[5].set_color(MANT_COLOR)
        self.play(Write(formula), run_time=2)
        self.wait(1.5)

        # --- step 1: binary with a place-value table ---
        int_bits, frac_bits = binary_expansion(abs(value), exact_frac_length(abs(value), 8))
        digits = int_bits + frac_bits
        weights = [Fraction(2) ** k for k in range(len(int_bits) - 1, -len(frac_bits) - 1, -1)]
        header_strs = [exact_decimal(w) for w in weights]
        headers = [ru_text(h, font_size=24) for h in header_strs]
        table, heads, digit_mobs, point = place_value_table(headers, digits, point_after=len(int_bits))
        labels = row_labels(table)
        VGroup(table, labels).move_to([0.3, -1.2, 0])

        cap = caption(f"Шаг 1.  Запишем {x_str} в двоичной системе")
        self.play(FadeIn(cap))
        self.play(Create(table[0]), FadeIn(heads), FadeIn(point), run_time=1.5)
        self.play(FadeIn(labels, shift=RIGHT * 0.2))
        self.play(Indicate(labels[0]), Indicate(heads, color=YELLOW, scale_factor=1.05))
        self.play(Indicate(labels[1]))

        # the number is split into its integer and fraction parts, each one goes over its half of the table
        int_part = abs(value).numerator // abs(value).denominator
        frac_part = abs(value) - int_part
        number = MathTex(str(int_part), "." + exact_decimal(frac_part)[2:], font_size=48).move_to([0.3, -0.05, 0])
        self.play(Write(number))
        self.wait(0.5)
        rem_y = -0.05
        rem_int = MathTex(str(int_part), font_size=40, color=YELLOW)
        rem_int.move_to([heads[: len(int_bits)].get_x(), rem_y, 0])
        rem_frac = MathTex(exact_decimal(frac_part), font_size=40, color=YELLOW)
        rem_frac.move_to([heads[len(int_bits):].get_x(), rem_y, 0])
        self.play(ReplacementTransform(number[0], rem_int), ReplacementTransform(number[1], rem_frac), run_time=1.2)

        # fill the bits from left to right: take the place value if it still fits into what is left
        rest = [Fraction(int_part), frac_part]
        trackers = [rem_int, rem_frac]
        for i, w in enumerate(weights):
            part = 0 if i < len(int_bits) else 1
            r = rest[part]
            r_str, w_str = exact_decimal(r), exact_decimal(w)
            col = SurroundingRectangle(VGroup(table[0][2 * i], table[0][2 * i + 1]), color=YELLOW, buff=0.03)
            if digits[i] == "1":
                rest[part] = r - w
                note = MathTex(rf"{r_str} \ge {w_str}", r"\;\Rightarrow\;", "1", rf",\quad {r_str} - {w_str} = {exact_decimal(rest[part])}", font_size=34)
            else:
                note = MathTex(rf"{r_str} < {w_str}", r"\;\Rightarrow\;", "0", font_size=34)
            note[2].set_color(YELLOW)
            note.move_to([0, -2.45, 0])
            self.play(Create(col), FadeIn(note), run_time=0.45)
            anims = [TransformFromCopy(note[2], digit_mobs[i])]
            if rest[part] != r:
                new_tracker = MathTex(exact_decimal(rest[part]), font_size=40, color=YELLOW).move_to(trackers[part])
                anims.append(Transform(trackers[part], new_tracker))
            self.play(*anims, run_time=0.5)
            self.play(FadeOut(col), FadeOut(note), run_time=0.3)
        self.play(FadeOut(rem_int), FadeOut(rem_frac))

        # every 1 bit adds its place value, every 0 bit adds nothing
        ones = [i for i, d in enumerate(digits) if d == "1"]
        zeros = [i for i, d in enumerate(digits) if d == "0"]
        rule = ru_text("Бит 1 → прибавляем вес разряда; бит 0 → пропускаем", font_size=26).move_to([0.3, rem_y, 0])
        self.play(FadeIn(rule))
        self.play(
            *[heads[i].animate.set_color(YELLOW) for i in ones], *[digit_mobs[i].animate.set_color(YELLOW) for i in ones],
            *[heads[i].animate.set_opacity(0.35) for i in zeros], *[digit_mobs[i].animate.set_opacity(0.35) for i in zeros],
        )
        picked, term_mobs, pluses = terms_row(digit_mobs, digits, header_strs, -2.45, font_size=28, color=YELLOW, max_w=0.68)
        arrows = VGroup(*[
            Arrow([digit_mobs[i].get_x(), -1.92, 0], term.get_top() + UP * 0.05, buff=0, stroke_width=3,
                  max_tip_length_to_length_ratio=0.35, color=YELLOW)
            for i, term in zip(picked, term_mobs)
        ])
        self.play(LaggedStart(*[
            AnimationGroup(GrowArrow(a), TransformFromCopy(heads[i], t)) for i, a, t in zip(picked, arrows, term_mobs)
        ], lag_ratio=0.4), run_time=3)
        self.play(FadeIn(pluses))
        bin_line = MathTex(rf"{x_str} = {int_bits}.{frac_bits}_2", font_size=40).move_to([0.3, -3.35, 0])
        self.play(Write(bin_line))
        self.wait(2)
        self.play(*[FadeOut(m) for m in [table, labels, cap, rule, arrows, term_mobs, pluses, bin_line]])

        # --- step 2: normalize by moving the binary point ---
        e, lead = normalize(int_bits, frac_bits)
        cap = caption("Шаг 2.  Нормализация: одна единица перед точкой")
        row = VGroup(*[ru_text(d, font=MONO, font_size=44) for d in digits])
        for i, d in enumerate(row):
            d.move_to([i * 0.5, 0, 0])
        row.move_to([0, -1.1, 0])

        def point_at(k):
            # binary point between digit k-1 and digit k
            return [(row[k - 1].get_x() + row[k].get_x()) / 2, row[0].get_bottom()[1] + 0.07, 0]

        dot = Dot(radius=0.07).move_to(point_at(len(int_bits)))
        exp_label = MathTex(r"\cdot\, 2^{0}", font_size=50).next_to(row, RIGHT, buff=0.3)
        self.play(FadeIn(cap), FadeIn(row), FadeIn(dot))
        self.play(FadeIn(exp_label))

        k = len(int_bits)
        step = -1 if k > lead + 1 else 1
        while k != lead + 1:
            k += step
            moved = len(int_bits) - k
            new_label = MathTex(rf"\cdot\, 2^{{{moved}}}", font_size=50).move_to(exp_label, aligned_edge=LEFT)
            self.play(dot.animate.move_to(point_at(k)), Transform(exp_label, new_label), run_time=0.5)
        if lead > 0:
            self.play(FadeOut(row[:lead]))

        # the moving row itself turns into the normalized form, so it is not written twice
        rest = digits[lead + 1:].rstrip("0") or "0"
        norm_line = MathTex(f"{x_str} =", "1.", f"{rest}_2", rf"\cdot\, 2^{{{e}}}", font_size=48)
        norm_line.move_to([0, -1.1, 0])
        norm_line[2].set_color(MANT_COLOR)
        norm_line[3].set_color(EXP_COLOR)
        self.play(
            FadeIn(norm_line[0], shift=RIGHT * 0.3),
            ReplacementTransform(VGroup(row[lead], dot), norm_line[1]),
            ReplacementTransform(row[lead + 1:], norm_line[2]),
            ReplacementTransform(exp_label, norm_line[3]),
            run_time=1.5,
        )
        self.wait(1.5)

        # keep the normalized form as a reference for the next steps
        self.play(FadeOut(cap), norm_line.animate.scale(40 / 48).move_to([0, -0.15, 0]))

        # --- step 3: biased exponent ---
        assert E == e + BIAS
        cap = caption("Шаг 3.  Порядок:  E = e + 1023", y=0.55)
        e_line = MathTex(f"E = {e} + {BIAS} = {E} =", font_size=40)
        e_digits = VGroup(*[ru_text(b, font=MONO, font_size=36, color=EXP_COLOR) for b in e_bits])
        e_digits.arrange(RIGHT, buff=0.08)
        sub2 = MathTex("_2", font_size=40)
        e_group = VGroup(e_line, e_digits, sub2).arrange(RIGHT, buff=0.15).move_to([0, -1.3, 0])
        e_digits.align_to(e_line, DOWN)
        sub2.next_to(e_digits, RIGHT, buff=0.05).align_to(e_digits, DOWN).shift(DOWN * 0.1)
        powers = [2 ** (10 - i) for i, b in enumerate(e_bits) if b == "1"]
        e_sum = MathTex(f"{E} = " + " + ".join(map(str, powers)), font_size=36).move_to([0, -2.2, 0])

        self.play(FadeIn(cap), Indicate(norm_line[3], color=EXP_COLOR))
        self.play(Write(e_line))
        self.play(FadeIn(e_digits, lag_ratio=0.1), FadeIn(sub2), Write(e_sum))
        self.wait(1)
        self.play(LaggedStart(*[TransformFromCopy(e_digits[i], bit_mobs[1 + i]) for i in range(11)], lag_ratio=0.1), run_time=2)
        self.wait(1)
        self.play(FadeOut(cap), FadeOut(e_group), FadeOut(e_sum))

        # --- step 4: mantissa with place values 2^-1, 2^-2, ... ---
        shown = m_bits.rstrip("0") or "0"
        n = min(len(shown), 12)
        m_head_strs = [f"2^{{-{k}}}" for k in range(1, n + 1)]
        m_heads = [MathTex(h, font_size=32) for h in m_head_strs]
        m_table, m_head_mobs, m_digit_mobs, _ = place_value_table(m_heads, m_bits[:n], col_w=0.9, digit_color=MANT_COLOR)
        m_labels = row_labels(m_table)
        VGroup(m_table, m_labels).move_to([-1.2, -1.3, 0])
        m_frac = Fraction(int(m_bits, 2), 2**MANT_BITS)

        cap = caption("Шаг 4. Мантисса: биты после 1", y=0.55)
        self.play(FadeIn(cap), Indicate(norm_line[2], color=MANT_COLOR))
        self.play(Create(m_table[0]), FadeIn(m_table[1]), FadeIn(m_labels))
        self.play(TransformFromCopy(norm_line[2][:n], m_digit_mobs), run_time=1.5)
        self.play(LaggedStart(*[TransformFromCopy(m_digit_mobs[i], bit_mobs[12 + i]) for i in range(n)], lag_ratio=0.1), run_time=2)
        zeros_note = ru_text(f"Остальные {MANT_BITS - n} бита — нули", font_size=24, color=GREY_B)
        zeros_note.next_to(cap, RIGHT, buff=0.3)
        self.play(LaggedStart(*[FadeIn(b) for b in bit_mobs[12 + n:]], lag_ratio=0.02), FadeIn(zeros_note), run_time=1.5)

        # what the mantissa bits are worth: the same place value idea as in step 1, now only after the point
        picked, m_terms, m_pluses = terms_row(m_digit_mobs, m_bits[:n], m_head_strs, -2.4, font_size=32, color=MANT_COLOR)
        m_arrows = VGroup(*[
            Arrow([m_digit_mobs[i].get_x(), -2.02, 0], term.get_top() + UP * 0.03, buff=0, stroke_width=3,
                  max_tip_length_to_length_ratio=0.4, color=MANT_COLOR)
            for i, term in zip(picked, m_terms)
        ])
        m_sum = MathTex(f"= {exact_decimal(m_frac)}", font_size=32).next_to(m_terms[-1], RIGHT, buff=0.25)
        self.play(*[m_digit_mobs[i].animate.set_opacity(0.35) for i in range(n) if m_bits[i] == "0"])
        self.play(LaggedStart(*[
            AnimationGroup(GrowArrow(a), TransformFromCopy(m_head_mobs[i], t)) for i, a, t in zip(picked, m_arrows, m_terms)
        ], lag_ratio=0.4), run_time=2.5)
        self.play(FadeIn(m_pluses), Write(m_sum))
        self.wait(1)

        # this sum is the M/2^52 part of the formula: M is the 52 bits read as one whole number,
        # dividing by 2^52 moves the point back in front of them
        m_line = MathTex(r"\frac{M}{2^{52}}", "=", rf"0.{shown}_2", "=", exact_decimal(m_frac), font_size=36)
        m_line[0].set_color(MANT_COLOR)
        why = VGroup(
            ru_text("M — 52 бита мантиссы как одно целое число", font_size=28),
            ru_text("Деление на 2⁵² ставит точку перед этими битами", font_size=28),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.15).set_color(GREY_B)
        explanation = VGroup(m_line, why).arrange(RIGHT, buff=0.4)
        if explanation.width > 12.8:
            explanation.scale_to_fit_width(12.8)
        explanation.move_to([0, -3.3, 0])
        m_box = SurroundingRectangle(formula[5], color=MANT_COLOR, buff=0.08)
        self.play(Create(m_box), Indicate(norm_line[1:3], color=MANT_COLOR))
        self.play(TransformFromCopy(formula[5], m_line[0]), FadeIn(why[0]))
        self.play(FadeIn(why[1]))
        self.play(Write(m_line[1:]))
        self.wait(2.5)
        self.play(*[FadeOut(m) for m in [cap, zeros_note, m_table, m_labels, m_arrows, m_terms, m_pluses, m_sum, m_line, why, m_box]])

        # --- step 5: sign ---
        cap = caption("Шаг 5.  Знак", y=0.55)
        relation = ">" if s_bit == "0" else "<"
        s_line = MathTex(f"{exact_decimal(value)} {relation} 0", r"\;\Rightarrow\;", f"S = {s_bit}", font_size=44)
        s_line[2].set_color(SIGN_COLOR)
        s_line.move_to([0, -1.4, 0])
        self.play(FadeIn(cap), Write(s_line))
        self.play(TransformFromCopy(s_line[2][-1], bit_mobs[0]), run_time=1.2)
        self.play(Indicate(bit_mobs[0], color=SIGN_COLOR), Circumscribe(cells, color=YELLOW, buff=0.05))
        self.wait(1)
        self.play(FadeOut(cap), FadeOut(s_line), FadeOut(norm_line))

        # --- step 6: back from the bits to the number ---
        decoded = decode_fields(s_bit, e_bits, m_bits)
        assert decoded == Fraction(bits_to_double(bits))
        cap = caption("Шаг 6.  Обратно в десятичную: подставим S, E, M", y=0.55)
        vals = MathTex(
            f"S = {s_bit}", r",\qquad", f"E = {E}", r",\qquad", rf"\frac{{M}}{{2^{{52}}}} = {exact_decimal(m_frac)}",
            font_size=38,
        ).move_to([0, -0.45, 0])
        vals[0].set_color(SIGN_COLOR)
        vals[2].set_color(EXP_COLOR)
        vals[4].set_color(MANT_COLOR)

        self.play(FadeIn(cap), Indicate(formula, scale_factor=1.05))
        for field, part in [(cells[0:1], 0), (cells[1:12], 2), (cells[12:], 4)]:
            box = SurroundingRectangle(field, color=YELLOW, buff=0.04)
            self.play(Create(box), FadeIn(vals[part]), run_time=0.8)
            self.play(FadeOut(box), run_time=0.3)
        self.play(FadeIn(vals[1]), FadeIn(vals[3]))

        power = Fraction(2) ** (E - BIAS)
        line1 = MathTex(
            "F =", f"(-1)^{{{s_bit}}}", r"\cdot", f"2^{{{E}-{BIAS}}}", r"\cdot", rf"(1 + {exact_decimal(m_frac)})",
            font_size=40,
        ).move_to([0, -1.45, 0])
        line1[1].set_color(SIGN_COLOR)
        line1[3].set_color(EXP_COLOR)
        line1[5].set_color(MANT_COLOR)
        line2 = MathTex(
            "=", f"{(-1) ** int(s_bit)}", r"\cdot", exact_decimal(power), r"\cdot", exact_decimal(1 + m_frac), font_size=40
        ).next_to(line1, DOWN, buff=0.3)
        line2[1].set_color(SIGN_COLOR)
        line2[3].set_color(EXP_COLOR)
        line2[5].set_color(MANT_COLOR)
        line3 = MathTex(f"= {exact_decimal(decoded)}", font_size=48).next_to(line2, DOWN, buff=0.3)
        self.play(Write(line1), run_time=1.5)
        self.play(FadeIn(line2[0]), FadeIn(line2[2]), FadeIn(line2[4]))
        # each colored part of the formula turns into its own value, in the same color
        for part in (1, 3, 5):
            self.play(TransformFromCopy(line1[part], line2[part]), run_time=0.8)
        self.play(Write(line3))
        self.play(Create(SurroundingRectangle(line3, color=YELLOW, buff=0.15)))
        hex_note = ru_text(f"Код: 0x{int(bits, 2):016X}", font=MONO, font_size=22, color=GREY_B)
        hex_note.to_corner(DR, buff=0.4)
        self.play(FadeIn(hex_note))
        self.wait(3)


class RoundoffErrorRU(Scene):
    def construct(self):
        true_value = Fraction(SCENE2_NUMBER)
        x = float(SCENE2_NUMBER)
        stored = Fraction(x)
        bits = double_bits(x)
        s_bit, e_bits, m_bits = split_fields(bits)
        E = int(e_bits, 2)
        x_str = exact_decimal(true_value)

        # --- intro ---
        title = ru_text("Погрешность округления", font_size=48).to_edge(UP, buff=0.8)
        big = MathTex(f"x = {x_str}", font_size=96)
        question = ru_text("Просто в десятичной системе. А что хранит компьютер?", font_size=28, color=GREY_B)
        question.next_to(big, DOWN, buff=0.7)
        self.play(Write(title))
        self.play(Write(big))
        self.play(FadeIn(question))
        self.wait(1.5)
        self.play(FadeOut(title), FadeOut(question), FadeOut(big))

        # --- multiply by 2 method for the fraction part ---
        int_part = true_value.numerator // true_value.denominator
        cap = ru_text("Шаг 1. Перевод дроби в двоичную систему: умножаем на 2", font_size=26)
        cap.to_edge(UP, buff=0.6)
        steps = times_two_steps(true_value - int_part, 8)
        lines = VGroup()
        for frac, product, digit, _ in steps:
            line = MathTex(
                exact_decimal(frac), r"\cdot 2 =", exact_decimal(product), r"\;\rightarrow\;", str(digit),
                font_size=38,
            )
            line[0].set_color(MANT_COLOR)
            line[4].set_color(YELLOW)
            lines.add(line)
        lines.arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to([-3.2, -0.4, 0])
        legend = ru_text(f"Начинаем с {x_str}; далее берём дробную часть произведения.", font_size=23, color=GREY_B)
        legend.next_to(cap, DOWN, buff=0.3)
        self.play(FadeIn(cap), FadeIn(legend))
        bits_so_far = "".join(str(d) for _, _, d, _ in steps)
        collected_digits = VGroup(*[
            ru_text(d, font=MONO, font_size=30, color=YELLOW) for d in bits_so_far
        ]).arrange(RIGHT, buff=0.06)
        collected_prefix = MathTex(rf"{x_str} = {int_part}.", font_size=36)
        collected_suffix = MathTex(r"\ldots_2", font_size=36)
        collected = VGroup(collected_prefix, collected_digits, collected_suffix)
        collected.arrange(RIGHT, buff=0.08).move_to([3.2, -1.0, 0])
        order_note = ru_text('Читаем сверху вниз; биты пишем слева направо.', font_size=22, color=YELLOW)
        if order_note.width > 6.5:
            order_note.scale_to_fit_width(6.5)
        order_note.next_to(collected, DOWN, buff=0.35)
        self.play(Write(collected_prefix), FadeIn(order_note))
        deОстаток = VGroup()
        previous_remainder = None
        for i, (frac, product, digit, _) in enumerate(steps):
            remainder = product - digit
            detail_new = VGroup(
                ru_text("Выделяем целую и дробную части", font_size=22, color=GREY_B),
                MathTex(exact_decimal(product), "=", str(digit), "+", exact_decimal(remainder), font_size=34),
                MathTex(r"r_{i+1} =", exact_decimal(product), "-", str(digit), "=", exact_decimal(remainder), font_size=30),
            ).arrange(DOWN, buff=0.22).move_to([3.2, 1.0, 0])
            detail_new[1][2].set_color(YELLOW)
            detail_new[1][4].set_color(MANT_COLOR)
            detail_new[2][3].set_color(YELLOW)
            detail_new[2][5].set_color(MANT_COLOR)
            if previous_remainder is None:
                self.play(FadeIn(lines[i][:4], shift=DOWN * 0.1), run_time=0.8)
            else:
                self.play(TransformFromCopy(previous_remainder, lines[i][0], path_arc=PI / 4), run_time=1.3)
                self.play(FadeIn(lines[i][1:4]), run_time=0.6)
            self.play(FadeOut(deОстаток), FadeIn(detail_new))
            deОстаток = detail_new
            self.play(Indicate(deОстаток[1][2], color=YELLOW), run_time=0.6)
            self.play(TransformFromCopy(deОстаток[1][2], lines[i][4]), run_time=0.8)
            self.play(TransformFromCopy(lines[i][4], collected_digits[i], path_arc=-PI / 4), run_time=1.3)
            self.play(Indicate(deОстаток[2][5], color=MANT_COLOR), run_time=0.6)
            previous_remainder = deОстаток[2][5]
            self.wait(0.7)
        self.play(Write(collected_suffix))
        if steps and steps[-1][3]:
            # the fraction came back to an earlier value, so the bits repeat forever
            first = next(i for i, s in enumerate(steps) if s[0] == steps[-1][0])
            boxes = VGroup(
                SurroundingRectangle(lines[first][:3], color=ORANGE, buff=0.06),
                SurroundingRectangle(lines[-1][:3], color=ORANGE, buff=0.06),
            )
            repeat_note = ru_text("Значение повторилось: биты будут повторяться", font_size=24, color=ORANGE)
            repeat_note.next_to(lines, DOWN, buff=0.35).align_to(lines, LEFT)
            self.play(Create(boxes), FadeIn(repeat_note))
        else:
            boxes = VGroup()
            repeat_note = VGroup()
        self.wait(2)
        self.play(FadeOut(cap), FadeOut(lines), FadeOut(boxes), FadeOut(repeat_note), FadeOut(collected),
                  FadeOut(legend), FadeOut(deОстаток), FadeOut(order_note))

        # --- long binary row, more bits than a double can hold ---
        int_bits, frac_bits = binary_expansion(true_value, SCENE2_FRAC_BITS)
        digits = int_bits + frac_bits
        spacing = 0.3
        row = VGroup(*[ru_text(d, font=MONO, font_size=30) for d in digits])
        for i, d in enumerate(row):
            d.move_to([-6.2 + i * spacing + (0.15 if i >= len(int_bits) else 0), 0.3, 0])

        def point_at(k):
            return [(row[k - 1].get_x() + row[k].get_x()) / 2, row[0].get_bottom()[1] + 0.05, 0]

        dot = Dot(radius=0.05).move_to(point_at(len(int_bits)))
        cap = ru_text(f"Итог шага 1. {x_str}: первые {SCENE2_FRAC_BITS} бит бесконечной двоичной дроби", font_size=25)
        cap.to_edge(UP, buff=0.6)
        self.play(FadeIn(cap))
        self.play(FadeIn(row[: len(int_bits)]), FadeIn(dot))
        self.play(LaggedStart(*[FadeIn(d) for d in row[len(int_bits):]], lag_ratio=0.03), run_time=3)
        self.play(VGroup(row, dot).animate.shift(LEFT * 14), run_time=2.5)
        self.play(VGroup(row, dot).animate.shift(RIGHT * 14), run_time=1.5)

        # --- normalize ---
        e, lead = normalize(int_bits, frac_bits)
        new_cap = ru_text("Шаг 2. Нормализация: одна единица перед точкой", font_size=26)
        new_cap.move_to(cap)
        self.play(Transform(cap, new_cap))
        k = len(int_bits)
        step = -1 if k > lead + 1 else 1
        power = MathTex(r"\times 2^{0}", font_size=38, color=EXP_COLOR)
        power.move_to([point_at(k)[0], -0.6, 0])
        shift_note = ru_text('Сдвиг точки вправо умножает число на 2; уменьшаем показатель на 1.', font_size=24, color=GREY_B).set_y(-1.5)
        self.play(Write(power), FadeIn(shift_note))
        while k != lead + 1:
            k += step
            exponent = len(int_bits) - k
            new_power = MathTex(rf"\times 2^{{{exponent}}}", font_size=38, color=EXP_COLOR)
            new_power.move_to([point_at(k)[0], -0.6, 0])
            self.play(dot.animate.move_to(point_at(k)), Transform(power, new_power), run_time=1)
            self.wait(0.5)
        if lead > 0:
            self.play(FadeOut(row[:lead]))
        after = digits[lead + 1:]
        norm_line = MathTex(f"{x_str} = 1.", rf"{after[:12]}\ldots_2", rf"\cdot\, 2^{{{e}}}", font_size=40)
        norm_line[1].set_color(MANT_COLOR)
        norm_line[2].set_color(EXP_COLOR)
        norm_line.move_to([0, -0.7, 0])
        mantissa_outline = SurroundingRectangle(row[lead + 1:lead + 13], color=MANT_COLOR, buff=0.08)
        self.play(FadeOut(shift_note))
        self.play(row[lead + 1:].animate.set_color(MANT_COLOR), Create(mantissa_outline))
        self.play(Write(norm_line[:2]), ReplacementTransform(power, norm_line[2]), run_time=2)
        self.play(Indicate(row[lead + 1:lead + 13], color=MANT_COLOR),
                  Indicate(norm_line[1], color=MANT_COLOR))
        self.play(FadeOut(mantissa_outline))
        self.wait(1)

        # --- the 64-bit grid, exponent and sign ---
        self.play(FadeOut(cap))
        cell_w = 0.18
        cells, deco = make_bar(cell_w, -6.8, 2.6, with_dimension=False)
        self.play(LaggedStart(*[FadeIn(c) for c in cells], lag_ratio=0.02), FadeIn(deco), run_time=1.5)
        bit_mobs = cell_digits(bits, cells, 14)
        step_header = ru_text("Шаг 3. Кодируем порядок и знак", font_size=26).set_y(1.45)
        self.play(FadeIn(step_header))

        assert E == e + BIAS
        bias_note = VGroup(
            ru_text('Поле порядка содержит 11 бит. Смещение по IEEE 754:', font_size=25, color=EXP_COLOR),
            MathTex(r"B = 2^{11-1} - 1 = 1023,\qquad E = e + B", font_size=36),
            ru_text('Смещение позволяет хранить отрицательный показатель без знака.', font_size=23, color=GREY_B),
        ).arrange(DOWN, buff=0.22).move_to([0, -2.15, 0])
        self.play(Write(bias_note), run_time=2)
        self.wait(2)
        self.play(FadeOut(bias_note))
        e_line = MathTex(f"E = {e} + {BIAS} = {E} =", font_size=36)
        e_digits = VGroup(*[ru_text(b, font=MONO, font_size=32, color=EXP_COLOR) for b in e_bits]).arrange(RIGHT, buff=0.07)
        VGroup(e_line, e_digits).arrange(RIGHT, buff=0.15).move_to([0, -1.8, 0])
        e_digits.align_to(e_line, DOWN)
        self.play(Write(e_line), FadeIn(e_digits, lag_ratio=0.1))
        self.play(LaggedStart(*[TransformFromCopy(e_digits[i], bit_mobs[1 + i]) for i in range(11)], lag_ratio=0.08), run_time=1.5)

        relation = ">" if s_bit == "0" else "<"
        s_line = MathTex(f"{x_str} {relation} 0", r"\;\Rightarrow\;", f"S = {s_bit}", font_size=36)
        s_line[2].set_color(SIGN_COLOR)
        s_line.move_to([0, -2.7, 0])
        self.play(Write(s_line))
        self.play(TransformFromCopy(s_line[2][-1], bit_mobs[0]))
        self.wait(0.5)
        self.play(FadeOut(e_line), FadeOut(e_digits), FadeOut(s_line), FadeOut(norm_line), FadeOut(step_header))

        # --- lay the bits after the leading 1 under the mantissa field ---
        row_y = 2.0
        small = VGroup()
        for i, d in enumerate(row):
            pos = i - lead - 1  # position after the leading 1
            small.add(ru_text(digits[i], font=MONO, font_size=14, color=MANT_COLOR if i > lead else WHITE).move_to([cells[12].get_x() + pos * cell_w, row_y, 0]))
        small_dot = Dot(radius=0.03).move_to([cells[12].get_left()[0], small[0].get_bottom()[1] + 0.03, 0])
        self.play(
            *[Transform(row[i], small[i]) for i in range(lead, len(row))],
            dot.animate.move_to(small_dot.get_center()).scale(0.6),
            run_time=2,
        )
        lead_note = ru_text("Старшая единица не хранится", font_size=20, color=GREY_B)
        lead_note.next_to(row[lead], DOWN, buff=0.3).align_to(cells[0], LEFT)
        self.play(FadeIn(lead_note), Indicate(row[lead]))
        self.play(FadeOut(row[lead]), FadeOut(dot), FadeOut(lead_note))

        kept_mobs = row[lead + 1: lead + 1 + MANT_BITS]
        tail_mobs = row[lead + 1 + MANT_BITS:]
        self.play(tail_mobs.animate.set_color(TAIL_COLOR))
        kept_box = SurroundingRectangle(kept_mobs, color=MANT_COLOR, buff=0.05)
        tail_left = cells[63].get_right()[0]
        tail_box = Rectangle(width=8, height=kept_box.height)
        tail_box.set_stroke(TAIL_COLOR, 2).set_fill(TAIL_COLOR, 0.15)
        tail_box.move_to([tail_left + 4 + 0.02, row_y, 0])
        kept_label = ru_text(f"В мантиссе помещается {MANT_BITS} бита", font_size=22, color=MANT_COLOR)
        kept_label.next_to(kept_box, DOWN, buff=0.2)
        tail_label = ru_text("Остаток", font_size=24, color=TAIL_COLOR).next_to(tail_box, DOWN, buff=0.2)
        tail_label.set_x((tail_left + 7.1) / 2)
        self.play(Create(kept_box), FadeIn(kept_label))
        self.play(FadeIn(tail_box), FadeIn(tail_label))
        self.wait(1)

        # --- rounding: round to nearest, ties to even ---
        e_r, truncated, rest, round_up = round_mantissa(true_value)
        assert truncated == after[:MANT_BITS]
        if rest == 0:
            case = "В остатке только нули: число представлено точно"
        elif rest < Fraction(1, 2):
            case = "Первый отброшенный бит — 0: сохранённые биты не меняются"
        elif rest > Fraction(1, 2):
            case = "Первый бит — 1, дальше есть единицы: округляем вверх"
        else:
            case = "Ровно посередине: выбираем чётного соседа"
        rule = ru_text("Шаг 4. Округление к ближайшему; при равенстве — к чётному", font_size=28).move_to([0, 0.3, 0])
        case_text = ru_text(case, font_size=26).next_to(rule, DOWN, buff=0.35)
        guard_box = SurroundingRectangle(tail_mobs[0], color=ORANGE, buff=0.04, stroke_width=3)
        self.play(Write(rule))
        self.play(Create(guard_box))
        self.play(FadeIn(case_text))
        self.wait(1.5)

        cross = Line([tail_left, row_y, 0], [7.3, row_y, 0], color=RED, stroke_width=5)
        self.play(Create(cross))
        self.play(FadeOut(tail_mobs), FadeOut(tail_box), FadeOut(cross), FadeOut(guard_box), FadeOut(tail_label))

        if round_up:
            changed = [i for i in range(MANT_BITS) if truncated[i] != m_bits[i]]
            plus_one = ru_text("+1 к младшему разряду", font_size=24, color=ORANGE).next_to(kept_label, DOWN, buff=0.2)
            self.play(FadeIn(plus_one))
            self.play(*[Transform(kept_mobs[i], ru_text(m_bits[i], font=MONO, font_size=14, color=ORANGE).move_to(kept_mobs[i])) for i in changed])
            self.wait(1)
            self.play(FadeOut(plus_one), *[kept_mobs[i].animate.set_color(MANT_COLOR) for i in changed])

        self.play(FadeOut(kept_box), FadeOut(kept_label), FadeOut(rule), FadeOut(case_text))
        self.play(*[kept_mobs[i].animate.move_to(cells[12 + i]) for i in range(MANT_BITS)], run_time=1.5)
        self.play(Circumscribe(cells, color=YELLOW, buff=0.05))
        self.wait(0.5)

        # Decode the displayed fields exactly before presenting the error.
        M = int(m_bits, 2)
        decoded = decode_fields(s_bit, e_bits, m_bits)
        assert decoded == stored
        decode_title = caption("Шаг 5. Восстановим число из сохранённых битов", y=1.4)
        decode_formula = MathTex(
            "x =", "(-1)^{S}", r"\cdot", "2^{E-B}", r"\cdot",
            r"\left(1+\frac{M}{2^{52}}\right)", font_size=36,
        ).set_y(0.55)
        decode_formula[1].set_color(SIGN_COLOR)
        decode_formula[3].set_color(EXP_COLOR)
        decode_formula[5].set_color(MANT_COLOR)
        field_values = MathTex(
            rf"S = {s_bit}", r",\quad", rf"E = {E}", r",\quad",
            rf"B = {BIAS}", r",\quad", rf"M = {M}",
            font_size=30,
        ).set_y(-0.35)
        field_values[0].set_color(SIGN_COLOR)
        field_values[2].set_color(EXP_COLOR)
        field_values[4].set_color(EXP_COLOR)
        field_values[6].set_color(MANT_COLOR)
        format_note = ru_text(
            "B — смещение; 52 — число битов мантиссы; старшая 1 подразумевается.",
            font_size=22, color=GREY_B,
        ).set_y(-1.05)
        weights = [rf"2^{{{MANT_BITS - 1 - i}}}" for i, bit in enumerate(m_bits) if bit == "1"]
        mantissa_sum = VGroup()
        for offset in range(0, len(weights), 9):
            chunk = "+".join(weights[offset:offset + 9])
            chunk = ("M = " if offset == 0 else "+ ") + chunk
            if offset + 9 >= len(weights):
                chunk += rf" = {M}"
            line = MathTex(chunk, font_size=25, color=MANT_COLOR)
            if line.width > 12.8:
                line.scale_to_fit_width(12.8)
            mantissa_sum.add(line)
        mantissa_sum.arrange(DOWN, buff=0.1).set_y(-2.0)
        substitution = MathTex(
            "=", rf"(-1)^{{{s_bit}}}", r"\cdot", rf"2^{{{E}-{BIAS}}}",
            r"\cdot", rf"\left(1+\frac{{{M}}}{{2^{{{MANT_BITS}}}}}\right)", font_size=36,
        ).set_y(-1.25)
        substitution[1].set_color(SIGN_COLOR)
        substitution[3].set_color(EXP_COLOR)
        substitution[5].set_color(MANT_COLOR)
        exact_fraction = MathTex(
            rf"= \frac{{{2**MANT_BITS + M}}}{{2^{{{MANT_BITS - e}}}}}"
            rf"= \frac{{{decoded.numerator}}}{{{decoded.denominator}}}", font_size=36,
        ).set_y(-2.15)
        decimal_result = MathTex(r"= " + exact_decimal(decoded), font_size=32)
        if decimal_result.width > 12.8:
            decimal_result.scale_to_fit_width(12.8)
        decimal_result.set_y(-3.1)
        self.play(FadeIn(decode_title))
        self.play(Write(decode_formula), run_time=2)
        self.play(Write(field_values[1]), Write(field_values[3]), Write(field_values[5]))
        self.play(TransformFromCopy(bit_mobs[0], field_values[0]), run_time=1)
        self.play(TransformFromCopy(bit_mobs[1:12], field_values[2]), run_time=1)
        self.play(Write(field_values[4]), FadeIn(format_note))
        self.play(TransformFromCopy(kept_mobs, field_values[6]), run_time=1.5)
        self.play(Indicate(cells[12:], color=MANT_COLOR), Write(mantissa_sum), run_time=2)
        self.wait(3)
        self.play(FadeOut(mantissa_sum), FadeOut(format_note))
        self.play(Write(substitution[0]), Write(substitution[2]), Write(substitution[4]))
        for part, sources, color in (
            (1, (0,), SIGN_COLOR), (3, (2, 4), EXP_COLOR), (5, (6,), MANT_COLOR),
        ):
            self.play(*[Indicate(field_values[i], color=color) for i in sources], run_time=0.7)
            self.play(TransformFromCopy(decode_formula[part], substitution[part]), run_time=1.3)
        self.play(Write(exact_fraction), run_time=2)
        self.play(Write(decimal_result), run_time=2)
        self.wait(3)
        self.play(*[FadeOut(mob) for mob in (
            decode_title, decode_formula, field_values, substitution, exact_fraction, decimal_result
        )])

        # --- stored value vs true value ---
        error = stored - true_value
        rel = abs(error) / true_value
        eps = Fraction(1, 2**MANT_BITS)
        cap = caption("Шаг 6. Сравним сохранённое число с точным", y=1.4)
        stored_line = MathTex(r"x_{\mathrm{double}} = " + exact_decimal(stored), font_size=34)
        if stored_line.width > 13:
            stored_line.scale_to_fit_width(13)
        true_line = MathTex(rf"x_{{\mathrm{{exact}}}} = {x_str}", font_size=34)
        err_line = MathTex(
            r"\Delta x = x_{\mathrm{double}} - x_{\mathrm{exact}}", r"\approx", sci_tex(error), font_size=38
        )
        err_line[2].set_color(YELLOW)
        rel_line = MathTex(
            r"\delta = \frac{|\Delta x|}{" + x_str + r"} \approx " + sci_tex(rel),
            rf"\approx {float(rel / eps):.2f}\,\varepsilon",
            font_size=34,
        )
        eps_line = MathTex(r"\varepsilon = 2^{-52} \approx " + sci_tex(eps), font_size=34, color=GREY_B)
        note = ru_text("Для нормальных чисел: относительная погрешность ≤ ε/2", font_size=24, color=GREY_B)
        results = VGroup(stored_line, true_line, err_line, rel_line, eps_line, note)
        results.arrange(DOWN, buff=0.32).next_to(cap, DOWN, buff=0.4).set_x(0)

        self.play(FadeIn(cap))
        self.play(Write(stored_line), run_time=2)
        self.play(Write(true_line))
        self.wait(0.5)
        self.play(Write(err_line))
        self.play(Create(SurroundingRectangle(err_line, color=YELLOW, buff=0.12)))
        self.play(Write(rel_line))
        self.play(FadeIn(eps_line), FadeIn(note))
        self.wait(3)