"""Tests for M12-I PolicyPlugin — policy-based decision control."""

from __future__ import annotations

import pytest

from plugins.plugin_capability import PluginCapability
from plugins.plugin_registry import PluginRegistry
from plugins.policy_plugin import (
    EvaluationContext,
    EvaluationResult,
    Policy,
    PolicyPlugin,
    evaluation_allow,
    evaluation_deny,
    evaluation_warn,
)


# ── Plugin metadata & lifecycle ───────────────────────────────────


class TestPolicyPluginMetadata:
    def test_name(self) -> None:
        p = PolicyPlugin()
        assert p.name == "ruleforge.policy"

    def test_version(self) -> None:
        p = PolicyPlugin()
        assert p.version == "1.0.0"

    def test_capability(self) -> None:
        p = PolicyPlugin()
        assert PluginCapability.EXECUTION_HOOK in p.metadata.capabilities

    def test_dependencies(self) -> None:
        p = PolicyPlugin()
        assert p.metadata.dependencies == ()


class TestPolicyPluginLifecycle:
    def test_full_lifecycle_in_registry(self) -> None:
        reg = PluginRegistry()
        reg.register(PolicyPlugin())
        assert reg.state("ruleforge.policy") == "LOADED"
        reg.enable("ruleforge.policy")
        assert reg.state("ruleforge.policy") == "ENABLED"
        reg.activate("ruleforge.policy")
        assert reg.state("ruleforge.policy") == "ACTIVE"
        reg.deactivate("ruleforge.policy")
        assert reg.state("ruleforge.policy") == "ENABLED"

    def test_discovery_via_capability(self) -> None:
        reg = PluginRegistry()
        reg.register(PolicyPlugin())
        reg.enable("ruleforge.policy")
        plugins = reg.list_by_capability(PluginCapability.EXECUTION_HOOK)
        assert any(p.name == "ruleforge.policy" for p in plugins)

    def test_not_found_when_loaded_only(self) -> None:
        reg = PluginRegistry()
        reg.register(PolicyPlugin())
        assert reg.list_by_capability(PluginCapability.EXECUTION_HOOK) == []

    def test_policies_persist_after_deactivation(self) -> None:
        reg = PluginRegistry()
        reg.register(PolicyPlugin())
        reg.enable("ruleforge.policy")
        reg.activate("ruleforge.policy")

        plugin = reg.get("ruleforge.policy")
        assert plugin is not None
        plugin.register(Policy("p1"))

        reg.deactivate("ruleforge.policy")
        assert plugin.policy_count == 1


# ── Policy registration ───────────────────────────────────────────


class TestPolicyRegistration:
    def test_register(self) -> None:
        p = PolicyPlugin()
        p.register(Policy("test"))
        assert p.policy_count == 1

    def test_register_duplicate_raises(self) -> None:
        p = PolicyPlugin()
        p.register(Policy("test"))
        with pytest.raises(ValueError, match="already registered"):
            p.register(Policy("test"))

    def test_unregister(self) -> None:
        p = PolicyPlugin()
        p.register(Policy("test"))
        assert p.unregister("test")
        assert p.policy_count == 0

    def test_unregister_nonexistent_returns_false(self) -> None:
        p = PolicyPlugin()
        assert p.unregister("nope") is False

    def test_register_multiple(self) -> None:
        p = PolicyPlugin()
        p.register(Policy("a"))
        p.register(Policy("b"))
        p.register(Policy("c"))
        assert p.policy_count == 3


# ── Policy discovery ──────────────────────────────────────────────


class TestPolicyDiscovery:
    def test_list_policies(self) -> None:
        p = PolicyPlugin()
        p.register(Policy("a"))
        p.register(Policy("b"))
        names = {pol.name for pol in p.list_policies()}
        assert names == {"a", "b"}

    def test_list_policies_empty(self) -> None:
        p = PolicyPlugin()
        assert p.list_policies() == ()

    def test_get_policy(self) -> None:
        p = PolicyPlugin()
        pol = Policy("test", "desc")
        p.register(pol)
        assert p.get("test") is pol

    def test_get_nonexistent_returns_none(self) -> None:
        p = PolicyPlugin()
        assert p.get("missing") is None


# ── Policy evaluation — success path ──────────────────────────────


class TestPolicyEvaluationSuccess:
    def test_evaluate_allow(self) -> None:
        p = PolicyPlugin()
        p.register(Policy("allow-all", evaluate=lambda ctx: evaluation_allow("ok")))
        result = p.evaluate("allow-all", {"count": 50})
        assert result.is_allowed
        assert not result.is_denied
        assert not result.is_warning
        assert result.reason == "ok"

    def test_evaluate_deny(self) -> None:
        p = PolicyPlugin()
        p.register(Policy("deny-all", evaluate=lambda ctx: evaluation_deny("nope")))
        result = p.evaluate("deny-all")
        assert result.is_denied
        assert not result.is_allowed

    def test_evaluate_warn(self) -> None:
        p = PolicyPlugin()
        p.register(Policy("warn-all", evaluate=lambda ctx: evaluation_warn("careful")))
        result = p.evaluate("warn-all")
        assert result.is_warning

    def test_evaluate_with_context(self) -> None:
        p = PolicyPlugin()
        p.register(
            Policy(
                "max-count",
                evaluate=lambda ctx: (
                    evaluation_allow("ok")
                    if ctx.get("count", 0) <= 10
                    else evaluation_deny("exceeds max")
                ),
            )
        )
        assert p.evaluate("max-count", {"count": 3}).is_allowed
        assert p.evaluate("max-count", {"count": 42}).is_denied

    def test_policy_name_in_result(self) -> None:
        p = PolicyPlugin()
        p.register(Policy("my-policy", evaluate=lambda ctx: evaluation_allow()))
        assert p.evaluate("my-policy").policy_name == "my-policy"

    def test_evaluate_nonexistent_raises(self) -> None:
        p = PolicyPlugin()
        with pytest.raises(KeyError, match="not found"):
            p.evaluate("missing")


# ── Evaluate all ──────────────────────────────────────────────────


class TestEvaluateAll:
    def test_evaluate_all(self) -> None:
        p = PolicyPlugin()
        p.register(Policy("p1", evaluate=lambda ctx: evaluation_allow("a")))
        p.register(Policy("p2", evaluate=lambda ctx: evaluation_deny("d")))
        results = p.evaluate_all({"k": "v"})
        assert len(results) == 2
        assert results[0].is_allowed
        assert results[1].is_denied

    def test_evaluate_all_empty(self) -> None:
        p = PolicyPlugin()
        assert p.evaluate_all() == ()

    def test_evaluate_all_order(self) -> None:
        p = PolicyPlugin()
        p.register(Policy("a", evaluate=lambda ctx: evaluation_allow()))
        p.register(Policy("b", evaluate=lambda ctx: evaluation_deny()))
        p.register(Policy("c", evaluate=lambda ctx: evaluation_warn()))
        names = [r.policy_name for r in p.evaluate_all()]
        assert names == ["a", "b", "c"]


# ── has_deny convenience ──────────────────────────────────────────


class TestHasDeny:
    def test_no_deny(self) -> None:
        p = PolicyPlugin()
        p.register(Policy("p1", evaluate=lambda ctx: evaluation_allow()))
        assert not p.has_deny()

    def test_has_deny(self) -> None:
        p = PolicyPlugin()
        p.register(Policy("p1", evaluate=lambda ctx: evaluation_allow()))
        p.register(Policy("p2", evaluate=lambda ctx: evaluation_deny()))
        assert p.has_deny()


# ── Error handling ────────────────────────────────────────────────


class TestErrorHandling:
    def test_policy_raises_propagates(self) -> None:
        p = PolicyPlugin()
        p.register(
            Policy(
                "explosive",
                evaluate=lambda ctx: (_ for _ in ()).throw(RuntimeError("boom")),  # type: ignore[attr-defined]
            )
        )
        with pytest.raises(Exception):
            p.evaluate("explosive")

    def test_default_policy_evaluates_to_allow(self) -> None:
        p = PolicyPlugin()
        p.register(Policy("default"))
        result = p.evaluate("default", {"x": 1})
        assert result.is_allowed


# ── Policy model ──────────────────────────────────────────────────


class TestPolicyModel:
    def test_defaults(self) -> None:
        pol = Policy("test")
        assert pol.name == "test"
        assert pol.description == ""

    def test_empty_name_raises(self) -> None:
        with pytest.raises(ValueError, match="must not be empty"):
            Policy("")

    def test_frozen(self) -> None:
        pol = Policy("test")
        with pytest.raises(Exception):
            pol.name = "other"  # type: ignore[misc]


# ── EvaluationResult model ────────────────────────────────────────


class TestEvaluationResult:
    def test_defaults(self) -> None:
        r = EvaluationResult("pol", "allow")
        assert r.policy_name == "pol"
        assert r.decision == "allow"
        assert r.reason == ""

    def test_invalid_decision(self) -> None:
        with pytest.raises(ValueError, match="must be 'allow', 'deny', or 'warn'"):
            EvaluationResult("x", "block")

    def test_is_allowed_is_denied_is_warning(self) -> None:
        assert EvaluationResult("x", "allow").is_allowed
        assert not EvaluationResult("x", "allow").is_denied
        assert EvaluationResult("x", "deny").is_denied
        assert EvaluationResult("x", "warn").is_warning

    def test_frozen(self) -> None:
        r = EvaluationResult("x", "allow")
        with pytest.raises(Exception):
            r.decision = "deny"  # type: ignore[misc]


# ── Convenience constructors ──────────────────────────────────────


class TestConvenienceConstructors:
    def test_evaluation_allow(self) -> None:
        r = evaluation_allow()
        assert r.is_allowed
        assert r.reason == ""

    def test_evaluation_deny(self) -> None:
        r = evaluation_deny("reason")
        assert r.is_denied
        assert r.reason == "reason"

    def test_evaluation_warn(self) -> None:
        r = evaluation_warn()
        assert r.is_warning


# ── Plugin independence ───────────────────────────────────────────


class TestPluginIndependence:
    def test_no_engine_imports(self) -> None:
        import plugins.policy_plugin as pp

        source = pp.__file__
        assert source is not None
        with open(source) as f:
            content = f.read()
        assert "from engine" not in content
        assert "import engine" not in content

    def test_standalone_usage_without_registry(self) -> None:
        p = PolicyPlugin()
        p.register(
            Policy(
                "check",
                evaluate=lambda ctx: (
                    evaluation_allow("good")
                    if ctx.get("valid")
                    else evaluation_deny("bad")
                ),
            )
        )
        assert p.evaluate("check", {"valid": True}).is_allowed
        assert p.evaluate("check", {"valid": False}).is_denied


# ── Full integration flow ─────────────────────────────────────────


class TestFullIntegrationFlow:
    def test_register_discover_evaluate(self) -> None:
        reg = PluginRegistry()
        reg.register(PolicyPlugin())
        reg.enable("ruleforge.policy")
        reg.activate("ruleforge.policy")

        plugin = reg.get("ruleforge.policy")
        assert plugin is not None

        # Register reference policies
        plugin.register(
            Policy(
                "max-files",
                "Limit file count to 100",
                evaluate=lambda ctx: (
                    evaluation_allow("within limit")
                    if ctx.get("file_count", 0) <= 100
                    else evaluation_deny("too many files")
                ),
            )
        )
        plugin.register(
            Policy(
                "allow-text-only",
                "Only allow .txt files",
                evaluate=lambda ctx: (
                    evaluation_allow("ok")
                    if ctx.get("ext", "") == ".txt"
                    else evaluation_deny("not a text file")
                ),
            )
        )

        # Discover
        policies = plugin.list_policies()
        assert len(policies) == 2
        assert {p.name for p in policies} == {"max-files", "allow-text-only"}

        # Evaluate individually
        r1 = plugin.evaluate("max-files", {"file_count": 50})
        assert r1.is_allowed

        r2 = plugin.evaluate("max-files", {"file_count": 200})
        assert r2.is_denied

        r3 = plugin.evaluate("allow-text-only", {"ext": ".txt"})
        assert r3.is_allowed

        r4 = plugin.evaluate("allow-text-only", {"ext": ".pdf"})
        assert r4.is_denied

        # Evaluate all
        results = plugin.evaluate_all({"file_count": 200, "ext": ".txt"})
        assert results[0].is_denied
        assert results[1].is_allowed

        # has_deny
        assert plugin.has_deny({"file_count": 200, "ext": ".txt"})
        assert not plugin.has_deny({"file_count": 50, "ext": ".txt"})

        # Unregister
        assert plugin.unregister("max-files")
        assert plugin.policy_count == 1
