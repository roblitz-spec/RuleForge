"""SchedulerPlugin — capability plugin for task scheduling.

Provides delayed and recurring task scheduling.  The plugin
orchestrates timing only — actual execution is delegated to
the Execution Platform or user-provided callbacks.

Does not modify Execution Platform, Batch Execution, or
Plugin Framework contracts.
"""

from __future__ import annotations

import threading
import time
import uuid
from dataclasses import dataclass, field

from plugins.plugin import Plugin, PluginMetadata
from plugins.plugin_capability import PluginCapability
from plugins.plugin_context import PluginContext


# ── Types ──────────────────────────────────────────────────────────


@dataclass(frozen=True)
class ScheduledTask:
    """Read-only snapshot of a scheduled task."""

    task_id: str
    name: str
    mode: str  # "once" | "recurring"
    interval_seconds: float  # 0 for "once" tasks
    remaining_runs: int | None  # None = unlimited


@dataclass(frozen=True)
class SchedulerStats:
    """Read-only statistics snapshot."""

    total_scheduled: int
    total_executed: int
    active_count: int


# ── Plugin ─────────────────────────────────────────────────────────


class SchedulerPlugin(Plugin):
    """Schedules delayed and recurring task callbacks.

    Usage:
        plugin = SchedulerPlugin()
        registry.register(plugin)
        registry.enable(plugin.name)
        registry.activate(plugin.name)

        def my_task():
            print("Task executed!")

        # Schedule once after 2 seconds
        plugin.schedule_once("backup", my_task, delay=2.0)

        # Schedule every 5 seconds
        plugin.schedule_recurring("heartbeat", my_task, interval=5.0)

        # Cancel
        plugin.cancel(task_id)

    The plugin uses threading.Timer internally.  It is the
    caller's responsibility to ensure callbacks are thread-safe.

    Capability: EXECUTION_HOOK — scheduling is a pre-execution
    orchestration concern.
    """

    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="ruleforge.scheduler",
            version="1.0.0",
            description="Schedules delayed and recurring task execution",
            author="RuleForge",
            capabilities=(PluginCapability.EXECUTION_HOOK,),
        )

    def __init__(self) -> None:
        self._tasks: dict[str, _InternalTask] = {}
        self._lock = threading.Lock()
        self._executed_count: int = 0
        self._active = False

    # ── Lifecycle ──────────────────────────────────────────────

    def on_activate(self, ctx: PluginContext) -> None:
        self._active = True

    def on_deactivate(self, ctx: PluginContext) -> None:
        self._active = False
        self.cancel_all()

    # ── Public API ─────────────────────────────────────────────

    def schedule_once(
        self,
        name: str,
        callback: object,
        delay: float = 0.0,
    ) -> str:
        """Schedule a one-shot task after *delay* seconds.

        Returns the task_id for cancellation.
        Raises ValueError if delay is negative.
        """
        if delay < 0:
            raise ValueError("delay must be non-negative")
        task_id = str(uuid.uuid4())
        internal = _InternalTask(
            task_id=task_id,
            name=name,
            mode="once",
            interval_seconds=0.0,
            remaining_runs=1,
            callback=callback,
        )
        with self._lock:
            self._tasks[task_id] = internal
        self._schedule(internal, delay_seconds=delay)
        return task_id

    def schedule_recurring(
        self,
        name: str,
        callback: object,
        interval: float,
        max_runs: int | None = None,
    ) -> str:
        """Schedule a recurring task every *interval* seconds.

        Args:
            max_runs: Maximum number of executions (None = unlimited).
        Raises ValueError if interval <= 0.
        """
        if interval <= 0:
            raise ValueError("interval must be positive")
        task_id = str(uuid.uuid4())
        internal = _InternalTask(
            task_id=task_id,
            name=name,
            mode="recurring",
            interval_seconds=interval,
            remaining_runs=max_runs,
            callback=callback,
        )
        with self._lock:
            self._tasks[task_id] = internal
        self._schedule(internal, delay_seconds=interval)
        return task_id

    def cancel(self, task_id: str) -> bool:
        """Cancel a scheduled task. Returns True if cancelled.

        Already-executing tasks may still run to completion.
        """
        with self._lock:
            task = self._tasks.pop(task_id, None)
        if task is None:
            return False
        task.timer.cancel()
        return True

    def cancel_all(self) -> int:
        """Cancel all scheduled tasks. Returns count cancelled."""
        with self._lock:
            task_ids = list(self._tasks.keys())
        count = 0
        for tid in task_ids:
            if self.cancel(tid):
                count += 1
        return count

    def list_scheduled(self) -> list[ScheduledTask]:
        """Return a snapshot of all currently scheduled tasks."""
        with self._lock:
            return [
                ScheduledTask(
                    task_id=t.task_id,
                    name=t.name,
                    mode=t.mode,
                    interval_seconds=t.interval_seconds,
                    remaining_runs=t.remaining_runs,
                )
                for t in self._tasks.values()
            ]

    def get_task(self, task_id: str) -> ScheduledTask | None:
        """Return a scheduled task by ID, or None."""
        with self._lock:
            t = self._tasks.get(task_id)
        if t is None:
            return None
        return ScheduledTask(
            task_id=t.task_id,
            name=t.name,
            mode=t.mode,
            interval_seconds=t.interval_seconds,
            remaining_runs=t.remaining_runs,
        )

    @property
    def stats(self) -> SchedulerStats:
        with self._lock:
            return SchedulerStats(
                total_scheduled=len(self._tasks),
                total_executed=self._executed_count,
                active_count=sum(
                    1 for t in self._tasks.values() if t.timer.is_alive()
                ),
            )

    @property
    def scheduled_count(self) -> int:
        with self._lock:
            return len(self._tasks)

    # ── Internal ───────────────────────────────────────────────

    def _schedule(self, task: _InternalTask, delay_seconds: float) -> None:
        timer = threading.Timer(delay_seconds, self._run_task, args=[task.task_id])
        task.timer = timer
        if self._active:
            timer.start()

    def _run_task(self, task_id: str) -> None:
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return  # cancelled before execution

        try:
            task.callback()  # type: ignore[operator]
        except Exception:
            pass  # Fire-and-forget: errors are contained
        finally:
            self._executed_count += 1

        # Determine next action
        reschedule = False
        with self._lock:
            current = self._tasks.get(task_id)
            if current is None:
                return  # cancelled during execution

            if current.mode == "recurring":
                if current.remaining_runs is not None:
                    current.remaining_runs -= 1
                    if current.remaining_runs <= 0:
                        self._tasks.pop(task_id, None)
                    else:
                        reschedule = True
                else:
                    # Unlimited runs
                    reschedule = True
            else:
                # "once" — remove after execution
                self._tasks.pop(task_id, None)

        if reschedule and self._active:
            # Re-create internal task with fresh timer
            with self._lock:
                t = self._tasks.get(task_id)
                if t is not None:
                    self._schedule(t, delay_seconds=t.interval_seconds)


# ── Internal ───────────────────────────────────────────────────────


class _InternalTask:
    """Mutable per-task state. Owned exclusively by SchedulerPlugin."""

    __slots__ = (
        "task_id",
        "name",
        "mode",
        "interval_seconds",
        "remaining_runs",
        "callback",
        "timer",
    )

    def __init__(
        self,
        task_id: str,
        name: str,
        mode: str,
        interval_seconds: float,
        remaining_runs: int | None,
        callback: object,
    ) -> None:
        self.task_id = task_id
        self.name = name
        self.mode = mode
        self.interval_seconds = interval_seconds
        self.remaining_runs = remaining_runs
        self.callback = callback
        self.timer: threading.Timer | None = None
