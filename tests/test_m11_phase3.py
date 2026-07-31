"""M11-C: DryRun & Inspection Engine tests.

Validates extensibility of Execution Platform — same pipeline,
different engines, no architecture changes.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

from models.rule import Rule, RuleStep
from engine.execution_context import ExecutionContext
from engine.execution_pipeline import ExecutionPipeline
from engine.execution_result import ExecutionResult
from engine.dry_run_execution_engine import DryRunExecutionEngine
from engine.inspection_execution_engine import InspectionExecutionEngine
from engine.rename_execution_engine import RenameExecutionEngine
from engine.rule_workflow import RuleWorkflow


def _make_rule() -> Rule:
    return Rule(
        id="test-dry",
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


# ── DryRunExecutionEngine ─────────────────────────────────────────

class TestDryRunEngine:
    def test_single_file_plan(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            src = _make_files(td, "hello.txt")[0]
            rule = _make_rule()
            ctx = ExecutionContext(rule=rule, targets=[src])
            engine = DryRunExecutionEngine()

            result = ExecutionPipeline.run(ctx, engine)
            assert result.success is True
            assert result.diagnostics["mode"] == "dry_run"
            assert result.diagnostics["would_rename"] == 1
            assert result.diagnostics["would_skip"] == 0
            # File must NOT have been renamed
            assert Path(src).exists()

    def test_multiple_files(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            srcs = _make_files(td, "a.txt", "b.txt", "c.txt")
            rule = _make_rule()
            ctx = ExecutionContext(rule=rule, targets=srcs)
            engine = DryRunExecutionEngine()

            result = ExecutionPipeline.run(ctx, engine)
            assert result.success is True
            assert result.diagnostics["would_rename"] == 3
            # All files untouched
            for s in srcs:
                assert Path(s).exists()

    def test_no_change_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            src = _make_files(td, "ALREADY.txt")[0]
            rule = _make_rule()
            ctx = ExecutionContext(rule=rule, targets=[src])
            engine = DryRunExecutionEngine()

            result = ExecutionPipeline.run(ctx, engine)
            assert result.success is True
            assert result.diagnostics["would_rename"] == 0
            assert result.diagnostics["would_skip"] == 1

    def test_conflict_duplicate_targets(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            srcs = _make_files(td, "hello.txt", "Hello.txt")
            rule = _make_rule()
            ctx = ExecutionContext(rule=rule, targets=srcs)
            engine = DryRunExecutionEngine()

            result = ExecutionPipeline.run(ctx, engine)
            assert result.success is False
            assert any("Duplicate target" in e for e in result.errors)

    def test_conflict_destination_exists(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            src = _make_files(td, "hello.txt")[0]
            _make_files(td, "HELLO.txt")
            rule = _make_rule()
            ctx = ExecutionContext(rule=rule, targets=[src])
            engine = DryRunExecutionEngine()

            result = ExecutionPipeline.run(ctx, engine)
            assert result.success is False
            assert any("already exists" in e.lower() for e in result.errors)
            assert Path(src).exists()

    def test_missing_source(self) -> None:
        rule = _make_rule()
        ctx = ExecutionContext(rule=rule, targets=["/nonexistent/x.txt"])
        engine = DryRunExecutionEngine()

        result = ExecutionPipeline.run(ctx, engine)
        assert result.success is False

    def test_no_filesystem_mutation(self) -> None:
        """Verify DryRun NEVER renames files — even on success path."""
        with tempfile.TemporaryDirectory() as td:
            srcs = _make_files(td, "x.txt", "y.txt")
            rule = _make_rule()
            ctx = ExecutionContext(rule=rule, targets=srcs)
            engine = DryRunExecutionEngine()

            ExecutionPipeline.run(ctx, engine)
            for s in srcs:
                assert Path(s).exists()
            assert not Path(td, "X.txt").exists()


# ── InspectionExecutionEngine ─────────────────────────────────────

class TestInspectionEngine:
    def test_summary_statistics(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            srcs = _make_files(td, "hello.txt", "world.txt", "KEPT.txt")
            rule = _make_rule()
            ctx = ExecutionContext(rule=rule, targets=srcs)
            engine = InspectionExecutionEngine()

            result = ExecutionPipeline.run(ctx, engine)
            assert result.success is True
            assert result.diagnostics["mode"] == "inspection"
            assert result.diagnostics["total_targets"] == 3
            assert result.diagnostics["would_rename"] == 2
            assert result.diagnostics["would_skip"] == 1
            assert result.diagnostics["conflict_count"] == 0

    def test_metadata_collection(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            src = _make_files(td, "test.txt")[0]
            rule = _make_rule()
            ctx = ExecutionContext(rule=rule, targets=[src])
            engine = InspectionExecutionEngine()

            result = ExecutionPipeline.run(ctx, engine)
            assert result.diagnostics["rule_name"] == "ToUpper"
            assert result.diagnostics["step_count"] == 1
            assert result.diagnostics["source_stems"] == ["test"]
            assert result.diagnostics["target_stems"] == ["TEST"]

    def test_conflicts_reported(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            srcs = _make_files(td, "dup.txt", "dup.txt")
            rule = _make_rule()
            ctx = ExecutionContext(rule=rule, targets=srcs)
            engine = InspectionExecutionEngine()

            result = ExecutionPipeline.run(ctx, engine)
            assert result.success is False
            assert "conflict" in result.errors[0].lower()
            assert result.diagnostics["conflict_count"] == 1
            assert len(result.diagnostics["conflicts"]) == 1

    def test_scope_estimation(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            _make_files(td, *[f"f{i}.txt" for i in range(10)])
            srcs = [str(p) for p in Path(td).iterdir()]
            rule = _make_rule()
            ctx = ExecutionContext(rule=rule, targets=srcs)
            engine = InspectionExecutionEngine()

            result = ExecutionPipeline.run(ctx, engine)
            assert result.diagnostics["total_targets"] == 10
            assert result.diagnostics["would_rename"] == 10

    def test_no_filesystem_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            srcs = _make_files(td, "a.txt", "b.txt")
            rule = _make_rule()
            ctx = ExecutionContext(rule=rule, targets=srcs)
            engine = InspectionExecutionEngine()

            ExecutionPipeline.run(ctx, engine)
            for s in srcs:
                assert Path(s).exists()


# ── Pipeline consistency ──────────────────────────────────────────

class TestPipelineConsistency:
    """All three engines must go through identical pipeline lifecycle."""

    def test_all_engines_same_lifecycle(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            rule = _make_rule()

            # Test non-mutating engines (no filesystem changes)
            src = _make_files(td, "test.txt")[0]
            ctx = ExecutionContext(rule=rule, targets=[src])
            for engine_cls in [DryRunExecutionEngine, InspectionExecutionEngine]:
                engine = engine_cls()
                result = ExecutionPipeline.run(ctx, engine)
                assert isinstance(result, ExecutionResult)
                assert result.duration_ms is not None
                assert "operations_journal" in result.diagnostics

            # Rename engine (mutates filesystem) — fresh file
            src2 = _make_files(td, "other.txt")[0]
            ctx2 = ExecutionContext(rule=rule, targets=[src2])
            engine = RenameExecutionEngine()
            result = ExecutionPipeline.run(ctx2, engine)
            assert isinstance(result, ExecutionResult)
            assert result.duration_ms is not None
            assert "operations_journal" in result.diagnostics

    def test_prepare_before_execute(self) -> None:
        """Verify prepare is called before execute in pipeline."""
        with tempfile.TemporaryDirectory() as td:
            src = _make_files(td, "x.txt")[0]
            rule = _make_rule()
            ctx = ExecutionContext(rule=rule, targets=[src])

            order = []

            class TrackingEngine(DryRunExecutionEngine):
                def prepare(self, ctx):
                    order.append("prepare")
                    super().prepare(ctx)

                def execute(self, ctx):
                    order.append("execute")
                    return super().execute(ctx)

            ExecutionPipeline.run(ctx, TrackingEngine())
            assert order == ["prepare", "execute"]

    def test_cleanup_always_runs(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            srcs = _make_files(td, "hello.txt", "Hello.txt")  # conflict
            rule = _make_rule()
            ctx = ExecutionContext(rule=rule, targets=srcs)

            cleaned = []

            class TrackingEngine(DryRunExecutionEngine):
                def cleanup(self, ctx):
                    cleaned.append(True)
                    super().cleanup(ctx)

            result = ExecutionPipeline.run(ctx, TrackingEngine())
            assert result.success is False  # conflicts
            assert len(cleaned) == 1
