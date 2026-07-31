"""StringTransformEngine — default headless execution engine.

Applies a Rule to string inputs using preview_rule.  This is the
simplest execution engine — no filesystem access, no adapters.
"""
from __future__ import annotations

from engine.execution_context import ExecutionContext
from engine.execution_engine import ExecutionEngine
from engine.execution_result import ExecutionResult
from engine.preview_pipeline import preview_rule


class StringTransformEngine(ExecutionEngine):
    """Execute a Rule against string inputs.

    Pure string-level transformation — no side effects.
    """

    def prepare(self, context: ExecutionContext) -> None:
        if not context.targets:
            raise ValueError("ExecutionContext requires at least one target")
        if not context.rule.steps:
            raise ValueError("Rule has no steps")

    def execute(self, context: ExecutionContext) -> ExecutionResult:
        result = ExecutionResult()
        preview = preview_rule(context.rule, context.targets)

        for entry in preview.entries:
            result.outputs.append(entry.output_text)
            result.actions_executed += 1

        result.diagnostics["preview_all_match"] = preview.all_match
        return result

    def cleanup(self, context: ExecutionContext) -> None:
        pass  # No resources to release
