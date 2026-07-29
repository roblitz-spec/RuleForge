# PG-01 WP-01: Current State Assessment — Governance Versioning

| id | type | status | version | date |
|---|---|---|---|---|
| `GOV-REV-005` | `REV` | `accepted` | `1.0` | `2026-07-29` |

| part_of |
|---|
| PG-01 |

**Date**: 2026-07-29 | **Phase**: PAC-2 P0 Discovery | **Reference**: PG-05 (`Governance_Resolution_v1.0.md`)

---

## Purpose

Assess the current state of version identification, lifecycle tracking, naming conventions, and cross-reference integrity across the ResourceHub repository. This assessment establishes the factual baseline for the Versioning Framework design. It does not propose policies or make decisions.

---

## Assessment Scope

| Dimension | Scope |
|---|---|
| **Repository** | `/projects/ResourceHub` (full tree, excluding `.git/`, `__pycache__/`) |
| **Document types** | Markdown (`.md`), Python (`.py`), JSON (`.json`) |
| **Version indicators** | Semantic version strings, milestone labels, lifecycle status tags, file naming conventions |
| **Excluded** | `docs/PAC/` (frozen evidence), `dist/`, `build/`, `.agent_tmp/` |

---

## Repository Inventory

| Category | Count | Files |
|---|---|---|
| AI governance docs | 17 | `docs/AI/*.md` |
| Governance docs | 8 | `docs/governance/*.md` |
| Planning docs | 1 | `docs/planning/*.md` |
| Root-level docs | 5 | `AGENTS.md`, `README.md`, `README_AI.md`, `README_BUILD.md`, `Governance_Integration_Report.md` |
| Development status | 1 | `docs/development/current_status.md` |
| Python source | 54 | `*.py` across 14 packages |
| Config files | 2 | `config/rules.json`, `requirements.txt` |
| Git tags | 14 | `M2`–`M8`, `M11.2`, `M12`–`M16` |

---

## Current Version Status

### Version Identifiers in Use

| Identifier | Location | Context | Meaning |
|---|---|---|---|
| `v0.1` | `ui/main_window.py:85` | Window title (`ResourceHub v0.1`) | Application display version |
| `v1.0` | `docs/governance/*.md` (4 files) | Document status headers | Governance artifact version |
| `v2.0` | `README_AI.md:3`, `AI_MEMORY_PACK.md:5` | AI memory format version | AI handoff protocol version |
| `version: 1` | `config/rules.json:2` | JSON schema version | Serialization format version |
| `M8 (M8-complete)` | `CURRENT_STATUS.md`, `AI_HANDOFF.md` | Active baseline | Milestone label |
| `M11.1` | `AI_MEMORY_PACK.md`, `development/current_status.md` | Stale milestone | Former planning label |
| `M11.2` | `PROJECT_BRIEF.md`, `CHANGELOG_AI.md`, `ARCHITECTURE.md` | Stale milestone | Former planning label |
| `M15 RC` | `CHANGELOG_AI.md`, `AI_MEMORY_PACK.md` | Stale milestone | Former planning label |
| `M16` | `CHANGELOG_AI.md`, `AI_MEMORY_PACK.md`, `AGENTS.md`, `git tag` | Stale milestone | Former planning label |

### Version Conflict Matrix

| Conflict | Evidence A | Evidence B | Severity |
|---|---|---|---|
| App version vs governance version | `v0.1` (UI title) | `v1.0` (governance acceptance) | **HIGH** |
| Actual baseline vs stale docs | `M8` (CURRENT_STATUS, git tag) | `M11.2` (PROJECT_BRIEF, development/current_status) | **HIGH** |
| AI Memory format vs app version | `v2.0` (AI memory) | `v0.1` (app), `v1.0` (gov) | **MEDIUM** |
| Serialization version independent | `version: 1` (rules.json) | No other version shares this scheme | **LOW** |
| Dual CURRENT_STATUS | `docs/AI/CURRENT_STATUS.md` (M8) | `docs/development/current_status.md` (M11.2) | **HIGH** |

**5 distinct version schemes across the repository; no single master version identifier.**

---

## Current Lifecycle Status

### Document Freshness

| Document | Claims | Actual Baseline | Status |
|---|---|---|---|
| `CURRENT_STATUS.md` | M8 | M8 | ✅ Current |
| `AI_HANDOFF.md` | M8 | M8 | ✅ Current (updated during PAC-1 Integration) |
| `CHANGELOG_AI.md` | M8–M16 | M8 | ✅ Current (M8 entry), ⚠️ future entries exist |
| `DECISION_LOG.md` | ADRs M12–M16 | M8 | ⚠️ References future milestones |
| `ARCHITECTURE.md` | M11.1 | M8 | ❌ Stale |
| `PROJECT_BRIEF.md` | M11.2 | M8 | ❌ Stale |
| `AI_MEMORY_PACK.md` | M11.1, M15 RC, M16 | M8 | ❌ Stale |
| `NEXT_MILESTONE.md` | M7 (completed) | M8 | ❌ Stale (M8 not listed) |
| `KNOWN_LIMITATIONS.md` | Undated | — | ❌ Stale (missing M8 limitations) |
| `development/current_status.md` | M11.2 | M8 | ❌ Stale (PG-10) |
| `README_AI.md` | v2.0 protocol | — | ⚠️ References stale `docs/AI/README_AI.md` path |

**Summary**: 3 current, 2 partially current, 6 stale (out of 11 tracked docs). Staleness rate: **55%**.

### Git Tag Linearity

```
M2 → M3 → M4 → M4.1 → M5 → M6 → M7 → M8 → [gap] → M11.2 → M12 → M13 → M14 → M15 → M16
```

| Anomaly | Detail |
|---|---|
| Missing M9 | No `M9-complete` tag, but M8→M11.2 jump |
| Missing M10 | No `M10-complete` tag, but M8→M11.2 jump |
| Non-linear numbering | M11.2 exists between M8 and M12, but M9–M10 are absent |
| Future tags | M12–M16 tags exist but M8 is the active baseline |
| Branch name | `m10-phase3a-rule-analysis` (references M10, which has no tag) |

---

## Naming Convention Assessment

### Document Naming Patterns

| Pattern | Used By | Example |
|---|---|---|
| `*_v1.0.md` | Governance docs (4) | `Project_Charter_v1.0.md` |
| `*_PAC1.md` | Governance reports (3) | `Governance_Acceptance_PAC1.md` |
| `*_PAC2.md` | PAC-2 docs (1) | `PAC2_Project_Charter.md` |
| `UPPER_CASE.md` | AI docs (17) | `CURRENT_STATUS.md` |
| `XX_Title.md` | PAC docs (14) | `01_Project_Identity.md` |
| No version suffix | Planning (1), AI docs (17) | `Roadmap_Refresh.md` |

| Issue | Evidence |
|---|---|
| Version suffix only on governance docs | AI docs and planning docs have no version identifier in filename |
| PAC phase embedded in filename | `PAC1_*`, `PAC2_*` — but AI docs have no phase marker |
| No semantic versioning | `v1.0` is a governance artifact version, not a product version |
| AI Memory `v2.0` doesn't match its own content | Claims v2.0 but describes M11.1 (stale), not a protocol version |

### Milestone Naming

| Pattern | Used By | Example |
|---|---|---|
| `M{N}` | Git tags, CHANGELOG, most docs | `M8`, `M12` |
| `M{N}.{sub}` | Git tags, CHANGELOG | `M4.1`, `M11.2` |
| `M{N} RC` | CHANGELOG, AI_MEMORY_PACK | `M15 RC` |
| `M{N} Phase {X}{Y}` | Branch name | `m10-phase3a-rule-analysis` |

**No documented convention for when to use M vs M.x vs M RC.**

---

## Traceability Assessment

### Cross-Reference Integrity

| Reference Pattern | Count | Integrity |
|---|---|---|
| Internal doc refs (governance chain) | 6 | ✅ All resolve (Resolution→Charter→Baseline→Registry→Roadmap) |
| PAC-1 evidence refs | ~30 | ✅ All point to existing `docs/PAC/` files |
| AI doc cross-refs | ~50 | ⚠️ Some reference stale content (`AI_MEMORY_PACK.md` → M11.1, `README_AI.md` → `docs/AI/README_AI.md` which doesn't exist) |
| Code-to-doc refs | 0 | N/A — no code references governance docs |
| Governance-to-code refs | 5 | ✅ (D-11 through D-18 point to existing source files) |

| Broken Reference | Source | Target | Issue |
|---|---|---|---|
| `README_AI.md` path | `AI_HANDOFF.md:4`, `AI_MEMORY_PACK.md:84` | `docs/AI/README_AI.md` | File at repo root `/README_AI.md`, not `docs/AI/` |
| Stale milestone ref | `PROJECT_BRIEF.md:13` | Claims M11.2 | Actual baseline is M8 |
| Stale milestone ref | `AI_MEMORY_PACK.md:11` | Claims M11.1 | Actual baseline is M8 |

### Version Source of Truth

| Question | Answer |
|---|---|
| Is there a single version source of truth? | **No** |
| How many places define "the current version"? | **5**: UI title (`v0.1`), CURRENT_STATUS (`M8`), PROJECT_BRIEF (`M11.2`), development/current_status (`M11.2`), AI_MEMORY_PACK (`M11.1`) |
| Which is authoritative? | `CURRENT_STATUS.md` (M8) per Governance Baseline, but this is not stated in any versioning policy |

---

## Findings

| # | Finding | Severity | Evidence |
|---|---|---|---|
| F1 | **Version identity crisis**: 5 different version indicators (v0.1, v1.0, v2.0, version:1, M8) with no mapping between them | **HIGH** | § Version Identifiers |
| F2 | **Stale milestone references**: 7 docs reference M11.1/M11.2/M12/M15/M16, but M8 is the active baseline | **HIGH** | § Document Freshness |
| F3 | **Dual CURRENT_STATUS**: Two files claim to be the project status document | **HIGH** | PG-10, § Document Freshness |
| F4 | **Non-linear git tags**: M9–M10 missing; M11.2–M16 exist beyond M8 baseline | **MEDIUM** | § Git Tag Linearity |
| F5 | **No versioning policy**: No document defines how versions are assigned, incremented, or mapped | **HIGH** | § Version Source of Truth |
| F6 | **Inconsistent naming conventions**: Governance docs use `_v1.0`; AI docs and planning docs do not | **MEDIUM** | § Naming Convention Assessment |
| F7 | **AI Memory version drift**: `v2.0` claims to be a protocol version but describes stale milestone content | **MEDIUM** | § Naming Convention Assessment |
| F8 | **README_AI.md path mismatch**: Referenced as `docs/AI/README_AI.md` but located at repo root | **LOW** | § Cross-Reference Integrity |
| F9 | **Window title frozen at v0.1**: `ui/main_window.py` hardcodes `ResourceHub v0.1`; this has never been updated | **MEDIUM** | § Version Identifiers |
| F10 | **Branch name references M10**: Active branch is `m10-phase3a-rule-analysis` but no `M10-complete` git tag exists | **LOW** | § Git Tag Linearity |

---

## Gaps

| # | Gap | Impact |
|---|---|---|
| G1 | No versioning policy document | Every version decision is ad-hoc; no criteria for v1.0 |
| G2 | No M↔v mapping | "M8" and "v0.1" describe the same project with no relationship defined |
| G3 | No version increment rules | When does M8 become M9? When does v0.1 become v1.0? |
| G4 | No lifecycle stage definitions | "Stable," "Frozen," "Accepted," "Complete" used interchangeably |
| G5 | No deprecation procedure | `development/current_status.md` is known-stale (PG-10) but no formal deprecation exists |
| G6 | No git tag policy | Why do M12–M16 tags exist if M8 is the baseline? Are they forward-planning or abandoned? |
| G7 | No document versioning convention | Only governance docs carry a version suffix; no rules for when to increment |

---

## Risks

| # | Risk | Likelihood |
|---|---|---|
| R1 | New contributor reads `PROJECT_BRIEF.md` or `AI_MEMORY_PACK.md` and develops against M11.2, not M8 | **High** — 55% of tracked docs are stale |
| R2 | Governance acceptance (`v1.0`) is misinterpreted as product v1.0 | **Medium** — same version string, different meanings |
| R3 | M12–M16 tags are accidentally used as baselines for new work | **Low** — tags exist but no branch uses them |
| R4 | Version conflict blocks PAC-2 consistency automation | **Medium** — automated checks will fail if "current" version is ambiguous |

---

## Assessment Summary

| Dimension | Status | Key Issue |
|---|---|---|
| Version identifiers | ❌ **Conflicted** | 5 schemes, 0 mappings |
| Document freshness | ❌ **Fragmented** | 55% staleness rate |
| Milestone linearity | ❌ **Non-linear** | M9–M10 missing; M11.2–M16 beyond baseline |
| Naming conventions | ⚠️ **Inconsistent** | Governance uses `_v1.0`, others do not |
| Cross-reference integrity | ⚠️ **Mostly intact** | 2 broken refs, 1 path mismatch |
| Lifecycle tracking | ❌ **No standard** | Terms overlap with no definitions |
| Source of truth | ❌ **None** | 5 places claim "current version" |

---

## Next Step

This assessment is a factual baseline. It does not propose solutions. The Versioning Framework Design (PG-05) will use these findings to define:

1. A single version source of truth
2. Version increment rules
3. Document naming conventions
4. Lifecycle stage definitions
5. Git tag policy
6. Deprecation procedure

**Assessment complete. Ready for Framework Design.**
