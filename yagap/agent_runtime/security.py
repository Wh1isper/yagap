from __future__ import annotations

import secrets
from collections.abc import Callable

from fastapi import Request, status
from fastapi.responses import JSONResponse


def resolve_auth_token(configured_token: str | None) -> tuple[str, bool]:
    """Return active auth token and whether it was generated at runtime."""
    if configured_token:
        return configured_token, False
    return secrets.token_urlsafe(24), True


def build_auth_middleware(
    *,
    auth_header_name: str,
    get_active_token: Callable[[], str],
):
    async def auth_middleware(request: Request, call_next):
        if request.url.path in {"/health", "/docs", "/openapi.json", "/redoc"}:
            return await call_next(request)

        incoming = request.headers.get(auth_header_name, "")
        active_token = get_active_token()

        accepted = {active_token, f"Bearer {active_token}"}
        if incoming not in accepted:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": "unauthorized"},
            )

        return await call_next(request)

    return auth_middleware
