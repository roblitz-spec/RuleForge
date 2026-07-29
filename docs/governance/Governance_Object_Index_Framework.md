# Governance Object Index Framework v1.0-draft

| id | type | status | version | date |
|---|---|---|---|---|
| `GOV-REF-003` | `REF` | `accepted` | `1.0` | `2026-07-29` |

| source | predecessor |
|---|---|
| `GOV-REV-006` (PG-02 Current State Assessment) | — |

---

**Date**: 2026-07-29 | **Phase**: PAC-2 P0 — WP-03 Framework Design | **Baseline**: PG-02 Current State Assessment (commit `5561c5e`), Assessment Review (commit `76a1c74`)

---

## Purpose

Define the taxonomy, identifier model, metadata schema, relationship model, and versioning integration for all governance objects in the ResourceHub repository. This framework is the design specification for the Governance Object Index capability.

It does **not** perform repository migration, implement automation, or modify existing documents. Those activities belong to WP-05 (Implementation).

---

## Core Concepts

### Object Identity vs. Version Identity

A governance object has two distinct identities that serve different purposes:

| Identity | Meaning | Stability | Example |
|---|---|---|---|
| **Object Identity** | What the document *is* — its role in the governance system | Immutable for the object's lifetime | `GOV-CHARTER-001` (the Project Charter) |
| **Version Identity** | What *revision* of the document this is — its state at a point in time | Changes with each accepted update | `1.0` (initial baseline), `1.1` (amended) |

**Why this distinction matters:**

1. **Cross-references survive version changes.** A document referencing `GOV-CHARTER-001` does not break when the Charter is amended from v1.0 to v1.1. The reference is to the object, not the version.

2. **Traceability chains are stable.** The dependency chain `Resolution → Charter → Baseline → Registry → Roadmap` uses object identities. Version increments within any node do not require updating downstream references.

3. **History is navigable.** A superseded Charter v1.0 retains `GOV-CHARTER-001` as its object identity while its version marks it as `superseded`. The relationship `GOV-CHARTER-001 v1.1 updates GOV-CHARTER-001 v1.0` is explicit and queryable.

4. **Automation is predictable.** Scripts resolve `GOV-CHARTER-001` to "the current accepted version" without parsing filenames or guessing. The registry maps object identity to current version.

**Counter-example (current state):** Documents reference each other by filename (`Project_Charter_v1.0.md`). If the Charter is renamed to `Project_Charter_v1.1.md`, every reference breaks. Object identity solves this.

### Identity Lifecycle

```
Object Created        Version 1.0 Accepted     Version 1.1 Accepted
    │                       │                       │
    ▼                       ▼                       ▼
GOV-CHARTER-001 ────── GOV-CHARTER-001 ────── GOV-CHARTER-001
    v0.1                  v1.0                   v1.1
  (draft)              (accepted)             (accepted)
                         ▲                       ▲
                         │                       │
                    Object identity             Same object,
                    is now stable              version evolved
```

The object identity is assigned at creation and never changes. The version identity evolves through the lifecycle stages defined in §3.3.

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

| Assessment Type | Framework Type | Rationale |
|---|---|---|
| Constitution / Policy → | `CONST` | Both define binding rules; distinction (constitution vs policy) is content, not structural |
| Charter / Identity → | `CHARTER` | Identity documents are a subset of charter scope; single type avoids ambiguity |
| Architecture → | `ARCH` | Distinct structural role — no merge |
| Status / Handoff → | `STATUS` | Both serve state communication; handoff is a specialized status document |
| Decision Records → | `DEC` | Distinct evidential role — no merge |
| Governance Rules → | `GOV` | Distinct rule-making role — no merge |
| Planning / Roadmap → | `PLAN` | Roadmap is a planning sub-type; single type for all forward-looking documents |
| History / Changelog → | `REC` | Both are immutable historical records; changelog is a specialized record |
| Reviews / Audits + Review Work Product → | `REV` | Assessments, reviews, audits all serve the verification function; sub-types are content distinction |
| Retrospectives / Reports → | `REV` | Retrospectives are a specialized form of review; same lifecycle |
| Reference → | `REF` | Distinct supplementary role — no merge |
| Build Guide + Integration Report → | `GUIDE` | Both are procedural instructions; integration report is a transitional artifact that becomes a guide |

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

Every governance object has a **single, stable, globally unique identifier**. The identifier is independent of filename, location, and version — it is the object's identity for the lifetime of the object.

### 2.2 Identifier Semantics

The identifier encodes three properties, each serving a specific governance function:

| Component | Property Encoded | Governance Function |
|---|---|---|
| `GOV` | Namespace | Distinguishes governance objects from code symbols, ADR references, and PAC discovery docs |
| `{TYPE}` | Structural role | Enables type-based queries ("all decisions," "all status docs"), type-specific automation, and type-appropriate lifecycle enforcement |
| `{NNN}` | Chronology | Encodes creation order within type; enables "what was decided first?" queries without timestamp parsing |

**Why these three properties:**

1. **Namespace isolation** (`GOV`): ADRs (`ADR-001`), decisions (`D-01`), gaps (`G-01`), and proposals (`PG-01`) are content identifiers within documents. The `GOV` prefix prevents collision with these existing namespaces and with future code-level symbols.

2. **Type encoding** (`CHARTER`, `DEC`, etc.): Putting the type in the identifier makes it self-describing. `GOV-CHARTER-001` communicates its role without requiring a registry lookup. This is critical for human readability in cross-references — a reader encountering `GOV-CHARTER-001` in a `source` field immediately knows it references a charter document.

3. **Sequential numbering** (`001`, `002`): Sequential (not random, not hash-based) because governance documents are created by humans in a defined order. The number conveys "this is the first charter" vs "this is the second decision." No semantic meaning is attached to the number beyond creation order.

**What the identifier does NOT encode:**
- Version (belongs in the `version` metadata field)
- Status (belongs in the `status` metadata field)
- Location or filename (irrelevant to identity; an object may be renamed or moved)
- Content hash (too brittle for documents that undergo editorial revision)

### 2.3 Identifier Format

```
GOV-{TYPE}-{NNN}
```

| Component | Description | Example |
|---|---|---|
| `GOV` | Fixed prefix — all governance objects | `GOV` |
| `{TYPE}` | Object type code (4 chars, see §1.2) | `CHARTER`, `DEC`, `STATUS` |
| `{NNN}` | Sequential number within type, zero-padded to 3 digits | `001`, `002` |

**Examples**: `GOV-CHARTER-001`, `GOV-DEC-002`, `GOV-STATUS-001`

### 2.4 Identifier Assignment

| Rule | Description |
|---|---|
| I1 | Identifiers are assigned at document creation |
| I2 | Identifiers are immutable — never reused, never reassigned |
| I3 | Sequential numbering within each type, starting at `001` |
| I4 | Deprecated or superseded documents retain their identifier |
| I5 | The identifier is declared in the document's metadata header |

### 2.5 Existing Identifier Namespaces

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

Every governance object carries a standard metadata header. Required fields ensure minimum discoverability and traceability. Optional fields support specific object types without burdening simple documents.

### 3.2 Field Selection Rationale

**Why these 6 fields are required:**

| Field | Justification |
|---|---|
| `id` | Object identity (§Core Concepts). Without an ID, cross-references cannot be stable. This is the single most important metadata field — it enables all other governance capabilities. |
| `title` | Human readability. The ID is machine-friendly; the title is human-friendly. Both are needed. |
| `type` | Determines lifecycle rules, expected content, and automation behavior. A `CONST` document cannot be `deprecated` in the same way a `STATUS` document can. |
| `status` | Answers "can I rely on this document right now?" without reading it. A document without a status field requires full-text inspection to determine if it's current. |
| `version` | Enables "is this the latest?" queries. Required for version-aware cross-references and stale detection. Integrates with PG-01 versioning framework. |
| `date` | Temporal ordering independent of version. Two `v1.0-draft` versions of the same document are ordered by date. Required for automation that answers "what changed since last week?" |

**Why these 6 fields are optional:**

| Field | Justification |
|---|---|
| `source` | Only meaningful for documents in a dependency chain. A `CONST` document has no primary source — it is foundational. A `CHARTER` document does. |
| `phase` | Only meaningful for work-in-progress documents (`PLAN`, `REV`). An accepted `REC` has no phase. |
| `milestone` | Only meaningful for milestone-bound documents (`STATUS`, `REC`). A `CONST` or `REF` transcends milestones. |
| `branch` | Only meaningful for actively developed documents. An accepted `REC` has no active branch. |
| `predecessor` | Only meaningful when a document supersedes another. First versions have no predecessor. |
| `audience` | Only meaningful when the document targets a specific reader. Most governance documents are universal within the project. |

### 3.3 Metadata Schema

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

### 3.4 Lifecycle Stages

| Stage | Meaning | Applicable Types |
|---|---|---|
| `draft` | Under active development; not yet reviewed | All |
| `review` | Submitted for review; awaiting approval | All |
| `accepted` | Approved and active; the current source of truth | All |
| `superseded` | Replaced by a newer version; retained for history | All |
| `deprecated` | No longer maintained; will be removed | All |
| `archived` | Historical record; immutable | `REC` |

### 3.5 Metadata Header Format

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

### 3.6 Metadata Coverage Target

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

Every governance object declares its relationships explicitly in metadata. No relationship is inferred from directory location, filename similarity, or content grep. Explicit relationships are the foundation for traceability and stale detection.

### 4.2 Relationship Semantics

Each relationship type serves a specific governance function in the traceability chain:

| Type | Direction | Governance Function | Traceability Role |
|---|---|---|---|
| `primary_source` | Upstream | Declares authority derivation | **Vertical traceability**: "Who decided this?" — traces upward to the source of authority |
| `references` | Downstream | Cites evidence or context | **Horizontal traceability**: "What informed this?" — traces outward to supporting evidence |
| `updates` | Bidirectional | Replaces or supersedes a prior version | **Version traceability**: "What did this replace?" — traces backward through version history |
| `depends_on` | Upstream | Declares content validity dependency | **Staleness traceability**: "What must I check when this changes?" — enables mechanical stale detection without content inspection |
| `part_of` | Upstream | Declares membership in a larger work package | **Structural traceability**: "What work package produced this?" — groups related artifacts |

### 4.3 Composite Traceability Chains

Individual relationships combine to form end-to-end traceability:

**Authority chain** (`primary_source`):
```
GOV-PLAN-003 (Roadmap)
    → GOV-DEC-002 (Registry)       [primary_source]
        → GOV-GOV-001 (Baseline)    [primary_source]
            → GOV-CHARTER-001       [primary_source]
                → GOV-GOV-002       [primary_source] — "The Resolution decided this"
```
Answers: "What is the authority basis for this roadmap item?" — traversable in O(n) from any node.

**Evidence chain** (`references` + `primary_source`):
```
GOV-CHARTER-001
    → GOV-GOV-002                   [primary_source]
    → docs/PAC/14_Alignment_Review.md [references]  — "This file informed the charter"
    → docs/PAC/01_Project_Identity.md [references]   — "This file informed the charter"
```
Answers: "What evidence supports this document?" — combines authority and evidence in a single query.

**Version chain** (`updates`):
```
GOV-CHARTER-001 v1.1
    → GOV-CHARTER-001 v1.0          [updates] — "v1.1 replaced v1.0"
```
Answers: "What is the full version history of this object?"

**Staleness chain** (`depends_on`):
```
GOV-STATUS-002 (AI_HANDOFF)
    → GOV-STATUS-001 (CURRENT_STATUS)  [depends_on]
    → GOV-ARCH-001 (ARCHITECTURE)       [depends_on]
```
Answers: "If CURRENT_STATUS changes, what else must be reviewed?" — the foundation for automated staleness detection.

### 4.4 Relationship Declaration

```markdown
| primary_source | references | depends_on |
|---|---|---|
| `GOV-GOV-002` | `docs/PAC/14_Alignment_Review.md` | — |
```

Relationships are declared in the metadata header as GOV-ID references. External references (PAC docs, code files) use repository paths.

### 4.5 Dependency Graph

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

### 4.6 Stale Propagation

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

### 5.1 Object Identity → Version Identity Mapping

The two-identity model (§Core Concepts) integrates with PG-01 as follows:

| Identity Layer | This Framework | PG-01 Framework |
|---|---|---|
| Object Identity | `GOV-{TYPE}-{NNN}` (immutable) | Not versioned — stable across all versions |
| Version Identity | `version` field in metadata | Semantic versioning rules, increment triggers |

The PG-01 versioning framework governs the `version` field. The Governance Object Index governs the `id` field. They are orthogonal and complementary.

### 5.2 Version Field

The `version` field in the metadata schema (§3.2) uses the semantic versioning scheme defined by PG-01 (Governance Versioning Framework, in development):

| Version | Meaning |
|---|---|
| `0.x` | Draft — under active development |
| `1.0` | Accepted baseline |
| `1.x` | Amendment — backward-compatible update |
| `2.0` | Major revision — breaking change to governance structure |

### 5.3 Version ↔ Lifecycle Mapping

| Lifecycle Stage | Typical Version |
|---|---|
| `draft` | `0.x` |
| `review` | `0.x` |
| `accepted` | `≥1.0` |
| `superseded` | Frozen at last version |
| `deprecated` | Frozen at last version |
| `archived` | Frozen at last version |

### 5.4 Version Increment Triggers

| Change | Version Increment |
|---|---|
| Typo fix, formatting | No change (patch: `1.0` → `1.0.1`) |
| New optional metadata field | Minor (`1.0` → `1.1`) |
| New required metadata field | Minor (`1.0` → `1.1`) |
| Relationship change (new `depends_on`) | Minor (`1.0` → `1.1`) |
| Type change | Major (`1.0` → `2.0`) |
| Status change only | No version change |

### 5.5 Index Versioning

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
| D1 | 11 formal types | Balances granularity with clarity. 14 was too many (COSNT vs POLICY distinction added no structural value). 8 would be too few (DEC, GOV, PLAN have fundamentally different lifecycles and merge would lose that). Each consolidation decision is justified in §1.2. |
| D2 | `GOV-{TYPE}-{NNN}` identifier format | Three encoded properties (namespace, role, chronology) each serve a distinct governance function. No property is redundant. See §2.2. |
| D3 | Metadata as Markdown table | Consistent with existing doc conventions (AI_HANDOFF, AI_MEMORY_PACK already use tables). Human-readable. Machine-parseable (pipe-delimited). No new format to learn. |
| D4 | 6 required + 6 optional fields | Required set is the minimum for discoverability and traceability. Optional fields prevent over-specification — a `CONST` document should not carry a `milestone` field. See §3.2. |
| D5 | Existing ID namespaces preserved | ADR, D, G, PG namespaces are content-level identifiers within documents, not document-level identifiers. No migration needed. No collision risk. |
| D6 | `depends_on` for stale detection | Explicit dependency declaration is the only reliable way to detect stale propagation. Grep-based detection (current state) misses cross-document dependencies. |
| D7 | Framework itself is `GOV-REF-003` | The index framework is a governance object; it must carry its own metadata to demonstrate the model it defines. |
| D8 | Object Identity ≠ Version Identity | Core design decision. Object identity (`GOV-CHARTER-001`) is stable across versions. Version identity (`1.0` → `1.1`) changes. This separation is what enables stable cross-references, version history navigation, and automation. Without it, every version increment breaks every reference — the current state problem the framework exists to solve. |
| D9 | Explicit relationships over inferred relationships | Every relationship is declared. Directory location, filename pattern, and content grep are not relationships. This is the single constraint that makes automation possible — a script can parse declared relationships; it cannot interpret human naming conventions. |

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
| Object taxonomy defined (≥8, ≤12 types) | ✅ 11 types with consolidation rationale |
| Identifier format specified with semantics | ✅ `GOV-{TYPE}-{NNN}` with per-component rationale |
| Object Identity vs Version Identity distinction defined | ✅ Core Concepts §2 |
| Metadata schema defined (required + optional) with field rationale | ✅ 6+6 fields with per-field justification |
| Relationship model defined (≥5 types) with traceability semantics | ✅ 5 types with composite chain documentation |
| Versioning integration defined | ✅ Object↔Version mapping + lifecycle integration |
| Provisional assignment table complete | ✅ 34 objects assigned |
| Design decisions documented with rationale | ✅ 9 decisions |
| No existing documents modified | ✅ |

---

**Framework design complete. Ready for PG-02 WP-04 Design Review.**
