# GS-03: Governance Review Standard v1.0-draft

| id | type | status | version | date |
|---|---|---|---|---|
| `GOV-GUIDE-005` | `GUIDE` | `accepted` | `1.0` | `2026-07-29` |

| source | part_of |
|---|---|
| `GOV-REF-007` (Standards Framework) | PAC-2 Standards |

---

## 1. Purpose

Define the standard review process for governance documents. This standard codifies the 3 review types demonstrated in PG-02 — Assessment Review, Design Review, and Validation — and establishes the unified severity taxonomy, decision vocabulary, and remediation procedures.

---

## 2. Review Types

| # | Review Type | WP | Reviews | Decision Vocabulary |
|---|---|---|---|---|
| R1 | **Assessment Review** | WP-02 | Current State Assessment | `PASS`, `PASS WITH OBSERVATIONS`, `REVISE REQUIRED` |
| R2 | **Design Review** | WP-04 | Framework Design, Policy Design, Standard Design | `PASS`, `PASS WITH OBSERVATIONS`, `REVISE REQUIRED` |
| R3 | **Validation** | WP-06 | Implementation | `PASS — ALL NON-CONFORMITIES RESOLVED`, `PASS WITH NON-CONFORMITIES`, `FAIL` |

---

## 3. Assessment Review (R1 — WP-02)

### 3.1 Criteria

| Dimension | Question |
|---|---|
| **Completeness** | Are all relevant artifacts assessed? Is every claim supported by evidence? |
| **Consistency** | Do findings contradict each other? Are counts and statistics internally consistent? |
| **Evidence** | Is every finding traceable to a specific repository artifact? Are claims verifiable? |
| **Readiness** | Does the assessment provide sufficient baseline for design (WP-03)? |

### 3.2 Output

A review document containing:
- Verification of each criterion
- Observations (if any)
- Formal decision

### 3.3 Observation Severity

| Severity | Definition | Example |
|---|---|---|
| **LOW** | Minor finding; does not affect assessment validity | Typo, formatting inconsistency, minor omission |
| **MEDIUM** | Significant finding; does not block design but should be addressed | Missing edge case, incomplete scope, imprecise claim |
| **HIGH** | Blocking finding; assessment cannot proceed to design without resolution | Unsupported claim, scope omission affecting design, factual error |

---

## 4. Design Review (R2 — WP-04)

### 4.1 Criteria

| Dimension | Question |
|---|---|
| **Completeness** | All design components present and substantive? |
| **Consistency** | Internal consistency — no contradictions, miscounts, format errors? |
| **Alignment** | All assessment findings and gaps resolved? |
| **Integration** | Compatible with existing accepted baselines? |
| **Rationale** | All design decisions have explicit justification? |
| **Traceability** | Design elements traceable to assessment requirements? |
| **Boundary** | Design is a specification, not an implementation? No implementation leakage? |

### 4.2 Output

A review document containing:
- Verification of all 7 dimensions
- Finding-by-finding traceability to assessment
- Observations (if any)
- Formal decision

### 4.3 Observation Severity

Same 3-level taxonomy as §3.3. HIGH observations block WP-05 implementation.

---

## 5. Validation (R3 — WP-06)

### 5.1 Criteria

| Dimension | Question |
|---|---|
| **Completeness** | All design components implemented? |
| **Correctness** | Does each implementation element match the design specification? |
| **Consistency** | No contradictions, conflicts, or inconsistencies in implementation? |
| **Integrity** | Existing accepted baselines preserved? No unapproved modifications? |

### 5.2 Output

A validation report containing:
- Verification of all 4 dimensions
- Defect list with severity
- Non-conformity resolution (fixed or deferred)
- Formal decision

### 5.3 Defect Severity

| Severity | Definition | Resolution Required |
|---|---|---|
| **LOW** | Cosmetic or informational; no functional impact | Documented; may be deferred |
| **MEDIUM** | Functional deviation; does not break integrity | Must be fixed before WP-07 |
| **HIGH** | Breaks baseline integrity or design conformance | Must be fixed immediately; WP-06 re-executed |

---

## 6. Decision Rules

| Decision | Meaning | Next Action |
|---|---|---|
| `PASS` | No observations or defects | Proceed to next WP |
| `PASS WITH OBSERVATIONS` | 1+ LOW or MEDIUM observations; no HIGH | Proceed to next WP; observations documented for future reference |
| `REVISE REQUIRED` | 1+ HIGH observations | Return to previous WP; fix HIGH observations; resubmit for review |
| `PASS — ALL NON-CONFORMITIES RESOLVED` | Validation: all defects fixed | Proceed to WP-07 |
| `PASS WITH NON-CONFORMITIES` | Validation: MEDIUM defects resolved; LOW defects deferred | Proceed to WP-07; deferred defects documented |
| `FAIL` | Validation: HIGH defect remains | Return to WP-05; fix all HIGH defects |

---

## 7. Remediation Procedure

### 7.1 REVISE REQUIRED (WP-02 or WP-04)

1. Reviewer issues REVISE REQUIRED with specific, numbered findings
2. Author fixes each finding
3. Author records fix in a revision summary
4. Revised document is resubmitted
5. Reviewer conducts second review
6. If second review is REVISE REQUIRED on the same finding → the finding is escalated (must involve a second reviewer)

### 7.2 FAIL (WP-06)

1. Validator issues FAIL with specific, numbered defects
2. Implementer fixes all HIGH defects; addresses all MEDIUM defects
3. Implementer records fixes in commit messages referencing defect numbers
4. Implementation is resubmitted
5. Validator re-executes WP-06
6. If second validation FAILs → the implementation scope is reviewed (may indicate design defect)

---

## 8. Review Document Format

All review documents follow GS-02. Review-specific content:

```markdown
# {Scope} — {Review Type}

| id | type | status | version | date |
|---|---|---|---|---|
| `GOV-REV-NNN` | `REV` | `accepted` | `1.0` | `YYYY-MM-DD` |

| part_of |
|---|
| {WP/Project} |

---

**Date**: ... | **Phase**: ... | **Reviewed Artifact**: ...

---

## Review Objective
...

## Review Decision
\```
{DECISION}
\```
```

---

## 9. Evidence References

| Precedent | Source | What It Proves |
|---|---|---|
| WP-02 Assessment Review | `PG02_Assessment_Review.md` (`GOV-REV-007`) | R1: 4 criteria (completeness, consistency, evidence, readiness) |
| WP-04 Design Review | `PG02_Design_Review.md` (`GOV-REV-008`) | R2: 7 criteria, same PASS/PASS WITH OBSERVATIONS/REVISE REQUIRED |
| WP-06 Validation | `PG02_Validation_Report.md` (`GOV-REV-009`) | R3: 4 criteria, defect tracking |
| Severity precedent | PG-02 reviews use "Low", "Medium", "High" | Severity taxonomy formalized from existing usage |

---

## 10. Constraints

| # | Constraint |
|---|---|
| C1 | Review decisions are final when issued; appeals require a new PG item (GS-01 §6 C3) |
| C2 | A reviewer must not be the sole author of the document under review |
| C3 | HIGH observations in WP-02 or WP-04 block the next WP; no work proceeds until resolved |
