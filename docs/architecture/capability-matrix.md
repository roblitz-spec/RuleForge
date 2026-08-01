# Capability Matrix

_M12 Baseline — Frozen_

## Full Capability Inventory

| # | Plugin | Name | Capability | Lifecycle Phase | Tests |
|---|---|---|---|---|---|
| C | `RuleValidationPlugin` | `ruleforge.validation` | `EXECUTION_HOOK` | Pre-execution | 36 |
| D | `RollbackPlugin` | `ruleforge.rollback` | `EXECUTION_HOOK` | Post-execution | 26 |
| E | `SchedulerPlugin` | `ruleforge.scheduler` | `EXECUTION_HOOK` | Pre-execution | 30 |
| F | `RemoteProviderPlugin` | `ruleforge.remoteprovider` | `EXECUTION_HOOK` | Pre-execution | 32 |
| G | `WorkflowPlugin` | `ruleforge.workflow` | `EXECUTION_HOOK` | Mid-execution | 40 |
| H | `EventPlugin` | `ruleforge.event` | `EXECUTION_HOOK` | Cross-cutting | 38 |
| I | `PolicyPlugin` | `ruleforge.policy` | `EXECUTION_HOOK` | Pre-execution | 43 |
| J | `ValidationPlugin` | `ruleforge.validation` | `EXECUTION_HOOK` | Pre-execution | 44 |
| K | `NotificationPlugin` | `ruleforge.notification` | `EXECUTION_HOOK` | Post-execution | 44 |

## Lifecycle Phase Coverage

| Phase | Plugins |
|---|---|
| Pre-execution | RuleValidation, Policy, Scheduler, RemoteProvider, Validation |
| Mid-execution | Workflow |
| Post-execution | Rollback, Notification |
| Cross-cutting | Event |

## Test Coverage

| Milestone | Plugin | Tests |
|---|---|---|
| M12-C | RuleValidationPlugin | 36 |
| M12-D | RollbackPlugin | 26 |
| M12-E | SchedulerPlugin | 30 |
| M12-F | RemoteProviderPlugin | 32 |
| M12-G | WorkflowPlugin | 40 |
| M12-H | EventPlugin | 38 |
| M12-I | PolicyPlugin | 43 |
| M12-J | ValidationPlugin | 44 |
| M12-K | NotificationPlugin | 44 |
| M12-A | Batch Execution | 27 |
| M12-B | Plugin Framework | 46 |
| **Total** | | **406** (M12 only) |

Full regression: **1134** tests (M1 through M12-K).
