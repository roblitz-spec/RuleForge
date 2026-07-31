"""DomainValidator — UI-independent Rule / RuleStep validation (Master Design AD-03)."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto

from models.rule import Rule
from models.rule_step import RuleStep


class ValidationSeverity(Enum):
    ERROR = auto()
    WARNING = auto()


@dataclass
class ValidationIssue:
    """A single validation finding — data only, no UI formatting."""

    field: str
    message: str
    severity: ValidationSeverity = ValidationSeverity.ERROR


class DomainValidator:
    """UI-independent validation of Rule and RuleStep domain objects.

    All methods are pure functions — they accept domain objects and return
    lists of ValidationIssue.  No Qt, no widgets, no filesystem access.

    Per Master Design Section 4.3, this is the single validation entry point
    for the Editor Core.  UI callers are migrated in WP-3.
    """

    @staticmethod
    def validate_rule(
        rule: Rule,
        existing_rules: list[Rule] | None = None,
    ) -> list[ValidationIssue]:
        """Validate a complete Rule, including all its steps.

        Args:
            rule: The Rule to validate.
            existing_rules: Other rules in the repository (for name-uniqueness
                checks).  If None, uniqueness is not checked.

        Returns:
            List of ValidationIssue — empty list means the rule is valid.
        """
        issues: list[ValidationIssue] = []

        # ── Rule-level checks ──
        name = rule.name.strip() if rule.name else ""
        if not name:
            issues.append(ValidationIssue(
                field="name",
                message="规则名称不能为空。",
            ))
        elif existing_rules is not None:
            for r in existing_rules:
                if r.id != rule.id and r.name == name:
                    issues.append(ValidationIssue(
                        field="name",
                        message=f"规则名称「{name}」已存在。",
                    ))
                    break

        # ── Step-level checks ──
        for i, step in enumerate(rule.steps):
            issues.extend(
                DomainValidator._validate_step(step, prefix=f"steps[{i}]"),
            )

        return issues

    @staticmethod
    def validate_step(step: RuleStep) -> list[ValidationIssue]:
        """Validate a single RuleStep's parameters.

        Returns:
            List of ValidationIssue — empty list means the step is valid.
        """
        return DomainValidator._validate_step(step, prefix="step")

    @staticmethod
    def _validate_step(step: RuleStep, prefix: str) -> list[ValidationIssue]:
        """Internal: validate one step, prefixing field paths."""
        issues: list[ValidationIssue] = []
        tp = step.type
        params = step.parameters

        if tp == "replace":
            if not str(params.get("from", "")):
                issues.append(ValidationIssue(
                    field=f"{prefix}.parameters.from",
                    message="Replace 步骤的 from 不能为空。",
                ))

        elif tp == "regex_replace":
            if not str(params.get("pattern", "")):
                issues.append(ValidationIssue(
                    field=f"{prefix}.parameters.pattern",
                    message="Regex Replace 步骤的 pattern 不能为空。",
                ))

        elif tp == "number":
            try:
                step_val = int(str(params.get("step", "1")))
                if step_val < 1:
                    issues.append(ValidationIssue(
                        field=f"{prefix}.parameters.step",
                        message="Number 步骤的 step 必须 >= 1。",
                    ))
            except ValueError:
                issues.append(ValidationIssue(
                    field=f"{prefix}.parameters.step",
                    message="Number 步骤的 step 不是有效数字。",
                ))

        elif tp == "insert":
            try:
                at_idx = int(str(params.get("at_index", "0")))
                if at_idx < -1:
                    issues.append(ValidationIssue(
                        field=f"{prefix}.parameters.at_index",
                        message="Insert 步骤的 at_index 必须 >= -1。",
                    ))
            except ValueError:
                issues.append(ValidationIssue(
                    field=f"{prefix}.parameters.at_index",
                    message="Insert 步骤的 at_index 不是有效数字。",
                ))

        elif tp == "date":
            fmt = str(params.get("format", ""))
            if not fmt or "%" not in fmt:
                issues.append(ValidationIssue(
                    field=f"{prefix}.parameters.format",
                    message="Date 步骤的 format 必须包含有效的 strftime 格式（例如 %Y-%m-%d）。",
                ))

        return issues
