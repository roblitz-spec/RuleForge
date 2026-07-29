# Governance Resolution v1.0

**PAC-1 | Date: 2026-07-24 | Source: `docs/PAC/14_Alignment_Review.md` §13–§14**

---

## Review Findings

| ID | Description | Severity |
|---|---|---|
| RF-01 | "Rule IDE" is undefined — referenced in code and docs without formal scope, purpose, or relationship to ResourceHub | HIGH |
| RF-02 | 7 of 13 canonical sources are stale — Mandatory Milestone Checklist not fully executed after M8 | HIGH |
| RF-03 | ARCHITECTURE.md documents only 10 of 21 modules; `editor/` package completely undocumented | HIGH |
| RF-04 | Two architectural decisions lack ADRs — editor/ layer separation and Preset architecture | MEDIUM |
| RF-05 | Version identity fractured — 5 documents claim 4 different versions (M8, M11.1, M11.2, v0.1) | HIGH |
| RF-06 | AI_HANDOFF.md is stale — claims M11.2 Stabilization; actual is M8 complete | HIGH |
| RF-07 | NEXT_MILESTONE.md is stale — lists Rule Presets as P3 (completed in M8) | HIGH |
| RF-08 | AGENTS.md RuleStep table incomplete — add_suffix (M15) is missing | MEDIUM |
| RF-09 | CHANGELOG_AI.md has conflicting M8 entries — "M8 (Rule Presets)" vs "M8-M11" | LOW |
| RF-10 | Two "current status" documents exist — `development/current_status.md` (M11.2) vs `AI/CURRENT_STATUS.md` (M8) | MEDIUM |

---

## Proposed Governance Statements

| ID | Statement |
|---|---|
| PG-01 | Define "Rule IDE" formally as either (a) a subsystem within ResourceHub, (b) a future product rename, or (c) a milestone category. Document in PROJECT_BRIEF.md or a new RULE_IDE_SCOPE.md. |
| PG-02 | Execute the Mandatory Milestone Checklist retroactively for M8: update PROJECT_BRIEF.md, AI_HANDOFF.md, NEXT_MILESTONE.md, AI_MEMORY_PACK.md. Regenerate AI_MEMORY_PACK.md. |
| PG-03 | Update ARCHITECTURE.md to include editor/ (EditSession, DomainValidator), storage/ (RuleRepository, PresetStore, JsonStorage, SessionStore), workers/, validator/, i18n/, config/. Add PresetManagerDialog to module table. |
| PG-04 | Create ADR-007 (Editor Layer Separation) and ADR-008 (Preset Architecture) in DECISION_LOG.md. |
| PG-05 | Normalize all version references to M8 (current baseline). Define versioning policy: M↔v mapping, v1.0 criteria. Update window title or document why it says v0.1. |
| PG-06 | Update AI_HANDOFF.md to reflect M8 complete baseline. Remove stale "M11.2 Stabilization" and "M12 Rule IDE" references. |
| PG-07 | Update NEXT_MILESTONE.md: remove Rule Presets (P3, completed). Add completed M8 entry. Re-evaluate remaining P1/P2/P4 priorities. |
| PG-08 | Add `add_suffix` row to AGENTS.md RuleStep 类型总览 table: `| add_suffix | 添加后缀 | text | "" |`. |
| PG-09 | Clarify CHANGELOG_AI.md: rename "M8-M11" entry to "M8–M11 (Early Pipeline)" or merge into a consolidated history section. |
| PG-10 | Deprecate or delete `docs/development/current_status.md`. Establish `docs/AI/CURRENT_STATUS.md` as the single project status document. |

---

## Resolution Status

These findings and statements constitute the PAC-1 governance resolution baseline. They are awaiting AC_AI approval and action assignment.

**Source evidence**: `docs/PAC/14_Alignment_Review.md` (full consolidated review with all evidence, confidence levels, and cross-references).
