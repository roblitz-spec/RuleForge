"""M12-A: Batch Execution Foundation tests.

Covers BatchItem, ExecutionBatch, BatchExecutor, BatchResult,
BatchExecutionEngine, anti-nesting guard, and RuleWorkflow
integration.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

from models.rule import Rule, RuleStep
from engine.batch_executor import BatchExecutor
from engine.batch_result import BatchItemResult, BatchResult
from engine.batch_execution_engine import BatchExecutionEngine
from engine.engine_registry import EngineRegistry
from engine.execution_batch import BatchItem, ExecutionBatch
from engine.execution_context import ExecutionContext
from engine.execution_pipeline import ExecutionPipeline
from engine.execution_result import ExecutionResult
from engine.rule_workflow import RuleWorkflow
from engine.string_transform_engine import StringTransformEngine


def _make_rule(name: str = "Test", mode: str = "upper") -> Rule:
    return Rule(
        id=f"test-{name.lower()}",
        name=name,
        steps=[RuleStep(type="case", parameters={"mode": mode})],
    )


def _make_files(parent: str, *names: str) -> list[str]:
    paths = []
    for name in names:
        p = str(Path(parent) / name)
        Path(p).write_text("")
        paths.append(p)
    return paths


# ── BatchItem / ExecutionBatch ─────────────────────────────────────

class TestBatchItem:
    def test_defaults(self) -> None:
        rule = _make_rule()
        item = BatchItem(rule=rule, targets=["a", "b"])
        assert item.engine_name == "string"
        assert item.label == ""
        assert item.options == {}

    def test_explicit_values(self) -> None:
        rule = _make_rule()
        item = BatchItem(
            rule=rule,
            targets=["x"],
            engine_name="dry-run",
            label="test-item",
            options={"dry_run": True},
        )
        assert item.engine_name == "dry-run"
        assert item.label == "test-item"
        assert item.options == {"dry_run": True}

    def test_frozen(self) -> None:
        import pytest
        from dataclasses import FrozenInstanceError
        rule = _make_rule()
        item = BatchItem(rule=rule, targets=["a"])
        with pytest.raises(FrozenInstanceError):
            item.engine_name = "rename"  # type: ignore[misc]


class TestExecutionBatch:
    def test_defaults(self) -> None:
        rule = _make_rule()
        item = BatchItem(rule=rule, targets=["a"])
        batch = ExecutionBatch(items=[item])
        assert batch.stop_on_error is True
        assert batch.validate_first is True

    def test_explicit_policy(self) -> None:
        rule = _make_rule()
        item = BatchItem(rule=rule, targets=["a"])
        batch = ExecutionBatch(items=[item], stop_on_error=False, validate_first=False)
        assert batch.stop_on_error is False
        assert batch.validate_first is False


# ── BatchResult ────────────────────────────────────────────────────

class TestBatchResult:
    def test_new_initializes_counts(self) -> None:
        result = BatchResult.new(total_items=3)
        assert result.total_items == 3
        assert result.succeeded == 0
        assert result.failed == 0
        assert result.skipped == 0
        assert result.success is True

    def test_add_successful_item(self) -> None:
        result = BatchResult.new(total_items=2)
        exec_result = ExecutionResult(success=True, actions_executed=1)
        ir = BatchItemResult(
            label="ok", item_index=0, result=exec_result, engine_name="string",
        )
        result.add_item_result(ir)
        assert result.succeeded == 1
        assert result.failed == 0
        assert result.success is True

    def test_add_failed_item(self) -> None:
        result = BatchResult.new(total_items=2)
        exec_result = ExecutionResult.from_error("boom")
        ir = BatchItemResult(
            label="bad", item_index=0, result=exec_result, engine_name="string",
        )
        result.add_item_result(ir)
        assert result.succeeded == 0
        assert result.failed == 1
        assert result.success is False

    def test_skipped_counts(self) -> None:
        result = BatchResult.new(total_items=5)
        result.mark_skipped(3)
        assert result.skipped == 3
        assert result.success is False


# ── BatchExecutor ──────────────────────────────────────────────────

class TestBatchExecutorSuccess:
    def test_single_item(self) -> None:
        rule = _make_rule()
        batch = ExecutionBatch(items=[BatchItem(rule=rule, targets=["hello"])])
        result = BatchExecutor.run(batch)
        assert result.success is True
        assert result.succeeded == 1
        assert result.failed == 0
        assert result.skipped == 0
        assert len(result.item_results) == 1
        assert result.item_results[0].result.outputs == ["HELLO"]

    def test_multiple_items(self) -> None:
        rule_a = _make_rule("Upper", "upper")
        rule_b = _make_rule("Lower", "lower")
        batch = ExecutionBatch(items=[
            BatchItem(rule=rule_a, targets=["hello"], label="to-upper"),
            BatchItem(rule=rule_b, targets=["WORLD"], label="to-lower"),
        ])
        result = BatchExecutor.run(batch)
        assert result.success is True
        assert result.succeeded == 2
        assert result.failed == 0
        assert result.item_results[0].result.outputs == ["HELLO"]
        assert result.item_results[1].result.outputs == ["world"]

    def test_timing_recorded(self) -> None:
        rule = _make_rule()
        batch = ExecutionBatch(items=[BatchItem(rule=rule, targets=["a"])])
        result = BatchExecutor.run(batch)
        assert result.duration_ms > 0


class TestBatchExecutorStopOnError:
    def test_stop_on_first_error(self) -> None:
        rule_ok = _make_rule("OK")
        rule_bad = Rule(id="bad", name="Bad", steps=[])  # no steps → will fail
        batch = ExecutionBatch(
            items=[
                BatchItem(rule=rule_ok, targets=["hello"], label="first"),
                BatchItem(rule=rule_bad, targets=["world"], label="should-fail"),
                BatchItem(rule=rule_ok, targets=["skip"], label="should-skip"),
            ],
            stop_on_error=True,
            validate_first=False,  # let failure happen during execute
        )
        result = BatchExecutor.run(batch)
        assert result.success is False
        assert result.succeeded == 1
        assert result.failed == 1
        assert result.skipped == 1
        assert result.total_items == 3
        assert result.item_results[0].label == "first"
        assert result.item_results[1].label == "should-fail"
        assert len(result.item_results) == 2  # third was skipped

    def test_continue_on_error(self) -> None:
        rule_ok = _make_rule("OK")
        rule_bad = Rule(id="bad", name="Bad", steps=[])
        batch = ExecutionBatch(
            items=[
                BatchItem(rule=rule_ok, targets=["hello"], label="first"),
                BatchItem(rule=rule_bad, targets=["world"], label="bad"),
                BatchItem(rule=rule_ok, targets=["third"], label="third"),
            ],
            stop_on_error=False,
            validate_first=False,
        )
        result = BatchExecutor.run(batch)
        assert result.success is False
        assert result.succeeded == 2
        assert result.failed == 1
        assert result.skipped == 0
        assert len(result.item_results) == 3  # all attempted


class TestBatchExecutorValidateFirst:
    def test_validate_first_catches_prepare_failure(self) -> None:
        rule = _make_rule()
        # An ExecutionContext with empty targets for non-string engines will fail prepare
        batch = ExecutionBatch(
            items=[BatchItem(rule=rule, targets=[], label="empty")],
            validate_first=True,
        )
        result = BatchExecutor.run(batch)
        assert result.success is False
        assert result.failed == 1
        assert result.skipped == 0
        assert "Pre-validation failed" in result.item_results[0].result.errors[0]

    def test_validate_first_stops_on_error(self) -> None:
        rule = _make_rule()
        batch = ExecutionBatch(
            items=[
                BatchItem(rule=rule, targets=[], label="bad"),
                BatchItem(rule=rule, targets=["good"], label="good"),
            ],
            validate_first=True,
            stop_on_error=True,
        )
        result = BatchExecutor.run(batch)
        assert result.success is False
        assert result.skipped == 1
        assert len(result.item_results) == 1

    def test_no_validate_first_lets_execute_catch_failure(self) -> None:
        rule_bad = Rule(id="bad", name="Bad", steps=[])
        batch = ExecutionBatch(
            items=[BatchItem(rule=rule_bad, targets=["x"])],
            validate_first=False,
        )
        result = BatchExecutor.run(batch)
        # Fails during execute because ExecutionContext rejects empty steps
        assert result.success is False
        assert result.failed == 1


class TestBatchExecutorEmpty:
    def test_empty_batch(self) -> None:
        batch = ExecutionBatch(items=[])
        result = BatchExecutor.run(batch)
        assert result.success is True
        assert result.total_items == 0
        assert result.succeeded == 0
        assert result.failed == 0


# ── Anti-nesting guard ─────────────────────────────────────────────

class TestAntiNesting:
    def test_batch_engine_name_rejected_in_batch_item(self) -> None:
        import pytest
        rule = _make_rule()
        batch = ExecutionBatch(items=[
            BatchItem(rule=rule, targets=["hello"], engine_name="batch"),
        ])
        with pytest.raises(ValueError, match="cannot be nested"):
            BatchExecutor.run(batch)

    def test_batch_engine_name_rejected_in_multi_item(self) -> None:
        import pytest
        rule = _make_rule()
        batch = ExecutionBatch(items=[
            BatchItem(rule=rule, targets=["a"], label="ok"),
            BatchItem(rule=rule, targets=["b"], engine_name="batch", label="bad"),
        ])
        with pytest.raises(ValueError, match="cannot be nested"):
            BatchExecutor.run(batch)


# ── BatchExecutionEngine ───────────────────────────────────────────

class TestBatchExecutionEngine:
    def test_lifecycle_through_pipeline(self) -> None:
        rule = _make_rule()
        batch_def = ExecutionBatch(items=[
            BatchItem(rule=rule, targets=["hello"], label="a"),
            BatchItem(rule=rule, targets=["world"], label="b"),
        ])
        ctx = ExecutionContext(
            rule=rule,
            targets=["hello", "world"],
            options={"_batch_definition": batch_def},
        )
        engine = BatchExecutionEngine()
        result = ExecutionPipeline.run(ctx, engine)
        assert result.success is True
        assert result.actions_executed == 2
        assert result.actions_skipped == 0
        assert result.diagnostics["batch"]["total_items"] == 2
        assert result.diagnostics["batch"]["succeeded"] == 2

    def test_failure_propagates(self) -> None:
        rule = _make_rule()
        rule_bad = Rule(id="bad", name="Bad", steps=[])
        batch_def = ExecutionBatch(items=[
            BatchItem(rule=rule_bad, targets=["hello"], label="bad"),
        ])
        ctx = ExecutionContext(
            rule=rule,
            targets=["hello"],
            options={"_batch_definition": batch_def},
        )
        engine = BatchExecutionEngine()
        result = ExecutionPipeline.run(ctx, engine)
        assert result.success is False
        assert "bad" in str(result.errors)

    def test_missing_batch_definition(self) -> None:
        import pytest
        rule = _make_rule()
        ctx = ExecutionContext(rule=rule, targets=["hello"])
        engine = BatchExecutionEngine()
        with pytest.raises(ValueError, match="_batch_definition"):
            engine.prepare(ctx)

    def test_empty_batch_definition(self) -> None:
        import pytest
        rule = _make_rule()
        ctx = ExecutionContext(
            rule=rule,
            targets=[],
            options={"_batch_definition": ExecutionBatch(items=[])},
        )
        engine = BatchExecutionEngine()
        with pytest.raises(ValueError, match="no items"):
            engine.prepare(ctx)


# ── RuleWorkflow integration ───────────────────────────────────────

class TestWorkflowBatchIntegration:
    def test_execute_batch_returns_batch_result(self) -> None:
        rule = _make_rule()
        batch = ExecutionBatch(items=[
            BatchItem(rule=rule, targets=["hello"], label="item1"),
        ])
        result = RuleWorkflow.execute_batch(batch)
        assert isinstance(result, BatchResult)
        assert result.success is True
        assert result.succeeded == 1

    def test_execute_batch_with_custom_registry(self) -> None:
        rule = _make_rule()
        batch = ExecutionBatch(items=[
            BatchItem(rule=rule, targets=["hello"]),
        ])
        reg = EngineRegistry.default()
        result = RuleWorkflow.execute_batch(batch, registry=reg)
        assert result.success is True


# ── Registry integration ───────────────────────────────────────────

class TestBatchInRegistry:
    def test_batch_registered_in_default(self) -> None:
        reg = EngineRegistry.default()
        assert reg.is_registered("batch")
        engine = reg.create("batch")
        assert isinstance(engine, BatchExecutionEngine)
