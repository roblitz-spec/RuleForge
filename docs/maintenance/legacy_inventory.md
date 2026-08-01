# Legacy Inventory

_M12 Frozen Baseline — Maintenance Mode_

> **Purpose**: Catalog the current status of every module in the execution
> path.  This is an inventory, not a cleanup plan.  No module removal is
> proposed or implied.
>
> See [`docs/architecture/runtime_architecture.md`](../architecture/runtime_architecture.md)
> for the runtime architecture these modules operate within.

## Status Definitions

| Status | Meaning |
|---|---|
| **Active** | In use in the current production path |
| **Primary Runtime** | The authoritative execution entry point (M11/M12 frozen) |
| **Legacy** | Superseded in production but still exists |
| **Deprecated Candidate** | No production references; kept for test compatibility |
| **Transitional** | Bridge between old and new APIs |

## Execution Path Modules

| Module | File | Status | Role | Notes |
|---|---|---|---|---|
| **ExecutionPipeline** | `engine/execution_pipeline.py` | Primary Runtime | Execution orchestration | M11 frozen. Prepare → Execute → Collect → Trace. |
| **RenameExecutionEngine** | `engine/rename_execution_engine.py` | Primary Runtime | Filesystem rename execution | M11 frozen. Replaces `RenameEngine.rename()`. |
| **DryRunExecutionEngine** | `engine/dry_run_execution_engine.py` | Primary Runtime | Dry-run execution | M11 frozen. No filesystem mutation. |
| **ExecutionContext** | `engine/execution_context.py` | Primary Runtime | Immutable execution input | M11 frozen. `rule` + `targets` + `options`. |
| **EngineRegistry** | `engine/engine_registry.py` | Primary Runtime | Engine registration and selection | M11 frozen. `create("rename")` pattern. |
| **ExecutionTrace** | `engine/execution_trace.py` | Primary Runtime | Per-run lifecycle trace | M11 frozen. |
| **ExecutionMetrics** | `engine/execution_metrics.py` | Primary Runtime | Structured statistics | M11 frozen. |
| **ExecutionIntegrationService** | `ui/execution_integration.py` | Active | Integration Layer | Thin adapter. Connects planning → execution. |
| **ExecutionWorker** | `workers/execution_worker.py` | Active | QThread wrapper | Replaces RenameWorker in the production path. |
| **RollbackPlugin** | `plugins/rollback_plugin.py` | Primary Runtime | Unified rollback | M12-D frozen. Replaces UndoEngine. |

## Planning & Support Modules

| Module | File | Status | Role | Notes |
|---|---|---|---|---|
| **RenamePlanEngine** | `engine/rename_plan_engine.py` | Active | Planning SSOT | Sole source of RenamePlan, RenamePolicy, validation, conflict detection. |
| **PreviewEngine** | `engine/engine/preview_engine.py` | Active | Preview generation | Generates preview_name for GUI display. |
| **RuleEngine** | `engine/rule_engine.py` | Active | Rule step application | Pure function. Called by PreviewEngine and via ExecutionPipeline. |
| **OperationLogger** | `engine/operation_logger.py` | Active | Cross-run operation log | Used by MainWindow, OperationLogDialog, and ExecutionWorker. |
| **Scanner** | `scanner/scanner.py` | Active | Filesystem scanning | Used by ScanWorker. |
| **ScanWorker** | `workers/scan_worker.py` | Active | Background scan thread | Unchanged. |

## Legacy Modules

| Module | File | Status | Role | Notes |
|---|---|---|---|---|
| **RenameEngine** | `engine/rename_engine.py` | Deprecated Candidate | Old rename execution | **0 production references.** Only referenced by tests and by RenameWorker (also legacy). Superseded by RenameExecutionEngine. |
| **UndoEngine** | `engine/undo_engine.py` | Deprecated Candidate | Old undo system | **0 production references.** Only referenced by tests. Superseded by RollbackPlugin. |
| **RenameWorker** | `workers/rename_worker.py` | Deprecated Candidate | Old rename QThread | **0 production references.** Only referenced by tests. Superseded by ExecutionWorker. |

## Plugin Modules (M12-C…K)

All capability plugins are **Primary Runtime** (M12 frozen).
See [`docs/architecture/capability-handbook.md`](../architecture/capability-handbook.md) for the full catalog.

| Module | File | Status |
|---|---|---|
| **RuleValidationPlugin** | `plugins/rule_validation_plugin.py` | Primary Runtime |
| **RollbackPlugin** | `plugins/rollback_plugin.py` | Primary Runtime |
| **SchedulerPlugin** | `plugins/scheduler_plugin.py` | Primary Runtime |
| **RemoteProviderPlugin** | `plugins/remote_provider_plugin.py` | Primary Runtime |
| **WorkflowPlugin** | `plugins/workflow_plugin.py` | Primary Runtime |
| **EventPlugin** | `plugins/event_plugin.py` | Primary Runtime |
| **PolicyPlugin** | `plugins/policy_plugin.py` | Primary Runtime |
| **ValidationPlugin** | `plugins/validation_plugin.py` | Primary Runtime |
| **NotificationPlugin** | `plugins/notification_plugin.py` | Primary Runtime |

## Summary

| Status | Count |
|---|---|
| Primary Runtime | 20 |
| Active | 6 |
| Deprecated Candidate | 3 |
| **Total** | **29** |

No module is in an ambiguous or unknown state.  All 3 "Deprecated Candidate"
modules have zero production references but are retained for test
compatibility.
