#!/usr/bin/env python3
import argparse
import base64
import datetime as dt
import json
import mimetypes
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

MODELS_JSON = Path("/root/.openclaw/agents/main/agent/models.json")
OPENCLAW_JSON = Path("/root/.openclaw/openclaw.json")
SESSIONS_JSON = Path("/root/.openclaw/agents/main/sessions/sessions.json")
DOTENV_PATH = Path("/root/.openclaw/.env")


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def load_dotenv(path: Path) -> dict:
    if not path.exists():
        return {}
    values = {}
    try:
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            if value.startswith('"') and value.endswith('"') and len(value) >= 2:
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'") and len(value) >= 2:
                value = value[1:-1]
            if key:
                values[key] = value
    except Exception:
        return values
    return values


def env_or_dot(name: str, dot: dict, default: str = "") -> str:
    return (os.environ.get(name) or dot.get(name) or default or "").strip()


def truthy(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def normalize_provider_name(name: str) -> str:
    return name.strip().strip('"').strip("'")


def ensure_v1_base_url(url: str) -> str:
    url = (url or "").strip().rstrip("/")
    if not url:
        return ""
    parsed = urllib.parse.urlparse(url)
    path = parsed.path or ""
    if path in ("", "/"):
        parsed = parsed._replace(path="/v1")
        return urllib.parse.urlunparse(parsed).rstrip("/")
    return url


def split_model_id(model: str) -> str:
    model = (model or "").strip()
    if "/" in model:
        return model.split("/", 1)[1]
    return model


def detect_task(prompt: str) -> str:
    text = prompt.strip()
    low = text.lower()

    video_keywords = ["视频", "出视频", "短视频", "动画", "video", "clip", "animate", "sora"]
    edit_keywords = [
        "改图",
        "修图",
        "抠图",
        "去背景",
        "换背景",
        "局部重绘",
        "edit image",
        "image edit",
        "inpaint",
        "remove background",
    ]
    image_keywords = [
        "出图",
        "图片",
        "图像",
        "画一张",
        "出一张",
        "生成一张",
        "做一张",
        "绘制",
        "画",
        "海报",
        "插画",
        "logo",
        "image",
        "picture",
        "photo",
        "draw",
        "illustration",
        "render",
    ]
    code_keywords = [
        "代码",
        "写代码",
        "编程",
        "脚本",
        "调试",
        "修复",
        "重构",
        "函数",
        "sql",
        "python",
        "javascript",
        "typescript",
        "java",
        "golang",
        "rust",
        "c++",
        "开发",
        "debug",
        "bug",
        "refactor",
        "implement",
        "code",
    ]

    if any(k in low or k in text for k in video_keywords):
        return "video"
    if any(k in low or k in text for k in edit_keywords):
        return "edit"
    if any(k in low or k in text for k in image_keywords):
        return "image"
    if any(k in low or k in text for k in code_keywords):
        return "code"
    return "code"


def pick_provider(default_provider: str = "") -> tuple[str, dict]:
    models_cfg = load_json(MODELS_JSON)
    providers = models_cfg.get("providers") or {}
    normalized = {
        normalize_provider_name(name): details
        for name, details in providers.items()
        if isinstance(details, dict)
    }

    if default_provider and default_provider in normalized:
        return default_provider, normalized[default_provider]
    if "customopenai" in normalized:
        return "customopenai", normalized["customopenai"]
    for name, details in normalized.items():
        if details.get("baseUrl") and details.get("apiKey"):
            return name, details
    return "", {}


def resolve_runtime_settings() -> dict:
    dot = load_dotenv(DOTENV_PATH)

    app_cfg = load_json(OPENCLAW_JSON)
    default_model_full = (
        (app_cfg.get("agents") or {}).get("defaults", {}).get("model")
        or env_or_dot("ROUTER_DEFAULT_MODEL", dot)
        or ""
    )

    default_provider = ""
    default_code_model = ""
    if isinstance(default_model_full, dict):
        primary = default_model_full.get("primary", "")
        if "/" in primary:
            default_provider, default_code_model = primary.split("/", 1)
    elif "/" in str(default_model_full):
        default_provider, default_code_model = str(default_model_full).split("/", 1)

    provider_name_env = env_or_dot("ROUTER_PROVIDER", dot)
    provider_name, provider_cfg = pick_provider(provider_name_env or default_provider)

    shared_base_url = ensure_v1_base_url(
        env_or_dot("ROUTER_BASE_URL", dot)
        or provider_cfg.get("baseUrl", "")
        or env_or_dot("OPENAI_BASE_URL", dot)
    )
    shared_api_key = (
        env_or_dot("ROUTER_API_KEY", dot)
        or provider_cfg.get("apiKey", "")
        or env_or_dot("OPENAI_API_KEY", dot)
    ).strip()

    provider_models = provider_cfg.get("models") or []
    first_provider_model = ""
    if provider_models and isinstance(provider_models[0], dict):
        first_provider_model = provider_models[0].get("id", "")

    code_model = split_model_id(
        env_or_dot("ROUTER_CODE_MODEL", dot)
        or default_code_model
        or first_provider_model
        or "gpt-4.1"
    )
    code_fallback_model = split_model_id(
        env_or_dot("ROUTER_CODE_FALLBACK_MODEL", dot) or first_provider_model
    )
    if code_fallback_model == code_model:
        code_fallback_model = ""

    image_model = split_model_id(
        env_or_dot("ROUTER_IMAGE_MODEL", dot)
        or env_or_dot("GROK_IMAGE_MODEL", dot)
        or "grok-imagine-1.0"
    )
    edit_model = split_model_id(
        env_or_dot("ROUTER_EDIT_MODEL", dot)
        or env_or_dot("GROK_EDIT_MODEL", dot)
        or image_model
    )
    video_model = split_model_id(
        env_or_dot("ROUTER_VIDEO_MODEL", dot)
        or env_or_dot("GROK_VIDEO_MODEL", dot)
        or "grok-imagine-1.0-video"
    )

    grok_url = env_or_dot("GROK_API_URL", dot)
    grok_key = env_or_dot("GROK_API_KEY", dot)

    code_base_url = ensure_v1_base_url(env_or_dot("ROUTER_CODE_BASE_URL", dot) or shared_base_url)
    code_fallback_base_url = ensure_v1_base_url(
        env_or_dot("ROUTER_CODE_FALLBACK_BASE_URL", dot) or shared_base_url
    )
    image_base_url = ensure_v1_base_url(
        env_or_dot("ROUTER_IMAGE_BASE_URL", dot) or grok_url or shared_base_url
    )
    edit_base_url = ensure_v1_base_url(
        env_or_dot("ROUTER_EDIT_BASE_URL", dot) or image_base_url
    )
    video_base_url = ensure_v1_base_url(
        env_or_dot("ROUTER_VIDEO_BASE_URL", dot) or grok_url or shared_base_url
    )

    code_api_key = (env_or_dot("ROUTER_CODE_API_KEY", dot) or shared_api_key).strip()
    code_fallback_api_key = (
        env_or_dot("ROUTER_CODE_FALLBACK_API_KEY", dot) or shared_api_key
    ).strip()
    image_api_key = (env_or_dot("ROUTER_IMAGE_API_KEY", dot) or grok_key or shared_api_key).strip()
    edit_api_key = (env_or_dot("ROUTER_EDIT_API_KEY", dot) or image_api_key).strip()
    video_api_key = (env_or_dot("ROUTER_VIDEO_API_KEY", dot) or grok_key or shared_api_key).strip()

    video_retry_attempts_raw = env_or_dot("ROUTER_VIDEO_RETRY_ATTEMPTS", dot, "3")
    video_retry_delay_raw = env_or_dot("ROUTER_VIDEO_RETRY_DELAY", dot, "6")
    try:
        video_retry_attempts = max(1, int(video_retry_attempts_raw))
    except Exception:
        video_retry_attempts = 3
    try:
        video_retry_delay = max(1, int(video_retry_delay_raw))
    except Exception:
        video_retry_delay = 6

    return {
        "dot": dot,
        "provider": provider_name,
        "code_model": code_model,
        "code_fallback_model": code_fallback_model,
        "image_model": image_model,
        "edit_model": edit_model,
        "video_model": video_model,
        "code_base_url": code_base_url,
        "code_fallback_base_url": code_fallback_base_url,
        "image_base_url": image_base_url,
        "edit_base_url": edit_base_url,
        "video_base_url": video_base_url,
        "code_api_key": code_api_key,
        "code_fallback_api_key": code_fallback_api_key,
        "image_api_key": image_api_key,
        "edit_api_key": edit_api_key,
        "video_api_key": video_api_key,
        "video_retry_attempts": video_retry_attempts,
        "video_retry_delay": video_retry_delay,
    }


def call_json_api(base_url: str, endpoint: str, api_key: str, payload: dict, timeout: int) -> dict:
    url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": os.environ.get("ROUTER_USER_AGENT", "curl/8.5.0"),
        },
        data=body,
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        err_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} from {url}: {err_body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Network error calling {url}: {exc}") from exc

    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Non-JSON response from {url}: {raw[:400]}") from exc


def build_multipart(fields: dict, file_field: str, file_path: Path) -> tuple[bytes, str]:
    boundary = f"----OpenClawBoundary{uuid.uuid4().hex}"
    parts = []

    for key, value in fields.items():
        if value is None:
            continue
        parts.append(f"--{boundary}\r\n".encode("utf-8"))
        parts.append(f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode("utf-8"))
        parts.append(str(value).encode("utf-8"))
        parts.append(b"\r\n")

    mime = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
    filename = file_path.name
    parts.append(f"--{boundary}\r\n".encode("utf-8"))
    parts.append(
        (
            f'Content-Disposition: form-data; name="{file_field}"; '
            f'filename="{filename}"\r\n'
        ).encode("utf-8")
    )
    parts.append(f"Content-Type: {mime}\r\n\r\n".encode("utf-8"))
    parts.append(file_path.read_bytes())
    parts.append(b"\r\n")

    parts.append(f"--{boundary}--\r\n".encode("utf-8"))
    body = b"".join(parts)
    return body, boundary


def normalize_choice_content(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                if isinstance(item.get("text"), str):
                    parts.append(item["text"])
                elif isinstance(item.get("content"), str):
                    parts.append(item["content"])
        return "\n".join([p for p in parts if p])
    return ""


def run_code(settings: dict, prompt: str, timeout: int) -> dict:
    primary_model = settings["code_model"]
    fallback_model = settings.get("code_fallback_model", "")

    payload = {
        "model": primary_model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
    }

    used_model = primary_model
    fallback_from = ""
    try:
        res = call_json_api(
            settings["code_base_url"],
            "/chat/completions",
            settings["code_api_key"],
            payload,
            timeout,
        )
    except RuntimeError:
        fb_base = settings.get("code_fallback_base_url", "")
        fb_key = settings.get("code_fallback_api_key", "")
        if fallback_model and fb_base and fb_key:
            payload["model"] = fallback_model
            res = call_json_api(
                fb_base,
                "/chat/completions",
                fb_key,
                payload,
                timeout,
            )
            used_model = fallback_model
            fallback_from = primary_model
        else:
            raise

    text = ""
    choices = res.get("choices") or []
    if choices and isinstance(choices[0], dict):
        msg = choices[0].get("message") or {}
        text = normalize_choice_content(msg.get("content"))

    result = {"task": "code", "model": used_model, "text": text, "raw": res}
    if fallback_from:
        result["fallbackFrom"] = fallback_from
    return result


def decode_b64_payload(raw_value: str) -> bytes:
    data = raw_value.strip()
    if data.startswith("data:") and "," in data:
        data = data.split(",", 1)[1]
    missing = len(data) % 4
    if missing:
        data += "=" * (4 - missing)
    return base64.b64decode(data)


def default_out_dir() -> Path:
    stamp = dt.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    out_dir = Path("./tmp") / f"model-auto-router-{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def ext_from_url(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    name = Path(parsed.path).name.lower()
    for ext in (".png", ".jpg", ".jpeg", ".webp", ".gif", ".mp4"):
        if name.endswith(ext):
            return ext
    return ".png"


def collect_media_files_from_response(res: dict, folder: Path, prefix: str) -> list[str]:
    files = []
    data_items = res.get("data") or []
    if not isinstance(data_items, list) or not data_items:
        raise RuntimeError(f"Unexpected media response: {json.dumps(res)[:400]}")

    for idx, item in enumerate(data_items, start=1):
        if not isinstance(item, dict):
            continue

        b64_val = item.get("b64_json")
        url_val = item.get("url")
        if isinstance(b64_val, str) and b64_val.startswith("http"):
            url_val = b64_val
            b64_val = None

        ext = ".png"
        if isinstance(url_val, str) and url_val:
            ext = ext_from_url(url_val)

        file_path = folder / f"{prefix}-{idx:03d}{ext}"
        if isinstance(b64_val, str) and b64_val:
            file_path.write_bytes(decode_b64_payload(b64_val))
        elif isinstance(url_val, str) and url_val:
            urllib.request.urlretrieve(url_val, file_path)
        else:
            raise RuntimeError(f"Response item has neither b64_json nor url: {json.dumps(item)[:200]}")

        files.append(str(file_path.resolve()))

    return files


def run_image(settings: dict, prompt: str, size: str, quality: str, count: int, timeout: int, out_dir: str) -> dict:
    payload = {
        "model": settings["image_model"],
        "prompt": prompt,
        "n": max(1, count),
        "size": size,
        "quality": quality,
        "response_format": "b64_json",
    }
    res = call_json_api(
        settings["image_base_url"],
        "/images/generations",
        settings["image_api_key"],
        payload,
        timeout,
    )

    folder = Path(out_dir).expanduser() if out_dir else default_out_dir()
    folder.mkdir(parents=True, exist_ok=True)
    files = collect_media_files_from_response(res, folder, "image")

    return {
        "task": "image",
        "model": settings["image_model"],
        "files": files,
        "out_dir": str(folder),
        "raw": res,
    }


def prepare_edit_image_value(image_input: str) -> str:
    raw = image_input.strip()
    if raw.startswith("http://") or raw.startswith("https://"):
        return raw

    candidate = Path(raw).expanduser()
    if not candidate.exists() or not candidate.is_file():
        raise RuntimeError(f"edit input image not found: {candidate}")

    mime = mimetypes.guess_type(str(candidate))[0] or "application/octet-stream"
    b64 = base64.b64encode(candidate.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def run_edit(
    settings: dict,
    prompt: str,
    image_input: str,
    size: str,
    quality: str,
    timeout: int,
    out_dir: str,
) -> dict:
    payload = {
        "model": settings["edit_model"],
        "prompt": prompt,
        "image": prepare_edit_image_value(image_input),
        "n": 1,
        "size": size,
        "quality": quality,
        "response_format": "b64_json",
    }
    res = call_json_api(
        settings["edit_base_url"],
        "/images/edits",
        settings["edit_api_key"],
        payload,
        timeout,
    )

    folder = Path(out_dir).expanduser() if out_dir else default_out_dir()
    folder.mkdir(parents=True, exist_ok=True)
    files = collect_media_files_from_response(res, folder, "edit")

    return {
        "task": "edit",
        "model": settings["edit_model"],
        "files": files,
        "out_dir": str(folder),
        "raw": res,
    }


def run_video(settings: dict, prompt: str, duration: int, size: str, timeout: int) -> dict:
    attempts = max(1, int(settings.get("video_retry_attempts", 1)))
    retry_delay = max(1, int(settings.get("video_retry_delay", 6)))

    payload = {"model": settings["video_model"], "prompt": prompt}
    if duration > 0:
        payload["duration"] = duration
    if size:
        payload["size"] = size

    last_res = {}
    all_ids = []

    for i in range(1, attempts + 1):
        res = call_json_api(
            settings["video_base_url"],
            "/videos/generations",
            settings["video_api_key"],
            payload,
            timeout,
        )
        last_res = res

        rid = res.get("id")
        if isinstance(rid, str) and rid:
            all_ids.append(rid)

        urls = []
        data_items = res.get("data") or []
        if isinstance(data_items, list):
            for item in data_items:
                if isinstance(item, dict):
                    for key in ("url", "video_url", "download_url"):
                        if isinstance(item.get(key), str) and item[key]:
                            urls.append(item[key])

        text = ""
        choices = res.get("choices") or []
        if choices and isinstance(choices[0], dict):
            msg = choices[0].get("message") or {}
            text = normalize_choice_content(msg.get("content"))

        if urls:
            return {
                "task": "video",
                "model": settings["video_model"],
                "urls": urls,
                "text": text,
                "raw": res,
                "attemptsUsed": i,
                "requestIds": all_ids,
            }

        if i < attempts:
            time.sleep(retry_delay)

    text = ""
    choices = last_res.get("choices") or []
    if choices and isinstance(choices[0], dict):
        msg = choices[0].get("message") or {}
        text = normalize_choice_content(msg.get("content"))

    return {
        "task": "video",
        "model": settings["video_model"],
        "urls": [],
        "text": text,
        "raw": last_res,
        "attemptsUsed": attempts,
        "requestIds": all_ids,
    }


def extract_telegram_chat_id_from_sessions() -> str:
    data = load_json(SESSIONS_JSON)
    if not isinstance(data, dict):
        return ""

    best_updated = -1
    best_chat = ""

    for _, entry in data.items():
        if not isinstance(entry, dict):
            continue
        updated = int(entry.get("updatedAt") or 0)
        candidates = []

        origin = entry.get("origin") or {}
        delivery = entry.get("deliveryContext") or {}
        for raw in [origin.get("from"), origin.get("to"), delivery.get("to")]:
            if isinstance(raw, str):
                candidates.append(raw)

        for raw in candidates:
            m = re.search(r"telegram:([-0-9]+)", raw)
            if m:
                chat_id = m.group(1)
                if updated >= best_updated:
                    best_updated = updated
                    best_chat = chat_id

    return best_chat


def resolve_telegram_credentials(settings: dict) -> tuple[str, str]:
    dot = settings.get("dot") or {}
    cfg = load_json(OPENCLAW_JSON)

    token = env_or_dot("TELEGRAM_BOT_TOKEN", dot)
    if not token:
        token = str((cfg.get("channels") or {}).get("telegram", {}).get("botToken", "")).strip()

    chat_id = env_or_dot("TELEGRAM_CHAT_ID", dot)
    if not chat_id:
        chat_id = extract_telegram_chat_id_from_sessions()

    return token, chat_id


def telegram_post_form(token: str, method: str, params: dict, timeout: int) -> dict:
    url = f"https://api.telegram.org/bot{token}/{method}"
    body = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None}).encode("utf-8")
    req = urllib.request.Request(
        url,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=body,
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
    return json.loads(raw)


def telegram_post_file(token: str, method: str, params: dict, file_field: str, file_path: Path, timeout: int) -> dict:
    body, boundary = build_multipart(params, file_field, file_path)
    url = f"https://api.telegram.org/bot{token}/{method}"
    req = urllib.request.Request(
        url,
        method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        data=body,
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
    return json.loads(raw)


def telegram_send_result(settings: dict, result: dict, prompt: str, timeout: int) -> None:
    token, chat_id = resolve_telegram_credentials(settings)
    if not token:
        raise RuntimeError("Telegram bot token missing (TELEGRAM_BOT_TOKEN or channels.telegram.botToken)")
    if not chat_id:
        raise RuntimeError("Telegram chat_id missing (TELEGRAM_CHAT_ID and no telegram:* session found)")

    task = result.get("task", "")
    model = result.get("model", "")
    caption = f"[{task}] {model}\\n{prompt}"[:900]

    if task in {"image", "edit"}:
        files = result.get("files") or []
        if not files:
            raise RuntimeError("no image files to send")
        for idx, file_path in enumerate(files, start=1):
            path_obj = Path(file_path)
            params = {
                "chat_id": chat_id,
                "caption": caption if idx == 1 else None,
                "parse_mode": None,
            }
            if str(file_path).startswith("http://") or str(file_path).startswith("https://"):
                params["photo"] = str(file_path)
                reply = telegram_post_form(token, "sendPhoto", params, timeout)
            else:
                reply = telegram_post_file(token, "sendPhoto", params, "photo", path_obj, timeout)
            if not reply.get("ok"):
                raise RuntimeError(f"telegram sendPhoto failed: {json.dumps(reply, ensure_ascii=False)}")
        return

    if task == "video":
        sent = False
        urls = result.get("urls") or []
        for idx, url in enumerate(urls, start=1):
            params = {
                "chat_id": chat_id,
                "video": url,
                "caption": caption if idx == 1 else None,
            }
            reply = telegram_post_form(token, "sendVideo", params, timeout)
            if reply.get("ok"):
                sent = True
                break

        if not sent:
            text = result.get("text") or "视频已生成，但上游未返回直链。"
            msg = f"{caption}\\n{text}"[:3500]
            reply = telegram_post_form(token, "sendMessage", {"chat_id": chat_id, "text": msg}, timeout)
            if not reply.get("ok"):
                raise RuntimeError(f"telegram sendMessage failed: {json.dumps(reply, ensure_ascii=False)}")
        return

    if task == "code":
        text = (result.get("text") or "(empty)")[:3500]
        reply = telegram_post_form(
            token,
            "sendMessage",
            {"chat_id": chat_id, "text": f"[{task}] {model}\\n{text}"},
            timeout,
        )
        if not reply.get("ok"):
            raise RuntimeError(f"telegram sendMessage failed: {json.dumps(reply, ensure_ascii=False)}")


def print_result(result: dict, as_json: bool) -> None:
    if as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    task = result.get("task")
    model = result.get("model", "")

    if task == "code":
        text = result.get("text") or ""
        if text:
            print(text)
        else:
            print(json.dumps(result.get("raw", {}), ensure_ascii=False, indent=2))
        if result.get("fallbackFrom"):
            print(f"[fallback] {result['fallbackFrom']} -> {result['model']}")
        return

    if task in {"image", "edit"}:
        print(f"{task.capitalize()} model: {model}")
        for file_path in (result.get("files") or []):
            print(file_path)
        return

    if task == "video":
        print(f"Video model: {model}")
        urls = result.get("urls") or []
        text = result.get("text") or ""
        attempts_used = result.get("attemptsUsed")
        if attempts_used:
            print(f"Video attempts: {attempts_used}")
        if urls:
            for url in urls:
                print(url)
        if text:
            print(text)
        if not urls and not text:
            print(json.dumps(result.get("raw", {}), ensure_ascii=False, indent=2))
        return

    print(json.dumps(result, ensure_ascii=False, indent=2))


def validate_lane_config(task: str, settings: dict) -> tuple[bool, str]:
    if task == "code":
        base_url = settings.get("code_base_url", "")
        api_key = settings.get("code_api_key", "")
        fb_model = settings.get("code_fallback_model", "")
        fb_base = settings.get("code_fallback_base_url", "")
        fb_key = settings.get("code_fallback_api_key", "")
        if not base_url and not (fb_model and fb_base and fb_key):
            return False, "Missing code base URL. Set ROUTER_CODE_BASE_URL or ROUTER_CODE_FALLBACK_*"
        if not api_key and not (fb_model and fb_base and fb_key):
            return False, "Missing code API key. Set ROUTER_CODE_API_KEY or ROUTER_CODE_FALLBACK_*"
        return True, ""

    lane = {
        "image": (settings.get("image_base_url", ""), settings.get("image_api_key", "")),
        "edit": (settings.get("edit_base_url", ""), settings.get("edit_api_key", "")),
        "video": (settings.get("video_base_url", ""), settings.get("video_api_key", "")),
    }[task]

    base_url, api_key = lane
    if not base_url:
        return False, f"Missing {task} base URL. Set ROUTER_{task.upper()}_BASE_URL or ROUTER_BASE_URL"
    if not api_key:
        return False, f"Missing {task} API key. Set ROUTER_{task.upper()}_API_KEY or ROUTER_API_KEY"
    return True, ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Auto-route prompt to code/image/edit/video model")
    parser.add_argument("--task", choices=["auto", "code", "image", "edit", "video"], default="auto")
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--image-input", default="", help="Input image path or URL for --task edit")
    parser.add_argument("--size", default="1024x1024")
    parser.add_argument("--quality", default="high")
    parser.add_argument("--count", type=int, default=1)
    parser.add_argument("--video-duration", type=int, default=4)
    parser.add_argument("--video-size", default="")
    parser.add_argument("--out-dir", default="")
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--telegram",
        choices=["auto", "on", "off"],
        default="auto",
        help="auto: controlled by ROUTER_SEND_TELEGRAM; on: always send; off: never send",
    )
    args = parser.parse_args()

    settings = resolve_runtime_settings()
    dot = settings.get("dot") or {}
    task = detect_task(args.prompt) if args.task == "auto" else args.task

    preview = {
        "task": task,
        "provider": settings.get("provider", ""),
        "code_model": settings.get("code_model", ""),
        "code_fallback_model": settings.get("code_fallback_model", ""),
        "image_model": settings.get("image_model", ""),
        "edit_model": settings.get("edit_model", ""),
        "video_model": settings.get("video_model", ""),
        "code_base_url": settings.get("code_base_url", ""),
        "code_fallback_base_url": settings.get("code_fallback_base_url", ""),
        "image_base_url": settings.get("image_base_url", ""),
        "edit_base_url": settings.get("edit_base_url", ""),
        "video_base_url": settings.get("video_base_url", ""),
        "video_retry_attempts": settings.get("video_retry_attempts", 1),
        "video_retry_delay": settings.get("video_retry_delay", 6),
        "telegram_chat_id": env_or_dot("TELEGRAM_CHAT_ID", dot) or extract_telegram_chat_id_from_sessions(),
    }

    if args.dry_run:
        print(json.dumps(preview, ensure_ascii=False, indent=2))
        return 0

    if task == "edit" and not args.image_input.strip():
        print("edit task requires --image-input (file path or URL)", file=sys.stderr)
        return 2

    ok, message = validate_lane_config(task, settings)
    if not ok:
        print(message, file=sys.stderr)
        return 2

    try:
        if task == "code":
            result = run_code(settings, args.prompt, args.timeout)
        elif task == "image":
            result = run_image(settings, args.prompt, args.size, args.quality, args.count, args.timeout, args.out_dir)
        elif task == "edit":
            result = run_edit(
                settings,
                args.prompt,
                args.image_input,
                args.size,
                args.quality,
                args.timeout,
                args.out_dir,
            )
        elif task == "video":
            result = run_video(settings, args.prompt, args.video_duration, args.video_size, args.timeout)
        else:
            raise RuntimeError(f"Unsupported task: {task}")
    except Exception as exc:
        print(f"dispatch failed: {exc}", file=sys.stderr)
        return 1

    result["resolved"] = preview
    print_result(result, args.json)

    auto_send = truthy(env_or_dot("ROUTER_SEND_TELEGRAM", dot, "0"))
    should_send = False
    if args.telegram == "on":
        should_send = True
    elif args.telegram == "off":
        should_send = False
    else:
        should_send = auto_send and task in {"image", "edit", "video"}

    if should_send:
        try:
            telegram_send_result(settings, result, args.prompt, min(args.timeout, 120))
            print("[telegram] delivered")
        except Exception as exc:
            print(f"telegram delivery failed: {exc}", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
