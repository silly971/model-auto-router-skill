---
name: model-auto-router
description: Route multimodal requests to dedicated models/endpoints with one command. Use when user asks to auto-select model by intent, or explicitly requests code generation, image generation, image editing, or video generation with different models, including auto delivery of generated media to Telegram.
---

# Model Auto Router

Route one prompt into `code`, `image`, `edit`, or `video` model lanes.

## Quick Start

Auto detect task:

```bash
python3 {baseDir}/scripts/dispatch.py --task auto --prompt "<user request>"
```

Force lane:

```bash
python3 {baseDir}/scripts/dispatch.py --task code  --prompt "实现一个快速排序并写测试"
python3 {baseDir}/scripts/dispatch.py --task image --prompt "赛博朋克风格的龙虾海报" --size 1024x1024
python3 {baseDir}/scripts/dispatch.py --task edit  --prompt "把背景改成白色" --image-input ./input.png
python3 {baseDir}/scripts/dispatch.py --task video --prompt "雨夜街头镜头推进" --video-duration 5
```

## Routing Policy

- `video`: video/animation intent (`视频`, `animation`, `clip`, `sora`)
- `edit`: image-edit intent (`改图`, `修图`, `inpaint`, `remove background`)
- `image`: image-generation intent (`出图`, `画一张`, `illustration`, `logo`)
- `code`: coding intent (`写代码`, `debug`, language keywords)
- default fallback: `code`

## Telegram Delivery

- Enable via `ROUTER_SEND_TELEGRAM=1` (auto mode).
- For `image`/`edit`/`video`, dispatcher sends results to Telegram automatically.
- Chat target resolution order:
  1. `TELEGRAM_CHAT_ID`
  2. latest `telegram:<chatId>` found in `sessions.json`

Manual override per call:

```bash
python3 {baseDir}/scripts/dispatch.py --task image --prompt "..." --telegram on
python3 {baseDir}/scripts/dispatch.py --task image --prompt "..." --telegram off
```

## Runtime Config

Read `references/config.md` before changing model mapping.

- Shared config: `ROUTER_BASE_URL`, `ROUTER_API_KEY`
- Per-lane overrides: `ROUTER_CODE_*`, `ROUTER_IMAGE_*`, `ROUTER_EDIT_*`, `ROUTER_VIDEO_*`
- Supports fallback from `~/.openclaw/.env` (`GROK_API_URL`, `GROK_API_KEY`)

## Safe Execution Rules

- Use `--dry-run --json` first when changing mappings.
- For `edit`, always pass `--image-input`.
- Do not print API keys or auth headers.
