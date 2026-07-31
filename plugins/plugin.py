"""Plugin — abstract base and immutable metadata for all plugins."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from plugins.plugin_capability import PluginCapability
from plugins.plugin_context import PluginContext


@dataclass(frozen=True)
class PluginMetadata:
    """Immutable plugin descriptor.

    Fields:
        name: Unique identifier within the registry.
        version: Semver-compatible version string.
        description: Human-readable summary.
        author: Plugin author or maintainer.
        capabilities: Declared capabilities this plugin provides.
        dependencies: Plugin names this plugin depends on.
    """

    name: str
    version: str
    description: str = ""
    author: str = ""
    capabilities: tuple[PluginCapability, ...] = ()
    dependencies: tuple[str, ...] = ()


class Plugin(ABC):
    """Abstract base for all RuleForge plugins.

    Lifecycle hooks have default no-op implementations — plugins
    override only what they need:

        discover → load → initialize → activate → deactivate → unload

    Plugin failures are contained: a failing lifecycle hook does not
    crash the host or prevent other plugins from operating.
    """

    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Return the plugin's immutable metadata descriptor."""
        ...

    def on_discover(self, ctx: PluginContext) -> None:
        """Called when the plugin is first registered.

        Use for lightweight introspection — no heavy init here.
        """

    def on_load(self, ctx: PluginContext) -> None:
        """Called after discovery, before initialization.

        Use for loading configuration, parsing manifests, etc.
        """

    def on_initialize(self, ctx: PluginContext) -> None:
        """Called after load, before the plugin is marked as ready.

        Use for establishing connections, warming caches, etc.
        """

    def on_activate(self, ctx: PluginContext) -> None:
        """Called when the plugin transitions to ACTIVE state.

        The plugin should be ready to receive hook invocations
        after this returns.
        """

    def on_deactivate(self, ctx: PluginContext) -> None:
        """Called when the plugin transitions out of ACTIVE state.

        Release active resources but keep the plugin loaded for
        potential re-activation.
        """

    def on_unload(self, ctx: PluginContext) -> None:
        """Called when the plugin is unregistered.

        Final cleanup — release all resources.
        """

    @property
    def name(self) -> str:
        return self.metadata.name

    @property
    def version(self) -> str:
        return self.metadata.version
