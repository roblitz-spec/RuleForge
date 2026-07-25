# ResourceHub — Current Status

**Version**: M11.2
**Date**: 2026-07-24

## Test Status

The project maintains a comprehensive automated test suite.

| Metric | Value |
|---|---|
| Automated Tests | **192 PASS** |
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
| Rename Pipeline | Stable |
| Rule Dependency Analysis | Stable |
| Scanner API | Stable (`scan(paths: list[Path])`) |
| Multi File Selection | Supported |
| Multi Directory Selection | Supported |
| Mixed Selection | Supported |
| Batch Rename | Supported |
| Batch Undo | Supported |

## Manual QA

PASS — Smoke tests cover: scan, preview, rename (batch), undo, rule persistence.

## Current Focus

**M11.3 Baseline Stabilization — Complete**

Completed:

1. Documentation Alignment ✅
2. Validator Consolidation ✅
3. Golden-path E2E ✅
4. Repository Housekeeping ✅
5. Baseline Code Review ✅ (M11.3 #1 + #2)
6. Review Fixes (F1 + F2) ✅

Next: M12 Rule IDE

## Recent Reviews

| Review | Scope | Status | Risk | Issues |
|---|---|---|---|---|
| M11.3 #1 | `validator/`, `engine/` | Completed | LOW | 0 |
| M11.3 #2 | `models/`, `scanner/`, `storage/`, `ui/`, `workers/`, `i18n/`, `config/`, `main.py` | Completed | MEDIUM | 2 |

**Closed**: F1 (Swallowed Exceptions) — added stderr logging to workers. F2 (Rule Validation) — added step/at_index/format validation to `_validate()`. No Critical or High findings. No new Technical Debt.

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
