from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE_JSON = ROOT / "comfywiki" / "result.json"
WIKI_DIR = ROOT / "wiki"
SOURCE_NOTES_DIR = WIKI_DIR / "sources" / "telegram"
MANIFEST_PATH = SOURCE_NOTES_DIR / "curated-manifest.json"

ALLOWED_TOPICS = {"Workflows", "Ваши Гайды", "Ресурсы", "Чат ComfyUI"}
KEYWORD_GROUPS = {
    "workflow": ["workflow", ".json", "json", "wan", "qwen image", "flux kontext"],
    "lora": ["#lora", " lora", "lora "],
    "setup": ["установ", "custom nodes", "manager", "обновл", "ошибка", "install", "setup"],
    "character": [
        "персонаж",
        "character",
        "consistency",
        "multiref",
        "turnaround",
        "pose",
        "realism",
        "ultrareal",
        "likeness",
    ],
    "resource": ["github.com", "civitai.com", "huggingface.co", ".pdf", ".zip"],
}
LINK_HINTS = ("github.com", "civitai.com", "huggingface.co", "comfyanonymous.github.io")
EXT_TO_KIND = {
    ".json": "workflow",
    ".pdf": "resource",
    ".zip": "resource",
    ".png": "resource",
    ".jpg": "resource",
    ".jpeg": "resource",
    ".webp": "resource",
    ".mp4": "workflow",
    ".gif": "workflow",
}
SLUG_OVERRIDES = {
    633: "flux-kontext-character-turnaround",
    1100: "lenovo-ultrareal-lora",
    3487: "wan-2-2-low-vram-video-workflow",
    4237: "vnccs-consistent-character-suite",
    5589: "lanpaint-node-and-installation",
    8565: "quick-connections-node",
    27147: "multiscene-photoshoot-softcore-edition-lora",
}
MANUAL_PRIORITY_IDS = [633, 1100, 3487, 4237, 5589, 8565, 27147]


@dataclass
class NormalizedMessage:
    message_id: int
    date: str
    author: str
    topic: str
    text_markdown: str
    links: list[str]
    local_files: list[str]
    media_kind: str
    tags_detected: list[str]
    content_type_guess: str
    file_name: str
    mime_type: str
    title: str
    score: int


def load_export() -> dict[str, Any]:
    with SOURCE_JSON.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def flatten_text(value: Any) -> str:
    if isinstance(value, str):
        return value.strip()
    if not isinstance(value, list):
        return ""

    parts: list[str] = []
    for item in value:
        if isinstance(item, str):
            parts.append(item)
        elif isinstance(item, dict):
            text = item.get("text", "")
            kind = item.get("type")
            href = item.get("href")
            if kind == "link" and href:
                parts.append(f"[{text or href}]({href})")
            elif kind == "bold" and text:
                parts.append(f"**{text}**")
            elif kind == "italic" and text:
                parts.append(f"*{text}*")
            elif kind == "code" and text:
                parts.append(f"`{text}`")
            else:
                parts.append(text)
    return "".join(parts).strip()


def strip_markup(value: str) -> str:
    value = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", value)
    value = value.replace("**", "").replace("*", "").replace("`", "")
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def extract_links(msg: dict[str, Any], flat_text: str) -> list[str]:
    links: list[str] = []
    for entity in msg.get("text_entities", []):
        if isinstance(entity, dict):
            href = entity.get("href")
            text = entity.get("text")
            if href:
                links.append(str(href))
            elif isinstance(text, str) and text.startswith("http"):
                links.append(text)
    links.extend(re.findall(r"https?://[^\s)\]]+", flat_text))
    deduped: list[str] = []
    for link in links:
        if link not in deduped:
            deduped.append(link)
    return deduped


def extract_local_files(msg: dict[str, Any]) -> list[str]:
    files: list[str] = []
    for key in ("file", "file_name", "photo", "thumbnail"):
        value = msg.get(key)
        if not isinstance(value, str) or not value:
            continue
        if value.startswith("(File not included"):
            continue
        if value.startswith("files/"):
            files.append(value)
        elif key == "file_name":
            files.append(f"files/{value}")
        else:
            files.append(value)
    deduped: list[str] = []
    for file_path in files:
        if file_path not in deduped:
            deduped.append(file_path)
    return deduped


def infer_media_kind(msg: dict[str, Any]) -> str:
    if msg.get("media_type"):
        return str(msg["media_type"])
    if msg.get("mime_type"):
        return str(msg["mime_type"]).split("/")[0]
    if msg.get("photo"):
        return "photo"
    return "text"


def infer_title(flat_text: str, file_name: str, message_id: int) -> str:
    for line in flat_text.splitlines():
        clean = strip_markup(line.strip().strip("#").strip())
        if clean:
            return clean[:120]
    if file_name:
        return Path(file_name).stem
    return f"Message {message_id}"


def detect_tags(flat_text: str, file_name: str, links: list[str]) -> list[str]:
    low = " ".join([flat_text.lower(), file_name.lower(), " ".join(links).lower()])
    tags: list[str] = []
    for tag, keywords in KEYWORD_GROUPS.items():
        if any(keyword in low for keyword in keywords):
            tags.append(tag)
    if "qwen" in low:
        tags.append("qwen")
    if "flux" in low:
        tags.append("flux")
    if "wan" in low:
        tags.append("wan")
    if "custom_nodes" in low or "custom nodes" in low:
        tags.append("custom_nodes")
    if "realism" in low or "ultrareal" in low:
        tags.append("realism")
    if "turnaround" in low:
        tags.append("turnaround")
    if "consistency" in low:
        tags.append("consistency")
    return sorted(set(tags))


def infer_content_type(file_name: str, tags: list[str], topic: str) -> str:
    suffix = Path(file_name).suffix.lower()
    if suffix in EXT_TO_KIND:
        return EXT_TO_KIND[suffix]
    if "setup" in tags or "custom_nodes" in tags:
        return "node" if "custom_nodes" in tags else "guide"
    if "lora" in tags and "workflow" not in tags:
        return "lora"
    if "lora" in tags and not file_name:
        return "lora"
    if "workflow" in tags:
        return "workflow"
    if "lora" in tags:
        return "lora"
    if topic == "Ресурсы":
        return "resource"
    return "guide"


def score_message(topic: str, tags: list[str], links: list[str], local_files: list[str], file_name: str) -> int:
    score = 0
    if topic in ALLOWED_TOPICS:
        score += 8
    if any(tag in tags for tag in ("workflow", "lora", "setup", "character", "resource")):
        score += 4
    if any(domain in " ".join(links) for domain in LINK_HINTS):
        score += 3
    if local_files:
        score += 3
    suffix = Path(file_name).suffix.lower()
    if suffix in {".json", ".pdf", ".zip", ".mp4"}:
        score += 4
    if "character" in tags or "consistency" in tags or "turnaround" in tags:
        score += 3
    return score


def slugify(value: str, fallback: str) -> str:
    value = value.lower()
    repl = {
        "а": "a",
        "б": "b",
        "в": "v",
        "г": "g",
        "д": "d",
        "е": "e",
        "ё": "e",
        "ж": "zh",
        "з": "z",
        "и": "i",
        "й": "y",
        "к": "k",
        "л": "l",
        "м": "m",
        "н": "n",
        "о": "o",
        "п": "p",
        "р": "r",
        "с": "s",
        "т": "t",
        "у": "u",
        "ф": "f",
        "х": "h",
        "ц": "ts",
        "ч": "ch",
        "ш": "sh",
        "щ": "sch",
        "ъ": "",
        "ы": "y",
        "ь": "",
        "э": "e",
        "ю": "yu",
        "я": "ya",
    }
    value = "".join(repl.get(char, char) for char in value)
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value or fallback


def normalize_messages(data: dict[str, Any]) -> list[NormalizedMessage]:
    msgs = data["messages"]
    topic_titles = {
        msg["id"]: msg.get("title", "")
        for msg in msgs
        if msg.get("type") == "service" and msg.get("action") == "topic_created"
    }
    normalized: list[NormalizedMessage] = []
    for msg in msgs:
        if msg.get("type") == "service":
            continue
        topic = topic_titles.get(msg.get("reply_to_message_id"), "")
        flat_text = flatten_text(msg.get("text", ""))
        links = extract_links(msg, flat_text)
        local_files = extract_local_files(msg)
        file_name = str(msg.get("file_name", ""))
        tags = detect_tags(flat_text, file_name, links)
        content_type = infer_content_type(file_name, tags, topic)
        title = infer_title(flat_text, file_name, int(msg["id"]))
        score = score_message(topic, tags, links, local_files, file_name)
        normalized.append(
            NormalizedMessage(
                message_id=int(msg["id"]),
                date=str(msg.get("date", "")),
                author=str(msg.get("from", msg.get("actor", "Unknown"))),
                topic=topic,
                text_markdown=flat_text,
                links=links,
                local_files=local_files,
                media_kind=infer_media_kind(msg),
                tags_detected=tags,
                content_type_guess=content_type,
                file_name=file_name,
                mime_type=str(msg.get("mime_type", "")),
                title=title,
                score=score,
            )
        )
    return normalized


def choose_curated_seed(messages: list[NormalizedMessage]) -> list[NormalizedMessage]:
    by_id = {message.message_id: message for message in messages}
    selected: list[NormalizedMessage] = []
    for message_id in MANUAL_PRIORITY_IDS:
        message = by_id.get(message_id)
        if message:
            selected.append(message)

    if not selected:
        return []

    return sorted(selected, key=lambda item: (item.content_type_guess, item.message_id))


def yaml_list(values: list[Any], indent: int = 0) -> str:
    pad = " " * indent
    if not values:
        return f"{pad}[]"
    return "\n".join(f"{pad}- {value}" for value in values)


def make_summary(message: NormalizedMessage) -> list[str]:
    bullets: list[str] = []
    if message.topic:
        bullets.append(f"Источник из Telegram topic: `{message.topic}`.")
    if message.file_name:
        bullets.append(f"Есть локальный файл: `{message.file_name}`.")
    if message.links:
        bullets.append("Содержит внешние ссылки на модели, ноды или документацию.")
    if "lora" in message.tags_detected:
        bullets.append("Материал относится к LoRA или использованию LoRA в workflow.")
    if "character" in message.tags_detected or "turnaround" in message.tags_detected:
        bullets.append("Полезно для character generation, consistency или turnaround.")
    text_lines = [line.strip() for line in message.text_markdown.splitlines() if line.strip()]
    for line in text_lines[1:4]:
        line = line.replace("|", "\\|")
        if len(line) > 220:
            line = line[:217] + "..."
        bullets.append(line)
    return bullets[:6]


def note_body(message: NormalizedMessage, slug: str) -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    bullets = make_summary(message)
    related_pages = infer_related_pages(message)
    local_file_links = [f"[[comfywiki/{path}]]" for path in message.local_files]
    title = message.title.replace("---", "").strip()
    tag_lines = "\n".join(f"  - {tag}" for tag in sorted(set(["comfyui", "telegram", "source", *message.tags_detected])))
    return f"""---
type: source
status: curated
created: {today}
updated: {today}
source_messages:
  - {message.message_id}
source_files:
{yaml_list(local_file_links, indent=2)}
topics:
{yaml_list([message.topic] if message.topic else [], indent=2)}
tags:
{tag_lines}
---

# {title}

## Summary

{chr(10).join(f"- {bullet}" for bullet in bullets)}

## Metadata

- Message ID: `{message.message_id}`
- Date: `{message.date}`
- Author: `{message.author}`
- Topic: `{message.topic or "Unknown"}`
- Content Type: `{message.content_type_guess}`
- Media Kind: `{message.media_kind}`

## Extracted Links

{chr(10).join(f"- {link}" for link in message.links) if message.links else "- None"}

## Related Local Files

{chr(10).join(f"- [[comfywiki/{path}]]" for path in message.local_files) if message.local_files else "- None"}

## Notes

{render_excerpt(message.text_markdown)}

## Related Pages

{chr(10).join(f"- [[{page}]]" for page in related_pages)}
"""


def render_excerpt(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    excerpt = lines[:12]
    return "\n".join(f"- {line}" for line in excerpt) if excerpt else "- Нет текстового описания."


def infer_related_pages(message: NormalizedMessage) -> list[str]:
    pages = ["resources/Best Guides From Telegram"]
    if "setup" in message.tags_detected or "custom_nodes" in message.tags_detected:
        pages.append("setup/Setup & Troubleshooting")
    if "lora" in message.tags_detected:
        pages.append("lora/LoRA Catalog")
        pages.append("lora/LoRA для персонажей")
    if "workflow" in message.tags_detected or message.content_type_guess == "workflow":
        pages.append("workflows/Workflow Catalog")
    if any(tag in message.tags_detected for tag in ("character", "turnaround", "consistency", "realism")):
        pages.append("characters/Character Generation Hub")
        pages.append("characters/Consistency персонажей")
        pages.append("workflows/Workflow для персонажей")
    if "qwen" in message.tags_detected or "flux" in message.tags_detected or "wan" in message.tags_detected:
        pages.append("models/Models & Nodes")
    deduped: list[str] = []
    for page in pages:
        if page not in deduped:
            deduped.append(page)
    return deduped


def write_curated_seed(messages: list[NormalizedMessage]) -> None:
    SOURCE_NOTES_DIR.mkdir(parents=True, exist_ok=True)
    manifest_items: list[dict[str, Any]] = []
    for message in messages:
        slug = SLUG_OVERRIDES.get(
            message.message_id,
            slugify(message.title, f"message-{message.message_id}"),
        )
        note_path = SOURCE_NOTES_DIR / f"{slug}.md"
        note_path.write_text(note_body(message, slug), encoding="utf-8")
        manifest_items.append(
            {
                "message_id": message.message_id,
                "title": message.title,
                "topic": message.topic,
                "note_path": str(note_path.relative_to(ROOT)).replace("\\", "/"),
                "content_type_guess": message.content_type_guess,
                "score": message.score,
                "links": message.links,
                "local_files": message.local_files,
                "tags_detected": message.tags_detected,
            }
        )
    MANIFEST_PATH.write_text(
        json.dumps({"generated_at": datetime.now().isoformat(), "items": manifest_items}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main() -> None:
    data = load_export()
    messages = normalize_messages(data)
    curated = choose_curated_seed(messages)
    write_curated_seed(curated)
    print(f"Generated {len(curated)} curated source notes.")
    print(f"Manifest: {MANIFEST_PATH}")


if __name__ == "__main__":
    main()
