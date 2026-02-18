from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sse_starlette.sse import AppStatus

from yagap.agent_runtime.config import get_settings
from yagap.agent_runtime.security import build_auth_middleware, resolve_auth_token
from yagap.shared.logging import setup_logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    setup_logging(settings.log_level)

    active_token, generated = resolve_auth_token(settings.auth_token)
    app.state.active_auth_token = active_token

    if generated:
        logger.warning("Agent runtime auth token not configured. Generated bootstrap token: %s", active_token)

    # Let SSE streams drain naturally on shutdown.
    AppStatus.disable_automatic_graceful_drain()

    yield


app = FastAPI(title="yagap-agent-runtime", lifespan=lifespan)

app.middleware("http")(
    build_auth_middleware(
        auth_header_name=get_settings().auth_header_name,
        get_active_token=lambda: app.state.active_auth_token,
    )
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
