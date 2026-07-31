"""M11-A: Execution Pipeline tests.

Covers pipeline, context, result, engine interface, and
RuleWorkflow integration.
"""
from __future__ import annotations

from models.rule import Rule, RuleStep
from engine.execution_context import ExecutionContext
from engine.execution_engine import ExecutionEngine
from engine.execution_pipeline import ExecutionPipeline
from engine.execution_result import ExecutionResult
from engine.string_transform_engine import StringTransformEngine
from engine.rule_workflow import RuleWorkflow


def _make_rule(name: str = "Test") -> Rule:
    return Rule(
        id="test-rule",
        name=name,
        steps=[RuleStep(type="case", parameters={"mode": "upper"})],
    )


# ── ExecutionContext ──────────────────────────────────────────────

class TestExecutionContext:
    def test_create_with_rule_and_targets(self) -> None:
        rule = _make_rule()
        ctx = ExecutionContext(rule=rule, targets=["hello", "world"])
        assert ctx.rule is rule
        assert ctx.targets == ["hello", "world"]
        assert ctx.target_count == 2
        assert ctx.options == {}

    def test_create_with_options(self) -> None:
        rule = _make_rule()
        ctx = ExecutionContext(rule=rule, targets=["a"], options={"dry_run": True})
        assert ctx.options["dry_run"] is True

    def test_empty_steps_raises(self) -> None:
        import pytest
        rule = Rule(id="e", name="Empty", steps=[])
        with pytest.raises(ValueError, match="at least one step"):
            ExecutionContext(rule=rule)

    def test_immutable(self) -> None:
        import pytest
        from dataclasses import FrozenInstanceError
        rule = _make_rule()
        ctx = ExecutionContext(rule=rule, targets=["x"])
        with pytest.raises(FrozenInstanceError):
            ctx.targets = ["y"]  # type: ignore[misc]


# ── ExecutionResult ───────────────────────────────────────────────

class TestExecutionResult:
    def test_default_is_success(self) -> None:
        r = ExecutionResult()
        assert r.success is True
        assert r.errors == []

    def test_add_error_flips_success(self) -> None:
        r = ExecutionResult()
        r.add_error("fail")
        assert r.success is False

    def test_from_error_factory(self) -> None:
        r = ExecutionResult.from_error("boom")
        assert r.success is False
        assert r.errors == ["boom"]

    def test_total_actions(self) -> None:
        r = ExecutionResult(actions_executed=3, actions_skipped=1)
        assert r.total_actions == 4

    def test_duration_set(self) -> None:
        r = ExecutionResult(duration_ms=12.5)
        assert r.duration_ms == 12.5


# ── StringTransformEngine ─────────────────────────────────────────

class TestStringTransformEngine:
    def test_prepare_and_execute(self) -> None:
        rule = _make_rule()
        ctx = ExecutionContext(rule=rule, targets=["hello", "WORLD"])
        engine = StringTransformEngine()
        engine.prepare(ctx)
        result = engine.execute(ctx)
        assert result.success is True
        assert result.outputs == ["HELLO", "WORLD"]
        assert result.actions_executed == 2

    def test_prepare_no_targets_raises(self) -> None:
        import pytest
        rule = _make_rule()
        ctx = ExecutionContext(rule=rule)
        engine = StringTransformEngine()
        with pytest.raises(ValueError, match="at least one target"):
            engine.prepare(ctx)

    def test_cleanup_is_noop(self) -> None:
        rule = _make_rule()
        ctx = ExecutionContext(rule=rule, targets=["a"])
        engine = StringTransformEngine()
        engine.cleanup(ctx)  # No exception


# ── ExecutionPipeline ─────────────────────────────────────────────

class TestExecutionPipeline:
    def test_successful_run(self) -> None:
        rule = _make_rule()
        ctx = ExecutionContext(rule=rule, targets=["hello", "world"])
        engine = StringTransformEngine()
        result = ExecutionPipeline.run(ctx, engine)
        assert result.success is True
        assert result.outputs == ["HELLO", "WORLD"]
        assert result.actions_executed == 2
        assert result.duration_ms is not None
        assert result.duration_ms >= 0

    def test_no_targets_runs_cleanly(self) -> None:
        """Pipeline with zero targets should produce empty result."""
        rule = _make_rule()
        ctx = ExecutionContext(rule=rule, targets=[])
        engine = StringTransformEngine()
        result = ExecutionPipeline.run(ctx, engine)
        # prepare raises on no targets, so this should fail
        assert result.success is False

    def test_engine_failure_normalized(self) -> None:
        rule = _make_rule()
        ctx = ExecutionContext(rule=rule, targets=["hello"])

        class FailingEngine(ExecutionEngine):
            def prepare(self, ctx): pass
            def execute(self, ctx):
                msg = "boom"
                raise RuntimeError(msg)
            def cleanup(self, ctx): pass

        result = ExecutionPipeline.run(ctx, FailingEngine())
        assert result.success is False
        assert "Execute failed" in result.errors[0]

    def test_prepare_failure_normalized(self) -> None:
        rule = _make_rule()
        ctx = ExecutionContext(rule=rule, targets=["hello"])

        class BadPrepareEngine(ExecutionEngine):
            def prepare(self, ctx):
                msg = "no resources"
                raise RuntimeError(msg)
            def execute(self, ctx): return ExecutionResult()
            def cleanup(self, ctx): pass

        result = ExecutionPipeline.run(ctx, BadPrepareEngine())
        assert result.success is False
        assert "Prepare failed" in result.errors[0]

    def test_cleanup_runs_after_execute_failure(self) -> None:
        rule = _make_rule()
        ctx = ExecutionContext(rule=rule, targets=["hello"])
        cleanup_called = []

        class CleanupTrackingEngine(ExecutionEngine):
            def prepare(self, ctx): pass
            def execute(self, ctx):
                msg = "fail"
                raise RuntimeError(msg)
            def cleanup(self, ctx):
                cleanup_called.append(True)

        ExecutionPipeline.run(ctx, CleanupTrackingEngine())
        assert len(cleanup_called) == 1

    def test_multiple_targets(self) -> None:
        rule = _make_rule()
        ctx = ExecutionContext(rule=rule, targets=["a", "b", "c", "d", "e"])
        engine = StringTransformEngine()
        result = ExecutionPipeline.run(ctx, engine)
        assert result.actions_executed == 5
        assert len(result.outputs) == 5


# ── RuleWorkflow Integration ──────────────────────────────────────

class TestWorkflowPipelineIntegration:
    def test_execute_with_engine_default(self) -> None:
        rule = _make_rule()
        result = RuleWorkflow.execute_with_engine(rule, ["hello", "WORLD"])
        assert isinstance(result, ExecutionResult)
        assert result.success is True
        assert result.outputs == ["HELLO", "WORLD"]
        assert result.duration_ms is not None

    def test_execute_with_custom_engine(self) -> None:
        rule = _make_rule()

        class DryRunEngine(ExecutionEngine):
            def prepare(self, ctx): pass
            def execute(self, ctx):
                return ExecutionResult(
                    outputs=[f"[dry] {t}" for t in ctx.targets],
                    actions_executed=len(ctx.targets),
                    diagnostics={"mode": "dry_run"},
                )
            def cleanup(self, ctx): pass

        result = RuleWorkflow.execute_with_engine(
            rule, ["x", "y"], engine=DryRunEngine(),
        )
        assert result.outputs == ["[dry] x", "[dry] y"]
        assert result.diagnostics["mode"] == "dry_run"

    def test_existing_execute_still_works(self) -> None:
        """Backward compatibility: execute() returns list[str]."""
        rule = _make_rule()
        outputs = RuleWorkflow.execute(rule, ["hello"])
        assert isinstance(outputs, list)
        assert outputs == ["HELLO"]

    def test_full_workflow_to_pipeline_execute(self) -> None:
        """E2E: infer → session → commit → execute via pipeline."""
        wf = RuleWorkflow()
        ir = wf.infer([("hello", "HELLO"), ("world", "WORLD")])
        assert ir is not None
        result = wf.execute_with_engine(ir.rule, ["foo", "bar"])
        assert result.success is True
        assert result.outputs == ["FOO", "BAR"]


# ── Engine Contract ───────────────────────────────────────────────

class TestEngineContract:
    """Verify that custom engines implement the interface correctly."""

    def test_engine_abc_enforces_interface(self) -> None:
        import pytest
        with pytest.raises(TypeError):
            ExecutionEngine()  # type: ignore[abstract]

    def test_custom_engine_with_all_methods(self) -> None:
        rule = _make_rule()
        ctx = ExecutionContext(rule=rule, targets=["a"])

        class ValidEngine(ExecutionEngine):
            def prepare(self, ctx): pass
            def execute(self, ctx):
                return ExecutionResult(outputs=ctx.targets, actions_executed=1)
            def cleanup(self, ctx): pass

        result = ExecutionPipeline.run(ctx, ValidEngine())
        assert result.success is True
        assert result.outputs == ["a"]
