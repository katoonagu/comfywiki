# AGENTS.md

Этот vault работает по паттерну `LLM Wiki`, но домен у него один: `ComfyUI`, `LoRA`, `workflow`, генерация AI-персонажей и смежные практические гайды.

## Mission

Поддерживать Obsidian wiki как производный слой знаний поверх Telegram-архива.

- `comfywiki/result.json` и `comfywiki/files/` являются source of truth.
- Агент никогда не редактирует `comfywiki/`.
- Агент пишет только производные markdown-заметки в `wiki/`.
- Цель wiki: превращать Telegram-архив в usable guides, каталоги и канон знаний, а не копировать чат как есть.

## Current Domain

Активная тематика:

- ComfyUI setup и troubleshooting
- custom nodes и расширения
- workflow для image, video и character generation
- LoRA, checkpoints, model families
- consistency персонажей, multiref, pose, turnaround, realism
- подбор полезных гайдов, PDF, JSON workflow и ссылок

## Vault Layout

- `comfywiki/` содержит исходный Telegram-экспорт и локальные вложения.
- `wiki/` содержит производные заметки и каталоги.
- `wiki/guides/` пошаговые гайды.
- `wiki/workflows/` карточки workflow и workflow-family.
- `wiki/lora/` карточки LoRA.
- `wiki/characters/` знания по генерации персонажей.
- `wiki/models/` модели и model families.
- `wiki/nodes/` custom nodes и расширения ComfyUI.
- `wiki/resources/` ссылки, статьи, PDF и внешние ресурсы.
- `wiki/setup/` установка, update, manager, troubleshooting.
- `wiki/queries/` полезные ответы и сравнения.
- `wiki/sources/telegram/` source notes по выбранным постам из архива.
- `wiki/index.md` главный каталог.
- `wiki/log.md` журнал изменений.
- `templates/` шаблоны для производных заметок.

## Hard Rules

1. Не редактировать `comfywiki/result.json` и ничего внутри `comfywiki/files/`.
2. Всегда отделять raw source от производного знания.
3. Использовать markdown links и кросс-ссылки везде, где это помогает навигации.
4. Явно различать verified facts, community advice, speculation и outdated content.
5. Если утверждение опирается на Telegram-пост или локальный файл, указывать `source_messages` и `source_files`.
6. Основной язык wiki русский, английские названия инструментов, моделей и upstream-проектов сохранять как есть.
7. Предпочитать обновление существующих заметок, а не создание дублей.
8. Приоритет тем: персонажи, LoRA, realism, consistency, workflows, setup, custom nodes.

## Frontmatter

Для заметок внутри `wiki/` использовать YAML frontmatter:

```yaml
---
type: guide|workflow|lora|model|node|resource|source|query|overview
status: seed|curated|needs-review
created: YYYY-MM-DD
updated: YYYY-MM-DD
source_messages:
  - 123
source_files:
  - [[comfywiki/files/example.json]]
topics:
  - Workflows
tags:
  - comfyui
---
```

Поля добавлять только если они реально полезны.

## Ingest Workflow

Когда пользователь просит обработать архив или новый материал:

1. Прочитать `comfywiki/result.json` или указанный локальный файл.
2. Нормализовать текст, ссылки, вложения и topic metadata.
3. Решить, относится ли материал к `guide`, `workflow`, `lora`, `model`, `node`, `resource` или `setup`.
4. Создать или обновить source note в `wiki/sources/telegram/`.
5. Обновить соответствующие каталоги и hub pages.
6. Добавить запись в `wiki/log.md`, если были значимые новые материалы.

## Query Workflow

Когда пользователь задает вопрос:

1. Начинать поиск с `wiki/index.md` и hub pages.
2. Затем читать релевантные производные заметки, а при необходимости идти в source notes.
3. Если ответ полезен повторно, сохранять его в `wiki/queries/`.
4. Не пересказывать весь Telegram-архив, а собирать краткую практическую выжимку.

## Character Generation Workflow

При работе с генерацией персонажей:

1. Отдавать приоритет consistency, turnaround, multiref, pose, realism и workflow связкам.
2. Фиксировать совместимые LoRA, workflow, nodes и модели.
3. Указывать ограничения: VRAM, чувствительность к входным изображениям, требуемые ноды, слабые места likeness.

## Lint Workflow

Периодически проверять:

- дубли страниц про один и тот же workflow или LoRA
- устаревшие рекомендации после новых постов
- страницы без source links
- orphan pages без полезных входящих ссылок
- каталоги, где есть упоминание сущности, но нет отдельной карточки

Исправления должны быть маленькими и точными.
