# model-auto-router-skill (English)

## Overview

`model-auto-router-skill` routes one request into dedicated model lanes:
`code`, `image`, `edit`, or `video`.

## Features

- Intent-aware routing with `--task auto`.
- Forced lane execution with `--task code|image|edit|video`.
- Optional Telegram auto-delivery for image/edit/video outputs.
- Dry-run mode for safe validation.

## Install

1. Copy this folder into your OpenClaw workspace skills directory.
2. Ensure `SKILL.md`, `scripts/dispatch.py`, and `references/config.md` are present.
3. Reload/restart your OpenClaw gateway if needed.

## Config

Use environment variables from `references/config.md`.
All values in this repository are placeholders and must be replaced in your own environment.

## Security

- Do not commit real API keys or bot tokens.
- Do not commit private chat IDs.
- Do not commit private/internal endpoint URLs.
- Keep secrets in environment variables or your local secret manager.

## Usage

```bash
python3 {baseDir}/scripts/dispatch.py --task auto --prompt "Write a Python function"
python3 {baseDir}/scripts/dispatch.py --task code --prompt "Refactor this function"
python3 {baseDir}/scripts/dispatch.py --task image --prompt "Create a poster" --size 1024x1024
```

## License

MIT. See `LICENSE`.
