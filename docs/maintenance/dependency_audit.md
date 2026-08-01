# Dependency Audit

_M12 Frozen Baseline — Maintenance Mode_

> **Purpose**: Document current dependents of legacy modules.  This is an
> audit, not a migration plan.  No import modifications or refactoring is
> proposed.
>
> See [`docs/contracts/execution_integration.md`](../contracts/execution_integration.md)
> for the normative contract governing the active execution path.

---

## 1. RenameEngine

**File**: `engine/rename_engine.py`
**Status**: Deprecated Candidate (see [Legacy Inventory](legacy_inventory.md))

### Current Dependents

#### Production (0)

None.  `RenameEngine` is no longer imported or called by any production code.

#### Test (9 files)

| Test File | Import |
|---|---|
| `tests/test_rename_engine.py` | `from engine.rename_engine import RenameEngine` |
| `tests/test_rename_e2e.py` | `from engine.rename_engine import RenameEngine` |
| `tests/test_rename_policy.py` | `from engine.rename_engine import RenameEngine` |
| `tests/test_multi_select.py` | `from engine.rename_engine import RenameEngine` |
| `tests/test_operation_logger.py` | `from engine.rename_engine import RenameEngine` |
| `tests/test_undo_engine.py` | `from engine.rename_engine import RenameEngine` |
| `tests/test_undo_ui.py` | `from engine.rename_engine import RenameEngine` |
| `tests/test_rule_engine_ext.py` | `from engine.rename_engine import RenameEngine` |
| `tests/test_scan_worker.py` | `from engine.rename_engine import RenameEngine` |

#### Legacy Bridge (1)

| File | Import |
|---|---|
| `workers/rename_worker.py` | `from engine.rename_engine import RenameEngine` |

`RenameWorker` is itself a Deprecated Candidate.

### Current Purpose

Was the primary rename execution engine (M2-M10).  Replaced by
`RenameExecutionEngine` via `ExecutionPipeline.run()`.

### Migration Status

**Complete.**  Production path (`MainWindow._on_rename()`) no longer
calls `RenameEngine`.  Tests still exercise it for legacy behavior
verification.

---

## 2. UndoEngine

**File**: `engine/undo_engine.py`
**Status**: Deprecated Candidate (see [Legacy Inventory](legacy_inventory.md))

### Current Dependents

#### Production (0)

None.  `UndoEngine` is no longer imported or called by any production code.
`MainWindow._on_undo()` now uses `RollbackPlugin.rollback()` via
`ExecutionIntegrationService`.

#### Test (4 files)

| Test File | Import |
|---|---|
| `tests/test_undo_engine.py` | `from engine.undo_engine import UndoEngine` |
| `tests/test_undo_ui.py` | `from engine.undo_engine import UndoEngine` |
| `tests/test_multi_select.py` | `from engine.undo_engine import UndoEngine` |
| `tests/test_rename_e2e.py` | `from engine.undo_engine import UndoEngine` |

### Current Purpose

Was the primary undo mechanism (M2-M10).  Replaced by `RollbackPlugin`.

### Migration Status

**Complete.**  Production path (`MainWindow._on_undo()`) no longer
calls `UndoEngine`.  Tests still exercise it for legacy behavior
verification.

---

## 3. RenameWorker

**File**: `workers/rename_worker.py`
**Status**: Deprecated Candidate (see [Legacy Inventory](legacy_inventory.md))

### Current Dependents

#### Production (0)

None.  `RenameWorker` is no longer used in `MainWindow`.
`MainWindow._on_rename()` now uses `ExecutionWorker`.

#### Test (4 files)

| Test File | Import |
|---|---|
| `tests/test_rename_worker.py` | `from workers.rename_worker import RenameWorker` |
| `tests/test_progress_signal.py` | `from workers.rename_worker import RenameWorker` |
| `tests/test_scan_worker.py` | `from workers.rename_worker import RenameWorker` |
| `tests/test_execution_integration.py` | `from workers.rename_worker import RenameWorker` (contract comparison) |

#### Imports RenameEngine

`RenameWorker` imports and calls `RenameEngine.rename()` — it is a
transitive legacy dependency chain: `RenameWorker` → `RenameEngine`.

### Current Purpose

Was the QThread wrapper for `RenameEngine`.  Replaced by `ExecutionWorker`
which wraps `ExecutionIntegrationService` → `ExecutionPipeline`.

### Migration Status

**Complete.**  Production path uses `ExecutionWorker`.

---

## 4. OperationLogger

**File**: `engine/operation_logger.py`
**Status**: Active (see [Legacy Inventory](legacy_inventory.md))

### Current Dependents

#### Production (4 files)

| File | Usage |
|---|---|
| `ui/main_window.py` | `self._logger = OperationLogger()` — passed to ExecutionWorker and OperationLogDialog |
| `ui/operation_log_dialog.py` | `OperationLogDialog(logger)` — displays `logger.records()` |
| `workers/execution_worker.py` | `self._logger.record(rr)` — records each RenameResult |
| `workers/rename_worker.py` | `logger=self._logger` — legacy path, still calls `logger.record()` |

#### Legacy Production (2 files)

| File | Usage |
|---|---|
| `engine/rename_engine.py` | Optional logger parameter in `rename()` |
| `engine/undo_engine.py` | `UndoEngine.undo(logger)` — reads and clears logger |

#### Test (3 files)

| Test File | Usage |
|---|---|
| `tests/test_operation_logger.py` | Tests OperationLogger directly |
| `tests/test_export_log.py` | Tests CSV/TXT export via OperationLogDialog |
| `tests/test_operation_log_dialog.py` | Tests OperationLogDialog UI |

### Current Purpose

Cross-run operation history for:
- `OperationLogDialog` display (read-only table view + CSV/TXT export)
- Undo data source (legacy path via `UndoEngine`; new path via `RollbackPlugin`)

### Migration Status

**Not migrated.**  `OperationLogger` remains the active history store.
`ExecutionTrace` is per-run (not cumulative), so `OperationLogger` is
still needed for cross-run log display.  The new `ExecutionWorker`
populates it alongside the new execution path.

---

## Summary

| Legacy Module | Prod Refs | Test Refs | Migration |
|---|---|---|---|
| `RenameEngine` | 0 | 9 | Complete |
| `UndoEngine` | 0 | 4 | Complete |
| `RenameWorker` | 0 | 4 | Complete |
| `OperationLogger` | 4 | 3 | Not migrated (still active) |
