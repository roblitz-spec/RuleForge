# GS-05: Governance Traceability Standard v1.0-draft

| id | type | status | version | date |
|---|---|---|---|---|
| `GOV-GUIDE-007` | `GUIDE` | `accepted` | `1.0` | `2026-07-29` |

| source | part_of |
|---|---|
| `GOV-REF-007` (Standards Framework) | PAC-2 Standards |

---

## 1. Purpose

Define the standard traceability model for governance documents. This standard codifies the 5 relationship types from the PG-02 Framework (§4) and establishes applicability rules, chain verification, and stale detection procedures.

---

## 2. Relationship Types

Every relationship between governance objects is explicit and declared in metadata. No relationship is inferred from directory location, filename similarity, or content references.

| Type | Direction | Governance Function | Traceability Role |
|---|---|---|---|
| `primary_source` | Upstream | Declares authority derivation | **Vertical**: "Who decided this?" — traces upward |
| `references` | Downstream | Declares evidence citation | **Evidence**: "What supports this?" — traces downward |
| `updates` | Bidirectional | Declares version succession | **Version**: "What did this replace?" — traces backward |
| `depends_on` | Upstream | Declares content validity dependency | **Staleness**: "What must be current?" — propagates staleness |
| `part_of` | Upstream | Declares work package membership | **Project**: "What project produced this?" — groups work products |

---

## 3. Applicability Rules

| Object Type | primary_source | references | updates | depends_on | part_of |
|---|---|---|---|---|---|
| `CONST` | Never | Never | Rarely (amendment) | Never | Never |
| `CHARTER` | Always (to source of authority) | Often (to discovery docs) | Rarely (v2) | Never | Never |
| `ARCH` | Rarely | Often | Sometimes | Never | Never |
| `STATUS` | Never | Often | Sometimes | **Often** (to docs it summarizes) | Never |
| `DEC` | **Always** (to authority) | Often | Never | Never | Never |
| `GOV` | **Always** (to charter) | Often | Never | Never | Never |
| `PLAN` | **Always** (to decision registry) | Often | Sometimes | Sometimes | Never |
| `REC` | Sometimes | Often | Never | Never | Often (to PG item) |
| `REV` | Never | Often (to reviewed artifact) | Never | Never | **Always** (to PG item) |
| `REF` | Often (to source) | Often | Sometimes | Sometimes | Sometimes |
| `GUIDE` | **Always** (to framework) | Often | Never | Never | **Always** (to standards project) |

**Key**: Always = required. Often = recommended when applicable. Sometimes = situation-dependent. Rarely = exceptional. Never = semantically invalid.

---

## 4. Relationship Declaration

Relationships are declared in the metadata header as optional fields:

```markdown
| source | primary_source | depends_on | part_of |
|---|---|---|---|
| `GOV-DEC-002` | `GOV-GOV-001` | `GOV-STATUS-001` | PG-02 |
```

Rules:
- Each relationship field can contain one GOV-ID (exception: `depends_on` allows multiple)
- The target must be a valid, existing GOV-ID
- Circular dependencies are invalid (A → B → A)
- Self-references are invalid (A → A)

---

## 5. Composite Traceability Chains

### 5.1 Authority Chain (`primary_source`)

Traces governance authority from a document to its ultimate source.

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

Each link must be explicitly declared. The chain terminates at a document with no `primary_source`.

### 5.2 Evidence Chain (`references`)

Traces supporting evidence from a document to its sources.

```
GOV-CHARTER-001 (Project Charter)
    ↓ references
GOV-PAC-discovery-1 (14_Alignment_Review.md)  ← content-level reference
    ↓ references
GOV-PAC-discovery-2 (01_Project_Identity.md)  ← content-level reference
```

Evidence references may point to content-level documents (docs/PAC/*) that are not registered governance objects.

### 5.3 Version Chain (`updates`)

Traces version history of a document.

```
GOV-CHARTER-001 v2.0
    ↓ updates
GOV-CHARTER-001 v1.1  (amendment)
    ↓ updates
GOV-CHARTER-001 v1.0  (original)
```

Version chain is declared in the `updates` field. The current version's `predecessor` field points to the immediately previous version.

### 5.4 Staleness Chain (`depends_on`)

Propagates staleness when a dependency changes.

```
GOV-STATUS-002 (AI_HANDOFF)
    ├── depends_on → GOV-STATUS-001 (CURRENT_STATUS)
    ├── depends_on → GOV-ARCH-001 (ARCHITECTURE)
    ├── depends_on → GOV-CONST-001 (DEVELOPMENT_CONSTITUTION)
    ├── depends_on → GOV-CONST-002 (AI_WORKFLOW)
    ├── depends_on → GOV-REF-002 (TEST_STRATEGY)
    └── depends_on → GOV-PLAN-002 (NEXT_MILESTONE)
```

When any dependency's version increments, the dependent document is stale and must be reviewed.

---

## 6. Stale Detection

### 6.1 Algorithm

```
For each document D:
    For each dependency T declared in D.depends_on:
        If T.status == 'superseded' OR T.status == 'deprecated':
            D is STALE (content-level staleness)
        If T.version changed since D was last updated:
            D is POTENTIALLY STALE (review recommended)
```

### 6.2 Verification

Stale detection is performed:
- During WP-06 Validation (mandatory)
- On any document update (recommended)
- On acceptance of any PG item (recommended)

### 6.3 Resolution

| Staleness Level | Action |
|---|---|
| **STALE** | Document must be updated or deprecated; cannot remain `accepted` |
| **POTENTIALLY STALE** | Document should be reviewed; may remain `accepted` with review note |

---

## 7. Circular Dependency Prevention

| Rule | Description |
|---|---|
| T1 | A document's `depends_on` chain must not contain the document itself |
| T2 | A document's `primary_source` chain must not contain the document itself |
| T3 | A → B and B → A via the same relationship type is invalid |
| T4 | Validation (WP-06) must verify T1–T3 for all new or modified relationships |

---

## 8. Evidence References

| Precedent | Source | What It Proves |
|---|---|---|
| 5 relationship types | `Governance_Object_Index_Framework.md` §4.2 | Semantics, direction, traceability role |
| Composite chains | `Governance_Object_Index_Framework.md` §4.3 | Authority, evidence, version, staleness chains with examples |
| Stale propagation | `Governance_Object_Index_Framework.md` §4.6 | Pseudocode algorithm; `depends_on`-based detection |
| Dependency graph | `Governance_Object_Registry.md` §Relationship Index | Working example: AI_HANDOFF → 6 targets |
| Circular prevention | PG-02 Framework §4.5 implicitly | No circular dependencies in PG-02 authority chain |

---

## 9. Constraints

| # | Constraint |
|---|---|
| C1 | Relationships are explicit; no relationship is inferred from content or file location |
| C2 | Circular dependencies are invalid; validation must detect them |
| C3 | Staleness detection is mandatory in WP-06 for documents with `depends_on` declarations |
| C4 | `primary_source` chains must terminate (no infinite chain) |
