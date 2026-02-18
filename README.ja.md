# model-auto-router-skill（日本語）

## Overview

`model-auto-router-skill` は、リクエストを `code` / `image` / `edit` / `video` の専用レーンに振り分けます。

## Features

- `--task auto` による意図ベースの自動ルーティング。
- `--task code|image|edit|video` による強制レーン実行。
- 画像/編集/動画結果の Telegram 自動送信（任意）。
- `--dry-run --json` による安全な事前検証。

## Install

1. このフォルダを OpenClaw workspace の `skills/` に配置します。
2. `SKILL.md`、`scripts/dispatch.py`、`references/config.md` が存在することを確認します。
3. 必要に応じて OpenClaw gateway を再起動します。

## Config

設定は `references/config.md` を参照してください。
このリポジトリの値はすべてプレースホルダーです。実運用値に置き換えてください。

## Security

- 実際の API キーや Bot トークンをコミットしない。
- 実際の Chat ID をコミットしない。
- 内部/私有エンドポイント URL をコミットしない。
- 秘密情報は環境変数またはシークレット管理で保持する。

## Usage

```bash
python3 {baseDir}/scripts/dispatch.py --task auto --prompt "Python 関数を書いて"
python3 {baseDir}/scripts/dispatch.py --task code --prompt "この関数をリファクタ"
python3 {baseDir}/scripts/dispatch.py --task image --prompt "ポスター画像を作成" --size 1024x1024
```

## License

MIT。`LICENSE` を参照してください。
