"""ExecutionTrace — unified execution lifecycle trace.

Owned by ExecutionPipeline, not by individual engines.  Records
stage transitions, timestamps, and per-stage metadata.
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field


@dataclass
class TraceEvent:
    """A single lifecycle event within an execution trace."""

    event_type: str          # e.g. "prepare.completed"
    stage: str               # e.g. "prepare"
    timestamp: float = field(default_factory=time.monotonic)
    duration_ms: float | None = None
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass
class ExecutionTrace:
    """Complete trace of one execution run.

    Created by ExecutionPipeline at the start of each run.
    """

    execution_id: str = field(default_factory=lambda: f"exec_{uuid.uuid4().hex[:12]}")
    engine_name: str = ""
    started_at: float = 0.0
    finished_at: float = 0.0
    events: list[TraceEvent] = field(default_factory=list)

    @property
    def duration_ms(self) -> float:
        return (self.finished_at - self.started_at) * 1000 if self.finished_at else 0.0

    # ── Lifecycle event helpers ───────────────────────────────────

    def _add_event(
        self, event_type: str, stage: str, duration_ms: float | None = None,
        **meta: object,
    ) -> None:
        self.events.append(TraceEvent(
            event_type=event_type,
            stage=stage,
            duration_ms=duration_ms,
            metadata=dict(meta),
        ))

    def start(self, engine_name: str) -> None:
        self.engine_name = engine_name
        self.started_at = time.monotonic()
        self._add_event("execution.started", "execution")

    def stage_started(self, stage: str) -> float:
        t = time.monotonic()
        self._add_event(f"{stage}.started", stage)
        return t

    def stage_completed(self, stage: str, started_at: float) -> None:
        duration = (time.monotonic() - started_at) * 1000
        self._add_event(f"{stage}.completed", stage, duration_ms=duration)

    def finish(self) -> None:
        self.finished_at = time.monotonic()
        self._add_event("execution.finished", "execution")

    # ── Serialization ─────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "execution_id": self.execution_id,
            "engine_name": self.engine_name,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "duration_ms": self.duration_ms,
            "events": [
                {
                    "event_type": e.event_type,
                    "stage": e.stage,
                    "timestamp": e.timestamp,
                    "duration_ms": e.duration_ms,
                    "metadata": e.metadata,
                }
                for e in self.events
            ],
        }
