"""Tests for M12-C RuleValidationPlugin — first official plugin."""

from __future__ import annotations

import pytest

from models.rule import Rule
from models.rule_step import RuleStep
from plugins.plugin_capability import PluginCapability
from plugins.plugin_errors import PluginLifecycleError
from plugins.plugin_registry import PluginRegistry
from plugins.rule_validation_plugin import (
    RuleValidationPlugin,
    ValidationIssue,
    ValidationResult,
)


# ── Helpers ───────────────────────────────────────────────────────

def _make_rule(
    rid: str = "r1",
    name: str = "Test Rule",
    steps: list[RuleStep] | None = None,
) -> Rule:
    return Rule(id=rid, name=name, steps=steps or [])


def _step(type: str, **params: object) -> RuleStep:  # noqa: A002
    return RuleStep(type=type, parameters=dict(params))


# ── Plugin metadata & lifecycle ───────────────────────────────────


class TestRuleValidationPluginMetadata:
    def test_name(self) -> None:
        p = RuleValidationPlugin()
        assert p.name == "ruleforge.validation"

    def test_version(self) -> None:
        p = RuleValidationPlugin()
        assert p.version == "1.0.0"

    def test_capability(self) -> None:
        p = RuleValidationPlugin()
        assert PluginCapability.VALIDATION in p.metadata.capabilities

    def test_dependencies(self) -> None:
        p = RuleValidationPlugin()
        assert p.metadata.dependencies == ()


class TestRuleValidationPluginLifecycle:
    def test_full_lifecycle_in_registry(self) -> None:
        reg = PluginRegistry()
        p = RuleValidationPlugin()
        reg.register(p)
        assert reg.state("ruleforge.validation") == "LOADED"
        reg.enable("ruleforge.validation")
        assert reg.state("ruleforge.validation") == "ENABLED"
        reg.activate("ruleforge.validation")
        assert reg.state("ruleforge.validation") == "ACTIVE"
        reg.deactivate("ruleforge.validation")
        assert reg.state("ruleforge.validation") == "ENABLED"

    def test_cannot_activate_before_enable(self) -> None:
        reg = PluginRegistry()
        reg.register(RuleValidationPlugin())
        with pytest.raises(PluginLifecycleError):
            reg.activate("ruleforge.validation")

    def test_discovery_via_capability(self) -> None:
        reg = PluginRegistry()
        reg.register(RuleValidationPlugin())
        reg.enable("ruleforge.validation")
        plugins = reg.list_by_capability(PluginCapability.VALIDATION)
        assert len(plugins) == 1
        assert plugins[0].name == "ruleforge.validation"

    def test_not_found_when_loaded_only(self) -> None:
        reg = PluginRegistry()
        reg.register(RuleValidationPlugin())
        # LOADED, not enabled
        assert (
            reg.list_by_capability(PluginCapability.VALIDATION) == []
        )

    def test_not_found_when_disabled(self) -> None:
        reg = PluginRegistry()
        reg.register(RuleValidationPlugin())
        reg.enable("ruleforge.validation")
        reg.disable("ruleforge.validation")
        assert (
            reg.list_by_capability(PluginCapability.VALIDATION) == []
        )

    def test_unregister(self) -> None:
        reg = PluginRegistry()
        p = RuleValidationPlugin()
        reg.register(p)
        reg.enable("ruleforge.validation")
        reg.unregister("ruleforge.validation")
        assert reg.get("ruleforge.validation") is None


# ── Validation: empty / no steps ──────────────────────────────────


class TestValidationEmptyRule:
    def test_empty_steps_emits_warning(self) -> None:
        p = RuleValidationPlugin()
        rule = _make_rule(steps=[])
        result = p.validate(rule)
        assert result.is_valid  # no errors, only a warning
        assert result.warning_count == 1
        assert "no steps" in result.issues[0].message

    def test_non_empty_steps_no_warning(self) -> None:
        p = RuleValidationPlugin()
        rule = _make_rule(steps=[_step("trim", mode="both")])
        result = p.validate(rule)
        assert result.warning_count == 0


# ── Validation: unknown step type ─────────────────────────────────


class TestValidationUnknownType:
    def test_unknown_step_type_is_error(self) -> None:
        p = RuleValidationPlugin()
        rule = _make_rule(steps=[_step("bogus_type")])
        result = p.validate(rule)
        assert not result.is_valid
        assert result.error_count == 1
        assert "Unknown step type" in result.issues[0].message

    def test_unknown_step_index_reported(self) -> None:
        p = RuleValidationPlugin()
        rule = _make_rule(
            steps=[
                _step("trim", mode="both"),
                _step("bogus"),
                _step("case", mode="upper"),
            ]
        )
        result = p.validate(rule)
        assert result.issues[0].step_index == 1
        assert "bogus" in result.issues[0].message


# ── Validation: missing required params ───────────────────────────


class TestValidationMissingParams:
    def test_replace_missing_from(self) -> None:
        p = RuleValidationPlugin()
        rule = _make_rule(steps=[_step("replace", to="bar")])
        result = p.validate(rule)
        assert not result.is_valid
        assert any("'from'" in i.message for i in result.issues)

    def test_replace_missing_from_is_flagged(self) -> None:
        p = RuleValidationPlugin()
        rule = _make_rule(steps=[RuleStep(type="replace", parameters={"to": "bar"})])
        result = p.validate(rule)
        assert not result.is_valid
        assert any("'from'" in i.message for i in result.issues)

    def test_replace_empty_from(self) -> None:
        p = RuleValidationPlugin()
        rule = _make_rule(steps=[RuleStep(type="replace", parameters={"from": "", "to": "x"})])
        result = p.validate(rule)
        assert not result.is_valid
        assert any("'from'" in i.message for i in result.issues)

    def test_add_prefix_missing_text(self) -> None:
        p = RuleValidationPlugin()
        rule = _make_rule(steps=[_step("add_prefix")])
        result = p.validate(rule)
        assert not result.is_valid
        assert any("'text'" in i.message for i in result.issues)

    def test_all_required_params_present(self) -> None:
        p = RuleValidationPlugin()
        rule = _make_rule(steps=[_step("replace", **{"from": "a", "to": "b"})])
        result = p.validate(rule)
        assert result.error_count == 0


# ── Validation: regex ─────────────────────────────────────────────


class TestValidationRegex:
    def test_valid_regex(self) -> None:
        p = RuleValidationPlugin()
        rule = _make_rule(
            steps=[
                _step(
                    "regex_replace",
                    pattern=r"\d+",
                    replacement="N",
                )
            ]
        )
        result = p.validate(rule)
        assert result.is_valid

    def test_invalid_regex_pattern(self) -> None:
        p = RuleValidationPlugin()
        rule = _make_rule(
            steps=[
                _step(
                    "regex_replace",
                    pattern="[unclosed",
                    replacement="x",
                )
            ]
        )
        result = p.validate(rule)
        assert not result.is_valid
        assert any("invalid regex" in i.message for i in result.issues)

    def test_invalid_regex_flags(self) -> None:
        p = RuleValidationPlugin()
        rule = _make_rule(
            steps=[
                _step(
                    "regex_replace",
                    pattern="a",
                    replacement="b",
                    flags="not_an_int",
                )
            ]
        )
        result = p.validate(rule)
        assert not result.is_valid
        assert any("flags" in i.message for i in result.issues)


# ── Validation: case mode ─────────────────────────────────────────


class TestValidationCaseMode:
    def test_valid_modes(self) -> None:
        p = RuleValidationPlugin()
        for mode in ("upper", "lower", "title", "sentence"):
            rule = _make_rule(steps=[_step("case", mode=mode)])
            result = p.validate(rule)
            assert result.is_valid, f"mode '{mode}' should be valid"

    def test_invalid_mode(self) -> None:
        p = RuleValidationPlugin()
        rule = _make_rule(steps=[_step("case", mode="kebab")])
        result = p.validate(rule)
        assert not result.is_valid
        assert any("case mode" in i.message for i in result.issues)


# ── Validation: trim mode ─────────────────────────────────────────


class TestValidationTrimMode:
    def test_valid_modes(self) -> None:
        p = RuleValidationPlugin()
        for mode in ("both", "left", "right"):
            rule = _make_rule(steps=[_step("trim", mode=mode)])
            result = p.validate(rule)
            assert result.is_valid, f"mode '{mode}' should be valid"

    def test_invalid_mode(self) -> None:
        p = RuleValidationPlugin()
        rule = _make_rule(steps=[_step("trim", mode="all")])
        result = p.validate(rule)
        assert not result.is_valid
        assert any("trim mode" in i.message for i in result.issues)


# ── Validation: number params ─────────────────────────────────────


class TestValidationNumberParams:
    def test_valid_number_params(self) -> None:
        p = RuleValidationPlugin()
        rule = _make_rule(
            steps=[_step("number", start="1", step="2", padding="3")]
        )
        result = p.validate(rule)
        assert result.is_valid

    def test_non_integer_start(self) -> None:
        p = RuleValidationPlugin()
        rule = _make_rule(steps=[_step("number", start="abc")])
        result = p.validate(rule)
        assert not result.is_valid
        assert any("'start'" in i.message for i in result.issues)

    def test_negative_padding(self) -> None:
        p = RuleValidationPlugin()
        rule = _make_rule(steps=[_step("number", padding="-1")])
        result = p.validate(rule)
        assert not result.is_valid
        assert any("'padding'" in i.message for i in result.issues)


# ── ValidationResult ──────────────────────────────────────────────


class TestValidationResult:
    def test_valid_empty_issues(self) -> None:
        result = ValidationResult(rule_id="r1", rule_name="n")
        assert result.is_valid
        assert result.error_count == 0
        assert result.warning_count == 0

    def test_error_makes_invalid(self) -> None:
        result = ValidationResult(
            rule_id="r1",
            rule_name="n",
            issues=[ValidationIssue("error", 0, "bad")],
        )
        assert not result.is_valid
        assert result.error_count == 1

    def test_warning_only_is_valid(self) -> None:
        result = ValidationResult(
            rule_id="r1",
            rule_name="n",
            issues=[ValidationIssue("warning", None, "meh")],
        )
        assert result.is_valid
        assert result.warning_count == 1

    def test_mixed(self) -> None:
        result = ValidationResult(
            rule_id="r1",
            rule_name="n",
            issues=[
                ValidationIssue("error", 0, "e1"),
                ValidationIssue("warning", 1, "w1"),
                ValidationIssue("error", 2, "e2"),
            ],
        )
        assert not result.is_valid
        assert result.error_count == 2
        assert result.warning_count == 1


# ── Integration: multi-step rule ──────────────────────────────────


class TestMultiStepValidation:
    def test_multiple_issues_aggregated(self) -> None:
        p = RuleValidationPlugin()
        rule = _make_rule(
            steps=[
                _step("bogus1"),  # unknown
                _step("trim", mode="bad"),  # invalid mode
                _step("regex_replace", pattern="[bad", replacement="x"),  # invalid regex
            ]
        )
        result = p.validate(rule)
        assert result.error_count == 3
        assert len(result.issues) == 3

    def test_aggregate_result_identity(self) -> None:
        p = RuleValidationPlugin()
        rule = _make_rule(
            steps=[
                _step("trim", mode="both"),
                _step("case", mode="upper"),
            ]
        )
        result = p.validate(rule)
        assert result.rule_id == "r1"
        assert result.rule_name == "Test Rule"


# ── Issue count convenience ───────────────────────────────────────


def test_validation_issue_frozen() -> None:
    issue = ValidationIssue("error", 0, "test message")
    assert issue.severity == "error"
    assert issue.step_index == 0
    assert issue.message == "test message"
    with pytest.raises(Exception):
        issue.severity = "warning"  # type: ignore[misc]
