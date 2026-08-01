# ADR-002: Frozen Contract

## Status

Accepted (M11). Reinforced at M12-B. Frozen.

## Context

As RuleForge accumulated milestones (M11 execution platform, M12-A batch
execution, M12-B plugin framework), the risk grew that later changes
would inadvertently break earlier behavior. The project needed a way
to guarantee stability of public APIs.

## Decision

Once a milestone's public API is frozen, it never changes.
All modifications are additive only.

Frozen contracts include:
- Public class APIs (method signatures, parameter semantics)
- Lifecycle state machines
- Error semantics (which errors are raised and when)
- Registry contracts
- Capability enums

## Consequences

**Positive:**
- M11 engine API: 0 breaking changes through M12-K
- M12-B framework API: 0 diff from freeze through M12-K
- All 9 plugin files: unchanged since their respective freeze points
- Backward compatibility is guaranteed at the contract level

**Negative:**
- Design mistakes in frozen APIs cannot be corrected (only extended)
- Requires upfront design rigor before freezing

## Evidence

- `git diff M11-complete -- engine/` → only additive batch execution files
- `git diff M12-B-complete -- plugins/plugin*.py` → 0 changes
- All M12-C through M12-K plugin files: 0 diff from their freeze tags
- Full regression: 1134 tests, zero failures since M1
