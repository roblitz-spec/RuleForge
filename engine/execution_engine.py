"""ExecutionEngine — stable contract for execution engines.

All engines (rename, dry-run, validation, inspection) implement
this interface.  Adding a new engine never requires pipeline changes.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from engine.execution_context import ExecutionContext
from engine.execution_result import ExecutionResult


class ExecutionEngine(ABC):
    """Abstract execution engine.

    Lifecycle: prepare → execute → cleanup

    Engines must not manipulate RuleSession or workflow state.
    They receive an immutable ExecutionContext and produce an
    ExecutionResult.
    """

    @abstractmethod
    def prepare(self, context: ExecutionContext) -> None:
        """Validate preconditions and initialize engine state.

        Raises ValueError if preconditions are not met.
        """
        ...

    @abstractmethod
    def execute(self, context: ExecutionContext) -> ExecutionResult:
        """Execute the rule against the context's targets.

        Must return an ExecutionResult even on failure — do not
        leak engine-specific exceptions.
        """
        ...

    @abstractmethod
    def cleanup(self, context: ExecutionContext) -> None:
        """Release resources acquired during prepare/execute.

        Called unconditionally after execute, even on failure.
        """
        ...
