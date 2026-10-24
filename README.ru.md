# IEEE 754 double precision - анимации на Manim

Две короткие анимации о формате double (64 бита): как хранится число 19.59375 и почему 0.3 не хранится точно.

[English](README.md) · [Wiki](https://github.com/SYRRUS-Ali/ieee754-manim/wiki)

![Предварительный просмотр](assets/preview.gif)

## Видео

| Сцена | Что показано | English | Русский |
| --- | --- | --- | --- |
| `BuildDouble` | 19.59375: двоичная запись, нормализация, порядок, мантисса, знак, обратное преобразование | [BuildDouble.mp4](videos/BuildDouble.mp4) | [BuildDoubleRU.mp4](videos/ru/BuildDoubleRU.mp4) |
| `RoundoffError` | 0.3: периодическая дробь, округление и погрешность | [RoundoffError.mp4](videos/RoundoffError.mp4) | [RoundoffErrorRU.mp4](videos/ru/RoundoffErrorRU.mp4) |

Звука в видео нет. Знак показан зелёным, порядок красным, мантисса голубым, отброшенный хвост жёлтым.

## Установка и запуск

Нужны Manim Community 0.22.0, LaTeX с `dvisvgm` и шрифты DejaVu Sans и DejaVu Sans Mono. PowerShell, из папки проекта:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m manim -qh ieee754_scenes.py BuildDouble RoundoffError
.\.venv\Scripts\python.exe -m manim -qh ieee754_scenes_ru.py BuildDoubleRU RoundoffErrorRU
```

Для быстрого просмотра в 480p вместо `-qh` используйте `-pql`. Результат сохраняется в `media/` (в Git не попадает).

## Математика

Нормальное число double: `x = (-1)^S * 2^(E-1023) * (1 + M/2^52)`, где 1 бит знака, 11 бит порядка и 52 бита мантиссы.

```text
19.59375 = 10011.10011 (двоичное) = 1.001110011 * 2^4
S = 0, E = 4 + 1023 = 1027, M = 001110011 и 43 нуля
hex = 0x4033980000000000
```

Двоичная запись 0.3 = 0.0100110011... бесконечна, поэтому биты после 52-го округляются:

```text
хранится = 0.299999999999999988897769753748434595763683319091796875
ошибка   = хранится - 0.3, около -1.1e-17
относительная ошибка около 3.7e-17 (машинный эпсилон 2^-52 около 2.2e-16)
```

## Ограничения

Сцены сделаны под эти два примера. Ноль, subnormal, NaN, бесконечности и другие входные данные не обрабатываются, для других чисел может понадобиться править подписи. Входные числа заданы в начале файлов со сценами.

## Авторы и лицензия

Махмуд А.А., Мехрез М., группа 231-352. [Лицензия MIT](LICENSE).
