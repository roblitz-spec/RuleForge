# Roadmap Refresh

**Status**: Accepted v1.0 | **PAC-1** | **Date**: 2026-07-29
**Primary Source**: [`Decision_Registry_v1.0.md`](../governance/Decision_Registry_v1.0.md)
**Supporting Evidence: `docs/AI/NEXT_MILESTONE.md`, `docs/PAC/14_Alignment_Review.md` §4, §11**

---

## Completed Milestones

| Milestone | Feature | Tests | Tag |
|---|---|---|---|
| M2 | EditSession, WorkingCopy, UI Integration | — | M2-complete |
| M3 | — | — | M3-complete |
| M4 | — | — | M4-complete |
| M4.1 | — | — | M4.1-complete |
| M5 | — | — | M5-complete |
| M6 | Rule Duplication | 384 | M6-complete |
| M7 | Architecture Consolidation & Quality Hardening | 398 | M7-complete |
| M8 | Rule Presets | 447 | M8-complete |

---

## Planned Features (from NEXT_MILESTONE.md)

| Priority | Feature | Status |
|---|---|---|
| P1 | **Filter System** — Filter files by extension/pattern before rename | Not started |
| P2 | **EXIF Date** — Use EXIF metadata for photo date | Not started |
| P3 | ~~Rule Presets~~ | **Completed (M8)** |
| P4 | **Variables** — User-defined variables in Rule parameters | Not started |

---

## Feature Gap After M8

With P3 (Rule Presets) completed in M8, the remaining candidate features are:

| Priority | Feature | Notes |
|---|---|---|
| P1 | Filter System | Allow users to filter files before rename |
| P2 | EXIF Date | Photo date from EXIF, not mtime |
| P4 | Variables | `$counter` and other dynamic values |

No replacement P3 has been designated.

---

## Emerging Direction: Rule IDE

The `editor/` package (EditSession, DomainValidator — 382 lines) implements a UI-independent rule editing layer. `AI_HANDOFF.md` references "M12 Rule IDE" as a planned milestone. However:

1. `M12-complete` git tag already exists (Number Rule, 122 tests)
2. "Rule IDE" is not formally defined (see PG-01)
3. The relationship between Filter System (P1) and Rule IDE is unresolved

---

## Deferred Technical Debt

From `docs/AI/CURRENT_STATUS.md` § Deferred Technical Debt:

| ID | Item | Trigger |
|---|---|---|
| TD-003 | Refactor RuleManagerDialog | New RuleStep type or M12 Rule IDE |
| TD-004 | — | — |
| TD-009 | Remove debug code residues | Code cleanup milestone |
| TD-012 | — | — |
| TD-013 | Expand README.md | Documentation milestone |
| TD-018 | Refactor validator/ | Validation rules change or Rule IDE |

---

## Roadmap Questions Requiring Governance

| # | Question | Reference |
|---|---|---|
| 1 | What is M9? Filter System (P1) or Rule IDE continuation? | PG-02, PG-07 |
| 2 | What is the priority relationship between Filter, EXIF, Variables, and Rule IDE? | Not addressed |
| 3 | Should there be a new P3 to replace Rule Presets? | PG-07 |
| 4 | Is there a target milestone for v1.0? | PG-05 |
| 5 | What milestone sequence optimizes for user value? | Not addressed |

---

**Primary Source**: [`Decision_Registry_v1.0.md`](../governance/Decision_Registry_v1.0.md) — approved decisions that inform roadmap priorities.
**Supporting Evidence**: `docs/AI/NEXT_MILESTONE.md`, `docs/AI/CURRENT_STATUS.md`, `docs/AI/AI_HANDOFF.md`, `docs/PAC/02_Product_Evolution.md`, `docs/PAC/14_Alignment_Review.md`.
