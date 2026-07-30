# GS-01: PAC-2 Governance Standard v1.0-draft

| id | type | status | version | date |
|---|---|---|---|---|
| `GOV-GUIDE-003` | `GUIDE` | `accepted` | `1.0` | `2026-07-29` |

| source | part_of |
|---|---|
| `GOV-REF-007` (Standards Framework) | PAC-2 Standards |

---

## 1. Purpose

Define the standard lifecycle for conducting governance work under PAC-2. This standard codifies the 7-Work-Package (7-WP) process proven in PG-02 and establishes it as the canonical workflow for all governance projects, including the creation of this standard and all subsequent PG items.

---

## 1.1 Standard Precedence

This standard (GS-01) is the root governance standard. All other governance standards (GS-02 through GS-05) define compliance requirements within the lifecycle this standard defines. In any conflict between GS-01 and another standard, GS-01 takes precedence.

---

## 2. The 7-WP Lifecycle

Every governance project conducts 7 sequential Work Packages. Each WP has a defined purpose, deliverable, review mechanism, and exit criterion.

| WP | Phase | Purpose | Produces | Reviewed By |
|---|---|---|---|---|
| **WP-01** | Current State Assessment | Establish factual baseline — what exists, what's broken, what's implicit | Assessment document enumerating findings, gaps, risks | WP-02 (Assessment Review) |
| **WP-02** | Assessment Review | Validate assessment completeness, accuracy, and readiness | Review document with PASS / PASS WITH OBSERVATIONS / REVISE REQUIRED decision | — (decision is final) |
| **WP-03** | Framework Design | Define the solution specification | Design document (framework, policy, or standard) | WP-04 (Design Review) |
| **WP-04** | Design Review | Validate design against assessment baseline | Review document with decision | — (decision is final) |
| **WP-05** | Implementation | Apply the approved design to the repository | Implemented artifacts (registry, documents, scripts) | WP-06 (Validation) |
| **WP-06** | Validation | Verify implementation conformance to design | Validation report with PASS / PASS WITH NON-CONFORMITIES / FAIL decision | — (decision is final) |
| **WP-07** | Acceptance | Formal closure; confirm all deliverables and success criteria | Acceptance record with ACCEPTED / REJECTED decision | — (decision is final) |

---

## 2.1 WP-01: Current State Assessment

**Purpose**: Establish the factual baseline before any design or implementation.

**Required contents**:
- Scope statement — what is assessed, what is excluded
- Evidence for every claim — file references, line counts, commit hashes
- Findings table — what is wrong, missing, or inconsistent
- Gaps table — what is needed but absent
- Risks table — what could go wrong, with likelihood

**Format**: Assessment document stored in `docs/governance/reviews/`. Title format: `{Scope}_Current_State_Assessment.md`.

**Exit criterion**: All claims are evidence-supported. Scope covers the entire project. No design proposals appear in the assessment.

---

## 2.2 WP-02: Assessment Review

**Purpose**: Validate that WP-01 is complete and accurate before design begins.

**Review criteria**:
- **Completeness**: All relevant artifacts assessed? All claims supported?
- **Consistency**: No internal contradictions in findings?
- **Evidence**: Every claim traceable to a repository artifact?
- **Readiness**: Sufficient baseline for WP-03 design?

**Decision vocabulary**: `PASS`, `PASS WITH OBSERVATIONS`, `REVISE REQUIRED`.

**REVISE REQUIRED procedure**: The assessment is returned to WP-01. The reviewer must specify which finding, gap, or claim requires revision. The revised assessment is resubmitted for a second WP-02 review. No design work (WP-03) begins until WP-02 is PASS or PASS WITH OBSERVATIONS.

**Format**: Review document stored in `docs/governance/reviews/`. Title format: `{Scope}_Assessment_Review.md`.

---

## 2.3 WP-03: Framework Design

**Purpose**: Define the solution specification that WP-05 will implement.

**Required contents**:
- Design principles — what guides the design
- Component specification — what the solution contains
- Integration points — how it connects to existing systems
- Design decisions — what was chosen and why
- Constraints — what the design does NOT do
- Exit criteria — what must be true for the design to be complete

**Exit criterion**: The design addresses all findings and gaps from WP-01. The design defines everything WP-05 needs to implement. No implementation decisions remain unspecified.

---

## 2.4 WP-04: Design Review

**Purpose**: Validate that WP-03 is complete, consistent, and aligned with the assessment baseline.

**Review criteria**:
- **Completeness**: All components present and substantive?
- **Consistency**: No internal contradictions?
- **Alignment**: All assessment findings resolved?
- **Integration**: Compatible with existing baselines?
- **Rationale**: All decisions justified?
- **Traceability**: Design elements traceable to requirements?
- **Boundary**: No implementation leakage?

**Decision vocabulary**: `PASS`, `PASS WITH OBSERVATIONS`, `REVISE REQUIRED`.

**REVISE REQUIRED procedure**: Same as WP-02 — return to WP-03 with specific revision requirements. No implementation begins until WP-04 is PASS or PASS WITH OBSERVATIONS.

**Format**: Review document in `docs/governance/reviews/`. Title format: `{Scope}_Design_Review.md`.

---

## 2.5 WP-05: Implementation

**Purpose**: Apply the approved design to the repository.

**Scope**: Exactly what WP-03 specifies. No additions, no redesign.

**Required**: Each implementation commit references WP-03 design decisions. Each deliverable is traceable to a design element.

**Exit criterion**: The repository state matches the approved design. No unapproved artifacts are added. No accepted baselines are modified.

---

## 2.6 WP-06: Validation

**Purpose**: Verify that WP-05 conforms to the approved design.

**Validation criteria** (derived from design):
- Completeness — all design components implemented?
- Correctness — does each implementation element match the design?
- Consistency — no contradictions in implementation?
- Integrity — existing baselines preserved?

**Decision vocabulary**: `PASS — ALL NON-CONFORMITIES RESOLVED`, `PASS WITH NON-CONFORMITIES`, `FAIL`.

**PASS WITH NON-CONFORMITIES procedure**: Non-conformities are documented with severity. Each must be resolved or formally deferred before WP-07.

**FAIL procedure**: The implementation is returned to WP-05. The validation report must specify every non-conformity. All must be resolved before WP-06 retesting.

**Format**: Validation report in `docs/governance/reviews/`. Title format: `{Scope}_Validation_Report.md`.

---

## 2.7 WP-07: Acceptance

**Purpose**: Formally close the governance project and establish operational baseline.

**Required contents**:
- Acceptance decision (ACCEPTED / REJECTED)
- Work package completion table (WP-01 through WP-07 with commit hashes)
- Success criteria verification
- Deliverables inventory
- Defect history (if any)
- Baseline declaration — which artifacts are now accepted

**Exit criterion**: All WPs complete. All review decisions are PASS or PASS WITH OBSERVATIONS. All validation non-conformities resolved. PAC-1 baseline intact.

**Format**: Acceptance document in `docs/governance/`. Title format: `Governance_Acceptance_{Scope}.md`.

---

## 3. Complexity-Based WP Selection

Not all governance projects require all 7 WPs. The lifecycle adapts to project complexity:

| Complexity | Example | Required WPs |
|---|---|---|
| **Full** | New policy, new framework, new standard | All 7 (WP-01 → WP-07) |
| **Document** | Single document update, ADR | WP-03 (lightweight design) → WP-04 (review) → WP-05 (implementation) → WP-07 (acceptance) |
| **Amendment** | Correction, clarification, minor update | WP-03 (design note) → WP-05 (implementation) → WP-07 (acceptance record) |

**Rule**: A WP may only be skipped if its purpose is demonstrably unnecessary. WP-05 and WP-07 are never skipped. The decision to skip a WP must be documented in WP-03.

---

## 4. Evidence References

| Precedent | Source | What It Proves |
|---|---|---|
| PG-02 WP-01 | `PG02_Current_State_Assessment.md` (`GOV-REV-006`) | Assessment format: findings, gaps, risks, evidence |
| PG-02 WP-02 | `PG02_Assessment_Review.md` (`GOV-REV-007`) | Review criteria: completeness, consistency, evidence |
| PG-02 WP-03 | `Governance_Object_Index_Framework.md` (`GOV-REF-003`) | Design format: principles, specifications, decisions, constraints |
| PG-02 WP-04 | `PG02_Design_Review.md` (`GOV-REV-008`) | Design review criteria: 7 dimensions |
| PG-02 WP-05 | Commits `2f62d9a` → `54a7b5d` | Implementation: registry + metadata headers |
| PG-02 WP-06 | `PG02_Validation_Report.md` (`GOV-REV-009`) | Validation criteria: 6 dimensions, defect tracking |
| PG-02 WP-07 | `Governance_Acceptance_PG02.md` (`GOV-REC-007`) | Acceptance: WP table, success criteria, baseline declaration |

---

## 5. Compliance

This standard applies to all governance work initiated under PAC-2, including:
- Remaining PG items (PG-01, PG-03 through PG-10)
- Creation of GS-02 through GS-05
- Any new governance project initiated before PAC-2 closure

Non-compliance: A governance project that skips a required WP without documented justification is not accepted per this standard.

---

## 6. Constraints

| # | Constraint |
|---|---|
| C1 | This standard defines process, not policy outcomes |
| C2 | WP-05 must never modify PAC-1 Accepted v1.0 documents without explicit authorization |
| C3 | Review decisions WP-02, WP-04, WP-06 are final when issued; appeals require a new PG item |
| C4 | The 7-WP lifecycle is linear; concurrent work on multiple WPs within one project is not permitted |
