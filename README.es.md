# 🔀 OpenClaw Model Auto Router Skill

[English](./README.md) | [简体中文](./README.zh-CN.md) | [日本語](./README.ja.md) | **Español**

> Enruta solicitudes de code/image/edit/video al carril de modelo correcto desde un solo punto de entrada.

<p align="center">
  <img src="https://img.shields.io/badge/OpenClaw-Skill-blue?style=flat-square" alt="OpenClaw Skill" />
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="MIT License" />
</p>

---

## ✨ Features

| Comando | Descripción |
|---------|-------------|
| `--task auto` | Detecta intención y enruta a `code` / `image` / `edit` / `video` |
| `--task code` | Fuerza el carril de código |
| `--task image` | Fuerza el carril de generación de imagen |
| `--task edit` | Fuerza el carril de edición (requiere `--image-input`) |
| `--task video` | Fuerza el carril de video |
| `--dry-run --json` | Valida mapeo de modelos sin generación real |
| `--telegram auto|on|off` | Controla el envío automático a Telegram |

## Why?

Cuando un solo agent maneja tareas de código y multimedia, el cambio manual de modelo se vuelve frágil.
Este skill mantiene el enrutamiento determinista y repetible.

## How It Works

```text
Tú: Genera un póster estilo neón
Skill: enruta al carril image
Resultado: devuelve imagen (y opcionalmente la envía a Telegram)

Tú: Refactoriza esta función de Python
Skill: enruta al carril code
Resultado: devuelve salida de código
```

## 🚀 Quick Start

### 🧑 Si eres humano

Envía este mensaje a tu agente OpenClaw:

> Please install https://github.com/silly971/model-auto-router-skill into my OpenClaw workspace skills, replace placeholders in references/config.md with my real local values, and run dry-run validation for code/image/edit/video lanes.

### 🤖 Si eres una IA

Pide permiso al humano primero y luego sigue la instalación y validación.

---

## 📦 Installation

### 1. Clonar repositorio

```bash
git clone https://github.com/silly971/model-auto-router-skill.git /opt/openclaw-skills/model-auto-router-skill
```

### 2. Instalar en el workspace de OpenClaw

```bash
mkdir -p ~/.openclaw/workspace/skills
cp -r /opt/openclaw-skills/model-auto-router-skill ~/.openclaw/workspace/skills/model-auto-router
```

### 3. Configurar entorno

Usa `references/config.md` y reemplaza los placeholders con valores reales en tu entorno local.

### 4. Validar

```bash
python3 ~/.openclaw/workspace/skills/model-auto-router/scripts/dispatch.py --task auto --prompt "Escribe una función en Python" --dry-run --json
```

## ⚙️ Configuration

Variables principales (lista completa en `references/config.md`):

| Grupo | Propósito |
|-------|-----------|
| `ROUTER_CODE_*` | Endpoint, clave y modelo para código |
| `ROUTER_IMAGE_*` | Endpoint, clave y modelo para imagen |
| `ROUTER_EDIT_*` | Endpoint, clave y modelo para edición |
| `ROUTER_VIDEO_*` | Endpoint, clave, modelo y reintentos de video |
| `ROUTER_SEND_TELEGRAM` / `TELEGRAM_*` | Entrega automática por Telegram |

## 🔒 Security

- Este repositorio incluye **solo configuración de ejemplo**.
- No subas claves API reales, tokens de bot, chat IDs ni endpoints privados.
- Guarda secretos en variables de entorno o en un gestor de secretos.

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

Issues y PRs son bienvenidos.

## 📄 License

MIT. Ver `LICENSE`.
