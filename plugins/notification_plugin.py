"""NotificationPlugin — capability plugin for notification delivery.

Manages notification channel registration, discovery, and dispatch.
Each channel delivers Notifications to an external target (console,
file, webhook, in-memory collector, etc.).

v1: Best-effort, synchronous, lightweight.  No retry, queue,
persistence, or guaranteed delivery.

Does not modify Execution Platform, Batch Execution, or Plugin
Framework contracts.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable

from plugins.plugin import Plugin, PluginMetadata
from plugins.plugin_capability import PluginCapability
from plugins.plugin_context import PluginContext


# ── Notification model ───────────────────────────────────────────


@dataclass(frozen=True)
class Notification:
    """A notification to be delivered through a channel.

    Attributes:
        subject: Short summary of the notification.
        body: Detailed message content.
        metadata: Optional key-value context (execution IDs, timings, etc.).
        timestamp: Unix timestamp when the notification was created.
    """
    subject: str
    body: str = ""
    metadata: dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


# ── Delivery result ──────────────────────────────────────────────


@dataclass(frozen=True)
class DeliveryResult:
    """Outcome of delivering a notification to a channel.

    Attributes:
        channel_name: The channel that was notified.
        delivered: True if the channel accepted the notification.
        message: Optional diagnostic message (empty on success).
    """
    channel_name: str
    delivered: bool
    message: str = ""


def delivery_ok(channel_name: str) -> DeliveryResult:
    return DeliveryResult(channel_name=channel_name, delivered=True)


def delivery_failed(channel_name: str, message: str = "") -> DeliveryResult:
    return DeliveryResult(channel_name=channel_name, delivered=False, message=message)


# ── Channel model ─────────────────────────────────────────────────


@dataclass(frozen=True)
class NotificationChannel:
    """A named delivery target for notifications.

    Attributes:
        name: Unique channel identifier.
        description: Human-readable description.
        deliver: Callable that receives a Notification and returns
            True (delivered) or False (failed).
    """
    name: str
    description: str = ""
    deliver: Callable = field(default=lambda n: True)

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("Channel name must not be empty")


# ── Plugin ───────────────────────────────────────────────────────


class NotificationPlugin(Plugin):
    """Manages notification channel registration, discovery, and delivery.

    Usage:
        plugin = NotificationPlugin()
        registry.register(plugin)
        registry.enable(plugin.name)
        registry.activate(plugin.name)

        channel = NotificationChannel(
            name="console",
            description="Print to stdout",
            deliver=lambda n: print(n.subject) or True,
        )
        plugin.register(channel)
        result = plugin.notify("console", Notification("Hello"))
        assert result.delivered

    Capability: EXECUTION_HOOK — notifications complement execution feedback.
    """

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="ruleforge.notification",
            version="1.0.0",
            description="Manages notification channel registration, discovery, and delivery",
            author="RuleForge",
            capabilities=(PluginCapability.EXECUTION_HOOK,),
        )

    def __init__(self) -> None:
        self._channels: dict[str, NotificationChannel] = {}

    def on_activate(self, ctx: PluginContext) -> None:
        pass

    def on_deactivate(self, ctx: PluginContext) -> None:
        pass

    # ── Registration ───────────────────────────────────────────

    def register(self, channel: NotificationChannel) -> None:
        """Register a channel. Raises ValueError on duplicate name."""
        if channel.name in self._channels:
            raise ValueError(
                f"Notification channel '{channel.name}' is already registered"
            )
        self._channels[channel.name] = channel

    def unregister(self, name: str) -> bool:
        """Unregister a channel by name. Returns True if removed."""
        return self._channels.pop(name, None) is not None

    # ── Discovery ──────────────────────────────────────────────

    def list_channels(self) -> tuple[NotificationChannel, ...]:
        """Return all registered channels."""
        return tuple(self._channels.values())

    def get(self, name: str) -> NotificationChannel | None:
        """Return a channel by name, or None."""
        return self._channels.get(name)

    @property
    def channel_count(self) -> int:
        return len(self._channels)

    # ── Delivery ───────────────────────────────────────────────

    def notify(
        self,
        channel_name: str,
        notification: Notification,
    ) -> DeliveryResult:
        """Deliver a notification to a single channel.

        Raises KeyError if the channel is not found.
        Channel exceptions propagate to the caller.
        """
        channel = self._channels.get(channel_name)
        if channel is None:
            raise KeyError(
                f"Notification channel '{channel_name}' not found"
            )
        return _deliver(channel, notification)

    def notify_all(
        self,
        notification: Notification,
    ) -> dict[str, DeliveryResult]:
        """Deliver a notification to all registered channels.

        Each channel is executed independently.  One channel
        failing (including raising an exception) does NOT affect
        delivery to other channels.  Exceptions are caught and
        reported as DeliveryResult(delivered=False, message=...).

        Returns a dict mapping channel_name → DeliveryResult,
        in registration order.
        """
        results: dict[str, DeliveryResult] = {}
        for channel in self._channels.values():
            try:
                results[channel.name] = _deliver(channel, notification)
            except Exception as exc:
                results[channel.name] = delivery_failed(
                    channel.name, str(exc)
                )
        return results


# ── Internal ──────────────────────────────────────────────────────


def _deliver(
    channel: NotificationChannel,
    notification: Notification,
) -> DeliveryResult:
    delivered = channel.deliver(notification)
    if delivered:
        return delivery_ok(channel.name)
    return delivery_failed(channel.name, "delivery returned False")
