"""ExamplePreview — apply a Rule to string examples and compare results.

Pure function.  No state, no UI, no filesystem access.

Reusable by RuleSession, CLI, API, and IDE.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from engine.rule_inference import _apply_step
from models.rule import Rule


@dataclass
class PreviewEntry:
    """One example preview result."""
    input_text: str
    output_text: str
    expected: str | None = None
    match: bool | None = None  # None if no expected provided


@dataclass
class ExamplePreviewResult:
    """Result of previewing a Rule against a set of examples."""

    entries: list[PreviewEntry] = field(default_factory=list)
    all_match: bool = True

    @property
    def total(self) -> int:
        return len(self.entries)

    @property
    def matched(self) -> int:
        return sum(1 for e in self.entries if e.match is True)

    @property
    def failed(self) -> int:
        return sum(1 for e in self.entries if e.match is False)


def preview_rule(
    rule: Rule,
    examples: list[str],
    expected: list[str] | None = None,
) -> ExamplePreviewResult:
    """Apply *rule* to each example string, compare to expected if provided.

    Args:
        rule: The Rule to apply.
        examples: List of input strings.
        expected: Optional list of expected outputs (same length as examples).

    Returns:
        ExamplePreviewResult with one PreviewEntry per example.
    """
    entries: list[PreviewEntry] = []
    all_match = True

    for i, text in enumerate(examples):
        result = text
        for step in rule.steps:
            result = _apply_step(result, step)

        exp = expected[i] if expected and i < len(expected) else None
        match = (result == exp) if exp is not None else None
        if match is False:
            all_match = False

        entries.append(PreviewEntry(
            input_text=text,
            output_text=result,
            expected=exp,
            match=match,
        ))

    return ExamplePreviewResult(entries=entries, all_match=all_match)
