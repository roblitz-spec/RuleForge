from __future__ import annotations

from dataclasses import dataclass, field

from models.rule import Rule

# ── step types whose empty-param check targets a specific key ──
_EMPTY_PARAM_CHECKS: dict[str, str] = {
    "remove_text": "text",
    "add_prefix": "text",
    "add_suffix": "text",
    "regex_replace": "pattern",
    "replace": "from",
}


@dataclass
class RuleWarning:
    """A non-blocking advisory raised during rule analysis."""

    code: str
    message: str

    # ── known warning codes ──────────────────────────────
    EMPTY_RULE = "empty_rule"
    EMPTY_PARAM = "empty_param"


@dataclass
class RuleAnalysis:
    """Rule 对 Context 的依赖声明。

    在 Preview 循环外调用 analyze() 一次，结果在循环中复用。
    """

    uses_index: bool = False
    uses_metadata: bool = False
    warnings: list[RuleWarning] = field(default_factory=list)

    @staticmethod
    def analyze(rule: Rule) -> RuleAnalysis:
        result = RuleAnalysis()
        # empty rule
        if not rule.steps:
            result.warnings.append(RuleWarning(
                code=RuleWarning.EMPTY_RULE,
                message="规则没有步骤，不会改变文件名。",
            ))
            return result

        for step in rule.steps:
            if step.type == "number":
                result.uses_index = True
            elif step.type == "date":
                result.uses_metadata = True

            # empty-param check
            check_key = _EMPTY_PARAM_CHECKS.get(step.type)
            if check_key is not None:
                val = str(step.parameters.get(check_key, ""))
                if not val:
                    result.warnings.append(RuleWarning(
                        code=RuleWarning.EMPTY_PARAM,
                        message=f"「{step.type}」步骤的 {check_key} 为空，不会改变文件名。",
                    ))

        return result

    def format_warnings(self) -> str | None:
        """WP-14: render warnings as display text (pure function, no Qt dependency)."""
        if not self.warnings:
            return None
        return "\n".join(f"⚠ {w.message}" for w in self.warnings)
