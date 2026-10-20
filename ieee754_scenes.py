from fractions import Fraction

from manim import *

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
    weight_str,
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
MONO = "DejaVu Sans Mono"


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
        Text("63", font_size=16).next_to(cells[0], UP, buff=0.1).align_to(cells[0], RIGHT).shift(LEFT * 0.03),
        Text("62", font_size=16).next_to(cells[1], UP, buff=0.1).align_to(cells[1], LEFT).shift(RIGHT * 0.03),
        Text("51", font_size=16).next_to(cells[12], UP, buff=0.1).align_to(cells[12], LEFT),
        Text("0", font_size=16).next_to(cells[63], UP, buff=0.1).align_to(cells[63], RIGHT),
    )

    names = VGroup(
        Text("Sign", font_size=22, color=SIGN_COLOR).align_to(cells[0], LEFT),
        Text("Exponent", font_size=22, color=EXP_COLOR),
        Text("Mantissa", font_size=22, color=MANT_COLOR).set_x(fields[2].get_x()),
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
        label = Text("64", font_size=20).move_to(arrow)
        label.add_background_rectangle(opacity=1, buff=0.08)
        deco.add(VGroup(ticks, arrow, label))
    return cells, deco


def cell_digits(bits, cells, font_size):
    return VGroup(*[Text(b, font=MONO, font_size=font_size).move_to(c) for b, c in zip(bits, cells)])


def caption(text, y=0.55):
    return Text(text, font_size=28).to_edge(LEFT, buff=0.6).set_y(y)


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
        digit_mobs.add(Text(d, font=MONO, font_size=36, color=digit_color).move_to(bottom))
        x += col_w
    boxes.set_stroke(GREY_B, 1.5)
    heads = VGroup(*headers)
    table = VGroup(boxes, heads, digit_mobs)
    if point is not None:
        table.add(point)
    return table, heads, digit_mobs, point


class BuildDouble(Scene):
    def construct(self):
        value = Fraction(SCENE1_NUMBER)
        x = float(SCENE1_NUMBER)
        bits = double_bits(x)
        s_bit, e_bits, m_bits = split_fields(bits)
        E = int(e_bits, 2)
        x_str = exact_decimal(abs(value))

        # --- intro and the empty 64-bit layout ---
        title = Text("IEEE-754 double precision (64 bit)", font_size=44)
        authors = Text("Ali Makhmud, Mohamad Mehrez  |  group 352", font_size=24, color=GREY_B)
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
        header_strs = [str(2**k) for k in range(len(int_bits) - 1, -1, -1)]
        header_strs += [weight_str(k) for k in range(1, len(frac_bits) + 1)]
        headers = [Text(h, font_size=24) for h in header_strs]
        table, heads, digit_mobs, point = place_value_table(headers, digits, point_after=len(int_bits))
        table.move_to([0, -0.9, 0])

        cap = caption(f"1.  Write {x_str} in binary")
        self.play(FadeIn(cap))
        self.play(Create(table[0]), FadeIn(heads), run_time=1.5)
        self.play(LaggedStart(*[FadeIn(d, shift=DOWN * 0.2) for d in digit_mobs], lag_ratio=0.15), FadeIn(point))

        ones = [i for i, d in enumerate(digits) if d == "1"]
        self.play(*[heads[i].animate.set_color(YELLOW) for i in ones], *[digit_mobs[i].animate.set_color(YELLOW) for i in ones])
        sum_line = MathTex(" + ".join(header_strs[i] for i in ones) + f" = {x_str}", font_size=36)
        sum_line.next_to(table, DOWN, buff=0.45)
        bin_line = MathTex(rf"{x_str} = {int_bits}.{frac_bits}_2", font_size=40).next_to(sum_line, DOWN, buff=0.35)
        self.play(Write(sum_line))
        self.play(Write(bin_line))
        self.wait(2)
        self.play(FadeOut(table), FadeOut(sum_line), FadeOut(cap), FadeOut(bin_line))

        # --- step 2: normalize by moving the binary point ---
        e, lead = normalize(int_bits, frac_bits)
        cap = caption("2.  Normalize: move the point so that one 1 is left of it")
        row = VGroup(*[Text(d, font=MONO, font_size=44) for d in digits])
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

        rest = digits[lead + 1:].rstrip("0") or "0"
        norm_line = MathTex(f"{x_str} =", "1.", f"{rest}_2", rf"\cdot\, 2^{{{e}}}", font_size=40)
        norm_line.next_to(row, DOWN, buff=0.6)
        norm_line[2].set_color(MANT_COLOR)
        norm_line[3].set_color(EXP_COLOR)
        self.play(Write(norm_line))
        self.wait(1.5)

        # keep the normalized form as a reference for the next steps
        self.play(FadeOut(row[lead:]), FadeOut(dot), FadeOut(exp_label), FadeOut(cap),
                  norm_line.animate.move_to([0, -0.15, 0]))

        # --- step 3: biased exponent ---
        assert E == e + BIAS
        cap = caption("3.  Exponent:  E = e + 1023", y=0.55)
        e_line = MathTex(f"E = {e} + {BIAS} = {E} =", font_size=40)
        e_digits = VGroup(*[Text(b, font=MONO, font_size=36, color=EXP_COLOR) for b in e_bits])
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
        m_heads = [MathTex(f"2^{{-{k}}}", font_size=32) for k in range(1, n + 1)]
        m_table, _, m_digit_mobs, _ = place_value_table(m_heads, m_bits[:n], col_w=0.8, digit_color=MANT_COLOR)
        m_table.move_to([0, -1.55, 0])
        m_frac = Fraction(int(m_bits, 2), 2**MANT_BITS)
        m_line = MathTex(rf"\frac{{M}}{{2^{{52}}}} = 0.{shown}_2 = {exact_decimal(m_frac)}", font_size=36)
        m_line.next_to(m_table, DOWN, buff=0.35)

        cap = caption("4.  Mantissa: the bits after the leading 1", y=0.55)
        self.play(FadeIn(cap), Indicate(norm_line[2], color=MANT_COLOR))
        self.play(Create(m_table[0]), FadeIn(m_table[1]))
        self.play(TransformFromCopy(norm_line[2][:n], m_digit_mobs), run_time=1.5)
        self.play(LaggedStart(*[TransformFromCopy(m_digit_mobs[i], bit_mobs[12 + i]) for i in range(n)], lag_ratio=0.1), run_time=2)
        zeros_note = Text(f"the other {MANT_BITS - n} bits are 0", font_size=24, color=GREY_B)
        zeros_note.next_to(cap, RIGHT, buff=0.6)
        self.play(LaggedStart(*[FadeIn(b) for b in bit_mobs[12 + n:]], lag_ratio=0.02), FadeIn(zeros_note), run_time=1.5)
        self.play(Write(m_line))
        self.wait(1.5)
        self.play(FadeOut(cap), FadeOut(zeros_note), FadeOut(m_table), FadeOut(m_line))

        # --- step 5: sign ---
        cap = caption("5.  Sign", y=0.55)
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
        cap = caption("6.  Back to decimal: plug S, E, M into the formula", y=0.55)
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
            rf"= {(-1) ** int(s_bit)} \cdot {exact_decimal(power)} \cdot {exact_decimal(1 + m_frac)}", font_size=40
        ).next_to(line1, DOWN, buff=0.3)
        line3 = MathTex(f"= {exact_decimal(decoded)}", font_size=48).next_to(line2, DOWN, buff=0.3)
        self.play(Write(line1), run_time=1.5)
        self.play(Write(line2))
        self.play(Write(line3))
        self.play(Create(SurroundingRectangle(line3, color=YELLOW, buff=0.15)))
        hex_note = Text(f"hex: 0x{int(bits, 2):016X}", font=MONO, font_size=22, color=GREY_B)
        hex_note.to_corner(DR, buff=0.4)
        self.play(FadeIn(hex_note))
        self.wait(3)


class RoundoffError(Scene):
    def construct(self):
        true_value = Fraction(SCENE2_NUMBER)
        x = float(SCENE2_NUMBER)
        stored = Fraction(x)
        bits = double_bits(x)
        s_bit, e_bits, m_bits = split_fields(bits)
        E = int(e_bits, 2)
        x_str = exact_decimal(true_value)

        # --- intro ---
        title = Text("Roundoff error", font_size=48).to_edge(UP, buff=0.8)
        big = MathTex(f"x = {x_str}", font_size=96)
        question = Text("Simple in decimal. What does the computer actually store?", font_size=28, color=GREY_B)
        question.next_to(big, DOWN, buff=0.7)
        self.play(Write(title))
        self.play(Write(big))
        self.play(FadeIn(question))
        self.wait(1.5)
        self.play(FadeOut(title), FadeOut(question), FadeOut(big))

        # --- multiply by 2 method for the fraction part ---
        int_part = true_value.numerator // true_value.denominator
        cap = Text("Fraction part to binary: multiply by 2, the integer part is the next bit", font_size=26)
        cap.to_edge(UP, buff=0.6)
        steps = times_two_steps(true_value - int_part, 8)
        lines = VGroup()
        for frac, product, digit, _ in steps:
            line = MathTex(
                rf"{exact_decimal(frac)} \cdot 2 = {exact_decimal(product)}", r"\;\rightarrow\;", str(digit),
                font_size=38,
            )
            line[2].set_color(YELLOW)
            lines.add(line)
        lines.arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to([-1.5, -0.4, 0])
        self.play(FadeIn(cap))
        for line in lines:
            self.play(FadeIn(line, shift=DOWN * 0.1), run_time=0.6)
        bits_so_far = "".join(str(d) for _, _, d, _ in steps)
        collected = MathTex(rf"{x_str} = {int_part}.{bits_so_far}\ldots_2", font_size=40, color=YELLOW)
        collected.next_to(lines, RIGHT, buff=1.0)
        if steps and steps[-1][3]:
            # the fraction came back to an earlier value, so the bits repeat forever
            first = next(i for i, s in enumerate(steps) if s[0] == steps[-1][0])
            boxes = VGroup(
                SurroundingRectangle(lines[first][0], color=ORANGE, buff=0.06),
                SurroundingRectangle(lines[-1][0], color=ORANGE, buff=0.06),
            )
            repeat_note = Text("same value again: the bits repeat forever", font_size=24, color=ORANGE)
            repeat_note.next_to(lines, DOWN, buff=0.35).align_to(lines, LEFT)
            self.play(Create(boxes), FadeIn(repeat_note))
        else:
            boxes = VGroup()
            repeat_note = VGroup()
        self.play(Write(collected))
        self.wait(2)
        self.play(FadeOut(cap), FadeOut(lines), FadeOut(boxes), FadeOut(repeat_note), FadeOut(collected))

        # --- long binary row, more bits than a double can hold ---
        int_bits, frac_bits = binary_expansion(true_value, SCENE2_FRAC_BITS)
        digits = int_bits + frac_bits
        spacing = 0.3
        row = VGroup(*[Text(d, font=MONO, font_size=30) for d in digits])
        for i, d in enumerate(row):
            d.move_to([-6.2 + i * spacing + (0.15 if i >= len(int_bits) else 0), 0.3, 0])

        def point_at(k):
            return [(row[k - 1].get_x() + row[k].get_x()) / 2, row[0].get_bottom()[1] + 0.05, 0]

        dot = Dot(radius=0.05).move_to(point_at(len(int_bits)))
        cap = Text(f"{x_str} in binary, {SCENE2_FRAC_BITS} bits after the point (and it never ends)", font_size=26)
        cap.to_edge(UP, buff=0.6)
        self.play(FadeIn(cap))
        self.play(FadeIn(row[: len(int_bits)]), FadeIn(dot))
        self.play(LaggedStart(*[FadeIn(d) for d in row[len(int_bits):]], lag_ratio=0.03), run_time=3)
        self.play(VGroup(row, dot).animate.shift(LEFT * 14), run_time=2.5)
        self.play(VGroup(row, dot).animate.shift(RIGHT * 14), run_time=1.5)

        # --- normalize ---
        e, lead = normalize(int_bits, frac_bits)
        new_cap = Text("Normalize: move the point so that one 1 is left of it", font_size=26)
        new_cap.move_to(cap)
        self.play(Transform(cap, new_cap))
        k = len(int_bits)
        step = -1 if k > lead + 1 else 1
        while k != lead + 1:
            k += step
            self.play(dot.animate.move_to(point_at(k)), run_time=0.5)
        if lead > 0:
            self.play(FadeOut(row[:lead]))
        after = digits[lead + 1:]
        norm_line = MathTex(f"{x_str} = 1.", rf"{after[:12]}\ldots_2", rf"\cdot\, 2^{{{e}}}", font_size=40)
        norm_line[1].set_color(MANT_COLOR)
        norm_line[2].set_color(EXP_COLOR)
        norm_line.move_to([0, -0.7, 0])
        self.play(Write(norm_line))
        self.wait(1)

        # --- the 64-bit grid, exponent and sign ---
        self.play(FadeOut(cap))
        cell_w = 0.18
        cells, deco = make_bar(cell_w, -6.8, 2.6, with_dimension=False)
        self.play(LaggedStart(*[FadeIn(c) for c in cells], lag_ratio=0.02), FadeIn(deco), run_time=1.5)
        bit_mobs = cell_digits(bits, cells, 14)

        assert E == e + BIAS
        e_line = MathTex(f"E = {e} + {BIAS} = {E} =", font_size=36)
        e_digits = VGroup(*[Text(b, font=MONO, font_size=32, color=EXP_COLOR) for b in e_bits]).arrange(RIGHT, buff=0.07)
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
        self.play(FadeOut(e_line), FadeOut(e_digits), FadeOut(s_line), FadeOut(norm_line))

        # --- lay the bits after the leading 1 under the mantissa field ---
        row_y = 2.0
        small = VGroup()
        for i, d in enumerate(row):
            pos = i - lead - 1  # position after the leading 1
            small.add(Text(digits[i], font=MONO, font_size=14).move_to([cells[12].get_x() + pos * cell_w, row_y, 0]))
        small_dot = Dot(radius=0.03).move_to([cells[12].get_left()[0], small[0].get_bottom()[1] + 0.03, 0])
        self.play(
            *[Transform(row[i], small[i]) for i in range(lead, len(row))],
            dot.animate.move_to(small_dot.get_center()).scale(0.6),
            run_time=2,
        )
        lead_note = Text("leading 1 is not stored", font_size=20, color=GREY_B)
        lead_note.next_to(row[lead], DOWN, buff=0.3).align_to(cells[0], LEFT)
        self.play(FadeIn(lead_note), Indicate(row[lead]))
        self.play(FadeOut(row[lead]), FadeOut(dot), FadeOut(lead_note))

        kept_mobs = row[lead + 1: lead + 1 + MANT_BITS]
        tail_mobs = row[lead + 1 + MANT_BITS:]
        kept_box = SurroundingRectangle(kept_mobs, color=MANT_COLOR, buff=0.05)
        tail_left = cells[63].get_right()[0]
        tail_box = Rectangle(width=8, height=kept_box.height)
        tail_box.set_stroke(TAIL_COLOR, 2).set_fill(TAIL_COLOR, 0.15)
        tail_box.move_to([tail_left + 4 + 0.02, row_y, 0])
        kept_label = Text(f"{MANT_BITS} bits fit into the mantissa", font_size=22, color=MANT_COLOR)
        kept_label.next_to(kept_box, DOWN, buff=0.2)
        tail_label = Text("tail", font_size=24, color=TAIL_COLOR).next_to(tail_box, DOWN, buff=0.2)
        tail_label.set_x((tail_left + 7.1) / 2)
        self.play(Create(kept_box), FadeIn(kept_label))
        self.play(FadeIn(tail_box), FadeIn(tail_label))
        self.wait(1)

        # --- rounding: round to nearest, ties to even ---
        e_r, truncated, rest, round_up = round_mantissa(true_value)
        assert truncated == after[:MANT_BITS]
        if rest == 0:
            case = "the tail is all zeros, nothing is lost"
        elif rest < Fraction(1, 2):
            case = "first dropped bit is 0  ->  round down, kept bits stay the same"
        elif rest > Fraction(1, 2):
            case = "first dropped bit is 1 and the rest is not 0  ->  round up"
        else:
            case = "exactly half way  ->  round to the even neighbour"
        rule = Text("Round to nearest, ties to even", font_size=30).move_to([0, 0.3, 0])
        case_text = Text(case, font_size=26).next_to(rule, DOWN, buff=0.35)
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
            plus_one = Text("+1 in the last place", font_size=24, color=ORANGE).next_to(kept_label, DOWN, buff=0.2)
            self.play(FadeIn(plus_one))
            self.play(*[Transform(kept_mobs[i], Text(m_bits[i], font=MONO, font_size=14, color=ORANGE).move_to(kept_mobs[i])) for i in changed])
            self.wait(1)
            self.play(FadeOut(plus_one), *[kept_mobs[i].animate.set_color(WHITE) for i in changed])

        self.play(FadeOut(kept_box), FadeOut(kept_label), FadeOut(rule), FadeOut(case_text))
        self.play(*[kept_mobs[i].animate.move_to(cells[12 + i]) for i in range(MANT_BITS)], run_time=1.5)
        self.play(Circumscribe(cells, color=YELLOW, buff=0.05))
        self.wait(0.5)

        # --- stored value vs true value ---
        error = stored - true_value
        rel = abs(error) / true_value
        eps = Fraction(1, 2**MANT_BITS)
        cap = caption("What is actually stored", y=1.4)
        stored_line = MathTex(r"\text{stored} = " + exact_decimal(stored), font_size=34)
        if stored_line.width > 13:
            stored_line.scale_to_fit_width(13)
        true_line = MathTex(rf"\text{{true}} = {x_str}", font_size=34)
        err_line = MathTex(
            r"\text{Roundoff error} = \text{stored} - \text{true}", r"\approx", sci_tex(error), font_size=38
        )
        err_line[2].set_color(YELLOW)
        rel_line = MathTex(
            r"\text{relative error} = \frac{|\text{error}|}{" + x_str + r"} \approx " + sci_tex(rel),
            rf"\approx {float(rel / eps):.2f}\,\varepsilon",
            font_size=34,
        )
        eps_line = MathTex(r"\varepsilon = 2^{-52} \approx " + sci_tex(eps), font_size=34, color=GREY_B)
        note = Text("round to nearest keeps the relative error below ε/2", font_size=24, color=GREY_B)
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