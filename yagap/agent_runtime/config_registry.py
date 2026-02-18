from __future__ import annotations

from pydantic import BaseModel


class UnknownRuntimePresetError(ValueError):
    """Raised when runtime preset cannot be resolved."""

    def __init__(self, preset_name: str) -> None:
        super().__init__(f"Unknown runtime preset: {preset_name}")


class UnknownModelProfileError(ValueError):
    """Raised when model profile cannot be resolved."""

    def __init__(self, profile_name: str) -> None:
        super().__init__(f"Unknown model profile: {profile_name}")


class ModelProfile(BaseModel):
    name: str
    model: str
    max_tool_calls: int | None = None


class RuntimePreset(BaseModel):
    name: str
    model_profile: str
    max_tool_calls: int | None = None
    steering_enabled: bool | None = None
    async_notifications_enabled: bool | None = None
    sse_ping_interval: float | None = None


class RuntimeConfigRegistry(BaseModel):
    model_profiles: dict[str, ModelProfile]
    runtime_presets: dict[str, RuntimePreset]

    def get_preset(self, preset_name: str) -> RuntimePreset:
        preset = self.runtime_presets.get(preset_name)
        if preset is None:
            raise UnknownRuntimePresetError(preset_name)
        return preset

    def get_model_profile(self, profile_name: str) -> ModelProfile:
        profile = self.model_profiles.get(profile_name)
        if profile is None:
            raise UnknownModelProfileError(profile_name)
        return profile


def build_default_registry() -> RuntimeConfigRegistry:
    model_profiles = {
        "default": ModelProfile(name="default", model="anthropic:claude-sonnet-4-5", max_tool_calls=10000),
        "haiku": ModelProfile(name="haiku", model="anthropic:claude-4-5-haiku-latest", max_tool_calls=10000),
    }

    runtime_presets = {
        "default": RuntimePreset(name="default", model_profile="default"),
        "fast": RuntimePreset(name="fast", model_profile="haiku", sse_ping_interval=10.0),
    }

    return RuntimeConfigRegistry(model_profiles=model_profiles, runtime_presets=runtime_presets)
