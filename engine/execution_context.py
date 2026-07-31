"""ExecutionContext — immutable snapshot of an execution request.

Independent of CLI, GUI, and concrete engine implementations.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from models.rule import Rule


@dataclass(frozen=True)
class ExecutionContext:
    """Immutable context for a single execution run.

    Fields:
        rule: The Rule to execute.
        targets: String inputs (headless) or file paths (rename).
        options: Runtime configuration (dry_run, trace, etc.).
    """

    rule: Rule
    targets: list[str] = field(default_factory=list)
    options: dict[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.rule.steps:
            raise ValueError("ExecutionContext requires a rule with at least one step")

    @property
    def target_count(self) -> int:
        return len(self.targets)
