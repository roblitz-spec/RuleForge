# RuleForge — Engineering Baseline

> **Status**: Active (M10.5-F)
> **Applies to**: All milestones M11+

This document defines the default engineering practices for
RuleForge.  Every milestone is expected to meet these standards
unless an explicit exception is recorded in its ADR.

## 1. Testing

### 1.1 Regression Policy

- The complete regression suite must pass before milestone completion.
- New functionality requires new tests.
- Existing test coverage must not be weakened.
- The known pre-existing failure (`test_date_does_stat`) requires
  explicit acknowledgement when reporting regression results.

### 1.2 Test Categories

| Category | Example | Purpose |
|---|---|---|
| Unit | `test_rule_engine.py` | Individual function/module behavior |
| Integration | `test_m10_phase5.py` | Multi-module interaction |
| E2E | `test_m10_phase5.py` (E2E tests) | Full workflow from entry point |
| Contract | `test_m10_phase5e.py` | Public API behavior stability |
| CLI | `test_m10_phase5b.py` | CLI integration |

### 1.3 Test Design

- Test contracts, not implementation details.
- Prefer real objects over mocks.
- Use `pytest` conventions.
- Tests go in `tests/` with naming `test_m<N>_phase<N>.py` or
  `test_<module>.py`.

## 2. Documentation

### 2.1 Required Updates Per Milestone

| Document | When to Update |
|---|---|
| `AGENTS.md` | Every milestone (git baseline, behavior changes, architecture) |
| `DECISION_LOG.md` | Architectural decisions affecting public API |
| `API_CONTRACT.md` | Public API additions or changes |
| `ARCHITECTURE.md` | Module additions, layer changes |
| `CONSTITUTION.md` | Governance changes |

### 2.2 Documentation Style

- Document current architecture only, not future plans.
- Use Chinese for developer reference (`AGENTS.md`).
- Use English for technical docs (ADR, API contract, architecture).
- Keep documentation concise; prefer tables for structured data.

## 3. API Compatibility

### 3.1 Public API Stability

- Public API is defined in `docs/AI/API_CONTRACT.md`.
- Backward compatible within 1.x.
- Extend, don't replace.

### 3.2 Breaking Change Process

1. File an ADR explaining the reason.
2. Provide a migration path.
3. Get explicit architectural approval.
4. Update `API_CONTRACT.md`.
5. Update `DECISION_LOG.md`.

## 4. Lifecycle Consistency

### 4.1 SessionState

- `SessionState` is the single workflow state authority.
- All state transitions go through `RuleSession`.
- `InvalidStateTransition` on invalid transitions.
- Failed operations do not advance state.

### 4.2 RuleLifecycle

- `RuleLifecycle` tracks rule maturity (INFERRED → EDITABLE → TESTED → EXECUTABLE).
- Orthogonal to `SessionState` — one tracks the rule, the other tracks the session.
- `InferredRuleStore` depends on `RuleLifecycle`, not `SessionState`.

## 5. Exception Consistency

### 5.1 Public Exceptions

Only `InvalidStateTransition` is part of the public API contract.

### 5.2 Error Reporting

- Workflow-level errors → `WorkflowResult.errors` (not exceptions).
- Validation errors → `SessionValidationResult.session_errors`
  (not exceptions).
- State errors → `InvalidStateTransition` (exception, public).
- Internal errors → `RuntimeError` (exception, not part of compatibility contract).

### 5.3 Exception Design

- Exceptions carry human-readable messages.
- Messages identify the failed stage and reason.
- Stack traces are suppressed in CLI output.

## 6. Review Expectations

### 6.1 Milestone Review Checklist

Every milestone must pass review against:

1. **Architecture**: Boundaries preserved, responsibilities clear, layering maintained.
2. **Public API**: Compatibility preserved, contracts documented, public/internal boundaries respected.
3. **Testing**: Regression suite passes, new functionality covered, no coverage reduction.
4. **Documentation**: AGENTS.md updated, ADRs current, public API documented.
5. **Compatibility**: No undocumented breaking changes, behavior consistent with contracts.

### 6.2 Code Review

- Small, focused commits preferred.
- One Milestone = One Core Feature (Constitution §6 in AGENTS.md).
- Commit messages describe what and why, not how.

## 7. Development Workflow

### 7.1 Milestone Cycle

1. **Implementation** — small iterative steps, one clear goal each.
2. **Automated Tests** — write tests alongside or before implementation.
3. **Validation** — verify product behavior against spec.
4. **Smoke Test** — real-world usage validation.
5. **Git Tag** — `Mxx-complete` stable baseline.
6. **Feature Freeze** — no changes to completed modules except bug fixes.
7. **Update AGENTS.md** — document new behavior, update baselines.

### 7.2 Git Conventions

- Tags: `Mxx-complete` for stable baselines.
- Branch: feature branches for active development, merge to `main` on completion.
- Commits: descriptive messages with scope prefix (e.g., `M10.5-D: ...`).

## 8. Version

| Version | Milestone | Changes |
|---|---|---|
| 1.0 | M10.5-F | Initial Engineering Baseline |
