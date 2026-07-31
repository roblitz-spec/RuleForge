"""ExecutionPipeline — coordinates execution without owning state.

Validates context, invokes engine, collects results, normalizes
errors, and owns the execution trace (M11-E).  Pure coordination —
no domain logic, no engine-specific branches.
"""
from __future__ import annotations

import time

from engine.execution_context import ExecutionContext
from engine.execution_engine import ExecutionEngine
from engine.execution_metrics import ExecutionMetrics
from engine.execution_result import ExecutionResult
from engine.execution_trace import ExecutionTrace


class ExecutionPipeline:
    """Coordinates a single execution run.

    Usage:
        pipeline = ExecutionPipeline()
        context = ExecutionContext(rule=rule, targets=["hello", "world"])
        engine = StringTransformEngine()
        result = pipeline.run(context, engine)
    """

    @staticmethod
    def run(context: ExecutionContext, engine: ExecutionEngine) -> ExecutionResult:
        """Run the full execution lifecycle.

        Order: validate → prepare → execute → collect → cleanup.
        Cleanup runs unconditionally after execute, even on failure.
        """
        start = time.monotonic()

        # Trace owned by Pipeline, not Engine (M11-E)
        engine_name = type(engine).__name__
        trace = ExecutionTrace()
        trace.start(engine_name)

        # 1. Validate
        if not context.rule.steps:
            result = ExecutionResult.from_error("Rule has no steps")
            trace.finish()
            result.trace = trace
            result.metrics = _build_metrics(result, trace)
            result.duration_ms = (time.monotonic() - start) * 1000
            return result

        result = ExecutionResult()

        # 2. Prepare
        t_prep = trace.stage_started("prepare")
        try:
            engine.prepare(context)
        except Exception as exc:
            result = ExecutionResult.from_error(f"Prepare failed: {exc}")
            trace.stage_completed("prepare", t_prep)
            _try_cleanup(engine, context, trace)
            trace.finish()
            result.trace = trace
            result.metrics = _build_metrics(result, trace)
            result.duration_ms = (time.monotonic() - start) * 1000
            return result
        trace.stage_completed("prepare", t_prep)

        # 3. Execute
        t_exec = trace.stage_started("execute")
        try:
            result = engine.execute(context)
        except Exception as exc:
            result = ExecutionResult.from_error(f"Execute failed: {exc}")
        trace.stage_completed("execute", t_exec)

        # 4. Cleanup (always)
        _try_cleanup(engine, context, trace)

        trace.finish()

        result.trace = trace
        result.metrics = _build_metrics(result, trace)
        result.duration_ms = (time.monotonic() - start) * 1000
        return result


def _build_metrics(result: ExecutionResult, trace: ExecutionTrace) -> ExecutionMetrics:
    return ExecutionMetrics(
        files_selected=result.total_actions,
        files_modified=result.actions_executed,
        files_skipped=result.actions_skipped,
        conflict_count=result.diagnostics.get("conflict_count", 0)  # type: ignore[arg-type]
        if isinstance(result.diagnostics.get("conflict_count"), int)
        else 0,
        error_count=len(result.errors),
        duration_ms=trace.duration_ms,
    )


def _try_cleanup(
    engine: ExecutionEngine, context: ExecutionContext, trace: ExecutionTrace,
) -> None:
    t_clean = trace.stage_started("cleanup")
    try:
        engine.cleanup(context)
    except Exception:
        pass  # Cleanup failures are non-fatal
    trace.stage_completed("cleanup", t_clean)
