from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

from yagap.agent_runtime.config_models import RuntimeConfig, RuntimeConfigPatch
from yagap.agent_runtime.config_registry import RuntimeConfigRegistry, build_default_registry


class AgentRuntimeSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="YAGAP_AGENT_RUNTIME_", case_sensitive=False)

    host: str = "0.0.0.0"  # noqa: S104
    port: int = 8001
    log_level: str = "INFO"

    auth_header_name: str = "Authorization"
    auth_token: str | None = None

    runtime_default_model: str = "anthropic:claude-sonnet-4-5"
    runtime_max_tool_calls: int = 10000

    session_backend: Literal["local", "s3"] = "local"
    session_local_storage_path: str = "./sessions"
    session_s3_bucket: str | None = None
    session_s3_prefix: str = "sessions/"

    def build_default_runtime_config(self) -> RuntimeConfig:
        return RuntimeConfig(
            model=self.runtime_default_model,
            max_tool_calls=self.runtime_max_tool_calls,
            session_backend=self.session_backend,
            session_local_storage_path=self.session_local_storage_path,
            session_s3_bucket=self.session_s3_bucket,
            session_s3_prefix=self.session_s3_prefix,
        )

    def build_service_runtime_patch(self) -> RuntimeConfigPatch:
        return RuntimeConfigPatch(
            model=self.runtime_default_model,
            max_tool_calls=self.runtime_max_tool_calls,
            session_backend=self.session_backend,
            session_local_storage_path=self.session_local_storage_path,
            session_s3_bucket=self.session_s3_bucket,
            session_s3_prefix=self.session_s3_prefix,
        )


@lru_cache
def get_settings() -> AgentRuntimeSettings:
    return AgentRuntimeSettings()


@lru_cache
def get_runtime_registry() -> RuntimeConfigRegistry:
    return build_default_registry()
