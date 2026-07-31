"""ExecutionResult — stable public contract for execution outcomes.

Single result type for all engines.  Errors are normalized
so engine internals never leak through the public API.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from engine.execution_metrics import ExecutionMetrics
from engine.execution_trace import ExecutionTrace


@dataclass
class ExecutionResult:
    """Result of an execution run.

    Fields:
        success: True iff no errors occurred.
        outputs: Transformed output strings (one per target).
        actions_executed: Count of successful transformations.
        actions_skipped: Count of targets that could not be transformed.
        errors: Normalized error messages (never None).
        diagnostics: Engine-specific metadata (timing, trace, etc.).
        duration_ms: Wall-clock execution time in milliseconds.
        trace: Execution lifecycle trace (M11-E, optional).
        metrics: Structured execution metrics (M11-E, optional).
    """

    success: bool = True
    outputs: list[str] = field(default_factory=list)
    actions_executed: int = 0
    actions_skipped: int = 0
    errors: list[str] = field(default_factory=list)
    diagnostics: dict[str, object] = field(default_factory=dict)
    duration_ms: float | None = None
    trace: ExecutionTrace | None = None
    metrics: ExecutionMetrics | None = None

    def add_error(self, message: str) -> None:
        self.errors.append(message)
        self.success = False

    @property
    def total_actions(self) -> int:
        return self.actions_executed + self.actions_skipped

    @classmethod
    def from_error(cls, message: str) -> ExecutionResult:
        return cls(success=False, errors=[message])
