# PAC-2 Governance Operating Model v1.0-draft

| id | type | status | version | date |
|---|---|---|---|---|
| `GOV-GUIDE-008` | `GUIDE` | `accepted` | `1.0` | `2026-07-29` |

| source | part_of |
|---|---|
| `GOV-REF-007` (Standards Framework), GS-01 through GS-05 | PAC-2 Governance |

---

**Date**: 2026-07-29 | **Type**: Governance Operating Model | **Status**: Draft for review

---

## 1. Purpose

Define the permanent operating model for PAC-2 governance. This model governs how governance itself evolves — how changes to governance capabilities, projects, standards, and releases are evaluated, approved, implemented, and released.

The GOM is the **meta-lifecycle**: it operates above individual governance projects (PG items) and provides the unified process through which the governance SYSTEM evolves. Individual PG items execute within this model using GS-01 (7-WP lifecycle).

---

## 2. Governance Principles

The operating model formally adopts the following principles. Every governance decision, process, and artifact must be consistent with these principles.

| # | Principle | Definition | Enforcement |
|---|---|---|---|
| P1 | **Evidence Before Decision** | No governance decision is made without repository evidence establishing the current state, the gap, and the need. | Gate G1 (Evidence Complete) |
| P2 | **Capability Before Structure** | Architecture decisions are based on governance capabilities (what the system must do), not existing document assignments (where things currently live). | Gate G3 (Architecture Approved) |
| P3 | **Architecture Before Implementation** | No repository change begins without an approved architecture design and migration plan. | Gate G5 (Implementation Authorized) |
| P4 | **Historical Evidence Is Immutable** | Accepted governance artifacts are never modified retroactively. Forward changes are declared, not retrofitted. | All stages |
| P5 | **Forward Changes Require Explicit Approval** | Every governance change — reclassification, re-labeling, merger, deprecation — requires an explicit governance decision before execution. | Gate G5 (Implementation Authorized) |
| P6 | **Every Governance Change Must Be Traceable** | From evidence to decision to implementation to release — the full chain must be traceable through GOV-IDs, relationship metadata, and registry entries. | GS-05 (Traceability Standard) |
| P7 | **Governance Releases Define Operational Baselines** | A governance release (PAC-N) bundles completed governance work into an accepted, immutable baseline. The release is the source of truth for what is operational. | Gate G7 (Release Approved) |

---

## 3. Governance Lifecycle

### 3.1 Lifecycle Overview

```
Repository Evidence
        │
        ▼
┌─────────────────────────────┐
│  EI: Evidence Investigation │  ← Gate G1: Evidence Complete
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│  SDR: Scope Decision Review │  ← Gate G2: Scope Confirmed
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│  CAR: Capability Arch Review│  ← Gate G3: Architecture Approved
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│  CMP: Capability Migr Plan  │  ← Gate G4: Migration Approved
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│  EAR: Evolution Appr Review │  ← Gate G5: Implementation Authorized
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│  ADR: Architecture Dec Rec  │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│  IC: Implementation Contract│
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│  Repository Implementation  │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│  Validation                 │  ← Gate G6: Validation Passed
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│  GR: Governance Release     │  ← Gate G7: Release Approved
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│  Registry Synchronization   │
└─────────────────────────────┘
```

### 3.2 Stage Definitions

#### EI: Evidence Investigation

| Attribute | Definition |
|---|---|
| **Objective** | Establish the factual baseline for a governance question using repository evidence only. |
| **Inputs** | Repository artifacts, registry, acceptance records, git history |
| **Outputs** | Evidence Investigation document (GOV-REV-XXX): findings, root cause, status determination |
| **Entry criteria** | A governance question or inconsistency has been identified |
| **Exit criteria** | All claims are evidence-supported. No assumptions. No status changes without evidence. Investigation scope is complete. |
| **Authority** | Governance Architect |
| **Precedent** | PG-01 Lifecycle Status Investigation (`GOV-REV-014`) |

#### SDR: Scope Decision Review

| Attribute | Definition |
|---|---|
| **Objective** | Determine whether an identified governance issue requires architectural-level analysis or can be resolved through an existing PG item. |
| **Inputs** | Evidence Investigation output, PAC-2 Charter, PG item inventory |
| **Outputs** | Scope Decision: (a) escalated to CAR, (b) assigned to existing PG, (c) deferred to PAC-3, (d) resolved immediately (ADR) |
| **Entry criteria** | Gate G1 passed |
| **Exit criteria** | Scope decision is documented with rationale. Clear next stage is identified. |
| **Authority** | Governance Sponsor + Governance Architect |
| **Precedent** | Decision to escalate PG-01/PG-05 scope conflict to CAR-001 |

#### CAR: Capability Architecture Review

| Attribute | Definition |
|---|---|
| **Objective** | Determine appropriate capability boundaries based on governance objectives and long-term architecture. |
| **Inputs** | Evidence Investigation, repository evidence, governance objectives, existing capability model |
| **Outputs** | Capability Architecture Review: objectives analysis, capability catalogue, dependency model, boundary assessment, project mapping, decision options, recommended architecture |
| **Entry criteria** | Gate G2 passed |
| **Exit criteria** | Architecture is complete (all capability boundaries defined), internally consistent, and ready for migration planning. |
| **Authority** | Governance Architect |
| **Precedent** | CAR-001 (`GOV-REV-015`) — PG-01/PG-05 capability boundary analysis |

#### CMP: Capability Migration Plan

| Attribute | Definition |
|---|---|
| **Objective** | Transform architectural conclusions into a structured, executable migration strategy. |
| **Inputs** | CAR output, current state baseline, registry |
| **Outputs** | Capability Migration Plan: current state, target state, migration matrix, traceability plan, decision requirements, roadmap, risk assessment, decision options, recommendation |
| **Entry criteria** | Gate G3 passed |
| **Exit criteria** | Migration plan is executable, traceability is preserved, all risks mitigated |
| **Authority** | Governance Architect |
| **Precedent** | CMP-001 (`GOV-REV-016`) |

#### EAR: Evolution Approval Review

| Attribute | Definition |
|---|---|
| **Objective** | Formal review and approval of the complete architecture + migration plan before any repository changes. |
| **Inputs** | CAR, CMP, decision requirements |
| **Outputs** | Evolution Approval document: PASS / PASS WITH OBSERVATIONS / REVISE REQUIRED |
| **Entry criteria** | Gate G4 passed |
| **Exit criteria** | All decision requirements approved; implementation is authorized |
| **Authority** | Governance Reviewer (per GS-03 R2: Design Review) |
| **Precedent** | GS-03 Design Review process |

#### ADR: Architecture Decision Record

| Attribute | Definition |
|---|---|
| **Objective** | Record each governance architecture decision as a formal, traceable decision record. |
| **Inputs** | EAR-approved decisions |
| **Outputs** | ADR entry in Decision Registry or DECISION_LOG.md |
| **Entry criteria** | Gate G5 passed |
| **Exit criteria** | Every approved decision has an ADR with rationale, alternatives considered, and traceability |
| **Authority** | Decision Authority |
| **Precedent** | PG-04 (ADR creation workflow) |

#### IC: Implementation Contract

| Attribute | Definition |
|---|---|
| **Objective** | Define the precise scope, deliverables, and constraints for repository implementation. |
| **Inputs** | CMP migration matrix, approved ADRs |
| **Outputs** | Implementation Contract: artifact list, change specifications, validation criteria, rollback conditions |
| **Entry criteria** | All ADRs recorded |
| **Exit criteria** | Contract is specific enough to validate implementation against |
| **Authority** | Repository Maintainer |
| **Precedent** | GS-01 WP-05 (Implementation scope) |

#### Repository Implementation

| Attribute | Definition |
|---|---|
| **Objective** | Execute the approved migration plan under the implementation contract. |
| **Inputs** | IC, CMP migration matrix |
| **Outputs** | Committed repository changes |
| **Entry criteria** | IC approved |
| **Exit criteria** | All changes match IC specifications; no unapproved artifacts; PAC-1 baselines preserved |
| **Authority** | Repository Maintainer |
| **Precedent** | GS-01 WP-05 + WP-06 |

#### Validation

| Attribute | Definition |
|---|---|
| **Objective** | Verify implementation conformance to the implementation contract and migration plan. |
| **Inputs** | IC, CMP, implemented changes |
| **Outputs** | Validation Report: PASS — ALL NON-CONFORMITIES RESOLVED / PASS WITH NON-CONFORMITIES / FAIL |
| **Entry criteria** | Implementation complete |
| **Exit criteria** | All non-conformities resolved; Gate G6 passed |
| **Authority** | Governance Reviewer (per GS-03 R3: Validation) |
| **Precedent** | GS-03 R3 (Validation) |

#### GR: Governance Release

| Attribute | Definition |
|---|---|
| **Objective** | Bundle completed governance work into an accepted, immutable baseline. |
| **Inputs** | Validation report, all stage artifacts, ADRs |
| **Outputs** | Governance Release: acceptance record, release manifest, capability status, operational baseline declaration |
| **Entry criteria** | Gate G6 passed |
| **Exit criteria** | Release accepted; Gate G7 passed |
| **Authority** | Release Authority |
| **Precedent** | PAC-2 Standards Acceptance (`GOV-REC-008`) |

#### Registry Synchronization

| Attribute | Definition |
|---|---|
| **Objective** | Synchronize governance registries with the accepted release baseline. |
| **Inputs** | GR acceptance record, new/updated artifacts |
| **Outputs** | Updated Governance Object Registry, updated statistics, updated relationship index |
| **Entry criteria** | Gate G7 passed |
| **Exit criteria** | Registry reflects the release baseline |
| **Authority** | Repository Maintainer |
| **Precedent** | Registry updates post-PG-02 and post-PAC-2 Standards |

---

## 4. Decision Gates

| Gate | Stage | Decision | Decision Vocabulary | Blocking? |
|---|---|---|---|---|
| **G1** | EI → SDR | Is the evidence complete and sufficient? | PASS / REVISE REQUIRED | ✅ Blocks SDR |
| **G2** | SDR → CAR | Is the scope confirmed? | PASS / DEFER / REASSIGN | ✅ Blocks CAR |
| **G3** | CAR → CMP | Is the architecture approved? | PASS / PASS WITH OBSERVATIONS / REVISE REQUIRED | ✅ Blocks CMP |
| **G4** | CMP → EAR | Is the migration plan approved? | PASS / PASS WITH OBSERVATIONS / REVISE REQUIRED | ✅ Blocks EAR |
| **G5** | EAR → ADR/IC | Is implementation authorized? | PASS / REVISE REQUIRED | ✅ Blocks implementation |
| **G6** | Validation → GR | Is validation passed? | PASS — ALL NON-CONFORMITIES RESOLVED / PASS WITH NON-CONFORMITIES / FAIL | ✅ Blocks GR |
| **G7** | GR → Registry | Is the release approved? | ACCEPTED / REJECTED | ✅ Blocks registry sync |

**All gates are blocking.** No stage may proceed without passing the preceding gate. A FAIL or REVISE REQUIRED at any gate returns the process to the appropriate previous stage per GS-03 §7 (Remediation Procedure).

---

## 5. Governance Roles

| Role | Responsibilities | Decision Rights | Approval Authority | Accountability |
|---|---|---|---|---|
| **Governance Sponsor** | Sets governance priorities, defines PG item scope, resolves scope conflicts | Approve scope decisions (G2), approve releases (G7) | Final authority on governance scope and releases | PAC-2 Charter objectives, PG item completion |
| **Governance Architect** | Conducts evidence investigations, capability architecture reviews, migration planning | Approve architecture decisions (G3, G4) | Final authority on capability boundaries and architecture | Architecture quality, capability coherence, long-term maintainability |
| **Governance Reviewer** | Conducts formal reviews (per GS-03): Scope Decision Review, Design Review, Validation | Issue PASS / REVISE REQUIRED / FAIL decisions (G1, G3, G4, G5, G6) | Review decisions per GS-03 | Review quality, evidence verification, design integrity |
| **Repository Maintainer** | Executes approved migrations, maintains registry, synchronizes baselines | Execute implementation per IC | No independent decision authority — implements approved plans only | Repository integrity, PAC-1 baseline preservation, registry accuracy |
| **Release Authority** | Assembles governance releases, verifies release readiness, declares baselines | Accept or reject releases (G7) | Final authority on release acceptance | Release completeness, baseline integrity |
| **Decision Authority** | Records formal governance decisions as ADRs | Create ADRs | Decision documentation per GS-01 and PG-04 | Decision traceability, rationale documentation |

### Role Assignment Constraints

| Constraint | Source |
|---|---|
| A reviewer must not be the sole author of the artifact under review | GS-03 §10 C2 |
| The Release Authority must not be the sole author of validation or implementation | Separation of duties |
| The Governance Sponsor may delegate scope decisions but not release acceptance | G7 is non-delegable |

---

## 6. Governance Artifact Classification

| Category | Artifacts | Stage | Lifecycle |
|---|---|---|---|
| **Architecture** | CAR, ADR | CAR → ADR | One-time per evolution cycle; immutable after acceptance |
| **Planning** | CMP, IC | CMP → EAR | One-time per evolution cycle; superseded by implementation |
| **Execution** | Repository Changes, Validation Report | Implementation → Validation | One-time; superseded by release |
| **Release** | GR, Release Manifest | GR | Per release; immutable baseline |
| **Operational** | Registries, Metrics, Standards | Ongoing | Continuously updated; versioned |

### Artifact Lifecycle

```
Architecture artifacts: draft → review → accepted → [immutable]
Planning artifacts:     draft → review → approved → implemented → [superseded]
Execution artifacts:    draft → review → approved → executed → [superseded by release]
Release artifacts:      draft → review → accepted → [immutable baseline]
Operational artifacts:  continuously maintained; versioned per GS-02 §5
```

---

## 7. Governance State Model

### 7.1 States

| State | Definition | Applies To |
|---|---|---|
| `draft` | Work in progress; not reviewed | All artifacts during creation |
| `under_review` | Under formal review per GS-03 | All artifacts during review stages |
| `approved` | Passed review but not yet operational | Architecture and planning artifacts |
| `operational` | In active use; governs current governance work | Standards, operating model, registries |
| `superseded` | Replaced by newer version; retained for history | Versioned artifacts |
| `deprecated` | No longer used; retained for traceability | Retired artifacts |
| `archived` | Moved to archive; minimal retention | Very old artifacts |
| `historical` | Accepted baseline; immutable by policy | PAC-1 and PAC-2 accepted baselines |
| `mapped` | Ownership transferred to successor via formal migration | Artifacts undergoing capability reassignment |
| `transitioning` | In migration; ownership changing | Artifacts during CMP execution |

### 7.2 State Transitions

```
draft ──→ under_review ──→ approved ──→ operational
  │              │              │              │
  │              │              │              ├──→ superseded ──→ deprecated ──→ archived
  │              │              │              │
  │              │              │              └──→ historical (immutable baseline)
  │              │              │
  │              │              └──→ mapped ──→ transitioning ──→ operational (under new owner)
  │              │
  │              └──→ draft (REVISE REQUIRED)
  │
  └──→ archived (abandoned draft)
```

### 7.3 Transition Rules

| From | To | Condition |
|---|---|---|
| `draft` | `under_review` | Artifact submitted for formal review |
| `under_review` | `approved` | Review decision: PASS or PASS WITH OBSERVATIONS |
| `under_review` | `draft` | Review decision: REVISE REQUIRED |
| `approved` | `operational` | Gate passed; artifact becomes active |
| `operational` | `superseded` | Newer version accepted (GS-02 §5) |
| `operational` | `historical` | Baseline declared immutable (PAC-1/PAC-2 Acceptance) |
| `operational` | `mapped` | Migration plan approved (CMP); ownership transferring |
| `mapped` | `transitioning` | Migration execution begins |
| `transitioning` | `operational` | Migration complete; new owner active |
| `superseded` | `deprecated` | No longer needed |
| `deprecated` | `archived` | Moved to archive |
| Any | `archived` | Explicit archival decision |

---

## 8. Governance Release Policy

### 8.1 Release Definition

A Governance Release (GR) is an immutable baseline that bundles completed governance work into a single accepted artifact. Each release:

- Corresponds to one PAC phase (PAC-1, PAC-2, PAC-3, ...)
- Contains all governance artifacts accepted during that phase
- Declares the operational capability baseline
- Is accepted through a formal Governance Acceptance record (GOV-REC-XXX)
- Is immutable after acceptance (P4: Historical Evidence Is Immutable)

### 8.2 Baseline Formation

| Step | Action |
|---|---|
| 1 | All PG items in the release scope complete WP-07 (Acceptance) |
| 2 | Validation confirms all non-conformities resolved (Gate G6) |
| 3 | Release Authority reviews release readiness |
| 4 | Governance Acceptance record produced (GOV-REC-XXX) |
| 5 | Release manifest published (list of all accepted artifacts) |
| 6 | Gate G7 passed |
| 7 | Registry synchronized |
| 8 | Baseline declared immutable |

### 8.3 Compatibility Policy

| Rule | Description |
|---|---|
| C1 | A release must not modify artifacts from a previous accepted release |
| C2 | A release may add new artifacts, register new objects, and update operational registries |
| C3 | A release may supersede operational artifacts (standards, registries) but may not supersede historical baselines |
| C4 | Breaking changes to governance standards require a new major release (PAC-N+1) with explicit migration |

### 8.4 Migration Policy

| Rule | Description |
|---|---|
| M1 | Capability migration follows CMP; no ad-hoc ownership changes |
| M2 | Migrated artifacts retain their GOV-ID; metadata is updated, not content |
| M3 | Migration is forward-only; artifacts are never "un-migrated" |

### 8.5 Rollback Policy

| Rule | Description |
|---|---|
| R1 | An accepted release cannot be rolled back — it is immutable |
| R2 | Errors in an accepted release are corrected through a subsequent PG item + new release |
| R3 | The registry records superseded/deprecated states for corrected artifacts |

### 8.6 Deprecation Policy

| Rule | Description |
|---|---|
| D1 | Deprecation requires a formal governance decision (ADR or PG item) |
| D2 | Deprecated artifacts retain their GOV-ID and remain in the registry |
| D3 | Consumers of a deprecated artifact are notified via `depends_on` staleness (GS-05 §6) |

---

## 9. Governance Metrics

### 9.1 Metrics Framework

| # | Metric | Definition | Target | Measurement |
|---|---|---|---|---|
| M1 | **Architecture Stability** | Number of CARs per release | Decreasing | Count CAR artifacts per PAC phase |
| M2 | **Capability Coverage** | % of capabilities with accepted ownership | 100% | Capabilities registered / capabilities identified |
| M3 | **Traceability Completeness** | % of objects with `primary_source` chain terminating at a baseline | 100% | Registry traversal |
| M4 | **Decision Lead Time** | Days from EI start to G7 passed | Decreasing | Timestamp delta per evolution cycle |
| M5 | **Migration Success Rate** | % of CMP artifacts migrated without rollback | 100% | Validated migrations / planned migrations |
| M6 | **Release Success Rate** | % of releases accepted on first submission | 100% | Accepted releases / submitted releases |
| M7 | **Review Pass Rate** | % of reviews passing on first submission | >80% | PASS / total reviews |
| M8 | **Registry Consistency** | % of registry entries matching artifact metadata | 100% | Automated diff between registry and artifacts |
| M9 | **Evidence Completeness** | % of findings with repository evidence references | 100% | Findings with references / total findings |

### 9.2 Metrics Governance

| Attribute | Policy |
|---|---|
| Measurement frequency | Per governance release (PAC-N acceptance) |
| Metric changes | Amendments follow GS-01 Amendment complexity |
| Metric retirement | Deprecated through ADR when no longer relevant |

---

## 10. GOM ↔ GS-01 Relationship

The GOM and GS-01 serve different governance layers:

| Layer | Model | Scope | When Used |
|---|---|---|---|
| **GOM** (this document) | 12-stage evolution lifecycle | Governance SYSTEM changes — capability reassignment, architecture evolution, release management | When governance itself needs to change: capability reallocation, standard evolution, release assembly |
| **GS-01** | 7-WP project lifecycle | Individual governance PROJECTS — PG items, new standards, policy creation | When executing a specific PG item or creating a new governance artifact |

### Interaction

```
GOM Stage: CAR → CMP → EAR → ADR
                            │
                            ▼
              PG Item created (or re-scoped)
                            │
                            ▼
              GS-01: WP-01 → WP-02 → ... → WP-07
                            │
                            ▼
              GOM Stage: Validation → GR → Registry
```

The GOM determines WHAT changes. GS-01 determines HOW each individual change is executed.

---

## 11. Governance Operating Guidelines

### 11.1 When to Use the GOM (vs GS-01 Only)

| Situation | Use |
|---|---|
| New PG item within existing capability model | GS-01 only |
| Capability ownership change (re-label, reclassify) | GOM EI → CAR → CMP → EAR, then GS-01 per PG |
| New standard proposal | GS-01 (Full complexity) |
| Architecture-level decision affecting multiple PGs | GOM full lifecycle |
| Release assembly | GOM GR stage |
| Scope conflict between PG items | GOM EI → SDR → CAR |

### 11.2 Minimum Artifact Requirements

| GOM Stage | Minimum Artifact |
|---|---|
| EI | Evidence Investigation document with GOV-ID |
| CAR | Capability Architecture Review document with GOV-ID |
| CMP | Capability Migration Plan document with GOV-ID |
| EAR | Evolution Approval document with GOV-ID |
| ADR | ADR entry in governance registry |
| IC | Implementation Contract (may be section in CMP) |
| GR | Governance Acceptance record with GOV-ID |

### 11.3 Governance Release Cadence

| Rule | Description |
|---|---|
| No minimum cadence | Releases are capability-driven, not calendar-driven |
| PAC-2 release | When all P0 and P1 PG items are complete |
| PAC-3 release | When next set of governance objectives is achieved |
| Release scope | Declared at PAC-N Charter; may be amended via GOM |

---

## 12. Constraints

| # | Constraint |
|---|---|
| C1 | The GOM does not replace GS-01 — it operates above it for system-level governance evolution |
| C2 | The GOM does not modify PAC-1 or PAC-2 accepted baselines |
| C3 | All GOM stages produce governance artifacts with GOV-IDs |
| C4 | GOM decisions are traceable through GS-05 relationship model |
| C5 | The GOM is itself governed by the GOM — future GOM evolution follows the GOM lifecycle |

---

## 13. Evidence References

| Precedent | Source | What It Proves |
|---|---|---|
| EI precedent | `GOV-REV-014` (PG-01 Investigation) | Evidence Investigation stage: findings, root cause, status determination |
| CAR precedent | `GOV-REV-015` (CAR-001) | Capability Architecture Review: 6 phases, objectives → project mapping |
| CMP precedent | `GOV-REV-016` (CMP-001) | Capability Migration Plan: 8 phases, migration matrix, decision options |
| GR precedent | `GOV-REC-008` (PAC-2 Standards Acceptance) | Governance Release: acceptance decision, capability status, project status |
| GS-01 | `GOV-GUIDE-003` | 7-WP lifecycle for individual PG items |
| GS-03 | `GOV-GUIDE-005` | Review types, severity, decisions used in GOM gates |
| GS-05 | `GOV-GUIDE-006` | Traceability model for GOM artifact chains |

---

**This Governance Operating Model governs all future PAC-2 governance evolution.**
