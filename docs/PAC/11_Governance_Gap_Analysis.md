# 11 — Governance Gap Analysis

**PAC-1 Phase 2 | Date: 2026-07-24**

Identifying missing governance artifacts. This document does NOT create them.

---

## Primary Gaps

### G-01: Missing Project Charter

| Field | Value |
|---|---|
| Current Situation | No document defines the project's mission, scope, stakeholders, or success criteria. The closest documents are `PROJECT_BRIEF.md` (22 lines, M11.2 stale) and `README.md` (16 lines, minimal). |
| Evidence | `PROJECT_BRIEF.md` describes "what" but not "why." No stakeholder identification. No scope boundaries. No success criteria. |
| Potential Risk | Without a charter: feature creep, stakeholder misalignment, unclear M9 scope, inability to evaluate "done." |
| Suggested Artifact | `docs/PROJECT_CHARTER.md` — mission, scope, stakeholders, success criteria, non-goals. |

**Confidence**: HIGH

---

### G-02: Missing Master Design Document

| Field | Value |
|---|---|
| Current Situation | `editor/__init__.py`, `editor/domain_validator.py`, and `editor/edit_session.py` reference a "Master Design" document with specific sections (Section 3, AD-03, Section 4.1). This document is not in the repository. |
| Evidence | 3 source file docstrings with section references. 26 repository documents searched — no match. |
| Potential Risk | 382 lines of production code cannot be fully understood. New developers cannot onboard to the Rule IDE subsystem. Architecture rationale for `editor/` package is undocumented. |
| Suggested Artifact | `docs/design/MASTER_DESIGN.md` — Rule IDE architecture: EditSession lifecycle, DomainValidator design, Editor Core layer. Either locate existing document or reconstruct from code + module docstrings. |

**Confidence**: HIGH

---

### G-03: Missing Product Roadmap

| Field | Value |
|---|---|
| Current Situation | Planning horizon is 1 milestone only (`NEXT_MILESTONE.md`). No multi-milestone roadmap exists. No release planning. No feature sequencing beyond "P1, P2, P4." |
| Evidence | `NEXT_MILESTONE.md` lists 4 candidate features. `CURRENT_STATUS.md` tracks deferred debt. No document connects these into a sequenced plan. |
| Potential Risk | M9 → M10 → M11 decisions are ad-hoc. Priority conflicts between Filter (P1) and Rule IDE (AI_HANDOFF) cannot be resolved without a roadmap. |
| Suggested Artifact | `docs/ROADMAP.md` — M9 through M12 candidate features with sequencing rationale, dependencies, and release criteria. |

**Confidence**: HIGH

---

### G-04: Missing Versioning Policy

| Field | Value |
|---|---|
| Current Situation | Window title says "v0.1." Milestones use M-numbering. Tags use "Mxx-complete." No documented relationship between these systems. No v1.0 criteria. |
| Evidence | `ui/main_window.py:85`: "ResourceHub v0.1". No versioning document exists. No semver/calver declaration. No release checklist. |
| Potential Risk | Cannot answer "when is it 1.0?" Cannot communicate version to users. Milestone numbering and version numbering are disconnected. |
| Suggested Artifact | `docs/VERSIONING.md` — version scheme (semver?), milestone-to-version mapping, v1.0 exit criteria. |

**Confidence**: HIGH

---

### G-05: Missing ADR for `editor/` Package

| Field | Value |
|---|---|
| Current Situation | The `editor/` package (EditSession, DomainValidator) represents a significant architectural decision — creating a UI-independent editing layer. No ADR documents this. |
| Evidence | 6 ADRs exist (ADR-001 through ADR-006). None cover the `editor/` package or the Rule IDE layering decision. |
| Potential Risk | Architectural rationale for the `editor/` layer is lost. Future developers may not understand why `DomainValidator` exists separately from `validator/`. |
| Suggested Artifact | `ADR-007` in `DECISION_LOG.md` — "Editor Layer Separation: UI-independent rule editing via `editor/` package." |

**Confidence**: HIGH

---

### G-06: Missing ADR for Preset Architecture

| Field | Value |
|---|---|
| Current Situation | M8 added `PresetStore` as a separate persistence layer with `RuleRepository` as runtime truth. This architectural decision is documented in `AGENTS.md` and `M8_COMPLETION.md` but not in `DECISION_LOG.md` as a formal ADR. |
| Evidence | `AGENTS.md` § Rule Presets § 架构约束 documents the architecture. `M8_COMPLETION.md` § Architecture Compliance documents the invariants. But no ADR in DECISION_LOG.md. |
| Potential Risk | ADR registry is incomplete. Future architecture changes to persistence may not have the full decision context. |
| Suggested Artifact | `ADR-008` in `DECISION_LOG.md` — "Preset Architecture: Repository as runtime truth, PresetStore as persistence, Settings as metadata." |

**Confidence**: MEDIUM (decision is documented elsewhere, but not in the ADR registry)

---

### G-07: Missing Milestone Completion Records (M2–M5, M9–M11.1, M12–M16)

| Field | Value |
|---|---|
| Current Situation | Only M6 (`M6_COMPLETION.md`, `REVIEW_M6.md`) and M8 (`M8_COMPLETION.md`) have completion records. M2–M5, M9–M11.1, and M12–M16 have none. |
| Evidence | `docs/AI/` contains `M6_COMPLETION.md` and `M8_COMPLETION.md`. `git tag -l` shows 15 tags. 13 tags lack completion records. |
| Potential Risk | Incomplete project history. Cannot reconstruct decision rationale for earlier milestones. M12–M16 (earlier branch) have no records at all. |
| Suggested Artifact | Completion records for remaining milestones. Priority: M9–M11.1 (current branch gap), M12–M16 (earlier branch, may be lower priority). |

**Confidence**: HIGH

---

### G-08: Missing Release Process

| Field | Value |
|---|---|
| Current Situation | No release checklist, no release cadence, no packaging verification process, no changelog for end-users. |
| Evidence | `scripts/build.py` handles packaging. `README_BUILD.md` describes the build. No release process document exists. `CHANGELOG_AI.md` is AI-facing, not user-facing. |
| Potential Risk | Cannot ship. No verification that packaged build works. No user communication process. |
| Suggested Artifact | `docs/RELEASE_PROCESS.md` — packaging, smoke test, changelog generation, distribution. |

**Confidence**: HIGH

---

### G-09: Missing Decision Ownership

| Field | Value |
|---|---|
| Current Situation | Decisions are made in AI sessions. No documented ownership for architectural decisions, milestone scope, or feature prioritization. |
| Evidence | All ADRs say "Accepted" but none say "Accepted by [person/role]." M6 review was "Independent Reviewer" (unidentified). No decision authority matrix exists. |
| Potential Risk | Unclear who can approve M9 scope, resolve product naming, or authorize Rule IDE transition. |
| Suggested Artifact | `docs/GOVERNANCE.md` — decision authority matrix: who decides what. |

**Confidence**: MEDIUM

---

### G-10: Missing Contributor Guide

| Field | Value |
|---|---|
| Current Situation | `README_AI.md` covers AI session onboarding. No guide for human contributors: setup, coding conventions, PR process, review expectations. |
| Evidence | `README.md` is 16 lines. `README_AI.md` is AI-focused. No CONTRIBUTING.md. No CODEOWNERS. |
| Potential Risk | Human contributors cannot onboard without AI assistance. Bus factor = 1. |
| Suggested Artifact | `CONTRIBUTING.md` — environment setup, coding conventions (from DEVELOPMENT_CONSTITUTION), test expectations, PR process. |

**Confidence**: HIGH

---

### G-11: Missing M8 Known Limitations in KNOWN_LIMITATIONS.md

| Field | Value |
|---|---|
| Current Situation | `KNOWN_LIMITATIONS.md` was not updated after M8. M8 introduced 4 documented limitations: no bidirectional preset sync, no merge/partial load, no import/export, no preset description editing in toolbar. |
| Evidence | `docs/AI/M8_COMPLETION.md` § Known Limitations lists 4 items. `docs/AI/KNOWN_LIMITATIONS.md` has no preset-related entries. |
| Potential Risk | Users and developers encounter preset limitations without documentation. |
| Suggested Artifact | Update `KNOWN_LIMITATIONS.md` with M8 preset limitations. |

**Confidence**: HIGH

---

### G-12: Stale Documentation Artifacts

| Field | Value |
|---|---|
| Current Situation | Multiple documents are stale: `PROJECT_BRIEF.md` (M11.2), `AI_HANDOFF.md` (M11.2 + M12 Rule IDE), `AI_MEMORY_PACK.md` (M11.1), `NEXT_MILESTONE.md` (P3 Presets still listed), `development/current_status.md` (M11.2). |
| Evidence | See PAC-1 `09_Evidence_Cross_Validation.md` conflicts C-02 through C-05, C-09, C-14, C-17. |
| Potential Risk | Every new AI session reads stale documents. Milestone planning is based on outdated information. |
| Suggested Artifact | Update all stale documents to reflect M8 baseline. |

**Confidence**: HIGH

---

### G-13: Missing "Rule IDE" Definition

| Field | Value |
|---|---|
| Current Situation | "Rule IDE" is referenced in `editor/`, `AI_HANDOFF.md`, and `CURRENT_STATUS.md` but never formally defined. Is it a product rename? A subsystem? A milestone name? |
| Evidence | 5 references. No definition. No scope boundary. No relationship to ResourceHub. |
| Potential Risk | Ambiguity blocks M9 planning. Cannot resolve Filter vs. Rule IDE priority without knowing what Rule IDE means. |
| Suggested Artifact | `docs/design/RULE_IDE_SCOPE.md` — what is Rule IDE, how it relates to ResourceHub, what's in scope, what's not. |

**Confidence**: HIGH

---

### G-14: AGENTS.md Table Missing `add_suffix`

| Field | Value |
|---|---|
| Current Situation | `AGENTS.md` RuleStep 类型总览 shows 9 types. Code has 10. `add_suffix` is missing. |
| Evidence | See C-01 in cross-validation. |
| Potential Risk | New contributors and AI sessions reference an incomplete table. Low risk but high visibility (AGENTS.md is the primary reference). |
| Suggested Artifact | Add `add_suffix` row to AGENTS.md RuleStep table: `\| add_suffix \| 添加后缀 \| text \| "" \|`. |

**Confidence**: HIGH

---

### G-15: Dead Packages in Repository

| Field | Value |
|---|---|
| Current Situation | `app/` (0-byte __init__.py) and `resources/` (empty directory) exist but are never used, imported, or documented. |
| Evidence | `app/__init__.py`: 0 bytes. `resources/`: no files. No imports of `app` or `resources` anywhere in the codebase. |
| Potential Risk | Clutter. Confusion for new developers ("is this used?"). |
| Suggested Artifact | Either populate or delete these packages. Document the decision. |

**Confidence**: HIGH

---

## Gap Summary

| ID | Gap | Priority | Blocks M9? |
|---|---|---|---|
| G-01 | Project Charter | HIGH | No |
| G-02 | Master Design Document | HIGH | No (but blocks Rule IDE work) |
| G-03 | Product Roadmap | HIGH | **Yes** (scope priority) |
| G-04 | Versioning Policy | MEDIUM | No |
| G-05 | ADR for editor/ package | MEDIUM | No |
| G-06 | ADR for Preset architecture | LOW | No |
| G-07 | Milestone completion records | LOW | No |
| G-08 | Release process | MEDIUM | No |
| G-09 | Decision ownership | MEDIUM | No |
| G-10 | Contributor guide | LOW | No |
| G-11 | M8 limitations in KNOWN_LIMITATIONS | MEDIUM | No |
| G-12 | Stale documentation | HIGH | **Yes** (M9 planning accuracy) |
| G-13 | Rule IDE definition | HIGH | **Yes** (scope clarity) |
| G-14 | add_suffix in AGENTS.md | LOW | No |
| G-15 | Dead packages | LOW | No |

---

## What Must Be Resolved Before Project Charter v1.0

| # | Item | Why |
|---|---|---|
| 1 | **Product name decision** | Charter must state the product name |
| 2 | **Rule IDE definition + scope** | Charter must define product scope |
| 3 | **Versioning policy** | Charter references version scheme |
| 4 | **M9+ roadmap** | Charter references product direction |
| 5 | **Decision authority** | Charter must state who governs the project |
| 6 | **Stale documentation cleaned** | Charter must be consistent with other docs |

---

**Confidence**: HIGH (all gaps confirmed by repository absence + documentation inspection)
