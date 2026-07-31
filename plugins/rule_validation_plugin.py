"""RuleValidationPlugin — first official RuleForge plugin.

Validates Rule objects for common issues: empty steps, unknown step
types, missing required parameters, invalid regex patterns.

This plugin demonstrates the M12-B Plugin Framework in a real-world
scenario without modifying any frozen contract (M11/M12-A/M12-B).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from plugins.plugin import Plugin, PluginMetadata
from plugins.plugin_capability import PluginCapability
from plugins.plugin_context import PluginContext

# ── Step-type registry (stable — mirrored from RuleEngine _HANDLERS) ──

_KNOWN_STEP_TYPES: set[str] = {
    "replace",
    "remove_text",
    "regex_replace",
    "case",
    "trim",
    "number",
    "insert",
    "date",
    "add_prefix",
    "add_suffix",
}

_REQUIRED_PARAMS: dict[str, set[str]] = {
    "replace": {"from", "to"},
    "remove_text": {"text"},
    "regex_replace": {"pattern", "replacement"},
    "case": {"mode"},
    "trim": {"mode"},
    "number": set(),
    "insert": {"text"},
    "date": set(),
    "add_prefix": {"text"},
    "add_suffix": {"text"},
}

_VALID_CASE_MODES: set[str] = {"upper", "lower", "title", "sentence"}
_VALID_TRIM_MODES: set[str] = {"both", "left", "right"}


# ── Result type ────────────────────────────────────────────────────


@dataclass(frozen=True)
class ValidationIssue:
    """A single validation problem detected in a rule or step."""

    severity: str  # "error" | "warning"
    step_index: int | None  # None = rule-level issue
    message: str


@dataclass
class ValidationResult:
    """Aggregated validation result for a Rule."""

    rule_id: str
    rule_name: str
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not any(i.severity == "error" for i in self.issues)

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "warning")


# ── Plugin ─────────────────────────────────────────────────────────


class RuleValidationPlugin(Plugin):
    """Validates Rule objects for correctness and best practices.

    Usage:
        plugin = RuleValidationPlugin()
        registry.register(plugin)
        registry.enable(plugin.name)
        registry.activate(plugin.name)

        result = plugin.validate(rule)
        if not result.is_valid:
            for issue in result.issues:
                print(issue.message)
    """

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="ruleforge.validation",
            version="1.0.0",
            description="Validates Rule objects for common issues",
            author="RuleForge",
            capabilities=(PluginCapability.VALIDATION,),
        )

    def on_activate(self, ctx: PluginContext) -> None:
        # Warm any caches here if needed in future versions.
        pass

    def on_deactivate(self, ctx: PluginContext) -> None:
        # Release any activation resources.
        pass

    # ── Public API ───────────────────────────────────────────────

    def validate(self, rule) -> ValidationResult:  # type: ignore[no-untyped-def]
        """Validate a Rule and return all detected issues.

        The rule argument should be a ``models.rule.Rule`` instance.
        The plugin avoids a hard import to stay loosely coupled.
        """
        result = ValidationResult(
            rule_id=getattr(rule, "id", "?"),
            rule_name=getattr(rule, "name", "?"),
        )
        steps: list = getattr(rule, "steps", []) or []

        # Rule-level checks
        if len(steps) == 0:
            result.issues.append(
                ValidationIssue("warning", None, "Rule has no steps")
            )

        for idx, step in enumerate(steps):
            step_type: str = getattr(step, "type", "")
            params: dict = dict(getattr(step, "parameters", {}) or {})

            if step_type not in _KNOWN_STEP_TYPES:
                result.issues.append(
                    ValidationIssue(
                        "error",
                        idx,
                        f"Unknown step type '{step_type}'",
                    )
                )
                continue

            # Required parameter check
            required = _REQUIRED_PARAMS.get(step_type, set())
            for param in required:
                if param not in params or params[param] == "":
                    result.issues.append(
                        ValidationIssue(
                            "error",
                            idx,
                            f"Step {idx}: '{step_type}' missing required "
                            f"parameter '{param}'",
                        )
                    )

            # Type-specific checks
            if step_type == "regex_replace":
                self._check_regex(idx, params, result)
            elif step_type == "case":
                self._check_case_mode(idx, params, result)
            elif step_type == "trim":
                self._check_trim_mode(idx, params, result)
            elif step_type == "number":
                self._check_number_params(idx, params, result)

        return result

    # ── Parameter validators ─────────────────────────────────────

    @staticmethod
    def _check_regex(
        idx: int, params: dict, result: ValidationResult
    ) -> None:
        pattern = str(params.get("pattern", ""))
        flags_str = str(params.get("flags", ""))
        try:
            flag_val = 0
            if flags_str:
                flag_val = int(flags_str)
            re.compile(pattern, flag_val)
        except re.error as exc:
            result.issues.append(
                ValidationIssue(
                    "error",
                    idx,
                    f"Step {idx}: invalid regex pattern — {exc}",
                )
            )
        except (ValueError, TypeError):
            result.issues.append(
                ValidationIssue(
                    "error",
                    idx,
                    f"Step {idx}: invalid regex flags '{flags_str}'",
                )
            )

    @staticmethod
    def _check_case_mode(
        idx: int, params: dict, result: ValidationResult
    ) -> None:
        mode = str(params.get("mode", ""))
        if mode and mode not in _VALID_CASE_MODES:
            valid = ", ".join(sorted(_VALID_CASE_MODES))
            result.issues.append(
                ValidationIssue(
                    "error",
                    idx,
                    f"Step {idx}: unknown case mode '{mode}' "
                    f"(valid: {valid})",
                )
            )

    @staticmethod
    def _check_trim_mode(
        idx: int, params: dict, result: ValidationResult
    ) -> None:
        mode = str(params.get("mode", ""))
        if mode and mode not in _VALID_TRIM_MODES:
            valid = ", ".join(sorted(_VALID_TRIM_MODES))
            result.issues.append(
                ValidationIssue(
                    "error",
                    idx,
                    f"Step {idx}: unknown trim mode '{mode}' "
                    f"(valid: {valid})",
                )
            )

    @staticmethod
    def _check_number_params(
        idx: int, params: dict, result: ValidationResult
    ) -> None:
        for param in ("start", "step"):
            val = params.get(param)
            if val is not None:
                try:
                    int(str(val))
                except (ValueError, TypeError):
                    result.issues.append(
                        ValidationIssue(
                            "error",
                            idx,
                            f"Step {idx}: '{param}' must be an integer, "
                            f"got '{val}'",
                        )
                    )
        padding = params.get("padding")
        if padding is not None:
            try:
                p = int(str(padding))
                if p < 0:
                    raise ValueError
            except (ValueError, TypeError):
                result.issues.append(
                    ValidationIssue(
                        "error",
                        idx,
                        f"Step {idx}: 'padding' must be a non-negative "
                        f"integer, got '{padding}'",
                    )
                )
