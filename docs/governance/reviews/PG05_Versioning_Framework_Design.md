# PG-05 WP-03: Versioning Framework Design v1.0-draft

| id | type | status | version | date |
|---|---|---|---|---|
| `GOV-REF-008` | `REF` | `accepted` | `1.0` | `2026-07-29` |

| source | part_of |
|---|---|
| `GOV-REV-005` (PG-05 WP-01 Assessment), `GOV-REV-017` (PG-05 WP-02 Review) | PG-05 |

---

**Date**: 2026-07-29 | **Phase**: PG-05 WP-03 Framework Design | **Baseline**: Assessment `GOV-REV-005`, Review `GOV-REV-017`

---

## 1. Purpose

Define the ResourceHub Versioning Framework — a single, coherent versioning policy that resolves the 5 conflicting version schemes identified in the WP-01 Assessment. This framework establishes version domains, source-of-truth rules, increment rules, naming conventions, git tag policy, and deprecation procedures.

---

## 2. Design Principles

| # | Principle | Rationale |
|---|---|---|
| P1 | **One domain, one scheme.** Each version domain has exactly one version scheme. No domain uses two schemes. | Resolves F1 (5 schemes, 0 mappings) |
| P2 | **Source of truth is explicit.** Every version is declared in exactly one place. Consumers know where to look. | Resolves F2 (stale references), F5 (no policy) |
| P3 | **Versions are forward-only.** Versions never decrease. Deprecated artifacts are deprecated, not deleted. | Resolves F4 (non-linear tags) |
| P4 | **Compatible with existing baselines.** The framework defines forward conventions. Existing artifacts are grandfathered. | Constraint from PAC-1 freeze |
| P5 | **Minimal mapping.** Domains are independent; no complex cross-domain mapping table. Where mapping exists, it is one-directional. | Resolves G2 (no M↔v mapping) |

---

## 3. Version Domains

The framework defines 5 independent version domains. Each has a single scheme, a single source of truth, and clear increment rules.

### 3.1 Domain: Milestone (M)

| Attribute | Definition |
|---|---|
| **Purpose** | Track development progress. Milestones represent functional completion points. |
| **Scheme** | `M{N}[.{sub}]` — integer major with optional minor |
| **Source of Truth** | `CURRENT_STATUS.md` — the active milestone is declared here |
| **Current** | `M8` (active baseline) |
| **Increment Rule** | Major: when a milestone's scope is functionally complete. Minor (`.{sub}`): when a partial milestone checkpoint is reached. |
| **Example** | `M8` → `M8.1` (checkpoint) → `M9` (next milestone) |
| **Git Tag** | `M{N}-complete` for completed milestones. Checkpoint tags optional. |
| **Consumers** | All documents, AI agents, roadmap planning |

### 3.2 Domain: Governance Artifact Version (v)

| Attribute | Definition |
|---|---|
| **Purpose** | Track governance document revisions. Each governance artifact carries its own version. |
| **Scheme** | `v{major}.{minor}` — semantic versioning for governance documents |
| **Source of Truth** | Document metadata header — `version` field |
| **Current** | Per-document: most are `1.0`; PAC-1 docs are `1.0` |
| **Increment Rule** | Major: content change that alters meaning or decisions. Minor: clarification, formatting, non-substantive change. |
| **Example** | `v1.0` → `v1.1` (clarification) → `v2.0` (substantive revision) |
| **Naming** | Version is in metadata, not in filename. GS-04 §3.2 R5: "No version suffix in filename." Existing `_v1.0.md` files are grandfathered. |
| **Consumers** | Registry, validation scripts, reviewers |

### 3.3 Domain: Application Version

| Attribute | Definition |
|---|---|
| **Purpose** | Display version for the ResourceHub application UI |
| **Scheme** | `v{major}.{minor}` — semantic versioning for the product |
| **Source of Truth** | Single constant in source code (currently `ui/main_window.py:85`) |
| **Current** | `v0.1` (pre-1.0) |
| **Increment Rule** | Major: breaking API changes or governance baseline milestones. Minor: feature additions. |
| **v1.0 Criteria** | All P0 PG items complete + M8 → M9 transition + governance release accepted |
| **Consumers** | UI, about dialog, external communication |

### 3.4 Domain: Serialization Format Version

| Attribute | Definition |
|---|---|
| **Purpose** | Track data format compatibility for serialized files (rules.json, etc.) |
| **Scheme** | Integer (`version: N`) |
| **Source of Truth** | `version` field in the serialized file |
| **Current** | `version: 1` (rules.json) |
| **Increment Rule** | Increment when serialization format changes in a backward-incompatible way |
| **Consumers** | Deserialization code, migration scripts |

### 3.5 Domain: AI Protocol Version

| Attribute | Definition |
|---|---|
| **Purpose** | Track AI handoff protocol format (AI_MEMORY_PACK, README_AI) |
| **Scheme** | `v{major}` — major version only (protocol changes are breaking by definition) |
| **Source of Truth** | `README_AI.md` and `AI_MEMORY_PACK.md` metadata headers |
| **Current** | `v2.0` (declared in `README_AI.md` and `AI_MEMORY_PACK.md`) |
| **Increment Rule** | Increment when the AI handoff protocol format changes |
| **Consumers** | AI agents reading AI_HANDOFF.md, AI_MEMORY_PACK.md |

---

## 4. Version Domain Summary

| Domain | Scheme | Source of Truth | Current | Consumers |
|---|---|---|---|---|
| Milestone | `M{N}` | `CURRENT_STATUS.md` | `M8` | All docs, AI, roadmap |
| Gov Artifact | `v{N}.{n}` | Document metadata | `1.0` (most) | Registry, validation |
| Application | `v{N}.{n}` | `ui/main_window.py` | `v0.1` | UI, external |
| Serialization | `N` (int) | File `version` field | `1` | Code, migration |
| AI Protocol | `v{N}` | `README_AI.md` | `v2.0` | AI agents |

**Key**: The 5 domains are independent. No cross-domain mapping is required. If a consumer needs to know "what milestone was current when this document was at v1.0?", that is a traceability question (GS-05), not a versioning question.

---

## 5. Resolution of Assessment Findings

| # | Finding | Resolution |
|---|---|---|
| F1 | 5 version schemes, 0 mappings | 5 independent domains defined; no mapping needed — domains serve different purposes |
| F2 | 7 docs with stale milestone refs | M8 declared as active baseline in CURRENT_STATUS.md; stale docs will be updated by PG-03, PG-06, PG-10 |
| F3 | Dual CURRENT_STATUS | PG-10 deprecates `development/current_status.md`; `docs/AI/CURRENT_STATUS.md` is sole source |
| F4 | Non-linear git tags | Git tag policy (§7): only `M{N}-complete` tags are authoritative; existing tags grandfathered |
| F5 | No versioning policy | This document IS the versioning policy |
| F6 | Inconsistent naming | GS-04 already defines naming; version suffix removed from new filenames; existing `_v1.0` grandfathered |
| F7 | AI Memory v2.0 drift | AI protocol domain (§3.5) — `v2.0` is a protocol version, not a milestone reference; clarified |
| F8 | README_AI path mismatch | Not a versioning issue — PG-06 will fix the path |
| F9 | Window title v0.1 | Application version domain (§3.3) — `v0.1` is the correct pre-1.0 version; no change needed |
| F10 | Branch name M10 | Branch naming convention (§8) — branch names reference target milestones; M10 tag doesn't need to exist |

---

## 6. Resolution of Assessment Gaps

| # | Gap | Resolution |
|---|---|---|
| G1 | No versioning policy | This document (`GOV-REF-008` → future VERSIONING.md) |
| G2 | No M↔v mapping | Mapping is unnecessary — M (milestone) and v (governance) are independent domains. Consumers query the domain they need. |
| G3 | No version increment rules | Defined per domain (§3.1–§3.5) |
| G4 | No lifecycle stage definitions | GS-02 §5 already defines lifecycle stages (draft → review → accepted → superseded → deprecated → archived) |
| G5 | No deprecation procedure | Deprecation procedure (§9): PG item → ADR → status update → registry sync |
| G6 | No git tag policy | Git tag policy (§7) |
| G7 | No document versioning convention | Governance artifact version domain (§3.2): metadata `version` field; GS-04 naming rules |

---

## 7. Git Tag Policy

| Rule | Description |
|---|---|
| T1 | **Authoritative tags**: Only `M{N}-complete` tags are authoritative. These correspond to completed milestones. |
| T2 | **Optional checkpoint tags**: `M{N}.{sub}` tags may exist for partial milestone checkpoints. They are informational, not authoritative. |
| T3 | **Future tags**: Tags beyond the active baseline (M12–M16) are grandfathered. New tags are created when milestones complete, not in advance. |
| T4 | **Missing tags**: M9 and M10 have no `-complete` tags. This is correct — these milestones were never formally completed. |
| T5 | **Tag immutability**: Tags are never deleted or moved. The commit they point to is permanent. |

### Git Tag Inventory

| Tag | Status | Notes |
|---|---|---|
| M2–M8 | ✅ Authoritative | Completed milestones |
| M9, M10 | ❌ Missing | Never completed — correct |
| M11.2 | ⚠️ Grandfathered | Checkpoint tag; exists but not authoritative |
| M12–M14 | ✅ Authoritative | Rule engine milestones (M8 baseline, these are feature tags) |
| M15, M16 | ⚠️ Grandfathered | Future-looking tags |

---

## 8. Branch Naming Convention

| Rule | Description |
|---|---|
| B1 | Branch names reference the milestone they target: `m{N}-{description}` |
| B2 | The `M{N}` in a branch name is a target, not a declaration. It means "working toward M{N}", not "M{N} is complete." |
| B3 | A branch named `m10-*` is valid even if no `M10-complete` tag exists. The branch target and tag existence are independent. |
| B4 | Active development branch targets the next milestone. |

---

## 9. Deprecation Procedure

| Step | Action |
|---|---|
| 1 | PG item or ADR identifies document for deprecation |
| 2 | Document status updated to `deprecated` in metadata |
| 3 | Registry updated (status → `deprecated`) |
| 4 | GS-05 staleness detection triggers for consumers with `depends_on` |
| 5 | After one release cycle, deprecated document may be archived |
| 6 | Archive: move to `docs/archive/` or mark as `archived` in registry |

---

## 10. Document Versioning Rules

| Rule | Description |
|---|---|
| V1 | Every governance document declares its version in the metadata header `version` field |
| V2 | Version is NOT in the filename for new documents (GS-04 §3.2 R5) |
| V3 | Version increment rules per domain §3.2 |
| V4 | A document's version is independent of the milestone it was created under |
| V5 | Version history is documented in the document's Version History section (GS-02 §2) |

---

## 11. Implementation Notes for WP-05

| # | Action |
|---|---|
| IMP1 | Create `VERSIONING.md` at `docs/governance/VERSIONING.md` containing this framework |
| IMP2 | Register `VERSIONING.md` in Governance Object Registry |
| IMP3 | No modification to existing documents required (grandfathering per P4) |
| IMP4 | PG-06 (AI_HANDOFF) should reference this policy when updating milestone references |
| IMP5 | PG-10 (deprecation) follows §9 procedure |

---

## 12. Operational Friction Record (WP-03)

| # | Friction | Severity | Context |
|---|---|---|---|
| F-WP03-1 | **No pre-existing VERSIONING.md template.** GS-02 defines document structure but not versioning-specific sections. The design had to define its own section structure within GS-02 constraints. | LOW | Acceptable — GS-02 is intentionally generic; domain-specific documents define their own body sections. |
| F-WP03-2 | **G2 resolution is a non-resolution.** "No M↔v mapping needed" is correct architecturally (domains are independent) but may disappoint consumers who expected a lookup table. | LOW | Documented in design rationale. Independent domains are cleaner than a mapping table that would immediately go stale. |

**No governance deficiencies or execution blockers. No modifications to GOM, GCAM, or Standards required.**

---

## 13. GCAM Activation Record

| Capability | Activated? | Justification |
|---|---|---|
| Core: Evidence Management | ✅ | Assessment + review are evidence |
| Core: Governance Registry | ✅ | GOV-REF-008 will be registered |
| Core: Basic Traceability | ✅ | `source`, `part_of` declared |
| Core: Governance Standards | ✅ | GS-01 §2.3 format followed |
| Core: Decision Records | ✅ | Design decisions documented in §2 |
| Core: Document Lifecycle | ✅ | `v1.0-draft` status |
| Growth: GS-03 Formal Review | — | WP-04 will apply this |
| Growth: CAR/CMP | — | Not needed — no capability reassignment |
| Enterprise: Any | — | Not applicable at Small+Low |

**GCAM activation: Core only. Correct for Small+Low per Scenario A.**

---

## 14. GOM Gate Record

| Gate | Status | Notes |
|---|---|---|
| G1 (Evidence Complete) | ✅ | WP-01 assessment passed WP-02 review |
| G2 (Scope Confirmed) | — | Not activated per GCAM (Single maintainer, no scope contest) |
| G3 (Architecture Approved) | — | Not activated — no CAR needed for PG-05 WP-03 |
| G4 (Migration Approved) | — | Not activated — no CMP needed |
| G5 (Implementation Authorized) | — | WP-04 Review controls this |
| G6 (Validation Passed) | — | WP-06 |
| G7 (Release Approved) | — | WP-07 |

---

## 15. Decision Gate Exercise Summary

| Finding | Detail |
|---|---|
| Gates applicable to WP-03 | G1 only (evidence must be complete before design) |
| Gates deferred per GCAM | G2–G4 (Growth capabilities, not activated at Small+Low) |
| Gates pending | G5–G7 (future WPs) |
| Governance bypass? | No — G1 was satisfied via WP-02 PASS decision |

---

## 16. Exit Criteria

| # | Criterion | Status |
|---|---|---|
| E1 | All 10 assessment findings resolved | ✅ §5 |
| E2 | All 7 assessment gaps resolved | ✅ §6 |
| E3 | All 10 WP-02 design requirements addressed | ✅ D1–D10 mapped to framework sections |
| E4 | Design follows GS-01 §2.3 format | ✅ Purpose, principles, specification, decisions, constraints, exit criteria |
| E5 | Design is a specification, not implementation | ✅ Implementation notes in §11; actual creation is WP-05 |
| E6 | GOM/GCAM/Standards not modified | ✅ Confirmed in §12 |

---

## Next Phase

```
PG-05 WP-04: Design Review
```

**Versioning Framework Design complete. Ready for Design Review.**
