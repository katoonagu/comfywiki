---
type: source
status: curated
created: 2026-04-06
updated: 2026-04-06
source_messages:
  - 27147
source_files:
  - [[comfywiki/files/interp_00017 (1).mp4]]
topics:
  - Workflows
tags:
  - comfyui
  - lora
  - resource
  - source
  - telegram
  - wan
  - workflow
---

# Multiscene Photoshoot: Softcore Edition LoRA

## Summary

- Источник из Telegram topic: `Workflows`.
- Есть локальный файл: `interp_00017 (1).mp4`.
- Содержит внешние ссылки на модели, ноды или документацию.
- Материал относится к LoRA или использованию LoRA в workflow.
- LoRA для генерации длинного видео сразу (257 кадров) в стиле динамичного фотосета с быстрыми склейками и множеством ракурсов. По ощущениям — fast-cut photoshoot, собранный в один прогон.
- Крайне рекомендуется использовать авторский workflow — без него результат будет заметно хуже.

## Metadata

- Message ID: `27147`
- Date: `2026-01-21T21:07:23`
- Author: `Admin | Smyshnikov`
- Topic: `Workflows`
- Content Type: `workflow`
- Media Kind: `animation`

## Extracted Links

- https://civitai.com/models/2316517/wan-multiscene-photoshoot-softcore-edition?modelVersionId=2606755
- https://civitai.com/api/download/models/2606755?type=Training%20Data

## Related Local Files

- [[comfywiki/files/interp_00017 (1).mp4]]

## Notes

- Multiscene Photoshoot: Softcore Edition LoRA
- LoRA для генерации длинного видео сразу (257 кадров) в стиле динамичного фотосета с быстрыми склейками и множеством ракурсов. По ощущениям — fast-cut photoshoot, собранный в один прогон.
- Крайне рекомендуется использовать авторский workflow — без него результат будет заметно хуже.
- **Как это работает**
- Workflow состоит из двух фаз:
- **Фаза 1 — Low-res предпросмотр**
- — Генерирует 257 кадров в низком разрешении
- — Минимальные требования к VRAM
- — Быстро подбираете удачный seed
- — Ликенесс на этом этапе слабый — это нормально
- **Фаза 2 — High-res финал**
- — Видео делится на 4 части

## Related Pages

- [[resources/Best Guides From Telegram]]
- [[lora/LoRA Catalog]]
- [[lora/LoRA для персонажей]]
- [[workflows/Workflow Catalog]]
- [[models/Models & Nodes]]
