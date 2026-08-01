"""Tests for M12-K NotificationPlugin — notification delivery channels."""

from __future__ import annotations

import pytest

from plugins.notification_plugin import (
    DeliveryResult,
    Notification,
    NotificationChannel,
    NotificationPlugin,
    delivery_failed,
    delivery_ok,
)
from plugins.plugin_capability import PluginCapability
from plugins.plugin_registry import PluginRegistry


# ── Plugin metadata & lifecycle ───────────────────────────────────


class TestNotificationPluginMetadata:
    def test_name(self) -> None:
        p = NotificationPlugin()
        assert p.name == "ruleforge.notification"

    def test_version(self) -> None:
        p = NotificationPlugin()
        assert p.version == "1.0.0"

    def test_capability(self) -> None:
        p = NotificationPlugin()
        assert PluginCapability.EXECUTION_HOOK in p.metadata.capabilities

    def test_dependencies(self) -> None:
        p = NotificationPlugin()
        assert p.metadata.dependencies == ()


class TestNotificationPluginLifecycle:
    def test_full_lifecycle_in_registry(self) -> None:
        reg = PluginRegistry()
        reg.register(NotificationPlugin())
        assert reg.state("ruleforge.notification") == "LOADED"
        reg.enable("ruleforge.notification")
        assert reg.state("ruleforge.notification") == "ENABLED"
        reg.activate("ruleforge.notification")
        assert reg.state("ruleforge.notification") == "ACTIVE"
        reg.deactivate("ruleforge.notification")
        assert reg.state("ruleforge.notification") == "ENABLED"

    def test_discovery_via_capability(self) -> None:
        reg = PluginRegistry()
        reg.register(NotificationPlugin())
        reg.enable("ruleforge.notification")
        plugins = reg.list_by_capability(PluginCapability.EXECUTION_HOOK)
        assert any(p.name == "ruleforge.notification" for p in plugins)

    def test_not_found_when_loaded_only(self) -> None:
        reg = PluginRegistry()
        reg.register(NotificationPlugin())
        assert reg.list_by_capability(PluginCapability.EXECUTION_HOOK) == []

    def test_channels_persist_after_deactivation(self) -> None:
        reg = PluginRegistry()
        reg.register(NotificationPlugin())
        reg.enable("ruleforge.notification")
        reg.activate("ruleforge.notification")

        plugin = reg.get("ruleforge.notification")
        assert plugin is not None
        plugin.register(NotificationChannel("ch1"))

        reg.deactivate("ruleforge.notification")
        assert plugin.channel_count == 1


# ── Channel registration ──────────────────────────────────────────


class TestChannelRegistration:
    def test_register(self) -> None:
        p = NotificationPlugin()
        p.register(NotificationChannel("test"))
        assert p.channel_count == 1

    def test_register_duplicate_raises(self) -> None:
        p = NotificationPlugin()
        p.register(NotificationChannel("test"))
        with pytest.raises(ValueError, match="already registered"):
            p.register(NotificationChannel("test"))

    def test_unregister(self) -> None:
        p = NotificationPlugin()
        p.register(NotificationChannel("test"))
        assert p.unregister("test")
        assert p.channel_count == 0

    def test_unregister_nonexistent_returns_false(self) -> None:
        p = NotificationPlugin()
        assert p.unregister("nope") is False

    def test_register_multiple(self) -> None:
        p = NotificationPlugin()
        p.register(NotificationChannel("a"))
        p.register(NotificationChannel("b"))
        p.register(NotificationChannel("c"))
        assert p.channel_count == 3


# ── Channel discovery ─────────────────────────────────────────────


class TestChannelDiscovery:
    def test_list_channels(self) -> None:
        p = NotificationPlugin()
        p.register(NotificationChannel("a"))
        p.register(NotificationChannel("b"))
        names = {c.name for c in p.list_channels()}
        assert names == {"a", "b"}

    def test_list_channels_empty(self) -> None:
        p = NotificationPlugin()
        assert p.list_channels() == ()

    def test_get_channel(self) -> None:
        p = NotificationPlugin()
        ch = NotificationChannel("test", "desc")
        p.register(ch)
        assert p.get("test") is ch

    def test_get_nonexistent_returns_none(self) -> None:
        p = NotificationPlugin()
        assert p.get("missing") is None


# ── Single-channel notify ─────────────────────────────────────────


class TestNotify:
    def test_notify_delivered(self) -> None:
        p = NotificationPlugin()
        p.register(NotificationChannel("ch", deliver=lambda n: True))
        result = p.notify("ch", Notification("subj"))
        assert result.delivered
        assert result.channel_name == "ch"

    def test_notify_failed(self) -> None:
        p = NotificationPlugin()
        p.register(NotificationChannel("ch", deliver=lambda n: False))
        result = p.notify("ch", Notification("subj"))
        assert not result.delivered
        assert result.message == "delivery returned False"

    def test_notify_unknown_channel_raises(self) -> None:
        p = NotificationPlugin()
        with pytest.raises(KeyError, match="not found"):
            p.notify("missing", Notification("x"))

    def test_notify_passes_notification(self) -> None:
        received: list[Notification] = []
        p = NotificationPlugin()
        p.register(
            NotificationChannel(
                "capture",
                deliver=lambda n: received.append(n) or True,
            )
        )
        notif = Notification("S", "B", {"k": "v"})
        p.notify("capture", notif)
        assert len(received) == 1
        assert received[0].subject == "S"
        assert received[0].body == "B"
        assert received[0].metadata == {"k": "v"}

    def test_notify_channel_raises_propagates(self) -> None:
        p = NotificationPlugin()
        p.register(
            NotificationChannel(
                "explosive",
                deliver=lambda n: (_ for _ in ()).throw(RuntimeError("boom")),  # type: ignore[attr-defined]
            )
        )
        with pytest.raises(RuntimeError, match="boom"):
            p.notify("explosive", Notification("x"))


# ── notify_all ────────────────────────────────────────────────────


class TestNotifyAll:
    def test_notify_all_multiple(self) -> None:
        results_received: list[str] = []

        def make_deliver(name: str):
            def _deliver(n: Notification) -> bool:
                results_received.append(name)
                return True

            return _deliver

        p = NotificationPlugin()
        p.register(NotificationChannel("a", deliver=make_deliver("a")))
        p.register(NotificationChannel("b", deliver=make_deliver("b")))
        p.register(NotificationChannel("c", deliver=make_deliver("c")))

        results = p.notify_all(Notification("subj"))
        assert len(results) == 3
        assert all(r.delivered for r in results.values())
        assert results_received == ["a", "b", "c"]

    def test_notify_all_empty_registry(self) -> None:
        p = NotificationPlugin()
        assert p.notify_all(Notification("subj")) == {}

    def test_notify_all_mixed_results(self) -> None:
        p = NotificationPlugin()
        p.register(NotificationChannel("pass", deliver=lambda n: True))
        p.register(NotificationChannel("fail", deliver=lambda n: False))

        results = p.notify_all(Notification("subj"))
        assert results["pass"].delivered
        assert not results["fail"].delivered

    def test_notify_all_isolates_channel_errors(self) -> None:
        """One channel raising does NOT affect delivery to others."""
        reached: list[str] = []

        p = NotificationPlugin()
        p.register(
            NotificationChannel(
                "before",
                deliver=lambda n: reached.append("before") or True,
            )
        )
        p.register(
            NotificationChannel(
                "explosive",
                deliver=lambda n: (_ for _ in ()).throw(RuntimeError("boom")),  # type: ignore[attr-defined]
            )
        )
        p.register(
            NotificationChannel(
                "after",
                deliver=lambda n: reached.append("after") or True,
            )
        )

        results = p.notify_all(Notification("subj"))
        assert results["before"].delivered
        assert not results["explosive"].delivered
        assert "boom" in results["explosive"].message
        assert results["after"].delivered
        assert reached == ["before", "after"]

    def test_notify_all_order_stable(self) -> None:
        p = NotificationPlugin()
        p.register(NotificationChannel("a"))
        p.register(NotificationChannel("b"))
        p.register(NotificationChannel("c"))
        order = list(p.notify_all(Notification("x")).keys())
        assert order == ["a", "b", "c"]


# ── Notification model ────────────────────────────────────────────


class TestNotificationModel:
    def test_defaults(self) -> None:
        n = Notification("subj")
        assert n.subject == "subj"
        assert n.body == ""
        assert n.metadata == {}

    def test_all_fields(self) -> None:
        n = Notification("S", "B", {"k": "v"}, 100.0)
        assert n.subject == "S"
        assert n.body == "B"
        assert n.metadata == {"k": "v"}
        assert n.timestamp == 100.0

    def test_frozen(self) -> None:
        n = Notification("subj")
        with pytest.raises(Exception):
            n.subject = "other"  # type: ignore[misc]

    def test_timestamp_auto(self) -> None:
        n1 = Notification("a")
        n2 = Notification("b")
        assert n1.timestamp > 0
        assert n2.timestamp >= n1.timestamp


# ── NotificationChannel model ─────────────────────────────────────


class TestNotificationChannelModel:
    def test_defaults(self) -> None:
        ch = NotificationChannel("test")
        assert ch.name == "test"
        assert ch.description == ""

    def test_empty_name_raises(self) -> None:
        with pytest.raises(ValueError, match="must not be empty"):
            NotificationChannel("")

    def test_frozen(self) -> None:
        ch = NotificationChannel("test")
        with pytest.raises(Exception):
            ch.name = "other"  # type: ignore[misc]


# ── DeliveryResult model ──────────────────────────────────────────


class TestDeliveryResult:
    def test_defaults(self) -> None:
        r = DeliveryResult("ch", True)
        assert r.channel_name == "ch"
        assert r.delivered
        assert r.message == ""

    def test_frozen(self) -> None:
        r = DeliveryResult("ch", False, "bad")
        with pytest.raises(Exception):
            r.delivered = True  # type: ignore[misc]


# ── Convenience constructors ──────────────────────────────────────


class TestConvenienceConstructors:
    def test_delivery_ok(self) -> None:
        r = delivery_ok("ch")
        assert r.delivered
        assert r.channel_name == "ch"
        assert r.message == ""

    def test_delivery_failed(self) -> None:
        r = delivery_failed("ch", "reason")
        assert not r.delivered
        assert r.channel_name == "ch"
        assert r.message == "reason"


# ── Plugin independence ───────────────────────────────────────────


class TestPluginIndependence:
    def test_no_engine_imports(self) -> None:
        import plugins.notification_plugin as np

        source = np.__file__
        assert source is not None
        with open(source) as f:
            content = f.read()
        assert "from engine" not in content
        assert "import engine" not in content

    def test_standalone_usage_without_registry(self) -> None:
        p = NotificationPlugin()
        p.register(NotificationChannel("console"))
        result = p.notify("console", Notification("hello"))
        assert result.delivered
        assert result.channel_name == "console"


# ── Reference channels ────────────────────────────────────────────


class TestReferenceChannels:
    def test_console_channel(self, capsys) -> None:  # type: ignore[no-untyped-def]
        p = NotificationPlugin()
        p.register(
            NotificationChannel(
                "console",
                deliver=lambda n: print(f"[{n.subject}] {n.body}") or True,
            )
        )
        result = p.notify("console", Notification("ALERT", "Disk full"))
        assert result.delivered
        captured = capsys.readouterr()
        assert "[ALERT] Disk full" in captured.out

    def test_collector_channel(self) -> None:
        collected: list[Notification] = []

        p = NotificationPlugin()
        p.register(
            NotificationChannel(
                "collector",
                deliver=lambda n: collected.append(n) or True,
            )
        )
        n1 = Notification("A")
        n2 = Notification("B")
        p.notify("collector", n1)
        p.notify("collector", n2)
        assert len(collected) == 2
        assert collected[0].subject == "A"
        assert collected[1].subject == "B"

    def test_collector_via_notify_all(self) -> None:
        collected: list[Notification] = []

        p = NotificationPlugin()
        p.register(
            NotificationChannel(
                "collector",
                deliver=lambda n: collected.append(n) or True,
            )
        )
        notif = Notification("Batch")
        p.notify_all(notif)
        assert len(collected) == 1


# ── Full integration flow ─────────────────────────────────────────


class TestFullIntegrationFlow:
    def test_register_discover_notify(self) -> None:
        reg = PluginRegistry()
        reg.register(NotificationPlugin())
        reg.enable("ruleforge.notification")
        reg.activate("ruleforge.notification")

        plugin = reg.get("ruleforge.notification")
        assert plugin is not None

        # Register reference channels
        plugin.register(
            NotificationChannel(
                "console",
                "Print to stdout",
            )
        )
        plugin.register(
            NotificationChannel(
                "collector",
                "Store in memory",
            )
        )

        # Discover
        channels = plugin.list_channels()
        assert len(channels) == 2
        assert {c.name for c in channels} == {"console", "collector"}

        # Single notify
        assert plugin.notify("console", Notification("test")).delivered

        # notify_all
        results = plugin.notify_all(Notification("all"))
        assert results["console"].delivered
        assert results["collector"].delivered

        # Unregister
        assert plugin.unregister("console")
        assert plugin.channel_count == 1
