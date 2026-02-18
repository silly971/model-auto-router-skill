# model-auto-router-skill (Español)

## Overview

`model-auto-router-skill` enruta una solicitud a carriles de modelo dedicados:
`code`, `image`, `edit` y `video`.

## Features

- Enrutamiento por intención con `--task auto`.
- Ejecución forzada con `--task code|image|edit|video`.
- Entrega automática opcional a Telegram para resultados de imagen/edición/video.
- Validación segura con `--dry-run --json`.

## Install

1. Copia esta carpeta al directorio `skills/` de tu workspace de OpenClaw.
2. Verifica que existan `SKILL.md`, `scripts/dispatch.py` y `references/config.md`.
3. Reinicia OpenClaw gateway si es necesario para recargar el skill.

## Config

Usa las variables de entorno definidas en `references/config.md`.
Todos los valores de este repositorio son marcadores de posición.

## Security

- No subas claves API reales ni tokens de bot.
- No subas chat IDs reales.
- No subas URLs privadas/internas de servicios.
- Guarda secretos en variables de entorno o gestor de secretos.

## Usage

```bash
python3 {baseDir}/scripts/dispatch.py --task auto --prompt "Escribe una función en Python"
python3 {baseDir}/scripts/dispatch.py --task code --prompt "Refactoriza esta función"
python3 {baseDir}/scripts/dispatch.py --task image --prompt "Genera un póster" --size 1024x1024
```

## License

MIT. Ver `LICENSE`.
