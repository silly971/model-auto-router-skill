# model-auto-router-skill（简体中文）

## Overview

`model-auto-router-skill` 用于把请求路由到独立模型通道：
`code`、`image`、`edit`、`video`。

## Features

- 支持 `--task auto` 自动识别意图并路由。
- 支持 `--task code|image|edit|video` 强制走指定通道。
- 可选 Telegram 自动回传图片/改图/视频结果。
- 支持 `--dry-run --json` 安全预检。

## Install

1. 将本目录复制到 OpenClaw workspace 的 `skills/` 目录。
2. 确认 `SKILL.md`、`scripts/dispatch.py`、`references/config.md` 存在。
3. 必要时重启 OpenClaw gateway 以重新加载 skill。

## Config

配置项见 `references/config.md`。
本仓库内示例均为占位符，需在你自己的环境中替换。

## Security

- 不要提交真实 API Key 或 Bot Token。
- 不要提交真实 Chat ID。
- 不要提交私有/内网接口 URL。
- 敏感信息只放环境变量或密钥管理服务。

## Usage

```bash
python3 {baseDir}/scripts/dispatch.py --task auto --prompt "写一个 Python 函数"
python3 {baseDir}/scripts/dispatch.py --task code --prompt "重构这段函数"
python3 {baseDir}/scripts/dispatch.py --task image --prompt "生成一张海报" --size 1024x1024
```

## License

MIT，见 `LICENSE`。
