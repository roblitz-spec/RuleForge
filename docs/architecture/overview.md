# RuleForge Architecture Overview

_M12 Baseline — Frozen_

> 📋 See [`PROJECT_IDENTITY.md`](../../PROJECT_IDENTITY.md) for the canonical project context and principles.

## Platform Layers

```
┌──────────────────────────────────────────────────────────┐
│                Capability Plugins (M12-C→K)               │
│  Rollback │ Scheduler │ RemoteProvider │ Workflow │       │
│  Event │ Policy │ Validation │ Notification             │
├──────────────────────────────────────────────────────────┤
│              Plugin Framework (M12-B)                     │
│     Plugin │ Registry │ Lifecycle │ Capability            │
├──────────────────────────────────────────────────────────┤
│           Batch Execution (M12-A)                         │
│     BatchEngine │ BatchExecutor │ BatchResult             │
├──────────────────────────────────────────────────────────┤
│          Execution Platform v1 (M11)                       │
│     Pipeline │ Context │ Result │ Trace │ Registry         │
│     RenameEngine │ DryRun │ Inspection │ StringTransform   │
└──────────────────────────────────────────────────────────┘
```

## Design Principles

1. **Plugin First** — All new platform capabilities enter through the Plugin Framework, not by modifying the engine or framework.
2. **Frozen Contract** — Once frozen, public APIs never change. Extensions are additive only.
3. **Single Responsibility** — Each layer and plugin owns exactly one concern.
4. **Capability Decoupling** — Zero cross-plugin imports, zero engine/ imports from plugins.
5. **Backward Compatibility** — All existing behavior and tests continue to pass.
6. **Composition First** — Before creating a new capability plugin, verify the feature cannot be composed from existing ones.

## Key Technologies

- Python 3.13+
- PyQt6 (GUI)
- pytest (testing)

## Repository Layout

```
plugins/          Capability plugins (each is a Plugin ABC implementation)
engine/           Execution Platform (M11) + Batch Execution (M12-A)
tests/            All tests
docs/
  architecture/   Architecture documentation (this directory)
  AI/             AI development context
  governance/     Governance documentation
  knowledge/      Domain knowledge articles
  planning/       Roadmap and planning
```

## Frozen Milestones

| Tag | Content |
|---|---|
| `M11-complete` | Execution Platform v1 |
| `M12-A-complete` | Batch Execution Foundation |
| `M12-B-complete` | Plugin Framework |
| `M12-C-complete` | RuleValidationPlugin (first official plugin) |
| `M12-D-complete` | RollbackPlugin |
| `M12-E-complete` | SchedulerPlugin |
| `M12-F-complete` | RemoteProviderPlugin |
| `M12-G-complete` | WorkflowPlugin |
| `M12-H-complete` | EventPlugin |
| `M12-I-complete` | PolicyPlugin |
| `M12-J-complete` | ValidationPlugin |
| `M12-K-complete` | NotificationPlugin |

All milestones are feature-complete, tested, and frozen.
