# 04 — Governance Baseline

**PAC-1 Discovery | Date: 2026-07-24**

Source: `README_AI.md`, `docs/AI/` documents, `AGENTS.md`, repository structure.

---

## 1. Existing Governance Documents

### Core Governance

| Document | Purpose | Status |
|---|---|---|
| `README_AI.md` | AI Memory v2.0 governance, onboarding, mandatory checklists | ✅ Active |
| `docs/AI/DEVELOPMENT_CONSTITUTION.md` | 10 core principles + 6 performance design principles | ✅ Active |
| `docs/AI/AI_WORKFLOW.md` | 6-phase standard operating procedure | ✅ Active |
| `docs/AI/REVIEW_GUIDELINES.md` | Reviewer checklist (architecture, compatibility, testing, UX, release) | ✅ Active |
| `docs/AI/ARCHITECTURE.md` | Pipeline diagram, module boundaries, hard rules | ✅ Active |

### Status & History

| Document | Purpose | Update Cadence |
|---|---|---|
| `docs/AI/PROJECT_BRIEF.md` | What, why, current version, completed capabilities | Major release |
| `docs/AI/CURRENT_STATUS.md` | Freeze state, test counts, Git tags, current focus | Every Milestone |
| `docs/AI/CHANGELOG_AI.md` | Per-Milestone timeline | Every Milestone |
| `docs/AI/AI_HANDOFF.md` | Quick context restore for new AI sessions | Every Milestone |
| `docs/AI/AI_MEMORY_PACK.md` | Auto-generated snapshot from source docs | After Major Milestone |

### Planning

| Document | Purpose | Update Cadence |
|---|---|---|
| `docs/AI/NEXT_MILESTONE.md` | Candidate features for next Milestone (P1–P4) | Every Milestone |
| `docs/AI/DECISION_LOG.md` | Architecture Decision Records (ADR-001 through ADR-006) | On architectural decision |
| `docs/AI/KNOWN_LIMITATIONS.md` | Current constraints; update when resolved | When limitation changes |
| `docs/AI/TEST_STRATEGY.md` | Test layers, release gates | On test policy change |

### Milestone Completion Records

| Document | Milestone |
|---|---|
| `docs/AI/M6_COMPLETION.md` | M6 Rule Duplication |
| `docs/AI/M8_COMPLETION.md` | M8 Rule Presets |
| `docs/AI/REVIEW_M6.md` | Independent review of M6 |

### Knowledge Base

| Document | Topic |
|---|---|
| `docs/knowledge/README.md` | Index |
| `docs/knowledge/windows_case_only_rename.md` | Windows case-only rename bug |
| `docs/knowledge/refresh_after_rename.md` | Post-rename rescan strategy |

### Architecture Audits

| Document | Scope |
|---|---|
| `docs/AI/ARCHITECTURE_AUDIT_M4.md` | M4 architecture boundary audit |

### Repository-Level

| Document | Purpose |
|---|---|
| `AGENTS.md` | Development reference: Git baselines, RuleStep types, behaviors, architecture principles |
| `README.md` | Minimal project overview (16 lines) |
| `README_BUILD.md` | Build guide (Chinese) |
| `README_AI.md` | AI onboarding & governance (v2.0) |

---

## 2. Decision Records

| ID | Title | Milestone | Status |
|---|---|---|---|
| ADR-001 | Prefix / Suffix independent design | M15 | Accepted |
| ADR-002 | Single-level Undo only | M15 | Accepted |
| ADR-003 | Feature Freeze Policy | M15 RC | Accepted |
| ADR-004 | RuleEngine pure function contract | M12 | Accepted |
| ADR-005 | Context Contract (frozen fields) | M14 | Accepted |
| ADR-006 | Avoid Path.resolve() in Scanner hot path | M11.1 | Accepted |

**Location**: `docs/AI/DECISION_LOG.md`

---

## 3. Planning Artifacts

| Artifact | Content | Scope |
|---|---|---|
| `NEXT_MILESTONE.md` | P1–P4 candidate features + deferred list | Next milestone only |
| `AI_HANDOFF.md` | Current state + next actions | Current state |
| `CURRENT_STATUS.md` | Full project status + deferred debt register | Comprehensive |
| `PROJECT_BRIEF.md` | Original vision + completed capabilities | Long-term |
| `AGENTS.md` | Baseline table + architecture reference | Permanent |

---

## 4. Roadmaps

**No formal roadmap document exists.** Planning is milestone-based:

| Source | Type | Horizon |
|---|---|---|
| `NEXT_MILESTONE.md` | Next milestone candidate selection | 1 milestone |
| `CURRENT_STATUS.md` § Deferred Technical Debt | Deferred work register | Indefinite |
| `AI_HANDOFF.md` § Next Action | Short-term priorities | Current |
| `AGENTS.md` § Git 基线 | Completed milestone history | Historical |

---

## 5. Milestones

### Completed (15 tagged)

| Tag | Content | Tests |
|---|---|---|
| `M2-complete` | EditSession, WorkingCopy, UI Integration | — |
| `M3-complete` | Commit, Undo/Redo, Preview Isolation | — |
| `M4-complete` | Auto Save, Unsaved Changes Warning, Session Persistence | — |
| `M4.1-complete` | Architecture Alignment Patch | — |
| `M5-complete` | Smart Previews & Analysis Warnings | 356 |
| `M6-complete` | Rule Duplication | 384 |
| `M7-complete` | Architecture Consolidation & Quality Hardening | 398 |
| `M8-complete` | Rule Presets | 447 |
| `M11.2-complete` | Sortable Table, Context Menu, Pin Rules, Regex Assistant | — |
| `M12-complete` | Number Rule | 122 |
| `M13-complete` | Insert Rule | 131 |
| `M14-complete` | Date Rule | 144 |
| `M15-complete` | AddSuffix Rule, AI Memory | — |
| `M16-complete` | AI Memory v2.0 Governance, Selection Features | — |

### Not Yet Started (from documented plans)

| Item | Priority | Source |
|---|---|---|
| M9 (Filter System) | P1 | `NEXT_MILESTONE.md` |

---

## 6. Missing Governance Components

| Component | Evidence of Need | Impact |
|---|---|---|
| **Project Charter** | `editor/` package references "Rule IDE"; no formal identity document | MEDIUM |
| **"Master Design" document** | Referenced by 3 `editor/` source files; not in repo | MEDIUM |
| **Product Roadmap** (multi-milestone) | `NEXT_MILESTONE.md` covers 1 milestone only | LOW |
| **Release versioning scheme** | `v0.1` in window title; no version policy documented | LOW |
| **Milestone acceptance criteria checklist** | Each Milestone has independent WP-level criteria; no unified template | LOW |
| **Contributor onboarding guide** | `README_AI.md` covers AI sessions only | LOW |
| **M9/M10/M11.1 milestone records** | No tags, no scope docs for these gaps | LOW |

---

## 7. Governance Maturity Assessment

| Dimension | Status | Evidence |
|---|---|---|
| **Decision traceability** | ✅ Strong | 6 ADRs in `DECISION_LOG.md` |
| **Architecture documentation** | ✅ Strong | `ARCHITECTURE.md` + source inspection agreement |
| **AI session continuity** | ✅ Strong | 12-document system + `AI_MEMORY_PACK.md` auto-generation |
| **Milestone records** | ⚠️ Incomplete | M2–M5, M9–M11.1, M12–M16 lack completion reports; M6 and M8 have them |
| **Planning horizon** | ⚠️ Limited | 1 milestone look-ahead only |
| **Product identity** | ⚠️ Unclear | ResourceHub vs. Rule IDE unresolved |
| **Release management** | ❌ Absent | No versioning policy, no release checklist, no changelog for end-users |
| **External design documents** | ❌ Missing | "Master Design" is referenced but not in repo |

---

**Confidence**: HIGH (governance documents are well-structured and consistent among themselves; gaps identified by absence of expected artifacts)
