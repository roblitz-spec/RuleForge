"""DryRunExecutionEngine — validate and plan without filesystem mutation.

Identical validation and conflict detection to RenameExecutionEngine.
Never calls fs.rename() or fs.delete() — diagnostics only.
"""
from __future__ import annotations

from engine.execution_context import ExecutionContext
from engine.execution_engine import ExecutionEngine
from engine.execution_result import ExecutionResult
from engine.filesystem_adapter import FilesystemAdapter, RealFilesystemAdapter
from engine.rename_plan_builder import build_rename_plan, _RenameOp


class DryRunExecutionEngine(ExecutionEngine):
    """Validate rename plan without modifying the filesystem.

    Shares the same validation, stem computation, and conflict
    detection as RenameExecutionEngine via build_rename_plan().
    """

    def __init__(self, fs: FilesystemAdapter | None = None) -> None:
        self._fs: FilesystemAdapter = fs or RealFilesystemAdapter()
        self._ops: list[_RenameOp] = []
        self._conflicts: list[str] = []

    def prepare(self, context: ExecutionContext) -> None:
        self._ops, self._conflicts = build_rename_plan(context, self._fs)

    def execute(self, context: ExecutionContext) -> ExecutionResult:
        result = ExecutionResult()

        if self._conflicts:
            for msg in self._conflicts:
                result.add_error(msg)
            result.diagnostics["conflict_count"] = len(self._conflicts)
            self._populate_journal(result)
            return result

        for op in sorted(self._ops, key=lambda o: o.source):
            if op.source == op.target:
                op.status = "skipped"
                result.actions_skipped += 1
            else:
                op.status = "success"
                result.actions_executed += 1

        result.diagnostics["mode"] = "dry_run"
        result.diagnostics["would_rename"] = result.actions_executed
        result.diagnostics["would_skip"] = result.actions_skipped
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
