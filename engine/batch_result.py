"""BatchResult — aggregated results from batch execution.

Pure aggregation layer.  Does NOT add batch-specific fields to
ExecutionResult — each item's ExecutionResult is preserved
unmodified inside BatchItemResult.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from engine.execution_result import ExecutionResult


@dataclass
class BatchItemResult:
    """Result of executing a single BatchItem.

    Fields:
        label: From BatchItem.label (or auto-generated if empty).
        item_index: 0-based position in the batch.
        result: The ExecutionResult produced by ExecutionPipeline.
        engine_name: The engine used for this item.
    """

    label: str
    item_index: int
    result: ExecutionResult
    engine_name: str


@dataclass
class BatchResult:
    """Aggregated result of executing an entire ExecutionBatch.

    Fields:
        item_results: Per-item results, in execution order.
        total_items: Total BatchItems in the batch.
        succeeded: Count of items with result.success == True.
        failed: Count of items with result.success == False.
        skipped: Items not executed (stop_on_error after prior failure).
        duration_ms: Wall-clock duration of the entire batch run.
        success: True iff all items succeeded and none were skipped.
    """

    item_results: list[BatchItemResult] = field(default_factory=list)
    total_items: int = 0
    succeeded: int = 0
    failed: int = 0
    skipped: int = 0
    duration_ms: float = 0.0
    success: bool = True

    def add_item_result(self, item_result: BatchItemResult) -> None:
        self.item_results.append(item_result)
        if item_result.result.success:
            self.succeeded += 1
        else:
            self.failed += 1
            self.success = False

    def mark_skipped(self, count: int = 1) -> None:
        self.skipped += count
        self.success = False

    @classmethod
    def new(cls, total_items: int) -> BatchResult:
        return cls(total_items=total_items)
