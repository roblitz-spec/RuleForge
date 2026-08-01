"""ValidationPlugin — capability plugin for rule-based data validation.

Manages validation rule registration, discovery, and execution.
Each validation rule inspects a context dict and returns a
pass/fail result.  The plugin reports results but does NOT
execute actions or make policy decisions — that is the caller's
responsibility.

Distinct from M12-C RuleValidationPlugin (which validates
RuleForge rule configurations for static correctness).  This
plugin validates arbitrary data against user-defined rules.

Does not modify Execution Platform, Batch Execution, or Plugin
Framework contracts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from plugins.plugin import Plugin, PluginMetadata
from plugins.plugin_capability import PluginCapability
from plugins.plugin_context import PluginContext


# ── Validation model ──────────────────────────────────────────────


@dataclass(frozen=True)
class ValidationRule:
    """A named validation check.

    Attributes:
        name: Unique rule identifier.
        description: Human-readable description.
        validate: Callable that receives a context dict and returns
            either True/False (pass/fail) or a message string
            (empty = pass, non-empty = fail).
    """
    name: str
    description: str = ""
    validate: Callable = field(default=lambda ctx: True)

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("Validation rule name must not be empty")


# ── Validation context ────────────────────────────────────────────


ValidationContext = dict


# ── Result types ──────────────────────────────────────────────────


@dataclass(frozen=True)
class ValidationResult:
    """Outcome of executing a single validation rule.

    Attributes:
        rule_name: Name of the validated rule.
        status: "pass" or "fail".
        message: Human-readable details, empty on pass.
    """
    rule_name: str
    status: str  # "pass" | "fail"
    message: str = ""

    def __post_init__(self) -> None:
        if self.status not in ("pass", "fail"):
            raise ValueError(
                f"status must be 'pass' or 'fail', got {self.status!r}"
            )

    @property
    def is_valid(self) -> bool:
        return self.status == "pass"


# ── Convenience constructors ──────────────────────────────────────


def validation_pass(message: str = "") -> ValidationResult:
    return ValidationResult(rule_name="", status="pass", message=message)


def validation_fail(message: str = "") -> ValidationResult:
    return ValidationResult(rule_name="", status="fail", message=message)


# ── Plugin ────────────────────────────────────────────────────────


class ValidationPlugin(Plugin):
    """Manages validation rule registration, discovery, and execution.

    Usage:
        plugin = ValidationPlugin()
        registry.register(plugin)
        registry.enable(plugin.name)
        registry.activate(plugin.name)

        rule = ValidationRule(
            name="non-empty",
            description="Value must not be empty",
            validate=lambda ctx: len(ctx.get("value", "")) > 0,
        )
        plugin.register(rule)
        result = plugin.validate("non-empty", {"value": "hello"})
        assert result.is_valid

    Capability: EXECUTION_HOOK — validation gates execution flow.
    """

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="ruleforge.validation",
            version="1.0.0",
            description="Manages validation rule registration, discovery, and execution",
            author="RuleForge",
            capabilities=(PluginCapability.EXECUTION_HOOK,),
        )

    def __init__(self) -> None:
        self._rules: dict[str, ValidationRule] = {}

    def on_activate(self, ctx: PluginContext) -> None:
        pass

    def on_deactivate(self, ctx: PluginContext) -> None:
        # Preserve rules on deactivation (Lifecycle vs Business State)
        pass

    # ── Registration ───────────────────────────────────────────

    def register(self, rule: ValidationRule) -> None:
        """Register a validation rule. Raises ValueError on duplicate."""
        if rule.name in self._rules:
            raise ValueError(
                f"Validation rule '{rule.name}' is already registered"
            )
        self._rules[rule.name] = rule

    def unregister(self, name: str) -> bool:
        """Unregister a rule by name. Returns True if removed."""
        return self._rules.pop(name, None) is not None

    # ── Discovery ──────────────────────────────────────────────

    def list_rules(self) -> tuple[ValidationRule, ...]:
        """Return all registered validation rules."""
        return tuple(self._rules.values())

    def get(self, name: str) -> ValidationRule | None:
        """Return a rule by name, or None."""
        return self._rules.get(name)

    @property
    def rule_count(self) -> int:
        return len(self._rules)

    # ── Execution ──────────────────────────────────────────────

    def validate(
        self,
        name: str,
        context: ValidationContext | None = None,
    ) -> ValidationResult:
        """Execute a single validation rule against a context.

        Raises KeyError if the rule is not found.
        """
        rule = self._rules.get(name)
        if rule is None:
            raise KeyError(f"Validation rule '{name}' not found")
        return _execute_rule(rule, context or {})

    def validate_all(
        self,
        context: ValidationContext | None = None,
    ) -> tuple[ValidationResult, ...]:
        """Execute all registered rules against a context.

        Each rule is executed independently.  Results are returned
        in registration order.
        """
        ctx = context or {}
        return tuple(_execute_rule(r, ctx) for r in self._rules.values())

    def has_failures(
        self,
        context: ValidationContext | None = None,
    ) -> bool:
        """Check if any rule fails validation."""
        return any(not r.is_valid for r in self.validate_all(context))


# ── Internal ──────────────────────────────────────────────────────


def _execute_rule(rule: ValidationRule, ctx: ValidationContext) -> ValidationResult:
    result = rule.validate(ctx)
    if isinstance(result, str):
        status = "pass" if not result else "fail"
        message = result
    elif isinstance(result, bool):
        status = "pass" if result else "fail"
        message = "" if result else "validation failed"
    else:
        status = "fail"
        message = str(result)
    return ValidationResult(rule_name=rule.name, status=status, message=message)
