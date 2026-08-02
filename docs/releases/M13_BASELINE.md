# M13 Baseline Manifest

## Identity

| Field | Value |
|---|---|
| Milestone | M13 — Workspace Foundation |
| Branch | `m11-execution-platform` |
| Parent commit | `be7ab0f` (M12 Integration Milestone) |
| Baseline commit | `9ed6a8f` (this commit) |
| Intended freeze tag | `M13-complete` (placeholder — tag not yet created) |
| Date | 2026-08-01 |

## Product Baseline

M13 establishes the RuleForge Workspace — a task-first, multi-application
product shell.  All existing rename functionality is preserved unchanged.

| Capability | Maturity |
|---|---|
| Workspace Shell | Complete — `WorkspaceWindow` as primary entry point; sidebar + content layout |
| Workspace Navigation | Complete — `_NavItem` custom widget; wild-card switching via `_activate_app()` |
| Task-First Entry | Complete — `WorkspaceHome` landing page; 4 task cards mapping to ResourceHub |
| Application Framework | Foundation — `WorkspaceApp` frozen dataclass; `AppStatus`; static `_APP_REGISTRY` |
| ResourceHub | Complete (unchanged) — embedded as "resourcehub" application |
| History | Basic — table view with Refresh/Export/Clear; shares `OperationLogger` |
| Rule Studio | Foundation — "Open Rule Manager" via public API; planned features as placeholders |
| Workflow | Foundation — product surface only; no execution/scheduling/orchestration |
| Session Persistence | Complete — QSettings-based; 3 lightweight keys |
| Continue Last Session | Complete — restores last active application on startup |
| Actionable Recent Tasks | Complete — clickable recents on home page; navigate to ResourceHub |

## Architecture Baseline

### Workspace Boundary
- `WorkspaceWindow` owns the application container (`QStackedWidget`), navigation,
  session persistence, and task routing.
- Applications (`MainWindow`, `HistoryApp`, `RuleStudioApp`, `WorkflowApp`)
  own their respective business logic.
- Cross-application interaction: public Signals + public methods only.
  No private-member access across component boundaries.

### Runtime Boundary
- **11 Runtime files unchanged from M12 baseline**:
  `ExecutionPipeline`, `RenameExecutionEngine`, `ExecutionContext`,
  `EngineRegistry`, `ExecutionTrace`, `ExecutionMetrics`,
  `RenamePlanEngine`, `RollbackPlugin`, `PluginFramework`,
  `ExecutionIntegrationService`, `OperationLogger`.
- Workspace state (QSettings) isolated from Runtime state (in-memory).
- No execution pipeline serialization.  No background job persistence.

### Public Interaction Model
- `RuleStudioApp.open_rule_manager_requested` (Signal) → `MainWindow.open_rule_manager()` (public method)
- `WorkspaceHome.task_selected` (Signal) → `WorkspaceWindow._on_task_selected()` → `_activate_app("resourcehub")`
- `HistoryApp` receives `OperationLogger` reference at construction time (shared service)

### MainWindow Boundary
- `MainWindow` is preserved unchanged except for one public method addition:
  `open_rule_manager()` delegates to existing `_on_rule_manage()`.
- All M12 rename workflow code (scan, rule config, preview, execute, rollback)
  is untouched.

## Runtime Status

**Verified.**  Eleven Runtime files have zero diff vs M12 baseline:
`ExecutionPipeline`, `RenameExecutionEngine`, `ExecutionContext`,
`EngineRegistry`, `ExecutionTrace`, `ExecutionMetrics`,
`RenamePlanEngine`, `RollbackPlugin`, `PluginFramework`,
`ExecutionIntegrationService`, `OperationLogger`.
All 1131 non-UI tests pass (1 pre-existing flaky failure: `test_date_does_stat`).

## Known Technical Debt

### Baseline Technical Debt

| Item | Impact | Notes |
|---|---|---|
| History logger coupling | Low | `HistoryApp` accesses `_resourcehub._logger` (private attr).  `OperationLogger` is a service, not an implementation detail — acceptable. |
| Pre-existing formatting diffs (68 files) | Low | Equal insertions/deletions in engine/, plugins/, tests/, docs/ — no semantic changes. Should be committed separately. |
| No M13-specific automated tests | Low | All M13 code is presentation-layer PySide6 widgets requiring display server. Indirectly verified via M12 test suite. |

### Future Enhancement (M14+)

| Item | Target |
|---|---|
| Plugin Architecture | M14 |
| Dynamic Application Discovery | M14 |
| Application Lifecycle Framework | M14 |
| Extension Point System | M14 |
| Capability API | M14 |
| Workflow Execution Engine | M14+ |
| Rule Studio testing/validation/sharing capabilities | M14+ |

## Parent / Successor

- **Parent**: M12 Integration Milestone (`M12-complete`, 1134 tests)
- **Successor**: M14 Workspace Platform

---

*This manifest is the permanent baseline record for M13.  It was produced
during the Baseline Materialization task (2026-08-01) and reflects the
repository state at the time of materialization.*
