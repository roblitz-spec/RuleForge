# Architecture Decision Records

_M12 Baseline — Frozen_

## Index

| ADR | Title | Status |
|---|---|---|
| [ADR-001](adr/001-plugin-first.md) | Plugin First | Accepted |
| [ADR-002](adr/002-frozen-contract.md) | Frozen Contract | Accepted |
| [ADR-003](adr/003-capability-plugin-model.md) | Capability Plugin Model | Accepted |
| [ADR-004](adr/004-zero-cross-plugin-dependency.md) | Zero Cross-Plugin Dependency | Accepted |
| [ADR-005](adr/005-capability-acceptance-rules.md) | Capability Acceptance Rules | Accepted |
| [ADR-006](adr/006-best-effort-notification.md) | Best-Effort Notification Delivery | Accepted |
| [ADR-007](adr/007-execution-integration.md) | Execution Integration (M12 Maintenance) | Accepted |

## What is an ADR?

An Architecture Decision Record captures a significant architectural
decision, the context in which it was made, and its consequences.

Each ADR answers: **why** was it designed this way, not just **what**
was designed.

## Writing a New ADR

1. Create `docs/architecture/adr/NNN-title-with-dashes.md`
2. Use the next available number
3. Follow the structure: Status → Context → Decision → Consequences → Evidence
4. Add to this index

ADRs are immutable once accepted. Superseded ADRs are marked as such
but never deleted.
