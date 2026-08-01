# Plugin Framework

_M12-B Baseline — Frozen_

The Plugin Framework is the unified extension mechanism for RuleForge.
All capability plugins (M12-C through M12-K) are built on this framework.

## Architecture

```
PluginRegistry
    │
    ├── register(plugin)     → LOADED
    ├── enable(name)         → ENABLED
    ├── activate(name)       → ACTIVE
    ├── deactivate(name)     → ENABLED
    ├── disable(name)        → LOADED
    ├── get(name)            → Plugin | None
    ├── list_by_capability() → tuple[Plugin]
    └── state(name)          → str
```

## Plugin Contract

Every plugin must:

```python
class MyPlugin(Plugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="ruleforge.myplugin",
            version="1.0.0",
            description="...",
            author="RuleForge",
            capabilities=(PluginCapability.EXECUTION_HOOK,),
        )

    def on_activate(self, ctx: PluginContext) -> None:
        pass

    def on_deactivate(self, ctx: PluginContext) -> None:
        pass
```

## Lifecycle State Machine

```
         register()
  ┌───┐ ───────────→ ┌────────┐
  │ ∅ │              │ LOADED │
  └───┘ ←─────────── └────────┘
         unregister()     │ enable()
                          ↓
         disable()   ┌─────────┐
  ┌────────┐ ←────── │ ENABLED │
  │ LOADED │          └─────────┘
  └────────┘               │ activate()
                      ┌────↓────┐
                      │  ACTIVE │
                      └─────────┘
                           │ deactivate()
                           ↓
                      ┌─────────┐
                      │ ENABLED │
                      └─────────┘
```

Invalid transitions raise `InvalidStateTransitionError`.

## Capability Model

Currently one capability: `PluginCapability.EXECUTION_HOOK`.

Capability plugins are discovered via:

```python
registry.list_by_capability(PluginCapability.EXECUTION_HOOK)
```

## Framework Files

| File | Responsibility |
|---|---|
| `plugin.py` | Plugin ABC, PluginMetadata |
| `plugin_capability.py` | PluginCapability enum |
| `plugin_context.py` | PluginContext |
| `plugin_registry.py` | PluginRegistry, state machine |
| `plugin_errors.py` | PluginNotFoundError, InvalidStateTransitionError |

## Freeze Status

The Plugin Framework (M12-B) is frozen. No API changes are permitted.
All extensions must enter through new plugins, never through framework modification.
