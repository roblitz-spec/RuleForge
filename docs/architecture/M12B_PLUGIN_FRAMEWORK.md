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
        ├── RuleValidationPlugin (M12-C) ← frozen: first official plugin
        ├── RollbackPlugin (M12-D) ← frozen: first capability plugin
        ├── SchedulerPlugin (M12-E) ← frozen: execution orchestration
        ├── RemoteProviderPlugin (M12-F) ← frozen: remote provider hub
        ├── WorkflowPlugin (M12-G) ← frozen: workflow orchestration
        ├── EventPlugin (M12-H) ← frozen: event-driven pub/sub
        ├── PolicyPlugin (M12-I) ← frozen: policy evaluation
        ├── ValidationPlugin (M12-J) ← frozen: data validation
        └── ... future extensions
```

### Official Plugin Baseline (M12-C)

`RuleValidationPlugin` is the first official plugin, proving that the
M12-B Plugin Framework can support real-world extensions without any
framework modification.

| Attribute | Value |
|---|---|
| Name | `ruleforge.validation` |
| Capability | `VALIDATION` |
| Tests | 36 |
| Framework changes needed | **0** |

All future official plugins MUST follow the same pattern:
1. Implement `Plugin` contract (metadata + lifecycle hooks)
2. Register through `PluginRegistry`
3. Declare capabilities via `PluginCapability`
4. Never bypass the plugin framework

### Capability Plugin Baseline (M12-D)

`RollbackPlugin` is the first official capability plugin, demonstrating
that the Plugin Framework supports plugins with business state (history,
transactions) without modifying the framework.

| Attribute | Value |
|---|---|
| Name | `ruleforge.rollback` |
| Capability | `EXECUTION_HOOK` |
| Business Domain | LIFO rename rollback |
| Tests | 26 |

Key architectural finding: **Lifecycle state** (LOADED/ENABLED/ACTIVE)
and **business state** (rollback history) are separate domains.
`deactivate()` preserves business data; `unregister()` triggers cleanup.

All future capability plugins MUST:
1. Implement `Plugin` contract
2. Use official Registry
3. Use official Lifecycle
4. Use official Capability Model
5. Not bypass Plugin Framework
6. Keep business state separate from lifecycle state

### Execution Orchestration Baseline (M12-E)

`SchedulerPlugin` is the first official execution orchestration plugin,
demonstrating that the Plugin Framework supports timing-based capabilities
without modifying the framework or the Execution Platform.

| Attribute | Value |
|---|---|
| Name | `ruleforge.scheduler` |
| Capability | `EXECUTION_HOOK` |
| Business Domain | Task scheduling (delayed + recurring) |
| Tests | 30 |

#### Scheduler / Execution Boundary

The Scheduler and Execution Platform operate on separate concerns:

| Concern | Scheduler Plugin | Execution Platform | Rollback Plugin |
|---|---|---|---|
| Trigger & timing | ✅ Responsible | — | — |
| Scheduling policy | ✅ Responsible | — | — |
| Execute tasks | ❌ Not responsible | ✅ Responsible | — |
| Retry logic | ❌ Not responsible | — | — |
| Runtime context | — | ✅ Responsible | — |
| Result delivery | — | ✅ Responsible | — |
| Rollback/recovery | — | — | ✅ Responsible |
| Business logic | ❌ Not responsible | ❌ Not responsible | — |

The Scheduler Plugin orchestrates *when* to execute — it delegates
*what* to execute to the Execution Platform via callbacks.

### Remote Execution Baseline (M12-F)

`RemoteProviderPlugin` is the first official remote execution plugin,
demonstrating that the Plugin Framework can manage provider abstractions
without modifying the framework or Execution Platform.

| Attribute | Value |
|---|---|
| Name | `ruleforge.remote-provider` |
| Capability | `EXECUTION_HOOK` |
| Business Domain | Provider registration, discovery, selection |
| Tests | 32 |
| Reference Provider | `LocalProvider` (always available) |

#### Provider / Execution / Orchestration Boundary

| Concern | RemoteProviderPlugin | SchedulerPlugin | Execution Platform | RollbackPlugin |
|---|---|---|---|---|
| Provider registration | ✅ Responsible | — | — | — |
| Provider discovery | ✅ Responsible | — | — | — |
| Provider selection | ✅ Responsible | — | — | — |
| Remote invocation abstraction | ✅ Responsible | — | — | — |
| Trigger & timing | — | ✅ Responsible | — | — |
| Execute tasks | ❌ Not responsible | ❌ Not responsible | ✅ Responsible | — |
| Retry logic | ❌ Not responsible | ❌ Not responsible | — | — |
| Rollback/recovery | — | — | — | ✅ Responsible |
| Business logic | ❌ Not responsible | ❌ Not responsible | ❌ Not responsible | — |

### Workflow Orchestration Baseline (M12-G)

`WorkflowPlugin` is the first official workflow orchestration plugin,
demonstrating that the Plugin Framework can manage multi-step sequenced
execution flows without modifying the framework or Execution Platform.

| Attribute | Value |
|---|---|
| Name | `ruleforge.workflow` |
| Capability | `EXECUTION_HOOK` |
| Business Domain | Workflow registration, discovery, sequenced execution |
| Tests | 40 |
| Reference Workflow | 3-step pipeline (validate → process → notify) |

#### Workflow / Execution / Orchestration Boundary

| Concern | WorkflowPlugin | SchedulerPlugin | RemoteProviderPlugin | Execution Platform | RollbackPlugin |
|---|---|---|---|---|---|
| Workflow definition | ✅ Responsible | — | — | — | — |
| Step orchestration | ✅ Responsible | — | — | — | — |
| Flow coordination | ✅ Responsible | — | — | — | — |
| Failure policy | ✅ Responsible | — | — | — | — |
| Trigger & timing | — | ✅ Responsible | — | — | — |
| Provider selection | — | — | ✅ Responsible | — | — |
| Execute tasks | ❌ Not responsible | ❌ Not responsible | ❌ Not responsible | ✅ Responsible | — |
| Rollback/recovery | — | — | — | — | ✅ Responsible |
| Business logic | ❌ Not responsible | ❌ Not responsible | ❌ Not responsible | ❌ Not responsible | — |

### Event-Driven Baseline (M12-H)

`EventPlugin` is the first official event-driven plugin,
demonstrating that the Plugin Framework can manage publish/subscribe
semantics without modifying the framework or Execution Platform.

| Attribute | Value |
|---|---|
| Name | `ruleforge.event` |
| Capability | `EXECUTION_HOOK` |
| Business Domain | Event pub/sub — define, subscribe, publish, dispatch |
| Tests | 38 |
| Reference Events | `execution.started`, `execution.completed`, `execution.failed` |

#### Event / Execution / Orchestration Boundary

| Concern | EventPlugin | WorkflowPlugin | SchedulerPlugin | RemoteProviderPlugin | Execution Platform | RollbackPlugin |
|---|---|---|---|---|---|---|
| Event definition | ✅ Responsible | — | — | — | — | — |
| Subscribe/Unsubscribe | ✅ Responsible | — | — | — | — | — |
| Publish/Dispatch | ✅ Responsible | — | — | — | — | — |
| Subscriber registry | ✅ Responsible | — | — | — | — | — |
| Workflow definition | — | ✅ Responsible | — | — | — | — |
| Step orchestration | — | ✅ Responsible | — | — | — | — |
| Trigger & timing | — | — | ✅ Responsible | — | — | — |
| Provider selection | — | — | — | ✅ Responsible | — | — |
| Execute tasks | ❌ | ❌ | ❌ | ❌ | ✅ Responsible | — |
| Rollback/recovery | — | — | — | — | — | ✅ Responsible |
| Business logic | ❌ | ❌ | ❌ | ❌ | ❌ | — |

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

### Lifecycle State vs. Business State

Plugin lifecycle state (LOADED/ENABLED/ACTIVE) and plugin business state
are **separate domains**.

| Domain | Managed by | Example |
|---|---|---|
| Lifecycle | `PluginRegistry` | LOADED → ENABLED → ACTIVE |
| Business | Plugin internals | Rollback history, validation cache |

Key rules:
- `deactivate()` does NOT destroy business state (history, caches).
- `unregister()` (via `on_unload`) is the designated cleanup point.
- `clear_history()` / `reset()` are business operations, independent of
  lifecycle hooks.
- A deactivated plugin may still provide queries against its business
  state (e.g., check history size after deactivation).

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

### Policy Capability Baseline (M12-I)

`PolicyPlugin` is the first official policy evaluation plugin,
demonstrating that the Plugin Framework can manage allow/deny/warn
decision-making without modifying the framework or Execution Platform.

| Attribute | Value |
|---|---|
| Name | `ruleforge.policy` |
| Capability | `EXECUTION_HOOK` |
| Business Domain | Policy definition, registration, evaluation (allow/deny/warn) |
| Tests | 43 |
| Reference Policies | `max-files`, `allow-text-only` |

**Important:** Policy Plugin v1 is a decision-support tool, NOT a
security authorization engine.  The "default allow" behavior (empty
policy raises no error) applies ONLY to this Policy Capability
Baseline.  Future security-oriented policy capabilities must NOT
inherit the default-allow behavior without explicit design review.

#### Policy / Execution / Orchestration Boundary

| Concern | PolicyPlugin | EventPlugin | WorkflowPlugin | SchedulerPlugin | RemoteProviderPlugin | Execution Platform | RollbackPlugin |
|---|---|---|---|---|---|---|---|
| Policy definition | ✅ Responsible | — | — | — | — | — | — |
| Policy evaluation | ✅ Responsible | — | — | — | — | — | — |
| allow/deny/warn | ✅ Responsible | — | — | — | — | — | — |
| Event pub/sub | — | ✅ Responsible | — | — | — | — | — |
| Workflow orchestration | — | — | ✅ Responsible | — | — | — | — |
| Trigger \& timing | — | — | — | ✅ Responsible | — | — | — |
| Provider selection | — | — | — | — | ✅ Responsible | — | — |
| Execute tasks | ❌ Not responsible | ❌ Not responsible | ❌ Not responsible | ❌ Not responsible | ❌ Not responsible | ✅ Responsible | — |
| Rollback/recovery | — | — | — | — | — | — | ✅ Responsible |
| Business logic | ❌ Not responsible | ❌ Not responsible | ❌ Not responsible | ❌ Not responsible | ❌ Not responsible | ❌ Not responsible | — |

### Validation Capability Baseline (M12-J)

`ValidationPlugin` is the first official data validation plugin,
demonstrating that the Plugin Framework can manage pass/fail
validation checks without modifying the framework or Execution Platform.

| Attribute | Value |
|---|---|
| Name | `ruleforge.validation` |
| Capability | `EXECUTION_HOOK` |
| Business Domain | Data validation — define, register, execute validation rules |
| Tests | 44 |
| Reference Rules | `non-empty-name`, `positive-count` |

**Important:** Validation Plugin v1 validates data — it does NOT auto-repair,
make policy decisions, or execute business logic. Unknown return types
from validation callbacks are treated as failure (fail-safe). Future
schema engines, constraint solvers, or auto-repair must be separate
capabilities.

#### Validation / Execution / Orchestration Boundary

| Concern | ValidationPlugin | PolicyPlugin | EventPlugin | WorkflowPlugin | SchedulerPlugin | RemoteProviderPlugin | Execution Platform | RollbackPlugin |
|---|---|---|---|---|---|---|---|---|
| Validation rules | ✅ Responsible | — | — | — | — | — | — | — |
| Pass/fail checks | ✅ Responsible | — | — | — | — | — | — | — |
| allow/deny/warn | — | ✅ Responsible | — | — | — | — | — | — |
| Event pub/sub | — | — | ✅ Responsible | — | — | — | — | — |
| Workflow orchestration | — | — | — | ✅ Responsible | — | — | — | — |
| Trigger \& timing | — | — | — | — | ✅ Responsible | — | — | — |
| Provider selection | — | — | — | — | — | ✅ Responsible | — | — |
| Execute tasks | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ Responsible | — |
| Rollback/recovery | — | — | — | — | — | — | — | ✅ Responsible |
| Auto repair | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | — |
| Business logic | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | — |
