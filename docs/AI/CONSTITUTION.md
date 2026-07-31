# RuleForge — Project Constitution

> **Status**: Active (M10.5-F)
> **Scope**: All modules, all presentation layers, all milestones

This Constitution defines the non-negotiable architectural and
engineering rules for RuleForge.  Every milestone, pull request, and
design decision must be consistent with these principles.

## 1. Architecture

### 1.1 Single Orchestration Entry Point

**RuleWorkflow is the only public orchestration entry point.**

All consumers — CLI, SDK, REST API, GUI, automation — invoke
`RuleWorkflow` to traverse the Rule IDE workflow.  No consumer
may bypass `RuleWorkflow` to manipulate `RuleSession`, `RuleEngine`,
or any other internal component directly.

### 1.2 State Ownership

**RuleSession is the only mutable workflow state owner.**

`RuleWorkflow` reads `session.state` but delegates all state
transitions to `RuleSession`.  No other component may mutate
session state.

### 1.3 Runtime Independence

**Runtime is independent from presentation layers.**

CLI, GUI, SDK, and API layers contain presentation logic only.
Business logic, validation, and execution live inside the engine
layer.  Presentation layers must not duplicate execution paths.

### 1.4 Composition Over Redesign

**Prefer composition over redesign.**

New capability is added by composing existing modules, not by
rewriting them.  If a module's contract is insufficient, extend it
without breaking existing consumers.

## 2. Workflow

### 2.1 Explicit State Transitions

Workflow state transitions must be explicit and validated.

```
NEW → INFERRED → EDITING → VALIDATED → PREVIEW_READY → COMMITTED → EXECUTED
```

Invalid transitions raise `InvalidStateTransition`.  Same-state
transitions are idempotent no-ops.

### 2.2 Failed Operations Do Not Advance State

If a workflow operation fails, `SessionState` must remain unchanged.
The session must be retryable without side effects.

### 2.3 Commit Requires Validation

`RuleSession.commit()` must auto-validate before persisting.
Validation failure rejects the commit — no silent corrupt state.

### 2.4 Terminal States

`EXECUTED` is terminal.  Recovery from terminal states requires an
explicit reset workflow (not yet implemented).  Do not introduce
implicit recovery paths.

## 3. Public API

### 3.1 Compatibility Contract

The public API (defined in `docs/AI/API_CONTRACT.md`) is the
long-term contract for all external consumers.  Backward compatibility
within 1.x is mandatory.

### 3.2 Extension Over Replacement

New functionality extends existing public APIs.  Breaking changes
require:
1. An Architecture Decision Record (ADR)
2. A documented migration path
3. Explicit architectural approval

### 3.3 Public/Internal Boundary

Public API types are documented and stable.  Internal modules
(`EditSession`, `DomainValidator`, stores, UI, batch engines)
may change without notice.  Consumers must not depend on them.

## 4. Engineering

### 4.1 Fail-Fast

Operations must fail immediately on invalid input or invalid state.
Do not silently continue after errors.  Errors must identify the
failed stage and reason.

### 4.2 Regression Immunity

All existing tests must remain green.  New functionality requires
tests.  Test coverage must not be weakened by any change.

### 4.3 Pure Functions Where Possible

Engines (`RuleEngine`, `RuleInference`, `PreviewEngine`) are
stateless pure functions.  State lives in `RuleSession` only.

## 5. CLI

### 5.1 Thin Presentation Layer

CLI invokes `RuleWorkflow` only.  CLI contains no business logic,
no state management, and no validation beyond argument parsing.

### 5.2 Output Contract

- **Machine-readable output** (infer JSON, exit codes) is a
  compatibility commitment.
- **Human-readable messages** (status, help text, formatting)
  may evolve without compatibility guarantees.

### 5.3 Exit Codes

| Code | Meaning |
|---|---|
| `0` | Success |
| `1` | Failure |
| `2`–`127` | Reserved for future workflow categories |

## 6. Documentation

### 6.1 ADRs Required For

- Architecture decisions affecting public API
- Breaking changes
- New module introduction
- Compatibility policy changes
- Deprecation or removal of public API

### 6.2 Living Documents

- `AGENTS.md` — developer quick reference (updated every milestone)
- `API_CONTRACT.md` — public API surface (updated on API changes)
- `DECISION_LOG.md` — ADRs (updated on architecture decisions)
- `CONSTITUTION.md` — this document (updated on governance changes)
- `ARCHITECTURE.md` — system design overview (updated on module changes)

## 7. Version

| Version | Milestone | Changes |
|---|---|---|
| 1.0 | M10.5-F | Initial Constitution |
