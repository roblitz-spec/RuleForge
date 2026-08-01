# Runtime Architecture

_M12 Maintenance Integration — Frozen_

> Describes the current runtime execution path from GUI through ExecutionPlatform.
> For platform layer design, see [`overview.md`](overview.md).
> For plugin lifecycle, see [`execution-lifecycle.md`](execution-lifecycle.md).

---

## Section 1 — Runtime Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     GUI (MainWindow)                              │
│  py: ui/main_window.py                                           │
│  User interaction, status display, result reception               │
├─────────────────────────────────────────────────────────────────┤
│                     Planning Layer                                │
│  py: engine/rename_plan_engine.py                                 │
│  RenamePlan generation, RenamePolicy, validation,                 │
│  conflict detection                                              │
├─────────────────────────────────────────────────────────────────┤
│                     Integration Layer                             │
│  py: ui/execution_integration.py                                  │
│  ExecutionContext construction, Pipeline invocation,              │
│  ExecutionResult mapping                                          │
├─────────────────────────────────────────────────────────────────┤
│                     Execution Layer                               │
│  py: engine/execution_pipeline.py                                 │
│     engine/rename_execution_engine.py                             │
│  Pipeline orchestration, Engine execution, Trace collection       │
├─────────────────────────────────────────────────────────────────┤
│                     Rollback Layer                                │
│  py: plugins/rollback_plugin.py                                   │
│  LIFO undo, RollbackResult, history management                   │
└─────────────────────────────────────────────────────────────────┘
```

**Execution Integration belongs to M12 Maintenance Integration.**
It bridges the frozen M11 Execution Platform to the GUI without modifying either.

---

## Section 2 — Layer Responsibilities

### GUI Layer

**Component**: `MainWindow` (`ui/main_window.py`)

| Responsibility | Details |
|---|---|
| User interaction | Browse, scan, select, rename trigger |
| Status display | Progress dialog, success/failure counts |
| Result reception | `_on_rename_finished()` reads `plan.status` |

**Does NOT**: compute plans, apply rules, detect conflicts, record history.

---

### Planning Layer

**Component**: `RenamePlanEngine` (`engine/rename_plan_engine.py`)

| Role | SSOT |
|---|---|
| **RenamePlan — sole source** | `RenamePlanEngine.generate()` constructs every `RenamePlan` consumed by the execution path |
| **RenamePolicy — sole source** | FAIL / SKIP / OVERWRITE resolution (`rename_plan_engine.py:74-103`) |
| **Validation — sole source** | Filename legality checks via `check_legality()` (`validator/validator.py:16-30`) |
| **Conflict Detection — sole source** | Target collision + Windows CI detection (`rename_plan_engine.py:108-140`) |

**Planning output** is a `list[RenamePlan]` with fully resolved `action` and `status` fields.
The Integration Layer executes plans as-is; it never re-evaluates policy, legality, or conflicts.

---

### Integration Layer

**Component**: `ExecutionIntegrationService` (`ui/execution_integration.py`)

| Allowed | Forbidden |
|---|---|
| Lifecycle coordination (QThread wiring in `ExecutionWorker`) | RenamePolicy |
| `ExecutionContext` construction from `plan.source` + `rule` | Validation |
| `ExecutionPipeline.run()` invocation | Conflict Detection |
| `ExecutionResult.diagnostics["operations_journal"]` → `RenameResult` mapping | History store creation |
| `plan.status` back-write for GUI compatibility | Business rules |

**Classification**: Thin Integration Layer (A/B/C class only).

---

### Execution Layer

**Component**: `ExecutionPipeline` (`engine/execution_pipeline.py`)

| Component | Role |
|---|---|
| `ExecutionContext` | Immutable input: `rule` + `targets` |
| `EngineRegistry` | Named engine selection (`"rename"` → `RenameExecutionEngine`) |
| `ExecutionPipeline.run()` | Prepare → Execute → Collect → Trace |
| `ExecutionResult` | Unified output: `outputs`, `diagnostics`, `trace`, `metrics` |

**Current primary execution entry point** for the GUI rename flow.

---

### Rollback Layer

**Component**: `RollbackPlugin` (`plugins/rollback_plugin.py`)

| Method | Role |
|---|---|
| `record_rename(old, new)` | Called after each successful rename |
| `rollback()` | LIFO reverse of all recorded renames |
| `history_size` | Checkable for undo availability |

**Unified rollback capability**. Replaces the pre-M12 `UndoEngine`.

---

## Section 3 — Single Source of Truth

| Capability | SSOT Component | SSOT File |
|---|---|---|
| **RenamePlan** | `RenamePlanEngine.generate()` | `engine/rename_plan_engine.py:47-105` |
| **RenamePolicy** | `RenamePlanEngine.generate()` policy branch | `engine/rename_plan_engine.py:74-103` |
| **Validation** | `check_legality()` | `validator/validator.py:16-30` |
| **Conflict Detection** | `RenamePlanEngine._detect_conflicts()` | `engine/rename_plan_engine.py:108-140` |
| **Execution** | `ExecutionPipeline.run()` | `engine/execution_pipeline.py:18-87` |
| **Rollback** | `RollbackPlugin` | `plugins/rollback_plugin.py:52-148` |
| **Trace** | `ExecutionTrace` + `ExecutionMetrics` | `engine/execution_trace.py` + `engine/execution_metrics.py` |

Each capability has exactly one authoritative source. No dual-SSOT exists in the current runtime path.

---

## Section 4 — Runtime Flow

```
User clicks "Rename"
  │
  ▼
MainWindow._on_rename()                            ui/main_window.py:293
  │
  ├── 1. Collect selected items from table view
  │
  ├── 2. RenamePlanEngine.generate(items, policy)  engine/rename_plan_engine.py:47
  │       │
  │       ├── Compute preview_name per item
  │       ├── check_legality(target_name)           validator/validator.py:16
  │       ├── _detect_conflicts(plans)               rename_plan_engine.py:108
  │       └── Apply RenamePolicy per conflict        rename_plan_engine.py:74
  │
  ├── 3. Block INVALID / CONFLICT plans
  │
  ├── 4. Confirm dialog (RENAME + OVERWRITE count)
  │
  ├── 5. ExecutionWorker.start()                    workers/execution_worker.py:45
  │       │                                         (QThread — non-blocking)
  │       │
  │       ▼
  │     ExecutionIntegrationService.execute()       ui/execution_integration.py:37
  │       │
  │       ├── OVERWRITE: pre-delete plan.target
  │       │
  │       ├── ExecutionContext(rule, targets=       engine/execution_context.py:10
  │       │     [str(plan.source)])
  │       │
  │       ├── EngineRegistry.default()              engine/engine_registry.py
  │       │     .create("rename")
  │       │
  │       ├── ExecutionPipeline.run(ctx, engine)    engine/execution_pipeline.py
  │       │       │
  │       │       ├── Validate context
  │       │       ├── Engine.prepare()
  │       │       │     └── build_rename_plan()     engine/rename_plan_builder.py:30
  │       │       ├── Engine.execute()
  │       │       │     └── RenameExecutionEngine    engine/rename_execution_engine.py:16
  │       │       │         .execute()
  │       │       ├── Engine.cleanup()
  │       │       └── Return ExecutionResult
  │       │
  │       ├── ExecutionResult.diagnostics            ui/execution_integration.py:62
  │       │     ["operations_journal"]
  │       │       │
  │       │       ├── Map to RenameResult             ui/execution_integration.py:78-90
  │       │       ├── Write plan.status                ui/execution_integration.py:72-85
  │       │       └── RollbackPlugin.record_rename()   ui/execution_integration.py:77
  │       │
  │       └── Return RenameResult
  │
  ├── 6. ExecutionWorker emits progress_changed     workers/execution_worker.py:61
  │
  ├── 7. ExecutionWorker emits finished_with_result workers/execution_worker.py:64
  │
  └── 8. MainWindow._on_rename_finished()           ui/main_window.py:375
          │
          ├── Read plan.status for counts
          ├── Display success/overwrite/skip/failed
          ├── Enable undo action
          └── Rescan directory
```

---

## Section 5 — Architecture Boundary

### ExecutionIntegrationService is a **Thin Integration Layer**.

It is **not**:

| Not | Because |
|---|---|
| **Business Service** | Contains zero business logic. Does not apply RenamePolicy, validate filenames, detect conflicts, or manage history. |
| **Rule Engine** | Does not compute rule steps. Rule application is delegated to `ExecutionPipeline` → `RenameExecutionEngine` → `RuleEngine`. |
| **Planning Engine** | Does not generate `RenamePlan`. All plans come from `RenamePlanEngine.generate()`. |

### Classification (A/B/C)

| Class | Definition | Evidence in `ExecutionIntegrationService` |
|---|---|---|
| **A** — Pure Call Adapter | Wraps existing API calls with no transformation | `ExecutionPipeline.run(ctx, engine)`, `RollbackPlugin.record_rename()` |
| **B** — Type/Result Conversion | Converts between data models | `operations_journal` dict → `RenameResult`, `operations_journal` → `plan.status` |
| **C** — Existing Capability Reuse | Delegates to existing public API | `EngineRegistry.default()`, `ExecutionContext`, `OperationLogger` |

### Frozen Modules (untouched)

```
engine/execution_context.py       — CLEAN
engine/execution_pipeline.py      — CLEAN
engine/execution_trace.py         — CLEAN
engine/execution_metrics.py       — CLEAN
engine/engine_registry.py         — CLEAN
engine/execution_engine.py        — CLEAN
engine/rename_plan_builder.py     — CLEAN
engine/rename_execution_engine.py — CLEAN
plugins/rollback_plugin.py        — CLEAN
plugins/plugin_framework.py       — CLEAN
engine/rename_plan_engine.py      — CLEAN
```

---

_Last updated: 2026-08-01 — M12 Integration Closure, Stage 1_
