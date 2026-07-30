# Capability Migration Plan — CMP-001

| id | type | status | version | date |
|---|---|---|---|---|
| `GOV-REV-016` | `REV` | `accepted` | `1.0` | `2026-07-29` |

| source | part_of |
|---|---|
| `GOV-REV-015` (CAR-001) | PAC-2 Architecture |

---

**Date**: 2026-07-29 | **Type**: Capability Migration Plan | **Source**: CAR-001 (`GOV-REV-015`)

---

## Phase 1 — Current State Baseline

### Governance Artifact Inventory

| # | Artifact | GOV-ID | Type | Current PG Owner | Current Capability | Lifecycle Status | Evidence |
|---|---|---|---|---|---|---|---|
| A1 | `PG01_Current_State_Assessment.md` | `GOV-REV-005` | `REV` | PG-01 | Versioning (mislabeled) | WP-01 complete | Registry, file metadata |
| A2 | `PG01_Lifecycle_Status_Investigation.md` | `GOV-REV-014` | `REV` | PG-01 | Investigation (PG-01 status) | Investigation complete | Registry (not registered) |
| A3 | `PG02_Current_State_Assessment.md` | `GOV-REV-006` | `REV` | PG-02 | Governance Object Index | WP-01 complete | Registry |
| A4 | `PG02_Assessment_Review.md` | `GOV-REV-007` | `REV` | PG-02 | Governance Object Index | WP-02 complete | Registry |
| A5 | `Governance_Object_Index_Framework.md` | `GOV-REF-003` | `REF` | PG-02 | Governance Object Index | WP-03 complete | Registry |
| A6 | `PG02_Design_Review.md` | `GOV-REV-008` | `REV` | PG-02 | Governance Object Index | WP-04 complete | Registry |
| A7 | `Governance_Object_Registry.md` | `GOV-REF-006` | `REF` | PG-02 | Registry | WP-05 complete | Registry |
| A8 | `PG02_Validation_Report.md` | `GOV-REV-009` | `REV` | PG-02 | Governance Object Index | WP-06 complete | Registry |
| A9 | `Governance_Acceptance_PG02.md` | `GOV-REC-007` | `REC` | PG-02 | Governance Object Index | WP-07 complete (ACCEPTED) | Registry |
| A10 | `PAC2_Standards_Assessment.md` | `GOV-REV-010` | `REV` | PAC-2 Standards | Standards | WP-01 complete | Registry |
| A11 | `PAC2_Standards_Assessment_Review.md` | `GOV-REV-011` | `REV` | PAC-2 Standards | Standards | WP-02 complete | Registry |
| A12 | `Governance_Standards_Framework.md` | `GOV-REF-007` | `REF` | PAC-2 Standards | Standards | WP-03 complete | Registry |
| A13 | `PAC2_Standards_Design_Review.md` | `GOV-REV-012` | `REV` | PAC-2 Standards | Standards | WP-04 complete | Registry |
| A14–A18 | 5 standards docs (GS-01 through GS-05) | `GOV-GUIDE-003`–`007` | `GUIDE` | PAC-2 Standards | Standards | WP-05 complete | Registry |
| A19 | `PAC2_Standards_Validation_Report.md` | `GOV-REV-013` | `REV` | PAC-2 Standards | Standards | WP-06 complete | Registry |
| A20 | `Governance_Acceptance_PAC2_Standards.md` | `GOV-REC-008` | `REC` | PAC-2 Standards | Standards | WP-07 complete (ACCEPTED) | Registry |
| A21 | *(No artifacts)* | — | — | PG-05 | Versioning | Not started | Absence of PG-05 files |
| A22 | *(No artifacts)* | — | — | PG-08 | AGENTS.md rule | Not started | Absence of PG-08 files |
| A23 | *(No artifacts)* | — | — | PG-09 | CHANGELOG | Not started | Absence of PG-09 files |

### Current PG Ownership Summary

| PG | Current Capability | Artifacts | Status |
|---|---|---|---|
| PG-01 | Versioning (de facto via assessment label) | 2 | WP-01 only; remainder pending |
| PG-02 | Governance Object Index | 7 | ✅ COMPLETED (ACCEPTED) |
| PG-05 | *(none — no artifacts)* | 0 | Not started |
| PG-08 | *(none — no artifacts)* | 0 | Not started |
| PG-09 | *(none — no artifacts)* | 0 | Not started |
| PAC-2 Standards | Standards | 11 | ✅ COMPLETED (ACCEPTED) |

---

## Phase 2 — Target Capability Architecture

### Capability Ownership Model (CAR-001 Approved)

| Capability | Target Owner | Complexity | Priority | Rationale |
|---|---|---|---|---|
| **C2: Versioning** | **PG-05** | Full (7 WPs) | P0 | Foundational — all dependent capabilities require it. Single owner eliminates PG-01/PG-05 scope conflict. |
| **C1: Project Identity** | **PG-01** | Decision (4 WPs) | P1 | One-time decision — is Rule IDE a rename, subsystem, or milestone category? Produces one ADR, not ongoing governance. |
| C3: Architecture Docs | PG-03 | Document | P1 | Unchanged |
| C4: Decision Records | PG-04 | Document | P1 | Unchanged |
| C5: AI Documentation | PG-06 | Document | P0 | Unchanged |
| C6: Milestone Planning | PG-07 | Document | P0 | Unchanged |
| C7: Documentation Standards | **PG-08** (merged PG-08 + PG-09) | Amendment | P3 | Both are minor, independent, single-commit fixes |
| C8: Document Lifecycle | PG-10 | Document | P2 | Unchanged |
| C9: Registry | PG-02 | — | — | ✅ COMPLETED |
| C10: Review / Standards | PAC-2 Standards | — | — | ✅ COMPLETED |

### Ownership Distinction

| PG | Historical Owner (PAC-1) | Current Owner (de facto) | Target Owner (CAR-001) |
|---|---|---|---|
| PG-01 | Rule IDE definition | Governance Versioning | **Project Identity** (Decision/ADR) |
| PG-05 | Versioning policy | *(unclaimed — no artifacts)* | **Versioning** (Full, 7 WPs) |
| PG-08 | AGENTS.md add_suffix | *(unclaimed)* | **Documentation Standards** (merged) |
| PG-09 | CHANGELOG clarification | *(unclaimed)* | *(merged into PG-08)* |

---

## Phase 3 — Capability Migration Matrix

### Affected Artifacts

| # | Artifact | GOV-ID | Historical Owner | Current Capability | → Future Owner | Future Capability | Migration Method | Effective Point | Traceability Method |
|---|---|---|---|---|---|---|---|---|---|
| A1 | `PG01_Current_State_Assessment.md` | `GOV-REV-005` | PG-01 | Versioning | **PG-05** | Versioning | **Forward Assignment** | WP-02 start | `primary_source: GOV-REV-005` in PG-05 artifacts; `updates` records transition |
| A2 | `PG01_Lifecycle_Status_Investigation.md` | `GOV-REV-014` | PG-01 | Investigation | **N/A** | N/A | **No Action** | — | Investigation is evidence; no ownership migration needed |
| A3–A9 | All PG-02 artifacts | `GOV-REV-006`–`009`, `GOV-REF-003`,`006`, `GOV-REC-007` | PG-02 | Governance Object Index | PG-02 | Governance Object Index | **No Action** | — | PG-02 is completed; immutable |
| A10–A20 | All PAC-2 Standards artifacts | `GOV-REV-010`–`013`, `GOV-REF-007`, `GOV-GUIDE-003`–`007`, `GOV-REC-008` | PAC-2 Standards | Standards | PAC-2 Standards | Standards | **No Action** | — | PAC-2 Standards is completed; immutable |
| — | *(Future PG-05 WP-01)* | *(new)* | — | — | PG-05 | Versioning | **Forward Assignment** | PG-05 WP-02 | References `GOV-REV-005` as predecessor assessment |
| — | *(Future PG-01 ADR)* | *(new)* | — | — | PG-01 | Project Identity | **Forward Assignment** | PG-01 WP-03 | New ADR references PAC-2 Charter PG-01 definition |
| — | *(Future PG-08)* | *(new)* | — | — | PG-08 | Doc Standards | **Forward Assignment** | PG-08 WP-03 | Combined scope from PG-08 and PG-09 PAC-1 definitions |

### Migration Methods Used

| Method | Applied To | Definition |
|---|---|---|
| **No Action** | A2, A3–A9, A10–A20 | Artifact requires no change — completed, immutable, or unaffected |
| **Forward Assignment** | A1 | Artifact's metadata `part_of` field is updated to reflect target owner; content is unchanged |
| **Reference Mapping** | Future artifacts | New artifacts declare predecessor relationship via `primary_source` or `references` |

---

## Phase 4 — Traceability Preservation

### Historical Evidence Chain

```
PAC-1 Governance Resolution (GOV-GOV-002)
    │
    ├── PG-01 defined: "Rule IDE scope"
    │       │
    │       ├── PAC-2 Charter: PG-01 = Rule IDE (P1)    [preserved]
    │       ├── GOV-REV-005 (PG-01 Assessment)           [re-labeled → PG-05]
    │       ├── GOV-REV-014 (PG-01 Investigation)        [preserved as evidence]
    │       └── Future: PG-01 ADR (Project Identity)     [new, references Charter]
    │
    ├── PG-05 defined: "Versioning policy"
    │       │
    │       ├── PAC-2 Charter: PG-05 = Versioning (P0)   [preserved]
    │       ├── GOV-REV-005 → re-labeled to PG-05        [forward assignment]
    │       └── Future: PG-05 WP-02 through WP-07        [new, references GOV-REV-005]
    │
    └── PG-08 + PG-09 defined: "add_suffix" + "CHANGELOG"
            │
            └── Future: PG-08 = Documentation Standards  [merged scope]
```

### Legacy Reference Handling

| Legacy Reference | Where It Appears | Handling |
|---|---|---|
| "PG-01 Assessment" in registry, CAR-001, CMP-001 | Registry entry for `GOV-REV-005` | Registry `part_of` updated to PG-05; historical reference in CAR-001/CMP-001 documents the transition |
| "PG-01 Current State Assessment" in filename | Filesystem | Filename preserved (PG01 prefix is a review work product convention per GS-04 §3.3); new PG-05 artifacts use PG05 prefix |
| "PG-01 WP-01" in document title | `PG01_Current_State_Assessment.md` content | Title updated to reflect PG-05 ownership; change documented in revision history |

### Registry Continuity

| Action | Rationale |
|---|---|
| `GOV-REV-005` `part_of` updated: PG-01 → PG-05 | Registry reflects actual capability ownership |
| `GOV-REV-014` registered: `part_of: PG-01` | Investigation was about PG-01 status; correctly assigned |
| `GOV-REV-005` `primary_source` remains PAC-2 Charter | Evidence chain unbroken — assessment was authorized by PAC-2 Charter regardless of label |
| New PG-05 artifacts reference `GOV-REV-005` via `predecessor` | Explicit successor relationship |

**No historical evidence chain is broken.**

---

## Phase 5 — Governance Decision Requirements

| # | Decision | Authority | Review Required | Approval | Output |
|---|---|---|---|---|---|
| D1 | **Capability Ownership**: PG-05 owns Versioning; PG-01 owns Identity (ADR) | PAC-2 Steering | WP-04 Design Review | CAR-001 + CMP-001 acceptance | Decision recorded in Decision Registry; PG-01 and PG-05 updated in PAC-2 Charter |
| D2 | **PG-01 Reclassification**: PG-01 changed from Full complexity to Decision complexity | PAC-2 Steering | WP-04 Design Review | GS-01 §3 complexity selection | Updated PG-01 scope document (WP-03) |
| D3 | **PG-08/PG-09 Merger**: PG-08 absorbs PG-09 scope; PG-09 retired | PAC-2 Steering | WP-04 Design Review | Documented in PAC-2 Charter amendment | PG-08 combined scope document |
| D4 | **GOV-REV-005 Re-label**: Metadata `part_of` from PG-01 to PG-05 | Registry Maintainer | WP-04 Design Review | Per GS-04 R2 (immutable identifiers; metadata is mutable) | Registry update commit |
| D5 | **Retire PG-09**: Remove PG-09 from active PG item list | PAC-2 Steering | WP-07 Acceptance | Acceptance record | PG-09 marked as merged/retired in registry |
| D6 | **CMP-001 Acceptance**: Approve migration plan | PAC-2 Steering | WP-07 Acceptance | Acceptance record | `GOV-REC-009` or equivalent |

---

## Phase 6 — Implementation Roadmap

### Stage 1: Architecture Approval

| Step | Action | Deliverable | Prerequisite |
|---|---|---|---|
| S1.1 | CAR-001 reviewed and accepted | CAR-001 Acceptance | — |
| S1.2 | CMP-001 reviewed and accepted | CMP-001 Acceptance | S1.1 |
| S1.3 | PAC-2 Charter amended (PG-01 scope, PG-05 ownership, PG-08/09 merger) | Charter amendment or ADR | S1.2 |

### Stage 2: Decision Approval

| Step | Action | Deliverable | Prerequisite |
|---|---|---|---|
| S2.1 | D1 approved: PG-05 owns Versioning | Decision Registry entry | S1.3 |
| S2.2 | D2 approved: PG-01 reclassified as Decision complexity | Decision Registry entry | S1.3 |
| S2.3 | D3 approved: PG-08/PG-09 merger | Decision Registry entry | S1.3 |

### Stage 3: Repository Updates

| Step | Action | Affected Artifact | Prerequisite |
|---|---|---|---|
| S3.1 | Re-label `GOV-REV-005` metadata: `part_of: PG-01` → `part_of: PG-05` | `PG01_Current_State_Assessment.md` | S2.1 |
| S3.2 | Update `GOV-REV-005` title to reflect PG-05 ownership | `PG01_Current_State_Assessment.md` | S2.1 |
| S3.3 | Register `GOV-REV-014` (investigation) in registry | `Governance_Object_Registry.md` | S2.1 |
| S3.4 | Begin PG-05 WP-02 (Assessment Review) | New `PG05_Assessment_Review.md` | S3.1 |

### Stage 4: Registry Synchronization

| Step | Action | Affected Registry Entry | Prerequisite |
|---|---|---|---|
| S4.1 | Update `GOV-REV-005` `part_of` → PG-05 | Registry row | S3.1 |
| S4.2 | Add `GOV-REV-014` registration | Registry new row | S3.3 |
| S4.3 | Update statistics (PG-01: 1 artifact, PG-05: 1 artifact) | Registry stats | S4.1, S4.2 |
| S4.4 | Mark PG-09 as merged/retired (when PG-08 completes) | Registry | S2.3 |

### Stage 5: Release Integration

| Step | Action | Deliverable | Prerequisite |
|---|---|---|---|
| S5.1 | PG-05 completed (WP-02 through WP-07) | VERSIONING.md, PG-05 Acceptance | S4.4 |
| S5.2 | PAC-2 Governance Release assembled | PAC-2 Acceptance Record | All P1 PG items complete |
| S5.3 | CAR-001 + CMP-001 included in release evidence | Release manifest | S5.2 |

---

## Phase 7 — Risk Assessment

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R1 | **Traceability loss**: Re-labeling `GOV-REV-005` breaks references to "PG-01 Assessment" | Low | Medium | Registry entry and `PG01_` filename preserved; historical references documented in CAR-001/CMP-001. The `PG01_` prefix in the filename is a review work product convention (GS-04 §3.3), not a capability declaration. |
| R2 | **Capability ambiguity**: PG-01 still perceived as versioning after re-label | Medium | High | PG-01 WP-03 (Identity ADR) explicitly addresses the scope change. PG-01's new ADR references PAC-2 Charter original definition. |
| R3 | **Duplicate ownership**: PG-05 WP-01 and PG-01 Assessment both reference versioning after migration | Low | Low | After re-label, PG-01 has no versioning scope. PG-05 has exactly one WP-01 artifact. |
| R4 | **Repository inconsistency**: Registry shows PG-01 with 1 artifact and PG-05 with 1 artifact, but filenames still show PG01 prefix | Low | Low | GS-04 §3.3 explicitly allows `PG{NN}_` prefix as review work product convention. The prefix identifies the review, not the capability. Documented in migration plan. |
| R5 | **Backward compatibility**: PAC-1 and PAC-2 Charter reference "PG-01 = Rule IDE" — reclassification creates confusion if PG-01 is now Identity (ADR) | Low | Low | PG-01's target scope (Identity) is the SAME scope as PAC-1's original definition (Rule IDE). The reclassification is from Versioning (incorrect) BACK to Identity (correct). The PAC-2 Charter's PG-01 definition is the historical truth — the migration restores it. |
| R6 | **Governance confusion**: Stakeholders don't understand why PG-01 was reclassified | Medium | Medium | CAR-001 documents the architectural reasoning. CMP-001 documents the migration path. Both are reviewable governance documents. |

---

## Phase 8 — Decision Options

### Option A: Historical Preservation with Capability Reassignment (RECOMMENDED)

| Aspect | Assessment |
|---|---|
| **Description** | Re-label `GOV-REV-005` to PG-05; PG-01 becomes Decision complexity for Identity; PG-08/09 merged. Historical filenames preserved. |
| **Governance impact** | Low — 1 metadata field change, 1 PG reclassification, 2 PGs merged |
| **Repository impact** | Minimal — 1 file metadata edit, registry update |
| **Traceability** | Preserved — `GOV-REV-005` keeps its GOV-ID, file location, and relationship to PAC-2 Charter |
| **Long-term maintainability** | High — single owner per capability, no scope overlap |
| **Implementation effort** | Low — 1 metadata edit + registry sync |
| **Risk** | Low — all risks have mitigation |

### Option B: Historical Renumbering

| Aspect | Assessment |
|---|---|
| **Description** | Rename `PG01_Current_State_Assessment.md` to `PG05_Current_State_Assessment.md`; assign new GOV-ID; deprecate old GOV-ID. |
| **Governance impact** | Medium — breaks filename convention, creates deprecated GOV-ID, requires new GOV-ID assignment |
| **Repository impact** | Medium — file rename, registry update, deprecation entry |
| **Traceability** | ⚠️ Weakened — `GOV-REV-005` becomes a deprecated pointer to a new GOV-ID |
| **Long-term maintainability** | Lower — introduces a deprecated record for what is effectively the same assessment |
| **Implementation effort** | Medium — rename + re-register + deprecation |
| **Risk** | Medium — unnecessary complexity |

### Option C: Legacy Mapping with Forward Ownership

| Aspect | Assessment |
|---|---|
| **Description** | Keep `GOV-REV-005` under PG-01; PG-05 starts fresh with no WP-01; PG-05 references PG-01 assessment as external input. |
| **Governance impact** | Medium — PG-01 still "owns" a versioning assessment permanently |
| **Repository impact** | Low — no changes |
| **Traceability** | ⚠️ Confusing — PG-01 owns versioning assessment but PG-05 owns versioning |
| **Long-term maintainability** | Lower — permanent capability overlap between PG-01 and PG-05 |
| **Implementation effort** | Lowest — nothing changes |
| **Risk** | High — perpetuates the scope error CAR-001 identified |

### Option D: No Migration

| Aspect | Assessment |
|---|---|
| **Description** | Do nothing. PG-01 and PG-05 both remain as versioning projects. |
| **Governance impact** | High — permanent scope conflict |
| **Repository impact** | None |
| **Traceability** | Broken — two projects claiming the same capability |
| **Long-term maintainability** | Lowest — conflict must be resolved eventually |
| **Implementation effort** | None — but deferred cost is higher |
| **Risk** | Highest — violates CAR-001 findings, GS-01 lifecycle, and capability ownership clarity |

### Comparison Matrix

| Criterion | Option A | Option B | Option C | Option D |
|---|---|---|---|---|
| Clear capability ownership | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐ |
| Low coupling | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐ |
| High cohesion | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐ |
| Traceability preservation | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐ |
| Long-term maintainability | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐ |
| Implementation effort | ⭐⭐⭐ (low) | ⭐⭐ (medium) | ⭐⭐⭐ (none) | ⭐⭐⭐ (none) |
| Risk minimization | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐ |

---

## Final Recommendation

```
Option A: Historical Preservation with Capability Reassignment
```

**Rationale**: Option A achieves all CAR-001 architectural goals — clear ownership, no scope overlap, single owner per capability — with minimal repository change (1 metadata field, 1 registry update). It preserves all historical evidence. The `PG01_` filename prefix is a review work product convention per GS-04 §3.3, not a capability declaration. The assessment content is versioning; it belongs to PG-05.

### Migration Summary

| What Changes | What Doesn't Change |
|---|---|
| `GOV-REV-005` `part_of`: PG-01 → PG-05 | `GOV-REV-005` filename, GOV-ID, content, file location |
| PG-01 scope: Versioning → Identity (ADR) | PG-01 PG number, PAC-1 definition, PAC-2 Charter reference |
| PG-05: starts at WP-02 (WP-01 = re-labeled assessment) | PG-05 PG number, PAC-1 definition, PAC-2 Charter priority (P0) |
| PG-08 scope: + CHANGELOG (merged from PG-09) | PG-08 PG number |
| PG-09: retired (merged into PG-08) | PG-09 PAC-1 definition (preserved in PG-08 scope document) |

### Post-Migration Architecture

```
PAC-2 Governance Projects (Post-CMP-001)

PG-01: Project Identity [Decision, P1]
    └─ Scope: RULE_IDE_SCOPE.md or ADR-nnn

PG-02: Governance Object Index [COMPLETED]
    └─ 7 artifacts, immutable

PG-03: Architecture Documentation [Document, P1]
PG-04: Decision Records [Document, P1]
PG-05: Versioning [Full, P0]
    └─ WP-01: GOV-REV-005 (re-labeled)
    └─ WP-02 onward: new
PG-06: AI Documentation [Document, P0]
PG-07: Milestone Planning [Document, P0]
PG-08: Documentation Standards [Amendment, P3]
    └─ Combined scope: AGENTS.md + CHANGELOG_AI.md
PG-09: [RETIRED — merged into PG-08]
PG-10: Document Lifecycle [Document, P2]

PAC-2 Standards Layer [COMPLETED]
    └─ GS-01 through GS-05 operational
```

**Migration plan complete. Awaiting Stage 1: Architecture Approval.**
