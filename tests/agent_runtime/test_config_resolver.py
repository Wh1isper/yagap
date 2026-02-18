import pytest

from yagap.agent_runtime.config_models import RuntimeConfig, RuntimeConfigPatch
from yagap.agent_runtime.config_registry import (
    ModelProfile,
    RuntimeConfigRegistry,
    RuntimePreset,
    UnknownModelProfileError,
    UnknownRuntimePresetError,
)
from yagap.agent_runtime.config_resolver import RuntimeConfigResolver


def test_runtime_config_resolver_priority_order():
    resolver = RuntimeConfigResolver()
    default = RuntimeConfig(model="default-model", max_tool_calls=100, steering_enabled=True)

    service = RuntimeConfigPatch(model="service-model", max_tool_calls=200)
    gateway = RuntimeConfigPatch(model="gateway-model")
    override = RuntimeConfigPatch(max_tool_calls=300, steering_enabled=False)

    resolved = resolver.resolve(
        default=default,
        preset_name="fast",
        service_runtime_config=service,
        gateway_runtime_input=gateway,
        run_override=override,
    )

    assert resolved.model == "gateway-model"
    assert resolved.max_tool_calls == 300
    assert resolved.steering_enabled is False


def test_runtime_config_requires_s3_bucket_when_s3_backend():
    resolver = RuntimeConfigResolver()
    default = RuntimeConfig()

    with pytest.raises(ValueError):
        resolver.resolve(
            default=default,
            run_override=RuntimeConfigPatch(session_backend="s3"),
        )


def test_runtime_config_resolver_applies_runtime_preset():
    resolver = RuntimeConfigResolver()
    default = RuntimeConfig(model="default-model", max_tool_calls=100)

    resolved = resolver.resolve(default=default, preset_name="fast")

    assert resolved.model == "anthropic:claude-4-5-haiku-latest"
    assert resolved.sse_ping_interval == 10.0


def test_runtime_config_resolver_raises_for_unknown_preset():
    resolver = RuntimeConfigResolver()
    default = RuntimeConfig()

    with pytest.raises(UnknownRuntimePresetError):
        resolver.resolve(default=default, preset_name="unknown")


def test_runtime_config_resolver_raises_for_unknown_model_profile():
    registry = RuntimeConfigRegistry(
        model_profiles={"default": ModelProfile(name="default", model="anthropic:claude-sonnet-4-5")},
        runtime_presets={"broken": RuntimePreset(name="broken", model_profile="missing")},
    )
    resolver = RuntimeConfigResolver(registry=registry)

    with pytest.raises(UnknownModelProfileError):
        resolver.resolve(default=RuntimeConfig(), preset_name="broken")
