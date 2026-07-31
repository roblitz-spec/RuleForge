"""RenameExecutionEngine — rename files through the ExecutionPipeline.

First concrete ExecutionEngine.  Owns rename-specific logic only —
planning, conflict detection, filesystem operations.  Does not
manipulate RuleSession or workflow state.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from engine.execution_context import ExecutionContext
from engine.execution_engine import ExecutionEngine
from engine.execution_result import ExecutionResult
from engine.filesystem_adapter import FilesystemAdapter, RealFilesystemAdapter
from engine.preview_pipeline import preview_rule


@dataclass
class _RenameOp:
    """Internal rename operation record.

    Also serves as the journal entry for future rollback support.
    """

    source: str
    target: str
    status: str = "pending"  # pending | success | failed
    error: str | None = None


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
        if not context.targets:
            raise ValueError("ExecutionContext requires at least one target path")
        if not context.rule.steps:
            raise ValueError("Rule has no steps")

        self._ops = []
        self._conflicts = []

        # 1. Validate all sources exist
        missing = [t for t in context.targets if not self._fs.exists(t)]
        if missing:
            raise ValueError(
                f"Source paths do not exist: {', '.join(missing[:5])}"
                + ("..." if len(missing) > 5 else "")
            )

        # 2. Compute target names via preview_rule
        stem_map = self._compute_target_stems(context)

        # 3. Build rename operations
        for src in context.targets:
            p = Path(src)
            new_stem = stem_map.get(src, p.stem)
            dst = str(p.parent / f"{new_stem}{p.suffix}")
            self._ops.append(_RenameOp(source=src, target=dst))

        # 4. Detect conflicts
        self._detect_conflicts()

    def _compute_target_stems(self, context: ExecutionContext) -> dict[str, str]:
        """Apply the rule to each path's stem and return stem map."""
        stems = [Path(t).stem for t in context.targets]
        preview = preview_rule(context.rule, stems)
        return {
            src: entry.output_text
            for src, entry in zip(context.targets, preview.entries)
        }

    def _detect_conflicts(self) -> None:
        """Detect duplicate targets and existing destination conflicts."""
        targets_seen: dict[str, str] = {}
        for op in self._ops:
            if op.target in targets_seen:
                self._conflicts.append(
                    f"Duplicate target '{op.target}' from "
                    f"'{targets_seen[op.target]}' and '{op.source}'"
                )
            else:
                targets_seen[op.target] = op.source

            if op.source != op.target and self._fs.exists(op.target):
                self._conflicts.append(
                    f"Destination already exists: '{op.target}'"
                )

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
