"""Tests for M12-B Plugin / Extension Framework."""

from __future__ import annotations

import pytest

from plugins import (
    Plugin,
    PluginCapability,
    PluginContext,
    PluginDependencyError,
    PluginError,
    PluginLifecycleError,
    PluginMetadata,
    PluginNotFoundError,
    PluginRegistry,
)


# ── Test helpers ────────────────────────────────────────────────────


class _BasePlugin(Plugin):
    """Minimal plugin implementation for testing."""

    def __init__(
        self,
        name: str = "test-plugin",
        version: str = "1.0.0",
        capabilities: tuple[PluginCapability, ...] = (),
        dependencies: tuple[str, ...] = (),
    ) -> None:
        self._meta = PluginMetadata(
            name=name,
            version=version,
            capabilities=capabilities,
            dependencies=dependencies,
        )
        self.lifecycle_calls: list[str] = []

    @property
    def metadata(self) -> PluginMetadata:
        return self._meta

    def on_discover(self, ctx: PluginContext) -> None:
        self.lifecycle_calls.append("discover")

    def on_load(self, ctx: PluginContext) -> None:
        self.lifecycle_calls.append("load")

    def on_initialize(self, ctx: PluginContext) -> None:
        self.lifecycle_calls.append("initialize")

    def on_activate(self, ctx: PluginContext) -> None:
        self.lifecycle_calls.append("activate")

    def on_deactivate(self, ctx: PluginContext) -> None:
        self.lifecycle_calls.append("deactivate")

    def on_unload(self, ctx: PluginContext) -> None:
        self.lifecycle_calls.append("unload")


class _FailingActivatePlugin(_BasePlugin):
    def on_activate(self, ctx: PluginContext) -> None:
        self.lifecycle_calls.append("activate-fail")
        raise RuntimeError("activate failed")


# ── PluginMetadata ──────────────────────────────────────────────────


class TestPluginMetadata:
    def test_defaults(self) -> None:
        meta = PluginMetadata(name="p", version="1.0")
        assert meta.name == "p"
        assert meta.version == "1.0"
        assert meta.description == ""
        assert meta.author == ""
        assert meta.capabilities == ()
        assert meta.dependencies == ()

    def test_with_capabilities(self) -> None:
        meta = PluginMetadata(
            name="p",
            version="1.0",
            capabilities=(PluginCapability.EXECUTION_HOOK,),
        )
        assert PluginCapability.EXECUTION_HOOK in meta.capabilities

    def test_frozen(self) -> None:
        meta = PluginMetadata(name="p", version="1.0")
        with pytest.raises(Exception):
            meta.name = "other"  # type: ignore[misc]

    def test_equality(self) -> None:
        a = PluginMetadata(name="p", version="1.0")
        b = PluginMetadata(name="p", version="1.0")
        assert a == b


# ── Plugin ──────────────────────────────────────────────────────────


class TestPlugin:
    def test_name_property(self) -> None:
        p = _BasePlugin(name="my-plugin")
        assert p.name == "my-plugin"

    def test_version_property(self) -> None:
        p = _BasePlugin(version="2.3.4")
        assert p.version == "2.3.4"

    def test_default_lifecycle_noops(self) -> None:
        """Base Plugin lifecycle methods are no-ops, not abstract."""
        p = _BasePlugin()
        ctx = PluginContext()
        # Should not raise
        p.on_discover(ctx)
        p.on_load(ctx)
        p.on_initialize(ctx)
        p.on_activate(ctx)
        p.on_deactivate(ctx)
        p.on_unload(ctx)


# ── PluginContext ───────────────────────────────────────────────────


class TestPluginContext:
    def test_defaults(self) -> None:
        ctx = PluginContext()
        assert ctx.registry is None
        assert ctx.data == {}

    def test_with_registry(self) -> None:
        reg = PluginRegistry()
        ctx = PluginContext(registry=reg)
        assert ctx.registry is reg

    def test_with_data(self) -> None:
        ctx = PluginContext(data={"key": "value"})
        assert ctx.data["key"] == "value"

    def test_frozen(self) -> None:
        ctx = PluginContext()
        with pytest.raises(Exception):
            ctx.data = {}  # type: ignore[misc]


# ── PluginRegistry: Registration ────────────────────────────────────


class TestRegistryRegistration:
    def test_register_lifecycle_calls(self) -> None:
        reg = PluginRegistry()
        p = _BasePlugin()
        reg.register(p)
        assert p.lifecycle_calls == ["discover", "load", "initialize"]

    def test_register_state_loaded(self) -> None:
        reg = PluginRegistry()
        reg.register(_BasePlugin())
        assert reg.state("test-plugin") == "LOADED"

    def test_register_duplicate_raises(self) -> None:
        reg = PluginRegistry()
        reg.register(_BasePlugin())
        with pytest.raises(ValueError, match="already registered"):
            reg.register(_BasePlugin())

    def test_unregister_lifecycle_calls(self) -> None:
        reg = PluginRegistry()
        p = _BasePlugin()
        reg.register(p)
        p.lifecycle_calls.clear()
        reg.unregister("test-plugin")
        # LOADED → unload only (no deactivate since not active)
        assert "unload" in p.lifecycle_calls

    def test_unregister_active_calls_deactivate_then_unload(self) -> None:
        reg = PluginRegistry()
        p = _BasePlugin()
        reg.register(p)
        reg.enable("test-plugin")
        reg.activate("test-plugin")
        p.lifecycle_calls.clear()
        reg.unregister("test-plugin")
        assert p.lifecycle_calls == ["deactivate", "unload"]

    def test_unregister_not_found_raises(self) -> None:
        reg = PluginRegistry()
        with pytest.raises(PluginNotFoundError):
            reg.unregister("nonexistent")

    def test_get_returns_none_for_unknown(self) -> None:
        reg = PluginRegistry()
        assert reg.get("nonexistent") is None

    def test_list_all(self) -> None:
        reg = PluginRegistry()
        reg.register(_BasePlugin(name="a"))
        reg.register(_BasePlugin(name="b"))
        names = [p.name for p in reg.list_all()]
        assert sorted(names) == ["a", "b"]


# ── PluginRegistry: Lifecycle ───────────────────────────────────────


class TestRegistryLifecycle:
    def test_enable_transition(self) -> None:
        reg = PluginRegistry()
        reg.register(_BasePlugin())
        reg.enable("test-plugin")
        assert reg.state("test-plugin") == "ENABLED"

    def test_enable_without_register_raises(self) -> None:
        reg = PluginRegistry()
        with pytest.raises(PluginNotFoundError):
            reg.enable("nonexistent")

    def test_enable_twice_raises(self) -> None:
        reg = PluginRegistry()
        reg.register(_BasePlugin())
        reg.enable("test-plugin")
        with pytest.raises(PluginLifecycleError):
            reg.enable("test-plugin")

    def test_activate_transition(self) -> None:
        reg = PluginRegistry()
        p = _BasePlugin()
        reg.register(p)
        reg.enable("test-plugin")
        reg.activate("test-plugin")
        assert reg.state("test-plugin") == "ACTIVE"
        assert "activate" in p.lifecycle_calls

    def test_activate_without_enable_raises(self) -> None:
        reg = PluginRegistry()
        reg.register(_BasePlugin())
        with pytest.raises(PluginLifecycleError):
            reg.activate("test-plugin")

    def test_deactivate_transition(self) -> None:
        reg = PluginRegistry()
        p = _BasePlugin()
        reg.register(p)
        reg.enable("test-plugin")
        reg.activate("test-plugin")
        reg.deactivate("test-plugin")
        assert reg.state("test-plugin") == "ENABLED"
        assert "deactivate" in p.lifecycle_calls

    def test_deactivate_not_active_is_idempotent(self) -> None:
        reg = PluginRegistry()
        reg.register(_BasePlugin())
        # LOADED → deactivate is a no-op
        reg.deactivate("test-plugin")
        assert reg.state("test-plugin") == "LOADED"

    def test_disable_from_enabled(self) -> None:
        reg = PluginRegistry()
        reg.register(_BasePlugin())
        reg.enable("test-plugin")
        reg.disable("test-plugin")
        assert reg.state("test-plugin") == "LOADED"

    def test_disable_from_active_calls_deactivate(self) -> None:
        reg = PluginRegistry()
        p = _BasePlugin()
        reg.register(p)
        reg.enable("test-plugin")
        reg.activate("test-plugin")
        p.lifecycle_calls.clear()
        reg.disable("test-plugin")
        assert reg.state("test-plugin") == "LOADED"
        assert "deactivate" in p.lifecycle_calls

    def test_disable_already_loaded_is_idempotent(self) -> None:
        reg = PluginRegistry()
        reg.register(_BasePlugin())
        reg.disable("test-plugin")  # no error
        assert reg.state("test-plugin") == "LOADED"

    def test_is_enabled(self) -> None:
        reg = PluginRegistry()
        reg.register(_BasePlugin())
        assert not reg.is_enabled("test-plugin")
        reg.enable("test-plugin")
        assert reg.is_enabled("test-plugin")

    def test_is_active(self) -> None:
        reg = PluginRegistry()
        reg.register(_BasePlugin())
        reg.enable("test-plugin")
        assert not reg.is_active("test-plugin")
        reg.activate("test-plugin")
        assert reg.is_active("test-plugin")

    def test_registered_count(self) -> None:
        reg = PluginRegistry()
        assert reg.registered_count == 0
        reg.register(_BasePlugin(name="a"))
        assert reg.registered_count == 1
        reg.register(_BasePlugin(name="b"))
        assert reg.registered_count == 2
        reg.unregister("a")
        assert reg.registered_count == 1


# ── PluginRegistry: Capability queries ──────────────────────────────


class TestRegistryCapabilityQuery:
    def test_list_by_capability_empty(self) -> None:
        reg = PluginRegistry()
        assert reg.list_by_capability(PluginCapability.EXECUTION_HOOK) == []

    def test_list_by_capability_returns_enabled_plugins(self) -> None:
        reg = PluginRegistry()
        p = _BasePlugin(capabilities=(PluginCapability.EXECUTION_HOOK,))
        reg.register(p)
        reg.enable("test-plugin")
        result = reg.list_by_capability(PluginCapability.EXECUTION_HOOK)
        assert len(result) == 1
        assert result[0] is p

    def test_list_by_capability_excludes_loaded(self) -> None:
        reg = PluginRegistry()
        reg.register(
            _BasePlugin(capabilities=(PluginCapability.EXECUTION_HOOK,))
        )
        # LOADED, not enabled → excluded
        assert reg.list_by_capability(PluginCapability.EXECUTION_HOOK) == []

    def test_list_by_capability_excludes_disabled(self) -> None:
        reg = PluginRegistry()
        p = _BasePlugin(capabilities=(PluginCapability.EXECUTION_HOOK,))
        reg.register(p)
        reg.enable("test-plugin")
        reg.disable("test-plugin")
        assert reg.list_by_capability(PluginCapability.EXECUTION_HOOK) == []

    def test_list_by_capability_multiple_plugins(self) -> None:
        reg = PluginRegistry()
        p1 = _BasePlugin(
            name="a", capabilities=(PluginCapability.EXECUTION_HOOK,)
        )
        p2 = _BasePlugin(
            name="b", capabilities=(PluginCapability.EXECUTION_HOOK,)
        )
        p3 = _BasePlugin(
            name="c", capabilities=(PluginCapability.VALIDATION,)
        )
        for p in (p1, p2, p3):
            reg.register(p)
            reg.enable(p.name)
        hooks = reg.list_by_capability(PluginCapability.EXECUTION_HOOK)
        assert len(hooks) == 2
        validators = reg.list_by_capability(PluginCapability.VALIDATION)
        assert len(validators) == 1


# ── Dependency validation ───────────────────────────────────────────


class TestRegistryDependencies:
    def test_missing_dependency_blocks_enable(self) -> None:
        reg = PluginRegistry()
        p = _BasePlugin(name="a", dependencies=("b",))
        reg.register(p)
        with pytest.raises(PluginDependencyError, match="b"):
            reg.enable("a")

    def test_disabled_dependency_blocks_enable(self) -> None:
        reg = PluginRegistry()
        reg.register(_BasePlugin(name="b"))
        reg.register(_BasePlugin(name="a", dependencies=("b",)))
        # b is LOADED (not enabled)
        with pytest.raises(PluginDependencyError):
            reg.enable("a")

    def test_enabled_dependency_allows_enable(self) -> None:
        reg = PluginRegistry()
        reg.register(_BasePlugin(name="b"))
        reg.enable("b")
        reg.register(_BasePlugin(name="a", dependencies=("b",)))
        reg.enable("a")  # should not raise
        assert reg.is_enabled("a")

    def test_no_dependencies_trivial(self) -> None:
        reg = PluginRegistry()
        reg.register(_BasePlugin())
        reg.enable("test-plugin")  # should not raise


# ── Error containment ───────────────────────────────────────────────


class TestErrorContainment:
    def test_failing_activate_plugin_stays_enabled(self) -> None:
        reg = PluginRegistry()
        p = _FailingActivatePlugin()
        reg.register(p)
        reg.enable("test-plugin")
        with pytest.raises(RuntimeError, match="activate failed"):
            reg.activate("test-plugin")
        # Plugin should still be in ENABLED state
        assert reg.state("test-plugin") == "ENABLED"

    def test_failing_activate_does_not_block_others(self) -> None:
        reg = PluginRegistry()
        failing = _FailingActivatePlugin(name="failing")
        working = _BasePlugin(name="working")
        reg.register(failing)
        reg.enable("failing")
        reg.register(working)
        reg.enable("working")

        with pytest.raises(RuntimeError):
            reg.activate("failing")

        # Working plugin should still be activatable
        reg.activate("working")
        assert reg.is_active("working")


# ── PluginCapability enum ───────────────────────────────────────────


class TestPluginCapabilityEnum:
    def test_all_values_unique(self) -> None:
        values = [c.value for c in PluginCapability]
        assert len(values) == len(set(values))

    def test_known_capabilities(self) -> None:
        names = {c.name for c in PluginCapability}
        expected = {
            "RULE_DISCOVERY",
            "VALIDATION",
            "EXECUTION_HOOK",
            "BATCH_HOOK",
            "RESULT_PROCESSING",
            "OUTPUT_EXPORT",
        }
        assert names == expected


# ── Integration: full lifecycle ─────────────────────────────────────


class TestFullLifecycle:
    def test_register_enable_activate_deactivate_disable_unregister(
        self,
    ) -> None:
        reg = PluginRegistry()
        p = _BasePlugin()
        reg.register(p)
        assert reg.state("test-plugin") == "LOADED"
        assert p.lifecycle_calls == ["discover", "load", "initialize"]

        reg.enable("test-plugin")
        assert reg.state("test-plugin") == "ENABLED"

        reg.activate("test-plugin")
        assert reg.state("test-plugin") == "ACTIVE"
        assert "activate" in p.lifecycle_calls

        reg.deactivate("test-plugin")
        assert reg.state("test-plugin") == "ENABLED"
        assert "deactivate" in p.lifecycle_calls

        reg.disable("test-plugin")
        assert reg.state("test-plugin") == "LOADED"

        p.lifecycle_calls.clear()
        reg.unregister("test-plugin")
        assert "unload" in p.lifecycle_calls
        assert reg.get("test-plugin") is None
