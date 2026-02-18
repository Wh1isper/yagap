from __future__ import annotations

import uvicorn

from yagap.gateway.config import get_settings


def start_gateway(host: str | None = None, port: int | None = None) -> None:
    from yagap.gateway.app import app

    settings = get_settings()
    uvicorn.run(
        app,
        host=host or settings.host,
        port=port or settings.port,
        timeout_graceful_shutdown=3600,
        access_log=False,
    )
