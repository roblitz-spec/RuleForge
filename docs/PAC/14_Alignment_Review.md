# 14 — Alignment Review (Consolidated)

**PAC-1 | Date: 2026-07-24 | Single Input for Governance Resolution**

> This document consolidates 13 PAC-1 discovery reports into a single, non-redundant review artifact. Every section preserves original evidence. No governance conclusions have been added or modified.

---

## §1 — Governance Process

**Source**: `docs/AI/AI_WORKFLOW.md` (6-phase SOP), `docs/AI/DEVELOPMENT_CONSTITUTION.md` (10 principles), `docs/AI/README_AI.md` (AI Memory v2.0).

### Governance Principles (Established)

| # | Principle | Source |
|---|---|---|
| P1 | Stability First | `DEVELOPMENT_CONSTITUTION.md` |
| P2 | Backward Compatibility First | `DEVELOPMENT_CONSTITUTION.md` |
| P3 | Extension over Modification | `DEVELOPMENT_CONSTITUTION.md` |
| P4 | Feature Freeze after Milestone close | `DEVELOPMENT_CONSTITUTION.md`, ADR-003 |
| P5 | One Milestone, One Core Feature | `AGENTS.md` |
| P6 | Tests Required for every behavioral change | `DEVELOPMENT_CONSTITUTION.md` |
| P7 | Documents are Source of Truth | `DEVELOPMENT_CONSTITUTION.md` |
| P8 | Evidence First | `AI_WORKFLOW.md` §3 |
| P9 | Governance Before Commit | `AI_WORKFLOW.md` §3 |
| P10 | Network Filesystem by Default | `DEVELOPMENT_CONSTITUTION.md` |

### Standard Development Workflow

Per `AI_WORKFLOW.md`: Inspection → Human Review → Implementation → Documentation Update → Governance Validation → Commit.

See Governance Process for full SOP.

### Mandatory Milestone Checklist

Per `README_AI.md`: CURRENT_STATUS, CHANGELOG_AI, NEXT_MILESTONE, AI_HANDOFF must be updated every Milestone. ARCHITECTURE.md updated when boundaries change. DECISION_LOG.md updated on architectural decisions.

---

## §2 — Project Identity Model

**Sources**: `docs/PAC/01_Project_Identity.md`, `docs/PAC/06_Naming_Review.md`, `docs/PAC/13_Governance_Normalization_Input.md` §1, `docs/PAC/02_Product_Evolution.md`.

### 2.1 Product Name

| Attribute | Value | Evidence |
|---|---|---|
| Product name | **ResourceHub** | 30+ references across README, all docs/AI/, config, build, UI window title |
| Window title | `ResourceHub v0.1` | `ui/main_window.py:85` |
| Org/App config | `ResourceHub` / `ResourceHub` | `config/settings.py:7-8` |
| Build artifact | `ResourceHub.exe` | `build.spec`, `scripts/build.py` |
| Repository root | `/projects/ResourceHub` | Filesystem |

**Assessment**: ResourceHub is the single, uniform product name. No rename has occurred in repository history (0 relevant commits in `git log --all`).

**Confidence**: HIGH.

### 2.2 Subsystem: "Rule IDE"

| Attribute | Value | Evidence |
|---|---|---|
| Current usage | Subsystem descriptor | `editor/__init__.py`: "Rule IDE editing layer" |
| Planning reference | Planned milestone name (stale) | `AI_HANDOFF.md:23`: "Prepare M12 Rule IDE" |
| Technical debt triggers | Refactoring cue | `CURRENT_STATUS.md` TD-003, TD-018 |
| Implementation status | Partially implemented | `editor/` package: 382 lines (EditSession, DomainValidator) |
| Product rename | **Not executed** | No window title change, no config change, no doc rename |

**Review Finding RF-01**: "Rule IDE" is referenced in 5 locations without a formal definition. Is it a product rename, a subsystem, a feature category, or a development milestone? No document answers this.

**Confidence**: MEDIUM (evidence exists; definition does not).

### 2.3 Product Purpose

**Confirmed**: Windows desktop batch file rename tool with rule-based transformations, preview, and undo.

**Evidence**: `README.md`, `PROJECT_BRIEF.md`, `AI_MEMORY_PACK.md` — all agree.

**Confidence**: HIGH.

### 2.4 Core Domain

**Confirmed**: Rule-driven file renaming. Primary domain object: `Rule` (id, name, description, steps). 10 RuleStep types. Pipeline: Scanner → Preview → Plan → Rename → Undo.

**Confidence**: HIGH.

---

## §3 — Canonical Sources

**Source**: `docs/PAC/13_Governance_Normalization_Input.md` §1.

Each governance object has one artifact that appears intended as the primary reference, based on repository conventions and README_AI mandates.

| Domain | Canonical Source | Update Trigger | Current State |
|---|---|---|---|
| Project Name | `README.md` | Rarely | Accurate |
| Product Identity | `PROJECT_BRIEF.md` | Major release | **Stale** (claims M11.2) |
| Current Version | `CURRENT_STATUS.md` | Every Milestone | **Accurate** (M8) |
| Active Milestone | `CURRENT_STATUS.md` § Active Baseline | Every Milestone | **Accurate** (M8) |
| Architecture | `ARCHITECTURE.md` | Boundary change | **Stale** (missing 7 packages) |
| Roadmap | `NEXT_MILESTONE.md` | Every Milestone | **Stale** (P3 completed) |
| Next Actions | `AI_HANDOFF.md` | Every Milestone | **Stale** (M11.2 + M12 Rule IDE) |
| Decision Records | `DECISION_LOG.md` | Architectural decision | **Incomplete** (2 ADRs missing) |
| Governance Hub | `README_AI.md` | Rarely | Accurate |
| AI Memory | `AI_MEMORY_PACK.md` | Major milestone | **Stale** (M11.1) |
| Development Reference | `AGENTS.md` | Milestone + Rule change | **Incomplete** (missing add_suffix) |
| Known Limitations | `KNOWN_LIMITATIONS.md` | Limitation change | **Stale** (missing M8 limitations) |
| Test Baseline | `CURRENT_STATUS.md` | Every Milestone | Accurate (447) |

**Review Finding RF-02**: 7 of 13 canonical sources are stale or incomplete. The Mandatory Milestone Checklist (README_AI) was not fully executed after M8 closure — NEXT_MILESTONE.md and AI_HANDOFF.md were missed (see §9).

---

## §4 — Product Evolution

**Source**: `docs/PAC/02_Product_Evolution.md`.

### Evolution Stages

```
Problem (manual rename)
  → Initial Solution (M2–M5: core pipeline, basic rules)
    → Rule Generation (M12–M16: Number, Insert, Date, AddSuffix)
      → Rule Management (M15–M16, M6–M7: duplication, consolidation)
        → Rule Platform (M8, M11.2: presets, sorting, pinning)
          → Rule IDE (EMERGING: editor/ package, not formalized)
```

### Major Architectural Shifts

| Shift | Milestone | ADR |
|---|---|---|
| RuleEngine → pure function | M12 | ADR-004 |
| Context Contract frozen | M14 | ADR-005 |
| Scanner: no Path.resolve() | M11.2 | ADR-006 |
| Feature Freeze policy | M15 RC | ADR-003 |
| Prefix/Suffix kept independent | M15 | ADR-001 |
| Single-level Undo | M15 | ADR-002 |
| editor/ package introduced | M7–M8 | **No ADR** |
| PresetStore separate persistence | M8 | **No ADR** |

---

## §5 — Architecture Baseline

**Sources**: `docs/PAC/03_Current_Architecture.md`, `docs/AI/ARCHITECTURE.md`, source code inspection.

### 5.1 Documented Pipeline

```
File System → Scanner → PreviewEngine → RenamePlanEngine → RenameEngine → UndoEngine
```

10 modules documented in `ARCHITECTURE.md`: Scanner, RuleEngine, PreviewEngine, RuleAnalysis, RenamePlanEngine, RenameEngine, UndoEngine, FileTableModel, RuleManagerDialog, MainWindow.

### 5.2 Undocumented Modules

| Package | Lines | Modules | Added In |
|---|---|---|---|
| `editor/` | 382 | EditSession, DomainValidator | M7–M8 |
| `storage/` | 347 | RuleRepository, PresetStore, JsonStorage, SessionStore | M2–M8 |
| `workers/` | 128 | ScanWorker, RenameWorker | M2–M3 |
| `validator/` | 75 | Validator | Pre-M2 |
| `config/` | 48 | Settings | Pre-M2 |
| `i18n/` | 36 | Translator | Pre-M2 |
| `models/` | — | 11 dataclasses + enums | Pre-M2 |

**Review Finding RF-03**: ARCHITECTURE.md is the authoritative architecture document but documents only 10 of 21 modules. 7 packages (1,016+ lines) have no architecture documentation. The `editor/` package, representing the most significant architectural addition since M5, is completely undocumented in ARCHITECTURE.md.

### 5.3 Architecture Invariants

| # | Invariant | Status |
|---|---|---|
| A1 | RuleEngine = pure function, stateless | ✅ |
| A2 | Repository = sole Runtime Source of Truth | ✅ |
| A3 | PresetStore = persistent storage only | ✅ |
| A4 | Settings = metadata only | ✅ |
| A5 | Context Contract frozen (index, count, metadata) | ✅ |
| A6 | Preview ↔ Rename share RenamePlan | ✅ |
| A7 | UI → RenameWorker (QThread) → RenameEngine | ✅ |
| A8 | New Rule types: handler + UI + tests | ✅ |
| A9 | Backward compatible rules.json | ✅ |
| A10 | Feature Freeze after Milestone close | ✅ |

### 5.4 Dead Packages

| Package | State | Evidence |
|---|---|---|
| `app/` | Empty (0-byte __init__.py, no modules) | Never imported |
| `resources/` | Empty directory | No files |

---

## §6 — Terminology

**Source**: `docs/PAC/13_Governance_Normalization_Input.md` §2.

### Stable Terms (18)

ResourceHub, Rule, RuleStep, RuleEngine, RuleManager (dialog), EditSession, DomainValidator, Preset, PresetStore, MetadataProvider, RuleAnalysis, Context Contract, Pipeline, MainWindow, FileTableModel, Milestone (Mxx), Work Package (WP-xx), ADR.

### Emerging Terms (3)

| Term | Evidence |
|---|---|
| **Rule IDE** | 5 references (`editor/`, `AI_HANDOFF`, `CURRENT_STATUS`). Subsystem descriptor. Not a product rename. No formal definition. |
| **PAC-1** | 13 discovery documents created. Process defined through deliverables. |
| **Editor** (package) | `editor/` directory. 382 lines. Distinct from `validator/`. |

### Conflicting Terms (1)

| Term | Conflict |
|---|---|
| **Repository** vs **RuleRepository** | Code: `class RuleRepository`. All docs: "Repository." |

### Deprecated Terms (1)

| Term | Status |
|---|---|
| **WorkingCopy** | No class exists. Superseded by `EditSession`. Survives in `ARCHITECTURE_AUDIT_M4.md` and `AGENTS.md` M2 tag. |

### Undefined Terms (3)

Rule Editor, Rule Asset, Workspace — no repository artifact uses these formally.

---

## §7 — Decision Registry

**Source**: `docs/PAC/05_Decision_Registry.md`, `docs/AI/DECISION_LOG.md`.

### Confirmed Decisions (18)

| # | Decision | ADR | Milestone |
|---|---|---|---|
| D-01 | RuleEngine pure function contract | ADR-004 | M12 |
| D-02 | Context Contract frozen | ADR-005 | M14 |
| D-03 | Avoid Path.resolve() in Scanner | ADR-006 | M11.2 |
| D-04 | Feature Freeze Policy | ADR-003 | M15 RC |
| D-05 | Prefix/Suffix independent | ADR-001 | M15 |
| D-06 | Single-level Undo only | ADR-002 | M15 |
| D-07 | Preview ↔ Rename share RenamePlan | — | — |
| D-08 | Repository = sole Runtime Source of Truth | — | — |
| D-09 | RuleAnalysis declares context dependencies | — | — |
| D-10 | One Milestone, One Core Feature | — | — |
| D-11 | zh_CN default locale | — | — |
| D-12 | PySide6 over PyQt | — | — |
| D-13 | Non-recursive scan | — | — |
| D-14 | JSON serialization (no migration beyond v1) | — | — |
| D-15 | Windows case-only rename via samefile() | — | — |
| D-16 | PresetStore at ~/.resourcehub/presets.json | — | M8 |
| D-17 | Preset load uses deepcopy | — | M8 |
| D-18 | Startup preset restoration is defensive | — | M8 |

### Unconfirmed / Open (3)

| # | Question | Status |
|---|---|---|
| UD-01 | Product rename to "Rule IDE"? | **Unconfirmed** — insufficient evidence |
| UD-02 | M12 = Number Rule OR Rule IDE? | **Unconfirmed** — contradictory evidence |
| UD-03 | Master Design document location? | **Unconfirmed** — referenced but unavailable |

### Missing ADRs

**Review Finding RF-04**: Two significant architectural decisions lack formal ADRs:
- **Editor layer separation** (`editor/` package — EditSession + DomainValidator)
- **Preset architecture** (Repository as runtime truth, PresetStore as persistence, Settings as metadata)

Current ADR count: 6 (ADR-001 through ADR-006). Two additional ADRs (ADR-007, ADR-008) would complete the registry.

---

## §8 — Evidence Cross-Validation

**Source**: `docs/PAC/09_Evidence_Cross_Validation.md`.

### Top-Level Conflicts

| ID | Severity | Artifacts | Conflict |
|---|---|---|---|
| C-01 | HIGH | PROJECT_BRIEF, AI_HANDOFF, AI_MEMORY_PACK, development/current_status vs CURRENT_STATUS | **Version identity**: 4 docs claim M11.x; CURRENT_STATUS says M8 |
| C-02 | HIGH | NEXT_MILESTONE.md vs M8-complete tag | **Stale planning**: Rule Presets still listed as P3 |
| C-03 | HIGH | ARCHITECTURE.md vs source code | **Undocumented modules**: 7 packages not in architecture doc |
| C-04 | HIGH | ARCHITECTURE.md vs preset modules | **Missing M8 modules**: PresetStore, PresetManagerDialog not documented |
| C-05 | HIGH | AI_HANDOFF.md vs CURRENT_STATUS.md | **Stale status**: Claims "M11.2 Stabilization"; actual is M8 complete |
| C-06 | HIGH | AI_HANDOFF.md vs M12-complete tag | **M12 conflict**: Doc says "Rule IDE"; tag says Number Rule |
| C-07 | MEDIUM | AGENTS.md vs engine/rule_engine.py | **Missing type**: add_suffix not in RuleStep table |
| C-08 | MEDIUM | development/current_status.md vs AI/CURRENT_STATUS.md | **Duplicate status docs**: Two files with different versions |
| C-09 | MEDIUM | KNOWN_LIMITATIONS.md vs M8_COMPLETION.md | **Stale limitations**: M8 preset limitations not recorded |
| C-10 | MEDIUM | NEXT_MILESTONE.md | **Not updated after M8**: Per README_AI mandatory checklist |
| C-11 | LOW | CHANGELOG_AI.md | **Duplicate M8 entries**: "M8 (Rule Presets)" and "M8-M11" |
| C-12 | LOW | Window title vs CURRENT_STATUS | **v0.1** doesn't match any milestone |
| C-13 | LOW | README.md | **16 lines** for a 15-milestone project |

### Consistent Finding

**CF-01**: Test counts are consistent across all sources: AGENTS.md, CHANGELOG_AI.md, CURRENT_STATUS.md, and actual pytest output all agree at 447. Confidence: HIGH.

---

## §9 — Governance Baseline & Gaps

**Sources**: `docs/PAC/04_Governance_Baseline.md`, `docs/PAC/11_Governance_Gap_Analysis.md`.

### Existing Artifacts (17 documents)

**Core Governance** (5): README_AI.md, DEVELOPMENT_CONSTITUTION.md, AI_WORKFLOW.md, REVIEW_GUIDELINES.md, ARCHITECTURE.md.

**Status & History** (5): PROJECT_BRIEF.md, CURRENT_STATUS.md, CHANGELOG_AI.md, AI_HANDOFF.md, AI_MEMORY_PACK.md.

**Planning** (3): NEXT_MILESTONE.md, DECISION_LOG.md, KNOWN_LIMITATIONS.md.

**Milestone Records** (3): M6_COMPLETION.md, M8_COMPLETION.md, REVIEW_M6.md.

**Other** (1): TEST_STRATEGY.md.

### Missing Governance Artifacts

| ID | Gap | Priority |
|---|---|---|
| G-01 | **Project Charter** — no mission, scope, stakeholders, success criteria | HIGH |
| G-02 | **Master Design document** — referenced by editor/ package; not in repo | HIGH |
| G-03 | **Product Roadmap** — no multi-milestone plan; 1-milestone horizon only | HIGH |
| G-04 | **Versioning policy** — no v1.0 criteria; no M↔v mapping | MEDIUM |
| G-05 | **ADR-007** (editor/ package) + **ADR-008** (Preset architecture) | MEDIUM |
| G-06 | **M2–M5, M9–M16 milestone completion records** — only M6 and M8 have them | LOW |
| G-07 | **Release process** — no checklist, no cadence, no user changelog | MEDIUM |
| G-08 | **Decision authority matrix** — no "accepted by" field in ADRs | MEDIUM |
| G-09 | **Contributor guide** — AI-only onboarding (README_AI.md) | LOW |
| G-10 | **Rule IDE definition** — 5 references, 0 definitions | HIGH |
| G-11 | **Stale documentation** — 7 of 17 docs need updates | HIGH |
| G-12 | **AGENTS.md add_suffix row** | LOW |
| G-13 | **Dead packages** (`app/`, `resources/`) | LOW |

---

## §10 — Normalization Candidates

**Source**: `docs/PAC/13_Governance_Normalization_Input.md` §4.

Every object requiring governance decision. Listed in no particular order.

| ID | Object | Current State | Affected Artifacts | Confidence |
|---|---|---|---|---|
| N-01 | ResourceHub ↔ Rule IDE relationship | "Rule IDE" referenced 5 times, never defined | `editor/`, `AI_HANDOFF.md`, `CURRENT_STATUS.md` | HIGH |
| N-02 | Single current version | 5 docs claim 4 versions (M8, M11.1, M11.2, v0.1) | PROJECT_BRIEF, AI_HANDOFF, AI_MEMORY_PACK, CURRENT_STATUS, window title, development/current_status | HIGH |
| N-03 | M12 definition | Tag = Number Rule; doc = "Rule IDE" | `AI_HANDOFF.md`, M12-complete tag | HIGH |
| N-04 | ARCHITECTURE.md scope | 10 documented modules; 7 undocumented packages | `ARCHITECTURE.md`, `editor/`, `storage/`, `workers/`, `validator/`, `i18n/`, `config/` | HIGH |
| N-05 | NEXT_MILESTONE.md accuracy | P3 Rule Presets listed as planned (done in M8) | `NEXT_MILESTONE.md` | HIGH |
| N-06 | AI_HANDOFF.md currency | Claims M11.2 Stabilization + M12 Rule IDE | `AI_HANDOFF.md` | HIGH |
| N-07 | AGENTS.md add_suffix | Table shows 9 types; code has 10 | `AGENTS.md` | HIGH |
| N-08 | CHANGELOG M8 entry conflict | Two "M8" entries (Rule Presets + M8-M11) | `CHANGELOG_AI.md` | HIGH |
| N-09 | Duplicate status docs | `development/current_status.md` (M11.2) vs `AI/CURRENT_STATUS.md` (M8) | Both files | HIGH |
| N-10 | Master Design availability | Referenced by 3 source files; not in repo | `editor/` package | HIGH |
| N-11 | Dead packages | `app/` (empty), `resources/` (empty) | `app/`, `resources/` | HIGH |
| N-12 | KNOWN_LIMITATIONS currency | Missing M8 preset limitations | `KNOWN_LIMITATIONS.md` | HIGH |
| N-13 | WorkingCopy deprecation | Term survives in docs without deprecation notice | `ARCHITECTURE_AUDIT_M4.md`, `AGENTS.md` | HIGH |
| N-14 | Repository vs RuleRepository | Code class name vs doc name | `storage/repository.py`, `AGENTS.md` | HIGH |
| N-15 | Versioning policy | 3 numbering systems (M, v, tag) with no mapping | Window title, all tags, all milestone docs | HIGH |

---

## §11 — Alignment Readiness

**Source**: `docs/PAC/13_Governance_Normalization_Input.md` §5.

Assessment of whether PAC-1 evidence is sufficient for each governance artifact.

| Artifact | Readiness | Missing Evidence |
|---|---|---|
| **Naming Review** | **Ready** | None |
| **Governance Baseline** | **Nearly Ready** | Decision authority matrix, release process, contributor guide |
| **Roadmap Refresh** | **Nearly Ready** | M9 scope decision, multi-milestone sequence, Filter-vs-Rule-IDE priority |
| **Project Charter** | **Nearly Ready** | Rule IDE definition, stakeholder ID, success criteria, non-goals |
| **Decision Registry** | **Evidence Missing** | ADR-007 (editor/), ADR-008 (Preset), decision ownership for all ADRs |

### What Must Be Resolved Before Project Charter v1.0

1. Product name decision (ResourceHub only vs. ResourceHub + Rule IDE)
2. Rule IDE definition and scope
3. Versioning policy (M↔v mapping, v1.0 criteria)
4. M9+ roadmap
5. Decision authority structure
6. Stale documentation cleaned (7 docs)

---

## §12 — Project Maturity Assessment

**Source**: `docs/PAC/12_Project_State_Assessment.md`.

Scale: Established → Emerging → Fragmented → Unclear.

| Dimension | Maturity | Trend | Key Evidence |
|---|---|---|---|
| Identity | **Fragmented** | ⬇️ | Name consistent; version conflicted; Rule IDE ambiguous |
| Architecture | **Emerging** | ⬆️ | Strong core pipeline; documentation lags by 2 milestones |
| Documentation | **Fragmented** | ⬇️ | Governance docs strong; 7/17 status docs stale |
| Governance | **Emerging** | ➡️ | Processes well-designed; execution gaps (M8 checklist partial) |
| Planning | **Fragmented** | ⬇️ | 3 conflicting next actions; no multi-milestone roadmap |
| Naming | **Fragmented** | ⬇️ | ResourceHub consistent; Rule IDE undefined; no naming decision |
| Decision Traceability | **Established** | ➡️ | 6 ADRs traceable; 2 ADRs missing |

---

## §13 — Review Findings

All findings classified per SOW terminology requirements.

| ID | Classification | Description | Severity |
|---|---|---|---|
| RF-01 | Review Finding | "Rule IDE" is undefined — referenced in code and docs without formal scope, purpose, or relationship to ResourceHub | HIGH |
| RF-02 | Review Finding | 7 of 13 canonical sources are stale — Mandatory Milestone Checklist not fully executed after M8 | HIGH |
| RF-03 | Review Finding | ARCHITECTURE.md is the authoritative architecture document but documents only 10 of 21 modules; `editor/` package completely undocumented | HIGH |
| RF-04 | Review Finding | Two architectural decisions lack ADRs — editor/ layer separation and Preset architecture | MEDIUM |
| RF-05 | Review Finding | Version identity fractured — 5 documents claim 4 different versions (M8, M11.1, M11.2, v0.1) | HIGH |
| RF-06 | Review Finding | AI_HANDOFF.md is stale — claims M11.2 Stabilization; actual is M8 complete | HIGH |
| RF-07 | Review Finding | NEXT_MILESTONE.md is stale — lists Rule Presets as P3 (completed in M8) | HIGH |
| RF-08 | Review Finding | AGENTS.md RuleStep table incomplete — add_suffix (M15) is missing | MEDIUM |
| RF-09 | Review Finding | CHANGELOG_AI.md has conflicting M8 entries — "M8 (Rule Presets)" vs "M8-M11" | LOW |
| RF-10 | Review Finding | Two "current status" documents exist — `development/current_status.md` (M11.2) vs `AI/CURRENT_STATUS.md` (M8) | MEDIUM |

---

## §14 — Proposed Governance Statements

For each Review Finding, a proposed statement for governance resolution. These do NOT constitute governance decisions — they are candidate resolutions for AC_AI review.

| For | Proposed Governance Statement |
|---|---|
| RF-01 | **PG-01**: Define "Rule IDE" formally as either (a) a subsystem within ResourceHub, (b) a future product rename, or (c) a milestone category. Document in PROJECT_BRIEF.md or a new RULE_IDE_SCOPE.md. |
| RF-02 | **PG-02**: Execute the Mandatory Milestone Checklist retroactively for M8: update PROJECT_BRIEF.md, AI_HANDOFF.md, NEXT_MILESTONE.md, AI_MEMORY_PACK.md. Regenerate AI_MEMORY_PACK.md. |
| RF-03 | **PG-03**: Update ARCHITECTURE.md to include editor/ (EditSession, DomainValidator), storage/ (RuleRepository, PresetStore, JsonStorage, SessionStore), workers/, validator/, i18n/, config/. Add PresetManagerDialog to module table. |
| RF-04 | **PG-04**: Create ADR-007 (Editor Layer Separation) and ADR-008 (Preset Architecture) in DECISION_LOG.md. |
| RF-05 | **PG-05**: Normalize all version references to M8 (current baseline). Define versioning policy: M↔v mapping, v1.0 criteria. Update window title or document why it says v0.1. |
| RF-06 | **PG-06**: Update AI_HANDOFF.md to reflect M8 complete baseline. Remove stale "M11.2 Stabilization" and "M12 Rule IDE" references. |
| RF-07 | **PG-07**: Update NEXT_MILESTONE.md: remove Rule Presets (P3, completed). Add completed M8 entry. Re-evaluate remaining P1/P2/P4 priorities. |
| RF-08 | **PG-08**: Add `add_suffix` row to AGENTS.md RuleStep 类型总览 table: `| add_suffix | 添加后缀 | text | "" |`. |
| RF-09 | **PG-09**: Clarify CHANGELOG_AI.md: rename "M8-M11" entry to "M8–M11 (Early Pipeline)" or merge into a consolidated history section. |
| RF-10 | **PG-10**: Deprecate or delete `docs/development/current_status.md`. Establish `docs/AI/CURRENT_STATUS.md` as the single project status document. |

---

## §15 — Consolidation Report

### Removed Duplicate Sections

| Original Location(s) | Content | Consolidated To |
|---|---|---|
| 01 §1, 02 §1, 06 §1-3 | ResourceHub product name evidence | §2.1 |
| 01 §3-4, 02 §6, 06 §2, 07 Q-01, 13 N-01 | Rule IDE references and ambiguity | §2.2, RF-01 |
| 03 §5, 09 C-07/C-08, 10 §4, 12 §2 | ARCHITECTURE.md gaps | §5.2, RF-03 |
| 09 C-03, 10 §3, 13 N-02 | Version identity conflict | §8 C-01, RF-05 |
| 09 C-02/C-17, 10 §8, 12 §5 | NEXT_MILESTONE staleness | §8 C-02, RF-07 |
| 09 C-04/C-05, 11 G-12, 13 N-06 | AI_HANDOFF staleness | §8 C-05/C-06, RF-06 |
| 07 Q-09, 09 C-01/C-10, 11 G-14, 13 N-07 | AGENTS.md add_suffix gap | §8 C-07, RF-08 |
| 04, 11 | Governance artifact inventory + gaps | §9 (merged) |
| 05, 13 | Decision registry (detailed + referenced) | §7 (merged, D-01 through D-18) |
| 06, 10 §5, 13 §2 | Terminology inventory | §6 (uses 13 §2 as source) |
| 12, 13 §5 | Maturity assessment + readiness | §11 + §12 |

### Terminology Changes

| Before (PAC-1) | After (Consolidated) |
|---|---|
| "Conflict C-xx" | "Conflict C-xx" (preserved for traceability) |
| "Gap G-xx" | "Gap G-xx" (preserved for traceability) |
| "Normalization candidate N-xx" | "Normalization candidate N-xx" (preserved) |
| "Finding" / "Conclusion" / "Observation" | **"Review Finding RF-xx"** (uniform) |
| Loose recommendations in §8, §9, §11 | **"Proposed Governance Statement PG-xx"** (uniform) |
| "Canonical Source" (scattered) | **§3 Canonical Sources** (single section) |
| "Governance process" (scattered) | **§1 Governance Process** (single section) |

### Structural Adjustments

| Adjustment | Rationale |
|---|---|
| 13 input sections → 15 consolidated sections | Merge overlapping content; separate layers |
| Evidence → Assessment → Finding → Proposal chain | Explicit layer separation per SOW |
| All confidence levels retained | Evidence preservation rule |
| All tables preserved, deduplicated | Remove repeated evidence presentations |
| "See Governance Process" cross-references added | Avoid redefining the SOP workflow |

### Sections Merged

| Merged Sections | Source Docs | Result |
|---|---|---|
| All Rule IDE references | 01, 02, 06, 07, 09, 11, 13 | §2.2 + RF-01 |
| All architecture gap reports | 03, 09, 10, 12 | §5.2 + RF-03 |
| All version conflict reports | 09, 10, 12, 13 | §8 C-01 + RF-05 |
| All staleness reports | 09, 10, 11, 12, 13 | §8 (C-02 through C-13) + §9 G-11 |
| All decision inventories | 05, 13 | §7 |
| All governance inventories | 04, 11 | §9 |
| All terminology inventories | 06, 10, 13 | §6 |
| All readiness/assessment reports | 12, 13 | §11 + §12 |
| All proposed actions scattered across docs | 08 §4, 09, 11, 12 §11, 13 §4 | §14 (Proposed Governance Statements PG-01 through PG-10) |

### No Governance Changes Confirmation

| Check | Status |
|---|---|
| No Charter modified | ✅ |
| No Decision changed | ✅ |
| No Identity changed | ✅ |
| No Naming changed | ✅ |
| No Roadmap changed | ✅ |
| All evidence preserved | ✅ |
| All 15 normalization candidates preserved | ✅ |
| All 19 conflicts preserved | ✅ |
| All 15 governance gaps preserved | ✅ |
| Confidence levels preserved on all findings | ✅ |
| Maturity ratings preserved | ✅ |

---

**PAC-1 Alignment Review complete. This document is the single input for Governance Resolution.**

**Awaiting AC_AI review.**
