# GS-04: Governance Naming Standard v1.0-draft

| id | type | status | version | date |
|---|---|---|---|---|
| `GOV-GUIDE-006` | `GUIDE` | `accepted` | `1.0` | `2026-07-29` |

| source | part_of |
|---|---|
| `GOV-REF-007` (Standards Framework) | PAC-2 Standards |

---

## 1. Purpose

Define the standard naming conventions for governance objects, files, titles, and directories. This standard resolves the 5 competing naming conventions identified in the WP-01 Assessment (F4-01) by establishing a single canonical convention derived from the PG-02 identifier and type models.

---

## 2. Object Identifiers (GOV-ID)

### 2.1 Format

```
GOV-{TYPE}-{NNN}
```

| Component | Meaning | Source |
|---|---|---|
| `GOV` | Governance namespace | PG-02 Framework §2.2 |
| `{TYPE}` | Object type code | PG-02 Framework §1.2 |
| `{NNN}` | Sequential number (3-digit, zero-padded) | PG-02 Framework §2.2 |

### 2.2 Type Codes

| Code | Type | Example |
|---|---|---|
| `CONST` | Constitution | `GOV-CONST-001` |
| `CHARTER` | Charter | `GOV-CHARTER-001` |
| `ARCH` | Architecture | `GOV-ARCH-001` |
| `STATUS` | Status | `GOV-STATUS-001` |
| `DEC` | Decision | `GOV-DEC-002` |
| `GOV` | Governance Baseline | `GOV-GOV-001` |
| `PLAN` | Plan | `GOV-PLAN-001` |
| `REC` | Record | `GOV-REC-001` |
| `REV` | Review | `GOV-REV-005` |
| `REF` | Reference | `GOV-REF-003` |
| `GUIDE` | Guide / Standard | `GOV-GUIDE-003` |

### 2.3 Assignment Rules

| Rule | Description |
|---|---|
| R1 | Identifiers are immutable — never reused, never reassigned |
| R2 | Deprecated or superseded documents retain their identifier |
| R3 | New objects get the next available number in their type sequence |
| R4 | Numbers are assigned in creation order, not alphabetical order |

---

## 3. File Naming

### 3.1 Canonical Convention

```
{Descriptor}.md
```

| Component | Description | Example |
|---|---|---|
| `{Descriptor}` | Pascal_Snake_Case — words separated by underscores with initial capitals | `Governance_Standard_Naming.md` |

### 3.2 Rules

| Rule | Description |
|---|---|
| R5 | No version suffix in filename (version is in metadata) |
| R6 | No phase or project suffix in filename (e.g., `_PAC2`, `_PG02`) |
| R7 | No prefix numbering unless it's a review work product (see §3.3) |
| R8 | Descriptor must be descriptive: `Governance_Standard_Naming.md`, not `gs04.md` |
| R9 | No UPPER_CASE filenames |

### 3.3 Review Work Products

Review work products in `docs/governance/reviews/` use a prefixed convention:

```
{PG-NN}_{Descriptor}.md
```

| Component | Description | Example |
|---|---|---|
| `{PG-NN}` | PG item identifier | `PG02`, `PG01` |
| `{Descriptor}` | Pascal_Snake_Case | `Current_State_Assessment` |

Example: `PG02_Current_State_Assessment.md`

This exception acknowledges the PG work product convention established during PG-01 and PG-02. New review formats should follow GS-02 document structure; the `PG-NN` prefix provides project grouping within the reviews directory.

---

## 4. Document Titles

### 4.1 Canonical Format

```
# {Descriptor} v{Version}
```

| Component | Description | Example |
|---|---|---|
| `{Descriptor}` | Descriptive title | `Governance Standard — Naming` |
| `v{Version}` | Semantic version (optional for drafts) | `v1.0-draft`, `v1.0` |

### 4.2 Review Work Products

```
# {Scope} — {Review Type}: {Detail}
```

Example: `# PG-02 WP-01: Current State Assessment — Governance Object Index`

---

## 5. Directory Placement

| Directory | Contains |
|---|---|
| `docs/governance/` | Governance documents, standards, charters, registries, acceptance records |
| `docs/governance/reviews/` | Review work products (assessments, reviews, validation reports) |
| `docs/AI/` | AI governance documents |
| `docs/planning/` | Planning documents, roadmaps |
| `docs/PAC/` | PAC discovery artifacts |
| `/` (root) | Project-level reference documents (AGENTS.md, README*.md) |

---

## 6. Existing Namespaces

The PG-02 Framework identified 3 existing identifier namespaces that are preserved:

| Namespace | Type | ID Format | Content-Level | Examples |
|---|---|---|---|---|
| **ADR** | Decision | `ADR-NNN` | Yes | `ADR-007` (pending), `ADR-008` (pending) |
| **PG** | Statement | `PG-NN` | Yes | `PG-01` through `PG-10` |
| **GOV** | Object | `GOV-{TYPE}-{NNN}` | No — document-level | `GOV-CHARTER-001` |

GOV-IDs coexist with content-level identifiers (ADR-NNN, PG-NN). They serve different purposes:
- GOV-IDs identify the document as a governance object
- Content-level identifiers reference concepts within documents

---

## 7. Phased Migration

| Phase | Documents | Requirement | When |
|---|---|---|---|
| **Phase 1** | New PAC-2 docs | Full GS-04 compliance (§2–§5) | Immediate |
| **Phase 2** | Existing docs with `_v1.0` suffix | Metadata version field replaces filename version | Deferred (PAC-1 freeze) |
| **Phase 3** | Existing docs with `_PAC1` / `_PG02` suffix | Metadata replaces filename project indicator | Deferred (PAC-1 freeze) |

---

## 8. Evidence References

| Precedent | Source | What It Proves |
|---|---|---|
| GOV-ID format | `Governance_Object_Index_Framework.md` §2.2 | `GOV-{TYPE}-{NNN}` with 3-digit zero-padding |
| Object type taxonomy | `Governance_Object_Index_Framework.md` §1.2 | 11 type codes with purpose and lifecycle |
| Reviews naming pattern | `docs/governance/reviews/PG02_*` | `PG{NN}_{Descriptor}.md` convention |
| Registry | `Governance_Object_Registry.md` | Working example: 40 objects, 11 types, all with GOV-IDs |

---

## 9. Constraints

| # | Constraint |
|---|---|
| C1 | File naming rules (§3) apply forward; existing PAC-1 files are not renamed |
| C2 | A GOV-ID is assigned once and never reused (R1) |
| C3 | Descriptor must be meaningful — `misc.md` or `temp.md` are not valid governance filenames |
