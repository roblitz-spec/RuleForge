# Governance Object Index Framework v1.0-draft

**Date**: 2026-07-29 | **Phase**: PAC-2 P0 — WP-03 Framework Design | **Baseline**: PG-02 Current State Assessment (commit `5561c5e`), Assessment Review (commit `76a1c74`)

---

## Purpose

Define the taxonomy, identifier model, metadata schema, relationship model, and versioning integration for all governance objects in the ResourceHub repository. This framework is the design specification for the Governance Object Index capability.

It does **not** perform repository migration, implement automation, or modify existing documents. Those activities belong to WP-05 (Implementation).

---

## 1. Governance Object Taxonomy

### 1.1 Taxonomy Design Principle

Every governance object is assigned exactly one **Object Type**. The type determines the object's purpose, expected content, lifecycle, and metadata requirements.

### 1.2 Object Types

| Type | Code | Purpose | Lifecycle | Example |
|---|---|---|---|---|
| **Constitution** | `CONST` | Immutable development principles and workflow rules | Accepted → (rare revision) | `DEVELOPMENT_CONSTITUTION.md`, `AI_WORKFLOW.md` |
| **Charter** | `CHARTER` | Project identity, scope, capabilities, tech stack | Accepted → Amended | `Project_Charter_v1.0.md`, `PROJECT_BRIEF.md` |
| **Architecture** | `ARCH` | Module boundaries, pipeline, design decisions | Accepted → Updated (per milestone) | `ARCHITECTURE.md` |
| **Status** | `STATUS` | Current project state, test baseline, active milestone | Updated (per milestone) | `CURRENT_STATUS.md`, `AI_HANDOFF.md` |
| **Decision** | `DEC` | Architectural decisions with rationale and alternatives | Proposed → Accepted → Superseded | `DECISION_LOG.md`, `Decision_Registry_v1.0.md` |
| **Governance** | `GOV` | Governance rules, processes, artifact inventory | Accepted → Amended | `Governance_Baseline_v1.0.md`, `Governance_Resolution_v1.0.md` |
| **Planning** | `PLAN` | Milestone plans, feature roadmaps, technical debt | Updated (per milestone) → Archived | `Roadmap_Refresh.md`, `NEXT_MILESTONE.md`, `PAC2_Project_Charter.md` |
| **Record** | `REC` | Historical completion reports, changelogs, acceptance records | Final (immutable after creation) | `CHANGELOG_AI.md`, `M8_COMPLETION.md`, `Governance_Acceptance_PAC1.md` |
| **Review** | `REV` | Review guidelines, audit reports, assessment reviews | Draft → Accepted | `REVIEW_GUIDELINES.md`, `REVIEW_M6.md`, `PG02_Assessment_Review.md` |
| **Reference** | `REF` | Supplementary reference material, limitations, test strategy | Updated (as needed) | `AGENTS.md`, `KNOWN_LIMITATIONS.md`, `TEST_STRATEGY.md`, `README_AI.md` |
| **Guide** | `GUIDE` | Build instructions, onboarding, setup | Updated (as needed) | `README.md`, `README_BUILD.md` |

**11 formal types** replace the 14 ad-hoc inferred types from the assessment. The consolidation:

| Assessment Type | Framework Type |
|---|---|
| Constitution / Policy → | `CONST` |
| Charter / Identity → | `CHARTER` |
| Architecture → | `ARCH` |
| Status / Handoff → | `STATUS` |
| Decision Records → | `DEC` |
| Governance Rules → | `GOV` |
| Planning / Roadmap → | `PLAN` |
| History / Changelog → | `REC` |
| Reviews / Audits + Review Work Product → | `REV` |
| Reference → | `REF` |
| Build Guide + Integration Report → | `GUIDE` |

### 1.3 Type Assignment Rules

| Rule | Description |
|---|---|
| T1 | Every governance document is assigned exactly one Object Type |
| T2 | The type is declared in the document's metadata header |
| T3 | A document's type does not change unless its purpose fundamentally shifts |
| T4 | New types may be added by governance amendment; existing types may not be removed |

---

## 2. Object Identifier Model

### 2.1 Identifier Design Principle

Every governance object has a **single, stable, globally unique identifier**. The identifier is independent of filename, location, and version.

### 2.2 Identifier Format

```
GOV-{TYPE}-{NNN}
```

| Component | Description | Example |
|---|---|---|
| `GOV` | Fixed prefix — all governance objects | `GOV` |
| `{TYPE}` | Object type code (4 chars, see §1.2) | `CHARTER`, `DEC`, `STATUS` |
| `{NNN}` | Sequential number within type, zero-padded to 3 digits | `001`, `002` |

**Examples**: `GOV-CHARTER-001`, `GOV-DEC-002`, `GOV-STATUS-001`

### 2.3 Identifier Assignment

| Rule | Description |
|---|---|
| I1 | Identifiers are assigned at document creation |
| I2 | Identifiers are immutable — never reused, never reassigned |
| I3 | Sequential numbering within each type, starting at `001` |
| I4 | Deprecated or superseded documents retain their identifier |
| I5 | The identifier is declared in the document's metadata header |

### 2.4 Existing Identifier Namespaces

Existing ID namespaces (ADR, D, UD, G, PG) remain for backward compatibility:

| Namespace | Scope | Relationship to GOV-ID |
|---|---|---|
| `ADR-NNN` | Individual architectural decisions | Cross-referenced from `GOV-DEC-*` documents |
| `D-NN` | Confirmed product decisions | Cross-referenced from `GOV-DEC-002` (Decision Registry) |
| `G-NN` | Governance gaps | Cross-referenced from `GOV-GOV-001` (Baseline) |
| `PG-NN` | Proposed governance statements | Cross-referenced from `GOV-GOV-002` (Resolution) |

These are **content identifiers** (within documents), not document identifiers. No migration required.

---

## 3. Object Metadata Model

### 3.1 Metadata Design Principle

Every governance object carries a standard metadata header. Required fields ensure minimum discoverability. Optional fields support specific object types.

### 3.2 Metadata Schema

#### Required Fields (All Objects)

| Field | Key | Format | Example |
|---|---|---|---|
| **Object ID** | `id` | `GOV-{TYPE}-{NNN}` | `GOV-CHARTER-001` |
| **Title** | `title` | Free text | `Project Charter` |
| **Type** | `type` | Type code from §1.2 | `CHARTER` |
| **Status** | `status` | Lifecycle stage from §3.3 | `accepted` |
| **Version** | `version` | Semantic version (see PG-01) | `1.0` |
| **Date** | `date` | `YYYY-MM-DD` | `2026-07-29` |

#### Optional Fields (Type-Dependent)

| Field | Key | Format | Used By |
|---|---|---|---|
| **Primary Source** | `source` | GOV-ID reference | `CHARTER`, `GOV`, `DEC`, `PLAN` |
| **Phase** | `phase` | Free text | `PLAN`, `REV` |
| **Milestone** | `milestone` | `M{N}[.{n}]` | `STATUS`, `REC` |
| **Branch** | `branch` | Git branch name | `STATUS` |
| **Predecessor** | `predecessor` | GOV-ID or commit hash | `PLAN`, `CHARTER` |
| **Audience** | `audience` | Free text | `REF`, `CONST` |

### 3.3 Lifecycle Stages

| Stage | Meaning | Applicable Types |
|---|---|---|
| `draft` | Under active development; not yet reviewed | All |
| `review` | Submitted for review; awaiting approval | All |
| `accepted` | Approved and active; the current source of truth | All |
| `superseded` | Replaced by a newer version; retained for history | All |
| `deprecated` | No longer maintained; will be removed | All |
| `archived` | Historical record; immutable | `REC` |

### 3.4 Metadata Header Format

```markdown
# {Title}

| id | type | status | version | date |
|---|---|---|---|---|
| `GOV-CHARTER-001` | `CHARTER` | `accepted` | `1.0` | `2026-07-29` |

| source | milestone |
|---|---|
| `GOV-GOV-002` | — |
```

Single canonical format. Replaces the 3+ date formats and 2+ status formats identified in the assessment.

### 3.5 Metadata Coverage Target

| Field | Current Coverage | Target (Post-Implementation) |
|---|---|---|
| Title | 100% (33/33) | 100% |
| Date | 48% (16/33) | 100% |
| Status | 24% (8/33) | 100% |
| Type | 0% (0/33) | 100% |
| ID | 0% (0/33) | 100% |
| Version | 12% (4/33) | 100% |
| Source | 15% (5/33) | Type-dependent |
| Phase | 6% (2/33) | Type-dependent |

---

## 4. Object Relationship Model

### 4.1 Relationship Design Principle

Every governance object declares its relationships explicitly in metadata. No relationship is inferred from directory location, filename similarity, or content grep.

### 4.2 Relationship Types

| Type | Direction | Meaning | Example |
|---|---|---|---|
| `primary_source` | Upstream | This object's authority derives from the target | Charter → Resolution |
| `references` | Downstream | This object cites the target for context or evidence | Charter → PAC-1 discovery doc |
| `updates` | Bidirectional | This object replaces or supersedes the target | Charter v1.1 → Charter v1.0 |
| `depends_on` | Upstream | This object's content is invalid if the target changes | AI_HANDOFF → CURRENT_STATUS |
| `part_of` | Upstream | This object belongs to a larger work package | PG02_Assessment → PG-02 work package |

### 4.3 Relationship Declaration

```markdown
| primary_source | references | depends_on |
|---|---|---|
| `GOV-GOV-002` | `docs/PAC/14_Alignment_Review.md` | — |
```

Relationships are declared in the metadata header as GOV-ID references. External references (PAC docs, code files) use repository paths.

### 4.4 Dependency Graph

The framework enables automated dependency graph generation:

```
GOV-GOV-002 (Resolution)
    ↓ primary_source
GOV-CHARTER-001 (Charter)
    ↓ primary_source
GOV-GOV-001 (Baseline)
    ↓ primary_source
GOV-DEC-002 (Registry)
    ↓ primary_source
GOV-PLAN-003 (Roadmap)
```

AI docs form a separate subgraph:

```
GOV-STATUS-001 (CURRENT_STATUS)
    ↓ depends_on
GOV-STATUS-002 (AI_HANDOFF)
    ↓ references
GOV-ARCH-001 (ARCHITECTURE)
GOV-CONST-001 (DEVELOPMENT_CONSTITUTION)
GOV-CONST-002 (AI_WORKFLOW)
...
```

### 4.5 Stale Propagation

With explicit `depends_on` relationships, staleness detection becomes mechanical:

```
For each document D:
    For each target T in D.depends_on:
        If T.status == "deprecated" or T.version > D.referenced_version:
            Flag D as potentially stale
```

This replaces the current manual grep-based staleness detection (F7 from assessment).

---

## 5. Integration with PG-01 Governance Versioning Framework

### 5.1 Version Field

The `version` field in the metadata schema (§3.2) uses the semantic versioning scheme defined by PG-01 (Governance Versioning Framework, in development):

| Version | Meaning |
|---|---|
| `0.x` | Draft — under active development |
| `1.0` | Accepted baseline |
| `1.x` | Amendment — backward-compatible update |
| `2.0` | Major revision — breaking change to governance structure |

### 5.2 Version ↔ Lifecycle Mapping

| Lifecycle Stage | Typical Version |
|---|---|
| `draft` | `0.x` |
| `review` | `0.x` |
| `accepted` | `≥1.0` |
| `superseded` | Frozen at last version |
| `deprecated` | Frozen at last version |
| `archived` | Frozen at last version |

### 5.3 Version Increment Triggers

| Change | Version Increment |
|---|---|
| Typo fix, formatting | No change (patch: `1.0` → `1.0.1`) |
| New optional metadata field | Minor (`1.0` → `1.1`) |
| New required metadata field | Minor (`1.0` → `1.1`) |
| Relationship change (new `depends_on`) | Minor (`1.0` → `1.1`) |
| Type change | Major (`1.0` → `2.0`) |
| Status change only | No version change |

### 5.4 Index Versioning

The Governance Object Index itself is a governance object:

| Field | Value |
|---|---|
| ID | `GOV-REF-003` |
| Type | `REF` |
| Version | Follows PG-01 versioning |

---

## 6. Assignment Table (Provisional)

### 6.1 Governance Documents (`docs/governance/`)

| Document | ID | Type | Status |
|---|---|---|---|
| `Governance_Resolution_v1.0.md` | `GOV-GOV-002` | `GOV` | `accepted` |
| `Project_Charter_v1.0.md` | `GOV-CHARTER-001` | `CHARTER` | `accepted` |
| `Governance_Baseline_v1.0.md` | `GOV-GOV-001` | `GOV` | `accepted` |
| `Decision_Registry_v1.0.md` | `GOV-DEC-002` | `DEC` | `accepted` |
| `Governance_Acceptance_PAC1.md` | `GOV-REC-001` | `REC` | `accepted` |
| `Governance_Revision_Report_PAC1.md` | `GOV-REC-002` | `REC` | `accepted` |
| `PAC1_Architecture_Retrospective.md` | `GOV-REV-001` | `REV` | `accepted` |
| `PAC2_Project_Charter.md` | `GOV-PLAN-001` | `PLAN` | `accepted` |

### 6.2 AI Governance Documents (`docs/AI/`)

| Document | ID | Type | Status |
|---|---|---|---|
| `DEVELOPMENT_CONSTITUTION.md` | `GOV-CONST-001` | `CONST` | `accepted` |
| `AI_WORKFLOW.md` | `GOV-CONST-002` | `CONST` | `accepted` |
| `PROJECT_BRIEF.md` | `GOV-CHARTER-002` | `CHARTER` | `superseded` |
| `ARCHITECTURE.md` | `GOV-ARCH-001` | `ARCH` | `accepted` |
| `CURRENT_STATUS.md` | `GOV-STATUS-001` | `STATUS` | `accepted` |
| `AI_HANDOFF.md` | `GOV-STATUS-002` | `STATUS` | `accepted` |
| `AI_MEMORY_PACK.md` | `GOV-STATUS-003` | `STATUS` | `superseded` |
| `DECISION_LOG.md` | `GOV-DEC-001` | `DEC` | `accepted` |
| `NEXT_MILESTONE.md` | `GOV-PLAN-002` | `PLAN` | `accepted` |
| `CHANGELOG_AI.md` | `GOV-REC-003` | `REC` | `accepted` |
| `M6_COMPLETION.md` | `GOV-REC-004` | `REC` | `accepted` |
| `M8_COMPLETION.md` | `GOV-REC-005` | `REC` | `accepted` |
| `REVIEW_GUIDELINES.md` | `GOV-REV-002` | `REV` | `accepted` |
| `REVIEW_M6.md` | `GOV-REV-003` | `REV` | `accepted` |
| `ARCHITECTURE_AUDIT_M4.md` | `GOV-REV-004` | `REV` | `accepted` |
| `KNOWN_LIMITATIONS.md` | `GOV-REF-001` | `REF` | `accepted` |
| `TEST_STRATEGY.md` | `GOV-REF-002` | `REF` | `accepted` |

### 6.3 Planning Documents (`docs/planning/`)

| Document | ID | Type | Status |
|---|---|---|---|
| `Roadmap_Refresh.md` | `GOV-PLAN-003` | `PLAN` | `accepted` |

### 6.4 Root-Level Documents

| Document | ID | Type | Status |
|---|---|---|---|
| `AGENTS.md` | `GOV-REF-004` | `REF` | `accepted` |
| `README.md` | `GOV-GUIDE-001` | `GUIDE` | `accepted` |
| `README_AI.md` | `GOV-REF-005` | `REF` | `accepted` |
| `README_BUILD.md` | `GOV-GUIDE-002` | `GUIDE` | `accepted` |
| `Governance_Integration_Report.md` | `GOV-REC-006` | `REC` | `accepted` |

### 6.5 Work Products (`docs/governance/reviews/`)

| Document | ID | Type | Status |
|---|---|---|---|
| `PG01_Current_State_Assessment.md` | `GOV-REV-005` | `REV` | `draft` |
| `PG02_Current_State_Assessment.md` | `GOV-REV-006` | `REV` | `review` |
| `PG02_Assessment_Review.md` | `GOV-REV-007` | `REV` | `accepted` |

### 6.6 Deprecated Document

| Document | ID | Type | Status |
|---|---|---|---|
| `docs/development/current_status.md` | `GOV-STATUS-004` | `STATUS` | `deprecated` |

**Total**: 34 governance objects assigned across 11 types. No object is unclassified.

---

## 7. Design Decisions

| # | Decision | Rationale |
|---|---|---|
| D1 | 11 formal types | Balances granularity (14 was too many) with clarity (8 would be too few). Consolidates similar types. |
| D2 | `GOV-{TYPE}-{NNN}` identifier format | 4-char type codes balance human readability with grep-friendliness. Sequential numbering is simple and collision-free. |
| D3 | Metadata as Markdown table | Consistent with existing doc conventions; human-readable; machine-parseable (pipe-delimited). |
| D4 | 6 required + 6 optional fields | Minimum required set ensures discoverability; optional fields prevent over-specification for simple documents. |
| D5 | Existing ID namespaces preserved | ADR, D, G, PG namespaces are content-level, not document-level. No migration needed. |
| D6 | `depends_on` for stale detection | Explicit dependency declaration is the only reliable way to detect stale propagation. |
| D7 | Framework itself is `GOV-REF-003` | The index framework is a reference document; it must carry its own metadata. |

---

## 8. Constraints

| Constraint | Detail |
|---|---|
| No repository migration in this phase | ID assignment table is provisional until WP-05 Implementation |
| No document modification | Existing documents are not edited to add metadata headers |
| Framework is design-only | Automation, tooling, and enforcement are WP-05 scope |
| PG-01 versioning integration | Uses placeholder schema until PG-01 Framework Design is complete |
| Backward compatibility | Existing document filenames, paths, and content are not changed by this framework |

---

## 9. Exit Criteria for WP-03

| Criterion | Status |
|---|---|
| Object taxonomy defined (≥8, ≤12 types) | ✅ 11 types |
| Identifier format specified | ✅ `GOV-{TYPE}-{NNN}` |
| Metadata schema defined (required + optional) | ✅ 6 required + 6 optional |
| Relationship model defined (≥3 types) | ✅ 5 types |
| Versioning integration defined | ✅ Schema + lifecycle mapping |
| Provisional assignment table complete | ✅ 34 objects assigned |
| Design decisions documented | ✅ 7 decisions |
| No existing documents modified | ✅ |

---

**Framework design complete. Ready for PG-02 WP-04 Design Review.**
