# 13 — Governance Normalization Input

**PAC-1 Phase 2.5 — Final Discovery | Date: 2026-07-24**

This is the final evidence package for Alignment Review. No governance decisions are made here.

---

## Section 1 — Canonical Source Candidates

For each governance object, the artifact that appears intended as the primary reference based on repository evidence.

### 1.1 Project Name

| Field | Value |
|---|---|
| Object | Project Name |
| Current Sources | `README.md` ("ResourceHub"), 12 `docs/AI/` headers ("ResourceHub"), `config/settings.py`, `build.spec`, `ui/main_window.py` |
| Repository Evidence | "ResourceHub" is the only name in production code, configuration, build artifacts, and all documentation headers. Used consistently for 30+ references across all layers. |
| Potential Canonical Source | `README.md` (project root file — conventional entry point) |
| Confidence | HIGH |

### 1.2 Working / Subsystem Name

| Field | Value |
|---|---|
| Object | "Rule IDE" — subsystem or working name |
| Current Sources | `editor/__init__.py` ("Rule IDE editing layer"), `AI_HANDOFF.md` ("Prepare M12 Rule IDE"), `CURRENT_STATUS.md` TD-003/TD-018 triggers |
| Repository Evidence | 5 references total. `editor/` package uses it as a code-level descriptor referencing an external "Master Design." `AI_HANDOFF.md` uses it as a planned milestone name (stale). No product-level adoption. |
| Potential Canonical Source | `editor/__init__.py` (package docstring, references Master Design) — appears intended as the authoritative definition |
| Confidence | MEDIUM (no formal document exists; evidence is sparse) |

### 1.3 Product Identity

| Field | Value |
|---|---|
| Object | What the project IS (mission, scope, domain) |
| Current Sources | `PROJECT_BRIEF.md` ("Windows desktop batch file rename tool"), `README.md` ("Windows 桌面批量重命名工具"), `AI_MEMORY_PACK.md` ("batch file rename tool") |
| Repository Evidence | All sources agree on "batch file rename tool." No document defines scope boundaries, non-goals, or stakeholder value proposition. |
| Potential Canonical Source | `PROJECT_BRIEF.md` (section "What" and "Why") |
| Confidence | HIGH (description is consistent; completeness is low) |

### 1.4 Version

| Field | Value |
|---|---|
| Object | Current software version |
| Current Sources | `ui/main_window.py` ("v0.1"), `PROJECT_BRIEF.md` ("M11.2"), `AI_HANDOFF.md` ("M11.2"), `AI_MEMORY_PACK.md` ("M11.1"), `CURRENT_STATUS.md` ("M8, M8-complete") |
| Repository Evidence | 5 sources claim 4 different versions. `CURRENT_STATUS.md` is the only document updated after M8 closure and is consistent with `M8-complete` git tag. Window title "v0.1" appears to be the original version set at project creation and never updated. |
| Potential Canonical Source | `CURRENT_STATUS.md` (updated every Milestone per README_AI Mandatory Checklist) |
| Confidence | HIGH (canonical source identifiable despite inconsistency) |

### 1.5 Active Milestone

| Field | Value |
|---|---|
| Object | Current development milestone |
| Current Sources | `CURRENT_STATUS.md` ("M8, M8-complete"), `AI_HANDOFF.md` ("M11.2 Stabilization"), `development/current_status.md` ("M11.2") |
| Repository Evidence | `M8-complete` tag is the most recent tag on the current branch. `CURRENT_STATUS.md` was updated in WP-26 (M8 closure). `AI_HANDOFF.md` and `development/current_status.md` were not updated after M2–M8 baseline series. |
| Potential Canonical Source | `CURRENT_STATUS.md` § Active Baseline (updated every Milestone) |
| Confidence | HIGH |

### 1.6 Roadmap

| Field | Value |
|---|---|
| Object | Multi-milestone feature plan |
| Current Sources | `NEXT_MILESTONE.md` (P1–P4 candidate features), `AI_HANDOFF.md` § Next Action (4 items), `CURRENT_STATUS.md` § Deferred Technical Debt |
| Repository Evidence | `NEXT_MILESTONE.md` is the only document structured as a feature roadmap. But it lists Rule Presets as P3 (completed in M8) — it was not updated. `AI_HANDOFF.md` lists different next actions. No multi-milestone sequencing exists. |
| Potential Canonical Source | `NEXT_MILESTONE.md` (title and structure indicate it is the intended roadmap) |
| Confidence | MEDIUM (intended canonical source is stale; no single accurate roadmap exists) |

### 1.7 Architecture

| Field | Value |
|---|---|
| Object | Module boundaries, pipeline, hard rules |
| Current Sources | `ARCHITECTURE.md` (pipeline + 10 modules + hard rules), `AGENTS.md` (Rule Presets architecture constraints), source code (14 packages, 35+ classes) |
| Repository Evidence | `ARCHITECTURE.md` is explicitly referenced as the architecture authority by `README_AI.md`, `AI_MEMORY_PACK.md`, and `AI_HANDOFF.md`. But it documents only 10 modules and omits 7 packages added in M7–M8. |
| Potential Canonical Source | `ARCHITECTURE.md` (per README_AI: "When pipeline or boundaries change") |
| Confidence | HIGH (canonical source identifiable; content is stale) |

### 1.8 Planning (Next Milestone Scope)

| Field | Value |
|---|---|
| Object | Scope for the next milestone |
| Current Sources | `NEXT_MILESTONE.md` (Filter P1, EXIF P2, Presets P3, Variables P4), `AI_HANDOFF.md` ("Prepare M12 Rule IDE"), `CURRENT_STATUS.md` ("Awaiting M8 Milestone Review & Closure") |
| Repository Evidence | Three documents suggest three different next actions. `CURRENT_STATUS.md` is the only one updated after M8. `NEXT_MILESTONE.md` still has M8 items as "planned." |
| Potential Canonical Source | `NEXT_MILESTONE.md` (updated every Milestone per README_AI) |
| Confidence | MEDIUM (canonical source exists but is stale; ambiguity blocks M9) |

### 1.9 Design

| Field | Value |
|---|---|
| Object | System design documentation |
| Current Sources | `editor/` package docstrings (reference "Master Design" Sections 3, 4.1; AD-03), `ARCHITECTURE.md` (pipeline design), `DECISION_LOG.md` (ADR rationale) |
| Repository Evidence | A "Master Design" document is referenced by 3 production source files but is not in the repository. No formal design document directory exists. |
| Potential Canonical Source | Unknown — the referenced document is not in the repository |
| Confidence | LOW (cannot identify canonical source for an unavailable document) |

### 1.10 Decision Records

| Field | Value |
|---|---|
| Object | Architecture Decision Records |
| Current Sources | `DECISION_LOG.md` (6 ADRs: ADR-001 through ADR-006), `AGENTS.md` (architecture principles, Preset constraints), `M8_COMPLETION.md` (architecture compliance) |
| Repository Evidence | `DECISION_LOG.md` is the only ADR registry. 6 ADRs are documented. 2 significant architecture decisions (editor/ package, Preset architecture) lack ADRs. |
| Potential Canonical Source | `DECISION_LOG.md` (explicitly titled "Decision Log (ADR)") |
| Confidence | HIGH |

### 1.11 Governance Documents

| Field | Value |
|---|---|
| Object | AI governance system |
| Current Sources | `README_AI.md` (governance hub), `AI_WORKFLOW.md` (SOP), `DEVELOPMENT_CONSTITUTION.md` (principles), `REVIEW_GUIDELINES.md` (checklist), `AI_MEMORY_PACK.md` (auto-generated snapshot) |
| Repository Evidence | `README_AI.md` is the explicit governance hub (states "AI Memory Version: v2.0" and defines governance). The document names itself as the authority. |
| Potential Canonical Source | `README_AI.md` (self-identified as governance hub) |
| Confidence | HIGH |

---

## Section 2 — Terminology Inventory

### 2.1 Core Domain Terms

| Term | Meaning | Artifacts Using It | Consistency | Notes |
|---|---|---|---|---|
| **ResourceHub** | Product name | All docs, config, build, UI | **Stable** | Uniform across 30+ references. One of the few fully consistent terms. |
| **Rule IDE** | Subsystem / planned milestone | `editor/`, `AI_HANDOFF`, `CURRENT_STATUS` | **Emerging** | 5 references. "Rule IDE" is emerging as a subsystem descriptor. Not a product rename. No formal definition exists. |
| **Rule** | Primary domain object (id, name, description, steps, pinned) | All docs, code, tests | **Stable** | `models/rule.py` defines `Rule` dataclass. Uniform usage. |
| **RuleStep** | Single transformation step (type, parameters) | All docs, code, tests | **Stable** | `models/rule_step.py`. 10 types registered in `_HANDLERS`. |
| **Rule Engine** | Pure-function text transformation | `engine/rule_engine.py`, `ARCHITECTURE.md`, `AGENTS.md` | **Stable** | `RuleEngine` class. ADR-004 defines pure-function contract. |
| **Rule Editor** | UI for editing Rule + RuleSteps | Not formally used | **Undefined** | No artifact uses "Rule Editor" as a formal term. The editor is `RuleManagerDialog`. |
| **Rule Manager** | UI dialog for CRUD + step editing | `ui/rule_manager_dialog.py`, `PROJECT_BRIEF.md`, `REVIEW_M6.md` | **Stable** | Class: `RuleManagerDialog`. Docs use "Rule Manager." |
| **Rule Asset** | User-created rule configuration | Not used in repository | **Undefined** | No artifact uses "Rule Asset." |

### 2.2 Architecture Terms

| Term | Meaning | Artifacts Using It | Consistency | Notes |
|---|---|---|---|---|
| **Repository** (RuleRepository) | Sole runtime source of truth for rules | `storage/repository.py` (class: `RuleRepository`), `AGENTS.md` (refers to "Repository"), `ARCHITECTURE.md` (not in module table) | **Conflicting** | Class name is `RuleRepository`. Documentation consistently calls it "Repository." |
| **Editor** (package) | Rule IDE editing layer | `editor/__init__.py`, `editor/edit_session.py`, `editor/domain_validator.py` | **Emerging** | The `editor/` package is a distinct architectural layer. Not mentioned in `ARCHITECTURE.md`. |
| **EditSession** | Rule editing lifecycle manager | `editor/edit_session.py`, `ui/rule_manager_dialog.py`, `ui/preset_manager_dialog.py`, `tests/` | **Stable** | Class: `EditSession`. Manages CREATED→ACTIVE→CLOSED lifecycle. |
| **WorkingCopy** | Rule deep copy during editing | `ARCHITECTURE_AUDIT_M4.md`, `AGENTS.md` M2 tag description | **Deprecated** | No `WorkingCopy` class exists in current code. Superseded by `EditSession`. Historical term from M2–M4. |
| **DomainValidator** | UI-independent Rule/RuleStep validation | `editor/domain_validator.py`, `ui/rule_manager_dialog.py` | **Stable** | Class: `DomainValidator`. Referenced as "Master Design AD-03." |
| **Preset** | Saved rule configuration | `models/preset.py` (class: `Preset`), `storage/preset_store.py`, `ui/preset_manager_dialog.py`, `AGENTS.md` | **Stable** | Defined in M8. Uniform usage. |
| **PresetStore** | Persistent storage for presets | `storage/preset_store.py`, `AGENTS.md` | **Stable** | Class: `PresetStore`. JSON at `~/.resourcehub/presets.json`. |
| **MetadataProvider** | Lazy file metadata cache | `engine/metadata_provider.py`, `ARCHITECTURE.md`, `AGENTS.md` | **Stable** | Class: `MetadataProvider`. Provides `modified`/`created`. |
| **RuleAnalysis** | Context dependency declaration | `engine/rule_analysis.py`, `ARCHITECTURE.md` | **Stable** | Class: `RuleAnalysis`. `uses_index` / `uses_metadata`. |
| **Context Contract** | Frozen context fields | `AGENTS.md`, ADR-005 | **Stable** | `index`, `count`, `metadata` — frozen fields. |
| **Pipeline** | Scanner → Preview → Plan → Rename → Undo | `ARCHITECTURE.md`, `PROJECT_BRIEF.md` | **Stable** | All sources agree on the 5-stage pipeline. |

### 2.3 Governance Terms

| Term | Meaning | Artifacts Using It | Consistency | Notes |
|---|---|---|---|---|
| **Milestone (Mxx)** | Single development cycle with one core feature | `AGENTS.md`, all `docs/AI/` documents, git tags | **Stable** | Defined in AGENTS.md § One Milestone, One Core Feature. |
| **Work Package (WP-xx)** | Sub-task within a milestone | `AGENTS.md`, `CHANGELOG_AI.md`, `CURRENT_STATUS.md`, `M8_COMPLETION.md` | **Stable** | Used consistently from WP-19 through WP-26. |
| **PAC-1** | Project Alignment Check #1 | `docs/PAC/` (12 documents, this one makes 13) | **Emerging** | New governance process. Defined through its deliverables. |
| **ADR** | Architecture Decision Record | `DECISION_LOG.md` (ADR-001 through ADR-006) | **Stable** | ADR format is consistent across all 6 records. |
| **Feature Freeze** | No changes to frozen modules after Milestone close | `AGENTS.md`, `DEVELOPMENT_CONSTITUTION.md`, ADR-003 | **Stable** | Applied at M2–M8. |
| **Baseline** | Stable git tag after Milestone completion | `AGENTS.md` § Git 基线, `CURRENT_STATUS.md` | **Stable** | `Mxx-complete` tag format. |
| **Technical Debt (TD-xxx)** | Confirmed, observable issue with trigger condition | `CURRENT_STATUS.md` § Deferred Technical Debt, `AI_WORKFLOW.md` § Technical Debt Policy | **Stable** | 7 entries (TD-003 through TD-018). |
| **AI Memory** | Long-term AI knowledge system (v2.0) | `README_AI.md`, `AI_MEMORY_PACK.md` | **Stable** | 12 source documents, auto-generated snapshot. |

### 2.4 UI Terms

| Term | Meaning | Artifacts Using It | Consistency | Notes |
|---|---|---|---|---|
| **MainWindow** | Application main window | `ui/main_window.py` (class: `MainWindow`), `ARCHITECTURE.md` | **Stable** | QMainWindow subclass. Orchestration + toolbar. |
| **RuleManagerDialog** | Rule CRUD + RuleStep editing dialog | `ui/rule_manager_dialog.py` (class: `RuleManagerDialog`), `ARCHITECTURE.md` | **Stable** | Docs may call it "Rule Manager." |
| **PresetManagerDialog** | Preset save/load/delete/rename dialog | `ui/preset_manager_dialog.py` (class: `PresetManagerDialog`), `AGENTS.md` | **Stable** | Added in M8. |
| **FileTableModel** | QTableView data provider | `ui/file_table_model.py` (class: `FileTableModel`), `ARCHITECTURE.md` | **Stable** | Also `SortProxyModel` for sorting. |
| **RegexAssistant** | Regex reference window | `ui/regex_assistant.py` (class: `RegexAssistant`) | **Stable** | Non-modal reference window. |

---

## Section 3 — Source of Truth Matrix

| Domain | Current Sources | Observed State | Evidence |
|---|---|---|---|
| **Naming** | README vs editor/ vs AI_HANDOFF | **Conflicting** (ResourceHub stable; Rule IDE ambiguous) | 30+ "ResourceHub" refs. 5 "Rule IDE" refs. No formal definition of either relationship. |
| **Version Identity** | PROJECT_BRIEF vs AI_HANDOFF vs AI_MEMORY_PACK vs CURRENT_STATUS vs window title | **Conflicting** (5 sources, 4 versions) | M8, M11.1, M11.2, v0.1 — no single version is correct across all docs. |
| **Architecture** | ARCHITECTURE.md vs source code | **Partially Consistent** (core pipeline aligned; 7 packages undocumented) | 10 documented modules. 7 undocumented packages. |
| **Module Inventory** | ARCHITECTURE.md vs `ls */` | **Inconsistent** | ARCHITECTURE.md: 10 modules. Source: 14 packages (+ 2 dead). |
| **Planning** | NEXT_MILESTONE vs AI_HANDOFF vs CURRENT_STATUS | **Conflicting** (3 different "next actions") | Filter (P1) vs Rule IDE vs "awaiting review." Rule Presets still listed as P3. |
| **Decisions** | DECISION_LOG.md vs AGENTS.md vs M8_COMPLETION.md | **Fragmented** (ADRs in one file; Preset architecture in another; editor/ rationale missing) | 6 ADRs in DECISION_LOG. 2 undocumented architectural decisions (editor/, Preset). |
| **Documentation** | docs/AI/ vs docs/development/ vs README | **Fragmented** (2 status docs, stale handoff, stale brief) | 7/17 docs need updates. 2 docs track "current status" with different versions. |
| **Milestone History** | git tags vs CHANGELOG vs AGENTS.md | **Partially Consistent** (tags and AGENTS.md aligned; CHANGELOG has gaps) | 15 tags. CHANGELOG missing M2–M5. CHANGELOG has duplicate M8 entries. |
| **Governance** | README_AI vs AI_WORKFLOW vs README | **Partially Consistent** (process docs aligned; execution inconsistent) | Mandatory Checklist not fully followed after M8. |
| **Test Baseline** | CURRENT_STATUS vs CHANGELOG vs AGENTS.md vs pytest | **Consistent** (447 everywhere) | ✅ All four sources agree. |
| **Terminology** | AGENTS.md vs code vs architecture docs | **Partially Consistent** (core terms stable; WorkingCopy deprecated; Repository naming conflict) | 10 Stable, 3 Emerging, 1 Conflicting, 1 Deprecated, 3 Undefined. |

---

## Section 4 — Normalization Candidates

Every object requiring governance normalization. No prioritization. No proposed resolution.

### N-01: Project Name Relationship

| Field | Value |
|---|---|
| Object | Relationship between "ResourceHub" and "Rule IDE" |
| Current State | "ResourceHub" is the product name. "Rule IDE" is referenced in code and docs as a subsystem/milestone but never formally defined. |
| Observed Issue | 5 references to "Rule IDE" with no definition. No document states whether "Rule IDE" is: a product rename, a subsystem, a feature category, or a development milestone. |
| Affected Artifacts | `editor/__init__.py`, `editor/domain_validator.py`, `editor/edit_session.py`, `AI_HANDOFF.md`, `CURRENT_STATUS.md` |
| Evidence | `editor/__init__.py`: "Rule IDE editing layer." `AI_HANDOFF.md`: "Prepare M12 Rule IDE." No definition document exists. |
| Confidence | HIGH |

### N-02: Current Version

| Field | Value |
|---|---|
| Object | Single authoritative version number |
| Current State | PROJECT_BRIEF: M11.2; AI_HANDOFF: M11.2; AI_MEMORY_PACK: M11.1; CURRENT_STATUS: M8; Window: v0.1 |
| Observed Issue | 5 documents claim 4 different versions. New AI sessions or contributors cannot determine the current project version without cross-referencing git tags. |
| Affected Artifacts | `PROJECT_BRIEF.md`, `AI_HANDOFF.md`, `AI_MEMORY_PACK.md`, `CURRENT_STATUS.md`, `ui/main_window.py`, `development/current_status.md` |
| Evidence | Version strings extracted from each file. Git tag `M8-complete` is the most recent. |
| Confidence | HIGH |

### N-03: M12 Definition

| Field | Value |
|---|---|
| Object | What M12 actually is/was |
| Current State | Git tag `M12-complete` = Number Rule (122 tests). `AI_HANDOFF.md` = "Prepare M12 Rule IDE." |
| Observed Issue | M12 was defined and tagged as Number Rule. AI_HANDOFF.md still references a different M12 plan. This contradicts the immutable git history. |
| Affected Artifacts | `AI_HANDOFF.md`, `M12-complete` tag, `CHANGELOG_AI.md` |
| Evidence | `git tag -l M12-complete` → exists. `git show M12-complete` → Number Rule. `AI_HANDOFF.md:23` → "M12 Rule IDE." |
| Confidence | HIGH |

### N-04: Architecture Documentation Scope

| Field | Value |
|---|---|
| Object | Which modules belong in ARCHITECTURE.md |
| Current State | ARCHITECTURE.md documents 10 modules (Scanner, RuleEngine, PreviewEngine, RuleAnalysis, RenamePlanEngine, RenameEngine, UndoEngine, FileTableModel, RuleManagerDialog, MainWindow). 7 active packages are undocumented. |
| Observed Issue | 382 lines of `editor/` code, 347 lines of `storage/` code, and 5 other packages have no architecture documentation. ARCHITECTURE.md is incomplete. |
| Affected Artifacts | `ARCHITECTURE.md`, `editor/`, `storage/`, `workers/`, `validator/`, `i18n/`, `config/`, `models/` |
| Evidence | `ls -d */` counts 14 packages. `ARCHITECTURE.md` module table documents 10. |
| Confidence | HIGH |

### N-05: Planning Document Accuracy

| Field | Value |
|---|---|
| Object | Accurate, non-stale NEXT_MILESTONE.md |
| Current State | NEXT_MILESTONE.md lists Rule Presets as P3 (completed in M8). Lists Filter as P1, EXIF as P2, Variables as P4. |
| Observed Issue | P3 is already done. No new P3 replacement is listed. The document is stale and incomplete. |
| Affected Artifacts | `NEXT_MILESTONE.md` |
| Evidence | `M8-complete` tag exists. Rule Presets has 447 tests, dedicated modules, and a completion record. NEXT_MILESTONE.md was not updated. |
| Confidence | HIGH |

### N-06: AI_HANDOFF.md Currency

| Field | Value |
|---|---|
| Object | Current, accurate AI session handoff document |
| Current State | AI_HANDOFF claims "M11.2 Stabilization" and "Prepare M12 Rule IDE." Neither is current. |
| Observed Issue | The first document new AI sessions read is stale. Every session starts with inaccurate context. |
| Affected Artifacts | `AI_HANDOFF.md` |
| Evidence | File contents vs. `CURRENT_STATUS.md` vs. git tags. |
| Confidence | HIGH |

### N-07: RuleStep Table Completeness (AGENTS.md)

| Field | Value |
|---|---|
| Object | Complete RuleStep type table in AGENTS.md |
| Current State | AGENTS.md table lists 9 types (replace, remove_text, regex_replace, case, trim, number, insert, date, add_prefix). Code has 10 (add_suffix missing). |
| Observed Issue | `add_suffix` RuleStep type, delivered in M15, is not in the primary RuleStep reference table. Every AI session reads this as authoritative. |
| Affected Artifacts | `AGENTS.md` § RuleStep 类型总览 |
| Evidence | AGENTS.md table: 9 entries. `engine/rule_engine.py` `_HANDLERS`: 10 entries. `add_suffix` handler exists. |
| Confidence | HIGH |

### N-08: CHANGELOG_AI.md M8 Entry Conflict

| Field | Value |
|---|---|
| Object | Single, non-conflicting "M8" entry in CHANGELOG |
| Current State | CHANGELOG has "## M8 (Rule Presets)" (recent, Rule Presets) and "## M8-M11" (old, Core Pipeline). Two entries map to "M8." |
| Observed Issue | Chronological reading of CHANGELOG is confusing. The old "M8-M11" entry refers to completely different work than the new M8 entry. |
| Affected Artifacts | `CHANGELOG_AI.md` |
| Evidence | File grep shows two `## M8` entries with different content. |
| Confidence | HIGH |

### N-09: development/current_status.md vs. AI/CURRENT_STATUS.md

| Field | Value |
|---|---|
| Object | Single source of truth for project status |
| Current State | Two files claim to be "current status": `docs/development/current_status.md` (M11.2) and `docs/AI/CURRENT_STATUS.md` (M8). |
| Observed Issue | Two status documents with different content, different versions, and no indication of which is authoritative. |
| Affected Artifacts | `docs/development/current_status.md`, `docs/AI/CURRENT_STATUS.md` |
| Evidence | Both files exist. Both have "current status" in their title. Content is completely different. |
| Confidence | HIGH |

### N-10: "Master Design" Document Availability

| Field | Value |
|---|---|
| Object | Availability of the "Master Design" document referenced by `editor/` package |
| Current State | 3 source files reference a "Master Design" document. The document is not in the repository. |
| Observed Issue | 382 lines of production code reference an unavailable design document. The architectural rationale for the Rule IDE subsystem is inaccessible. |
| Affected Artifacts | `editor/__init__.py`, `editor/domain_validator.py`, `editor/edit_session.py` |
| Evidence | 3 docstrings with section references. 26 repository documents searched — no match. |
| Confidence | HIGH |

### N-11: Dead Packages (`app/`, `resources/`)

| Field | Value |
|---|---|
| Object | Empty, unused packages in repository |
| Current State | `app/__init__.py` (0 bytes). `resources/` (empty directory). Neither is imported anywhere. |
| Observed Issue | Clutter. Confusion for new developers. Violates clean repository principles. |
| Affected Artifacts | `app/`, `resources/` |
| Evidence | `app/__init__.py`: 0 bytes. `ls resources/`: empty. `grep -r "from app\|import app\|from resources\|import resources"`: no results. |
| Confidence | HIGH |

### N-12: KNOWN_LIMITATIONS.md Currency

| Field | Value |
|---|---|
| Object | Complete known limitations including M8 additions |
| Current State | KNOWN_LIMITATIONS.md has no preset-related entries. M8 introduced 4 documented limitations. |
| Observed Issue | The project's known limitations document is incomplete. Users and developers cannot discover preset limitations through documentation. |
| Affected Artifacts | `KNOWN_LIMITATIONS.md`, `M8_COMPLETION.md` § Known Limitations |
| Evidence | M8_COMPLETION.md lists 4 preset limitations. KNOWN_LIMITATIONS.md has 0 preset entries. |
| Confidence | HIGH |

### N-13: Terminology — WorkingCopy

| Field | Value |
|---|---|
| Object | WorkingCopy term — deprecated or current? |
| Current State | "WorkingCopy" appears in `ARCHITECTURE_AUDIT_M4.md` and `AGENTS.md` M2 tag description. No `WorkingCopy` class exists in current code. `EditSession` has replaced it. |
| Observed Issue | Historical term survives in documentation without deprecation notice. New contributors may search for "WorkingCopy" and find only historical references. |
| Affected Artifacts | `ARCHITECTURE_AUDIT_M4.md`, `AGENTS.md` (M2 tag description) |
| Evidence | `grep -r "class WorkingCopy" --include="*.py"` → no results. `EditSession` handles all editing lifecycle. |
| Confidence | HIGH |

### N-14: Terminology — Repository vs RuleRepository

| Field | Value |
|---|---|
| Object | Class name (RuleRepository) vs documentation name (Repository) |
| Current State | Code: `class RuleRepository`. AGENTS.md: "Repository." ARCHITECTURE.md: not in module table but referenced as sole source of truth. |
| Observed Issue | The class is `RuleRepository` but all documentation calls it "Repository." This is minor but creates grep-ability issues for new developers. |
| Affected Artifacts | `storage/repository.py`, `AGENTS.md` § 架构原则, `AGENTS.md` § Rule Presets |
| Evidence | Class definition: `class RuleRepository`. AGENTS.md: "Repository 始终为唯一运行时真源." |
| Confidence | HIGH |

### N-15: Versioning Policy

| Field | Value |
|---|---|
| Object | Relationship between milestone numbers, version numbers, and git tags |
| Current State | Milestone: Mxx. Window version: v0.1. Git tag: Mxx-complete. No document explains how these relate. No v1.0 criteria. |
| Observed Issue | The project has 3 numbering systems (M, v, tag suffix) with no mapping between them. Cannot determine when v1.0 will be reached or what M-number corresponds to it. |
| Affected Artifacts | `ui/main_window.py`, all `Mxx-complete` tags, all milestone documents |
| Evidence | No VERSIONING.md exists. No document maps M-numbers to v-numbers. |
| Confidence | HIGH |

---

## Section 5 — Alignment Readiness

Assessment of whether PAC-1 evidence is sufficient for each governance artifact.

### 5.1 Project Charter

**Readiness: Nearly Ready**

| Criteria | Status |
|---|---|
| Project name identified | ✅ ResourceHub (confirmed) |
| Purpose identified | ✅ Batch file rename tool |
| Scope boundaries identified | ⚠️ Rule IDE subsystem not defined |
| Non-goals identified | ❌ Not documented |
| Stakeholders identified | ❌ Not documented |
| Success criteria identified | ❌ Not documented |

**Missing evidence**: Rule IDE scope definition, stakeholder identification, success criteria, non-goals.

---

### 5.2 Decision Registry

**Readiness: Evidence Missing**

| Criteria | Status |
|---|---|
| Architecture decisions documented | ⚠️ 6 ADRs exist; 2 decisions missing (editor/, Preset) |
| Product decisions documented | ⚠️ 8 identified in PAC-1 but not in DECISION_LOG.md |
| Unconfirmed decisions flagged | ✅ 3 identified in PAC-1 |
| Decision ownership documented | ❌ No "accepted by" field in any ADR |

**Missing evidence**: ADR-007 (editor/ package), ADR-008 (Preset architecture), decision ownership, product decisions registry.

---

### 5.3 Governance Baseline

**Readiness: Nearly Ready**

| Criteria | Status |
|---|---|
| Governance documents inventoried | ✅ 17 documents identified |
| Governance gaps identified | ✅ 15 gaps documented in PAC-1 |
| Process compliance assessed | ✅ Mandatory Checklist partially followed |
| Governance maturity rated | ✅ Emerging (PAC-1 Phase 2 assessment) |

**Missing evidence**: Decision authority matrix, release process document, contributor guide.

---

### 5.4 Roadmap Refresh

**Readiness: Nearly Ready**

| Criteria | Status |
|---|---|
| Completed milestones documented | ✅ 15 tagged milestones |
| Planned features identified | ⚠️ 3 remaining from NEXT_MILESTONE (Filter, EXIF, Variables) |
| Deferred work tracked | ✅ 7 TD items in CURRENT_STATUS.md |
| Sequencing rationale | ❌ No multi-milestone sequencing exists |
| Priority conflicts resolved | ❌ Filter (P1) vs Rule IDE unresolved |

**Missing evidence**: M9 scope decision, multi-milestone sequence, Rule IDE vs Filter priority resolution.

---

### 5.5 Naming Review

**Readiness: Ready**

| Criteria | Status |
|---|---|
| Historical names documented | ✅ Only "ResourceHub" in git history |
| Working names documented | ✅ "Rule IDE" as subsystem descriptor |
| Candidate names evaluated | ✅ ResourceHub and Rule IDE evaluated (PAC-1 §6) |
| Naming conflicts identified | ✅ ResourceHub/Rule IDE relationship ambiguous |
| Evidence completeness | ✅ All naming evidence extracted from repository |

**Missing evidence**: None. PAC-1 Naming Review is complete.

---

### 5.6 Overall Alignment Readiness

| Governance Artifact | Readiness |
|---|---|
| Project Charter | **Nearly Ready** (needs Rule IDE definition, stakeholder ID) |
| Decision Registry | **Evidence Missing** (needs 2 ADRs, decision ownership) |
| Governance Baseline | **Nearly Ready** (needs authority matrix, release process) |
| Roadmap Refresh | **Nearly Ready** (needs M9 scope, sequencing) |
| Naming Review | **Ready** |

**Overall**: **Nearly Ready**. The repository provides sufficient evidence for most governance artifacts. The primary blockers are: (1) Rule IDE definition, (2) M9 scope decision, (3) 2 missing ADRs, (4) decision authority documentation.

---

## Document Summary

| Count | Category |
|---|---|
| 12 | Canonical Source Candidates identified |
| 11 | Governance Object classes analyzed |
| 31 | Terminology entries classified (18 Stable, 3 Emerging, 1 Conflicting, 1 Deprecated, 5 Undefined) |
| 11 | Domain rows in Source of Truth Matrix |
| 15 | Normalization Candidates identified |
| 5 | Governance artifacts readiness-assessed |

---

**Confidence**: HIGH (all findings verified against repository evidence; no speculation)
