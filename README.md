# 🔀 OpenClaw Model Auto Router Skill

**English** | [简体中文](./README.zh-CN.md) | [日本語](./README.ja.md) | [Español](./README.es.md)

> Route code/image/edit/video requests to the right model lane from one entry point.

<p align="center">
  <img src="https://img.shields.io/badge/OpenClaw-Skill-blue?style=flat-square" alt="OpenClaw Skill" />
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="MIT License" />
</p>

---

## ✨ Features

| Command | Description |
|---------|-------------|
| `--task auto` | Detect intent and route to `code` / `image` / `edit` / `video` |
| `--task code` | Force code lane for coding/debug/refactor tasks |
| `--task image` | Force image generation lane |
| `--task edit` | Force image editing lane (requires `--image-input`) |
| `--task video` | Force video generation lane |
| `--dry-run --json` | Validate runtime model mapping without live generation |
| `--telegram auto|on|off` | Control Telegram auto-delivery behavior |

## Why?

When one agent handles mixed requests, model switching gets messy and error-prone.
This skill keeps routing deterministic:

- Code tasks use code-optimized models.
- Media tasks use image/video endpoints.
- Telegram delivery can happen automatically for media outputs.

## How It Works

```text
You: Generate a poster with neon style
Skill: route -> image lane
Result: image file/link returned (and optionally sent to Telegram)

You: Refactor this Python function
Skill: route -> code lane
Result: code answer from code lane model
```

## 🚀 Quick Start

### 🧑 If you're a human

Send this to your OpenClaw agent:

> Please install model-auto-router-skill from https://github.com/silly971/model-auto-router-skill into my OpenClaw workspace skills, configure placeholders in .env with my real providers, and run a dry-run validation for code/image/edit/video lanes.

### 🤖 If you're an AI

Get human approval first, then follow the installation and validation steps below.

---

## 📦 Installation

### 1. Clone repository

```bash
git clone https://github.com/silly971/model-auto-router-skill.git /opt/openclaw-skills/model-auto-router-skill
```

### 2. Install into OpenClaw workspace

```bash
mkdir -p ~/.openclaw/workspace/skills
cp -r /opt/openclaw-skills/model-auto-router-skill ~/.openclaw/workspace/skills/model-auto-router
```

### 3. Configure runtime env

Use placeholders from `references/config.md` and set your real values in your local environment.

### 4. Validate

```bash
python3 ~/.openclaw/workspace/skills/model-auto-router/scripts/dispatch.py --task auto --prompt "Write a Python function" --dry-run --json
```

## ⚙️ Configuration

Main variables (see full list in `references/config.md`):

| Variable Group | Purpose |
|----------------|---------|
| `ROUTER_CODE_*` | Code model endpoint, key, and model ID |
| `ROUTER_IMAGE_*` | Image generation endpoint, key, and model ID |
| `ROUTER_EDIT_*` | Image editing endpoint, key, and model ID |
| `ROUTER_VIDEO_*` | Video endpoint, key, model ID, and retry policy |
| `ROUTER_SEND_TELEGRAM` / `TELEGRAM_*` | Optional Telegram auto-delivery |

## 🔒 Security

- This repository contains **placeholder config only**.
- Never commit real API keys, bot tokens, chat IDs, or private endpoints.
- Keep secrets in local environment variables or a secret manager.

## 📁 Project Structure

```text
model-auto-router-skill/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── scripts/
│   └── dispatch.py
├── references/
│   └── config.md
├── README.md
├── README.zh-CN.md
├── README.ja.md
├── README.es.md
├── .gitignore
└── LICENSE
```

## 🤝 Contributing

Issues and PRs are welcome.

## 📄 License

MIT. See `LICENSE`.
