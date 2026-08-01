# ADR-007: Execution Integration (M12 Maintenance)

## Status

Accepted. M12 Frozen Baseline.

## Context

M12 completed the Capability Plugin Platform (M12-B through M12-K):
9 capability plugins, Batch Execution, Plugin Framework — all on top
of the M11 Execution Platform.  The Execution Platform (`ExecutionPipeline`,
`ExecutionContext`, `ExecutionResult`, `EngineRegistry`) was fully tested
and frozen.

The GUI (`ui/main_window.py`) continued to use pre-M11 execution APIs:
`RenameEngine.rename()` and `UndoEngine.undo()`.  These are superseded by
`RenameExecutionEngine` and `RollbackPlugin` respectively.

The goal was **Execution Layer Integration, not architecture refactoring**.
The project is in Maintenance Mode (M12 Frozen Baseline).  Any change that
modifies frozen modules, rewrites business logic, or introduces new
capabilities requires a new Major Milestone.

## Decision

1. **GUI stays Legacy** — `MainWindow` continues to use `RenamePlanEngine`
   for planning, `OperationLogger` for logging, `ScanWorker` for scanning.
   No GUI rewrite, no new UI framework.

2. **RenamePlanEngine stays Planning SSOT** — `RenamePlanEngine.generate()`
   remains the sole source of `RenamePlan`, RenamePolicy application,
   filename validation, and conflict detection.  The Integration Layer
   does not replicate any of these.

3. **Execution switches to RuleForge Execution Platform** — `RenameEngine.rename()`
   is replaced by `ExecutionPipeline.run()` with `RenameExecutionEngine`.
   The Integration Layer (`ExecutionIntegrationService`) handles the
   `ExecutionContext` construction and `ExecutionResult` mapping.

4. **Rollback uses RollbackPlugin** — `UndoEngine.undo()` is replaced by
   `RollbackPlugin.rollback()`.  `record_rename()` is called after each
   successful execution.  `UndoEngine` module remains for legacy test
   compatibility but is no longer called from production code.

5. **ExecutionIntegrationService is a Thin Integration Layer** — it
   performs lifecycle coordination, `ExecutionContext` construction,
   `ExecutionPipeline` invocation, and `ExecutionResult` mapping only.
   It contains zero business logic.

## Consequences

### Gained

- Execution Platform (`ExecutionPipeline` / `RenameExecutionEngine`) as
  the unified execution runtime — replacing ad-hoc `RenameEngine.rename()`
- Rollback via `RollbackPlugin` — LIFO undo with structured `RollbackResult`,
  replacing `UndoEngine`'s `OperationLogger`-based reverse
- Execution observability (`ExecutionTrace`, `ExecutionMetrics`) per run —
  replacing ad-hoc print-based logging
- Backward compatibility: all 1066 existing non-GUI tests pass; GUI
  signal contracts preserved (`progress_changed`, `finished_with_result`)

### Excluded (not in scope)

- Rule IDE
- Workspace
- GUI rewrite
- RenamePlan migration (moving plan generation to new API)
- Workflow Designer

## Future Direction

All excluded capabilities above require a new Major Milestone (M13+),
planned and approved through formal governance.  They must not be
implemented as incremental extensions of M12.

Specifically:

- **RenamePlan migration** (replacing `RenamePlanEngine.generate()` with
  new API) requires extracting RenamePolicy / validation / Windows CI
  as standalone public APIs — a refactoring of the Planning Layer that
  exceeds Maintenance boundaries.

- **Rule IDE / Workspace** are new application-level features that
  require new UI modules and design — not Execution Platform extensions.

---

## Architecture Invariants

The following constraints are part of the **M12 Frozen Baseline**.
Any modification that violates these requires a new ADR or a new
Major Milestone.

### 1. RenamePlanEngine — Planning SSOT

`RenamePlanEngine` (`engine/rename_plan_engine.py`) is the **sole
authoritative source** for:

| Capability | Location |
|---|---|
| RenamePlan generation | `RenamePlanEngine.generate()` — `rename_plan_engine.py:47-105` |
| RenamePolicy application (FAIL/SKIP/OVERWRITE) | `rename_plan_engine.py:74-103` |
| Filename validation (`check_legality`) | `validator/validator.py:16-30`, called from `rename_plan_engine.py:49-57` |
| Conflict detection (target collision + Windows CI) | `_detect_conflicts()` — `rename_plan_engine.py:108-140` |

No other component may replicate or replace these capabilities.

### 2. ExecutionIntegrationService — Allowed Operations

`ExecutionIntegrationService` (`ui/execution_integration.py`) is permitted
to perform **only**:

- Lifecycle coordination (QThread wiring in `ExecutionWorker`)
- `ExecutionContext` construction from `plan.source` + `rule`
- `ExecutionPipeline.run()` invocation
- `ExecutionResult.diagnostics["operations_journal"]` → `RenameResult` mapping
- `plan.status` back-write (GUI compatibility, not business logic)

### 3. ExecutionIntegrationService — Forbidden Operations

`ExecutionIntegrationService` must **never** contain:

- Business rules
- RenamePolicy logic
- Filename validation
- Conflict detection
- History store creation or management
- Metadata injection

### 4. ExecutionPipeline — Primary Execution Runtime

`ExecutionPipeline.run()` (`engine/execution_pipeline.py`) is the
**primary execution entry point** for runtime operations.  All
execution flows go through it.  Direct `Engine.execute()` calls
without Pipeline orchestration are not permitted in production paths.

### 5. RollbackPlugin — Unified Rollback

`RollbackPlugin` (`plugins/rollback_plugin.py`) is the **unified
rollback capability**.  All undo/rollback operations use it.
No separate undo system, no ad-hoc file restoration.

### 6. Frozen Baseline

These invariants are part of the **M12 Frozen Baseline**.  Changes
require:

- A new Architecture Decision Record that explicitly supersedes
  or amends this ADR, **AND**
- Approval through the Architecture Change Checklist
  (`docs/governance/ARCHITECTURE_CHANGE_CHECKLIST.md`), **OR**
- A new Major Milestone (M13+) planned through formal governance

---

## Evidence

- `ui/execution_integration.py` — Thin Integration Layer, 103 lines,
  zero business logic (verified by code evidence review)
- `workers/execution_worker.py` — QThread wrapper, 64 lines,
  zero business logic
- `docs/architecture/runtime_architecture.md` — Runtime architecture
  documentation, 5 sections
- Test suite: 9 new integration tests pass; 1066/1067 existing tests
  pass (1 pre-existing flaky)
- Frozen module audit: 11/11 frozen modules CLEAN (zero modifications)
- `ui/main_window.py` diff: 8 targeted changes, imports + worker
  replacement + undo migration, no logic changes
