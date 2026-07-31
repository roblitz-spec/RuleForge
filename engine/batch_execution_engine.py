"""BatchExecutionEngine — ExecutionEngine adapter for batch execution.

Wraps BatchExecutor as an ExecutionEngine so batch execution plugs
into the ExecutionPipeline like any other engine.  The batch
definition (ExecutionBatch) is stored in ExecutionContext.options.

Follows M11 principle #6: new execution modes are Engines, not
Pipeline branches.
"""
from __future__ import annotations

from engine.batch_executor import BatchExecutor
from engine.batch_result import BatchResult
from engine.engine_registry import EngineRegistry
from engine.execution_batch import ExecutionBatch
from engine.execution_context import ExecutionContext
from engine.execution_engine import ExecutionEngine
from engine.execution_result import ExecutionResult

_BATCH_KEY = "_batch_definition"


class BatchExecutionEngine(ExecutionEngine):
    """Execute an ExecutionBatch defined in ExecutionContext.options.

    The batch definition is passed as:
        context.options["_batch_definition"] = ExecutionBatch(...)

    This Engine exists so batch execution can be selected by name
    ("batch") through EngineRegistry, consistent with other engines.

    Lifecycle:
        prepare(ctx) → extract and validate batch definition
        execute(ctx) → delegate to BatchExecutor
        cleanup(ctx) → clear internal state
    """

    def __init__(self) -> None:
        self._batch: ExecutionBatch | None = None
        self._batch_result: BatchResult | None = None

    def prepare(self, context: ExecutionContext) -> None:
        raw = context.options.get(_BATCH_KEY)
        if raw is None:
            raise ValueError(
                "BatchExecutionEngine requires '_batch_definition' in context.options"
            )
        if not isinstance(raw, ExecutionBatch):
            raise ValueError(
                f"Expected ExecutionBatch, got {type(raw).__name__}"
            )
        if not raw.items:
            raise ValueError("ExecutionBatch has no items")

    def execute(self, context: ExecutionContext) -> ExecutionResult:
        batch: ExecutionBatch = context.options[_BATCH_KEY]  # type: ignore[assignment]
        self._batch = batch

        self._batch_result = BatchExecutor.run(batch)

        result = ExecutionResult()
        result.success = self._batch_result.success
        result.actions_executed = self._batch_result.succeeded
        result.actions_skipped = (
            self._batch_result.failed + self._batch_result.skipped
        )
        result.diagnostics["batch"] = {
            "total_items": self._batch_result.total_items,
            "succeeded": self._batch_result.succeeded,
            "failed": self._batch_result.failed,
            "skipped": self._batch_result.skipped,
            "stop_on_error": batch.stop_on_error,
            "validate_first": batch.validate_first,
        }
        result.diagnostics["per_item"] = [
            {
                "label": ir.label,
                "index": ir.item_index,
                "engine": ir.engine_name,
                "success": ir.result.success,
                "actions_executed": ir.result.actions_executed,
                "actions_skipped": ir.result.actions_skipped,
            }
            for ir in self._batch_result.item_results
        ]

        if not self._batch_result.success:
            # Collect error details from failed items
            for ir in self._batch_result.item_results:
                if not ir.result.success:
                    for err in ir.result.errors:
                        result.add_error(f"[{ir.label or ir.item_index}] {err}")

        result.duration_ms = self._batch_result.duration_ms
        return result

    def cleanup(self, context: ExecutionContext) -> None:
        self._batch = None
        self._batch_result = None
