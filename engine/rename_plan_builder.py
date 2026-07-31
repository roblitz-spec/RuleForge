"""Rename plan helpers — shared validation, stem computation, and
conflict detection for rename-family ExecutionEngines.

Used by RenameExecutionEngine, DryRunExecutionEngine, and
InspectionExecutionEngine.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from engine.execution_context import ExecutionContext
from engine.filesystem_adapter import FilesystemAdapter
from engine.preview_pipeline import preview_rule


@dataclass
class _RenameOp:
    """Internal rename operation record (also journal entry)."""

    source: str
    target: str
    status: str = "pending"  # pending | success | skipped | failed
    error: str | None = None


_FATAL_STATES = frozenset({"failed"})


def build_rename_plan(
    context: ExecutionContext,
    fs: FilesystemAdapter,
) -> tuple[list[_RenameOp], list[str]]:
    """Validate sources, compute targets, detect conflicts.

    Returns (operations, conflicts).  Conflicts being non-empty
    means execution should be aborted before any filesystem mutation.
    """
    targets = context.targets
    if not targets:
        raise ValueError("ExecutionContext requires at least one target path")
    if not context.rule.steps:
        raise ValueError("Rule has no steps")

    # 1. Validate sources exist
    missing = [t for t in targets if not fs.exists(t)]
    if missing:
        raise ValueError(
            f"Source paths do not exist: {', '.join(missing[:5])}"
            + ("..." if len(missing) > 5 else "")
        )

    # 2. Compute target stems via preview_rule
    stems = [Path(t).stem for t in targets]
    preview = preview_rule(context.rule, stems)
    stem_map = {
        src: entry.output_text
        for src, entry in zip(targets, preview.entries)
    }

    # 3. Build operations
    ops: list[_RenameOp] = []
    for src in targets:
        p = Path(src)
        new_stem = stem_map.get(src, p.stem)
        dst = str(p.parent / f"{new_stem}{p.suffix}")
        ops.append(_RenameOp(source=src, target=dst))

    # 4. Detect conflicts
    conflicts = _detect_conflicts(ops, fs)
    return ops, conflicts


def _detect_conflicts(ops: list[_RenameOp], fs: FilesystemAdapter) -> list[str]:
    conflicts: list[str] = []
    targets_seen: dict[str, str] = {}

    for op in ops:
        if op.target in targets_seen:
            conflicts.append(
                f"Duplicate target '{op.target}' from "
                f"'{targets_seen[op.target]}' and '{op.source}'"
            )
        else:
            targets_seen[op.target] = op.source

        if op.source != op.target and fs.exists(op.target):
            conflicts.append(
                f"Destination already exists: '{op.target}'"
            )

    return conflicts
