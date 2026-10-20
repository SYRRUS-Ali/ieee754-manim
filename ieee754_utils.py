import struct
from decimal import Decimal, localcontext
from fractions import Fraction

BIAS = 1023
MANT_BITS = 52


def double_bits(x):
    # the 64 bits of x as a string, bit 63 first
    (n,) = struct.unpack(">Q", struct.pack(">d", x))
    return format(n, "064b")


def bits_to_double(bits):
    return struct.unpack(">d", struct.pack(">Q", int(bits, 2)))[0]


def split_fields(bits):
    return bits[0], bits[1:12], bits[12:]


def decode_fields(sign, exp_bits, mant_bits):
    # F = (-1)^S * 2^(E-1023) * (1 + M/2^52), done exactly (normal numbers only)
    e = int(exp_bits, 2) - BIAS
    m = Fraction(int(mant_bits, 2), 2**MANT_BITS)
    return (-1) ** int(sign) * Fraction(2) ** e * (1 + m)


def binary_expansion(value, frac_digits):
    # value is a non-negative Fraction; the fraction part is cut after frac_digits bits
    int_part = value.numerator // value.denominator
    frac = value - int_part
    digits = ""
    for _ in range(frac_digits):
        frac *= 2
        if frac >= 1:
            digits += "1"
            frac -= 1
        else:
            digits += "0"
    return format(int_part, "b"), digits


def exact_frac_length(value, limit):
    # how many binary fraction digits are needed to write value exactly (at most limit)
    frac = value - value.numerator // value.denominator
    n = 0
    while frac != 0 and n < limit:
        frac = frac * 2 - int(frac * 2)
        n += 1
    return max(n, 1)


def normalize(int_bits, frac_bits):
    # returns the exponent e (so that value = 1.xxx * 2^e) and the index of the leading 1
    digits = int_bits + frac_bits
    lead = digits.index("1")
    return len(int_bits) - 1 - lead, lead


def times_two_steps(frac, max_steps):
    # the "multiply by 2" method; stops when the fraction becomes 0 or starts repeating
    steps = []
    seen = []
    while len(steps) < max_steps and frac != 0:
        product = frac * 2
        digit = int(product)
        repeats = frac in seen
        steps.append((frac, product, digit, repeats))
        if repeats:
            break
        seen.append(frac)
        frac = product - digit
    return steps


def round_mantissa(value):
    # round a positive Fraction to 52 mantissa bits (round to nearest, ties to even)
    e = value.numerator.bit_length() - value.denominator.bit_length()
    if Fraction(2) ** e > value:
        e -= 1
    scaled = (value / Fraction(2) ** e - 1) * 2**MANT_BITS
    truncated = scaled.numerator // scaled.denominator
    rest = scaled - truncated  # the dropped part, in units of the last kept bit
    if rest > Fraction(1, 2):
        round_up = True
    elif rest == Fraction(1, 2):
        round_up = truncated % 2 == 1
    else:
        round_up = False
    return e, format(truncated, "052b"), rest, round_up


def exact_decimal(value):
    # exact decimal string of a Fraction whose denominator is 2^a * 5^b
    with localcontext() as ctx:
        ctx.prec = 2000
        d = Decimal(value.numerator) / Decimal(value.denominator)
    s = format(d, "f")
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s


def to_decimal(value, digits=60):
    with localcontext() as ctx:
        ctx.prec = digits
        return Decimal(value.numerator) / Decimal(value.denominator)


def sci_tex(value, digits=2):
    # Fraction -> LaTeX like "-1.1 \cdot 10^{-17}"
    mant, exp = format(to_decimal(value), f".{digits - 1}e").split("e")
    return rf"{mant} \cdot 10^{{{int(exp)}}}"


def weight_str(k):
    # 2^-k written as a decimal, e.g. 3 -> "0.125"
    return exact_decimal(Fraction(1, 2**k))