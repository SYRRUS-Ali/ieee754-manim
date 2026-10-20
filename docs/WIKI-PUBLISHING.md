# Публикация GitHub Wiki вручную

Страницы находятся в `docs/wiki/`. Основной репозиторий и Wiki — отдельные Git-репозитории: обычный push проекта не публикует Wiki.

1. На GitHub открыть Settings → General → Features и включить Wikis, если функция доступна.
2. Во вкладке Wiki вручную создать первую страницу Home. Кнопка Save Page создаёт изменение в Wiki; это действие выполняет владелец.
3. Из корня основного проекта:

```powershell
git clone https://github.com/SYRRUS-Ali/ieee754-manim.wiki.git ../ieee754-manim.wiki
Copy-Item -Path ./docs/wiki/*.md -Destination ../ieee754-manim.wiki/
Set-Location ../ieee754-manim.wiki
git status --short
git diff
```

Копирование заменяет одноимённые страницы. Если Wiki уже содержит полезные материалы, сначала сравнить и объединить вручную. Не клонировать в существующий каталог: использовать имеющийся checkout после проверки его состояния.

4. Только после проверки владелец вручную выполняет:

```powershell
git add -- Home.md IEEE-754-Theory.md BuildDouble.md RoundoffError.md Installation-and-Rendering.md Utilities.md Russian-Version.md Troubleshooting.md Roadmap.md _Sidebar.md _Footer.md
git diff --cached
git commit -m "docs: publish Russian IEEE 754 project wiki"
git push
```

Убедиться, что текущая ветка — default branch Wiki: публикуется именно она. После публикации проверить страницы, формулы, ссылки и боковую панель.

Эти команды приведены для ручного запуска. Автоматически commit, push и публикация не выполнялись. Ссылки `[[подпись|страница]]` предназначены для GitHub Wiki.

[Официальная инструкция GitHub](https://docs.github.com/en/communities/documenting-your-project-with-wikis/adding-or-editing-wiki-pages)
