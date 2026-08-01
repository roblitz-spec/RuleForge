# Architecture Principles

_M12 Baseline — Frozen_

These principles govern all architecture decisions in RuleForge.
They are the unified standard for architecture reviews, design
proposals, and code contributions.

## Principles

### 1. Single Responsibility

Each module, class, and plugin owns exactly one concern.

- Capability plugins own one cross-cutting concern each
- Engine owns execution semantics
- Framework owns plugin infrastructure
- RuleEngine owns filename transformation

**Anti-pattern:** A plugin that both validates data and sends notifications.

### 2. Plugin First

All new platform capabilities enter through the Plugin Framework.

- Do not modify engine/ for new capabilities
- Do not modify the Plugin Framework for new capabilities
- Extend through new plugins that implement `Plugin` ABC

**Anti-pattern:** Adding scheduling logic directly to `ExecutionPipeline`.

### 3. Composition First

Before creating a new capability plugin, verify the feature cannot be
composed from existing plugins.

- `EventPlugin.emit() + NotificationPlugin.notify()` = audit trail
- `PolicyPlugin.evaluate() + SchedulerPlugin` = rate limiting
- `EventPlugin.subscribe() + WorkflowPlugin` = event-driven workflows

**Anti-pattern:** Creating `AuditPlugin` when Event + Notification already cover it.

### 4. Frozen Contract

Once a milestone's public API is frozen, it never changes.

- Public method signatures are immutable
- Error semantics are immutable
- Lifecycle state machines are immutable
- Behavior changes require a new version (v2), not modification of v1

**Anti-pattern:** Changing `EvaluationResult` fields after M12-I freeze.

### 5. Backward Compatibility

All existing behavior and tests must continue to pass.

- Existing tests are the compatibility contract
- Additive changes only — never remove or redefine
- If a change would break any existing test, it is a contract violation

**Anti-pattern:** Modifying `PluginRegistry.register()` to require a new parameter.

### 6. Zero Cross-Plugin Dependency

Capability plugins import only from the Plugin Framework and stdlib.

- No imports from other plugins
- No imports from engine/
- No shared utility modules between plugins

**Anti-pattern:** `RollbackPlugin` importing `NotificationPlugin` to send alerts.

### 7. Stable Public Contract

Every public API must be designed for long-term stability.

- Frozen dataclasses for domain models
- Explicit error semantics (which exceptions, when)
- Documented parameter contracts
- Convenience constructors for common patterns

**Anti-pattern:** Returning `dict` from a public method without documenting its schema.

### 8. Capability Decoupling

Capabilities are independent, composable, and replaceable.

- Each plugin works in isolation
- Plugins can be registered, enabled, or disabled independently
- No plugin assumes another plugin is present

**Anti-pattern:** `WorkflowPlugin` requiring `EventPlugin` to function.

## Applying the Principles

When reviewing any architecture decision, code change, or design proposal:

1. Does it violate Single Responsibility?
2. Is it Plugin First (or should it be)?
3. Can it be composed instead of new?
4. Does it break Frozen Contracts?
5. Is it backward compatible?
6. Does it introduce cross-plugin dependencies?
7. Does it have a stable public contract?
8. Is it properly decoupled?

## References

- [ADR-001: Plugin First](adr/001-plugin-first.md)
- [ADR-002: Frozen Contract](adr/002-frozen-contract.md)
- [ADR-004: Zero Cross-Plugin Dependency](adr/004-zero-cross-plugin-dependency.md)
- [ADR-005: Capability Acceptance Rules](adr/005-capability-acceptance-rules.md)
