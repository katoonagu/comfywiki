# ComfyUI Wiki для Obsidian

Этот vault теперь настроен как wiki по `ComfyUI`, `LoRA`, `workflow`, генерации AI-персонажей и related guides.

## Source Layer

- `comfywiki/result.json` — экспорт Telegram-группы
- `comfywiki/files/` — локальные JSON workflow, PDF, изображения, архивы и прочие вложения

Это неизменяемый source layer. Агент читает его, но не переписывает.

## Knowledge Layer

- `wiki/guides/` — пошаговые гайды
- `wiki/workflows/` — карточки workflow
- `wiki/lora/` — каталог LoRA
- `wiki/characters/` — генерация персонажей, consistency, pose, multiref
- `wiki/models/` — модели и model families
- `wiki/nodes/` — custom nodes
- `wiki/resources/` — полезные ссылки, PDF и каталоги
- `wiki/setup/` — установка и troubleshooting
- `wiki/sources/telegram/` — source notes по выбранным постам

## Как пользоваться

1. Открой vault в Obsidian.
2. Используй `wiki/index.md` как главный вход.
3. Пиши мне в чат:
   - `найди лучший workflow для consistency персонажа`
   - `собери гайд по Flux Kontext`
   - `вытащи полезные LoRA из telegram-архива`
   - `сравни workflow для turnaround sheet`
4. Смотри каталоги, hub pages и Graph View.

## Что уже сделано

- Активная тема vault переведена на ComfyUI wiki.
- Добавлен curated import pipeline для Telegram-архива.
- Созданы стартовые hub pages и каталоги.
- Источник и производный слой теперь разделены.
