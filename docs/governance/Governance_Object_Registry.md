# Governance Object Registry v1.0

| id | type | status | version | date |
|---|---|---|---|---|
| `GOV-REF-006` | `REF` | `accepted` | `1.0` | `2026-07-29` |

| source |
|---|
| `GOV-REF-003` (Governance_Object_Index_Framework.md) |

---

## Purpose

Central registry of all governance objects in the ResourceHub repository. This document is the implementation of the Governance Object Index Framework (`GOV-REF-005`). It maps every governance object to its identifier, type, status, version, and relationships.

**Query this document to answer:**
- What governance objects exist? (full inventory)
- What is the current status of object X? (lookup by ID or filename)
- What depends on object X? (dependency graph)
- What is the authority chain for decision Y? (traceability)

---

## Registry

### Governance Documents (`docs/governance/`)

| id | filename | type | status | version | primary_source |
|---|---|---|---|---|---|
| `GOV-GOV-002` | `Governance_Resolution_v1.0.md` | `GOV` | `accepted` | `1.0` | — |
| `GOV-CHARTER-001` | `Project_Charter_v1.0.md` | `CHARTER` | `accepted` | `1.0` | `GOV-GOV-002` |
| `GOV-GOV-001` | `Governance_Baseline_v1.0.md` | `GOV` | `accepted` | `1.0` | `GOV-CHARTER-001` |
| `GOV-DEC-002` | `Decision_Registry_v1.0.md` | `DEC` | `accepted` | `1.0` | `GOV-GOV-001` |
| `GOV-REC-001` | `Governance_Acceptance_PAC1.md` | `REC` | `accepted` | `1.0` | — |
| `GOV-REC-002` | `Governance_Revision_Report_PAC1.md` | `REC` | `accepted` | `1.0` | — |
| `GOV-REV-001` | `PAC1_Architecture_Retrospective.md` | `REV` | `accepted` | `1.0` | — |
| `GOV-PLAN-001` | `PAC2_Project_Charter.md` | `PLAN` | `accepted` | `1.0` | `GOV-REC-001` |
| `GOV-REF-006` | `Governance_Object_Registry.md` | `REF` | `accepted` | `1.0` | `GOV-REF-003` |
| `GOV-REF-003` | `Governance_Object_Index_Framework.md` | `REF` | `accepted` | `1.0` | `GOV-REV-006` |

### AI Governance Documents (`docs/AI/`)

| id | filename | type | status | version | depends_on |
|---|---|---|---|---|---|
| `GOV-CONST-001` | `DEVELOPMENT_CONSTITUTION.md` | `CONST` | `accepted` | `1.0` | — |
| `GOV-CONST-002` | `AI_WORKFLOW.md` | `CONST` | `accepted` | `1.0` | — |
| `GOV-CHARTER-002` | `PROJECT_BRIEF.md` | `CHARTER` | `superseded` | `1.0` | — |
| `GOV-ARCH-001` | `ARCHITECTURE.md` | `ARCH` | `accepted` | `1.0` | — |
| `GOV-STATUS-001` | `CURRENT_STATUS.md` | `STATUS` | `accepted` | `1.0` | — |
| `GOV-STATUS-002` | `AI_HANDOFF.md` | `STATUS` | `accepted` | `1.0` | `GOV-STATUS-001` |
| `GOV-STATUS-003` | `AI_MEMORY_PACK.md` | `STATUS` | `superseded` | `1.0` | — |
| `GOV-DEC-001` | `DECISION_LOG.md` | `DEC` | `accepted` | `1.0` | — |
| `GOV-PLAN-002` | `NEXT_MILESTONE.md` | `PLAN` | `accepted` | `1.0` | — |
| `GOV-REC-003` | `CHANGELOG_AI.md` | `REC` | `accepted` | `1.0` | — |
| `GOV-REC-004` | `M6_COMPLETION.md` | `REC` | `accepted` | `1.0` | — |
| `GOV-REC-005` | `M8_COMPLETION.md` | `REC` | `accepted` | `1.0` | — |
| `GOV-REV-002` | `REVIEW_GUIDELINES.md` | `REV` | `accepted` | `1.0` | — |
| `GOV-REV-003` | `REVIEW_M6.md` | `REV` | `accepted` | `1.0` | — |
| `GOV-REV-004` | `ARCHITECTURE_AUDIT_M4.md` | `REV` | `accepted` | `1.0` | — |
| `GOV-REF-001` | `KNOWN_LIMITATIONS.md` | `REF` | `accepted` | `1.0` | — |
| `GOV-REF-002` | `TEST_STRATEGY.md` | `REF` | `accepted` | `1.0` | — |

### Planning Documents (`docs/planning/`)

| id | filename | type | status | version | primary_source |
|---|---|---|---|---|---|
| `GOV-PLAN-003` | `Roadmap_Refresh.md` | `PLAN` | `accepted` | `1.0` | `GOV-DEC-002` |

### Root-Level Documents

| id | filename | type | status | version |
|---|---|---|---|---|
| `GOV-REF-004` | `AGENTS.md` | `REF` | `accepted` | `1.0` |
| `GOV-GUIDE-001` | `README.md` | `GUIDE` | `accepted` | `1.0` |
| `GOV-REF-005` | `README_AI.md` | `REF` | `accepted` | `1.0` |
| `GOV-GUIDE-002` | `README_BUILD.md` | `GUIDE` | `accepted` | `1.0` |
| `GOV-REC-006` | `Governance_Integration_Report.md` | `REC` | `accepted` | `1.0` |

### Review Work Products (`docs/governance/reviews/`)

| id | filename | type | status | version | part_of |
|---|---|---|---|---|---|
| `GOV-REV-005` | `PG01_Current_State_Assessment.md` | `REV` | `accepted` | `1.0` | PG-01 |
| `GOV-REV-006` | `PG02_Current_State_Assessment.md` | `REV` | `accepted` | `1.0` | PG-02 |
| `GOV-REV-007` | `PG02_Assessment_Review.md` | `REV` | `accepted` | `1.0` | PG-02 |
| `GOV-REV-008` | `PG02_Design_Review.md` | `REV` | `accepted` | `1.0` | PG-02 |

### Deprecated Documents

| id | filename | type | status | version | notes |
|---|---|---|---|---|---|
| `GOV-STATUS-004` | `docs/development/current_status.md` | `STATUS` | `deprecated` | `1.0` | Superseded by `GOV-STATUS-001`; marked for removal (PG-10) |

---

## Relationship Index

### Authority Chain (`primary_source`)

```
GOV-PLAN-003 (Roadmap)
    ↓ primary_source
GOV-DEC-002 (Decision Registry)
    ↓ primary_source
GOV-GOV-001 (Governance Baseline)
    ↓ primary_source
GOV-CHARTER-001 (Project Charter)
    ↓ primary_source
GOV-GOV-002 (Governance Resolution)
```

### Cross-Reference Index (`references`)

| source | target | relationship |
|---|---|---|
| `GOV-CHARTER-001` | `GOV-GOV-002` | `primary_source` |
| `GOV-CHARTER-001` | `docs/PAC/14_Alignment_Review.md` | `references` |
| `GOV-CHARTER-001` | `docs/PAC/01_Project_Identity.md` | `references` |
| `GOV-GOV-001` | `GOV-CHARTER-001` | `primary_source` |
| `GOV-DEC-002` | `GOV-GOV-001` | `primary_source` |
| `GOV-PLAN-003` | `GOV-DEC-002` | `primary_source` |
| `GOV-PLAN-001` | `GOV-REC-001` | `primary_source` |
| `GOV-STATUS-002` | `GOV-STATUS-001` | `depends_on` |
| `GOV-STATUS-002` | `GOV-ARCH-001` | `depends_on` |
| `GOV-STATUS-002` | `GOV-CONST-001` | `depends_on` |
| `GOV-STATUS-002` | `GOV-CONST-002` | `depends_on` |
| `GOV-STATUS-002` | `GOV-REF-002` | `depends_on` |
| `GOV-STATUS-002` | `GOV-PLAN-002` | `depends_on` |

### Dependency Graph

```
GOV-STATUS-002 (AI_HANDOFF)
    ├── GOV-STATUS-001 (CURRENT_STATUS)     [depends_on]
    ├── GOV-ARCH-001 (ARCHITECTURE)          [depends_on]
    ├── GOV-CONST-001 (DEVELOPMENT_CONSTITUTION) [depends_on]
    ├── GOV-CONST-002 (AI_WORKFLOW)          [depends_on]
    ├── GOV-REF-002 (TEST_STRATEGY)          [depends_on]
    └── GOV-PLAN-002 (NEXT_MILESTONE)        [depends_on]
```

---

## Statistics

| Metric | Value |
|---|---|
| Total objects | 38 |
| Accepted | 35 |
| Superseded | 2 |
| Deprecated | 1 |
| Types in use | 11/11 |
| Objects with `primary_source` | 5 |
| Objects with `depends_on` | 1 (references 6 targets) |
| Objects with no relationships | 27 |
| Objects with `part_of` | 4 |
| PAC-1 frozen objects | 4 (GOV-GOV-002, GOV-CHARTER-001, GOV-GOV-001, GOV-DEC-002) |

---

## Version History

| Version | Date | Change |
|---|---|---|
| `1.0` | 2026-07-29 | Initial registry: 35 objects, 11 types, authority chain + dependency graph |

---

## Maintenance

This registry is updated when:
- A new governance document is created (add row + assign GOV-ID)
- A document status changes (update `status` field)
- A document version changes (update `version` field)
- A new relationship is declared (add to Relationship Index)

**Do not edit this registry to change a document's content.** The registry reflects document state; it does not define it. If a document's status, version, or relationships are incorrect, update the document first, then update the registry.

This document itself is a governance object: `GOV-REF-006`, type `REF`, status `accepted`, version `1.0`.
