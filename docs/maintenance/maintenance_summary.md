# Maintenance Summary

_M12 Frozen Baseline — Maintenance Mode_

> **Purpose**: Summary view of the current maintenance landscape.
> References detailed documents for full context.

---

## Module Status Overview

### Stable (Active + Primary Runtime)

| Layer | Modules |
|---|---|
| **Execution** | `ExecutionPipeline`, `RenameExecutionEngine`, `DryRunExecutionEngine`, `ExecutionContext`, `EngineRegistry`, `ExecutionTrace`, `ExecutionMetrics` |
| **Plugins** | `RollbackPlugin`, `RuleValidationPlugin`, `SchedulerPlugin`, `RemoteProviderPlugin`, `WorkflowPlugin`, `EventPlugin`, `PolicyPlugin`, `ValidationPlugin`, `NotificationPlugin` |
| **Integration** | `ExecutionIntegrationService`, `ExecutionWorker` |
| **Planning** | `RenamePlanEngine`, `PreviewEngine`, `RuleEngine` |
| **Support** | `OperationLogger`, `Scanner`, `ScanWorker` |

### Legacy

| Module | Prod Refs | Notes |
|---|---|---|
| `RenameEngine` | 0 | Superseded by `RenameExecutionEngine` |
| `UndoEngine` | 0 | Superseded by `RollbackPlugin` |
| `RenameWorker` | 0 | Superseded by `ExecutionWorker` |

### Primary Runtime

| Module | Frozen |
|---|---|
| `ExecutionPipeline` | M11 |
| `RenameExecutionEngine` | M11 |
| `RollbackPlugin` | M12-D |
| All 9 Capability Plugins | M12-C…K |
| `PluginRegistry` / `Plugin` ABC | M12-B |

### Future Work

| Item | Requires |
|---|---|
| Rule IDE | M13+ |
| Workspace | M13+ |
| GUI Rewrite | M13+ |
| RenamePlan Migration | M13+ |
| Workflow Designer | M13+ |

All future work items are documented in:
- [ADR-007](../architecture/adr/007-execution-integration.md) — "Future Direction" section
- [PROJECT_IDENTITY.md](../../PROJECT_IDENTITY.md) — Section 4.2 "Scope Summary"
- [Known Limitations](known_limitations.md)

---

## Reference Documents

| Document | Content |
|---|---|
| [Legacy Inventory](legacy_inventory.md) | Full module catalog with status, file paths, and notes |
| [Dependency Audit](dependency_audit.md) | Per-module dependency analysis (production + test references) |
| [Known Limitations](known_limitations.md) | Scope limitations traceable to ADR-007 |
| [Runtime Contract](../contracts/execution_integration.md) | Normative contract for ExecutionIntegrationService |
| [Runtime Architecture](../architecture/runtime_architecture.md) | Runtime execution flow documentation |
| [ADR-007](../architecture/adr/007-execution-integration.md) | Architecture decision record for M12 Execution Integration |
