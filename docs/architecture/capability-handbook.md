# Capability Handbook

_M12 Baseline — Frozen_

Unified reference for all official capability plugins.

---

## RollbackPlugin

| Attribute | Value |
|---|---|
| Plugin | `ruleforge.rollback` |
| File | `plugins/rollback_plugin.py` |
| Milestone | M12-D |
| Capability | `EXECUTION_HOOK` |
| Lifecycle Phase | Post-execution |

**Responsibility:** Recovery, compensation, and rollback history after execution failures.

**Public API:**
- `RollbackAction` (frozen): action description, execute/compensate callables
- `register(action)` / `unregister(name)`
- `list_actions()` / `get(name)`
- `rollback(name, context)` / `rollback_all(context)`
- `action_count`

**Not Responsible For:** Execution runtime, scheduling, validation, policy decisions, business logic.

**Typical Usage:**
```python
plugin = registry.get("ruleforge.rollback")
plugin.register(RollbackAction("revert-rename", execute=undo_fn))
plugin.rollback("revert-rename", ctx)
```

---

## SchedulerPlugin

| Attribute | Value |
|---|---|
| Plugin | `ruleforge.scheduler` |
| File | `plugins/scheduler_plugin.py` |
| Milestone | M12-E |
| Capability | `EXECUTION_HOOK` |
| Lifecycle Phase | Pre-execution |

**Responsibility:** Trigger, timing, and scheduling policy for execution tasks.

**Public API:**
- `Schedule` (frozen): task reference, trigger time/condition, repeat policy
- `register(schedule)` / `unregister(name)`
- `list_schedules()` / `get(name)`
- `schedule_count`

**Not Responsible For:** Execution runtime, workflow orchestration, validation, rollback.

**Typical Usage:**
```python
plugin = registry.get("ruleforge.scheduler")
plugin.register(Schedule("daily-cleanup", trigger="0 3 * * *"))
```

---

## RemoteProviderPlugin

| Attribute | Value |
|---|---|
| Plugin | `ruleforge.remoteprovider` |
| File | `plugins/remote_provider_plugin.py` |
| Milestone | M12-F |
| Capability | `EXECUTION_HOOK` |
| Lifecycle Phase | Pre-execution |

**Responsibility:** Provider registration, discovery, and selection.

**Public API:**
- `Provider` (ABC): abstract provider interface
- `register(provider)` / `unregister(name)`
- `list_providers()` / `get(name)`
- `select(criteria)` → Provider
- `provider_count`

**Not Responsible For:** Remote invocation, execution runtime, rollback, validation.

**Typical Usage:**
```python
plugin = registry.get("ruleforge.remoteprovider")
provider = plugin.select({"type": "filesystem"})
```

---

## WorkflowPlugin

| Attribute | Value |
|---|---|
| Plugin | `ruleforge.workflow` |
| File | `plugins/workflow_plugin.py` |
| Milestone | M12-G |
| Capability | `EXECUTION_HOOK` |
| Lifecycle Phase | Mid-execution |

**Responsibility:** Workflow definition, step orchestration, and flow coordination.

**Public API:**
- `WorkflowStep` (frozen): name, action, dependencies
- `WorkflowDefinition` (frozen): name, steps, execution order
- `register(workflow)` / `unregister(name)`
- `list_workflows()` / `get(name)`
- `workflow_count`

**Not Responsible For:** Executing individual steps, scheduling, policy decisions, validation.

**Typical Usage:**
```python
plugin = registry.get("ruleforge.workflow")
wf = WorkflowDefinition("process", steps=[validate_step, rename_step])
```

---

## EventPlugin

| Attribute | Value |
|---|---|
| Plugin | `ruleforge.event` |
| File | `plugins/event_plugin.py` |
| Milestone | M12-H |
| Capability | `EXECUTION_HOOK` |
| Lifecycle Phase | Cross-cutting |

**Responsibility:** Event definition, publish, subscribe, and dispatch.

**Public API:**
- `Event` (frozen): name, data, timestamp
- `EventHandler` (frozen): event_name, callback
- `register(handler)` / `unregister(event_name, handler_id)`
- `list_handlers()` / `list_by_event(event_name)`
- `publish(event)` → `EventResult`
- `handler_count`

**Not Responsible For:** Business logic triggered by events, notification delivery, workflow orchestration.

**Typical Usage:**
```python
plugin = registry.get("ruleforge.event")
plugin.register(EventHandler("execution.completed", on_complete))
plugin.publish(Event("execution.completed", {"result": result}))
```

---

## PolicyPlugin

| Attribute | Value |
|---|---|
| Plugin | `ruleforge.policy` |
| File | `plugins/policy_plugin.py` |
| Milestone | M12-I |
| Capability | `EXECUTION_HOOK` |
| Lifecycle Phase | Pre-execution |

**Responsibility:** Policy definition, registration, and evaluation (allow/deny/warn).

**Public API:**
- `Policy` (frozen): name, description, evaluate callable
- `EvaluationResult` (frozen): policy_name, decision, reason, is_allowed/is_denied/is_warning
- `register(policy)` / `unregister(name)`
- `list_policies()` / `get(name)`
- `evaluate(name, context)` / `evaluate_all(context)`
- `has_deny(context)` → bool
- `policy_count`

**Not Responsible For:** Enforcement, RBAC/ABAC, authorization, execution, validation.

**Important:** v1 is a decision-support tool, NOT a security authorization engine. Default allow applies only to this Policy Capability Baseline.

**Typical Usage:**
```python
plugin = registry.get("ruleforge.policy")
result = plugin.evaluate("max-files", {"count": 10})
if result.is_denied:
    return  # blocked by policy
```

---

## ValidationPlugin

| Attribute | Value |
|---|---|
| Plugin | `ruleforge.validation` |
| File | `plugins/validation_plugin.py` |
| Milestone | M12-J |
| Capability | `EXECUTION_HOOK` |
| Lifecycle Phase | Pre-execution |

**Responsibility:** Validation rule definition, registration, and pass/fail checks.

**Public API:**
- `ValidationRule` (frozen): name, description, validate callable
- `ValidationResult` (frozen): rule_name, status (pass/fail), message, is_valid
- `register(rule)` / `unregister(name)`
- `list_rules()` / `get(name)`
- `validate(name, context)` / `validate_all(context)`
- `has_failures(context)` → bool
- `rule_count`

**Not Responsible For:** Auto-repair, policy decisions, business execution, rollback.

**Typical Usage:**
```python
plugin = registry.get("ruleforge.validation")
if not plugin.validate("non-empty-name", {"name": filename}).is_valid:
    return  # validation failed
```

---

## NotificationPlugin

| Attribute | Value |
|---|---|
| Plugin | `ruleforge.notification` |
| File | `plugins/notification_plugin.py` |
| Milestone | M12-K |
| Capability | `EXECUTION_HOOK` |
| Lifecycle Phase | Post-execution |

**Responsibility:** Channel registration, notification delivery, and broadcast.

**Public API:**
- `Notification` (frozen): subject, body, metadata, timestamp
- `NotificationChannel` (frozen): name, description, deliver callable
- `DeliveryResult` (frozen): channel_name, delivered, message
- `register(channel)` / `unregister(name)`
- `list_channels()` / `get(name)`
- `notify(name, notification)` / `notify_all(notification)`
- `channel_count`

**Not Responsible For:** Retry, queue, persistence, guaranteed delivery, async runtime, event bus.

**Important:** v1 is best-effort synchronous delivery. `notify_all()` isolates channel errors — one channel failing does not block others.

**Typical Usage:**
```python
plugin = registry.get("ruleforge.notification")
result = plugin.notify("console", Notification("Done", "All files renamed"))
plugin.notify_all(Notification("Batch complete"))
```
