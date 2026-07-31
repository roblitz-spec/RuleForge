# GS-02: Governance Document Standard v1.0-draft

| id | type | status | version | date |
|---|---|---|---|---|
| `GOV-GUIDE-004` | `GUIDE` | `accepted` | `1.0` | `2026-07-29` |

| source | part_of |
|---|---|
| `GOV-REF-007` (Standards Framework) | PAC-2 Standards |

---

## 1. Purpose

Define the canonical structure for all governance documents created under PAC-2. This standard resolves the 3 competing conventions identified in the WP-01 Assessment (F2-01) by establishing a single format derived from the PG-02 Framework metadata model.

---

## 2. Canonical Document Structure

Every governance document follows this structure:

```
┌─────────────────────────────────┐
│ 1. Title (# H1)                 │  ← GS-04 defines title format
├─────────────────────────────────┤
│ 2. Metadata Header (tables)     │  ← Required: id, type, status, version, date
│                                 │  ← Optional: source, predecessor, part_of, etc.
├─────────────────────────────────┤
│ 3. Context Subtitle             │  ← Optional: Date | Phase | Baseline
├─────────────────────────────────┤
│ 4. Purpose                      │  ← Required: what this document is for
├─────────────────────────────────┤
│ 5. Content Sections             │  ← Required: document body
├─────────────────────────────────┤
│ 6. Version History              │  ← Optional for new documents; required
│                                 │    after first revision
└─────────────────────────────────┘
```

---

## 3. Metadata Header

### 3.1 Required Fields

Every governance document must include the required metadata table immediately after the title:

```markdown
# {Title}

| id | type | status | version | date |
|---|---|---|---|---|
| `GOV-{TYPE}-{NNN}` | `{TYPE}` | `{status}` | `{version}` | `{YYYY-MM-DD}` |
```

| Field | Description | Example |
|---|---|---|
| `id` | GOV-ID per GS-04 | `GOV-CHARTER-001` |
| `type` | Object type per GS-04 | `CHARTER`, `DEC`, `REV` |
| `status` | Lifecycle stage | `draft`, `review`, `accepted`, `superseded`, `deprecated`, `archived` |
| `version` | Semantic version per PG-01 | `0.1`, `1.0`, `1.1` |
| `date` | Last modification date | `2026-07-29` |

### 3.2 Optional Fields

Optional metadata is placed in a second table after the required table:

```markdown
| source | predecessor | part_of |
|---|---|---|
| `GOV-XXX-NNN` | `GOV-YYY-NNN` | PG-NN |
```

| Field | When to Use |
|---|---|
| `source` | When the document is derived from another governance object |
| `predecessor` | When superseding an earlier version |
| `part_of` | When the document belongs to a work package or project |
| `depends_on` | When validity depends on another document (GS-05) |
| `primary_source` | When authority derives from another document (GS-05) |
| `references` | When citing other documents (GS-05) |

### 3.3 Metadata Placement

The metadata header is placed:
- **Immediately after the H1 title** (no intervening content)
- **Before the Purpose section**
- **Before any historical subtitle** (e.g., PAC-1 `**Status**: Accepted v1.0` lines)

Existing documents with historical subititles (PAC-1 format) retain those subititles below the metadata header as historical context.

---

## 4. Content Sections

### 4.1 Required: Purpose

Every document begins with a `## Purpose` section explaining what the document is for, who uses it, and why it exists.

### 4.2 Document Body

Content sections follow the Purpose. Section structure is not prescribed — sections depend on the document type. However:

- `##` is the standard heading level for content sections
- `###` is used for subsections
- Numbered sections (§1, §1.1, §2) are permitted but not required

---

## 5. Document Lifecycle

Documents progress through status stages:

```
draft → review → accepted → superseded → deprecated → archived
                                                         ↑
                                                    (any stage)
```

| Stage | Meaning | Version | When |
|---|---|---|---|
| `draft` | Work in progress; not reviewed | `0.x` | During WP-03 and WP-05 |
| `review` | Under formal review | `0.x` | During WP-02, WP-04, WP-06 |
| `accepted` | Approved and operational | `≥1.0` | After WP-07 |
| `superseded` | Replaced by newer version | Frozen | When a new version is accepted |
| `deprecated` | No longer used; retained for history | Frozen | When the document is no longer needed |
| `archived` | Moved to archive | Frozen | When deprecated and no longer referenced |

---

## 6. AI Document Minimum Metadata

AI governance documents in `docs/AI/` are exempt from full section standardization but must include a minimum metadata header:

```markdown
# {Title}

| id | type | status | version | date |
|---|---|---|---|---|
| `GOV-{TYPE}-{NNN}` | `{TYPE}` | `accepted` | `1.0` | `YYYY-MM-DD` |
```

AI docs are not required to restructure their content. The minimum metadata header enables registry integration without forcing AI docs to conform to the full governance document structure.

---

## 7. Phased Migration

| Phase | Documents | Requirement | When |
|---|---|---|---|
| **Phase 1** | New PAC-2 governance docs | Full GS-02 compliance (§2–§5) | Immediate |
| **Phase 2** | Existing AI docs (17) | Minimum metadata header only (§6) | During PG-06/PG-07 |
| **Phase 3** | PAC-1 Accepted v1.0 docs | Reference only — no modification | Deferred |

---

## 8. Evidence References

| Precedent | Source | What It Proves |
|---|---|---|
| PG-02 metadata format | `Governance_Object_Index_Framework.md` §3.5 | Metadata header format with 6 required fields |
| PG-02 metadata schema | `Governance_Object_Index_Framework.md` §3.3 | Field selection rationale for required/optional |
| PG-02 lifecycle stages | `Governance_Object_Index_Framework.md` §3.4 | 6 lifecycle stages mapped to version ranges |
| 6 PG-02 docs | PAC2_Project_Charter, PG01/02 reviews, framework | Working examples of metadata header format |

---

## 9. Constraints

| # | Constraint |
|---|---|
| C1 | This standard applies forward; it does not mandate retroactive restructuring of PAC-1 accepted documents |
| C2 | Minimum metadata (§6) is the only variance permitted; all new governance documents follow §2–§5 |
| C3 | The metadata header must be parseable as a Markdown table; embedded fields in prose are not valid metadata |
