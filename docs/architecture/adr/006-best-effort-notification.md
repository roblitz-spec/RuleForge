# ADR-006: Best-Effort Notification Delivery

## Status

Accepted (M12-K). Frozen.

## Context

M12-K introduced `NotificationPlugin`, the first capability plugin for
external communication. Notifications could be delivered to channels
(console, collector, future webhooks). The question: should notification
delivery be guaranteed (retry, queue, persistence) or best-effort?

## Decision

Notification Plugin v1 provides best-effort, synchronous delivery only.

- `notify(channel, notification)`: attempts delivery, returns `DeliveryResult`
- `notify_all(notification)`: delivers to all channels; one channel failing
  (including raising) does not block delivery to other channels
- No retry, queue, persistence, or guaranteed delivery
- No async runtime

Channel exceptions in `notify_all()` are caught and reported as
`DeliveryResult(delivered=False, message=str(exc))`.

## Consequences

**Positive:**
- Simple, predictable, testable behavior
- No infrastructure dependency (no queue, no persistence layer)
- Channel isolation in `notify_all()` is robust

**Negative:**
- Not suitable for critical notifications that must not be lost
- Future guaranteed-delivery requirements will need a separate capability
  or a v2 enhancement (through an Enhancement Proposal, not by modifying v1)

## Evidence

- `test_notify_all_isolates_channel_errors`: verifies "before" and "after"
  channels both succeed when middle channel raises
- `test_notify_channel_raises_propagates`: verifies single-channel notify
  propagates exceptions (caller handles)
