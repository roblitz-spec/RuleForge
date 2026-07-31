"""RenameExecutionEngine — rename files through the ExecutionPipeline.

First concrete ExecutionEngine.  Owns rename-specific logic only —
planning, conflict detection, filesystem operations.  Does not
manipulate RuleSession or workflow state.
"""
from __future__ import annotations

from engine.execution_context import ExecutionContext
from engine.execution_engine import ExecutionEngine
from engine.execution_result import ExecutionResult
from engine.filesystem_adapter import FilesystemAdapter, RealFilesystemAdapter
from engine.rename_plan_builder import build_rename_plan, _RenameOp


class RenameExecutionEngine(ExecutionEngine):
    """Execute a Rule as filesystem rename operations.

    Lifecycle:
        prepare(ctx)   → validate sources, compute targets, detect conflicts
        execute(ctx)   → perform renames in deterministic order
        cleanup(ctx)   → clear journal (future: rollback on failure)

    Filesystem operations go through a FilesystemAdapter so the
    engine is testable without real filesystem access.
    """

    def __init__(self, fs: FilesystemAdapter | None = None) -> None:
        self._fs: FilesystemAdapter = fs or RealFilesystemAdapter()
        self._ops: list[_RenameOp] = []
        self._conflicts: list[str] = []

    # ── prepare ───────────────────────────────────────────────────

    def prepare(self, context: ExecutionContext) -> None:
        self._ops, self._conflicts = build_rename_plan(context, self._fs)

    # ── execute ────────────────────────────────────────────────────

    def execute(self, context: ExecutionContext) -> ExecutionResult:
        result = ExecutionResult()

        # Pre-condition: conflicts are fatal
        if self._conflicts:
            for msg in self._conflicts:
                result.add_error(msg)
            result.diagnostics["conflict_count"] = len(self._conflicts)
            result.diagnostics["operations_journal"] = [
                {"source": op.source, "target": op.target, "status": op.status}
                for op in self._ops
            ]
            return result

        # Execute in deterministic order (source path sorted)
        sorted_ops = sorted(self._ops, key=lambda o: o.source)
        for op in sorted_ops:
            if op.source == op.target:
                op.status = "success"
                result.actions_skipped += 1
                continue

            try:
                self._fs.rename(op.source, op.target)
                op.status = "success"
                result.actions_executed += 1
            except Exception as exc:
                op.status = "failed"
                op.error = str(exc)
                result.add_error(f"Rename failed '{op.source}' → '{op.target}': {exc}")
                # Fail-fast: stop on first failure
                break

        # Diagnostics
        result.diagnostics["operations_journal"] = [
            {"source": op.source, "target": op.target, "status": op.status, "error": op.error}
            for op in sorted_ops
        ]
        result.diagnostics["conflict_count"] = 0
        result.diagnostics["order"] = "source_path_ascending"

        return result

    # ── cleanup ────────────────────────────────────────────────────

    def cleanup(self, context: ExecutionContext) -> None:
        self._ops.clear()
        self._conflicts.clear()
