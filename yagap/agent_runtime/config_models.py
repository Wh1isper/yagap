from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, model_validator


class InvalidSessionBackendConfigError(ValueError):
    def __init__(self) -> None:
        super().__init__("session_s3_bucket is required when session_backend='s3'")


class RuntimeConfig(BaseModel):
    model: str = "anthropic:claude-sonnet-4-5"
    max_tool_calls: int = 10000

    steering_enabled: bool = True
    async_notifications_enabled: bool = True

    sse_ping_interval: float = 15.0

    session_backend: Literal["local", "s3"] = "local"
    session_local_storage_path: str = "./sessions"
    session_s3_bucket: str | None = None
    session_s3_prefix: str = "sessions/"

    @model_validator(mode="after")
    def validate_session_backend(self) -> RuntimeConfig:
        if self.session_backend == "s3" and not self.session_s3_bucket:
            raise InvalidSessionBackendConfigError()
        return self


class RuntimeConfigPatch(BaseModel):
    model: str | None = None
    max_tool_calls: int | None = None

    steering_enabled: bool | None = None
    async_notifications_enabled: bool | None = None

    sse_ping_interval: float | None = None

    session_backend: Literal["local", "s3"] | None = None
    session_local_storage_path: str | None = None
    session_s3_bucket: str | None = None
    session_s3_prefix: str | None = None

    def to_dict(self) -> dict[str, object]:
        return self.model_dump(exclude_none=True)
