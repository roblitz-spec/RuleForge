# Independent Architecture Audit — M4 Frozen Baseline

**Audit Date:** 2026-07-29
**Audited Baseline:** M4-complete (commit `344b596`)
**Regression:** 315 / 315 PASS
**Auditor:** Independent Architecture Audit

---

## 1. Executive Summary

The M4 baseline architecture is **internally consistent and well-structured at the module level**. The EditSession → WorkingCopy → Commit → Repository pipeline correctly enforces the Single Commit Path principle for step-level edits. The Repository cleanly owns only committed domain state, and Preview is genuinely read-only.

However, the audit identifies **one architectural boundary violation** (the pinned toggle bypasses EditSession.commit()), **one dead component** (SessionStore has zero integration points), and **one ownership ambiguity** (name/description edits are partially committed and partially direct WorkingCopy mutation). These are architectural integrity concerns, not cosmetic issues.

Additionally, the architecture diagram presented in the review brief does not accurately represent the actual module topology — there are two distinct undo systems (EditSession undo/redo for rule editing and UndoEngine for file rename reversal), and the architectural level at which certain components sit differs from the diagram.

**Overall Decision: PASS WITH MAJOR FINDINGS**

---

## 2. Architecture Strengths

The following architectural decisions are sound and should remain unchanged:

### 2.1 Single Commit Path (Principle 1)
`EditSession.commit()` is correctly the sole path by which step-level WorkingCopy changes are applied to the original Rule. All three mutation triggers — Manual Save (`_on_save`), Auto Save (`_on_auto_save`), and Session Restore — route through `commit()` or `auto_commit()`. The `auto_commit()` method explicitly delegates to `commit()`, preserving the invariant. This is the architecture's strongest structural guarantee.

### 2.2 Repository Responsibility (Principle 3)
`RuleRepository` correctly owns only committed domain state — it stores, loads, saves, and queries `Rule` objects. It has no reference to `WorkingCopy`, `EditSession`, `UndoEngine`, `SessionStore`, or any UI component. The separation is clean and the boundary is well-defined.

### 2.3 Preview Read-Only (Principle 6)
`PreviewEngine.generate_preview()` is a pure read-only operation — it iterates `FileItem` objects and writes only the `preview_name` field. It never mutates `Rule`, `Repository`, or any domain state. The integration in `MainWindow._refresh_preview()` correctly reads the `current_working_copy` from the `RuleManagerDialog` when a session is active, falling back to the repository Rule otherwise. This is correctly implemented.

### 2.4 WorkingCopy Isolation
`EditSession.open()` creates a `deepcopy` of the original Rule, and all mutations through `update_param()` operate on the WorkingCopy only. The test suite confirms that the original Rule is never mutated by editing operations, undo, redo, discard, or preview reads. This isolation is robust and well-tested.

### 2.5 RuleEngine Pure Function Contract (ADR-004)
The RuleEngine remains a stateless pure function, receiving all context (`index`, `metadata`) through the `context` dictionary. The `RuleAnalysis` pre-pass correctly declares which context resources are needed so that `PreviewEngine` can construct context only when necessary. This design supports thread safety, testability, and future Rule types without architectural change.

### 2.6 Single Source of Truth — Dirty State (Principle 2)
`EditSession.is_dirty()` is the single source of truth for dirty state. The Unsaved Changes Warning (`_maybe_discard_changes`) is a read-only consumer that reads `is_dirty()` and never writes to it. The warning correctly offers Save/Discard/Cancel and does not mutate WorkingCopy, Repository, or domain state.

### 2.7 Dependency Direction
The dependency graph flows cleanly in one direction: UI → EditSession → Repository. There are no circular dependencies. `PreviewEngine` reads from the EditSession's WorkingCopy without creating a dependency cycle. `SessionStore` and `SerializableSession` are downstream of `EditSession` and have no reverse dependencies.

---

## 3. Architecture Boundary Review

### 3.1 UI → EditSession Boundary
**Clean.** The `RuleManagerDialog` creates an `EditSession`, opens it with a Rule from the Repository, and routes all step parameter changes through `session.update_param()`. The `current_working_copy` property exposes the WorkingCopy for Preview consumption without leaking mutation capability.

### 3.2 EditSession → WorkingCopy Boundary
**Clean.** WorkingCopy is a private field (`_working_copy`). External access is through the read-only `rule` property. Mutation is only through `update_param()`, `commit()`, `discard()`, `undo()`, `redo()`, and `auto_commit()`.

### 3.3 EditSession → Repository Boundary
**Clean.** EditSession has no reference to Repository. It operates on Rule objects passed to it and applies mutations through `commit()` to the original Rule in-place. The caller (UI) is responsible for calling `repo.save()` after `commit()`.

### 3.4 SessionStore Boundary
**Architecturally orphaned.** `SessionStore` and `SerializableSession` are fully implemented and covered by the architecture contract, but `SessionStore` is never imported or instantiated anywhere in the codebase. There is no session save/restore integration. This component is designed but not wired — it exists in the architecture on paper only.

### 3.5 Preview Boundary
**Clean.** `PreviewEngine` is a static method that accepts `items: list[FileItem]` and `rule: Rule` and writes `preview_name` on each item. It is called from `MainWindow._refresh_preview()` and from `ScanWorker.run()`. It does not access Repository, EditSession internals, or the filesystem (metadata comes from `MetadataProvider` via context).

---

## 4. Ownership Review

| Component | Owner | Assessment |
|---|---|---|
| WorkingCopy | EditSession (`_working_copy`) | **Correct** |
| Dirty State | EditSession (`_dirty`, `is_dirty()`) | **Correct** |
| Commit | EditSession (`commit()`, `auto_commit()`) | **Correct for steps; partial for name/description** |
| Repository | `RuleRepository` | **Correct** — committed domain state only |
| SessionStore | `SessionStore` class | **Correctly scoped but not integrated** |
| Preview | `PreviewEngine` | **Correct** — read-only |
| Auto Save | `RuleManagerDialog` (`_on_auto_save`) | **Acceptable but has ownership ambiguity** |
| Warning Policy | `RuleManagerDialog` (`_maybe_discard_changes`) | **Correct** — read-only projection of `is_dirty()` |

### 4.1 Auto Save Ownership Ambiguity
`_on_auto_save()` (line 714-732) performs two distinct operations:
1. Direct WorkingCopy mutation: `self._current_rule.name = ...` and `self._current_rule.description = ...`
2. Session commit: `self._session.auto_commit()`

The name/description mutation bypasses `update_param()` — it writes directly to the WorkingCopy before invoking `auto_commit()`. This means name/description changes are not tracked in the undo/redo history and do not contribute to the dirty flag through the normal `update_param` path. The dirty flag is only set if there were prior `update_param` calls. If the user changes only the rule name, the session will NOT be marked dirty, and auto-save will skip the change entirely.

This is an **ownership ambiguity**: name/description edits are partially owned by the UI dialog (direct mutation) and partially owned by the session (commit of steps). The audit brief identifies `_on_auto_save` as an architectural component; the ambiguity is that it straddles two ownership domains.

---

## 5. Commit Boundary Review

### 5.1 Step-Level Mutations
**Preserved.** All step parameter changes route through `update_param()` → `commit()` (or `auto_commit()`). Manual Save, Auto Save, and Session Restore all preserve this path for step-level changes.

### 5.2 Name/Description Mutations
**Partially preserved.** In `_on_save()` (line 772-773), name and description are written directly to `self._current_rule` (the WorkingCopy) before `commit()` is called. The `commit()` method does correctly copy `wc.name` and `wc.description` to the original Rule (lines 144-145). So the Commit boundary is preserved for the *original* Rule, but the *mutation path* for name/description bypasses `update_param()` — meaning these changes are invisible to undo/redo and dirty tracking.

### 5.3 Pinned Toggle Violation
**Boundary violation.** The context menu handler `_on_rule_context_menu` (lines 284-312) directly mutates `rule.pinned` on the Repository object and calls `self._repo.save()` without going through `EditSession.commit()`. This is a direct violation of the Single Commit Path principle. The pinned toggle is a Rule mutation that circumvents the Commit boundary entirely.

This is the only path that mutates a Rule in the Repository without involving EditSession. It is architecturally significant because:
- It creates an undocumented second mutation path
- If an EditSession is active for the same Rule, the pinned change will be overwritten on the next session commit (since the WorkingCopy is unaware of the external mutation)
- It sets a precedent for future bypass paths

### 5.4 Session Restore
**Preserved.** `EditSession.restore_from()` creates a new session with a deep-copied WorkingCopy. It never mutates the original Rule. The restored session's `commit()` will apply changes through the normal path. This is correctly implemented.

---

## 6. Repository Review

### 6.1 Responsibility Confirmation
`RuleRepository` correctly owns:
- In-memory `Rule` list
- `JsonStorage` persistence layer
- CRUD operations (`add`, `update`, `remove`, `find`, `all_rules`)
- `load()` and `save()` file I/O

### 6.2 Responsibility Boundary
`RuleRepository` does NOT own:
- WorkingCopy ✓
- Dirty State ✓
- Session Persistence ✓
- Undo History ✓
- UI state ✓ (QSettings is managed by the `Settings` class)

### 6.3 Direct Mutation Concern
The `_repo.save()` call in the pinned toggle handler (`_on_rule_context_menu`) writes a mutation to disk that did not go through the Commit boundary. While the Repository itself is not at fault (it simply persists what it's told), the architectural concern is that a UI handler has direct write access to the Repository for domain state mutation, creating a second mutation path alongside `EditSession.commit()`.

Similarly, `_on_add_rule` and `_on_delete_rule` go directly to `_repo.add()` / `_repo.remove()` / `_repo.save()` without going through an EditSession. This is acceptable for **structural** operations (add/delete rules) since there is no EditSession in play, but it creates two classes of mutation paths for the same repository.

---

## 7. Session Persistence Review

### 7.1 SerializableSession
**Correctly designed.** `SerializableSession` is a pure data holder with `working_copy: Rule` and `is_dirty: bool`. It explicitly excludes undo/redo history per the documented Option A policy. The decision to start restored sessions with clean history is a sound, intentional architectural choice.

### 7.2 SessionStore Implementation
**Correctly implemented.** `SessionStore` provides `save()`, `load()`, and `remove()` methods. Serialization is clean — it converts the WorkingCopy to a JSON-compatible dict without leaking internal EditSession state. The serialization functions (`_serialize`, `_deserialize`) are pure and separate from the store logic.

### 7.3 Integration Gap
**SessionStore is not integrated.** There is no import of `SessionStore` anywhere in the codebase. The session persistence layer is architecturally complete (design + implementation + tests for the data model) but has no runtime integration. The following are missing:
- No call to `SessionStore.save()` on app close or session close
- No call to `SessionStore.load()` on app startup or rule selection
- No session lifecycle management that invokes the store

This is a component that exists architecturally but does not contribute to the running system. It is not a boundary violation, but it is a gap between the architecture as documented and the architecture as implemented.

### 7.4 Restoration Invariants
The `restore_from()` method correctly:
- Creates a new ACTIVE session ✓
- Restores the WorkingCopy as the editing source of truth ✓
- Does NOT mutate the Domain Rule ✓
- Does NOT bypass commit() ✓
- Starts with clean undo/redo history ✓ (Option A)

---

## 8. Extensibility Assessment

### 8.1 Performance Optimization
**Low risk.** The clean separation between Scanner, PreviewEngine, RenamePlanEngine, and RenameEngine means each stage can be optimized independently. The ScanWorker already runs scanning + preview in a background thread, and RenameWorker runs rename in a separate thread. Adding parallel preview or batched rename would not require architectural changes.

### 8.2 Preview Optimization
**Low risk.** `PreviewEngine.generate_preview()` is a stateless function. `RuleAnalysis` already pre-computes context requirements to avoid unnecessary `MetadataProvider` construction. The Preview can be further optimized (e.g., incremental preview on single-rule changes) without touching the RuleEngine or Repository.

### 8.3 Diagnostics
**Low risk.** The `OperationLogger` pattern (in-memory records, queryable, clearable) is extensible. Adding structured logging levels, export formats, or trace context would not require architectural changes.

### 8.4 Multi-Session Editing
**Moderate risk.** EditSession is designed for single-rule editing. Multi-session editing (editing multiple rules concurrently) would require either multiple `EditSession` instances managed by a session registry, or extending EditSession to support multiple WorkingCopies. The current design supports multiple sessions (each is a standalone object), but the `RuleManagerDialog` assumes a single `_session` reference. This is solvable without architectural redesign but would require changes to the UI integration layer.

### 8.5 Plugin Extension Points
**Moderate risk.** Adding new RuleStep types follows a well-defined pattern: register a handler in `_HANDLERS`, add UI in `_STEP_TYPES` and `_STEP_DEFAULTS`, and add a parameter page. This is a clean extension point. However, there are no formal extension points for other subsystems (custom Preview filters, custom rename validators, custom storage backends). These would require architectural additions.

---

## 9. Architecture Debt

### 9.1 DEBT-01: Pinned Toggle Bypasses Commit Boundary (Major)
The context menu pin/unpin handler directly mutates `rule.pinned` on the Repository object and calls `repo.save()` without going through EditSession. This creates a second domain mutation path. See Finding F-001.

### 9.2 DEBT-02: SessionStore Zero Integration (Major)
The `SessionStore` component is architected, implemented, and tested but is never instantiated or called at runtime. This is dead architecture — it exists on paper and in code but not in the running system. The architecture document claims "SessionStore owns ONLY EditSession persistence" but no ownership is exercised at runtime. See Finding F-002.

### 9.3 DEBT-03: Name/Description Mutation Path Ambiguity (Minor)
Name and description changes are written directly to the WorkingCopy (`self._current_rule.name = ...`) rather than through `update_param()`. This means these edits are invisible to undo/redo and do not independently trigger dirty state. The `commit()` method does copy them to the original Rule, so the Commit boundary is preserved for the original — but the editing path is inconsistent with step-level changes. See Finding F-003.

### 9.4 DEBT-04: Architecture Diagram Inaccuracy (Informational)
The architecture diagram in the review brief shows Undo/Redo as a node between WorkingCopy and Preview. The actual architecture has two distinct undo systems:
- **EditSession undo/redo**: Snapshot-based, operates on WorkingCopy within EditSession, applies to rule editing
- **UndoEngine**: Single-level, operates on `OperationLogger` records, applies to file rename operations

The diagram does not distinguish between these, which could cause confusion for new contributors. See Finding F-004.

### 9.5 DEBT-05: RuleManagerDialog Has Dual Persistence Responsibility (Minor)
The `RuleManagerDialog` is responsible for both session management (create, edit, commit, discard) and repository persistence (save, add, delete). While the dialog is the natural orchestration point, it means the UI layer has direct write access to the Repository for domain mutations (add/delete/pin) that could bypass the session entirely. A cleaner separation would route all domain mutations through a single coordinator. See Finding F-005.

---

## 10. ADR Assessment

### 10.1 Existing ADRs
The project has thorough ADR documentation in `docs/AI/DECISION_LOG.md`:
- **ADR-001**: Prefix/Suffix Design (Accepted)
- **ADR-002**: Undo Design (single-level, Accepted)
- **ADR-003**: Feature Freeze Policy (Accepted)
- **ADR-004**: RuleEngine Pure Function Contract (Accepted)
- **ADR-005**: Context Contract (Accepted)
- **ADR-006**: Avoid Path.resolve() in Scanner Hot Path (Accepted)

All existing ADRs are well-documented with context, alternatives considered, and trade-offs.

### 10.2 ADR Recommendation

**Minor ADR Suggested: Session Persistence Strategy (WP-12 Option A)**

The decision to not restore undo/redo history (Option A in the audit brief) is architecturally significant and has already been implemented in `restore_from()`. However, it is not documented as an ADR. The decision has these long-term implications:
- Any future feature that requires undo persistence across sessions would need to change the `SerializableSession` schema
- The choice between Option A (clean history) and other options (partial or full history restoration) affects user experience expectations
- It exceeds implementation detail because it defines the session restore contract

**Recommendation:** Document the Option A decision as ADR-007 with the rationale (simplicity, clean restore semantics, no user demand for history persistence).

### 10.3 No Other ADRs Required
The remaining architectural decisions — WorkingCopy isolation, single Commit path, Repository scope — are either inherent to the design and self-evident from the code, or already documented in AGENTS.md and the architecture document.

---

## 11. Risk Assessment

| Risk Area | Level | Assessment |
|---|---|---|
| Architecture Drift | **Low** | The architecture has remained stable across milestones; ADRs, AGENTS.md, and test suite provide strong grounding |
| Boundary Violations | **Medium** | The pinned toggle bypass creates a real boundary violation; otherwise boundaries are clean |
| Ownership Ambiguity | **Medium** | Name/description editing and auto-save have ambiguous ownership between UI and session |
| Session Lifecycle | **Medium** | SessionStore exists but is not integrated; session persistence is an architectural claim not realized at runtime |
| Maintainability | **Low** | Module boundaries are clean; new RuleStep types follow a standard pattern; test coverage is comprehensive |
| Scalability | **Low** | ScanWorker and RenameWorker separate I/O from UI thread; RuleEngine is stateless; Preview can be parallelized |
| Long-Term Evolution | **Low-Medium** | Multi-session editing and plugin extension points are the main areas requiring architectural additions; current design does not block them |

---

## 12. Findings

### Finding F-001: Pinned Toggle Bypasses EditSession Commit Boundary

| Field | Detail |
|---|---|
| **Finding ID** | F-001 |
| **Severity** | Major |
| **Affected Component** | `RuleManagerDialog._on_rule_context_menu` |
| **Description** | The pin/unpin context menu handler directly mutates `rule.pinned` on the Repository object and calls `repo.save()`, bypassing EditSession.commit() entirely. If an EditSession is active for the same Rule, the session's WorkingCopy is unaware of the external pinned mutation. |
| **Impact** | Creates an undocumented second mutation path for domain state, violating Principle 1 (Single Commit Path). On the next session commit for the same rule, the pinned state from the context menu will be overwritten by the WorkingCopy's pinned value, potentially causing data loss. |
| **Suggested Action** | Route pinned changes through the EditSession when one is active, or at minimum sync the WorkingCopy's pinned state from the Repository after external mutations. Consider making `pinned` an `update_param`-tracked property so it participates in undo/redo and dirty tracking. |

### Finding F-002: SessionStore Is Not Integrated at Runtime

| Field | Detail |
|---|---|
| **Finding ID** | F-002 |
| **Severity** | Major |
| **Affected Component** | `storage/session_store.py`, system integration layer |
| **Description** | `SessionStore` and `SerializableSession` are fully implemented and tested, but `SessionStore` is never imported, instantiated, or called anywhere in the codebase. Session persistence — a key architectural component in the audit brief — does not function at runtime. |
| **Impact** | The architecture claims "SessionStore owns ONLY EditSession persistence" but no ownership is exercised. If the app crashes or the user closes the dialog, unsaved editing state is lost. The architecture is correct on paper but incomplete in execution. |
| **Suggested Action** | Integrate `SessionStore` into the application lifecycle: (1) save session state on dialog close; (2) save session state periodically (alongside or instead of auto-save); (3) restore session state on app startup or rule selection. Determine whether session persistence should replace or complement the current auto-save-to-Repository approach. |

### Finding F-003: Name/Description Edits Bypass update_param() Tracking

| Field | Detail |
|---|---|
| **Finding ID** | F-003 |
| **Severity** | Minor |
| **Affected Component** | `RuleManagerDialog._on_auto_save`, `RuleManagerDialog._on_save` |
| **Description** | Name and description are written directly to the WorkingCopy (`self._current_rule.name = ...`) rather than through `session.update_param()`. This means these edits are invisible to undo/redo history and do not independently trigger the dirty flag. If a user changes only the rule name without touching any step parameters, the session will not be marked dirty. |
| **Impact** | (1) Name-only changes may be lost if the user navigates away without an explicit save (the unsaved changes warning won't fire); (2) name changes cannot be undone/redone; (3) the editing model is inconsistent — steps use update_param, name/description use direct mutation. |
| **Suggested Action** | Either (A) extend `update_param` or add an `update_metadata` method for name/description changes so they participate in dirty tracking and undo/redo, or (B) set the dirty flag explicitly when name/description change and document the inconsistency as intentional. Option A is architecturally cleaner. |

### Finding F-004: Architecture Diagram Does Not Distinguish Two Undo Systems

| Field | Detail |
|---|---|
| **Finding ID** | F-004 |
| **Severity** | Informational |
| **Affected Component** | Architecture documentation |
| **Description** | The architecture diagram shows "Undo/Redo" as a single node between WorkingCopy and Preview. The actual system has two distinct undo mechanisms: (1) EditSession snapshot-based undo/redo for rule editing (operates on WorkingCopy), and (2) UndoEngine for file rename reversal (operates on OperationLogger, entirely separate pipeline). |
| **Impact** | Low — the two systems are independent and do not conflict. However, the diagram is misleading for new contributors who might assume undo/redo applies uniformly. |
| **Suggested Action** | Update the architecture diagram to show: (a) EditSession undo/redo as an internal EditSession mechanism operating on WorkingCopy; (b) UndoEngine as a separate component in the Rename pipeline, downstream of RenameEngine, reading from OperationLogger. |

### Finding F-005: RuleManagerDialog Has Dual Persistence Responsibility

| Field | Detail |
|---|---|
| **Finding ID** | F-005 |
| **Severity** | Minor |
| **Affected Component** | `RuleManagerDialog` |
| **Description** | The `RuleManagerDialog` directly calls `repo.add()`, `repo.remove()`, and `repo.save()` for domain mutations, while simultaneously managing an `EditSession` for step-level editing. This creates two classes of mutation paths: session-mediated (steps, name, description) and direct-repository (add, delete, pin). |
| **Impact** | The dialog has responsibilities spanning both the session layer (editing coordination) and the persistence layer (CRUD on Repository). This is acceptable for a dialog that owns the workflow, but it means the UI component has broader architectural reach than necessary — it's both the editing controller and the persistence controller. |
| **Suggested Action** | Consider introducing a `RuleService` or `RuleCoordinator` layer that wraps both the Repository and Session lifecycle, so the dialog delegates all mutations to a single coordinator. This would consolidate the two mutation paths into one. (This is a Minor recommendation — the current design is functional and the dialog is a natural integration point; the concern is future complexity if more mutation paths are added.) |

---

## 13. Recommendations

### Critical
*None.*

### Major
1. **R-001 (F-001):** Route pinned toggle mutations through EditSession when a session is active. At minimum, sync the WorkingCopy's pinned state from the Repository if the pinned state was changed externally. This closes the Commit boundary bypass.

2. **R-002 (F-002):** Integrate `SessionStore` into the application lifecycle or remove it from the architecture claims. If the architecture states "SessionStore persists EditSession state," the component must be wired in. Either:
   - Integrate: save on dialog close, restore on dialog open/app start
   - Remove: Remove SessionStore from architecture documentation and consider it a future component

### Minor
3. **R-003 (F-003):** Extend `EditSession` with an `update_metadata` method (or extend `update_param`) for name/description changes so they participate in dirty tracking and undo/redo.

4. **R-004 (F-005):** Consider a `RuleCoordinator` abstraction that consolidates mutation paths into one coordinator, separating the dialog's workflow concerns from persistence concerns.

5. **R-005 (ADR):** Document the WP-12 Option A decision (no undo/redo history restoration) as ADR-007.

### Informational
6. **R-006 (F-004):** Update the architecture diagram to accurately represent the two undo systems and their respective positions in the pipeline.

---

## 14. Overall Decision

**PASS WITH MAJOR FINDINGS**

The architecture is fundamentally sound. The core principles — Single Commit Path, WorkingCopy Isolation, Repository Responsibility, Preview Read-Only — are correctly implemented and well-tested. The two Major findings (F-001: pinned toggle Commit bypass, F-002: SessionStore zero integration) are real architectural concerns but are addressable without redesign.

The architecture does not require rework. The recommended changes are targeted fixes that would bring the implementation into full alignment with its own stated architectural principles, without destabilizing the frozen baseline.

---

*End of Architecture Audit*
