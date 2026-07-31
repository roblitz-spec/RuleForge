"""BatchExecutor — run an ExecutionBatch through ExecutionPipeline.

Pure execution coordination.  Delegates each BatchItem to
ExecutionPipeline.run() with the appropriate engine.  Owns the
batch-level error strategy (stop_on_error) and pre-validation
(validate_first).

Anti-nesting guard: BatchItem.engine_name must not be "batch".
"""
from __future__ import annotations

import time

from engine.batch_result import BatchItemResult, BatchResult
from engine.engine_registry import EngineRegistry
from engine.execution_batch import BatchItem, ExecutionBatch
from engine.execution_context import ExecutionContext
from engine.execution_pipeline import ExecutionPipeline
from engine.execution_result import ExecutionResult


class BatchExecutor:
    """Execute an ExecutionBatch by iterating through BatchItems.

    Each item goes through:
        registry.create(engine_name) → ExecutionContext → ExecutionPipeline.run()

    Usage:
        batch = ExecutionBatch(items=[...])
        executor = BatchExecutor()
        result = executor.run(batch)
    """

    @staticmethod
    def run(
        batch: ExecutionBatch,
        registry: EngineRegistry | None = None,
    ) -> BatchResult:
        """Execute a batch and collect aggregated results.

        Args:
            batch: The ExecutionBatch to execute.
            registry: EngineRegistry for resolving engine_name.
                      Defaults to EngineRegistry.default().

        Returns:
            BatchResult with per-item results and summary statistics.

        Raises:
            ValueError: If any BatchItem has engine_name="batch"
                        (anti-nesting guard).
        """
        reg = registry or EngineRegistry.default()
        start = time.monotonic()
        result = BatchResult.new(len(batch.items))

        # ── Anti-nesting guard ─────────────────────────────────
        for item in batch.items:
            if item.engine_name == "batch":
                raise ValueError(
                    "BatchExecutionEngine cannot be nested — "
                    "BatchItem.engine_name must not be 'batch'"
                )

        # ── Pre-validation ─────────────────────────────────────
        if batch.validate_first:
            for i, item in enumerate(batch.items):
                try:
                    eng = reg.create(item.engine_name)
                    ctx = ExecutionContext(
                        rule=item.rule,
                        targets=item.targets,
                        options=dict(item.options),
                    )
                    eng.prepare(ctx)
                except Exception as exc:
                    label = item.label or f"item-{i}"
                    err_result = batch_result_from_error(
                        f"Pre-validation failed [{label}]: {exc}"
                    )
                    item_result = BatchItemResult(
                        label=label,
                        item_index=i,
                        result=err_result,
                        engine_name=item.engine_name,
                    )
                    result.add_item_result(item_result)
                    if batch.stop_on_error:
                        result.mark_skipped(len(batch.items) - i - 1)
                        result.duration_ms = (time.monotonic() - start) * 1000
                        return result

        # ── Execute ────────────────────────────────────────────
        for i, item in enumerate(batch.items):
            try:
                ctx = ExecutionContext(
                    rule=item.rule,
                    targets=list(item.targets),
                    options=dict(item.options),
                )
                eng = reg.create(item.engine_name)
                exec_result = ExecutionPipeline.run(ctx, eng)
            except Exception as exc:
                exec_result = ExecutionResult.from_error(str(exc))
                exec_result.diagnostics["item_label"] = item.label or f"item-{i}"

            label = item.label or f"item-{i}"
            item_result = BatchItemResult(
                label=label,
                item_index=i,
                result=exec_result,
                engine_name=item.engine_name,
            )
            result.add_item_result(item_result)

            if not exec_result.success and batch.stop_on_error:
                result.mark_skipped(len(batch.items) - i - 1)
                break

        result.duration_ms = (time.monotonic() - start) * 1000
        return result


def batch_result_from_error(message: str) -> ExecutionResult:
    return ExecutionResult.from_error(message)
