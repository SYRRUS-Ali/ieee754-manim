# IEEE 754 double precision - Manim animations

Two short Manim animations about the 64-bit double format: how 19.59375 is stored, and why 0.3 is not stored exactly.

[Русская версия](README.ru.md) · [Wiki](https://github.com/SYRRUS-Ali/ieee754-manim/wiki)

![Animation preview](assets/preview.gif)

## Videos

| Scene | What it shows | English | Russian |
| --- | --- | --- | --- |
| `BuildDouble` | 19.59375: binary form, normalization, exponent, mantissa, sign, and back to decimal | [BuildDouble.mp4](videos/BuildDouble.mp4) | [BuildDoubleRU.mp4](videos/ru/BuildDoubleRU.mp4) |
| `RoundoffError` | 0.3: repeating binary digits, rounding and the error | [RoundoffError.mp4](videos/RoundoffError.mp4) | [RoundoffErrorRU.mp4](videos/ru/RoundoffErrorRU.mp4) |

The videos have no sound. Sign bits are green, exponent red, mantissa light blue and the dropped tail yellow.

## Install and render

Manim Community 0.22.0, LaTeX with `dvisvgm`, and the DejaVu Sans / DejaVu Sans Mono fonts are needed. From PowerShell in the project folder:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m manim -qh ieee754_scenes.py BuildDouble RoundoffError
.\.venv\Scripts\python.exe -m manim -qh ieee754_scenes_ru.py BuildDoubleRU RoundoffErrorRU
```

Use `-pql` instead of `-qh` for a quick 480p preview. Output goes to `media/`, which is ignored by Git.

## Math

A normal double is `x = (-1)^S * 2^(E-1023) * (1 + M/2^52)` with 1 sign bit, 11 exponent bits and 52 mantissa bits.

```text
19.59375 = 10011.10011 (binary) = 1.001110011 * 2^4
S = 0, E = 4 + 1023 = 1027, M = 001110011 and 43 zeros
hex = 0x4033980000000000
```

0.3 = 0.0100110011... in binary never ends, so the bits after the 52nd are rounded away:

```text
stored = 0.299999999999999988897769753748434595763683319091796875
error  = stored - 0.3 = about -1.1e-17
relative error = about 3.7e-17 (machine epsilon 2^-52 is about 2.2e-16)
```

## Limits

The scenes are made for these two examples. Zero, subnormals, NaN, infinity and other inputs are not handled, and other numbers may need changes to the captions. The input values are at the top of the scene files.

## Authors and license

Ali Makhmud and Mohamad Mehrez, group 231-352. [MIT License](LICENSE).
