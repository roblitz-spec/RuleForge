"""M11-D: Engine Registry tests.

Covers registration, resolution, error handling, lifecycle,
and RuleWorkflow integration.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

from models.rule import Rule, RuleStep
from engine.engine_registry import (
    EngineRegistry,
    EngineNotFoundError,
    DuplicateEngineError,
)
from engine.execution_context import ExecutionContext
from engine.execution_engine import ExecutionEngine
from engine.execution_pipeline import ExecutionPipeline
from engine.execution_result import ExecutionResult
from engine.string_transform_engine import StringTransformEngine
from engine.rename_execution_engine import RenameExecutionEngine
from engine.dry_run_execution_engine import DryRunExecutionEngine
from engine.inspection_execution_engine import InspectionExecutionEngine
from engine.rule_workflow import RuleWorkflow


def _make_rule() -> Rule:
    return Rule(
        id="test-reg",
        name="ToUpper",
        steps=[RuleStep(type="case", parameters={"mode": "upper"})],
    )


def _make_files(parent: str, *names: str) -> list[str]:
    paths = []
    for name in names:
        p = str(Path(parent) / name)
        Path(p).write_text("")
        paths.append(p)
    return paths


# ── Registration ──────────────────────────────────────────────────

class TestRegistration:
    def test_register_and_retrieve(self) -> None:
        r = EngineRegistry()
        r.register("test", StringTransformEngine)
        assert r.is_registered("test")
        engine = r.create("test")
        assert isinstance(engine, StringTransformEngine)

    def test_list_names(self) -> None:
        r = EngineRegistry()
        r.register("b", StringTransformEngine)
        r.register("a", StringTransformEngine)
        assert r.names() == ["a", "b"]  # sorted

    def test_duplicate_rejected(self) -> None:
        import pytest
        r = EngineRegistry()
        r.register("dup", StringTransformEngine)
        with pytest.raises(DuplicateEngineError, match="already registered"):
            r.register("dup", StringTransformEngine)

    def test_replace_allows_overwrite(self) -> None:
        r = EngineRegistry()
        r.register("x", StringTransformEngine)
        r.replace("x", RenameExecutionEngine)
        engine = r.create("x")
        assert isinstance(engine, RenameExecutionEngine)

    def test_default_registry_populated(self) -> None:
        r = EngineRegistry.default()
        assert r.is_registered("string")
        assert r.is_registered("rename")
        assert r.is_registered("dry-run")
        assert r.is_registered("inspect")
        assert r.is_registered("batch")
        assert "batch" in r.names()


# ── Resolution ────────────────────────────────────────────────────

class TestResolution:
    def test_resolve_string_engine(self) -> None:
        r = EngineRegistry.default()
        engine = r.create("string")
        assert isinstance(engine, StringTransformEngine)

    def test_resolve_rename_engine(self) -> None:
        r = EngineRegistry.default()
        engine = r.create("rename")
        assert isinstance(engine, RenameExecutionEngine)

    def test_resolve_dry_run_engine(self) -> None:
        r = EngineRegistry.default()
        engine = r.create("dry-run")
        assert isinstance(engine, DryRunExecutionEngine)

    def test_resolve_inspection_engine(self) -> None:
        r = EngineRegistry.default()
        engine = r.create("inspect")
        assert isinstance(engine, InspectionExecutionEngine)

    def test_get_class_no_instantiation(self) -> None:
        r = EngineRegistry.default()
        cls = r.get_class("rename")
        assert cls is RenameExecutionEngine


# ── Error handling ────────────────────────────────────────────────

class TestRegistryErrors:
    def test_unknown_engine_name(self) -> None:
        import pytest
        r = EngineRegistry()
        with pytest.raises(EngineNotFoundError) as exc:
            r.create("bogus")
        assert "bogus" in str(exc.value)
        assert exc.value.name == "bogus"
        assert exc.value.available == []

    def test_unknown_engine_lists_available(self) -> None:
        import pytest
        r = EngineRegistry.default()
        with pytest.raises(EngineNotFoundError) as exc:
            r.create("bogus")
        assert "Available:" in str(exc.value)
        assert "rename" in exc.value.available
        assert "dry-run" in exc.value.available

    def test_engine_errors_are_public_exceptions(self) -> None:
        """EngineNotFoundError and DuplicateEngineError are part of the public API."""
        assert issubclass(EngineNotFoundError, Exception)
        assert issubclass(DuplicateEngineError, Exception)


# ── Lifecycle ─────────────────────────────────────────────────────

class TestEngineLifecycle:
    def test_new_instance_per_create(self) -> None:
        r = EngineRegistry()
        r.register("test", StringTransformEngine)
        a = r.create("test")
        b = r.create("test")
        assert a is not b
        assert isinstance(a, StringTransformEngine)
        assert isinstance(b, StringTransformEngine)

    def test_no_shared_state_across_instances(self) -> None:
        r = EngineRegistry.default()
        a = r.create("rename")
        b = r.create("rename")
        # Each has its own internal state
        assert a._ops == []
        assert b._ops == []
        a._ops.append("stale")
        assert b._ops == []  # not affected


# ── RuleWorkflow integration ──────────────────────────────────────

class TestWorkflowIntegration:
    def test_execute_named_string_default(self) -> None:
        rule = _make_rule()
        result = RuleWorkflow.execute_named(rule, ["hello", "WORLD"])
        assert result.success is True
        assert result.outputs == ["HELLO", "WORLD"]

    def test_execute_named_with_name(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            src = _make_files(td, "test.txt")[0]
            rule = _make_rule()
            result = RuleWorkflow.execute_named(rule, [src], engine_name="rename")
            assert result.success is True
            assert not Path(src).exists()
            assert Path(td, "TEST.txt").exists()

    def test_execute_named_dry_run(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            src = _make_files(td, "hello.txt")[0]
            rule = _make_rule()
            result = RuleWorkflow.execute_named(rule, [src], engine_name="dry-run")
            assert result.success is True
            assert result.diagnostics["mode"] == "dry_run"
            assert Path(src).exists()  # not renamed

    def test_execute_named_inspect(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            src = _make_files(td, "x.txt")[0]
            rule = _make_rule()
            result = RuleWorkflow.execute_named(rule, [src], engine_name="inspect")
            assert result.success is True
            assert result.diagnostics["mode"] == "inspection"
            assert result.diagnostics["source_stems"] == ["x"]
            assert result.diagnostics["target_stems"] == ["X"]

    def test_custom_registry(self) -> None:
        r = EngineRegistry()
        r.register("my-engine", StringTransformEngine)
        rule = _make_rule()
        result = RuleWorkflow.execute_named(rule, ["a"], engine_name="my-engine", registry=r)
        assert result.success is True
        assert result.outputs == ["A"]

    def test_execute_with_engine_still_works(self) -> None:
        """Backward compat: direct engine injection still works."""
        rule = _make_rule()
        result = RuleWorkflow.execute_with_engine(
            rule, ["hello"], engine=StringTransformEngine(),
        )
        assert result.success is True
        assert result.outputs == ["HELLO"]

    def test_execute_returns_list_still_works(self) -> None:
        """Backward compat: execute() → list[str] still works."""
        rule = _make_rule()
        outputs = RuleWorkflow.execute(rule, ["hello"])
        assert outputs == ["HELLO"]

    def test_unknown_engine_name_via_workflow(self) -> None:
        import pytest
        rule = _make_rule()
        with pytest.raises(EngineNotFoundError):
            RuleWorkflow.execute_named(rule, ["x"], engine_name="nonexistent")
