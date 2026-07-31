# M12-A: Batch Execution Foundation

**Status**: Frozen (2026-07-31)
**Parent**: M11 Execution Platform v1
**Commit**: `cc2255c87b43052f460b89be4e8d427b7860e6ff`

## Architecture Overview

M12-A extends M11 Execution Platform with batch execution capability — running
multiple (Rule, targets) pairs as a single coordinated operation.  Each
batch item is an independent `ExecutionPipeline.run()` invocation; the
batch layer owns only ordering, error strategy, and result aggregation.

```
RuleWorkflow.execute_batch()
        │
        ▼
BatchExecutor.run(ExecutionBatch)
        │  对每个 BatchItem:
        │    registry.create(engine_name)
        │    → ExecutionContext(rule, targets, options)
        │    → ExecutionPipeline.run(ctx, engine)
        │    → 收集 ExecutionResult → BatchItemResult
        │
        ▼
BatchResult (聚合层: succeeded/failed/skipped + per-item results)

旁路 (通过 EngineRegistry):
  ExecutionContext(options={"_batch_definition": ExecutionBatch(...)})
    → ExecutionPipeline.run(ctx, BatchExecutionEngine())
      → BatchExecutionEngine.execute()
        → BatchExecutor.run(batch)
        → 映射 BatchResult → ExecutionResult
```

## Components

### ExecutionBatch (`engine/execution_batch.py`)

Ordered collection of `BatchItem` with execution policy.

```python
@dataclass(frozen=True)
class BatchItem:
    rule: Rule                               # committed Rule
    targets: list[str]                       # string inputs or file paths
    engine_name: str = "string"              # resolved via EngineRegistry
    label: str = ""                          # human-readable identifier
    options: dict[str, object] = {}          # forwarded to ExecutionContext

@dataclass
class ExecutionBatch:
    items: list[BatchItem]
    stop_on_error: bool = True               # abort on first failure
    validate_first: bool = True              # pre-validate all engines
```

**Design decisions**:
- `BatchItem` is frozen — batch definitions are declarative, not mutable state
- `ExecutionBatch` is mutable only for policy fields (rarely changed after construction)
- `engine_name` defaults to `"string"` — simplest engine, zero side effects
- `options` allows passing `dry_run`, `_batch_definition`, or custom flags per item

### BatchExecutor (`engine/batch_executor.py`)

Pure coordination.  Owns the batch execution loop — no domain logic,
no engine-specific branches, no filesystem access.

```python
class BatchExecutor:
    @staticmethod
    def run(
        batch: ExecutionBatch,
        registry: EngineRegistry | None = None,
    ) -> BatchResult: ...
```

Execution order:
1. **Anti-nesting guard**: reject `engine_name == "batch"` → `ValueError`
2. **Pre-validation** (if `validate_first`): create engine for each item, call `prepare()`
3. **Execute**: for each item, `registry.create()` → `ExecutionContext` → `ExecutionPipeline.run()`
4. **Error handling**: `try/except` around each item; `stop_on_error` controls early termination

### BatchResult (`engine/batch_result.py`)

Independent aggregation layer.  Does NOT modify `ExecutionResult` — each
item's complete `ExecutionResult` is preserved in `BatchItemResult.result`.

```python
@dataclass
class BatchItemResult:
    label: str
    item_index: int
    result: ExecutionResult       # unmodified M11 contract
    engine_name: str

@dataclass
class BatchResult:
    item_results: list[BatchItemResult]
    total_items: int
    succeeded: int                 # items where result.success == True
    failed: int                    # items where result.success == False
    skipped: int                   # not executed (stop_on_error)
    duration_ms: float
    success: bool                  # True iff all succeeded, none skipped
```

### BatchExecutionEngine (`engine/batch_execution_engine.py`)

`ExecutionEngine` adapter — wraps batch execution as a standard Engine so
it can be selected by name via `EngineRegistry`.  Follows M11 principle #6.

```python
class BatchExecutionEngine(ExecutionEngine):
    def prepare(self, context: ExecutionContext) -> None:
        # Extract ExecutionBatch from context.options["_batch_definition"]
        # Validate: exists, is ExecutionBatch, has items

    def execute(self, context: ExecutionContext) -> ExecutionResult:
        # Delegate to BatchExecutor.run()
        # Map BatchResult fields → ExecutionResult fields

    def cleanup(self, context: ExecutionContext) -> None:
        # Clear internal state
```

`ExecutionResult` mapping:

| BatchResult | ExecutionResult |
|---|---|
| `succeeded` | `actions_executed` |
| `failed + skipped` | `actions_skipped` |
| `success` | `success` |
| `duration_ms` | `duration_ms` |
| per-item results | `diagnostics["batch"]` + `diagnostics["per_item"]` |
| item errors | `errors[]` (prefixed with item label) |

## Design Principles

1. **ExecutionPipeline is the atomic unit.**  BatchExecutor delegates each item
   to `ExecutionPipeline.run()` — no inline reimplementation of the lifecycle.

2. **BatchResult is an aggregation layer, not an ExecutionResult modification.**
   Each item's `ExecutionResult` is preserved unmodified inside `BatchItemResult`.

3. **No nested batch execution.**  `BatchItem.engine_name == "batch"` raises
   `ValueError`.  Guard lives in `BatchExecutor.run()` — not in Registry or
   Pipeline.

4. **Batch is an Engine, not a Pipeline branch.**  `BatchExecutionEngine`
   implements `ExecutionEngine` so batch execution integrates through the
   standard execution path.

5. **Pure coordination, zero domain logic.**  `BatchExecutor` contains no
   rule processing, file operations, or engine-specific knowledge.

## Public API

| API | Module | Stability |
|---|---|---|
| `BatchItem` | `engine.execution_batch` | Frozen |
| `ExecutionBatch` | `engine.execution_batch` | Frozen |
| `BatchItemResult` | `engine.batch_result` | Frozen |
| `BatchResult` | `engine.batch_result` | Frozen |
| `BatchExecutor.run()` | `engine.batch_executor` | Frozen |
| `BatchExecutionEngine` | `engine.batch_execution_engine` | Frozen |
| `RuleWorkflow.execute_batch()` | `engine.rule_workflow` | Frozen |
| `EngineRegistry.default()` → `"batch"` | `engine.engine_registry` | Frozen |

## M11 Frozen Contract Verification

| M11 Component | M12-A Impact |
|---|---|
| `ExecutionEngine` (ABC) | **Unchanged** — `BatchExecutionEngine` implements, doesn't modify |
| `ExecutionPipeline.run()` | **Unchanged** — called as-is, zero diff |
| `ExecutionContext` (frozen) | **Unchanged** — zero diff |
| `ExecutionResult` | **Unchanged** — zero diff to fields; `diagnostics["batch"]` is engine-specific metadata |
| `EngineRegistry` | **Extended** — `register("batch", ...)` in `default()`, no interface change |
| `RuleWorkflow` | **Extended** — new `execute_batch()` static method, no signature changes to existing methods |

All six M11 frozen principles remain intact.

## Anti-Nesting Guard

`BatchExecutor.run()` rejects any `BatchItem` with `engine_name == "batch"`:

```python
for item in batch.items:
    if item.engine_name == "batch":
        raise ValueError(
            "BatchExecutionEngine cannot be nested — "
            "BatchItem.engine_name must not be 'batch'"
        )
```

Test coverage: single-item batch (`test_batch_engine_name_rejected_in_batch_item`)
and multi-item batch with one nested item (`test_batch_engine_name_rejected_in_multi_item`).

## Known Limitations

| ID | Limitation | Severity | Plan |
|---|---|---|---|
| KL-01 | `BatchResult` has no `to_dict()` | Low | Add in M12-B (CLI integration) |
| KL-02 | Sequential-only (no parallel) | Low | M12-C (Parallel Execution) |
| KL-03 | `_batch_definition` magic key in `context.options` | Low | Acceptable — `_` prefix convention |
| KL-04 | Unused `EngineRegistry` import in `batch_execution_engine.py` | Trivial | Clean in next maintenance pass |

## Test Coverage

**27 tests** in `tests/test_m12_phase1.py`:

| Class | Tests | Focus |
|---|---|---|
| `TestBatchItem` | 3 | defaults, explicit, frozen |
| `TestExecutionBatch` | 2 | policy defaults, explicit |
| `TestBatchResult` | 4 | init, success, failure, skip counts |
| `TestBatchExecutorSuccess` | 3 | single, multi, timing |
| `TestBatchExecutorStopOnError` | 2 | stop, continue |
| `TestBatchExecutorValidateFirst` | 3 | catch, stop, skip |
| `TestBatchExecutorEmpty` | 1 | empty batch |
| `TestAntiNesting` | 2 | single-item, multi-item |
| `TestBatchExecutionEngine` | 4 | pipeline, failure, missing def, empty def |
| `TestWorkflowBatchIntegration` | 2 | BatchResult type, custom registry |
| `TestBatchInRegistry` | 1 | default registry includes "batch" |

Full regression: **755 passed, 0 failed**.

## File Manifest

| File | Status | Lines |
|---|---|---|
| `engine/execution_batch.py` | New | 46 |
| `engine/batch_result.py` | New | 67 |
| `engine/batch_executor.py` | New | 125 |
| `engine/batch_execution_engine.py` | New | 100 |
| `engine/engine_registry.py` | Modified (+3) | 110 |
| `engine/rule_workflow.py` | Modified (+5) | 239 |
| `tests/test_m12_phase1.py` | New | 305 |
| `tests/test_m11_phase4.py` | Modified (+2) | 228 |
| `AGENTS.md` | Modified (+10) | — |
