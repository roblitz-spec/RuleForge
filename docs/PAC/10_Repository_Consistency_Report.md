# 10 — Repository Consistency Report

**PAC-1 Phase 2 | Date: 2026-07-24**

---

## 1. Project Name

| Artifact | Value | Consistent? |
|---|---|---|
| `README.md` | ResourceHub | ✅ |
| `AGENTS.md` | ResourceHub | ✅ |
| `docs/AI/*` (12 files) | ResourceHub | ✅ |
| `config/settings.py` | ResourceHub | ✅ |
| `build.spec` | ResourceHub | ✅ |
| `ui/main_window.py` | ResourceHub v0.1 | ✅ |
| `editor/__init__.py` | Rule IDE editing layer | ⚠️ Subsystem only |
| `docs/AI/AI_HANDOFF.md` | ResourceHub (header), M12 Rule IDE (body) | ⚠️ |

**Assessment**: **Partially Consistent**. "ResourceHub" is uniform across 30+ references. "Rule IDE" appears in 5 locations as a subsystem descriptor, not a product name. The lack of a formal decision makes this a governance gap.

---

## 2. Product Description

| Artifact | Description | Consistent? |
|---|---|---|
| `README.md` | "Windows 桌面批量重命名工具" | ✅ |
| `PROJECT_BRIEF.md` | "Windows desktop batch file rename tool" | ✅ |
| `AI_MEMORY_PACK.md` | "Windows desktop batch file rename tool" | ✅ |
| `README_BUILD.md` | Build guide (no description) | — |
| `docs/development/current_status.md` | "M11.2 — UX Improvement & Stability Fixes" | ⚠️ Different context |

**Assessment**: **Consistent**. All descriptions agree on "batch file rename tool."

---

## 3. Version / Milestone Identity

| Artifact | Version Claim | Consistent? |
|---|---|---|
| `PROJECT_BRIEF.md` | M11.2 | ❌ |
| `AI_HANDOFF.md` | M11.2 | ❌ |
| `AI_MEMORY_PACK.md` | M11.1 | ❌ |
| `development/current_status.md` | M11.2 | ❌ |
| `CURRENT_STATUS.md` | M8 (M8-complete) | ✅ (source of truth) |
| `window title` | v0.1 | ❌ |
| `M8-complete` tag | M8 | ✅ (git) |

**Assessment**: **Inconsistent**. Only CURRENT_STATUS.md and git tags agree. PROJECT_BRIEF, AI_HANDOFF, AI_MEMORY_PACK, and development/current_status all claim M11.x. Window title claims v0.1.

---

## 4. Module Boundaries — Documentation vs. Code

| Module | In `ARCHITECTURE.md` | In Source Code | Lines | Consistent? |
|---|---|---|---|---|
| Scanner | ✅ | `scanner/scanner.py` | 117 | ✅ |
| RuleEngine | ✅ | `engine/rule_engine.py` | — | ✅ |
| PreviewEngine | ✅ | `engine/preview_engine.py` | — | ✅ |
| RenamePlanEngine | ✅ | `engine/rename_plan_engine.py` | — | ✅ |
| RenameEngine | ✅ | `engine/rename_engine.py` | — | ✅ |
| UndoEngine | ✅ | `engine/undo_engine.py` | — | ✅ |
| RuleAnalysis | ✅ | `engine/rule_analysis.py` | — | ✅ |
| FileTableModel | ✅ | `ui/file_table_model.py` | — | ✅ |
| RuleManagerDialog | ✅ | `ui/rule_manager_dialog.py` | — | ⚠️ |
| MainWindow | ✅ | `ui/main_window.py` | — | ⚠️ |
| **EditSession** | ❌ | `editor/edit_session.py` | 239 | ❌ |
| **DomainValidator** | ❌ | `editor/domain_validator.py` | 142 | ❌ |
| **PresetStore** | ❌ | `storage/preset_store.py` | 129 | ❌ |
| **RuleRepository** | ❌ | `storage/repository.py` | 73 | ❌ |
| **SessionStore** | ❌ | `storage/session_store.py` | 84 | ❌ |
| **JsonStorage** | ❌ | `storage/json_storage.py` | 61 | ❌ |
| **Validator** | ❌ | `validator/validator.py` | 75 | ❌ |
| **ScanWorker** | ❌ | `workers/scan_worker.py` | 87 | ❌ |
| **RenameWorker** | ❌ | `workers/rename_worker.py` | 41 | ❌ |
| **Translator** | ❌ | `i18n/translator.py` | 36 | ❌ |
| **Settings** | ❌ | `config/settings.py` | 48 | ❌ |
| **PresetManagerDialog** | ❌ | `ui/preset_manager_dialog.py` | 216 | ❌ |

**Assessment**: **Inconsistent**. 10 modules documented. 12 modules undocumented. 7 of 14 packages have no ARCHITECTURE.md representation.

---

## 5. Terminology

| Term | Usage | Consistent? |
|---|---|---|
| RuleStep | Uniform across AGENTS.md, code, tests, UI | ✅ |
| Rule | Uniform across all docs and code | ✅ |
| Repository | In `storage/repository.py` = `RuleRepository`; in docs = `Repository` | ⚠️ Class name vs doc name differ |
| Preset | Uniform across M8 docs, code, tests | ✅ |
| WorkingCopy | Used in M2-M4 docs but absent in current code (superseded by `EditSession`) | ⚠️ Historical term |
| MetadataProvider | Uniform across ARCHITECTURE.md, AGENTS.md, code | ✅ |

**Assessment**: **Partially Consistent**. Core domain terms (Rule, RuleStep, Preset) are uniform. `Repository`/`RuleRepository` naming differs between code and docs. `WorkingCopy` is a historical term that no longer matches current code.

---

## 6. Directory Organization

| Directory | Purpose | Documentation Match | Consistent? |
|---|---|---|---|
| `engine/` | Pipeline + transformations | ARCHITECTURE.md ✅ | ✅ |
| `ui/` | Qt GUI components | ARCHITECTURE.md ✅ | ✅ |
| `models/` | Domain dataclasses | ARCHITECTURE.md ❌ (not in module table) | ⚠️ |
| `storage/` | Persistence layer | ARCHITECTURE.md ❌ | ❌ |
| `editor/` | Rule IDE editing layer | ARCHITECTURE.md ❌ | ❌ |
| `workers/` | QThread wrappers | ARCHITECTURE.md ❌ | ❌ |
| `validator/` | File validation | ARCHITECTURE.md ❌ | ❌ |
| `scanner/` | Filesystem scanning | ARCHITECTURE.md ✅ | ✅ |
| `i18n/` | Internationalization | ARCHITECTURE.md ❌ | ❌ |
| `config/` | Application configuration | ARCHITECTURE.md ❌ | ❌ |
| `app/` | Unknown (empty) | ARCHITECTURE.md ❌ | ❌ (dead) |
| `resources/` | Unknown (empty) | ARCHITECTURE.md ❌ | ❌ (dead) |
| `tools/` | Development tools | ARCHITECTURE.md ❌ | ⚠️ |
| `scripts/` | Build scripts | ARCHITECTURE.md ❌ | ⚠️ |
| `tests/` | Test suite (29 files) | TEST_STRATEGY.md ✅ | ✅ |
| `docs/` | Documentation | README_AI.md ✅ | ✅ |
| `translations/` | Locale files | PROJECT_BRIEF ✅ | ✅ |

**Assessment**: **Partially Consistent**. 5/17 directories are documented. 2 directories are dead/empty. The core pipeline directories are aligned; newer packages (editor, storage, workers) are undocumented.

---

## 7. Documentation Quality

| Document | Lines | Updated? | Issue |
|---|---|---|---|
| `README.md` | 16 | ❌ | Insufficient for project maturity |
| `README_BUILD.md` | ~50 | ✅ | Accurate |
| `README_AI.md` | ~130 | ✅ | Governance current |
| `AGENTS.md` | ~190 | ✅ (M8) | Missing `add_suffix` in table |
| `PROJECT_BRIEF.md` | ~22 | ❌ | M11.2 is stale |
| `AI_HANDOFF.md` | ~30 | ❌ | M11.2 + M12 Rule IDE stale |
| `AI_MEMORY_PACK.md` | ~300 | ⚠️ | M11.1 stale; auto-generated but outdated |
| `CURRENT_STATUS.md` | ~130 | ✅ | Current, accurate |
| `NEXT_MILESTONE.md` | ~25 | ❌ | Rule Presets still listed as P3 |
| `CHANGELOG_AI.md` | ~90 | ✅ (M8) | M2–M5 missing; M8-M11 duplicate entry |
| `ARCHITECTURE.md` | ~180 | ❌ | Missing 7 packages + M8 modules |
| `DECISION_LOG.md` | ~60 | ✅ | All 6 ADRs current |
| `DEVELOPMENT_CONSTITUTION.md` | ~55 | ✅ | Stable; missing editor/ coverage |
| `AI_WORKFLOW.md` | ~280 | ✅ | Stable |
| `TEST_STRATEGY.md` | ~25 | ⚠️ | No quantitative baselines |
| `KNOWN_LIMITATIONS.md` | ~40 | ❌ | Missing M8 limitations |
| `REVIEW_GUIDELINES.md` | ~30 | ✅ | Stable |

**Assessment**: **Partially Consistent**. 7/17 documents need updates. Core governance documents (README_AI, AI_WORKFLOW, DECISION_LOG) are stable. Status documents (PROJECT_BRIEF, AI_HANDOFF, NEXT_MILESTONE) are stale.

---

## 8. Planning Consistency

| Document | Milestone | Planned Work | Consistent? |
|---|---|---|---|
| `NEXT_MILESTONE.md` | M8+ | P1 Filter, P2 EXIF, P3 **Presets (done)**, P4 Variables | ❌ |
| `AI_HANDOFF.md` | — | "Prepare M12 Rule IDE" | ❌ |
| `CURRENT_STATUS.md` | M8 | "Next: Awaiting M8 Milestone Review & Closure" | ✅ |
| `development/current_status.md` | — | "Pending: Remove debug, M12 planning" | ❌ |

**Assessment**: **Inconsistent**. Three different "next actions" exist depending on which document is read.

---

## 9. Governance Consistency

| Process | Defined? | Followed? | Consistent? |
|---|---|---|---|
| Milestone workflow (8 steps) | AGENTS.md ✅ | M2–M8 ✅ | ✅ |
| AI Workflow SOP (6 phases) | AI_WORKFLOW.md ✅ | WP-22–WP-26 ✅ | ✅ |
| Mandatory Update Checklist | README_AI.md ✅ | M8 WP-26 partial | ⚠️ (missed NEXT_MILESTONE, AI_HANDOFF) |
| Feature Freeze | AGENTS.md ✅ | M8 ✅ | ✅ |
| One Milestone, One Core Feature | AGENTS.md ✅ | M6–M8 ✅ | ✅ |
| Release Exit Criteria | README_AI.md ✅ | M8 ✅ | ✅ |
| Documentation Split Policy | AI_WORKFLOW.md ✅ | M8_COMPLETION.md created ✅ | ✅ |

**Assessment**: **Partially Consistent**. Governance processes are well-defined and mostly followed. M8 WP-26 missed updating NEXT_MILESTONE.md and AI_HANDOFF.md per the Mandatory Checklist.

---

## 10. Overall Consistency Score

| Dimension | Status |
|---|---|
| Project Name | Partially Consistent |
| Product Description | Consistent |
| Version Identity | **Inconsistent** |
| Module Boundaries | **Inconsistent** |
| Terminology | Partially Consistent |
| Directory Organization | Partially Consistent |
| Documentation | Partially Consistent |
| Planning | **Inconsistent** |
| Governance | Partially Consistent |

**Overall**: **Partially Consistent**. The project has strong internal consistency within its core pipeline and governance processes but significant drift in status documents (version identity, module documentation, planning).

---

**Confidence**: HIGH (all assessments verified by file comparison)
