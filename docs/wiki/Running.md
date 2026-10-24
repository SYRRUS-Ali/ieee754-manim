# Запуск

Нужны Manim Community 0.22.0, LaTeX с `dvisvgm`, шрифты DejaVu Sans и DejaVu Sans Mono. PowerShell, из папки проекта:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m manim -pql ieee754_scenes.py BuildDouble RoundoffError
.\.venv\Scripts\python.exe -m manim -qh ieee754_scenes_ru.py BuildDoubleRU RoundoffErrorRU
```

`-pql` - быстрый просмотр 480p, `-qh` - финальное качество 1080p. Результат лежит в `media/videos/`.

Если нет `latex` или `dvisvgm`, проверьте установку LaTeX (например, MiKTeX) и PATH. Если кириллица отображается квадратами, установите DejaVu Sans.
