# RuleForge — Decision Log (ADR)

## ADR-001: Prefix / Suffix Design

- **Milestone**: M15
- **Status**: Accepted
- **Decision**: Keep `add_prefix` and `add_suffix` as independent RuleStep types.
- **Reason**: Backward compatibility — existing `rules.json` with `add_prefix` must load without migration. Avoids modifying frozen Rule structure post Feature Freeze.
- **Alternatives Considered**: Unify into single Rule with `position` parameter. Rejected due to migration risk.

## ADR-002: Undo Design

- **Milestone**: M15
- **Status**: Accepted
- **Decision**: Maintain single-level Undo only.
- **Reason**: Satisfies current requirements. Multi-level Undo adds session management complexity (stack, redo, history UI) without proven user demand.
- **Alternatives Considered**: Multi-level Undo stack. Deferred to future Milestone.

## ADR-003: Feature Freeze Policy

- **Milestone**: M15 RC
- **Status**: Accepted
- **Decision**: Freeze core pipeline modules (RuleEngine, RenameEngine, PreviewEngine, RenamePlanEngine, FileTableModel) after M15 RC.
- **Reason**: Reduce regression risk. Prioritize release stability over continued iteration.
- **Alternatives Considered**: Allow continuous modification. Rejected — risk of destabilizing 152-test baseline.

## ADR-004: RuleEngine Pure Function Contract

- **Milestone**: M12 (Number Rule design)
- **Status**: Accepted
- **Decision**: RuleEngine handlers must be pure functions. State (like numbering index) is passed via `context` dict from PreviewEngine.
- **Reason**: Testability, predictability, thread safety. Avoids global counters that break between Preview and Rename cycles.
- **Alternatives Considered**: Module-level counters with `reset()`. Rejected — violates stateless principle.

## ADR-005: Context Contract

- **Milestone**: M14 (Date Rule)
- **Status**: Accepted
- **Decision**: Context fields (`index`, `metadata`) are frozen. `metadata` is a `MetadataProvider` with lazy `modified`/`created` properties. New fields can be added but existing ones cannot be renamed or re-typed.
- **Reason**: Rule handlers depend on these fields. Renaming breaks existing Rule configurations.

## ADR-006: Avoid Path.resolve() in Scanner Hot Path

- **Milestone**: M11.1 (NAS Performance Fix)
- **Status**: Accepted
- **Decision**: Scanner hot path must not call `Path.resolve()`, `realpath()`, or any per-entry filesystem stat. Use `Path(entry.path)` directly from `os.scandir()` results.
- **Context**: `os.scandir()` returns `DirEntry` objects with `.path` already being an absolute path. `Path.resolve()` calls `os.path.realpath()` which traverses every path component with `lstat()`. On network filesystems (SMB/NAS), each `lstat()` is one network round trip.
- **Problem**: Scanner on real SMB NAS with 605 directories took **252.524s**. Root cause: `Path(entry.path).resolve()` in `_scan_dir()` triggered 2,420 `lstat()` calls (605 entries × ~4 path components each).
- **Root Cause**: `resolve()` → `realpath()` → `lstat()` per path component → 2,420 network round trips on SMB.
- **Solution**: Remove `Path.resolve()`. Merge `is_dir()` + `is_file()` into single `stat()`. Use `DirEntry.is_dir()` (cached `d_type`).
- **Validation** (real SMB NAS):
  - Scanner: 252.524s → 0.494s (≈511×)
  - Rename: 201 directories ≈10s (normal)
  - Regression: 179 PASS
- **Trade-offs**: Without `resolve()`, symlinked paths are not resolved to their canonical form. The `seen` dedup set may not catch symlinked duplicates. This is acceptable because: (a) directories within a scan are not typically symlinked to each other; (b) the multi-path input case is the primary dedup scenario.
- **Lessons Learned**:
  1. Any directory scanning code must assume it may run on network filesystems.
  2. A single seemingly harmless filesystem API in a hot loop can cause 500× performance degradation.
  3. All future Scanner/Indexer/Rename/Metadata code reviews must include network filesystem performance as a default review item.
  4. Local SSD testing alone is insufficient — network filesystem latency must be considered in design.
- **Alternatives Considered**: Keep `resolve()` but add caching. Rejected — caching adds complexity; `os.scandir()` paths are already absolute.

## ADR-009: Product Direction Convergence

- **Milestone**: M9
- **Status**: Accepted
- **Decision**: Converge on ONE product direction: AI-assisted Rule IDE (recommended name: RuleForge). ResourceHub is the origin and batch file rename is the initial adapter/use case — neither is a competing product direction.
- **Product Hierarchy**:
  - Product: AI-assisted Rule IDE (RuleForge)
  - Core Intelligence: RuleInference Engine (Example → Rule)
  - Core: Rule Engine / Rule Model
  - Development Environment: Rule IDE (`editor/` skeleton exists)
  - Execution: Rule Runtime
  - Initial Adapter: File Rename
- **Roadmap**: M9 RuleInference (✅) → M10 Rule IDE → M11 Rule Runtime → Later: additional adapters
- **Reason**: Single product identity eliminates roadmap ambiguity (UD-01, UD-02, PG-01). The existing `editor/` package (EditSession, DomainValidator, 382 lines) is the Rule IDE skeleton — build on it rather than maintain parallel roadmaps.
- **Alternatives Considered**: Keep "ResourceHub" name with batch rename as primary identity. Rejected — contradicts the evolution already underway (Rule Engine, EditSession, RuleAnalysis, RuleInference).
- **Naming**: Recommended "RuleForge". Mechanical rename deferred to avoid disrupting development.

## ADR-010: Adopt RuleForge as the Official Project Identity

- **Milestone**: M10
- **Status**: Accepted
- **Decision**: Adopt **RuleForge** as the official product and project identity. ResourceHub is the historical origin — preserved as the origin story, not erased.
- **Context**: The project evolved from ResourceHub (batch file renamer) into an AI-assisted Rule IDE. ADR-009 established the product direction; this ADR completes the identity convergence by formalizing the name.
- **Consequences**:
  1. All living documentation uses "RuleForge" as the product name.
  2. Architecture terminology uses RuleForge, Rule, RuleInference, RuleSession, RuleRuntime, Adapters.
  3. Window title: `RuleForge v0.1`.
  4. Configuration: `_ORGANIZATION = "RuleForge"`, `_APPLICATION = "RuleForge"`.
  5. Build artifact: `RuleForge.exe`.
  6. ResourceHub remains in historical documents (PAC reviews, governance assessments, git history, origin story).
  7. PyPI distribution naming is a separate decision — `ruleforge` is occupied on PyPI.
  8. Repository and import namespace not renamed — no functional impact.
- **Validation**: Full regression suite unchanged. No behavioral changes.
- **Alternatives Considered**: Keep "ResourceHub" indefinitely. Rejected — contradicts ADR-009 product direction.

## ADR-011: RuleSession Lifecycle

- **Milestone**: M10.5-B
- **Status**: Accepted
- **Decision**: Introduce `SessionState` (`models/session_state.py`) as the authoritative workflow state model. Every `RuleSession` owns a `SessionState`; `RuleWorkflow` reads it but never writes it directly.
- **Context**: Before ADR-011, `RuleLifecycle` was a conceptual-only enum with no enforcement. `RuleSession` had implicit state transitions buried inside `open()`, `commit()`, and `finalize()`. There was no way to detect invalid operation sequences, and no explicit state for validation or preview phases.
- **SessionState states**: `NEW → INFERRED → EDITING → VALIDATED → PREVIEW_READY → COMMITTED → EXECUTED`
- **Transition rules**:
  - `NEW` only to `INFERRED`
  - `INFERRED` to `EDITING`, `VALIDATED`, `PREVIEW_READY`, or `COMMITTED`
  - `EDITING` to `EDITING`, `VALIDATED`, or `PREVIEW_READY`
  - `VALIDATED` to `EDITING` or `PREVIEW_READY`
  - `PREVIEW_READY` to `EDITING`, `VALIDATED`, or `COMMITTED`
  - `COMMITTED` to `EDITING` or `EXECUTED`
  - `EXECUTED` is terminal
  - Invalid transitions raise `InvalidStateTransition`
- **Consequences**:
  1. `RuleSession` enforces transitions at every operation boundary.
  2. Failed operations do not advance state (e.g., validation failure keeps current state).
  3. `RuleWorkflow` reads `session.state` but delegates state changes to `RuleSession`.
  4. `RuleLifecycle` remains for rule maturity tracking (InferredRuleStore persistence).
  5. Future CLI/SDK/API/GUI must respect `SessionState` — it is the single workflow state authority.
- **Alternatives Considered**: Keep `RuleLifecycle` as the sole state model. Rejected — not granular enough for workflow stages (no VALIDATED, PREVIEW_READY states). Merging session states into RuleLifecycle would break the InferredRuleStore persistence contract.

## ADR-012: Public API Freeze & Compatibility Baseline

- **Milestone**: M10.5-E
- **Status**: Accepted
- **Decision**: Freeze the public Workflow API as the long-term contract for all external integrations. Document public vs internal boundaries explicitly. Adopt backward-compatible evolution policy within 1.x.
- **Context**: RuleForge now has a complete headless Rule IDE workflow (M10.5–M10.5-D). Before adding runtime adapters, SDKs, or GUI workflow integration, the public API surface must be stabilized so all future consumers depend on a well-defined contract rather than internal implementation details.
- **Public API** (frozen):
  1. `RuleWorkflow` — single orchestration entry point (infer, open_session, inspect, execute, run)
  2. `WorkflowResult` — deterministic success/failure with stage-level results
  3. `RuleSession` — mutable state owner (lifecycle enforcement)
  4. `SessionState` — explicit workflow state model
  5. `InvalidStateTransition` — only public exception type
  6. Domain models: `InferredRule`, `Rule`, `RuleStep`, `RuleLifecycle`
  7. Inspection/Preview: `RuleInspection`, `ExamplePreviewResult`, `PreviewEntry`
  8. Inference: `infer_rule()`
  9. CLI: `ruleforge workflow run|infer|execute` (machine-readable JSON for `infer`)
- **Internal API** (may change without notice):
  - `EditSession`, `DomainValidator`, `InferredRuleStore`, `RuleEngine`, `RenameEngine`, `RenamePlanEngine`, `PreviewEngine`, `RuleAnalysis`, `MetadataProvider`, `OperationLogger`, `UndoEngine`, `ui.*`
- **Compatibility policy**:
  1. Public API is backward compatible within 1.x
  2. New capability extends, never replaces
  3. Breaking changes require ADR + migration path
  4. Machine-readable output (infer JSON, exit codes) are compatibility commitments
  5. Human-readable messages (status, help) are not guaranteed stable
  6. Exit codes: `0` = success, `1` = failure; `2`–`127` reserved
- **Consequences**:
  1. CLI verified to use only public API methods
  2. Exception model is explicit (only `InvalidStateTransition` is public)
  3. `docs/AI/API_CONTRACT.md` is the authoritative reference
  4. All future milestones (M11+) must respect this contract
- **Alternatives Considered**: Defer API freeze until after M11 Runtime. Rejected — adding runtime adapters without a stable API contract risks coupling adapters to implementation details. Freeze now, extend later.
