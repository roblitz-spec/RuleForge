# Execution Lifecycle

_M12 Baseline — Frozen_

## Lifecycle Phases

```
┌─────────────────────────────────────────────────────────────┐
│                    PRE-EXECUTION                             │
│                                                              │
│  1. VALIDATE   ValidationPlugin: pass/fail data checks       │
│       │                                                      │
│  2. DECIDE     PolicyPlugin: allow/deny/warn decisions        │
│       │                                                      │
│  3. SCHEDULE   SchedulerPlugin: trigger, timing, delay        │
│       │                                                      │
│  4. SELECT     RemoteProviderPlugin: provider resolution      │
│       │                                                      │
├───────┴──────────────────────────────────────────────────────┤
│                    EXECUTION                                  │
│                                                              │
│  5. ORCHESTRATE  WorkflowPlugin: step definition, flow       │
│       │                                                      │
│  6. EXECUTE      ExecutionPlatform (M11): Engine.run()       │
│       │                                                      │
├───────┴──────────────────────────────────────────────────────┤
│                   POST-EXECUTION                              │
│                                                              │
│  7. RECOVER     RollbackPlugin: compensation, history        │
│       │                                                      │
│  8. NOTIFY      NotificationPlugin: channel delivery         │
│                                                              │
└──────────────────────────────────────────────────────────────┘

                    CROSS-CUTTING
          EventPlugin: publish/subscribe events
          at any lifecycle transition point
```

## Phase Responsibilities

### Pre-Execution

The platform validates, decides, schedules, and resolves before any engine runs.

| Order | Plugin | Question Answered |
|---|---|---|
| 1 | ValidationPlugin | Is the data valid? (pass/fail) |
| 2 | PolicyPlugin | Should we proceed? (allow/deny/warn) |
| 3 | SchedulerPlugin | When should we run? (trigger/timing) |
| 4 | RemoteProviderPlugin | Which provider? (selection) |

### Execution

The engine runs with full context. WorkflowPlugin coordinates multi-step flows.

| Order | Component | Question Answered |
|---|---|---|
| 5 | WorkflowPlugin | In what order? (orchestration) |
| 6 | ExecutionPlatform | What actually happens? (runtime) |

### Post-Execution

After the engine completes (success or failure), recovery and external communication occur.

| Order | Plugin | Question Answered |
|---|---|---|
| 7 | RollbackPlugin | How to recover? (compensation) |
| 8 | NotificationPlugin | Who needs to know? (delivery) |

### Cross-Cutting

EventPlugin operates across all phases — any plugin can emit events, any plugin can subscribe.

## Execution Flow

```
ExecutionContext
    │
    ├── ValidationPlugin.validate_all(ctx)
    ├── PolicyPlugin.evaluate_all(ctx)
    ├── SchedulerPlugin (timing control)
    ├── RemoteProviderPlugin (provider selection)
    │
    ├── WorkflowPlugin (step orchestration)
    │       │
    │       └── ExecutionPipeline.run(ctx, engine)
    │               │
    │               ├── EventPlugin.emit("execution.started")
    │               ├── engine.execute(ctx)
    │               ├── EventPlugin.emit("execution.completed")
    │               └── ExecutionResult
    │
    ├── RollbackPlugin (if failed)
    └── NotificationPlugin.notify_all(result)
```

Each phase is optional — plugins are invoked only when registered and active.
