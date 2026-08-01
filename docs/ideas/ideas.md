# Ideas & Deferred Capabilities

_M12 Baseline — Recorded, not planned._

This file records capability ideas that were considered during the M12
Capability Planning Review but deferred. Each entry explains why the
capability is not being implemented now and what conditions might
trigger re-evaluation.

No milestone is planned. No implementation design is provided.

---

## AuditPlugin

**What:** Structured audit trail of all execution decisions.

**Why deferred:** Audit = `EventPlugin.emit() + NotificationPlugin.notify("audit-channel")`.
Composable from existing plugins. M11's `ExecutionTrace` already provides
structured execution data.

**Re-evaluate if:** External audit requirements mandate dedicated audit log
format and guaranteed delivery that composition cannot provide.

---

## AuthPlugin / RBAC

**What:** Role-based access control for execution actions.

**Why deferred:** RuleForge is a file renaming tool, not a multi-user platform.
PolicyPlugin v1 explicitly excludes RBAC. Adding auth would be architectural
overreach for the current scope.

**Re-evaluate if:** RuleForge becomes a multi-user service with distinct roles.

---

## TemplatePlugin

**What:** Template-based output generation.

**Why deferred:** Template rendering is a RuleEngine concern (the `replace`,
`insert`, `date`, `number` rules already transform filenames). Templates
belong in the engine/rules layer, not as a cross-cutting plugin.

**Re-evaluate if:** Template requirements cannot be met by extending RuleEngine.

---

## CachePlugin

**What:** Result caching for repeated operations.

**Why deferred:** Caching is an engine-level optimization. M11 ExecutionEngine
implementations handle caching internally. A plugin for caching would violate
the principle that engines own execution semantics.

**Re-evaluate if:** Cross-engine caching becomes necessary and cannot be
implemented at the engine layer.

---

## ReportPlugin

**What:** Generate summary reports of execution results.

**Why deferred:** ExecutionResult already returns structured data. NotificationPlugin
with a report channel can deliver formatted reports. EventPlugin triggers can
initiate report generation via WorkflowPlugin.

**Re-evaluate if:** Complex multi-format reporting with templates exceeds what
composition can provide.

---

## LoggingPlugin

**What:** Structured logging to external sinks.

**Why deferred:** M11 ExecutionTrace handles execution logging. NotificationPlugin
with a log channel handles external delivery. EventPlugin handles lifecycle events.

**Re-evaluate if:** Logging requirements demand format standardization or guaranteed
delivery that composition cannot provide.

---

## RateLimitPlugin

**What:** Execution rate limiting.

**Why deferred:** SchedulerPlugin owns timing. PolicyPlugin can gate execution.
Combined: `Scheduler.delay() + Policy.evaluate(rate_limit_policy)`.

**Re-evaluate if:** Complex rate limiting policies (token bucket, sliding window)
require dedicated infrastructure.

---

## ConfigPlugin

**What:** Centralized configuration management.

**Why deferred:** Each plugin manages its own configuration. Centralized config
would require modifying PluginContext (M12-B framework), violating Frozen Contract.
This is a framework-level concern, not a capability plugin.

**Re-evaluate if:** Plugin configuration complexity reaches a threshold where
per-plugin config becomes unmanageable.

---

## Summary

| Candidate | Reason Deferred |
|---|---|
| AuditPlugin | Composable (Event + Notification) |
| AuthPlugin / RBAC | Architectural overreach |
| TemplatePlugin | Belongs in RuleEngine layer |
| ReportPlugin | Composable (Notification + Event) |
| CachePlugin | Belongs in Engine layer |
| LoggingPlugin | Composable (Trace + Notification) |
| RateLimitPlugin | Composable (Scheduler + Policy) |
| ConfigPlugin | Framework-level (requires PluginContext changes) |

These are recorded for future reference only. No implementation is planned.
