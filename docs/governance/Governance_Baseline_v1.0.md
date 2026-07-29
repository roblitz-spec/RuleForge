# Governance Baseline v1.0

**PAC-1 | Date: 2026-07-24 | Source: `docs/PAC/04_Governance_Baseline.md`, `docs/PAC/14_Alignment_Review.md` §1, §9**

---

## Governance Artifact Inventory

### Core Governance Documents (5)

| Document | Location | Purpose |
|---|---|---|
| README_AI.md | `docs/AI/` | AI memory governance hub — Mandatory Update Checklist, session onboarding |
| DEVELOPMENT_CONSTITUTION.md | `docs/AI/` | 10 development principles (Stability, Compatibility, Extension, etc.) |
| AI_WORKFLOW.md | `docs/AI/` | 6-phase SOP (Inspection → Human Review → Implementation → Docs → Governance → Commit) |
| REVIEW_GUIDELINES.md | `docs/AI/` | Code + architecture review checklist |
| ARCHITECTURE.md | `docs/AI/` | Module boundaries, pipeline, hard rules |

### Status & History (5)

| Document | Location | Currency |
|---|---|---|
| PROJECT_BRIEF.md | `docs/AI/` | **Stale** (M11.2) |
| CURRENT_STATUS.md | `docs/AI/` | Current (M8) |
| CHANGELOG_AI.md | `docs/AI/` | Current (M8 entry); has M8-M11 conflict |
| AI_HANDOFF.md | `docs/AI/` | **Stale** (M11.2) |
| AI_MEMORY_PACK.md | `docs/AI/` | **Stale** (M11.1) |

### Planning (3)

| Document | Location | Currency |
|---|---|---|
| NEXT_MILESTONE.md | `docs/AI/` | **Stale** (P3 completed) |
| DECISION_LOG.md | `docs/AI/` | Current (6 ADRs); 2 ADRs missing |
| KNOWN_LIMITATIONS.md | `docs/AI/` | **Stale** (missing M8 limitations) |

### Governance Artifacts (new)

| Document | Location | Status |
|---|---|---|
| Governance_Resolution_v1.0.md | `docs/governance/` | Created (PAC-1) |
| Project_Charter_v1.0.md | `docs/governance/` | Created (PAC-1) |
| Governance_Baseline_v1.0.md | `docs/governance/` | This document |
| Decision_Registry_v1.0.md | `docs/governance/` | Created (PAC-1) |
| Roadmap_Refresh.md | `docs/planning/` | Created (PAC-1) |

### PAC-1 Discovery (14 documents)

All 14 PAC-1 discovery reports are in `docs/PAC/` for full evidence traceability.

---

## Governance Gaps

| ID | Gap | Priority |
|---|---|---|
| G-01 | Project Charter — mission, scope, stakeholders, success criteria | HIGH |
| G-02 | Master Design document — referenced by editor/; not in repo | HIGH |
| G-03 | Product Roadmap — no multi-milestone plan | HIGH |
| G-04 | Versioning policy — no v1.0 criteria; no M↔v mapping | MEDIUM |
| G-05 | ADR-007 (editor/) + ADR-008 (Preset architecture) | MEDIUM |
| G-06 | M2–M5, M9–M16 milestone completion records | LOW |
| G-07 | Release process — no checklist, no cadence | MEDIUM |
| G-08 | Decision authority matrix — no "accepted by" in ADRs | MEDIUM |
| G-09 | Contributor guide — AI-only onboarding | LOW |
| G-10 | Rule IDE definition — 5 references, 0 definitions | HIGH |
| G-11 | Stale documentation — 7/17 docs need updates | HIGH |
| G-12 | AGENTS.md add_suffix row missing | LOW |
| G-13 | Dead packages (`app/`, `resources/`) | LOW |

---

## Governance Maturity

| Dimension | Maturity |
|---|---|
| Process Design | **Established** (SOP + Constitution + Checklist) |
| Process Execution | **Emerging** (M8 checklist partially executed) |
| Documentation Currency | **Fragmented** (7/17 docs stale) |
| Decision Traceability | **Established** (6 ADRs, 18 confirmed decisions) |
| Completeness | **Emerging** (charter, roadmap, versioning missing) |

---

**Source evidence**: `docs/PAC/04_Governance_Baseline.md`, `docs/PAC/11_Governance_Gap_Analysis.md`, `docs/PAC/14_Alignment_Review.md`.
