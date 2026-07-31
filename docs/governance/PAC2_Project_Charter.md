# PAC-2 Project Charter

| id | type | status | version | date |
|---|---|---|---|---|
| `GOV-PLAN-001` | `PLAN` | `accepted` | `1.0` | `2026-07-29` |

| primary_source |
|---|
| `GOV-REC-001` (Governance_Acceptance_PAC1.md) |

**Date**: 2026-07-29 | **Phase**: Initiation | **Predecessor**: PAC-1 (Accepted v1.0, commit [`8bf5125`](../../8bf5125))

---

## Purpose

PAC-2 enhances the governance operational capability of the ResourceHub project. It builds on the governance framework established and accepted by PAC-1, transforming it from a documented baseline into a running system with change management, ADR lifecycle, automated consistency enforcement, and stale document remediation.

PAC-2 does **not** rebuild the governance baseline. PAC-1's Accepted v1.0 documents are immutable input.

---

## Scope

### In Scope

| Area | Description |
|---|---|
| **PG Item Resolution** | Close open Proposed Governance Statements from PAC-1 (PG-01 through PG-10) |
| **ADR Lifecycle** | Formalize ADR creation/review/acceptance workflow; complete ADR-007 and ADR-008 |
| **Change Management** | Define how governance documents are modified post-baseline: who, what process, what evidence threshold |
| **Consistency Automation** | Script-based checks for cross-document consistency (version alignment, reference integrity, staleness detection) |
| **Stale Document Remediation** | Update or formally deprecate the 7 stale documents identified in PAC-1 |
| **Versioning Policy** | Define M↔v mapping, v1.0 criteria, version numbering rules |
| **Governance Index** | Create a single entry-point index (`docs/governance/README.md`) with dependency visualization |

### Out of Scope

| Item | Reason |
|---|---|
| Modifying PAC-1 Accepted v1.0 documents | Baseline is frozen |
| Redefining governance architecture | 5-layer model accepted; PAC-2 operates within it |
| New RuleStep types or product features | Implementation, not governance |
| PAC-3 scope or roadmap decisions | Future planning only |
| Human stakeholder recruitment | Not a deliverable |
| Renaming the project | PG-01 resolves definition, not rename decision |

---

## Objectives

| # | Objective | Success Measure |
|---|---|---|
| O1 | Close all 10 PG items from PAC-1 | 10/10 PG items resolved (accepted or formally deferred) |
| O2 | Formalize ADR lifecycle | ADR template + workflow documented; ADR-007 and ADR-008 created and accepted |
| O3 | Implement consistency automation | At least 3 automated checks (version, references, staleness) passing on the repository |
| O4 | Remediate stale documentation | 0 stale documents in `docs/AI/` (7 → 0) |
| O5 | Establish versioning policy | Single versioning policy document; all version references consistent |
| O6 | Create governance index | `docs/governance/README.md` with dependency graph |

---

## Success Criteria

PAC-2 is complete when ALL of the following are true:

1. **All PG items resolved**: 10/10 PG items from `Governance_Resolution_v1.0.md` have a final disposition (accepted, deferred, or superseded) recorded in `Decision_Registry_v1.0.md`
2. **ADR lifecycle operational**: ADR template exists; at least 2 ADRs (ADR-007, ADR-008) completed through the formal workflow; ADR status tracking is current
3. **Consistency checks pass**: Automated scripts confirm zero staleness, zero version conflicts, and zero broken cross-references across all governance documents
4. **Stale documents remediated**: All documents listed in `Governance_Baseline_v1.0.md` § Stale documentation (G-11) are updated or formally deprecated
5. **Versioning policy published**: A `VERSIONING.md` (or equivalent) exists with M↔v mapping and v1.0 criteria
6. **Governance index published**: `docs/governance/README.md` exists with all governance documents indexed and the dependency chain visualized
7. **Acceptance record created**: `Governance_Acceptance_PAC2.md` confirms all success criteria met, analogous to PAC-1 acceptance process
8. **No PAC-1 regression**: All PAC-1 Accepted v1.0 documents remain unmodified; all existing tests continue to pass

---

## Deliverables

| # | Deliverable | Type | Owner |
|---|---|---|---|
| D1 | PG Item Resolution Log | Document | PAC-2 |
| D2 | ADR Lifecycle Specification + Template | Document | PAC-2 |
| D3 | ADR-007 (Editor Layer Separation) | ADR | PAC-2 |
| D4 | ADR-008 (Preset Architecture) | ADR | PAC-2 |
| D5 | Consistency Check Scripts (≥3) | Tooling | PAC-2 |
| D6 | Stale Document Updates (7 docs) | Documents | PAC-2 |
| D7 | Versioning Policy (`VERSIONING.md`) | Document | PAC-2 |
| D8 | Governance Index (`docs/governance/README.md`) | Document | PAC-2 |
| D9 | Updated `Decision_Registry_v1.0.md` | Document | PAC-2 |
| D10 | `Governance_Acceptance_PAC2.md` | Document | PAC-2 |

---

## PG Item Prioritization

PAC-1 identified 10 Proposed Governance Statements. PAC-2 resolves them in this priority order:

| Priority | PG Items | Rationale |
|---|---|---|
| **P0 (Blocking)** | PG-05 (versioning), PG-06 (AI_HANDOFF), PG-07 (NEXT_MILESTONE) | These block all other consistency work. Without a single version of truth, no document can be validated. |
| **P1 (High)** | PG-01 (Rule IDE), PG-03 (ARCHITECTURE), PG-04 (ADR-007/008) | These define project identity and architecture. They are prerequisites for roadmap decisions. |
| **P2 (Medium)** | PG-02 (Mandatory Checklist), PG-10 (deprecate stale status doc) | Remediation of stale documents. Can proceed in parallel with P1. |
| **P3 (Low)** | PG-08 (AGENTS.md add_suffix), PG-09 (CHANGELOG clarification) | Minor documentation fixes. Independent of other work. |

---

## Risks & Assumptions

### Risks

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R1 | PG-01 (Rule IDE definition) requires human stakeholder decision | Medium | Medium | Produce 3 options with tradeoffs; defer to human if no decision authority exists |
| R2 | Stale document updates uncover additional undocumented decisions | Medium | Low | Stop at discovery boundary; log as PG-11+ for PAC-3; do not expand PAC-2 scope |
| R3 | Consistency automation reveals false positives | Low | Low | Scripts must be reviewable; false positives documented, not suppressed |
| R4 | ADR-007/008 creation surfaces undocumented architecture decisions | Medium | Medium | Discovery is allowed; decisions deferred to PAC-3 if not resolvable within PAC-2 scope |

### Assumptions

| # | Assumption |
|---|---|
| A1 | PAC-1 Accepted v1.0 baseline is correct and complete for its scope |
| A2 | The 5-layer governance architecture (Resolution → Charter → Baseline → Registry → Roadmap) remains the canonical structure |
| A3 | `docs/AI/` documents are within PAC-2 scope for staleness remediation |
| A4 | Repository test baseline (447 tests) remains the regression gate |
| A5 | PAC-2 operates under the same constraints as PAC-1: documentation-only, zero code changes to the production application |
| A6 | Decision authority for PG items rests with the governance review process; PAC-2 proposes, does not unilaterally decide |

---

## Non-Goals

PAC-2 explicitly does **not**:

- Add new RuleStep types or product features
- Change the application codebase
- Restructure the repository beyond `docs/`
- Define PAC-3 scope (beyond noting deferred items)
- Create new governance document types beyond those listed in deliverables
- Modify the AGENTS.md development workflow (that is a product governance document, not a governance capability document)

---

## Acceptance

PAC-2 is accepted when:

1. All 8 Success Criteria are verified
2. `Governance_Acceptance_PAC2.md` is created with the same structure as PAC-1 acceptance
3. The acceptance record links to this charter and confirms all deliverables
4. All PG items have final disposition in `Decision_Registry_v1.0.md`
5. Working tree is clean; all changes committed

---

## References

| Document | Relationship |
|---|---|
| `Governance_Acceptance_PAC1.md` | PAC-1 acceptance baseline (immutable input) |
| `Governance_Resolution_v1.0.md` | Source of PG-01 through PG-10 |
| `Governance_Baseline_v1.0.md` | Stale document inventory (G-11) |
| `Decision_Registry_v1.0.md` | Will receive PG resolutions |
| `PAC1_Architecture_Retrospective.md` | Recommendations 1–9 (design input) |
| `docs/AI/DEVELOPMENT_CONSTITUTION.md` | Constraint: Extension over Modification |

---

**PAC-2 is initiated. No governance changes are made until Phase 1 (Discovery) delivers its findings for review.**
