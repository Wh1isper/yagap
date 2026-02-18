from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from yagap.gateway.config import get_settings
from yagap.shared.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    setup_logging(settings.log_level)
    yield


app = FastAPI(title="yagap-gateway", lifespan=lifespan)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
