"""PluginRegistry — unified registry for plugin management.

Zero dependencies on engine/, models/, or any execution subsystem.
Manages registration, lifecycle, enable/disable, and capability queries.
"""

from __future__ import annotations

from enum import Enum, auto

from plugins.plugin import Plugin, PluginMetadata
from plugins.plugin_capability import PluginCapability
from plugins.plugin_context import PluginContext
from plugins.plugin_errors import (
    PluginDependencyError,
    PluginLifecycleError,
    PluginNotFoundError,
)


class _PluginState(Enum):
    """Internal lifecycle states for registered plugins."""

    LOADED = auto()
    ENABLED = auto()
    ACTIVE = auto()


class PluginRegistry:
    """Central registry for plugin management.

    Usage:
        registry = PluginRegistry()
        registry.register(MyPlugin())
        registry.enable("my-plugin")
        registry.activate("my-plugin")

        hooks = registry.list_by_capability(PluginCapability.EXECUTION_HOOK)
    """

    def __init__(self) -> None:
        self._plugins: dict[str, Plugin] = {}
        self._states: dict[str, _PluginState] = {}

    # ── Registration ──────────────────────────────────────────────

    def register(self, plugin: Plugin) -> None:
        """Register a plugin instance.

        Runs the early lifecycle: discover → load → initialize.
        Plugin starts in LOADED state.

        Raises ValueError if a plugin with the same name is
        already registered.
        """
        name = plugin.name
        if name in self._plugins:
            raise ValueError(f"Plugin '{name}' is already registered")
        ctx = PluginContext(registry=self)
        plugin.on_discover(ctx)
        plugin.on_load(ctx)
        plugin.on_initialize(ctx)
        self._plugins[name] = plugin
        self._states[name] = _PluginState.LOADED

    def unregister(self, name: str) -> None:
        """Unregister a plugin.

        Runs deactivate → unload lifecycle, then removes the plugin.
        """
        plugin = self._require(name)
        ctx = PluginContext(registry=self)
        if self._states[name] == _PluginState.ACTIVE:
            plugin.on_deactivate(ctx)
        plugin.on_unload(ctx)
        del self._plugins[name]
        del self._states[name]

    # ── Lifecycle ─────────────────────────────────────────────────

    def enable(self, name: str) -> None:
        """Enable a plugin (LOADED → ENABLED).

        Validates that all declared dependencies are registered
        and enabled.  Raises PluginDependencyError if not.
        """
        self._require(name)
        if self._states[name] != _PluginState.LOADED:
            raise PluginLifecycleError(name, self._states[name].name, "ENABLED")
        self._validate_dependencies(name)
        self._states[name] = _PluginState.ENABLED

    def disable(self, name: str) -> None:
        """Disable a plugin (any state → LOADED).

        If ACTIVE, runs deactivate first.  State returns to LOADED.
        Does not raise if already LOADED (idempotent).
        """
        plugin = self._require(name)
        state = self._states[name]
        if state == _PluginState.LOADED:
            return
        if state == _PluginState.ACTIVE:
            ctx = PluginContext(registry=self)
            plugin.on_deactivate(ctx)
        self._states[name] = _PluginState.LOADED

    def activate(self, name: str) -> None:
        """Activate a plugin (ENABLED → ACTIVE).

        Calls on_activate().  Plugin fires are contained — a
        failing on_activate keeps the plugin in ENABLED state.
        """
        plugin = self._require(name)
        if self._states[name] != _PluginState.ENABLED:
            raise PluginLifecycleError(name, self._states[name].name, "ACTIVE")
        ctx = PluginContext(registry=self)
        plugin.on_activate(ctx)
        self._states[name] = _PluginState.ACTIVE

    def deactivate(self, name: str) -> None:
        """Deactivate a plugin (ACTIVE → ENABLED).

        Calls on_deactivate().  Idempotent if not ACTIVE.
        """
        plugin = self._require(name)
        if self._states[name] != _PluginState.ACTIVE:
            return
        ctx = PluginContext(registry=self)
        plugin.on_deactivate(ctx)
        self._states[name] = _PluginState.ENABLED

    # ── Queries ───────────────────────────────────────────────────

    def get(self, name: str) -> Plugin | None:
        """Return the plugin by name, or None if not registered."""
        return self._plugins.get(name)

    def list_all(self) -> list[Plugin]:
        """Return all registered plugins."""
        return list(self._plugins.values())

    def list_by_capability(
        self, capability: PluginCapability
    ) -> list[Plugin]:
        """Return enabled plugins that declare the given capability.

        Only ENABLED and ACTIVE plugins are returned — LOADED
        plugins are excluded.
        """
        result: list[Plugin] = []
        for name, plugin in self._plugins.items():
            state = self._states[name]
            if state not in (_PluginState.ENABLED, _PluginState.ACTIVE):
                continue
            if capability in plugin.metadata.capabilities:
                result.append(plugin)
        return result

    def is_enabled(self, name: str) -> bool:
        """Return True if the plugin is ENABLED or ACTIVE."""
        state = self._states.get(name)
        return state in (_PluginState.ENABLED, _PluginState.ACTIVE)

    def is_active(self, name: str) -> bool:
        """Return True if the plugin is ACTIVE."""
        return self._states.get(name) == _PluginState.ACTIVE

    def state(self, name: str) -> str:
        """Return the plugin's state name as a string."""
        s = self._states.get(name)
        return s.name if s else "UNKNOWN"

    @property
    def registered_count(self) -> int:
        return len(self._plugins)

    # ── Helpers ───────────────────────────────────────────────────

    def _require(self, name: str) -> Plugin:
        plugin = self._plugins.get(name)
        if plugin is None:
            raise PluginNotFoundError(name)
        return plugin

    def _validate_dependencies(self, name: str) -> None:
        plugin = self._require(name)
        for dep_name in plugin.metadata.dependencies:
            if dep_name not in self._plugins:
                raise PluginDependencyError(name, dep_name)
            dep_state = self._states[dep_name]
            if dep_state not in (_PluginState.ENABLED, _PluginState.ACTIVE):
                raise PluginDependencyError(
                    name,
                    f"{dep_name} (state: {dep_state.name})",
                )
