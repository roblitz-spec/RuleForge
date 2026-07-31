"""InspectionExecutionEngine — analyze execution without filesystem mutation.

Summarizes execution plan, collects metadata, and estimates scope.
Never touches the filesystem — pure analysis.
"""
from __future__ import annotations

from pathlib import Path

from engine.execution_context import ExecutionContext
from engine.execution_engine import ExecutionEngine
from engine.execution_result import ExecutionResult
from engine.filesystem_adapter import FilesystemAdapter, RealFilesystemAdapter
from engine.rename_plan_builder import build_rename_plan, _RenameOp


class InspectionExecutionEngine(ExecutionEngine):
    """Inspect execution plan and collect metadata.

    Provides execution summary, scope estimation, and statistics
    without any filesystem mutation.  Reuses build_rename_plan() for
    validation and path computation.
    """

    def __init__(self, fs: FilesystemAdapter | None = None) -> None:
        self._fs: FilesystemAdapter = fs or RealFilesystemAdapter()
        self._ops: list[_RenameOp] = []
        self._conflicts: list[str] = []

    def prepare(self, context: ExecutionContext) -> None:
        self._ops, self._conflicts = build_rename_plan(context, self._fs)

    def execute(self, context: ExecutionContext) -> ExecutionResult:
        result = ExecutionResult()

        # Scope estimation
        rename_count = sum(1 for o in self._ops if o.source != o.target)
        skip_count = len(self._ops) - rename_count

        # Stem statistics
        stems = [Path(o.source).stem for o in self._ops]
        transformed = [Path(o.target).stem for o in self._ops]

        result.diagnostics["mode"] = "inspection"
        result.diagnostics["total_targets"] = len(self._ops)
        result.diagnostics["would_rename"] = rename_count
        result.diagnostics["would_skip"] = skip_count
        result.diagnostics["conflict_count"] = len(self._conflicts)
        result.diagnostics["conflicts"] = list(self._conflicts)
        result.diagnostics["source_stems"] = stems
        result.diagnostics["target_stems"] = transformed
        result.diagnostics["rule_name"] = context.rule.name
        result.diagnostics["step_count"] = len(context.rule.steps)

        result.actions_executed = rename_count
        result.actions_skipped = skip_count

        if self._conflicts:
            result.add_error(
                f"Inspection found {len(self._conflicts)} conflict(s)"
            )

        self._populate_journal(result)
        return result

    def cleanup(self, context: ExecutionContext) -> None:
        self._ops.clear()
        self._conflicts.clear()

    def _populate_journal(self, result: ExecutionResult) -> None:
        sorted_ops = sorted(self._ops, key=lambda o: o.source)
        result.diagnostics["operations_journal"] = [
            {"source": o.source, "target": o.target, "status": o.status, "error": o.error}
            for o in sorted_ops
        ]
        result.diagnostics["order"] = "source_path_ascending"
