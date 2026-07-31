"""Tests for M12-E SchedulerPlugin — capability plugin for scheduling."""

from __future__ import annotations

import threading
import time

import pytest

from plugins.plugin_capability import PluginCapability
from plugins.plugin_registry import PluginRegistry
from plugins.scheduler_plugin import SchedulerPlugin


# ── Helpers ───────────────────────────────────────────────────────


class _AtomicCounter:
    """Thread-safe counter for testing callback execution."""

    def __init__(self) -> None:
        self._value = 0
        self._lock = threading.Lock()

    def inc(self) -> int:
        with self._lock:
            self._value += 1
            return self._value

    @property
    def value(self) -> int:
        with self._lock:
            return self._value


# ── Plugin metadata & lifecycle ───────────────────────────────────


class TestSchedulerPluginMetadata:
    def test_name(self) -> None:
        p = SchedulerPlugin()
        assert p.name == "ruleforge.scheduler"

    def test_version(self) -> None:
        p = SchedulerPlugin()
        assert p.version == "1.0.0"

    def test_capability(self) -> None:
        p = SchedulerPlugin()
        assert PluginCapability.EXECUTION_HOOK in p.metadata.capabilities

    def test_dependencies(self) -> None:
        p = SchedulerPlugin()
        assert p.metadata.dependencies == ()


class TestSchedulerPluginLifecycle:
    def test_full_lifecycle_in_registry(self) -> None:
        reg = PluginRegistry()
        reg.register(SchedulerPlugin())
        assert reg.state("ruleforge.scheduler") == "LOADED"
        reg.enable("ruleforge.scheduler")
        assert reg.state("ruleforge.scheduler") == "ENABLED"
        reg.activate("ruleforge.scheduler")
        assert reg.state("ruleforge.scheduler") == "ACTIVE"
        reg.deactivate("ruleforge.scheduler")
        assert reg.state("ruleforge.scheduler") == "ENABLED"

    def test_discovery_via_capability(self) -> None:
        reg = PluginRegistry()
        reg.register(SchedulerPlugin())
        reg.enable("ruleforge.scheduler")
        plugins = reg.list_by_capability(PluginCapability.EXECUTION_HOOK)
        assert any(p.name == "ruleforge.scheduler" for p in plugins)

    def test_not_found_when_loaded_only(self) -> None:
        reg = PluginRegistry()
        reg.register(SchedulerPlugin())
        assert (
            reg.list_by_capability(PluginCapability.EXECUTION_HOOK) == []
        )

    def test_deactivation_cancels_all_pending(self) -> None:
        reg = PluginRegistry()
        reg.register(SchedulerPlugin())
        reg.enable("ruleforge.scheduler")
        reg.activate("ruleforge.scheduler")

        plugin = reg.get("ruleforge.scheduler")
        assert plugin is not None
        plugin.schedule_once("slow", lambda: None, delay=60.0)

        assert plugin.scheduled_count == 1
        reg.deactivate("ruleforge.scheduler")
        assert plugin.scheduled_count == 0


# ── Schedule once ─────────────────────────────────────────────────


class TestScheduleOnce:
    def test_schedules_and_executes(self) -> None:
        reg = PluginRegistry()
        reg.register(SchedulerPlugin())
        reg.enable("ruleforge.scheduler")
        reg.activate("ruleforge.scheduler")

        plugin = reg.get("ruleforge.scheduler")
        assert plugin is not None

        counter = _AtomicCounter()
        task_id = plugin.schedule_once("test", counter.inc, delay=0.1)
        assert task_id
        assert plugin.scheduled_count == 1

        time.sleep(0.3)
        assert counter.value == 1
        assert plugin.scheduled_count == 0

    def test_immediate_execution(self) -> None:
        reg = PluginRegistry()
        reg.register(SchedulerPlugin())
        reg.enable("ruleforge.scheduler")
        reg.activate("ruleforge.scheduler")

        plugin = reg.get("ruleforge.scheduler")
        assert plugin is not None

        counter = _AtomicCounter()
        plugin.schedule_once("test", counter.inc, delay=0.0)
        time.sleep(0.15)
        assert counter.value == 1

    def test_negative_delay_raises(self) -> None:
        p = SchedulerPlugin()
        with pytest.raises(ValueError, match="non-negative"):
            p.schedule_once("bad", lambda: None, delay=-1.0)


# ── Schedule recurring ────────────────────────────────────────────


class TestScheduleRecurring:
    def test_recurring_executes_multiple_times(self) -> None:
        reg = PluginRegistry()
        reg.register(SchedulerPlugin())
        reg.enable("ruleforge.scheduler")
        reg.activate("ruleforge.scheduler")

        plugin = reg.get("ruleforge.scheduler")
        assert plugin is not None

        counter = _AtomicCounter()
        plugin.schedule_recurring("test", counter.inc, interval=0.05)

        time.sleep(0.18)
        # Should have executed at least 2-3 times
        assert counter.value >= 2

        plugin.cancel_all()

    def test_max_runs_stops(self) -> None:
        reg = PluginRegistry()
        reg.register(SchedulerPlugin())
        reg.enable("ruleforge.scheduler")
        reg.activate("ruleforge.scheduler")

        plugin = reg.get("ruleforge.scheduler")
        assert plugin is not None

        counter = _AtomicCounter()
        plugin.schedule_recurring(
            "test", counter.inc, interval=0.03, max_runs=3
        )

        time.sleep(0.2)
        assert counter.value == 3
        assert plugin.scheduled_count == 0

    def test_zero_interval_raises(self) -> None:
        p = SchedulerPlugin()
        with pytest.raises(ValueError, match="positive"):
            p.schedule_recurring("bad", lambda: None, interval=0.0)

    def test_negative_interval_raises(self) -> None:
        p = SchedulerPlugin()
        with pytest.raises(ValueError, match="positive"):
            p.schedule_recurring("bad", lambda: None, interval=-1.0)


# ── Cancel ────────────────────────────────────────────────────────


class TestCancel:
    def test_cancel_removes_task(self) -> None:
        reg = PluginRegistry()
        reg.register(SchedulerPlugin())
        reg.enable("ruleforge.scheduler")
        reg.activate("ruleforge.scheduler")

        plugin = reg.get("ruleforge.scheduler")
        assert plugin is not None

        counter = _AtomicCounter()
        task_id = plugin.schedule_once("test", counter.inc, delay=5.0)
        assert plugin.scheduled_count == 1

        cancelled = plugin.cancel(task_id)
        assert cancelled
        assert plugin.scheduled_count == 0

        time.sleep(0.1)
        assert counter.value == 0

    def test_cancel_nonexistent_returns_false(self) -> None:
        p = SchedulerPlugin()
        assert p.cancel("nonexistent") is False

    def test_cancel_all(self) -> None:
        reg = PluginRegistry()
        reg.register(SchedulerPlugin())
        reg.enable("ruleforge.scheduler")
        reg.activate("ruleforge.scheduler")

        plugin = reg.get("ruleforge.scheduler")
        assert plugin is not None

        counter = _AtomicCounter()
        plugin.schedule_once("a", counter.inc, delay=5.0)
        plugin.schedule_once("b", counter.inc, delay=5.0)
        assert plugin.scheduled_count == 2

        count = plugin.cancel_all()
        assert count == 2
        assert plugin.scheduled_count == 0


# ── Query ─────────────────────────────────────────────────────────


class TestQuery:
    def test_list_scheduled(self) -> None:
        reg = PluginRegistry()
        reg.register(SchedulerPlugin())
        reg.enable("ruleforge.scheduler")
        reg.activate("ruleforge.scheduler")

        plugin = reg.get("ruleforge.scheduler")
        assert plugin is not None

        tid = plugin.schedule_once("query-test", lambda: None, delay=30.0)
        tasks = plugin.list_scheduled()
        assert len(tasks) == 1
        assert tasks[0].task_id == tid
        assert tasks[0].name == "query-test"
        assert tasks[0].mode == "once"

    def test_get_task(self) -> None:
        reg = PluginRegistry()
        reg.register(SchedulerPlugin())
        reg.enable("ruleforge.scheduler")
        reg.activate("ruleforge.scheduler")

        plugin = reg.get("ruleforge.scheduler")
        assert plugin is not None

        tid = plugin.schedule_once("gt", lambda: None, delay=30.0)
        t = plugin.get_task(tid)
        assert t is not None
        assert t.name == "gt"
        assert t.mode == "once"

    def test_get_nonexistent_task_returns_none(self) -> None:
        p = SchedulerPlugin()
        assert p.get_task("nope") is None

    def test_list_scheduled_empty_when_none(self) -> None:
        p = SchedulerPlugin()
        assert p.list_scheduled() == []


# ── Stats ─────────────────────────────────────────────────────────


class TestStats:
    def test_stats_executed_count(self) -> None:
        reg = PluginRegistry()
        reg.register(SchedulerPlugin())
        reg.enable("ruleforge.scheduler")
        reg.activate("ruleforge.scheduler")

        plugin = reg.get("ruleforge.scheduler")
        assert plugin is not None

        counter = _AtomicCounter()
        plugin.schedule_once("s1", counter.inc, delay=0.05)
        time.sleep(0.2)
        assert plugin.stats.total_executed >= 1


# ── Failure handling ──────────────────────────────────────────────


class TestFailureHandling:
    def test_callback_exception_does_not_crash_scheduler(self) -> None:
        reg = PluginRegistry()
        reg.register(SchedulerPlugin())
        reg.enable("ruleforge.scheduler")
        reg.activate("ruleforge.scheduler")

        plugin = reg.get("ruleforge.scheduler")
        assert plugin is not None

        def _fail() -> None:
            raise RuntimeError("intentional")

        counter = _AtomicCounter()
        plugin.schedule_once("failing", _fail, delay=0.05)
        plugin.schedule_once("success", counter.inc, delay=0.08)

        time.sleep(0.2)
        # The failing task should not prevent subsequent tasks
        assert counter.value == 1
        # Both executed (failing + success)
        assert plugin.stats.total_executed == 2

    def test_scheduler_still_usable_after_callback_failure(self) -> None:
        reg = PluginRegistry()
        reg.register(SchedulerPlugin())
        reg.enable("ruleforge.scheduler")
        reg.activate("ruleforge.scheduler")

        plugin = reg.get("ruleforge.scheduler")
        assert plugin is not None

        def _fail() -> None:
            raise ValueError("boom")

        plugin.schedule_once("bad", _fail, delay=0.03)
        time.sleep(0.1)

        # Scheduler still works
        counter = _AtomicCounter()
        plugin.schedule_once("good", counter.inc, delay=0.03)
        time.sleep(0.1)
        assert counter.value == 1


# ── Plugin independence ───────────────────────────────────────────


class TestPluginIndependence:
    def test_no_engine_imports(self) -> None:
        import plugins.scheduler_plugin as sp

        source = sp.__file__
        assert source is not None
        with open(source) as f:
            content = f.read()
        assert "from engine" not in content
        assert "import engine" not in content

    def test_standalone_usage_without_registry(self) -> None:
        p = SchedulerPlugin()
        counter = _AtomicCounter()
        # schedule_once without activation — timer not started
        tid = p.schedule_once("standalone", counter.inc, delay=0.05)
        assert tid
        assert p.scheduled_count == 1

    def test_not_active_skips_timer_start(self) -> None:
        p = SchedulerPlugin()
        counter = _AtomicCounter()
        p.schedule_once("dormant", counter.inc, delay=0.05)
        time.sleep(0.2)
        # Timer wasn't started (plugin not active), task still in list
        assert counter.value == 0
        assert p.scheduled_count == 1


# ── ScheduledTask dataclass ───────────────────────────────────────


class TestScheduledTask:
    def test_frozen(self) -> None:
        from plugins.scheduler_plugin import ScheduledTask

        s = ScheduledTask(
            task_id="x", name="n", mode="once",
            interval_seconds=0.0, remaining_runs=1,
        )
        assert s.task_id == "x"
        with pytest.raises(Exception):
            s.task_id = "y"  # type: ignore[misc]


# ── SchedulerStats dataclass ──────────────────────────────────────


class TestSchedulerStats:
    def test_frozen(self) -> None:
        from plugins.scheduler_plugin import SchedulerStats

        s = SchedulerStats(
            total_scheduled=5, total_executed=3, active_count=2,
        )
        assert s.total_scheduled == 5
        with pytest.raises(Exception):
            s.total_scheduled = 6  # type: ignore[misc]
