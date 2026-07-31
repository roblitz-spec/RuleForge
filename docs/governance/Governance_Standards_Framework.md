# PAC-2 Governance Standards Framework v1.0-draft

| id | type | status | version | date |
|---|---|---|---|---|
| `GOV-REF-007` | `REF` | `accepted` | `1.0` | `2026-07-29` |

| source |
|---|
| `GOV-REV-010` (PAC-2 Standards Assessment), `GOV-REV-011` (Assessment Review) |

---

**Date**: 2026-07-29 | **Phase**: PAC-2 Standards — WP-03 Framework Design | **Baseline**: `PAC2_Standards_Assessment.md` (commit `de2f066`), `PAC2_Standards_Assessment_Review.md` (commit `f8a7586`)

---

## Purpose

Define the PAC-2 Governance Standards Layer — a coherent set of five governance standards that formalize the practices proven in PG-01 and PG-02. This framework establishes the standards' scope, hierarchy, relationships, and design principles.

---

## Standards

| ID | Standard | Scope | Foundation |
|---|---|---|---|
| **GS-01** | PAC-2 Governance Standard | How governance projects are conducted — lifecycle, work packages, exit criteria, acceptance | PG-02 execution (7 WPs) |
| **GS-02** | Governance Document Standard | Structure of governance documents — metadata, sections, format, lifecycle | PG-02 Framework §3 (metadata model) |
| **GS-03** | Governance Review Standard | Review process — types, criteria, decision vocabulary, remediation | PG-02 WP-02, WP-04, WP-06 reviews |
| **GS-04** | Governance Naming Standard | Naming conventions — files, titles, identifiers, directories | PG-02 Framework §2 (identifier model) |
| **GS-05** | Governance Traceability Standard | Traceability model — relationships, chains, verification, stale detection | PG-02 Framework §4 (relationship model) |

---

## Standards Hierarchy

```
GS-01 (Lifecycle)
    │
    ├── GS-02 (Document Structure)    ← defines the format of governance documents
    ├── GS-03 (Review Process)        ← defines how documents are reviewed
    ├── GS-04 (Naming)                ← defines how documents and objects are named
    └── GS-05 (Traceability)          ← defines how documents relate to each other
```

**GS-01 is the root standard.** It defines the lifecycle through which all governance work is conducted — including the creation, review, and acceptance of GS-02 through GS-05 themselves.

---

## Design Principles

| # | Principle | Rationale |
|---|---|---|
| P1 | **Extract, don't invent** | Every standard rule must be traceable to a PG-01 or PG-02 precedent. No theoretical governance. |
| P2 | **Standalone and referenceable** | Each standard is a complete document with its own GOV-ID. Standards reference each other; they do not embed each other. |
| P3 | **Compatible with accepted baselines** | PAC-1 Accepted v1.0 documents and PG-02 accepted artifacts are not modified. Standards define forward conventions; they don't retrofit. |
| P4 | **Phased adoption** | Standards with high migration cost (GS-02, GS-04) define a phased migration path. The standard is the target state; immediate compliance is not required. |
| P5 | **Self-documenting** | Each standard follows the format it defines. GS-02 documents must conform to GS-02. GS-04 names must conform to GS-04. |

---

## Assessment Finding Coverage

| Assessment Finding | Standard | Resolution |
|---|---|---|
| F1-01: No lifecycle standard | GS-01 | 7-WP cycle codified |
| F1-02: WP formats scattered | GS-01 | Unified WP format definition |
| F1-03: No skip/combine guidance | GS-01 | Complexity-based WP selection |
| F2-01: 3 structure conventions | GS-02 | Canonical format + migration path |
| F2-02: AI docs unstandardized | GS-02 | Minimum metadata standard |
| F2-03: Metadata placement | GS-02 | Placement rule defined |
| F3-01: No review standard | GS-03 | 3 review types codified |
| F3-02: Severity taxonomy inconsistent | GS-03 | Unified severity taxonomy |
| F3-03: No REVISE REQUIRED procedure | GS-03 | Remediation procedure defined |
| F4-01: 5 naming conventions | GS-04 | Canonical convention + phase-out plan |
| F4-02: No GOV-ID ↔ filename rule | GS-04 | Mapping rules defined |
| F4-03: Title format varies | GS-04 | Title convention defined |
| F5-01: Relationship model not standalone | GS-05 | 5 relationship types codified |
| F5-02: No applicability rules | GS-05 | Type → relationship mapping |
| F5-03: Staleness not operational | GS-05 | Verification procedure defined |
| CX-01: Precedent not codified | All | All 5 standards formalize proven patterns |
| CX-02: Common need across all | All | This framework provides the unifying structure |
| CX-03: Lifecycle is vehicle | GS-01 | Standards themselves follow 7-WP lifecycle |

---

## Assessment Gap Coverage

| Gap | Resolution |
|---|---|
| G1: No lifecycle standard | GS-01 defines the 7-WP lifecycle |
| G2: No document structure standard | GS-02 defines canonical format |
| G3: No review process standard | GS-03 defines review types and procedures |
| G4: No naming standard | GS-04 defines naming conventions |
| G5: No traceability standard | GS-05 defines relationship model |
| G6: No standard precedence | GS-01 §1.1 establishes lifecycle as root standard |

---

## Observation Response (from WP-02)

| Observation | Response |
|---|---|
| O1: G6 resolves via GS-01 | ✅ GS-01 §1.1 defines standard precedence: GS-01 is root; GS-02–GS-05 are subordinate compliance standards |
| O2: GS-02/GS-04 high reform cost | ✅ GS-02 §7 and GS-04 §7 define phased migration: Phase 1 (PAC-2 docs only), Phase 2 (AI docs), Phase 3 (PAC-1 docs — deferred) |
| O3: AI docs need lighter standard | ✅ GS-02 §6 defines "Minimum Metadata" tier: AI docs require only metadata header, not full section standardization |

---

## Phased Adoption

| Phase | Scope | Standards | When |
|---|---|---|---|
| **Phase 1** | New PAC-2 documents | GS-01, GS-02 (full), GS-03, GS-04 (full), GS-05 | Immediate — applies to all PG items (03–10) and standards documents |
| **Phase 2** | Existing AI docs (17) | GS-02 (minimum) | During PG-06 (AI_HANDOFF update) and PG-07 (NEXT_MILESTONE update) |
| **Phase 3** | PAC-1 Accepted v1.0 docs | GS-02 (reference only) | Deferred — PAC-1 baseline is frozen; standards apply as reference convention, not modification mandate |

---

## Standards Documents

Each standard is a standalone governance document:

| Standard | Document | GOV-ID |
|---|---|---|
| GS-01 | `Governance_Standard_PAC2_Lifecycle.md` | `GOV-GUIDE-003` |
| GS-02 | `Governance_Standard_Document_Structure.md` | `GOV-GUIDE-004` |
| GS-03 | `Governance_Standard_Review.md` | `GOV-GUIDE-005` |
| GS-04 | `Governance_Standard_Naming.md` | `GOV-GUIDE-006` |
| GS-05 | `Governance_Standard_Traceability.md` | `GOV-GUIDE-007` |

---

## Constraints

| # | Constraint |
|---|---|
| C1 | Standards define process and convention; they do not define policy (what decisions are made) |
| C2 | No standard modifies PAC-1 Accepted v1.0 documents |
| C3 | No standard modifies PG-02 accepted artifacts |
| C4 | Standards are forward-looking: they apply to new work, not retroactively |
| C5 | Each standard must reference at least one PG-01 or PG-02 artifact as evidence |

---

## Design Decisions

| # | Decision | Rationale |
|---|---|---|
| D1 | GS-01 is the root standard | The lifecycle governs how all governance work is conducted; all other standards are created through this process |
| D2 | Standards use `GUIDE` type | Standards are instructional, not normative; they guide behavior rather than mandate decisions |
| D3 | Phased adoption for GS-02 and GS-04 | Immediate full compliance would require modifying 28+ frozen documents; phased approach respects freeze while establishing the target |
| D4 | AI docs get minimum metadata tier | AI docs serve AI consumption, not human governance; full section standardization is unnecessary overhead |
| D5 | Each standard is a standalone document | Standards must be referenceable individually; embedding reduces discoverability and creates circular dependencies |

---

## Exit Criteria for WP-03

| # | Criterion | Status |
|---|---|---|
| E1 | Standards Framework document complete | ✅ This document |
| E2 | GS-01 document complete | ✅ `Governance_Standard_PAC2_Lifecycle.md` |
| E3 | GS-02 document complete | ✅ `Governance_Standard_Document_Structure.md` |
| E4 | GS-03 document complete | ✅ `Governance_Standard_Review.md` |
| E5 | GS-04 document complete | ✅ `Governance_Standard_Naming.md` |
| E6 | GS-05 document complete | ✅ `Governance_Standard_Traceability.md` |
| E7 | All standards have GOV-IDs | ✅ GS-01: `GOV-GUIDE-003` through GS-05: `GOV-GUIDE-007` |
| E8 | All standards reference PG-01/PG-02 evidence | ✅ Each standard §Evidence References |
| E9 | All standards are internally consistent with each other | ✅ Cross-verified (see WP-04 for formal review) |
