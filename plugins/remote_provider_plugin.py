"""RemoteProviderPlugin — capability plugin for remote execution providers.

Manages registration, discovery, and selection of remote execution
providers.  Provides a `RemoteProvider` abstract base and a reference
`LocalProvider` implementation.

Does not modify Execution Platform, Batch Execution, or Plugin
Framework contracts.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from plugins.plugin import Plugin, PluginMetadata
from plugins.plugin_capability import PluginCapability
from plugins.plugin_context import PluginContext


# ── RemoteProvider ABC ─────────────────────────────────────────────


class RemoteProvider(ABC):
    """Abstract base for remote execution providers.

    A provider accepts execution requests and returns results.
    Implementations may be local stubs, remote API clients,
    cloud backends, etc.

    Subclasses must implement: name, execute(), is_available().
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique provider identifier (e.g. 'local', 'aws-batch')."""
        ...

    @abstractmethod
    def execute(self, request: dict) -> dict:
        """Execute a request and return the result.

        The request dict is opaque to the plugin — structure is
        defined by the provider implementation.
        """
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if the provider is ready to accept requests."""
        ...

    @property
    def metadata(self) -> dict:
        """Arbitrary provider metadata for discovery."""
        return {"name": self.name}


# ── Reference Provider ─────────────────────────────────────────────


class LocalProvider(RemoteProvider):
    """Reference provider — executes request locally (no-op)."""

    @property
    def name(self) -> str:
        return "local"

    def execute(self, request: dict) -> dict:
        return {"status": "ok", "provider": "local", "request": request}

    def is_available(self) -> bool:
        return True


# ── Result types ───────────────────────────────────────────────────


@dataclass(frozen=True)
class ProviderInfo:
    """Read-only snapshot of a registered provider."""

    name: str
    available: bool
    metadata: dict = field(default_factory=dict)


# ── Plugin ─────────────────────────────────────────────────────────


class RemoteProviderPlugin(Plugin):
    """Manages remote execution provider registration and discovery.

    Usage:
        plugin = RemoteProviderPlugin()
        registry.register(plugin)
        registry.enable(plugin.name)
        registry.activate(plugin.name)

        plugin.register_provider(LocalProvider())

        provider = plugin.select("local")
        result = provider.execute({"action": "ping"})

    Capability: EXECUTION_HOOK — remote provider management is an
    execution orchestration concern.
    """

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="ruleforge.remote-provider",
            version="1.0.0",
            description="Manages remote execution provider registration and discovery",
            author="RuleForge",
            capabilities=(PluginCapability.EXECUTION_HOOK,),
        )

    def __init__(self) -> None:
        self._providers: dict[str, RemoteProvider] = {}

    def on_activate(self, ctx: PluginContext) -> None:
        pass

    def on_deactivate(self, ctx: PluginContext) -> None:
        # Keep providers registered — deactivation does not
        # destroy provider state (following Lifecycle vs Business
        # State separation established in M12-D).
        pass

    # ── Provider management ────────────────────────────────────

    def register_provider(self, provider: RemoteProvider) -> None:
        """Register a remote execution provider.

        Raises ValueError if a provider with the same name is
        already registered.
        """
        name = provider.name
        if name in self._providers:
            raise ValueError(
                f"Provider '{name}' is already registered"
            )
        self._providers[name] = provider

    def unregister_provider(self, name: str) -> bool:
        """Unregister a provider by name.  Returns True if removed."""
        return self._providers.pop(name, None) is not None

    def list_providers(self) -> list[ProviderInfo]:
        """Return a snapshot of all registered providers."""
        return [
            ProviderInfo(
                name=p.name,
                available=p.is_available(),
                metadata=p.metadata,
            )
            for p in self._providers.values()
        ]

    def get_provider(self, name: str) -> RemoteProvider | None:
        """Return a provider by name, or None."""
        return self._providers.get(name)

    def select(self, name: str) -> RemoteProvider:
        """Select a provider by name.

        Raises KeyError if not found.
        Raises RuntimeError if the provider is not available.
        """
        provider = self._providers.get(name)
        if provider is None:
            raise KeyError(f"Provider '{name}' not found")
        if not provider.is_available():
            raise RuntimeError(f"Provider '{name}' is not available")
        return provider

    @property
    def provider_count(self) -> int:
        return len(self._providers)
