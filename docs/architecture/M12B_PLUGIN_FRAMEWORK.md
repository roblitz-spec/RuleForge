# M12-B: Plugin / Extension Framework

**Status**: Frozen (2026-07-31)
**Parent Baselines**: M11 (Execution Platform v1), M12-A (Batch Execution Foundation)
**Commit**: `eb7faecb488e3ad990fb511a830ab4b12e29fdd4`
**Tag**: `M12-B-complete`

## Architecture Overview

RuleForge Plugin Framework provides a stable extension mechanism that allows
new capabilities — Rollback, Scheduler, Remote Provider — to be added as
plugins without modifying core platform code.

This is the **official extension contract** for RuleForge.  All future
extensions (Rollback, Scheduler, Remote Provider, and beyond) MUST be
implemented as plugins using this framework — direct coupling to the
Execution Platform is prohibited.

### Platform Hierarchy

```
Execution Platform (M11)          ← frozen: ExecutionEngine, Pipeline, Context, Result
        │
Batch Execution Foundation (M12-A) ← frozen: ExecutionBatch, BatchExecutor, BatchResult
        │
Plugin / Extension Framework (M12-B) ← frozen: Plugin, Registry, Lifecycle, Extension Points
        │
        ├── M12-C Rollback (planned)
        ├── M12-D Scheduler (planned)
        ├── M12-E Remote Provider (planned)
        └── ... future extensions
```

```
plugins/                          (new, parallel to engine/)
  plugin.py              Plugin ABC + PluginMetadata
  plugin_capability.py   PluginCapability enum
  plugin_context.py      PluginContext
  plugin_registry.py     PluginRegistry
  plugin_errors.py       error types
```

Plugins are NOT ExecutionEngines.  They operate at a different layer:
ExecutionEngines implement execution behavior; plugins intercept and extend
the execution lifecycle at defined extension points.

```
Extension Points (defined, not yet wired into pipeline):
  ┌──────────────────────────────────────────────────┐
  │  Rule Discovery  ──  find rules from new sources │
  │  Validation      ──  custom rule validation      │
  │  Execution Hooks ──  pre/post execution hooks     │
  │  Batch Hooks     ──  pre/post batch item hooks    │
  │  Result Processing ── transform execution results │
  │  Output Export   ──  export results to new formats│
  └──────────────────────────────────────────────────┘
```

## Design Principles

1. **Extension, not modification** — Plugins extend behavior at defined hooks;
   they never modify core code or monkey-patch internals.

2. **Isolation** — Plugin failures are contained.  A failing plugin does not
   crash the host or affect other plugins' lifecycle.

3. **Explicit contracts** — Plugin API is defined through abstract base classes
   and frozen dataclasses.  No implicit conventions or magic methods.

4. **Capability-based discovery** — the registry answers "which plugins
   support capability X?" enabling targeted dispatch.

5. **Lazy activation** — Plugins are registered eagerly but activated on
   demand.  Lifecycle states are explicit and validated.

6. **Zero coupling to Engine** — PluginRegistry does not import or depend on
   EngineRegistry, ExecutionEngine, or ExecutionPipeline.

## Component Design

### Plugin (ABC)

Base class for all plugins. Provides lifecycle hooks with default no-op
implementations — plugins override only what they need.

```python
class Plugin(ABC):
    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata: ...

    def on_discover(self, ctx: PluginContext) -> None: pass
    def on_load(self, ctx: PluginContext) -> None: pass
    def on_initialize(self, ctx: PluginContext) -> None: pass
    def on_activate(self, ctx: PluginContext) -> None: pass
    def on_deactivate(self, ctx: PluginContext) -> None: pass
    def on_unload(self, ctx: PluginContext) -> None: pass
```

### PluginMetadata (frozen dataclass)

Immutable descriptor.  The `name` field is the unique key in the registry.

```python
@dataclass(frozen=True)
class PluginMetadata:
    name: str
    version: str
    description: str = ""
    author: str = ""
    capabilities: tuple[PluginCapability, ...] = ()
    dependencies: tuple[str, ...] = ()  # plugin names this depends on
```

### PluginCapability (enum)

Declared capabilities a plugin provides.  The registry uses these for
targeted queries (`list_by_capability`).

```python
class PluginCapability(Enum):
    RULE_DISCOVERY = "rule_discovery"
    VALIDATION = "validation"
    EXECUTION_HOOK = "execution_hook"
    BATCH_HOOK = "batch_hook"
    RESULT_PROCESSING = "result_processing"
    OUTPUT_EXPORT = "output_export"
```

### PluginContext (frozen dataclass)

Read-only context passed to lifecycle callbacks.  Contains a reference to
the registry (for inter-plugin communication) and an opaque data dict (for
host-to-plugin and plugin-to-plugin data sharing).

```python
@dataclass(frozen=True)
class PluginContext:
    registry: PluginRegistry | None = None
    data: dict[str, object] = field(default_factory=dict)
```

### PluginRegistry

Central plugin registry.  Zero dependencies on engine/ or models/.
Manages registration, lifecycle, enable/disable, and capability queries.

```python
class PluginRegistry:
    def register(self, plugin: Plugin) -> None
    def unregister(self, name: str) -> None
    def get(self, name: str) -> Plugin | None
    def list_all(self) -> list[Plugin]
    def list_by_capability(self, capability: PluginCapability) -> list[Plugin]
    def enable(self, name: str) -> None
    def disable(self, name: str) -> None
    def is_enabled(self, name: str) -> bool
    def activate(self, name: str) -> None
    def deactivate(self, name: str) -> None
```

### Error Types

```python
class PluginError(Exception): ...
class PluginNotFoundError(PluginError): ...
class PluginLifecycleError(PluginError): ...
class PluginDependencyError(PluginError): ...
```

## Lifecycle

```
  register()       enable()        activate()
  ─────────► LOADED ──────► ENABLED ────────► ACTIVE
                                          ◄────────
                                          deactivate()
              ◄────────                  ◄────────
              disable()                  disable()

  unregister()
  ─────────► (removed)
```

States:
- **LOADED**: Plugin instance is registered but not yet enabled.
- **ENABLED**: Plugin is enabled but not executing hooks.
- **ACTIVE**: Plugin is actively receiving lifecycle events.

Transitions:
- `register()` → LOADED (calls `on_discover` + `on_load` + `on_initialize`)
- `enable()`: LOADED → ENABLED
- `activate()`: ENABLED → ACTIVE (calls `on_activate`)
- `deactivate()`: ACTIVE → ENABLED (calls `on_deactivate`)
- `disable()`: any → LOADED (calls `on_deactivate` if ACTIVE)
- `unregister()`: any → removed (calls `on_deactivate` + `on_unload`)

Lifecycle errors are contained — a failing `on_activate` does not prevent
other plugins from activating.

## Extension Points

### Formal Extension Points (this framework defines)

| Point | Capability | Signature | Status |
|---|---|---|---|
| Rule Discovery | `RULE_DISCOVERY` | `(ctx) → list[Rule]` | Defined, not wired |
| Validation | `VALIDATION` | `(ctx, rule) → list[Issue]` | Defined, not wired |
| Execution Hook | `EXECUTION_HOOK` | `(ctx, phase, result) → None` | Defined, not wired |
| Batch Hook | `BATCH_HOOK` | `(ctx, phase, batch_result) → None` | Defined, not wired |
| Result Processing | `RESULT_PROCESSING` | `(ctx, result) → ExecutionResult` | Defined, not wired |
| Output Export | `OUTPUT_EXPORT` | `(ctx, results) → bytes` | Defined, not wired |

Extension points are defined as contracts in this framework.  The actual
hook invocation code lives in the host (ExecutionPipeline, RuleWorkflow)
and will be wired in future milestones when concrete plugins are implemented.

### Internal implementation (not extension points)

The following are internal concerns, not plugin extension points:
- Engine registration (EngineRegistry)
- Rule engine execution (RuleEngine)
- File system operations (FilesystemAdapter)
- Rename plan building (RenamePlanBuilder)

## Dependency Rules

- Plugin declares dependencies via `PluginMetadata.dependencies` (list of plugin names).
- Registry validates that all dependencies are registered before enabling a plugin.
- Missing dependency → `PluginDependencyError`, plugin remains LOADED.
- Circular dependencies are detected during enable — second plugin's enable is rejected.
- No implicit dependency resolution — plugins declare what they need explicitly.

## Compatibility Strategy

### M11 Frozen Contract

| Component | Impact |
|---|---|
| `ExecutionEngine` (ABC) | **None** — Plugin is not an ExecutionEngine |
| `ExecutionPipeline.run()` | **None** — not modified |
| `ExecutionContext` | **None** — not modified |
| `ExecutionResult` | **None** — not modified |

### M12-A Frozen Contract

| Component | Impact |
|---|---|
| `BatchExecutor.run()` | **None** — not modified |
| `BatchResult` | **None** — not modified |
| `ExecutionBatch` | **None** — not modified |

### Future Wiring Strategy

When a specific plugin capability is needed (e.g., Rollback as an
`EXECUTION_HOOK`), the host code will:
1. Query `PluginRegistry.list_by_capability(EXECUTION_HOOK)`
2. Invoke matching plugins at the defined point
3. Handle failures with isolation (one plugin failing does not block others)

This wiring is deferred to the milestone that implements the concrete
plugin (M12-C Rollback, M12-D Scheduler, etc.).
