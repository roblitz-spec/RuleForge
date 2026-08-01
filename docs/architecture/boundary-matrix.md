# Boundary Matrix

_M12 Baseline — Frozen_

Every capability plugin owns exactly one concern. This matrix documents
which plugin is responsible for which concern.

## Responsibility Matrix

| Concern | RuleVal | Rollback | Sched | RemoteProv | Workflow | Event | Policy | Valid | Notify | Engine |
|---|---|---|---|---|---|---|---|---|---|---|
| Rule config validation | ✅ | — | — | — | — | — | — | — | — | — |
| Recovery & compensation | — | ✅ | — | — | — | — | — | — | — | — |
| Trigger & timing | — | — | ✅ | — | — | — | — | — | — | — |
| Provider selection | — | — | — | ✅ | — | — | — | — | — | — |
| Step orchestration | — | — | — | — | ✅ | — | — | — | — | — |
| Pub/sub events | — | — | — | — | — | ✅ | — | — | — | — |
| allow/deny/warn | — | — | — | — | — | — | ✅ | — | — | — |
| pass/fail checks | — | — | — | — | — | — | — | ✅ | — | — |
| Channel delivery | — | — | — | — | — | — | — | — | ✅ | — |
| Execute tasks | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |

✅ = Primary responsibility
— = Not responsible (belongs to another plugin or layer)
❌ = Explicitly excluded

## Exclusion Matrix

| Concern | All Plugins |
|---|---|
| Execute tasks | ❌ Engine only |
| Business logic | ❌ Caller only |
| Cross-plugin imports | ❌ Plugin Framework only |
| engine/ imports | ❌ Plugin Framework only |

## Key Boundaries

### Policy vs. Validation

- **PolicyPlugin** decides "should we proceed?" → allow/deny/warn
- **ValidationPlugin** checks "is this data valid?" → pass/fail
- Both are pre-execution, both are advisory, both leave action to the caller.

### Event vs. Notification

- **EventPlugin** handles internal pub/sub within the plugin ecosystem.
- **NotificationPlugin** handles external delivery to channels (console, collector, future webhooks).
- Events are intra-platform; notifications are extra-platform.

### Workflow vs. Engine

- **WorkflowPlugin** orchestrates steps — defines order, flow, coordination.
- **ExecutionPlatform** executes steps — owns runtime, context, result delivery.
- Workflow says "in what order"; Engine says "what happens."

## Verification

This matrix was verified during the M12 Architecture Consistency Review.
Zero overlaps detected. Zero cross-plugin dependencies exist in the codebase.
