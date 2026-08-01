"""EventPlugin — capability plugin for event-driven architecture.

Manages event type definitions, subscriber registration, and
synchronous pub/sub dispatch.  Each subscriber receives an Event
and may process or ignore it.  Errors in one subscriber do not
prevent other subscribers from receiving the event.

Does not modify Execution Platform, Batch Execution, or Plugin
Framework contracts.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field

from plugins.plugin import Plugin, PluginMetadata
from plugins.plugin_capability import PluginCapability
from plugins.plugin_context import PluginContext


# ── Event model ───────────────────────────────────────────────────


@dataclass(frozen=True)
class Event:
    """An immutable event published to subscribers.

    Attributes:
        name: Event type name (e.g. 'execution.started').
        data: Arbitrary payload dict.
        timestamp: Unix timestamp when published.
        event_id: Unique event instance identifier.
    """

    name: str
    data: dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))


# ── Result types ───────────────────────────────────────────────────


@dataclass(frozen=True)
class EventResult:
    """Outcome of publishing an event.

    Attributes:
        event: The published event.
        subscriber_count: Total subscribers for this event type.
        delivered: Number of subscribers successfully called.
        failed: Number of subscriber callbacks that raised.
    """

    event: Event
    subscriber_count: int
    delivered: int
    failed: int

    @property
    def all_delivered(self) -> bool:
        return self.failed == 0


@dataclass(frozen=True)
class SubscriberInfo:
    """Read-only snapshot of a subscriber."""

    subscriber_id: str
    event_name: str


# ── Plugin ─────────────────────────────────────────────────────────


class EventPlugin(Plugin):
    """Manages event pub/sub — define, subscribe, publish, dispatch.

    Usage:
        plugin = EventPlugin()
        registry.register(plugin)
        registry.enable(plugin.name)
        registry.activate(plugin.name)

        def on_started(event: Event) -> None:
            print(f"Started: {event.data}")

        plugin.subscribe("execution.started", on_started)
        result = plugin.publish("execution.started", {"file": "a.txt"})

    Capability: EXECUTION_HOOK — event-driven execution coordination.
    """

    # Built-in reference events
    EVENT_EXECUTION_STARTED = "execution.started"
    EVENT_EXECUTION_COMPLETED = "execution.completed"
    EVENT_EXECUTION_FAILED = "execution.failed"

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="ruleforge.event",
            version="1.0.0",
            description="Manages event pub/sub — define, subscribe, publish, dispatch",
            author="RuleForge",
            capabilities=(PluginCapability.EXECUTION_HOOK,),
        )

    def __init__(self) -> None:
        # event_name → list of (subscriber_id, callback)
        self._subscribers: dict[str, list[tuple[str, object]]] = {}

    def on_activate(self, ctx: PluginContext) -> None:
        pass

    def on_deactivate(self, ctx: PluginContext) -> None:
        # Preserve subscriptions on deactivation (Lifecycle vs Business State)
        pass

    # ── Subscribe / Unsubscribe ────────────────────────────────

    def subscribe(self, event_name: str, callback: object) -> str:
        """Subscribe to an event type.

        Returns a subscriber_id for unsubscription.
        Callbacks receive an Event as their sole argument.
        """
        sub_id = str(uuid.uuid4())
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        self._subscribers[event_name].append((sub_id, callback))
        return sub_id

    def unsubscribe(self, event_name: str, subscriber_id: str) -> bool:
        """Remove a subscriber by ID. Returns True if removed."""
        subs = self._subscribers.get(event_name)
        if subs is None:
            return False
        for i, (sid, _) in enumerate(subs):
            if sid == subscriber_id:
                subs.pop(i)
                if not subs:
                    del self._subscribers[event_name]
                return True
        return False

    # ── Query ──────────────────────────────────────────────────

    def list_subscribers(self, event_name: str) -> tuple[SubscriberInfo, ...]:
        """Return a snapshot of subscribers for an event type."""
        subs = self._subscribers.get(event_name)
        if subs is None:
            return ()
        return tuple(
            SubscriberInfo(subscriber_id=sid, event_name=event_name)
            for sid, _ in subs
        )

    def list_event_types(self) -> tuple[str, ...]:
        """Return all event types that have at least one subscriber."""
        return tuple(sorted(self._subscribers.keys()))

    @property
    def subscriber_count(self) -> int:
        return sum(len(subs) for subs in self._subscribers.values())

    # ── Publish / Dispatch ─────────────────────────────────────

    def publish(self, event_name: str, data: dict | None = None) -> EventResult:
        """Publish an event and synchronously dispatch to all subscribers.

        Each subscriber is called in registration order.  If a
        subscriber raises an exception, the error is recorded and
        subsequent subscribers still receive the event.

        Returns an EventResult summarizing delivery.
        """
        event = Event(name=event_name, data=data or {})
        subs = self._subscribers.get(event_name, [])

        delivered = 0
        failed = 0

        for _, callback in subs:
            try:
                callback(event)  # type: ignore[operator]
                delivered += 1
            except Exception:
                failed += 1

        return EventResult(
            event=event,
            subscriber_count=len(subs),
            delivered=delivered,
            failed=failed,
        )
