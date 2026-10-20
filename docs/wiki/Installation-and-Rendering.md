# Установка и рендер

Нужны совместимый Python, `manim==0.22.0`, LaTeX с `dvisvgm`, шрифты DejaVu Sans и DejaVu Sans Mono. PowerShell из корня основного проекта:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m manim checkhealth
.\.venv\Scripts\python.exe -m manim -pql ieee754_scenes_ru.py BuildDoubleRU RoundoffErrorRU
```

После проверки предварительного просмотра:

```powershell
.\.venv\Scripts\python.exe -m manim -qh ieee754_scenes_ru.py BuildDoubleRU RoundoffErrorRU
```

Стандартный каталог: `media/videos/ieee754_scenes_ru/1080p60/`. Полностью просмотреть оба ролика и скопировать выбранные MP4 в `videos/ru/`. Команды копирования приведены в основном README. Для английского рендера использовать `ieee754_scenes.py BuildDouble RoundoffError`.

Рендер не создаёт озвучку. Наличие исходника не означает наличия проверенного MP4.

[Официальная установка Manim](https://docs.manim.community/en/stable/installation/uv.html)

[[Решение проблем|Troubleshooting]]
