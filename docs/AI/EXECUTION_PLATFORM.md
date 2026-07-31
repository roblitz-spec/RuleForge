# RuleForge Execution Platform — M11 Architecture Baseline

**Status**: M11 Complete — Execution Platform v1  
**Version**: Frozen after M11-E

## Purpose

M11 transforms RuleForge from a simple rule processing tool into a general
execution platform capable of running multiple execution semantics through
a unified architecture.

## Architecture

```
                       RuleWorkflow
                            │   Owns orchestration, accepts user intent
                            ▼
                     EngineRegistry
                            │   Owns engine selection; Pipeline does NOT
                            ▼                     know engine types
                   ExecutionPipeline
                            │   Owns execution lifecycle (validate →
                            ▼   prepare → execute → cleanup)
                    ExecutionEngine
                            │   Owns execution behavior; stateless
                            ▼                     whenever practical
                   ExecutionResult
                                Unified output contract (success,
                                diagnostics, trace, metrics)
```

## Core Components

### RuleWorkflow

| Does | Does NOT |
|---|---|
| Accept user intent | Execute filesystem operations |
| Select execution mode | Implement engine behavior |
| Coordinate workflow execution | Manage engine lifecycle |

### EngineRegistry

| Does | Does NOT |
|---|---|
| Register available engines | Create engines without explicit registration |
| Resolve engine by name | Auto-discover engines (M12+) |
| Create fresh engine instances | Share mutable engine state between calls |

Built-in engines: `"string"`, `"rename"`, `"dry-run"`, `"inspect"`.

### ExecutionPipeline

Lifecycle order (enforced):
```
validate → prepare → execute → cleanup
```

| Does | Does NOT |
|---|---|
| Execute lifecycle | Select engines |
| Maintain execution ordering | Contain engine-specific branches |
| Own execution trace + timing | Inspect engine internals |

### ExecutionEngine

| Engine | Semantics |
|---|---|
| `StringTransformEngine` | Headless string transformation |
| `RenameExecutionEngine` | Filesystem rename (mutating) |
| `DryRunExecutionEngine` | Validation-only (non-mutating) |
| `InspectionExecutionEngine` | Analysis-only (non-mutating) |

### Shared Planning Layer

`RenamePlanBuilder` — used by Rename, DryRun, and Inspection engines.

| Does | Does NOT |
|---|---|
| Validate operations | Mutate filesystem |
| Calculate targets | Control workflow |
| Detect conflicts | Manage result lifecycle |

## Execution Data Contracts

### ExecutionContext
Provides execution input and runtime information.  Owned by execution
lifecycle.

### ExecutionResult
Unified execution output.

```
success         : bool
diagnostics     : dict[str, object]     (backward compat)
trace           : ExecutionTrace | None (M11-E)
metrics         : ExecutionMetrics | None (M11-E)
```

Existing callers remain compatible — new fields are optional and additive.

## Observability Layer

All executions produce:

| Artefact | Content |
|---|---|
| `ExecutionTrace` | execution_id, lifecycle events, timestamps, per-stage duration |
| `ExecutionMetrics` | files_scanned/selected/modified/skipped, conflict_count, error_count, duration_ms |
| `ExecutionDiagnostics` | errors[], warnings[], conflicts[], journal[], metadata{} |

Trace is Pipeline-owned (never Engine-owned).  Diagnostics are engine-agnostic.

## Design Principles (Frozen After M11)

1. **Pipeline executes, Registry selects.** — Pipeline never resolves engines; Registry never executes.
2. **Engines implement behavior, not orchestration.** — Engines own execution semantics, not workflow control.
3. **Planning is separated from execution.** — `build_rename_plan()` validates and detects conflicts; engines execute.
4. **Observability belongs to execution lifecycle.** — Trace is created and populated by Pipeline, not by individual engines.
5. **ExecutionResult is the unified output contract.** — All engines produce the same result type.
6. **New execution modes are Engines, not Pipeline branches.** — Extend via new `ExecutionEngine` implementations, not by modifying `ExecutionPipeline`.

## M11 Completion State

| Phase | Deliverable | Modules | Tests |
|---|---|---|---|
| A | Execution Pipeline | 5 files | 24 |
| B | Rename Execution Engine | 2 files | 13 |
| C | Dry Run & Inspection | 3 files | 15 |
| D | Engine Registry | 1 file | 23 |
| E | Observability & Diagnostics | 3 files | 28 |
| **Total** | **Execution Platform v1** | **14 modules** | **103 tests (743 total)** |

## Next Directions (M12+)

Future extensions should build on the M11 platform without changing core contracts:

- Plugin / Extension Framework
- Undo / Rollback Foundation
- Batch Execution
- Scheduling
- Remote Filesystem Providers

Any future extension must be implemented as a new `ExecutionEngine`, not as
a Pipeline branch.
