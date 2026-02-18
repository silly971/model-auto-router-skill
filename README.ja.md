# 🔀 OpenClaw Model Auto Router Skill

[English](./README.md) | [简体中文](./README.zh-CN.md) | **日本語** | [Español](./README.es.md)

> 1つの入口で、code/image/edit/video リクエストを適切なモデルレーンへ安定的に振り分けます。

<p align="center">
  <img src="https://img.shields.io/badge/OpenClaw-Skill-blue?style=flat-square" alt="OpenClaw Skill" />
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="MIT License" />
</p>

---

## ✨ Features

| コマンド | 説明 |
|----------|------|
| `--task auto` | 意図を自動判定して `code` / `image` / `edit` / `video` に振り分け |
| `--task code` | コードレーンを強制 |
| `--task image` | 画像生成レーンを強制 |
| `--task edit` | 画像編集レーンを強制（`--image-input` 必須） |
| `--task video` | 動画レーンを強制 |
| `--dry-run --json` | 実生成なしでモデルマッピングを検証 |
| `--telegram auto|on|off` | Telegram 自動送信を制御 |

## 🆕 最新更新（2026-02-18）

- コードレーンの安定性を強化。主コードモデルが失敗または空応答の場合、自動でフォールバックモデルへ再試行します。
- 空応答時のエラーメッセージを明確化し、原因調査用に上流レスポンス要約を出力します。
- リポジトリは引き続き脱敏済みで、`references/config.md` はプレースホルダー例のみです。

## Why?

1つの Agent が「コーディング」と「マルチモーダル生成」を同時に扱うと、
手動切替は壊れやすくなります。
この skill はルーティングを決定的に保ちます。

## How It Works

```text
あなた: ネオン風ポスターを作成して
Skill: image レーンへルーティング
結果: 画像を返却（必要なら Telegram に自動送信）

あなた: この Python コードをリファクタして
Skill: code レーンへルーティング
結果: コード結果を返却
```

## 🚀 Quick Start

### 🧑 人間ユーザー

次のメッセージを OpenClaw agent に送ってください：

> Please install https://github.com/silly971/model-auto-router-skill into my OpenClaw workspace skills, replace placeholders in references/config.md with my real local values, and run dry-run validation for code/image/edit/video lanes.

### 🤖 AI エージェント

まず人間の許可を得てから、以下の手順を実行してください。

---

## 📦 Installation

### 1. リポジトリをクローン

```bash
git clone https://github.com/silly971/model-auto-router-skill.git /opt/openclaw-skills/model-auto-router-skill
```

### 2. OpenClaw workspace に配置

```bash
mkdir -p ~/.openclaw/workspace/skills
cp -r /opt/openclaw-skills/model-auto-router-skill ~/.openclaw/workspace/skills/model-auto-router
```

### 3. 実行環境を設定

`references/config.md` のプレースホルダーを、ローカルの実値に置き換えます。

### 4. 検証

```bash
python3 ~/.openclaw/workspace/skills/model-auto-router/scripts/dispatch.py --task auto --prompt "Python 関数を書いて" --dry-run --json
```

## ⚙️ Configuration

主要変数（詳細は `references/config.md`）：

| 変数グループ | 用途 |
|--------------|------|
| `ROUTER_CODE_*` | コード用エンドポイント/キー/モデル ID |
| `ROUTER_IMAGE_*` | 画像生成用エンドポイント/キー/モデル ID |
| `ROUTER_EDIT_*` | 画像編集用エンドポイント/キー/モデル ID |
| `ROUTER_VIDEO_*` | 動画用エンドポイント/キー/モデル ID/リトライ設定 |
| `ROUTER_SEND_TELEGRAM` / `TELEGRAM_*` | Telegram 自動配信設定 |

## 🔒 Security

- このリポジトリは**プレースホルダー設定のみ**を含みます。
- 実際の API キー、Bot トークン、Chat ID、内部 URL はコミットしないでください。
- 秘密情報は環境変数またはシークレット管理で扱ってください。

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

Issue / PR を歓迎します。

## 📄 License

MIT。`LICENSE` を参照してください。
