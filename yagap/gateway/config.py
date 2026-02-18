from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class GatewaySettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="YAGAP_GATEWAY_", case_sensitive=False)

    host: str = "0.0.0.0"  # noqa: S104
    port: int = 8000
    log_level: str = "INFO"


@lru_cache
def get_settings() -> GatewaySettings:
    return GatewaySettings()
