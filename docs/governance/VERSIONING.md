# RuleForge Versioning Policy — VERSIONING.md

| id | type | status | version | date |
|---|---|---|---|---|
| `GOV-REF-008` | `REF` | `accepted` | `1.0` | `2026-07-29` |

| source | part_of |
|---|---|
| `GOV-REV-005` (Assessment), `GOV-REV-017` (Review), `GOV-REV-019` (Design Review) | PG-05 |

---

**Authoritative Source**: This document is the single versioning policy for the RuleForge project. It resolves the version identity crisis identified in PG-05 WP-01.

---

## 1. Version Domains

The RuleForge project uses 5 independent version domains. Each domain has a single scheme, a single source of truth, and clear increment rules.

### 1.1 Milestone (`M{N}`)

Tracks development progress. Milestones represent functional completion points.

| Attribute | Value |
|---|---|
| **Scheme** | `M{N}[.{sub}]` — integer major with optional minor |
| **Source of Truth** | `docs/AI/CURRENT_STATUS.md` |
| **Current** | `M8` |
| **Increment Rule** | Major: milestone scope functionally complete. Minor (`.{sub}`): partial milestone checkpoint. |
| **Git Tag** | `M{N}-complete` for completed milestones; checkpoint tags optional |
| **Consumers** | All documents, AI agents, roadmap planning |

### 1.2 Governance Artifact Version (`v{N}.{n}`)

Tracks governance document revisions. Each governance artifact carries its own version.

| Attribute | Value |
|---|---|
| **Scheme** | `v{major}.{minor}` — semantic versioning |
| **Source of Truth** | Document metadata header `version` field |
| **Current** | `1.0` (most documents) |
| **Increment Rule** | Major: content change altering meaning or decisions. Minor: clarification, formatting, non-substantive change. |
| **Naming** | Version in metadata, not filename. Existing `_v1.0.md` filenames are grandfathered. |
| **Consumers** | Registry, validation scripts, reviewers |

### 1.3 Application Version (`v{N}.{n}`)

Display version for the RuleForge application.

| Attribute | Value |
|---|---|
| **Scheme** | `v{major}.{minor}` — semantic versioning |
| **Source of Truth** | `ui/main_window.py` — single constant |
| **Current** | `v0.1` (pre-1.0) |
| **Increment Rule** | Major: breaking API changes or governance baseline milestones. Minor: feature additions. |
| **v1.0 Criteria** | All P0 PG items complete + M8 → M9 transition + governance release accepted |
| **Consumers** | UI, about dialog, external communication |

### 1.4 Serialization Format Version (`N`)

Tracks data format compatibility for serialized files.

| Attribute | Value |
|---|---|
| **Scheme** | Integer |
| **Source of Truth** | `version` field in the serialized file |
| **Current** | `1` (`config/rules.json`) |
| **Increment Rule** | Increment when serialization format changes in a backward-incompatible way |
| **Consumers** | Deserialization code, migration scripts |

### 1.5 AI Protocol Version (`v{N}`)

Tracks AI handoff protocol format.

| Attribute | Value |
|---|---|
| **Scheme** | `v{major}` — major only (protocol changes are breaking) |
| **Source of Truth** | `README_AI.md` and `AI_MEMORY_PACK.md` metadata headers |
| **Current** | `v2.0` |
| **Increment Rule** | Increment when AI handoff protocol format changes |
| **Consumers** | AI agents |

---

## 2. Version Domain Independence

The 5 domains are independent. No cross-domain mapping is required.

| Domain | Scheme | Source of Truth | Current |
|---|---|---|---|
| Milestone | `M{N}` | `CURRENT_STATUS.md` | `M8` |
| Gov Artifact | `v{N}.{n}` | Document metadata | `1.0` |
| Application | `v{N}.{n}` | `ui/main_window.py` | `v0.1` |
| Serialization | `N` | File `version` field | `1` |
| AI Protocol | `v{N}` | `README_AI.md` | `v2.0` |

A consumer needing "what milestone was current when this document was at v1.0?" uses GS-05 traceability, not a version mapping table.

---

## 3. Document Versioning Rules

| # | Rule |
|---|---|
| V1 | Every governance document declares its version in the metadata header `version` field |
| V2 | Version is NOT in the filename for new documents |
| V3 | Major version increment: substantive content change. Minor: clarification or formatting. |
| V4 | A document's version is independent of the milestone it was created under |
| V5 | Version history is documented per GS-02 §2 |

---

## 4. Git Tag Policy

| # | Rule |
|---|---|
| T1 | Only `M{N}-complete` tags are authoritative — they correspond to completed milestones |
| T2 | `M{N}.{sub}` checkpoint tags are informational, not authoritative |
| T3 | Tags beyond the active baseline are grandfathered; new tags are created when milestones complete |
| T4 | Missing tags (M9, M10) indicate milestones that were never formally completed |
| T5 | Tags are immutable — they are never deleted or moved |

### Current Tag Inventory

| Tag | Status |
|---|---|
| M2–M8 | ✅ Authoritative — completed milestones |
| M9, M10 | ❌ Missing — never completed |
| M11.2 | ⚠️ Grandfathered — checkpoint tag |
| M12–M14 | ✅ Authoritative — rule engine feature milestones |
| M15, M16 | ⚠️ Grandfathered — future-looking tags |

---

## 5. Branch Naming Convention

| # | Rule |
|---|---|
| B1 | Branch names reference the target milestone: `m{N}-{description}` |
| B2 | The `M{N}` in a branch name is a target, not a declaration of completion |
| B3 | A branch targeting `M10` is valid even if no `M10-complete` tag exists |
| B4 | Active development branch targets the next milestone |

---

## 6. Deprecation Procedure

| Step | Action |
|---|---|
| 1 | PG item or ADR identifies document for deprecation |
| 2 | Document status updated to `deprecated` in metadata |
| 3 | Registry updated — status → `deprecated` |
| 4 | GS-05 staleness detection triggers for consumers with `depends_on` |
| 5 | After one release cycle, deprecated document may be archived |
| 6 | Archive: move to `docs/archive/` or mark `archived` in registry |

---

## 7. References

| Artifact | GOV-ID | Relationship |
|---|---|---|
| PG-05 WP-01 Assessment | `GOV-REV-005` | `primary_source` |
| PG-05 WP-02 Review | `GOV-REV-017` | `reviewed_by` |
| PG-05 WP-03 Design | *(this document implements the design)* | `implements` |
| PG-05 WP-04 Design Review | `GOV-REV-019` | `reviewed_by` |
| Governance Standards | `GOV-GUIDE-003`–`007` | `conforms_to` |

---

## Version History

| Version | Date | Change |
|---|---|---|
| `1.0` | 2026-07-29 | Initial version — PG-05 WP-05 Implementation |
