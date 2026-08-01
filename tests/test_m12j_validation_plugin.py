"""Tests for M12-J ValidationPlugin — rule-based data validation."""

from __future__ import annotations

import pytest

from plugins.plugin_capability import PluginCapability
from plugins.plugin_registry import PluginRegistry
from plugins.validation_plugin import (
    ValidationContext,
    ValidationPlugin,
    ValidationResult,
    ValidationRule,
    validation_fail,
    validation_pass,
)


# ── Plugin metadata & lifecycle ───────────────────────────────────


class TestValidationPluginMetadata:
    def test_name(self) -> None:
        p = ValidationPlugin()
        assert p.name == "ruleforge.validation"

    def test_version(self) -> None:
        p = ValidationPlugin()
        assert p.version == "1.0.0"

    def test_capability(self) -> None:
        p = ValidationPlugin()
        assert PluginCapability.EXECUTION_HOOK in p.metadata.capabilities

    def test_dependencies(self) -> None:
        p = ValidationPlugin()
        assert p.metadata.dependencies == ()


class TestValidationPluginLifecycle:
    def test_full_lifecycle_in_registry(self) -> None:
        reg = PluginRegistry()
        reg.register(ValidationPlugin())
        assert reg.state("ruleforge.validation") == "LOADED"
        reg.enable("ruleforge.validation")
        assert reg.state("ruleforge.validation") == "ENABLED"
        reg.activate("ruleforge.validation")
        assert reg.state("ruleforge.validation") == "ACTIVE"
        reg.deactivate("ruleforge.validation")
        assert reg.state("ruleforge.validation") == "ENABLED"

    def test_discovery_via_capability(self) -> None:
        reg = PluginRegistry()
        reg.register(ValidationPlugin())
        reg.enable("ruleforge.validation")
        plugins = reg.list_by_capability(PluginCapability.EXECUTION_HOOK)
        assert any(p.name == "ruleforge.validation" for p in plugins)

    def test_not_found_when_loaded_only(self) -> None:
        reg = PluginRegistry()
        reg.register(ValidationPlugin())
        assert reg.list_by_capability(PluginCapability.EXECUTION_HOOK) == []

    def test_rules_persist_after_deactivation(self) -> None:
        reg = PluginRegistry()
        reg.register(ValidationPlugin())
        reg.enable("ruleforge.validation")
        reg.activate("ruleforge.validation")

        plugin = reg.get("ruleforge.validation")
        assert plugin is not None
        plugin.register(ValidationRule("r1"))

        reg.deactivate("ruleforge.validation")
        assert plugin.rule_count == 1


# ── Rule registration ─────────────────────────────────────────────


class TestRuleRegistration:
    def test_register(self) -> None:
        p = ValidationPlugin()
        p.register(ValidationRule("test"))
        assert p.rule_count == 1

    def test_register_duplicate_raises(self) -> None:
        p = ValidationPlugin()
        p.register(ValidationRule("test"))
        with pytest.raises(ValueError, match="already registered"):
            p.register(ValidationRule("test"))

    def test_unregister(self) -> None:
        p = ValidationPlugin()
        p.register(ValidationRule("test"))
        assert p.unregister("test")
        assert p.rule_count == 0

    def test_unregister_nonexistent_returns_false(self) -> None:
        p = ValidationPlugin()
        assert p.unregister("nope") is False

    def test_register_multiple(self) -> None:
        p = ValidationPlugin()
        p.register(ValidationRule("a"))
        p.register(ValidationRule("b"))
        p.register(ValidationRule("c"))
        assert p.rule_count == 3


# ── Rule discovery ────────────────────────────────────────────────


class TestRuleDiscovery:
    def test_list_rules(self) -> None:
        p = ValidationPlugin()
        p.register(ValidationRule("a"))
        p.register(ValidationRule("b"))
        names = {r.name for r in p.list_rules()}
        assert names == {"a", "b"}

    def test_list_rules_empty(self) -> None:
        p = ValidationPlugin()
        assert p.list_rules() == ()

    def test_get_rule(self) -> None:
        p = ValidationPlugin()
        r = ValidationRule("test", "desc")
        p.register(r)
        assert p.get("test") is r

    def test_get_nonexistent_returns_none(self) -> None:
        p = ValidationPlugin()
        assert p.get("missing") is None


# ── Validation execution — success path ───────────────────────────


class TestValidateSuccess:
    def test_validate_bool_true_passes(self) -> None:
        p = ValidationPlugin()
        p.register(ValidationRule("r", validate=lambda ctx: True))
        result = p.validate("r", {"x": 1})
        assert result.is_valid
        assert result.status == "pass"

    def test_validate_bool_false_fails(self) -> None:
        p = ValidationPlugin()
        p.register(ValidationRule("r", validate=lambda ctx: False))
        result = p.validate("r")
        assert not result.is_valid
        assert result.status == "fail"
        assert result.message == "validation failed"

    def test_validate_str_empty_passes(self) -> None:
        p = ValidationPlugin()
        p.register(ValidationRule("r", validate=lambda ctx: ""))
        result = p.validate("r")
        assert result.is_valid

    def test_validate_str_nonempty_fails(self) -> None:
        p = ValidationPlugin()
        p.register(ValidationRule("r", validate=lambda ctx: "too short"))
        result = p.validate("r")
        assert not result.is_valid
        assert result.message == "too short"

    def test_validate_context_passed(self) -> None:
        p = ValidationPlugin()
        p.register(
            ValidationRule(
                "len",
                validate=lambda ctx: len(ctx.get("text", "")) > 3,
            )
        )
        assert p.validate("len", {"text": "hello"}).is_valid
        assert not p.validate("len", {"text": "hi"}).is_valid

    def test_rule_name_in_result(self) -> None:
        p = ValidationPlugin()
        p.register(ValidationRule("my-rule", validate=lambda ctx: True))
        assert p.validate("my-rule").rule_name == "my-rule"

    def test_validate_nonexistent_raises(self) -> None:
        p = ValidationPlugin()
        with pytest.raises(KeyError, match="not found"):
            p.validate("missing")


# ── validate_all ──────────────────────────────────────────────────


class TestValidateAll:
    def test_validate_all(self) -> None:
        p = ValidationPlugin()
        p.register(ValidationRule("p1", validate=lambda ctx: True))
        p.register(ValidationRule("p2", validate=lambda ctx: "bad"))
        results = p.validate_all({"k": "v"})
        assert len(results) == 2
        assert results[0].is_valid
        assert not results[1].is_valid
        assert results[1].message == "bad"

    def test_validate_all_empty(self) -> None:
        p = ValidationPlugin()
        assert p.validate_all() == ()

    def test_validate_all_order(self) -> None:
        p = ValidationPlugin()
        p.register(ValidationRule("a", validate=lambda ctx: True))
        p.register(ValidationRule("b", validate=lambda ctx: False))
        p.register(ValidationRule("c", validate=lambda ctx: True))
        names = [r.rule_name for r in p.validate_all()]
        assert names == ["a", "b", "c"]


# ── has_failures ──────────────────────────────────────────────────


class TestHasFailures:
    def test_no_failures(self) -> None:
        p = ValidationPlugin()
        p.register(ValidationRule("r1", validate=lambda ctx: True))
        assert not p.has_failures()

    def test_has_failures(self) -> None:
        p = ValidationPlugin()
        p.register(ValidationRule("r1", validate=lambda ctx: True))
        p.register(ValidationRule("r2", validate=lambda ctx: False))
        assert p.has_failures()


# ── Error handling ────────────────────────────────────────────────


class TestErrorHandling:
    def test_rule_raises_propagates(self) -> None:
        p = ValidationPlugin()
        p.register(
            ValidationRule(
                "explosive",
                validate=lambda ctx: (_ for _ in ()).throw(RuntimeError("boom")),  # type: ignore[attr-defined]
            )
        )
        with pytest.raises(Exception):
            p.validate("explosive")

    def test_default_rule_passes(self) -> None:
        p = ValidationPlugin()
        p.register(ValidationRule("default"))
        result = p.validate("default", {"x": 1})
        assert result.is_valid

    def test_non_bool_non_str_return(self) -> None:
        p = ValidationPlugin()
        p.register(ValidationRule("weird", validate=lambda ctx: 42))
        result = p.validate("weird")
        assert not result.is_valid
        assert result.message == "42"


# ── ValidationRule model ──────────────────────────────────────────


class TestValidationRuleModel:
    def test_defaults(self) -> None:
        r = ValidationRule("test")
        assert r.name == "test"
        assert r.description == ""

    def test_empty_name_raises(self) -> None:
        with pytest.raises(ValueError, match="must not be empty"):
            ValidationRule("")

    def test_frozen(self) -> None:
        r = ValidationRule("test")
        with pytest.raises(Exception):
            r.name = "other"  # type: ignore[misc]


# ── ValidationResult model ────────────────────────────────────────


class TestValidationResult:
    def test_defaults(self) -> None:
        r = ValidationResult("rule", "pass")
        assert r.rule_name == "rule"
        assert r.status == "pass"
        assert r.message == ""

    def test_invalid_status(self) -> None:
        with pytest.raises(ValueError, match="must be 'pass' or 'fail'"):
            ValidationResult("x", "error")

    def test_is_valid(self) -> None:
        assert ValidationResult("x", "pass").is_valid
        assert not ValidationResult("x", "fail").is_valid

    def test_frozen(self) -> None:
        r = ValidationResult("x", "pass")
        with pytest.raises(Exception):
            r.status = "fail"  # type: ignore[misc]


# ── Convenience constructors ──────────────────────────────────────


class TestConvenienceConstructors:
    def test_validation_pass(self) -> None:
        r = validation_pass()
        assert r.is_valid
        assert r.message == ""

    def test_validation_fail(self) -> None:
        r = validation_fail("reason")
        assert not r.is_valid
        assert r.message == "reason"


# ── Plugin independence ───────────────────────────────────────────


class TestPluginIndependence:
    def test_no_engine_imports(self) -> None:
        import plugins.validation_plugin as vp

        source = vp.__file__
        assert source is not None
        with open(source) as f:
            content = f.read()
        assert "from engine" not in content
        assert "import engine" not in content

    def test_standalone_usage_without_registry(self) -> None:
        p = ValidationPlugin()
        p.register(
            ValidationRule(
                "non-empty",
                validate=lambda ctx: bool(ctx.get("name")),
            )
        )
        assert p.validate("non-empty", {"name": "Alice"}).is_valid
        assert not p.validate("non-empty", {"name": ""}).is_valid


# ── Full integration flow ─────────────────────────────────────────


class TestFullIntegrationFlow:
    def test_register_discover_validate(self) -> None:
        reg = PluginRegistry()
        reg.register(ValidationPlugin())
        reg.enable("ruleforge.validation")
        reg.activate("ruleforge.validation")

        plugin = reg.get("ruleforge.validation")
        assert plugin is not None

        # Register reference rules
        plugin.register(
            ValidationRule(
                "non-empty-name",
                "Name must not be empty",
                validate=lambda ctx: len(ctx.get("name", "")) > 0,
            )
        )
        plugin.register(
            ValidationRule(
                "positive-count",
                "Count must be > 0",
                validate=lambda ctx: ctx.get("count", 0) > 0,
            )
        )

        # Discover
        rules = plugin.list_rules()
        assert len(rules) == 2
        assert {r.name for r in rules} == {"non-empty-name", "positive-count"}

        # Validate individually
        assert plugin.validate("non-empty-name", {"name": "Alice"}).is_valid
        assert not plugin.validate("non-empty-name", {"name": ""}).is_valid
        assert plugin.validate("positive-count", {"count": 5}).is_valid
        assert not plugin.validate("positive-count", {"count": 0}).is_valid

        # validate_all
        results = plugin.validate_all({"name": "", "count": 5})
        assert not results[0].is_valid  # name empty
        assert results[1].is_valid      # count ok

        # has_failures
        assert plugin.has_failures({"name": "", "count": 0})
        assert not plugin.has_failures({"name": "Alice", "count": 5})

        # Unregister
        assert plugin.unregister("non-empty-name")
        assert plugin.rule_count == 1
