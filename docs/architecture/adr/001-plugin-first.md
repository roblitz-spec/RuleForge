# ADR-001: Plugin First

## Status

Accepted (M12-B). Frozen.

## Context

RuleForge needed a way to extend the Execution Platform (M11) with
cross-cutting capabilities — validation, rollback, scheduling,
events, policy, notifications, etc. The traditional approach would
be to modify the engine/ layer directly for each new capability.

## Decision

All new platform capabilities enter through the Plugin Framework,
not by modifying engine/ or framework code.

The Plugin Framework provides:
- `Plugin` ABC: standard contract for all extensions
- `PluginRegistry`: centralized registration and discovery
- Lifecycle state machine: LOADED → ENABLED → ACTIVE
- `PluginCapability`: capability-based discovery

## Consequences

**Positive:**
- Engine layer (M11) remains unchanged across 9 capability plugins
- Each plugin is independently testable and deployable
- Zero cross-plugin coupling (verified: 0 imports)
- Framework API frozen at M12-B — no drift through M12-K

**Negative:**
- Adds one layer of indirection (Registry → Plugin → domain logic)
- Requires discipline: every new feature must be evaluated for plugin eligibility

## Evidence

- M12-C through M12-K: 9 plugins, 0 engine modifications
- Architecture Consistency Review: zero cross-plugin imports
- All plugins follow identical Plugin ABC pattern
