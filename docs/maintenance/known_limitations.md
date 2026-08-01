# Known Limitations

_M12 Frozen Baseline — Maintenance Mode_

> **Purpose**: Document current architecture limitations that are the
> result of deliberate M12 scope decisions — not defects or regressions.
>
> These are **scope decisions**, not bugs.  Addressing any of them
> requires a new Major Milestone (M13+).
>
> See [ADR-007](../architecture/adr/007-execution-integration.md) for the
> decision record that established the M12 scope boundary.

---

## Current Architecture Limitations

### 1. GUI is Legacy UI

**Limitation**: The GUI (`ui/main_window.py`) uses the pre-M12
ResourceHub-era UI framework.  It has not been rewritten to a
RuleForge-native IDE or workspace.

**Scope Decision**: M12 focused on Execution Platform integration,
not GUI modernization.  The GUI was intentionally kept as-is.

**Future**: Rule IDE / Workspace → M13+.

### 2. No Rule IDE

**Limitation**: Rules are managed through a basic dialog
(`RuleManagerDialog`).  There is no syntax highlighting, inline
validation, step reordering, or visual rule construction.

**Scope Decision**: M12 did not include a Rule IDE.  The Execution
Platform and Plugin Framework were the priority.

**Future**: Rule IDE → M13+.

### 3. No Workspace

**Limitation**: The application operates on a single directory at a
time.  There is no project/workspace concept for managing multiple
directories, rule sets, or execution configurations.

**Scope Decision**: Out of scope for M12.

**Future**: Workspace → M13+.

### 4. Planning Layer Stays Legacy

**Limitation**: `RenamePlanEngine.generate()` uses pre-M11 APIs for
plan generation, policy resolution, validation, and conflict detection.
The new `build_rename_plan()` in the Execution Platform does not
support RenamePolicy, filename validation, or Windows CI conflict
detection.

**Scope Decision**: Migrating the Planning Layer would require
extracting RenamePolicy, validation, and conflict detection as
standalone public APIs — a refactoring that exceeds Maintenance
boundaries.  The Planning Layer was intentionally kept as-is.

**Future**: RenamePlan Migration → M13+.

### 5. Execution is Migrated (Partial Architecture)

**Limitation**: The execution path is a hybrid:
- **Planning**: Legacy `RenamePlanEngine` (pre-M11)
- **Execution**: New `ExecutionPipeline` + `RenameExecutionEngine` (M11)
- **Rollback**: New `RollbackPlugin` (M12-D)
- **History**: Legacy `OperationLogger` (pre-M11)

This is an intentional transitional architecture — not a defect.
Execution, rollback, and observability are on the new platform;
planning and history remain on legacy APIs pending future milestones.

**Scope Decision**: M12 was Execution Integration, not full
architecture migration.

**Future**: Full migration → M13+.

### 6. No Visual Workflow Designer

**Limitation**: `WorkflowPlugin` exists as a programmatic API but
has no visual designer.  Workflows are defined in code only.

**Scope Decision**: WorkflowPlugin is a capability plugin (M12-G).
Visual tooling is a separate concern.

**Future**: Workflow Designer → M13+.

### 7. OperationLogger Remains Active (Not Migrated to ExecutionTrace)

**Limitation**: `OperationLogger` persists as the cross-run history
store.  `ExecutionTrace` is per-run only.  The `OperationLogDialog`
still reads from `OperationLogger`, and the `ExecutionWorker` still
writes to it.

**Scope Decision**: Cross-run history is a GUI concern, not an
Execution Platform concern.  Replacing `OperationLogger` with a
cumulative trace store was out of scope for M12.

**Future**: History store migration → M13+.

---

## Not Limitations (by Design)

The following are **not** limitations — they are architectural
invariants:

| Item | Why Not a Limitation |
|---|---|
| `ExecutionIntegrationService` is a Thin Layer | By design (ADR-007, Architecture Invariant #2). Business logic belongs in SSOT components, not the Integration Layer. |
| No dual-SSOT for any capability | By design. Each capability has exactly one authoritative source (verified: Section 8 of the Code Evidence Report). |
| `RenamePlanEngine` is the sole Planning SSOT | By design (ADR-007, Architecture Invariant #1). Centralizing planning prevents fragmentation. |
| `ExecutionPipeline` is the only execution entry point | By design (ADR-007, Architecture Invariant #4). Single execution path simplifies debugging and observability. |

---

## Summary

| Category | Count | Resolution Path |
|---|---|---|
| Scope Limitations (M12 deliberate) | 7 | M13+ Major Milestone |
| Architectural Invariants (by design) | 4 | No change expected |
| **Total documented** | **11** | |

All 7 scope limitations are traceable to the ADR-007 "Excluded" list
and the M12 Scope Summary in PROJECT_IDENTITY.md Section 4.2.
