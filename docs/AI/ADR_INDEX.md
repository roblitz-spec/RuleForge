# RuleForge — Architecture Decision Index

> **Last updated**: M10.5-F
> **Total ADRs**: 10

## Index

| ID | Title | Status | Milestone | Compatibility Impact |
|---|---|---|---|---|
| ADR-001 | Prefix / Suffix Design | Accepted | M15 | None |
| ADR-002 | Undo Design | Accepted | M15 | None |
| ADR-003 | Feature Freeze Policy | Accepted | M15 RC | None |
| ADR-004 | RuleEngine Pure Function Contract | Accepted | M12 | Backward compatible |
| ADR-005 | Context Contract | Accepted | M14 | Backward compatible |
| ADR-006 | Avoid Path.resolve() in Scanner Hot Path | Accepted | M11.1 | None (internal optimization) |
| ADR-007 | — | (reserved) | — | — |
| ADR-008 | — | (reserved) | — | — |
| ADR-009 | Product Direction Convergence | Accepted | M9 | Policy only |
| ADR-010 | Adopt RuleForge as Official Project Identity | Accepted | M10 | Name change only |
| ADR-011 | RuleSession Lifecycle | Accepted | M10.5-B | Backward compatible |
| ADR-012 | Public API Freeze & Compatibility Baseline | Accepted | M10.5-E | Backward compatible |

## Status Definitions

| Status | Meaning |
|---|---|
| Proposed | Under discussion, not yet implemented |
| Accepted | Implemented and active |
| Superseded | Replaced by a later ADR |
| Deprecated | No longer applicable |

## Supersession Chain

No ADRs currently superseded.

## Compatibility Impact Legend

| Level | Meaning |
|---|---|
| None | No public API impact |
| Backward compatible | Public API extended, existing consumers unaffected |
| Breaking | Requires migration path (not yet introduced) |
| Policy only | Governance/process decision, no code impact |
