# RuleForge — AI-Assisted Development Workflow

---

## 1. Purpose

This document defines the standard operating procedure (SOP) for AI-assisted development in this repository.

**Why this workflow exists**: AI assistants operate without persistent memory of past decisions, project conventions, or undocumented rules. A defined workflow ensures that every session produces consistent, reviewable, and reversible output regardless of which AI tool is used.

**What problems it solves**:

- AI sessions making irreversible changes before human review
- Documentation and code drifting out of sync
- Unverified review findings becoming permanent Technical Debt
- Scope creep driven by speculative refactoring

**Which activities it governs**: All AI-assisted development — code changes, test additions, documentation updates, code reviews, and Git operations.

**Why a phased workflow is used**: Each phase has a bounded scope with explicit allowed and prohibited actions. The assistant must not perform work belonging to later phases. This prevents premature implementation, hidden changes, and undocumented decisions.

---

## 2. Workflow Overview

### Phase 1 — Inspection

**Goal**: Understand the codebase and problem before acting.

**Allowed**:

- Read source code, tests, and documentation
- Run existing tests to establish baseline
- Search and grep for relevant patterns
- Report findings, risks, and recommendations

**Prohibited**:

- Modifying any file
- Creating new files
- Deleting files
- Running commands that change system state

**Expected output**: An assessment report with findings, scope, and recommendations. No modifications.

---

### Phase 2 — Human Review

**Goal**: Obtain explicit approval before any changes are made.

**Allowed**:

- Present findings from Phase 1
- Answer clarifying questions
- Revise approach based on feedback

**Prohibited**:

- Beginning implementation
- Modifying files

**Expected output**: Explicit approval signal from the reviewer. No code changes.

---

### Phase 3 — Implementation

**Goal**: Execute approved changes with minimal scope.

**Allowed**:

- Modify source code and tests within approved scope
- Run tests to verify correctness
- Commit changes with descriptive messages

**Prohibited**:

- Expanding scope beyond approval
- Refactoring unrelated code
- Modifying frozen modules without explicit permission
- Creating multiple versions of the same file
- Speculative changes

**Expected output**: Working code, passing tests, and a clean commit. If tests fail, the phase is not complete.

---

### Phase 4 — Documentation Update

**Goal**: Keep documentation synchronized with code changes.

**Allowed**:

- Update `CURRENT_STATUS.md` with new test counts, resolved issues
- Update `CHANGELOG_AI.md` with milestone progress
- Update `AGENTS.md` if architecture or conventions changed
- Record new deferred Technical Debt if identified during implementation

**Prohibited**:

- Creating new documentation files unless the Documentation Split Policy is satisfied
- Duplicating information across files
- Including temporary observations or session-specific notes

**Expected output**: Documentation that accurately reflects the current state. No drift between code and docs.

---

### Phase 5 — Governance Validation

**Goal**: Verify compliance with project governance rules before finalizing.

**Allowed**:

- Read-only verification of all changes
- Reporting violations or inconsistencies

**Prohibited**:

- Making additional changes
- Expanding scope

**Expected output**: PASS or FAIL against governance checklist. If FAIL, return to Phase 2 for re-approval of corrections.

---

### Phase 6 — Commit

**Goal**: Finalize and tag the completed work.

**Allowed**:

- Stage and commit all relevant files
- Create Git tags following project convention
- Push to remote (if explicitly approved)

**Prohibited**:

- Committing unrelated files
- Committing `__pycache__`, `.env`, or user data
- Creating tags that don't follow the naming convention

**Expected output**: A clean commit and an appropriate Git tag. Working tree clean of unintended artifacts.

---

## 3. Documentation Governance Principles

### Evidence First

All claims about code behavior, test results, or system state must be supported by direct observation — actual command output, test runs, or file contents. Never assume.

### Minimal Change

Make the smallest change that solves the problem. Prefer single-line fixes over multi-file refactors. Do not reorganize code that is not directly related to the task.

### Single Source of Truth

Every piece of information should have exactly one authoritative location. Duplicate definitions, copied logic, or redundant documentation entries are defects and should be consolidated.

### Prefer Extending Existing Documentation

Add sections to existing documents rather than creating new ones. New documentation files require justification under the Documentation Split Policy.

### No Unnecessary Documentation Expansion

Do not create documentation for documentation's sake. Every document, section, and entry must serve a clear purpose that cannot be fulfilled by an existing document.

### Record Only Confirmed Technical Debt

Technical Debt entries require evidence from inspection or review. Temporary observations, style suggestions, personal preferences, already-resolved issues, and unverified findings do not qualify.

### Governance Before Commit

Every commit that includes code or documentation changes must pass governance validation. Uncommitted working-tree cleanup (user data, `__pycache__`, build artifacts) must be addressed before tagging.

---

## 4. Technical Debt Policy

### What Qualifies

A valid Technical Debt entry must satisfy all of:

- A concrete, observable issue in the codebase (not a hypothetical concern)
- Clear evidence (test failure, duplicated logic, measurable complexity, documentation drift)
- A defined trigger condition for re-evaluation
- No immediate functional defect (otherwise it's a bug, not debt)

### Lifecycle

| State | Meaning |
|---|---|
| **Deferred** | Confirmed issue, not yet prioritized. Has a trigger condition. |
| **Planned** | Scheduled for a specific milestone. |
| **In Progress** | Actively being addressed in the current milestone. |
| **Resolved** | Fixed and verified. No longer appears in active debt register. |

### What Does NOT Qualify

- Temporary observations made during a single session
- Style suggestions without functional impact
- Personal preferences about naming or structure
- Already resolved issues (do not re-register)
- Unverified review findings lacking concrete evidence

---

## 5. Documentation Split Policy

Create a new documentation file **only when ALL** of these conditions are true:

1. **Independent responsibility**: The content has a distinct purpose not served by any existing document.
2. **Independent evolution**: The content will change on a different cadence than the document it would otherwise extend.
3. **Readability impact**: Keeping the content in the existing document noticeably reduces readability (e.g., exceeds ~200 lines, mixes unrelated concerns).

**Otherwise**: Extend the existing document with a new section.

**Examples**:

- Adding a review record → extend `CURRENT_STATUS.md`
- Creating a brand-new policy that governs all development → new file (rare)
- Adding a single Technical Debt entry → extend `CURRENT_STATUS.md`

---

## 6. Standard Task Prompt Pattern (Mandatory)

Every task assigned to an AI assistant **MUST** begin with:

```
Current Phase:
<Workflow Phase>

Task:
...

Constraints:
...

Expected Output:
...
```

**Rules**:

- Declaring `Current Phase` is mandatory.
- The declared phase defines the maximum scope of work.
- The assistant must not perform work belonging to later phases.
- If the requested work conflicts with the declared phase, the assistant must stop and report the conflict instead of proceeding.

---

## 7. Phase Cheat Sheet

| Phase | Allowed | Forbidden | Expected Output |
|---|---|---|---|
| **1. Inspection** | Read files, run tests, search code | Modify, create, or delete files | Assessment report |
| **2. Human Review** | Present findings, answer questions | Begin implementation | Explicit approval |
| **3. Implementation** | Modify approved files, run tests | Expand scope, refactor unrelated code | Working code, passing tests, commit |
| **4. Documentation Update** | Update existing docs, record new debt | Create new doc files (without Split Policy justification) | Synced documentation |
| **5. Governance Validation** | Read-only verification | Make changes | PASS or FAIL result |
| **6. Commit** | Stage, commit, tag | Commit unrelated files, user data, artifacts | Clean commit, valid tag |

---

## 8. Standard Prompt Templates

### Inspection

```
Current Phase: 1 — Inspection

Task:
<describe what to investigate>

Constraints:
- Read-only. Do not modify any files.
- Report evidence only.

Expected Output:
<findings, risks, recommendations>
```

### Human Review

```
Current Phase: 2 — Human Review

Task:
<describe what decision is needed>

Constraints:
- No implementation.
- Answer questions, revise approach based on feedback.

Expected Output:
<explicit approval or direction>
```

### Implementation

```
Current Phase: 3 — Implementation

Task:
<describe the approved change>

Constraints:
- Small changes only.
- Preserve existing architecture.
- No speculative refactoring.
- Run tests after changes.

Expected Output:
<working code, passing tests, commit>
```

### Documentation Update

```
Current Phase: 4 — Documentation Update

Task:
<describe what documentation to update>

Constraints:
- Documentation-only task.
- Do not modify source code.
- Do not create new documentation files without Split Policy justification.

Expected Output:
<files modified, summary of changes>
```

### Governance Validation

```
Current Phase: 5 — Governance Validation

Task:
<describe what to validate>

Constraints:
- Read-only.
- Do not modify any files.
- Report PASS or FAIL with evidence.

Expected Output:
<validation checklist, overall result>
```

### Commit

```
Current Phase: 6 — Commit

Task:
<describe commit and/or tag>

Constraints:
- Only commit relevant files.
- Use repository conventions.

Expected Output:
<commit SHA, tag name, branch>
```

---

## 9. Workflow Maintenance

This workflow is designed to be **stable and long-lived**.

**When to update**:

- A new phase is needed (e.g., a new quality gate)
- A governance principle is added or retired
- The Technical Debt lifecycle changes
- The Documentation Split Policy is revised

**When NOT to update**:

- A milestone is completed (that's `CURRENT_STATUS.md`)
- A specific bug is found or fixed
- A new tool is adopted (this document is tool-neutral)
- A project decision affects only the current milestone

**Principles**:

- Keep it stable — changes should be infrequent and intentional
- Avoid milestone-specific content — those belong in `CURRENT_STATUS.md`
- Avoid temporary project decisions — those belong in `DECISION_LOG.md`
- Keep it tool-neutral — applies to any AI coding assistant
- Update only when the workflow itself changes
