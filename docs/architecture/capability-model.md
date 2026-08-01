# Capability Model

_M12 Baseline — Frozen_

## What is a Capability Plugin?

A capability plugin is a Plugin Framework plugin that:

1. Implements `Plugin` ABC
2. Uses the official `PluginRegistry` and Lifecycle
3. Declares `PluginCapability.EXECUTION_HOOK`
4. Owns a single, well-defined cross-cutting concern
5. Has zero imports from `engine/` or other plugins
6. Has a stable, documented public API

## Capability Acceptance Rules

To qualify as a new official capability plugin, the candidate must satisfy **all** of:

1. **Cannot be composed from existing capabilities.** If the feature can be built by combining existing plugins (e.g., `EventPlugin.emit() + NotificationPlugin.notify()`), it is NOT a new capability.

2. **Owns a unique lifecycle responsibility.** The capability must address a distinct phase or concern in the execution lifecycle that no existing plugin covers.

3. **Has a stable public contract.** The plugin's API (models, methods, error semantics) must be designed for backward compatibility from v1.

4. **Has no responsibility overlap.** Must not duplicate responsibilities already owned by another plugin.

5. **Cannot reasonably belong to Engine / Framework / Rule layer.** If the concern is execution semantics → Engine. Framework infrastructure → Plugin ABC/Registry. Rule transformation → RuleEngine. None of these are capability plugins.

6. **Must implement Plugin ABC only.** Zero cross-plugin imports, zero engine/ imports, zero framework modifications.

## Capability Discovery

```python
from plugins.plugin_registry import PluginRegistry
from plugins.plugin_capability import PluginCapability

registry = PluginRegistry()
plugins = registry.list_by_capability(PluginCapability.EXECUTION_HOOK)
```

## Capability Lifecycle

Each capability plugin follows the standard Plugin Framework lifecycle:

```
register → LOADED → enable → ENABLED → activate → ACTIVE
```

When active, the plugin can register its domain objects (rules, policies, channels, etc.). Deactivation preserves internal state; only `disable()` or `unregister()` clears it.

## Current Capabilities

| Plugin | Domain |
|---|---|
| RollbackPlugin | Recovery & compensation |
| SchedulerPlugin | Trigger & timing |
| RemoteProviderPlugin | Provider selection |
| WorkflowPlugin | Step orchestration |
| EventPlugin | Pub/sub events |
| PolicyPlugin | allow/deny/warn decisions |
| ValidationPlugin | pass/fail data checks |
| NotificationPlugin | Channel delivery |

All are frozen and tested.
