"""Tests for M12-H EventPlugin — event-driven pub/sub dispatch."""

from __future__ import annotations

import pytest

from plugins.event_plugin import (
    Event,
    EventPlugin,
    EventResult,
    SubscriberInfo,
)
from plugins.plugin_capability import PluginCapability
from plugins.plugin_registry import PluginRegistry


# ── Plugin metadata & lifecycle ───────────────────────────────────


class TestEventPluginMetadata:
    def test_name(self) -> None:
        p = EventPlugin()
        assert p.name == "ruleforge.event"

    def test_version(self) -> None:
        p = EventPlugin()
        assert p.version == "1.0.0"

    def test_capability(self) -> None:
        p = EventPlugin()
        assert PluginCapability.EXECUTION_HOOK in p.metadata.capabilities

    def test_dependencies(self) -> None:
        p = EventPlugin()
        assert p.metadata.dependencies == ()

    def test_builtin_event_constants(self) -> None:
        assert EventPlugin.EVENT_EXECUTION_STARTED == "execution.started"
        assert EventPlugin.EVENT_EXECUTION_COMPLETED == "execution.completed"
        assert EventPlugin.EVENT_EXECUTION_FAILED == "execution.failed"


class TestEventPluginLifecycle:
    def test_full_lifecycle_in_registry(self) -> None:
        reg = PluginRegistry()
        reg.register(EventPlugin())
        assert reg.state("ruleforge.event") == "LOADED"
        reg.enable("ruleforge.event")
        assert reg.state("ruleforge.event") == "ENABLED"
        reg.activate("ruleforge.event")
        assert reg.state("ruleforge.event") == "ACTIVE"
        reg.deactivate("ruleforge.event")
        assert reg.state("ruleforge.event") == "ENABLED"

    def test_discovery_via_capability(self) -> None:
        reg = PluginRegistry()
        reg.register(EventPlugin())
        reg.enable("ruleforge.event")
        plugins = reg.list_by_capability(PluginCapability.EXECUTION_HOOK)
        assert any(p.name == "ruleforge.event" for p in plugins)

    def test_not_found_when_loaded_only(self) -> None:
        reg = PluginRegistry()
        reg.register(EventPlugin())
        assert reg.list_by_capability(PluginCapability.EXECUTION_HOOK) == []

    def test_subscriptions_persist_after_deactivation(self) -> None:
        reg = PluginRegistry()
        reg.register(EventPlugin())
        reg.enable("ruleforge.event")
        reg.activate("ruleforge.event")

        plugin = reg.get("ruleforge.event")
        assert plugin is not None
        plugin.subscribe("test.event", lambda e: None)

        reg.deactivate("ruleforge.event")
        assert plugin.subscriber_count == 1


# ── Subscribe / Unsubscribe ───────────────────────────────────────


class TestSubscribe:
    def test_subscribe_returns_id(self) -> None:
        p = EventPlugin()
        sid = p.subscribe("evt", lambda e: None)
        assert isinstance(sid, str)
        assert len(sid) > 0

    def test_subscribe_increments_count(self) -> None:
        p = EventPlugin()
        p.subscribe("evt", lambda e: None)
        assert p.subscriber_count == 1

    def test_unsubscribe_removes(self) -> None:
        p = EventPlugin()
        sid = p.subscribe("evt", lambda e: None)
        assert p.subscriber_count == 1
        assert p.unsubscribe("evt", sid)
        assert p.subscriber_count == 0

    def test_unsubscribe_nonexistent_event_returns_false(self) -> None:
        p = EventPlugin()
        assert p.unsubscribe("no-such", "id") is False

    def test_unsubscribe_nonexistent_subscriber_returns_false(self) -> None:
        p = EventPlugin()
        p.subscribe("evt", lambda e: None)
        assert p.unsubscribe("evt", "wrong-id") is False

    def test_unsubscribe_wrong_event_returns_false(self) -> None:
        p = EventPlugin()
        sid = p.subscribe("evt", lambda e: None)
        assert p.unsubscribe("other", sid) is False

    def test_multiple_subscribers_same_event(self) -> None:
        p = EventPlugin()
        p.subscribe("evt", lambda e: None)
        p.subscribe("evt", lambda e: None)
        assert p.subscriber_count == 2


# ── Publish / Dispatch ────────────────────────────────────────────


class TestPublish:
    def test_publish_without_subscribers(self) -> None:
        p = EventPlugin()
        result = p.publish("no.subscribers")
        assert result.subscriber_count == 0
        assert result.delivered == 0
        assert result.failed == 0
        assert result.all_delivered

    def test_publish_delivers_to_subscriber(self) -> None:
        p = EventPlugin()
        received: list[Event] = []
        p.subscribe("test.evt", lambda e: received.append(e))
        result = p.publish("test.evt", {"k": "v"})
        assert result.subscriber_count == 1
        assert result.delivered == 1
        assert result.failed == 0
        assert len(received) == 1
        assert received[0].name == "test.evt"
        assert received[0].data == {"k": "v"}

    def test_publish_to_multiple_subscribers(self) -> None:
        p = EventPlugin()
        calls: list[str] = []
        p.subscribe("evt", lambda e: calls.append("a"))
        p.subscribe("evt", lambda e: calls.append("b"))
        result = p.publish("evt")
        assert result.subscriber_count == 2
        assert result.delivered == 2
        assert calls == ["a", "b"]

    def test_dispatch_order_is_registration_order(self) -> None:
        p = EventPlugin()
        order: list[int] = []
        p.subscribe("evt", lambda e: order.append(1))
        p.subscribe("evt", lambda e: order.append(2))
        p.subscribe("evt", lambda e: order.append(3))
        p.publish("evt")
        assert order == [1, 2, 3]

    def test_event_has_timestamp_and_id(self) -> None:
        p = EventPlugin()
        received: list[Event] = []
        p.subscribe("evt", lambda e: received.append(e))
        p.publish("evt")
        assert len(received) == 1
        assert received[0].timestamp > 0
        assert len(received[0].event_id) > 0


# ── Error Handling ────────────────────────────────────────────────


class TestErrorHandling:
    def test_subscriber_error_does_not_block_others(self) -> None:
        p = EventPlugin()

        def _fail(e: Event) -> None:
            raise RuntimeError("boom")

        received: list[Event] = []
        p.subscribe("evt", _fail)
        p.subscribe("evt", lambda e: received.append(e))

        result = p.publish("evt")
        assert result.subscriber_count == 2
        assert result.failed == 1
        assert result.delivered == 1
        assert not result.all_delivered
        assert len(received) == 1

    def test_all_subscribers_fail(self) -> None:
        p = EventPlugin()

        def _fail(e: Event) -> None:
            raise RuntimeError("boom")

        p.subscribe("evt", _fail)
        p.subscribe("evt", _fail)
        result = p.publish("evt")
        assert result.failed == 2
        assert result.delivered == 0
        assert not result.all_delivered

    def test_publish_still_works_after_error(self) -> None:
        p = EventPlugin()

        def _fail(e: Event) -> None:
            raise RuntimeError("boom")

        p.subscribe("evt", _fail)
        p.publish("evt")

        # Plugin still functional
        received: list[Event] = []
        p.subscribe("evt2", lambda e: received.append(e))
        result = p.publish("evt2", {"x": 1})
        assert result.delivered == 1
        assert len(received) == 1
        assert received[0].data == {"x": 1}


# ── Query ─────────────────────────────────────────────────────────


class TestQuery:
    def test_list_subscribers(self) -> None:
        p = EventPlugin()
        sid1 = p.subscribe("evt", lambda e: None)
        sid2 = p.subscribe("evt", lambda e: None)
        subs = p.list_subscribers("evt")
        assert len(subs) == 2
        assert {s.subscriber_id for s in subs} == {sid1, sid2}

    def test_list_subscribers_empty(self) -> None:
        p = EventPlugin()
        assert p.list_subscribers("none") == ()

    def test_list_event_types(self) -> None:
        p = EventPlugin()
        p.subscribe("a", lambda e: None)
        p.subscribe("b", lambda e: None)
        assert p.list_event_types() == ("a", "b")

    def test_list_event_types_empty(self) -> None:
        p = EventPlugin()
        assert p.list_event_types() == ()


# ── Event dataclass ───────────────────────────────────────────────


class TestEvent:
    def test_defaults(self) -> None:
        e = Event("test")
        assert e.name == "test"
        assert e.data == {}
        assert e.timestamp > 0
        assert len(e.event_id) > 0

    def test_unique_ids(self) -> None:
        a = Event("x")
        b = Event("x")
        assert a.event_id != b.event_id

    def test_frozen(self) -> None:
        e = Event("test")
        with pytest.raises(Exception):
            e.name = "other"  # type: ignore[misc]


# ── EventResult dataclass ─────────────────────────────────────────


class TestEventResult:
    def test_all_delivered(self) -> None:
        assert EventResult(Event("x"), 1, 1, 0).all_delivered
        assert not EventResult(Event("x"), 1, 0, 1).all_delivered

    def test_frozen(self) -> None:
        r = EventResult(Event("x"), 1, 1, 0)
        with pytest.raises(Exception):
            r.delivered = 2  # type: ignore[misc]


# ── SubscriberInfo dataclass ──────────────────────────────────────


class TestSubscriberInfo:
    def test_fields(self) -> None:
        s = SubscriberInfo("id1", "evt")
        assert s.subscriber_id == "id1"
        assert s.event_name == "evt"

    def test_frozen(self) -> None:
        s = SubscriberInfo("id1", "evt")
        with pytest.raises(Exception):
            s.subscriber_id = "id2"  # type: ignore[misc]


# ── Plugin independence ───────────────────────────────────────────


class TestPluginIndependence:
    def test_no_engine_imports(self) -> None:
        import plugins.event_plugin as ep

        source = ep.__file__
        assert source is not None
        with open(source) as f:
            content = f.read()
        assert "from engine" not in content
        assert "import engine" not in content

    def test_standalone_usage_without_registry(self) -> None:
        p = EventPlugin()
        received: list[Event] = []
        p.subscribe("evt", lambda e: received.append(e))
        result = p.publish("evt", {"key": "val"})
        assert result.delivered == 1
        assert received[0].data == {"key": "val"}


# ── Full integration flow ─────────────────────────────────────────


class TestFullIntegrationFlow:
    def test_subscribe_publish_dispatch(self) -> None:
        reg = PluginRegistry()
        reg.register(EventPlugin())
        reg.enable("ruleforge.event")
        reg.activate("ruleforge.event")

        plugin = reg.get("ruleforge.event")
        assert plugin is not None

        # Subscribe to built-in events
        started: list[Event] = []
        completed: list[Event] = []

        plugin.subscribe(EventPlugin.EVENT_EXECUTION_STARTED, lambda e: started.append(e))
        plugin.subscribe(EventPlugin.EVENT_EXECUTION_COMPLETED, lambda e: completed.append(e))

        # Publish
        r1 = plugin.publish(EventPlugin.EVENT_EXECUTION_STARTED, {"file": "a.txt"})
        assert r1.delivered == 1
        assert len(started) == 1
        assert started[0].data == {"file": "a.txt"}

        r2 = plugin.publish(EventPlugin.EVENT_EXECUTION_COMPLETED, {"files": 3})
        assert r2.delivered == 1
        assert len(completed) == 1
        assert completed[0].data == {"files": 3}

        # Subscribers discoverable
        assert len(plugin.list_subscribers("execution.started")) == 1
        assert len(plugin.list_subscribers("execution.completed")) == 1

        # Unsubscribe
        sid = started[0].event_id  # not subscriber id — need the actual sub id
        # Unsubscribe by listing then removing
        subs = plugin.list_subscribers("execution.started")
        plugin.unsubscribe("execution.started", subs[0].subscriber_id)
        assert plugin.list_subscribers("execution.started") == ()
