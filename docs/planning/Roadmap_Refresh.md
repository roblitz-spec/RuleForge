# Roadmap Refresh

**Status**: Accepted v2.0 | **Post-ADR-009** | **Date**: 2026-07-30
**Primary Source**: [`Decision_Registry_v1.0.md`](../governance/Decision_Registry_v1.0.md), ADR-009
**Supporting Evidence: `docs/AI/NEXT_MILESTONE.md`, `docs/AI/DECISION_LOG.md`**

---

## Product Direction (ADR-009)

AI-assisted Rule IDE (RuleForge). ONE product, ONE roadmap, ONE development path.

- ResourceHub = origin
- Batch file rename = initial adapter/use case
- Core value: Example → Rule Inference → Rule → Test/Preview → Execute → Reuse

---

## Completed Milestones

| Milestone | Feature | Tests | Tag |
|---|---|---|---|
| M2–M8 | Batch Rename pipeline | 447 | M8-complete |
| M9 | RuleInference Engine (Example → Rule) | 480 | M9-complete |

---

## Strategic Roadmap

| Milestone | Capability | Status |
|---|---|---|
| M9 | Example → Rule Inference | ✅ |
| M10 | Rule IDE (editing, inspection, testing, persistence) | → Next |
| M11 | Rule Runtime (batch, error handling, recovery) | Planned |
| Later | Additional adapters | Deferred |

---

## Resolved Governance Questions

| # | Question | Resolution |
|---|---|---|
| PG-01 | What is Rule IDE? | Formalized as development environment layer (ADR-009) |
| PG-02/PG-07 | What is M9? | RuleInference Engine — complete ✅ |
| UD-01 | Product rename? | RuleForge recommended; mechanical rename deferred |
| UD-02 | M12 contradiction? | Resolved: new roadmap eliminates ambiguity |

---

## Deferred Technical Debt

| ID | Item | Trigger |
|---|---|---|
| TD-003 | Refactor RuleManagerDialog | M10 Rule IDE |
| TD-007 | MainWindow God Class | M10 Rule IDE |
| TD-018 | Refactor validator/ | M10 Rule IDE |

---

**Primary Source**: [`Decision_Registry_v1.0.md`](../governance/Decision_Registry_v1.0.md), ADR-009.
**Supporting Evidence**: `docs/AI/NEXT_MILESTONE.md`, `docs/AI/CURRENT_STATUS.md`, `docs/AI/AI_HANDOFF.md`, `docs/AI/PROJECT_BRIEF.md`.
