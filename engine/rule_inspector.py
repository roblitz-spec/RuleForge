"""RuleInspector — pure-function Rule analysis and inspection.

Provides structured breakdown of a Rule's steps, dependencies,
and completeness — no state, no UI, no filesystem access.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from models.rule import Rule
from models.rule_step import RuleStep

# Step-type metadata: description template and key parameters
_STEP_INFO: dict[str, dict[str, object]] = {
    "replace":       {"label": "Replace",        "params": ["from", "to"]},
    "remove_text":   {"label": "Remove Text",    "params": ["text"]},
    "regex_replace": {"label": "Regex Replace",  "params": ["pattern", "replacement"]},
    "case":          {"label": "Change Case",     "params": ["mode"]},
    "trim":          {"label": "Trim",            "params": ["mode"]},
    "number":        {"label": "Number",          "params": ["start", "step", "padding", "position"]},
    "insert":        {"label": "Insert Text",     "params": ["text", "at_index"]},
    "date":          {"label": "Date",            "params": ["source", "format", "position", "separator"]},
    "add_prefix":    {"label": "Add Prefix",      "params": ["text"]},
    "add_suffix":    {"label": "Add Suffix",      "params": ["text"]},
}


@dataclass
class StepInfo:
    """Structured description of a single RuleStep."""
    index: int            # 0-based position in the pipeline
    step_type: str        # e.g. "replace", "case"
    label: str            # human-readable label
    params: dict[str, str]  # key → value (all stringified)
    description: str      # one-line summary, e.g. 'Replace " " → "_"'

    @staticmethod
    def from_step(step: RuleStep, index: int) -> StepInfo:
        info = _STEP_INFO.get(step.type, {"label": step.type, "params": []})
        label = str(info["label"])
        param_names: list[str] = list(info["params"])  # type: ignore[arg-type]
        params = {
            k: str(step.parameters.get(k, ""))
            for k in param_names
        }
        description = _describe(step.type, params)
        return StepInfo(
            index=index,
            step_type=step.type,
            label=label,
            params=params,
            description=description,
        )


def _describe(step_type: str, params: dict[str, str]) -> str:
    """Generate a one-line human-readable summary of a step."""
    if step_type == "replace":
        return f'Replace "{params.get("from", "")}" → "{params.get("to", "")}"'
    if step_type == "remove_text":
        return f'Remove "{params.get("text", "")}"'
    if step_type == "regex_replace":
        return f'Regex: /{params.get("pattern", "")}/ → "{params.get("replacement", "")}"'
    if step_type == "case":
        return f'Change case to {params.get("mode", "")}'
    if step_type == "trim":
        return f'Trim {params.get("mode", "")} whitespace'
    if step_type == "add_prefix":
        return f'Add prefix "{params.get("text", "")}"'
    if step_type == "add_suffix":
        return f'Add suffix "{params.get("text", "")}"'
    if step_type == "insert":
        return f'Insert "{params.get("text", "")}" at position {params.get("at_index", "0")}'
    if step_type == "number":
        return f'Number starting at {params.get("start", "1")}, step {params.get("step", "1")}'
    if step_type == "date":
        return f'Date: {params.get("format", "%Y-%m-%d")} from {params.get("source", "modified")}'
    return f"{step_type}: {params}"


@dataclass
class RuleInspection:
    """Complete inspection result for a Rule."""

    rule_id: str
    rule_name: str
    step_count: int
    steps: list[StepInfo]
    uses_index: bool
    uses_metadata: bool
    is_empty: bool
    warnings: list[str] = field(default_factory=list)

    @staticmethod
    def inspect(rule: Rule) -> RuleInspection:
        from engine.rule_analysis import RuleAnalysis

        analysis = RuleAnalysis.analyze(rule)
        step_infos = [
            StepInfo.from_step(s, i) for i, s in enumerate(rule.steps)
        ]
        return RuleInspection(
            rule_id=rule.id,
            rule_name=rule.name,
            step_count=len(rule.steps),
            steps=step_infos,
            uses_index=analysis.uses_index,
            uses_metadata=analysis.uses_metadata,
            is_empty=len(rule.steps) == 0,
            warnings=[w.message for w in analysis.warnings],
        )
