# 🔀 OpenClaw Model Auto Router Skill

[English](./README.md) | **简体中文** | [日本語](./README.ja.md) | [Español](./README.es.md)

> 用一个入口，把 code/image/edit/video 请求稳定路由到正确模型通道。

<p align="center">
  <img src="https://img.shields.io/badge/OpenClaw-Skill-blue?style=flat-square" alt="OpenClaw Skill" />
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="MIT License" />
</p>

---

## ✨ Features

| 命令 | 说明 |
|------|------|
| `--task auto` | 自动识别意图并路由到 `code` / `image` / `edit` / `video` |
| `--task code` | 强制走代码通道 |
| `--task image` | 强制走出图通道 |
| `--task edit` | 强制走改图通道（需 `--image-input`） |
| `--task video` | 强制走视频通道 |
| `--dry-run --json` | 不触发真实生成，只验证模型映射 |
| `--telegram auto|on|off` | 控制 Telegram 自动回传 |

## 🆕 最新更新（2026-02-18）

- 增强代码通道稳定性：主代码模型报错或返回空内容时，自动切到 fallback 模型重试。
- 增加明确的空响应报错，并附带精简上游响应摘要，方便排障。
- 新增严格回执约束：仅当工具输出包含 `[telegram] delivered` 时，才允许声明“已发送到 Telegram”。
- 仓库继续保持脱敏：`references/config.md` 仅提供占位符示例。

## Why?

一个 Agent 同时处理“写代码 + 多模态生成”时，手工切模型容易混乱。
这个 skill 的目标是让路由确定且可复现：

- 代码请求走代码模型。
- 媒体请求走图像/视频模型。
- 图片/视频可自动发回 Telegram。

## How It Works

```text
你：生成一张霓虹风海报
Skill：路由到 image 通道
结果：返回图片（可选自动发 Telegram）

你：重构这段 Python 代码
Skill：路由到 code 通道
结果：返回代码结果
```

## 🚀 Quick Start

### 🧑 人类用户

把下面这段发给你的 OpenClaw agent：

> 请把 https://github.com/silly971/model-auto-router-skill 安装到我的 OpenClaw workspace skills，按 references/config.md 的占位符在本地填入真实配置，并对 code/image/edit/video 做 dry-run 验证。

### 🤖 AI 代理

先拿到人类授权，再按下面的安装与验证步骤执行。

---

## 📦 Installation

### 1. 克隆仓库

```bash
git clone https://github.com/silly971/model-auto-router-skill.git /opt/openclaw-skills/model-auto-router-skill
```

### 2. 安装到 OpenClaw workspace

```bash
mkdir -p ~/.openclaw/workspace/skills
cp -r /opt/openclaw-skills/model-auto-router-skill ~/.openclaw/workspace/skills/model-auto-router
```

### 3. 配置运行环境

参考 `references/config.md`，在你的本地环境替换为真实值。

### 4. 验证

```bash
python3 ~/.openclaw/workspace/skills/model-auto-router/scripts/dispatch.py --task auto --prompt "写一个 Python 函数" --dry-run --json
```

## ⚙️ Configuration

主要变量（完整列表见 `references/config.md`）：

| 变量组 | 用途 |
|--------|------|
| `ROUTER_CODE_*` | 代码模型地址/密钥/模型 ID |
| `ROUTER_IMAGE_*` | 出图模型地址/密钥/模型 ID |
| `ROUTER_EDIT_*` | 改图模型地址/密钥/模型 ID |
| `ROUTER_VIDEO_*` | 视频模型地址/密钥/模型 ID/重试策略 |
| `ROUTER_SEND_TELEGRAM` / `TELEGRAM_*` | Telegram 自动回传配置 |

## 🔒 Security

- 本仓库仅提供**占位符配置**。
- 禁止提交真实 API Key、Bot Token、Chat ID、私有接口地址。
- 敏感信息请放环境变量或密钥管理系统。

发布前快速扫描：

```bash
rg -n "sk-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{20,}|[0-9]{8,12}:[A-Za-z0-9_-]{20,}" -S .
```

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

欢迎提 Issue 和 PR。

## 📄 License

MIT，见 `LICENSE`。
