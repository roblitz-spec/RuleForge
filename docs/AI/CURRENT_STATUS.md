# ResourceHub — Current Status

**Branch**: `m10-phase3a-rule-analysis`
**Date**: 2026-07-29
**Active Baseline**: M7 (M6-complete frozen)

## Test Status

| Metric | Value |
|---|---|
| Automated Tests | **398 PASS** (M6: 384 + WP-19: +4 + WP-20: +10) |
| Regression Matrix | **PASS** |
| Unit + Integration | PASS |
| Preview==Rename E2E | PASS |
| Undo Cycle | PASS |
| Boundary (Unicode/Long/Conflict) | PASS |
| Multi-Select (File+Dir+Mixed) | PASS |

## Blocker

**None.**

## Project Status

| Item | Status |
|---|---|
| Architecture | Stable |
| Rule Duplication (M6) | Stable |
| ID Generation Consolidation (M7 WP-19) | Stable |
| EditSession Interaction Coverage (M7 WP-20) | Stable |
| Rule Editing Pipeline | Stable |
| Rule Dependency Analysis | Stable |
| Auto Save & Session Persistence | Stable |
| Undo / Redo | Stable |

## Current Focus

**M7 Architecture Consolidation & Quality Hardening — In Progress**

Completed:
- M6: Rule Duplication ✅ (frozen at `M6-complete`)
- WP-19: ID Generation Consolidation ✅
- WP-20: EditSession Interaction Coverage ✅

Pending:
- WP-21: Documentation Synchronization (in progress)

## Recent Reviews

| Review | Scope | Status | Risk | Issues |
|---|---|---|---|---|
| M6 Independent | `repository.py`, `ui/rule_manager_dialog.py`, `tests/test_rule_editor.py` | APPROVED | LOW | 6 observations (all non-blocking) |
| WP-19 Review | ID consolidation, 3 files | ACCEPTED | LOW | 0 |
| WP-20 Review | EditSession tests, 10 tests | ACCEPTED | LOW | 0 |

---

## Deferred Technical Debt

- **TD-003 — RuleManagerDialog God Class (694 行)**
  - Status: Deferred
  - Evidence: Project Health Review (2026-07-24)
  - Reason: 6 responsibilities in one class; no functional defect. Refactor when Rule IDE introduces new step types.
  - Trigger: New RuleStep type requires UI changes, or M12 Rule IDE begins.

- **TD-007 — MainWindow 接近 God Class (550 行)**
  - Status: Deferred
  - Evidence: Project Health Review (2026-07-24)
  - Reason: 4+ responsibilities; currently maintainable. Split when adding new top-level features.
  - Trigger: Adding a new major UI feature (e.g., preview panel, batch operation queue).

- **TD-008 — Number Rule 硬编码分隔符**
  - Status: Deferred
  - Evidence: Project Health Review (2026-07-24)
  - Reason: `_handle_number()` suffix mode uses hardcoded `_`; Date Rule already has configurable `separator`. Backward-compatible fix.
  - Trigger: User requests customizable Number separator, or Rule parameter audit.

- **TD-009 — 调试代码残留在生产文件**
  - Status: Deferred
  - Evidence: Project Health Review (2026-07-24)
  - Reason: `_record_role()` / `dump_role_stats()` in `ui/file_table_model.py:126-131`. No UI trigger; production dead code.
  - Trigger: Next file_table_model.py maintenance pass.

- **TD-011 — FileItem 命名歧义**
  - Status: Deferred
  - Evidence: Project Health Review (2026-07-24)
  - Reason: `FileItem` holds both files and directories. Onboarding confusion risk. Requires global rename.
  - Trigger: Major version bump or architecture refresh.

- **TD-013 — README.md 信息不足 (16 行)**
  - Status: Deferred
  - Evidence: Project Health Review (2026-07-24)
  - Reason: Missing feature list, Rule type table, usage guide. Not blocking development.
  - Trigger: Preparing for public release or GitHub promotion.

- **TD-018 — Validation Rule Drift**
  - Status: Deferred
  - Evidence: M11.3 Review #1
  - Reason: `Validator.validate()` reimplements checks inline rather than calling `check_legality()`. Current behavior is correct.
  - Trigger: Validation rules change, Rule IDE introduces new validation, or M13 validation refactor begins.

---

## Feature Freeze

The following modules are frozen. Changes require explicit approval:

| Module | Reason | When Unfrozen |
|---|---|---|
| `engine/rule_engine.py` | 10 Rule types stable, pure-function contract | Major version bump |
| `engine/rename_engine.py` | Plan-based execution stable | Architecture change |
| `engine/preview_engine.py` | Context contract frozen | New context field needed |
| `engine/rename_plan_engine.py` | Conflict detection stable | New conflict type |
| `ui/file_table_model.py` | `dataChanged` refresh stable | Performance regression |

## Git Tags

| Tag | Content |
|---|---|
| `M12-complete` | Number Rule |
| `M13-complete` | Insert Rule |
| `M14-complete` | Date Rule |
| `M15-complete` | AddSuffix Rule |
| `M16-complete` | AI Memory v2.0 Governance |
