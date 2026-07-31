"""ExecutionPipeline — coordinates execution without owning state.

Validates context, invokes engine, collects results, and
normalizes errors.  Pure coordination — no domain logic.
"""
from __future__ import annotations

import time

from engine.execution_context import ExecutionContext
from engine.execution_engine import ExecutionEngine
from engine.execution_result import ExecutionResult


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

        # 1. Validate context
        if not context.rule.steps:
            return ExecutionResult.from_error("Rule has no steps")

        result = ExecutionResult()

        try:
            # 2. Prepare
            engine.prepare(context)
        except Exception as exc:
            result = ExecutionResult.from_error(f"Prepare failed: {exc}")
            _try_cleanup(engine, context)
            result.duration_ms = (time.monotonic() - start) * 1000
            return result

        try:
            # 3. Execute
            result = engine.execute(context)
        except Exception as exc:
            result = ExecutionResult.from_error(f"Execute failed: {exc}")
        finally:
            # 4. Cleanup (always)
            _try_cleanup(engine, context)

        result.duration_ms = (time.monotonic() - start) * 1000
        return result


def _try_cleanup(engine: ExecutionEngine, context: ExecutionContext) -> None:
    try:
        engine.cleanup(context)
    except Exception:
        pass  # Cleanup failures are non-fatal
