# Model Auto Router Config

Use lane-level config so code/image/edit/video can use different providers.

## Shared defaults

- `ROUTER_BASE_URL`
- `ROUTER_API_KEY`

Each lane falls back to shared values if lane-specific values are not set.

## Lane-specific overrides

Code lane:
- `ROUTER_CODE_BASE_URL`
- `ROUTER_CODE_API_KEY`
- `ROUTER_CODE_MODEL`
- `ROUTER_CODE_FALLBACK_BASE_URL` (optional)
- `ROUTER_CODE_FALLBACK_API_KEY` (optional)
- `ROUTER_CODE_FALLBACK_MODEL` (optional)

Image generation lane:
- `ROUTER_IMAGE_BASE_URL`
- `ROUTER_IMAGE_API_KEY`
- `ROUTER_IMAGE_MODEL`

Image edit lane:
- `ROUTER_EDIT_BASE_URL`
- `ROUTER_EDIT_API_KEY`
- `ROUTER_EDIT_MODEL`

Video lane:
- `ROUTER_VIDEO_BASE_URL`
- `ROUTER_VIDEO_API_KEY`
- `ROUTER_VIDEO_MODEL`
- `ROUTER_VIDEO_RETRY_ATTEMPTS` (default 3)
- `ROUTER_VIDEO_RETRY_DELAY` seconds between retries (default 6)

## Telegram auto delivery

- `ROUTER_SEND_TELEGRAM=1` enables automatic delivery for image/edit/video tasks when `--telegram auto`.
- `TELEGRAM_BOT_TOKEN` optional (fallback: `channels.telegram.botToken` from `openclaw.json`).
- `TELEGRAM_CHAT_ID` optional (fallback: parsed from latest telegram session key in `sessions.json`).

## Fallback from ~/.openclaw/.env

If lane settings are not provided, dispatcher can use:
- `GROK_API_URL`
- `GROK_API_KEY`
- `GROK_IMAGE_MODEL`
- `GROK_EDIT_MODEL`
- `GROK_VIDEO_MODEL`

## Example

```bash
# code
export ROUTER_CODE_BASE_URL="https://api.example.com/v1"
export ROUTER_CODE_MODEL="<code_model_id>"
export ROUTER_CODE_API_KEY="<code_api_key>"

# image / edit / video
export ROUTER_IMAGE_BASE_URL="https://api.example.com/v1"
export ROUTER_IMAGE_API_KEY="<image_key>"
export ROUTER_IMAGE_MODEL="<image_model_id>"

export ROUTER_EDIT_BASE_URL="https://api.example.com/v1"
export ROUTER_EDIT_API_KEY="<image_key>"
export ROUTER_EDIT_MODEL="<edit_model_id>"

export ROUTER_VIDEO_BASE_URL="https://api.example.com/v1"
export ROUTER_VIDEO_API_KEY="<video_key>"
export ROUTER_VIDEO_MODEL="<video_model_id>"

# Telegram

export ROUTER_SEND_TELEGRAM="1"
export TELEGRAM_CHAT_ID="<your_chat_id>"
```

## Validate before live calls

```bash
python3 {baseDir}/scripts/dispatch.py --task auto --prompt "写一个 Python 函数" --dry-run --json
python3 {baseDir}/scripts/dispatch.py --task auto --prompt "做一张龙虾海报" --dry-run --json
python3 {baseDir}/scripts/dispatch.py --task auto --prompt "把这张图背景改白" --image-input ./input.png --dry-run --json
python3 {baseDir}/scripts/dispatch.py --task auto --prompt "生成 5 秒短视频" --dry-run --json
```
