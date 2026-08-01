"""Tests for M12-F RemoteProviderPlugin — remote provider management."""

from __future__ import annotations

import pytest

from plugins.plugin_capability import PluginCapability
from plugins.plugin_registry import PluginRegistry
from plugins.remote_provider_plugin import (
    LocalProvider,
    ProviderInfo,
    RemoteProvider,
    RemoteProviderPlugin,
)


# ── Helpers ───────────────────────────────────────────────────────


class _StubProvider(RemoteProvider):
    """Test provider with controllable availability."""

    def __init__(self, name: str = "stub", available: bool = True) -> None:
        self._name = name
        self._available = available
        self._calls: list[dict] = []

    @property
    def name(self) -> str:
        return self._name

    def execute(self, request: dict) -> dict:
        self._calls.append(request)
        return {"status": "stub", "echo": request}

    def is_available(self) -> bool:
        return self._available


class _UnavailableProvider(RemoteProvider):
    """Provider that is never available."""

    @property
    def name(self) -> str:
        return "offline"

    def execute(self, request: dict) -> dict:
        return {"status": "never-reached"}

    def is_available(self) -> bool:
        return False


# ── Plugin metadata & lifecycle ───────────────────────────────────


class TestRemoteProviderPluginMetadata:
    def test_name(self) -> None:
        p = RemoteProviderPlugin()
        assert p.name == "ruleforge.remote-provider"

    def test_version(self) -> None:
        p = RemoteProviderPlugin()
        assert p.version == "1.0.0"

    def test_capability(self) -> None:
        p = RemoteProviderPlugin()
        assert PluginCapability.EXECUTION_HOOK in p.metadata.capabilities

    def test_dependencies(self) -> None:
        p = RemoteProviderPlugin()
        assert p.metadata.dependencies == ()


class TestRemoteProviderPluginLifecycle:
    def test_full_lifecycle_in_registry(self) -> None:
        reg = PluginRegistry()
        reg.register(RemoteProviderPlugin())
        assert reg.state("ruleforge.remote-provider") == "LOADED"
        reg.enable("ruleforge.remote-provider")
        assert reg.state("ruleforge.remote-provider") == "ENABLED"
        reg.activate("ruleforge.remote-provider")
        assert reg.state("ruleforge.remote-provider") == "ACTIVE"
        reg.deactivate("ruleforge.remote-provider")
        assert reg.state("ruleforge.remote-provider") == "ENABLED"

    def test_discovery_via_capability(self) -> None:
        reg = PluginRegistry()
        reg.register(RemoteProviderPlugin())
        reg.enable("ruleforge.remote-provider")
        plugins = reg.list_by_capability(PluginCapability.EXECUTION_HOOK)
        assert any(p.name == "ruleforge.remote-provider" for p in plugins)

    def test_not_found_when_loaded_only(self) -> None:
        reg = PluginRegistry()
        reg.register(RemoteProviderPlugin())
        assert (
            reg.list_by_capability(PluginCapability.EXECUTION_HOOK) == []
        )

    def test_providers_persist_after_deactivation(self) -> None:
        reg = PluginRegistry()
        reg.register(RemoteProviderPlugin())
        reg.enable("ruleforge.remote-provider")
        reg.activate("ruleforge.remote-provider")

        plugin = reg.get("ruleforge.remote-provider")
        assert plugin is not None
        plugin.register_provider(LocalProvider())

        reg.deactivate("ruleforge.remote-provider")
        assert plugin.provider_count == 1


# ── Provider Registration ─────────────────────────────────────────


class TestProviderRegistration:
    def test_register_provider(self) -> None:
        p = RemoteProviderPlugin()
        p.register_provider(LocalProvider())
        assert p.provider_count == 1

    def test_register_duplicate_raises(self) -> None:
        p = RemoteProviderPlugin()
        p.register_provider(LocalProvider())
        with pytest.raises(ValueError, match="already registered"):
            p.register_provider(LocalProvider())

    def test_unregister_provider(self) -> None:
        p = RemoteProviderPlugin()
        p.register_provider(LocalProvider())
        removed = p.unregister_provider("local")
        assert removed
        assert p.provider_count == 0

    def test_unregister_nonexistent_returns_false(self) -> None:
        p = RemoteProviderPlugin()
        assert p.unregister_provider("nope") is False

    def test_register_multiple_providers(self) -> None:
        p = RemoteProviderPlugin()
        p.register_provider(LocalProvider())
        p.register_provider(_StubProvider("alpha"))
        p.register_provider(_StubProvider("beta"))
        assert p.provider_count == 3

    def test_register_unavailable_provider(self) -> None:
        p = RemoteProviderPlugin()
        p.register_provider(_UnavailableProvider())
        assert p.provider_count == 1
        # Registered but not available
        info = p.list_providers()[0]
        assert info.name == "offline"
        assert not info.available


# ── Provider Discovery & Selection ─────────────────────────────────


class TestProviderDiscovery:
    def test_list_providers(self) -> None:
        p = RemoteProviderPlugin()
        p.register_provider(LocalProvider())
        p.register_provider(_StubProvider("stub"))
        providers = p.list_providers()
        assert len(providers) == 2
        names = {pr.name for pr in providers}
        assert names == {"local", "stub"}

    def test_list_providers_empty(self) -> None:
        p = RemoteProviderPlugin()
        assert p.list_providers() == []

    def test_get_provider(self) -> None:
        p = RemoteProviderPlugin()
        p.register_provider(LocalProvider())
        pr = p.get_provider("local")
        assert pr is not None
        assert pr.name == "local"

    def test_get_nonexistent_returns_none(self) -> None:
        p = RemoteProviderPlugin()
        assert p.get_provider("missing") is None

    def test_provider_info_includes_availability(self) -> None:
        p = RemoteProviderPlugin()
        p.register_provider(LocalProvider())
        info = p.list_providers()[0]
        assert info.name == "local"
        assert info.available is True
        assert isinstance(info.metadata, dict)


# ── Provider Execution ────────────────────────────────────────────


class TestProviderExecution:
    def test_local_provider_execute(self) -> None:
        provider = LocalProvider()
        result = provider.execute({"action": "test"})
        assert result["status"] == "ok"
        assert result["provider"] == "local"
        assert result["request"]["action"] == "test"

    def test_stub_provider_execute(self) -> None:
        provider = _StubProvider("echo")
        result = provider.execute({"key": "val"})
        assert result["status"] == "stub"
        assert result["echo"]["key"] == "val"

    def test_select_and_execute(self) -> None:
        p = RemoteProviderPlugin()
        p.register_provider(LocalProvider())
        provider = p.select("local")
        result = provider.execute({"op": "ping"})
        assert result["status"] == "ok"

    def test_select_nonexistent_raises(self) -> None:
        p = RemoteProviderPlugin()
        with pytest.raises(KeyError, match="not found"):
            p.select("missing")

    def test_select_unavailable_raises(self) -> None:
        p = RemoteProviderPlugin()
        p.register_provider(_UnavailableProvider())
        with pytest.raises(RuntimeError, match="not available"):
            p.select("offline")


# ── RemoteProvider ABC ────────────────────────────────────────────


class TestRemoteProviderABC:
    def test_cannot_instantiate_abc(self) -> None:
        with pytest.raises(TypeError):
            RemoteProvider()  # type: ignore[abstract]

    def test_local_provider_is_remote_provider(self) -> None:
        p = LocalProvider()
        assert isinstance(p, RemoteProvider)

    def test_stub_provider_is_remote_provider(self) -> None:
        p = _StubProvider()
        assert isinstance(p, RemoteProvider)

    def test_local_provider_always_available(self) -> None:
        assert LocalProvider().is_available()


# ── ProviderInfo dataclass ────────────────────────────────────────


class TestProviderInfo:
    def test_frozen(self) -> None:
        info = ProviderInfo(name="x", available=True, metadata={"k": "v"})
        assert info.name == "x"
        with pytest.raises(Exception):
            info.name = "y"  # type: ignore[misc]


# ── Plugin independence ───────────────────────────────────────────


class TestPluginIndependence:
    def test_no_engine_imports(self) -> None:
        import plugins.remote_provider_plugin as rp

        source = rp.__file__
        assert source is not None
        with open(source) as f:
            content = f.read()
        assert "from engine" not in content
        assert "import engine" not in content

    def test_standalone_usage_without_registry(self) -> None:
        p = RemoteProviderPlugin()
        p.register_provider(LocalProvider())
        assert p.provider_count == 1
        result = p.select("local").execute({"test": True})
        assert result["status"] == "ok"


# ── Full integration flow ─────────────────────────────────────────


class TestFullIntegrationFlow:
    def test_register_discover_select_execute(self) -> None:
        reg = PluginRegistry()
        reg.register(RemoteProviderPlugin())
        reg.enable("ruleforge.remote-provider")
        reg.activate("ruleforge.remote-provider")

        plugin = reg.get("ruleforge.remote-provider")
        assert plugin is not None

        # Register providers
        plugin.register_provider(LocalProvider())
        plugin.register_provider(_StubProvider("remote-1"))

        # Discover
        providers = plugin.list_providers()
        assert len(providers) == 2

        # Select and execute
        local = plugin.select("local")
        assert local.execute({"cmd": "status"})["status"] == "ok"

        remote = plugin.select("remote-1")
        assert remote.execute({"cmd": "exec"})["status"] == "stub"
