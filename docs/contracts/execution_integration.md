# Execution Integration — Runtime Contract

| Field | Value |
|---|---|
| **Status** | Accepted |
| **Baseline** | M12 Frozen |
| **Type** | Normative |
| **Applies To** | Execution Runtime |
| **Last Updated** | 2026-08-01 |

---

## 1. Purpose

`ExecutionIntegrationService` (`ui/execution_integration.py`) connects the
Planning Layer (`RenamePlanEngine`) to the Execution Layer
(`ExecutionPipeline`).

This component is **not a business layer**.  It does not perform planning,
policy application, validation, conflict detection, or history management.

This contract defines the component's normative boundary.  All future
maintenance must respect these constraints.

---

## 2. Scope

### Included

- **Lifecycle Coordination** — QThread wiring (`ExecutionWorker`) for
  non-blocking GUI execution.
- **ExecutionContext Construction** — builds `ExecutionContext` from
  `RenamePlan.source` and `Rule`.
- **Pipeline Invocation** — calls `ExecutionPipeline.run(ctx, engine)`.
- **Result Mapping** — maps `ExecutionResult.diagnostics["operations_journal"]`
  to `RenameResult` + `plan.status` back-write.

### Excluded

- **RenamePolicy** — policy resolution is the sole responsibility of
  `RenamePlanEngine.generate()` (`engine/rename_plan_engine.py:74-103`).
- **Validation** — filename legality checks are the sole responsibility of
  `check_legality()` (`validator/validator.py:16-30`), called from
  `RenamePlanEngine.generate()`.
- **Conflict Detection** — target collision and Windows CI detection are
  the sole responsibility of `RenamePlanEngine._detect_conflicts()`
  (`engine/rename_plan_engine.py:108-140`).
- **History** — cross-run operation history is the sole responsibility of
  `OperationLogger` (`engine/operation_logger.py`).
- **Metadata Injection** — `RuleAnalysis` and `MetadataProvider` usage
  belongs to the Planning Layer (Preview phase), not the Integration Layer.
- **Business Rules** — no domain logic of any kind.

---

## 3. Inputs

| Input | Source | Type | Description |
|---|---|---|---|
| **RenamePlan** | `RenamePlanEngine.generate()` | `models.rename_plan.RenamePlan` | Fully resolved plan with `action` (RENAME/OVERWRITE/SKIP/FAIL), `status`, `source` (Path), `target` (Path) |
| **Rule** | `MainWindow._current_rule()` | `models.rule.Rule` | The active rule defining transformation steps |
| **OperationLogger** | `MainWindow._logger` | `engine.operation_logger.OperationLogger` | Existing logger instance for recording results |

### Input Contract

- `plan.action` is already resolved.  The Integration Layer does not
  re-evaluate or override it.
- `plan.source` must exist on the filesystem (validated by
  `RenamePlanEngine.generate()` before the Integration Layer is invoked).
- `rule.steps` must be non-empty (enforced by `ExecutionContext.__post_init__`).

---

## 4. Outputs

| Output | Destination | Type | Description |
|---|---|---|---|
| **ExecutionResult** | `ExecutionPipeline.run()` return | `engine.execution_pipeline.ExecutionResult` | Structured result with `outputs`, `diagnostics`, `trace`, `metrics` |
| **ExecutionTrace** | `ExecutionResult.trace` | `engine.execution_trace.ExecutionTrace` | Per-run lifecycle events and timing |
| **ExecutionMetrics** | `ExecutionResult.metrics` | `engine.execution_metrics.ExecutionMetrics` | Structured statistics (files_modified, error_count, duration_ms) |
| **RenameResult** | `OperationLogger.record()` | `models.rename_result.RenameResult` | Per-plan result for log display compatibility |
| **Rollback History** | `RollbackPlugin.record_rename()` | `plugins.rollback_plugin.RollbackPlugin` | LIFO rollback entries for undo |

### Output Contract

- `plan.status` is written back (SUCCESS / OVERWRITTEN / FAILED) for
  `_on_rename_finished` GUI compatibility.  This is a **GUI compatibility
  mutation**, not a business logic decision.
- `RenameResult` objects are created from `operations_journal` dict entries
  via pure type conversion (dict → dataclass).

---

## 5. Responsibilities

The Integration Layer **may**:

| # | Responsibility | Implementation |
|---|---|---|
| 1 | Manage execution lifecycle | `ExecutionWorker.run()` — iterate plans, call `execute()`, emit signals |
| 2 | Construct `ExecutionContext` | `ExecutionContext(rule=rule, targets=[str(plan.source)])` — `ui/execution_integration.py:55-58` |
| 3 | Invoke `ExecutionPipeline` | `ExecutionPipeline.run(ctx, engine)` — `ui/execution_integration.py:60` |
| 4 | Map `ExecutionResult` to GUI models | `operations_journal` → `RenameResult` + `plan.status` — `ui/execution_integration.py:62-91` |
| 5 | Record to `RollbackPlugin` | `record_rename(op["source"], op["target"])` — `ui/execution_integration.py:77` |
| 6 | Record to `OperationLogger` | `logger.record(rr)` — `workers/execution_worker.py:60` |

---

## 6. Non-Responsibilities

The Integration Layer **must never**:

| # | Forbidden Operation | Why |
|---|---|---|
| 1 | **Modify RenamePlan semantics** | `plan.action`, `plan.target`, `plan.source_name` are immutable post-planning. Only `plan.status` may be back-written for GUI compatibility. |
| 2 | **Create RenamePlan** | `RenamePlanEngine.generate()` is the sole RenamePlan source. |
| 3 | **Modify RenamePolicy** | Policy is resolved before this layer is invoked. |
| 4 | **Execute Validation** | `check_legality()` is called in the Planning Layer. |
| 5 | **Execute Conflict Detection** | `_detect_conflicts()` is called in the Planning Layer. |
| 6 | **Save History** | `OperationLogger` manages cross-run history. The Integration Layer only records single-run results. |
| 7 | **Implement Business Rules** | No domain logic of any kind. |

---

## 7. Architecture Constraints

The following constraints are **normative**.  Violating any of them
requires a new ADR or a new Major Milestone (M13+).

### 7.1 RenamePlanEngine — Planning SSOT

`RenamePlanEngine` (`engine/rename_plan_engine.py`) is the **sole
authoritative source** for RenamePlan generation, RenamePolicy
application, filename validation, and conflict detection.

No other component may replicate or replace these capabilities.

### 7.2 ExecutionPipeline — Primary Execution Runtime

`ExecutionPipeline.run()` (`engine/execution_pipeline.py`) is the
**only execution entry point** for runtime operations.  All execution
flows must go through it.

### 7.3 RollbackPlugin — Unified Rollback

`RollbackPlugin` (`plugins/rollback_plugin.py`) is the **unified
rollback capability**.  No separate undo system, no ad-hoc file
restoration.

### 7.4 ExecutionIntegrationService — Thin Integration Layer

`ExecutionIntegrationService` must remain a **Thin Integration Layer**
(A/B/C class only: pure call adaptation, type conversion, existing
capability reuse).  It must not evolve into a Business Layer.

### 7.5 No New Business Layer

The Integration Layer must not become a new Business Layer through
gradual accumulation of logic.  Any capability that requires domain
knowledge (policy, validation, conflict detection, history management)
must be placed in its designated SSOT component — not in the
Integration Layer.

---

## 8. Contract Authority

**This contract is normative.**

If implementation, documentation, and architectural intent diverge,
resolution follows this hierarchy:

1. **Accepted ADR** — the Architecture Decision Record that authorized
   this integration ([ADR-007](adr/007-execution-integration.md)).
2. **Architecture Review** — formal review against this contract and
   the Architecture Change Checklist
   ([`docs/governance/ARCHITECTURE_CHANGE_CHECKLIST.md`](../governance/ARCHITECTURE_CHANGE_CHECKLIST.md)).
3. **Implementation update** — code is corrected to match the contract.

The contract is **not** updated to match divergent implementation.
Implementation that violates this contract is a defect.

---

## 10. Compliance Checklist

Before modifying `ExecutionIntegrationService` or `ExecutionWorker`,
complete this checklist.  If **any** item is answered **Yes**, an
Architecture Review is required — the change must not be implemented
directly.

### Architecture Review Checklist

| # | Check | Answer |
|---|---|---|
| 1 | Does this change add a new business rule? | ☐ |
| 2 | Does this change add validation logic? | ☐ |
| 3 | Does this change add RenamePolicy logic? | ☐ |
| 4 | Does this change add conflict detection? | ☐ |
| 5 | Does this change modify RenamePlan semantics (beyond `plan.status` back-write)? | ☐ |
| 6 | Does this change add history management? | ☐ |
| 7 | Does this change add metadata injection? | ☐ |
| 8 | Does this change bypass `ExecutionPipeline`? | ☐ |
| 9 | Does this change add runtime decision logic? | ☐ |

### Process

1. Complete the checklist for every proposed change.
2. If all answers are **No**, the change is within Maintenance boundaries.
3. If **any** answer is **Yes**:
   - Do **not** implement the change.
   - Initiate an Architecture Review against this contract and
     [ADR-007](adr/007-execution-integration.md).
   - Proceed only after formal approval (ADR amendment or M13+).

---

## 11. Cross References

| Document | Relationship |
|---|---|
| [`docs/architecture/runtime_architecture.md`](../architecture/runtime_architecture.md) | Runtime architecture — describes the execution flow this contract governs |
| [`docs/architecture/adr/007-execution-integration.md`](../architecture/adr/007-execution-integration.md) | ADR-007 — the decision that authorized this integration |
| [`PROJECT_IDENTITY.md`](../../PROJECT_IDENTITY.md) | Project identity — Section 4.1 defines the runtime architecture layers |
| [`docs/AI/ADR_INDEX.md`](../AI/ADR_INDEX.md) | ADR Index — ADR-013 references this integration |
| [`docs/governance/ARCHITECTURE_CHANGE_CHECKLIST.md`](../governance/ARCHITECTURE_CHANGE_CHECKLIST.md) | Architecture change governance |
| [`engine/execution_pipeline.py`](../../engine/execution_pipeline.py) | ExecutionPipeline — the execution entry point (frozen, M11) |
| [`plugins/rollback_plugin.py`](../../plugins/rollback_plugin.py) | RollbackPlugin — the unified rollback capability (frozen, M12-D) |

---

*Normative.  M12 Frozen Baseline.  Do not modify without ADR.*
