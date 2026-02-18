from __future__ import annotations

from yagap.agent_runtime.config_models import RuntimeConfig, RuntimeConfigPatch
from yagap.agent_runtime.config_registry import RuntimeConfigRegistry, build_default_registry


class RuntimeConfigResolver:
    """Merge runtime config patches with deterministic priority.

    Priority:
    run_override > gateway_runtime_input > runtime_preset > service_runtime_config > default
    """

    def __init__(self, registry: RuntimeConfigRegistry | None = None) -> None:
        self._registry = registry or build_default_registry()

    def _build_preset_patch(self, preset_name: str) -> RuntimeConfigPatch:
        preset = self._registry.get_preset(preset_name)
        profile = self._registry.get_model_profile(preset.model_profile)

        max_tool_calls = preset.max_tool_calls
        if max_tool_calls is None:
            max_tool_calls = profile.max_tool_calls

        return RuntimeConfigPatch(
            model=profile.model,
            max_tool_calls=max_tool_calls,
            steering_enabled=preset.steering_enabled,
            async_notifications_enabled=preset.async_notifications_enabled,
            sse_ping_interval=preset.sse_ping_interval,
        )

    def resolve(
        self,
        *,
        default: RuntimeConfig,
        service_runtime_config: RuntimeConfigPatch | None = None,
        preset_name: str | None = None,
        gateway_runtime_input: RuntimeConfigPatch | None = None,
        run_override: RuntimeConfigPatch | None = None,
    ) -> RuntimeConfig:
        merged = default.model_dump()

        patch_order: list[RuntimeConfigPatch | None] = [service_runtime_config]
        if preset_name is not None:
            patch_order.append(self._build_preset_patch(preset_name))
        patch_order.extend([gateway_runtime_input, run_override])

        for patch in patch_order:
            if patch is None:
                continue
            merged.update(patch.to_dict())

        return RuntimeConfig.model_validate(merged)
